"""Workflow 1 tests that check rules BR1 and input validation.

These tests describe the EXPECTED behaviour from docs/TEST_BASIS.md.
"""
import pytest
from django.test import Client

from users.models import LeaveApplication
from conftest import PASSWORD


@pytest.fixture
def quiet_client(employee):
    """Like employee_client, but returns the 500 page instead of raising."""
    client = Client(raise_request_exception=False)
    assert client.login(username="emp1", password=PASSWORD)
    return client


def apply(client, start, end, leave_type="Annual Leave", message="Test"):
    return client.post(
        "/apply/",
        {"leave_type": leave_type, "startDate": start, "endDate": end, "message": message},
    )


@pytest.mark.xfail(strict=True, reason="DEF-001: open defect, see GitHub Issues")
def test_end_date_before_start_date_is_refused(employee_client, employee):
    """BR1: duration must be at least 1 day, so end before start is refused."""
    apply(employee_client, "2026-12-10", "2026-12-01")

    assert LeaveApplication.objects.filter(user=employee).count() == 0


@pytest.mark.xfail(strict=True, reason="DEF-002: open defect, see GitHub Issues")
def test_leave_longer_than_balance_is_refused(employee_client, employee):
    """BR1: duration above the 20-day annual balance is refused."""
    apply(employee_client, "2027-01-01", "2027-02-15")  # 46 days

    assert LeaveApplication.objects.filter(user=employee).count() == 0


@pytest.mark.xfail(strict=True, reason="DEF-003: open defect, see GitHub Issues")
def test_invalid_date_text_does_not_crash(quiet_client, employee):
    """Input validation: a non-date value must not cause a server error."""
    response = apply(quiet_client, "notadate", "2026-12-01")

    assert response.status_code < 500
    assert LeaveApplication.objects.filter(user=employee).count() == 0