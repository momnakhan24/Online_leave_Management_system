"""API level rule tests over real HTTP: cross-workflow read-back, repeated requests,
state transitions and decision tables (BR1 to BR4, FR3 to FR9)."""
import itertools

import pytest

from api_helpers import admin_api, anonymous_api, emp_api, other_api  # noqa: F401
from users.models import LeaveApplication, LeaveBalance, LeaveType

FORM = {"leave_type": "Annual Leave", "startDate": "2027-01-04",
        "endDate": "2027-01-06", "message": "api test"}  # 3 days


def annual(user):
    return LeaveBalance.objects.get(user=user).annual_leave


def make_app(user, status="Pending", start="2027-01-04", end="2027-01-06"):
    return LeaveApplication.objects.create(
        user=user, leave_type=LeaveType.objects.get(name="Annual Leave"),
        start_date=start, end_date=end, message="seed", status=status)


def approve(admin_api, app):
    return admin_api.call("approveLeave", "GET", f"/leaves/admin/{app.id}/approve/")


def reject(admin_api, app, reason="api reason"):
    return admin_api.call("rejectLeave", "POST", f"/leaves/admin/{app.id}/reject/",
                          {"rejection_reason": reason})


def cancel(api, app):
    return api.call("cancelLeave", "GET", f"/leave/{app.id}/cancel/")


# ---------- cross-workflow: Workflow 1 writes, Workflow 2 changes, Workflow 1 reads ----------

def test_apply_then_approve_updates_shared_records(emp_api, admin_api, employee, admin_user):
    response = emp_api.call("applyLeave", "POST", "/apply/", FORM)
    app = LeaveApplication.objects.get(user=employee)
    assert response.status_code == 302 and app.status == "Pending"
    assert annual(employee) == 20

    approve(admin_api, app)

    app.refresh_from_db()
    assert app.status == "Approved" and app.approved_by == admin_user
    assert annual(employee) == 17
    page = emp_api.call("viewBalance", "GET", "/balance/")
    assert page.status_code == 200


def test_apply_then_reject_keeps_balance(emp_api, admin_api, employee):
    emp_api.call("applyLeave", "POST", "/apply/", FORM)
    app = LeaveApplication.objects.get(user=employee)

    reject(admin_api, app, "Short staffed")

    app.refresh_from_db()
    assert app.status == "Rejected" and app.rejection_reason == "Short staffed"
    assert annual(employee) == 20


def test_rejected_application_is_readable_by_owner_after_refusal(emp_api, employee):
    """After a rule rejection nothing is stored and the balance is unchanged."""
    bad = dict(FORM, leave_type="Unknown Leave")
    response = emp_api.call("applyLeave", "POST", "/apply/", bad)

    assert response.status_code == 404
    assert LeaveApplication.objects.filter(user=employee).count() == 0
    assert annual(employee) == 20


# ---------- repeated requests: no duplicates, no double effects ----------

def test_repeated_apply_creates_one_record(emp_api, employee):
    first = emp_api.call("applyLeave", "POST", "/apply/", FORM)
    second = emp_api.call("applyLeave", "POST", "/apply/", FORM)

    assert (first.status_code, second.status_code) == (302, 200)
    assert LeaveApplication.objects.filter(user=employee).count() == 1


def test_repeated_approve_deducts_once(admin_api, employee):
    app = make_app(employee)
    approve(admin_api, app)
    approve(admin_api, app)

    assert annual(employee) == 17


def test_repeated_reject_keeps_first_reason(admin_api, employee):
    app = make_app(employee)
    reject(admin_api, app, "first")
    reject(admin_api, app, "second")

    app.refresh_from_db()
    assert app.rejection_reason == "first"


def test_repeated_cancel_keeps_one_cancelled_record(emp_api, employee):
    app = make_app(employee)
    cancel(emp_api, app)
    cancel(emp_api, app)

    assert LeaveApplication.objects.filter(user=employee, status="Cancelled").count() == 1
    assert LeaveApplication.objects.filter(user=employee).count() == 1


# ---------- state transition testing (BR3): every state x every action ----------

STATES = ["Pending", "Approved", "Rejected", "Cancelled"]
ACTIONS = {"approve": "Approved", "reject": "Rejected", "cancel": "Cancelled"}


@pytest.mark.parametrize("state, action", list(itertools.product(STATES, ACTIONS)),
                         ids=[f"{s}-{a}" for s, a in itertools.product(STATES, ACTIONS)])
def test_state_transitions(state, action, admin_api, emp_api, employee):
    """Only Pending may change (3 allowed transitions); the other 9 are disallowed."""
    app = make_app(employee, status=state)

    if action == "approve":
        approve(admin_api, app)
    elif action == "reject":
        reject(admin_api, app)
    else:
        cancel(emp_api, app)

    app.refresh_from_db()
    expected = ACTIONS[action] if state == "Pending" else state
    assert app.status == expected


# ---------- decision tables (rules with two or more conditions) ----------

@pytest.mark.parametrize("caller_is_admin, is_pending, expected", [
    (True, True, "Approved"),
    (True, False, "Rejected"),     # admin, already processed: unchanged
    (False, True, "Pending"),      # employee: refused (404), unchanged
    (False, False, "Rejected"),    # employee and processed: unchanged
], ids=["admin-pending", "admin-processed", "employee-pending", "employee-processed"])
def test_decision_table_approve(caller_is_admin, is_pending, expected, admin_api, emp_api, employee):
    """Approve is effective only if the caller is an admin AND the application is Pending."""
    app = make_app(employee, status="Pending" if is_pending else "Rejected")
    caller = admin_api if caller_is_admin else emp_api

    caller.call("approveLeave", "GET", f"/leaves/admin/{app.id}/approve/")

    app.refresh_from_db()
    assert app.status == expected


@pytest.mark.parametrize("caller_is_owner, is_pending, expected", [
    (True, True, "Cancelled"),
    (True, False, "Approved"),     # owner, already processed: unchanged
    (False, True, "Pending"),      # other employee: refused (404), unchanged
    (False, False, "Approved"),    # other employee and processed: unchanged
], ids=["owner-pending", "owner-processed", "other-pending", "other-processed"])
def test_decision_table_cancel(caller_is_owner, is_pending, expected, emp_api, other_api, employee):
    """Cancel is effective only if the caller is the owner AND the application is Pending."""
    app = make_app(employee, status="Pending" if is_pending else "Approved")
    caller = emp_api if caller_is_owner else other_api

    cancel(caller, app)

    app.refresh_from_db()
    assert app.status == expected


OVERLAP_DATES = {  # existing (start, end) for each (C3, C4) against a new start of 2026-12-10
    (True, True): ("2026-12-05", "2026-12-15"),
    (True, False): ("2026-12-01", "2026-12-05"),
    (False, True): ("2026-12-15", "2026-12-20"),
}
OVERLAP_ROWS = [(c1, c2) + c34 for c1, c2 in itertools.product([True, False], repeat=2)
                for c34 in OVERLAP_DATES]


@pytest.mark.parametrize("c1, c2, c3, c4", OVERLAP_ROWS,
                         ids=["".join("T" if v else "F" for v in r) for r in OVERLAP_ROWS])
def test_decision_table_overlap(c1, c2, c3, c4, emp_api, other_api, employee, django_user_model):
    """BR2 over HTTP: refused only when same user AND Pending AND the dates overlap.
    The 4 rows with C3 = C4 = F cannot occur with valid data and are in the unit level MCC."""
    owner = employee if c1 else django_user_model.objects.get(username="emp2")
    start, end = OVERLAP_DATES[(c3, c4)]
    make_app(owner, status="Pending" if c2 else "Rejected", start=start, end=end)

    response = emp_api.call("applyLeave", "POST", "/apply/", dict(
        FORM, startDate="2026-12-10", endDate="2026-12-12"))

    refused = c1 and c2 and c3 and c4
    assert response.status_code == (200 if refused else 302)
    assert LeaveApplication.objects.filter(user=employee, start_date="2026-12-10").count() == (0 if refused else 1)


# ---------- access: anonymous and wrong role ----------

def test_balance_requires_login(anonymous_api):
    response = anonymous_api.call("viewBalance", "GET", "/balance/")

    assert response.status_code == 302 and "/accounts/login/" in response.headers["Location"]


def test_balance_page_for_logged_in_employee(emp_api):
    assert emp_api.call("viewBalance", "GET", "/balance/").status_code == 200


def test_employee_cannot_reject(emp_api, employee):
    app = make_app(employee)
    response = emp_api.call("rejectLeave", "POST", f"/leaves/admin/{app.id}/reject/",
                            {"rejection_reason": "nope"})

    app.refresh_from_db()
    assert response.status_code == 404 and app.status == "Pending"