"""Branch and statement coverage for the leave lifecycle code in users/views.py.

Covers: leave types in approval (BR1 deduction branches), email failure handling,
rejection method and state checks, and the apply, home, balance, notification
and admin list pages (FR1, FR5, FR6, FR7, FR8, FR9).
"""
import pytest
from django.core import mail
from django.test import Client

from users.models import LeaveApplication, LeaveBalance, LeaveType
from conftest import PASSWORD


def make_application(employee, leave_type_name, start="2026-12-01", end="2026-12-03"):
    leave_type, _ = LeaveType.objects.get_or_create(name=leave_type_name)
    return LeaveApplication.objects.create(
        user=employee, leave_type=leave_type, start_date=start, end_date=end, message="m"
    )


def approve(client, application):
    return client.get(f"/leaves/admin/{application.id}/approve/")


# ---- BR1 deduction branches (annual, sick, other) ----

@pytest.mark.parametrize(
    "leave_type_name, field, expected",
    [("Annual Leave", "annual_leave", 17), ("Sick Leave", "sick_leave", 7),
     ("Other Leave", "other_leave", 2)],
)
def test_approval_deducts_from_matching_balance(
    admin_client, employee, leave_type_name, field, expected
):
    """FR7 / BR1: each leave type reduces only its own balance by 3 days."""
    application = make_application(employee, leave_type_name)

    approve(admin_client, application)

    assert getattr(LeaveBalance.objects.get(user=employee), field) == expected


def test_approval_sends_email_to_employee(admin_client, employee, pending_application):
    """FR10: an approval email is sent to the employee."""
    approve(admin_client, pending_application)

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["emp1@example.test"]


def test_approval_survives_email_failure(
    admin_client, employee, pending_application, monkeypatch
):
    """Robustness: if sending email raises, the approval still succeeds."""
    def broken(*args, **kwargs):
        raise OSError("mail server down")

    monkeypatch.setattr("users.views.send_mail", broken)
    approve(admin_client, pending_application)

    pending_application.refresh_from_db()
    assert pending_application.status == "Approved"
    assert LeaveBalance.objects.get(user=employee).annual_leave == 17


# ---- Rejection branches ----

def test_reject_by_get_is_refused(admin_client, pending_application):
    """FR8: rejection only works by POST; a GET changes nothing."""
    response = admin_client.get(f"/leaves/admin/{pending_application.id}/reject/")

    pending_application.refresh_from_db()
    assert response.status_code == 302
    assert pending_application.status == "Pending"


def test_reject_by_employee_is_refused(employee_client, pending_application):
    """FR6: an employee gets 404 on the reject URL and nothing changes."""
    response = employee_client.post(
        f"/leaves/admin/{pending_application.id}/reject/", {"rejection_reason": "x"}
    )

    pending_application.refresh_from_db()
    assert response.status_code == 404
    assert pending_application.status == "Pending"


def test_reject_twice_keeps_first_reason(admin_client, pending_application):
    """FR9 / BR3: a Rejected application cannot be rejected again."""
    url = f"/leaves/admin/{pending_application.id}/reject/"
    admin_client.post(url, {"rejection_reason": "first reason"})
    admin_client.post(url, {"rejection_reason": "second reason"})

    pending_application.refresh_from_db()
    assert pending_application.rejection_reason == "first reason"


def test_rejection_email_contains_reason(admin_client, pending_application):
    """FR8, FR10: the rejection email includes the reason."""
    admin_client.post(
        f"/leaves/admin/{pending_application.id}/reject/",
        {"rejection_reason": "Team is short-staffed"},
    )

    assert "Team is short-staffed" in mail.outbox[0].body


def test_rejection_survives_email_failure(admin_client, pending_application, monkeypatch):
    """Robustness: if sending email raises, the rejection still succeeds."""
    def broken(*args, **kwargs):
        raise OSError("mail server down")

    monkeypatch.setattr("users.views.send_mail", broken)
    admin_client.post(
        f"/leaves/admin/{pending_application.id}/reject/", {"rejection_reason": "No"}
    )

    pending_application.refresh_from_db()
    assert pending_application.status == "Rejected"


# ---- Employee pages ----

def test_apply_form_page_loads(employee_client):
    """FR1: the apply form is shown with the leave types."""
    response = employee_client.get("/apply/")

    assert response.status_code == 200
    assert b"Annual Leave" in response.content


def test_overlap_error_re_renders_form(employee_client, employee):
    """FR3 / BR2: a refused overlap shows the form again with an error message."""
    make_application(employee, "Annual Leave", "2026-12-01", "2026-12-10")

    response = employee_client.post(
        "/apply/",
        {"leave_type": "Annual Leave", "startDate": "2026-12-05",
         "endDate": "2026-12-06", "message": "m"},
    )

    assert response.status_code == 200
    assert b"overlaps" in response.content


def test_balance_page_shows_own_balance(employee_client, employee):
    """FR5: the balance page shows the user's own balance."""
    response = employee_client.get("/balance/")

    assert response.status_code == 200
    assert response.context["leave_balance"].user == employee


def test_home_counts_pending_and_approved(
    employee_client, admin_client, employee, pending_application
):
    """FR5: the dashboard counts the user's own applications by status."""
    make_application(employee, "Sick Leave", "2027-01-01", "2027-01-02")
    approve(admin_client, pending_application)

    response = employee_client.get("/")

    assert response.context["pending_count"] == 1
    assert response.context["approved_count"] == 1


@pytest.mark.parametrize(
    "query, expected_count",
    [("", 2), ("?status=Pending", 1), ("?status=Cancelled", 0),
     ("?date_from=2026-12-15", 1), ("?date_to=2026-12-05", 1)],
)
def test_notification_page_filters(employee_client, employee, query, expected_count):
    """FR5: the history page filters by status and dates (own records only)."""
    make_application(employee, "Annual Leave", "2026-12-01", "2026-12-03")
    make_application(employee, "Sick Leave", "2026-12-20", "2026-12-22")
    LeaveApplication.objects.filter(leave_type__name="Sick Leave").update(status="Approved")

    response = employee_client.get(f"/notifications/{query}")

    assert len(response.context["leave_applications"]) == expected_count


@pytest.mark.parametrize("page", ["abc", "999", "1"])
def test_notification_pagination_handles_bad_pages(employee_client, employee, page):
    """Robustness: a non-numeric or too-large page number still returns the page."""
    make_application(employee, "Annual Leave")

    response = employee_client.get(f"/notifications/?page={page}")

    assert response.status_code == 200


# ---- Admin list page ----

def test_admin_list_denied_for_employee(employee_client):
    """FR6: an employee cannot open the admin list."""
    assert employee_client.get("/leaves/admin/").status_code == 404


@pytest.mark.parametrize(
    "query, expected_count",
    [("", 2), ("?status=Pending", 1), ("?q=emp1", 2), ("?q=nobody", 0),
     ("?q=Sick", 1), ("?date_from=2026-12-15", 1), ("?date_to=2026-12-05", 1)],
)
def test_admin_list_filters(admin_client, employee, query, expected_count):
    """FR6: the admin list filters by status, search text and dates."""
    make_application(employee, "Annual Leave", "2026-12-01", "2026-12-03")
    make_application(employee, "Sick Leave", "2026-12-20", "2026-12-22")
    LeaveApplication.objects.filter(leave_type__name="Sick Leave").update(status="Approved")

    response = admin_client.get(f"/leaves/admin/{query}")

    assert len(response.context["leave_applications"]) == expected_count


@pytest.mark.parametrize("page", ["abc", "999"])
def test_admin_list_pagination_handles_bad_pages(admin_client, employee, page):
    """Robustness: bad page numbers fall back to a valid page."""
    make_application(employee, "Annual Leave")

    assert admin_client.get(f"/leaves/admin/?page={page}").status_code == 200


# ---- Login and logout ----

def test_login_redirects_employee_home(employee):
    """Login: a valid employee login goes to the dashboard."""
    response = Client().post("/accounts/login/", {"username": "emp1", "password": PASSWORD})

    assert response.status_code == 302
    assert response["Location"] == "/"


def test_login_redirects_admin_to_admin_site(admin_user):
    """Login: a valid admin login goes to /admin/."""
    response = Client().post("/accounts/login/", {"username": "admin1", "password": PASSWORD})

    assert response["Location"] == "/admin/"


def test_login_follows_next_parameter(employee):
    """Login: an employee login follows the next parameter."""
    response = Client().post(
        "/accounts/login/?next=/balance/", {"username": "emp1", "password": PASSWORD}
    )

    assert response["Location"] == "/balance/"


def test_login_with_wrong_password_shows_form(employee):
    """Login: a wrong password shows the form again, with no session."""
    client = Client()
    response = client.post("/accounts/login/", {"username": "emp1", "password": "wrong"})

    assert response.status_code == 200
    assert "_auth_user_id" not in client.session


def test_logged_in_user_visiting_login_is_redirected(employee_client, admin_client):
    """Login: an already logged-in user is redirected away from the login page."""
    assert employee_client.get("/accounts/login/")["Location"] == "/"
    assert admin_client.get("/accounts/login/")["Location"] == "/admin/"


def test_logout_ends_session(employee_client):
    """Logout: the session is ended and the user is sent to the login page."""
    response = employee_client.get("/logout/")

    assert response.status_code == 302
    assert "_auth_user_id" not in employee_client.session