"""Profile, password, calendar, registration, models and the Django admin screens.

The admin site is the main screen for admins (admin login redirects to /admin/),
so its approve and reject actions are tested against the same rules as the
custom views (FR6 to FR10, BR3).
"""
import pytest
from django.test import Client

from users.models import (
    Awards, Employee_Details, LeaveApplication, LeaveBalance, LeaveType,
    Notice, Notification, Profile,
)


def annual_balance(user):
    return LeaveBalance.objects.get(user=user).annual_leave


# ---- Profile and password pages (employee) ----

def test_profile_page_loads(employee_client):
    assert employee_client.get("/profile/").status_code == 200


def test_profile_update_saves_role_and_department(employee_client, employee):
    response = employee_client.post(
        "/profile/", {"update_profile": "1", "role": "Tester", "department": "QA"}
    )

    profile = Profile.objects.get(user=employee)
    assert response.status_code == 302
    assert (profile.role, profile.department) == ("Tester", "QA")


def test_profile_update_with_too_long_role_shows_errors(employee_client, employee):
    response = employee_client.post(
        "/profile/", {"update_profile": "1", "role": "x" * 60, "department": "QA"}
    )

    assert response.status_code == 200
    assert Profile.objects.get(user=employee).role != "x" * 60


def test_profile_contact_update_saves_phone(employee_client, employee):
    response = employee_client.post(
        "/profile/", {"update_contact": "1", "phone_number": "0300123", "address": "Here"}
    )

    assert response.status_code == 302
    assert Profile.objects.get(user=employee).phone_number == "0300123"


def test_profile_contact_with_too_long_phone_shows_errors(employee_client, employee):
    response = employee_client.post(
        "/profile/", {"update_contact": "1", "phone_number": "1" * 20, "address": "Here"}
    )

    assert response.status_code == 200
    assert Profile.objects.get(user=employee).phone_number != "1" * 20


def test_change_password_page_loads(employee_client):
    assert employee_client.get("/change_password/").status_code == 200


@pytest.mark.xfail(strict=True, reason="DEF-008: open defect, see GitHub Issues")
@pytest.mark.parametrize("url", ["/update_profile/", "/update_contact/"])
def test_edit_pages_load(employee_client, url):
    """The edit pages must open (the template they use does not exist)."""
    assert employee_client.get(url).status_code == 200


def test_update_profile_page_saves(employee_client, employee):
    response = employee_client.post(
        "/update_profile/", {"role": "Lead", "department": "Ops"}
    )

    assert response.status_code == 302
    assert Profile.objects.get(user=employee).role == "Lead"


@pytest.mark.xfail(strict=True, reason="DEF-008: open defect, see GitHub Issues")
def test_update_profile_page_rejects_bad_data(employee_client, employee):
    response = employee_client.post(
        "/update_profile/", {"role": "x" * 60, "department": "Ops"}
    )

    assert response.status_code == 200


def test_update_contact_page_saves(employee_client, employee):
    response = employee_client.post(
        "/update_contact/", {"phone_number": "0311999", "address": "There"}
    )

    assert response.status_code == 302
    assert Profile.objects.get(user=employee).address == "There"


@pytest.mark.xfail(strict=True, reason="DEF-008: open defect, see GitHub Issues")
def test_update_contact_page_rejects_bad_data(employee_client):
    response = employee_client.post(
        "/update_contact/", {"phone_number": "1" * 20, "address": "There"}
    )

    assert response.status_code == 200


def test_change_password_success_keeps_user_logged_in(employee_client, employee):
    response = employee_client.post(
        "/change_password/",
        {"old_password": "Test@12345", "new_password1": "Brand#New9876",
         "new_password2": "Brand#New9876"},
    )

    employee.refresh_from_db()
    assert response.status_code == 302
    assert employee.check_password("Brand#New9876")
    assert employee_client.get("/balance/").status_code == 200


def test_change_password_with_wrong_old_password_is_refused(employee_client, employee):
    response = employee_client.post(
        "/change_password/",
        {"old_password": "wrong", "new_password1": "Brand#New9876",
         "new_password2": "Brand#New9876"},
    )

    employee.refresh_from_db()
    assert response.status_code == 200
    assert employee.check_password("Test@12345")


# ---- Team calendar (admin only, FR6) ----

def test_calendar_denied_for_anonymous_and_employee(client, employee_client):
    anonymous = client.get("/calendar/")
    assert anonymous.status_code == 302
    assert "/accounts/login/" in anonymous["Location"]
    assert employee_client.get("/calendar/").status_code == 404


@pytest.mark.parametrize("query", ["", "?year=2026&month=12", "?year=2026&month=1",
                                   "?year=2026&month=0", "?year=2026&month=13"])
def test_calendar_loads_for_admin(admin_client, query):
    assert admin_client.get(f"/calendar/{query}").status_code == 200


def test_calendar_lists_approved_leave_only(admin_client, pending_application):
    month_url = "/calendar/?year=2026&month=12"
    assert len(admin_client.get(month_url).context["approved_leaves"]) == 0

    admin_client.get(f"/leaves/admin/{pending_application.id}/approve/")

    assert len(admin_client.get(month_url).context["approved_leaves"]) == 1


# ---- Registration ----

REGISTER_DATA = {
    "username": "newuser", "password1": "Str0ng#Pass1234", "password2": "Str0ng#Pass1234",
    "first_name": "New", "last_name": "User", "email": "new@example.test",
    "role": "Tester", "department": "QA",
}


def test_register_form_loads(client):
    assert client.get("/accounts/register/").status_code == 200


def test_register_with_mismatched_passwords_shows_errors(client, django_user_model):
    data = dict(REGISTER_DATA, password2="different")

    response = client.post("/accounts/register/", data)

    assert response.status_code == 200
    assert not django_user_model.objects.filter(username="newuser").exists()


def test_logged_in_user_is_redirected_from_register(employee_client):
    assert employee_client.get("/accounts/register/")["Location"] == "/"


@pytest.mark.xfail(strict=True, reason="DEF-006: open defect, see GitHub Issues")
def test_register_creates_account_and_logs_in(leave_types, django_user_model):
    client = Client(raise_request_exception=False)

    response = client.post("/accounts/register/", REGISTER_DATA)

    assert response.status_code == 302
    assert django_user_model.objects.get(username="newuser").profile is not None


# ---- Models ----

def test_model_text_representations(employee, pending_application):
    pending_application.refresh_from_db()
    notice = Notice.objects.create(vacancy="Clerk", date="2026-12-01", month="December",
                                   announcements="Hiring")
    award = Awards.objects.create(award="Best Team")
    detail = Employee_Details.objects.create(
        user=employee, first_name="A", last_name="B", email="a@b.test",
        role="r", department="d",
    )
    note = Notification.objects.create(user=employee, message="hello")

    assert str(LeaveType.objects.get(name="Annual Leave")) == "Annual Leave"
    assert str(pending_application) == "emp1 - Annual Leave"
    assert str(LeaveBalance.objects.get(user=employee)) == "emp1 - Leave Balance"
    assert str(note) == "Notification for emp1"
    assert str(Profile.objects.get(user=employee)) == "Profile of emp1"
    assert str(notice) == "Clerk"
    assert str(award) == "Best Team"
    assert str(detail) == "Profile of emp1"
    assert pending_application.duration == 3


# ---- Django admin: approve and reject actions ----

CHANGELIST = "/admin/users/leaveapplication/"


def run_action(client, action, application, extra=None):
    data = {"action": action, "_selected_action": [application.id]}
    data.update(extra or {})
    return client.post(CHANGELIST, data, follow=True)


def test_admin_bulk_approve_sets_status_and_notifies(
    admin_client, employee, pending_application
):
    """FR7, FR10 through the admin bulk action."""
    run_action(admin_client, "approve_selected", pending_application)

    pending_application.refresh_from_db()
    assert pending_application.status == "Approved"
    assert Notification.objects.filter(user=employee, message__contains="approved").count() == 1


@pytest.mark.xfail(strict=True, reason="DEF-007: open defect, see GitHub Issues")
def test_admin_bulk_approve_deducts_balance(admin_client, employee, pending_application):
    """FR7: approving through the admin must deduct 3 days, like the custom view."""
    run_action(admin_client, "approve_selected", pending_application)

    assert annual_balance(employee) == 17


def test_admin_bulk_reject_uses_default_reason(admin_client, employee, pending_application):
    """FR8 through the admin bulk action (default reason text)."""
    run_action(admin_client, "reject_selected", pending_application)

    pending_application.refresh_from_db()
    assert pending_application.status == "Rejected"
    assert pending_application.rejection_reason == "No reason provided."
    assert annual_balance(employee) == 20


def test_admin_bulk_actions_skip_processed_applications(admin_client, pending_application):
    """FR9 / BR3: bulk approve then bulk reject leaves the application Approved."""
    run_action(admin_client, "approve_selected", pending_application)
    run_action(admin_client, "reject_selected", pending_application)

    pending_application.refresh_from_db()
    assert pending_application.status == "Approved"


def change_url(application):
    return f"{CHANGELIST}{application.id}/change/"


def test_admin_change_form_approve_button(admin_client, pending_application):
    admin_client.post(change_url(pending_application), {"_approve": "1"})

    pending_application.refresh_from_db()
    assert pending_application.status == "Approved"


def test_admin_change_form_reject_button_stores_reason(admin_client, pending_application):
    admin_client.post(
        change_url(pending_application), {"_reject": "1", "rejection_reason": "Busy period"}
    )

    pending_application.refresh_from_db()
    assert pending_application.status == "Rejected"
    assert pending_application.rejection_reason == "Busy period"


def test_admin_change_form_buttons_ignore_processed_applications(
    admin_client, pending_application
):
    """BR3: pressing approve or reject on a processed application changes nothing."""
    admin_client.post(change_url(pending_application), {"_approve": "1"})
    admin_client.post(change_url(pending_application), {"_reject": "1", "rejection_reason": "x"})
    admin_client.post(change_url(pending_application), {"_approve": "1"})

    pending_application.refresh_from_db()
    assert pending_application.status == "Approved"


def test_admin_change_form_save_without_button(admin_client, pending_application):
    admin_client.post(change_url(pending_application), {})

    pending_application.refresh_from_db()
    assert pending_application.status == "Pending"


def test_admin_screens_require_superuser(employee_client):
    assert employee_client.get("/admin/").status_code in (302, 403, 404)
    assert employee_client.get(CHANGELIST).status_code in (302, 403, 404)


# ---- Django admin: every screen renders ----

def test_admin_dashboard_with_and_without_applications(admin_client, pending_application):
    assert admin_client.get("/admin/").context["approval_rate"] == 0

    admin_client.get(f"/leaves/admin/{pending_application.id}/approve/")

    assert admin_client.get("/admin/").context["approval_rate"] == 100.0


def test_admin_dashboard_with_no_applications(admin_client):
    assert admin_client.get("/admin/").context["approval_rate"] == 0


def test_admin_lists_render_for_all_models(admin_client, employee, pending_application):
    approved = LeaveApplication.objects.create(
        user=employee, leave_type=pending_application.leave_type,
        start_date="2027-01-01", end_date="2027-01-01", message="m",
    )
    rejected = LeaveApplication.objects.create(
        user=employee, leave_type=pending_application.leave_type,
        start_date="2027-02-01", end_date="2027-02-02", message="m",
    )
    admin_client.get(f"/leaves/admin/{approved.id}/approve/")
    admin_client.post(f"/leaves/admin/{rejected.id}/reject/", {"rejection_reason": "No"})
    Notification.objects.create(user=employee, message="short")
    Notification.objects.create(user=employee, message="long " * 30, is_read=True)
    Notice.objects.create(vacancy="Clerk", date="2026-12-01", month="December",
                          announcements="Hiring")
    Awards.objects.create(award="Best Team")
    Employee_Details.objects.create(user=employee, first_name="A", last_name="B",
                                    email="a@b.test", role="r", department="d")

    for model in ["leaveapplication", "profile", "leavebalance", "notification",
                  "leavetype", "awards", "notice", "employee_details", "user"]:
        assert admin_client.get(f"/admin/users/{model}/").status_code == 200, model


def test_admin_notification_bulk_read_and_unread(admin_client, employee):
    note = Notification.objects.create(user=employee, message="hello")
    url = "/admin/users/notification/"

    admin_client.post(url, {"action": "mark_as_read", "_selected_action": [note.id]})
    note.refresh_from_db()
    assert note.is_read is True

    admin_client.post(url, {"action": "mark_as_unread", "_selected_action": [note.id]})
    note.refresh_from_db()
    assert note.is_read is False


def test_admin_readonly_fields_without_an_object():
    """The add form is disabled, but the helper still returns the base read-only fields."""
    from users.admin import admin_site

    model_admin = admin_site._registry[LeaveApplication]

    assert "status" not in model_admin.get_readonly_fields(None)
    assert "status" in model_admin.get_readonly_fields(None, obj=LeaveApplication())