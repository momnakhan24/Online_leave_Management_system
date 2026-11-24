"""Workflow 2: admin approves or rejects leave (FR6 to FR10, BR3, BR4)."""
import pytest

from users.models import LeaveBalance, Notification


def approve(client, application):
    return client.get(f"/leaves/admin/{application.id}/approve/")


def reject(client, application, reason):
    return client.post(
        f"/leaves/admin/{application.id}/reject/", {"rejection_reason": reason}
    )


def annual_balance(user):
    return LeaveBalance.objects.get(user=user).annual_leave


def test_approve_sets_status_and_deducts_duration(
    admin_client, admin_user, employee, pending_application
):
    """FR7: approval marks Approved and deducts 3 days (20 to 17)."""
    approve(admin_client, pending_application)

    pending_application.refresh_from_db()
    assert pending_application.status == "Approved"
    assert pending_application.approved_by == admin_user
    assert annual_balance(employee) == 17


def test_approve_creates_notification(admin_client, employee, pending_application):
    """FR10: the employee is notified of the approval."""
    approve(admin_client, pending_application)

    assert Notification.objects.filter(user=employee, message__contains="approved").count() == 1


def test_reject_stores_reason_and_keeps_balance(
    admin_client, employee, pending_application
):
    """FR8: rejection stores the reason and does not touch the balance."""
    reject(admin_client, pending_application, "Team is short-staffed")

    pending_application.refresh_from_db()
    assert pending_application.status == "Rejected"
    assert pending_application.rejection_reason == "Team is short-staffed"
    assert annual_balance(employee) == 20


def test_second_approval_does_not_deduct_again(
    admin_client, employee, pending_application
):
    """FR9 / BR3: approving an Approved application changes nothing."""
    approve(admin_client, pending_application)
    approve(admin_client, pending_application)

    assert annual_balance(employee) == 17


def test_reject_after_approval_is_refused(admin_client, pending_application):
    """FR9 / BR3: an Approved application cannot be rejected."""
    approve(admin_client, pending_application)
    reject(admin_client, pending_application, "Changed my mind")

    pending_application.refresh_from_db()
    assert pending_application.status == "Approved"


def test_employee_cannot_approve(employee_client, employee, pending_application):
    """FR6: a non-admin gets 404 and the application stays Pending."""
    response = approve(employee_client, pending_application)

    pending_application.refresh_from_db()
    assert response.status_code == 404
    assert pending_application.status == "Pending"
    assert annual_balance(employee) == 20


@pytest.mark.xfail(strict=True, reason="DEF-004: open defect, see GitHub Issues")
def test_reject_with_empty_reason_is_refused(admin_client, pending_application):
    """BR4: rejection requires a non-empty reason."""
    reject(admin_client, pending_application, "")

    pending_application.refresh_from_db()
    assert pending_application.status == "Pending"