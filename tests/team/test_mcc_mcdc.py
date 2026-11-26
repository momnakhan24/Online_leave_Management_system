"""MCC (multiple condition coverage) and MC/DC tests for two compound rules.

Rule A (BR2, overlap in /apply/): refused when ALL four conditions hold
  C1 existing application belongs to the same user
  C2 existing application is Pending (the implemented rule only checks Pending)
  C3 existing start date <= new start date
  C4 existing end date   >= new start date
Rule B (FR5, users/views.py leave_detail): denied when
  A the application belongs to another user AND B the viewer is not an admin.
See docs/MCC_MCDC.md for the truth tables and the MC/DC pairs.
"""
import itertools

import pytest
from django.contrib.auth import get_user_model
from django.test import Client

from users.models import LeaveApplication, LeaveType
from conftest import PASSWORD

NEW_START, NEW_END = "2026-12-10", "2026-12-12"
# existing (start, end) for each (C3, C4) pair relative to the new start 2026-12-10
DATES = {
    (True, True): ("2026-12-05", "2026-12-15"),
    (True, False): ("2026-12-01", "2026-12-05"),
    (False, True): ("2026-12-15", "2026-12-20"),
    (False, False): ("2026-12-15", "2026-12-05"),  # needs an end-before-start record
}

ROWS = list(itertools.product([True, False], repeat=4))


def row_id(index, row):
    return f"R{index + 1:02d}_" + "".join("T" if value else "F" for value in row)


@pytest.mark.parametrize("row", ROWS, ids=[row_id(i, r) for i, r in enumerate(ROWS)])
def test_overlap_rule_all_16_combinations(employee_client, employee, row):
    """MCC for BR2: the application is refused only when C1, C2, C3 and C4 are all true."""
    c1, c2, c3, c4 = row
    owner = employee if c1 else get_user_model().objects.create_user(
        username="emp2", password=PASSWORD, email="emp2@example.test"
    )
    start, end = DATES[(c3, c4)]
    LeaveApplication.objects.create(
        user=owner, leave_type=LeaveType.objects.get(name="Annual Leave"),
        start_date=start, end_date=end, message="existing",
        status="Pending" if c2 else "Rejected",
    )

    employee_client.post(
        "/apply/",
        {"leave_type": "Annual Leave", "startDate": NEW_START, "endDate": NEW_END, "message": "new"},
    )

    created = LeaveApplication.objects.filter(user=employee, start_date=NEW_START).count()
    expected_refused = all(row)
    assert created == (0 if expected_refused else 1)


# MC/DC pairs for rule A: base case TTTT is refused, flipping ONE condition allows it.
MCDC_PAIRS = [
    ("C1", (True, True, True, True), (False, True, True, True)),
    ("C2", (True, True, True, True), (True, False, True, True)),
    ("C3", (True, True, True, True), (True, True, False, True)),
    ("C4", (True, True, True, True), (True, True, True, False)),
]


@pytest.mark.parametrize("name, base, flipped", MCDC_PAIRS, ids=[p[0] for p in MCDC_PAIRS])
def test_overlap_rule_mcdc_pairs(name, base, flipped):
    """Each pair differs in exactly one condition and the decision outcome differs."""
    differing = [i for i, (a, b) in enumerate(zip(base, flipped)) if a != b]
    assert len(differing) == 1
    assert all(base) is True and all(flipped) is False


@pytest.mark.parametrize(
    "viewer, owner_is_viewer, expected_status",
    [
        ("employee", False, 404),   # A true,  B true  -> denied
        ("admin", False, 200),      # A true,  B false -> allowed
        ("employee", True, 200),    # A false, B true  -> allowed
        ("admin", True, 200),       # A false, B false -> allowed
    ],
    ids=["TT_denied", "TF_admin_views_other", "FT_owner_views_own", "FF_admin_views_own"],
)
def test_detail_access_rule_all_4_combinations(
    employee, admin_user, viewer, owner_is_viewer, expected_status
):
    """MCC for FR5 access: denied only when the viewer is not the owner AND not an admin."""
    viewer_user = employee if viewer == "employee" else admin_user
    owner = viewer_user if owner_is_viewer else (
        admin_user if viewer == "employee" else employee
    )
    application = LeaveApplication.objects.create(
        user=owner, leave_type=LeaveType.objects.get(name="Annual Leave"),
        start_date="2026-12-01", end_date="2026-12-03", message="m",
    )
    client = Client()
    client.login(username=viewer_user.username, password=PASSWORD)

    assert client.get(f"/leave/{application.id}/").status_code == expected_status


@pytest.mark.xfail(strict=True, reason="DEF-009: open defect, see GitHub Issues")
def test_overlap_with_approved_leave_is_refused(employee_client, employee):
    """BR2 (assumption: active means Pending or Approved): approved leave blocks the dates."""
    LeaveApplication.objects.create(
        user=employee, leave_type=LeaveType.objects.get(name="Annual Leave"),
        start_date="2026-12-05", end_date="2026-12-10", message="existing", status="Approved",
    )

    employee_client.post(
        "/apply/",
        {"leave_type": "Annual Leave", "startDate": "2026-12-07", "endDate": "2026-12-08", "message": "new"},
    )

    assert LeaveApplication.objects.filter(user=employee, start_date="2026-12-07").count() == 0


@pytest.mark.xfail(strict=True, reason="DEF-009: open defect, see GitHub Issues")
def test_new_range_that_runs_into_existing_leave_is_refused(employee_client, employee):
    """BR2: a new range that starts before an existing Pending leave but overlaps it is refused."""
    LeaveApplication.objects.create(
        user=employee, leave_type=LeaveType.objects.get(name="Annual Leave"),
        start_date="2026-12-08", end_date="2026-12-12", message="existing", status="Pending",
    )

    employee_client.post(
        "/apply/",
        {"leave_type": "Annual Leave", "startDate": "2026-12-05", "endDate": "2026-12-09", "message": "new"},
    )

    assert LeaveApplication.objects.filter(user=employee, start_date="2026-12-05").count() == 0