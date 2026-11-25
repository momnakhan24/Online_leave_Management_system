# Traceability Matrix

Sources: docs/TEST_BASIS.md (requirements and rules), docs/RISK_REGISTER.md (risks), tests/team/ (tests).
Result key: PASS = test passes. XFAIL = test fails because of an open defect (marked in the test; see GitHub Issues).
Last updated at commit: c06af33 (22 tests: 16 passed, 6 xfailed).

## Requirements to tests

| Req | Requirement (short) | Tests | Result | Risks | Status |
|-----|---------------------|-------|--------|-------|--------|
| FR1 | Employee can submit an application | test_apply_leave.py::test_apply_creates_pending_application | PASS | PR2, PR3 | Covered |
| FR1 | (input validation) | test_apply_defects.py::test_invalid_date_text_does_not_crash | XFAIL (DEF-003) | PR3 | Defect found |
| FR2 | New application is Pending, balance unchanged | test_apply_leave.py::test_apply_creates_pending_application, test_apply_does_not_change_balance | PASS | PR1 | Covered |
| FR3 | Overlapping application is refused | test_apply_leave.py::test_overlapping_application_is_refused | PASS (same dates only) | PR4 | Partly covered |
| FR4 | Cancel only own Pending application | test_cancel_and_access.py::test_owner_cancels_pending_application, test_other_employee_cannot_cancel, test_approved_application_cannot_be_cancelled | PASS | PR5, PR6 | Covered |
| FR4 | (HTTP method) | test_cancel_and_access.py::test_cancel_by_plain_get_is_refused | XFAIL (DEF-005) | PR6 | Defect found |
| FR5 | Employee sees only own applications and balance | test_cancel_and_access.py::test_employee_cannot_view_another_employees_application, test_owner_and_admin_can_view_application | PASS | PR5 | Partly covered (balance page and list not tested) |
| FR6 | Only admin can process applications | test_approve_reject.py::test_employee_cannot_approve | PASS | PR5 | Partly covered (admin list page not tested) |
| FR7 | Approval sets Approved and deducts duration | test_approve_reject.py::test_approve_sets_status_and_deducts_duration | PASS | PR1 | Covered |
| FR7 | (HTTP method) | test_cancel_and_access.py::test_approve_by_plain_get_is_refused | XFAIL (DEF-005) | PR6 | Defect found |
| FR8 | Rejection stores reason and sets Rejected | test_approve_reject.py::test_reject_stores_reason_and_keeps_balance | PASS | PR7 | Covered |
| FR9 | Processed application cannot be processed again | test_approve_reject.py::test_second_approval_does_not_deduct_again, test_reject_after_approval_is_refused | PASS | PR1 | Covered |
| FR10 | Approval and rejection create a notification | test_approve_reject.py::test_approve_creates_notification | PASS | PR1 | Partly covered (rejection notification not tested) |

## Business rules to tests

| Rule | Description | Tests | Result | Risks | Status |
|------|-------------|-------|--------|-------|--------|
| BR1 | Duration at least 1 day and not above balance | test_end_date_before_start_date_is_refused, test_leave_longer_than_balance_is_refused | XFAIL (DEF-001, DEF-002) | PR1, PR2 | Defect found. Boundary tests (3 points) still to add |
| BR2 | Overlap refused (same user, active status, dates overlap) | test_overlapping_application_is_refused | PASS (same dates only) | PR4 | Partly covered. Decision table still to add |
| BR3 | Only Pending can change state | test_second_approval_does_not_deduct_again, test_reject_after_approval_is_refused, test_owner_cancels_pending_application, test_approved_application_cannot_be_cancelled | PASS | PR1, PR5 | Partly covered. Cancelled and Rejected as starting states still to add |
| BR4 | Rejection needs a non-empty reason | test_reject_with_empty_reason_is_refused | XFAIL (DEF-004) | PR7 | Defect found |

## Defects to risks

| Defect | Summary | Requirement / rule | Risk | Detected by |
|--------|---------|--------------------|------|-------------|
| DEF-001 | End date before start date accepted | FR1, BR1 | PR2 | test_end_date_before_start_date_is_refused |
| DEF-002 | Leave longer than balance accepted | FR1, BR1 | PR1, PR2 | test_leave_longer_than_balance_is_refused |
| DEF-003 | Non-date input causes a 500 error | FR1 | PR3 | test_invalid_date_text_does_not_crash |
| DEF-004 | Rejection with empty reason accepted | FR8, BR4 | PR7 | test_reject_with_empty_reason_is_refused |
| DEF-005 | Approve and cancel change data on plain GET | FR4, FR7, BR3 | PR6 | test_approve_by_plain_get_is_refused, test_cancel_by_plain_get_is_refused |

## Requirements coverage (current)

- Requirements with at least one test: FR1 to FR10 = 10 of 10 = 100%.
- Fully covered (no known gap): FR1, FR2, FR4, FR7, FR8, FR9. Partly covered: FR3, FR5, FR6, FR10. The gaps are listed in the Status column.
- Metric used in the weekly report: requirements coverage = requirements with at least one executed test / total requirements.
- Code coverage is tracked separately (baseline 47% before these tests, see evidence 23 and 24).