"""API tests driven by the generated EP and 3-point BVA data (tests/team/data/api_cases.json).

Oracle: a valid case must succeed and change the shared records; an invalid case must
be refused, create or change nothing, and never return a server error (5xx).
Cases the application gets wrong are marked xfail with the defect they expose.
"""
from datetime import date, timedelta

import pytest

from api_helpers import (EXECUTED_CASES, admin_api, emp_api, load_cases,  # noqa: F401
                         other_api, anonymous_api)
from users.models import LeaveApplication, LeaveBalance, LeaveType

BASE_FORM = {"leave_type": "Annual Leave", "startDate": "2027-01-04",
             "endDate": "2027-01-04", "message": "api test"}


def known_defect(case):
    """Map a generated case to the logged defect it is known to expose, if any."""
    name, klass = case["input"], case["class"]
    if name == "durationDays":
        if klass in ("invalid_below_min", "min-1"):
            return "DEF-001"
        if klass in ("invalid_above_max", "max+1"):
            return "DEF-002"
    if name in ("startDate", "endDate") and not case["valid"]:
        return "DEF-003"
    if name == "rejection_reason" and not case["valid"]:
        return "DEF-004"
    return None


def with_defect_mark(request, case):
    defect = known_defect(case)
    if defect:
        request.applymarker(pytest.mark.xfail(strict=True, reason=f"{defect}: open defect"))


def build_apply_form(case):
    form = dict(BASE_FORM)
    name, value = case["input"], case["value"]
    if name == "durationDays":
        start = date.fromisoformat(form["startDate"])
        form["endDate"] = (start + timedelta(days=value - 1)).isoformat()
    elif value is None:
        form.pop(name)
    else:
        form[name] = value
    return form


def ids(cases):
    return [c["id"] for c in cases]


# ---------------- POST /apply/ ----------------

APPLY_CASES = load_cases("applyLeave")


@pytest.mark.parametrize("case", APPLY_CASES, ids=ids(APPLY_CASES))
def test_apply_leave_generated(case, request, emp_api, employee):
    with_defect_mark(request, case)
    response = emp_api.call("applyLeave", "POST", "/apply/", build_apply_form(case))
    EXECUTED_CASES.add(case["id"])

    created = LeaveApplication.objects.filter(user=employee).count()
    assert response.status_code < 500, "server error on input"
    if case["valid"]:
        assert response.status_code == 302
        assert created == 1
        assert LeaveApplication.objects.get(user=employee).status == "Pending"
    else:
        assert created == 0
    # the balance is only ever changed by an approval
    assert LeaveBalance.objects.get(user=employee).annual_leave == 20


# ---------------- POST /leaves/admin/{id}/reject/ (reason) ----------------

REJECT_CASES = load_cases("rejectLeave")
REASON_CASES = [c for c in REJECT_CASES if c["input"] == "rejection_reason"]
ID_REJECT_CASES = [c for c in REJECT_CASES if c["input"] == "id"]


def make_pending(employee, count):
    leave_type = LeaveType.objects.get(name="Annual Leave")
    apps = []
    for i in range(count):
        apps.append(LeaveApplication.objects.create(
            user=employee, leave_type=leave_type, start_date=f"2030-01-{i + 1:02d}",
            end_date=f"2030-01-{i + 1:02d}", message="seed", status="Pending"))
    return apps


@pytest.mark.parametrize("case", REASON_CASES, ids=ids(REASON_CASES))
def test_reject_reason_generated(case, request, admin_api, employee):
    with_defect_mark(request, case)
    application = make_pending(employee, 1)[0]
    form = {} if case["value"] is None else {"rejection_reason": case["value"]}

    response = admin_api.call("rejectLeave", "POST", f"/leaves/admin/{application.id}/reject/", form)
    EXECUTED_CASES.add(case["id"])

    application.refresh_from_db()
    assert response.status_code < 500
    if case["valid"]:
        assert application.status == "Rejected"
        assert application.rejection_reason == case["value"]
    else:
        assert application.status == "Pending"
    assert LeaveBalance.objects.get(user=employee).annual_leave == 20


# ---------------- application number {id} on approve, reject and cancel ----------------

def resolve_id(value, apps):
    """Spec values 1..N mean the N-th seeded application; anything else is used as given."""
    if isinstance(value, int) and 1 <= value <= len(apps):
        return str(apps[value - 1].id), apps[value - 1]
    return str(value), None


def run_id_case(case, apps, caller, operation, method, path_fmt, data, expected_status_valid,
                expected_state):
    path_id, target = resolve_id(case["value"], apps)
    response = caller.call(operation, method, path_fmt.format(id=path_id), data)
    EXECUTED_CASES.add(case["id"])
    states = [LeaveApplication.objects.get(pk=a.pk).status for a in apps]
    if case["valid"]:
        assert response.status_code == expected_status_valid
        assert LeaveApplication.objects.get(pk=target.pk).status == expected_state
        assert states.count("Pending") == len(apps) - 1
    else:
        assert response.status_code == 404
        assert states.count("Pending") == len(apps)


APPROVE_CASES = load_cases("approveLeave")
CANCEL_CASES = load_cases("cancelLeave")


@pytest.mark.parametrize("case", APPROVE_CASES, ids=ids(APPROVE_CASES))
def test_approve_id_generated(case, admin_api, employee):
    apps = make_pending(employee, 10)
    run_id_case(case, apps, admin_api, "approveLeave", "GET", "/leaves/admin/{id}/approve/",
                None, 302, "Approved")


@pytest.mark.parametrize("case", ID_REJECT_CASES, ids=ids(ID_REJECT_CASES))
def test_reject_id_generated(case, admin_api, employee):
    apps = make_pending(employee, 10)
    run_id_case(case, apps, admin_api, "rejectLeave", "POST", "/leaves/admin/{id}/reject/",
                {"rejection_reason": "api reason"}, 302, "Rejected")


@pytest.mark.parametrize("case", CANCEL_CASES, ids=ids(CANCEL_CASES))
def test_cancel_id_generated(case, emp_api, employee):
    apps = make_pending(employee, 10)
    run_id_case(case, apps, emp_api, "cancelLeave", "GET", "/leave/{id}/cancel/",
                None, 302, "Cancelled")