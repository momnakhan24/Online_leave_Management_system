"""Cancel rules and record visibility (FR4, FR5, BR3) plus HTTP method safety."""
import pytest

from users.models import LeaveBalance


def cancel(client, application):
    return client.get(f"/leave/{application.id}/cancel/")


def test_owner_cancels_pending_application(
    employee_client, employee, pending_application
):
    """FR4 / BR3: the owner can move Pending to Cancelled, balance unchanged."""
    cancel(employee_client, pending_application)

    pending_application.refresh_from_db()
    assert pending_application.status == "Cancelled"
    assert LeaveBalance.objects.get(user=employee).annual_leave == 20


def test_other_employee_cannot_cancel(other_employee_client, pending_application):
    """FR4: another employee gets 404 and the application stays Pending."""
    response = cancel(other_employee_client, pending_application)

    pending_application.refresh_from_db()
    assert response.status_code == 404
    assert pending_application.status == "Pending"


def test_approved_application_cannot_be_cancelled(
    admin_client, employee_client, pending_application
):
    """BR3: Approved is final, so cancelling it changes nothing."""
    admin_client.get(f"/leaves/admin/{pending_application.id}/approve/")
    cancel(employee_client, pending_application)

    pending_application.refresh_from_db()
    assert pending_application.status == "Approved"


def test_employee_cannot_view_another_employees_application(
    other_employee_client, pending_application
):
    """FR5: another employee gets 404 on the detail page."""
    response = other_employee_client.get(f"/leave/{pending_application.id}/")

    assert response.status_code == 404


def test_owner_and_admin_can_view_application(
    employee_client, admin_client, pending_application
):
    """FR5, FR6: the owner and an admin can open the detail page."""
    url = f"/leave/{pending_application.id}/"

    assert employee_client.get(url).status_code == 200
    assert admin_client.get(url).status_code == 200


@pytest.mark.xfail(strict=True, reason="DEF-005: open defect, see GitHub Issues")
def test_approve_by_plain_get_is_refused(admin_client, pending_application):
    """Assumption A: a state-changing action must not run on a plain GET."""
    admin_client.get(f"/leaves/admin/{pending_application.id}/approve/")

    pending_application.refresh_from_db()
    assert pending_application.status == "Pending"


@pytest.mark.xfail(strict=True, reason="DEF-005: open defect, see GitHub Issues")
def test_cancel_by_plain_get_is_refused(employee_client, pending_application):
    """Assumption A: a state-changing action must not run on a plain GET."""
    cancel(employee_client, pending_application)

    pending_application.refresh_from_db()
    assert pending_application.status == "Pending"