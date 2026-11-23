"""Workflow 1: employee applies for leave (FR1, FR2, FR3)."""
from users.models import LeaveApplication, LeaveBalance


def apply(client, start, end, leave_type="Annual Leave", message="Family event"):
    return client.post(
        "/apply/",
        {"leave_type": leave_type, "startDate": start, "endDate": end, "message": message},
    )


def test_apply_creates_pending_application(employee_client, employee):
    """FR1, FR2: a valid application is stored as Pending."""
    response = apply(employee_client, "2026-12-01", "2026-12-03")

    assert response.status_code == 302
    application = LeaveApplication.objects.get(user=employee)
    assert application.status == "Pending"
    assert str(application.start_date) == "2026-12-01"
    assert str(application.end_date) == "2026-12-03"


def test_apply_does_not_change_balance(employee_client, employee):
    """FR2: applying never deducts from the balance."""
    apply(employee_client, "2026-12-01", "2026-12-03")

    assert LeaveBalance.objects.get(user=employee).annual_leave == 20


def test_apply_requires_login(client, leave_types):
    """Anonymous users are sent to the login page and nothing is created."""
    response = apply(client, "2026-12-01", "2026-12-03")

    assert response.status_code == 302
    assert "/accounts/login/" in response["Location"]
    assert LeaveApplication.objects.count() == 0


def test_overlapping_application_is_refused(employee_client, employee):
    """FR3 / BR2: a second application on the same dates creates no record."""
    apply(employee_client, "2026-12-01", "2026-12-03")
    apply(employee_client, "2026-12-01", "2026-12-03")

    assert LeaveApplication.objects.filter(user=employee).count() == 1