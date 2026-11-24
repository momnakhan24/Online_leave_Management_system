# Traceability Matrix

Sources: docs/TEST_BASIS.md (requirements and rules), docs/RISK_REGISTER.md (risks), tests/team/ (tests).
Result key: PASS = test passes. XFAIL = test fails because of an open defect (marked in the test; see GitHub Issues).
Last updated at commit: 0f81df4 (11 passed, 4 xfailed).

## Requirements to tests

| Req | Requirement (short) | Tests | Result | Risks | Status |
|-----|---------------------|-------|--------|-------|--------|
| FR1 | Employee can submit an application | test_apply_leave.py::test_apply_creates_pending_application | PASS | PR2, PR3 | Covered |
| FR1 | (input validation) | test_apply_defects.py::test_invalid_date_text_does_not_crash | XFAIL (DEF-003) | PR3 | Defect found |
| FR2 | New application is Pending, balance unchanged | test_apply_leave.py::test_apply_creates_pending_application, test_apply_does_not_change_balance | PASS | PR1 | Covered |
| FR3 | Overlapping application is refused | test_apply_leave.py::test_overlapping_application_is_refused | PASS (same dates only) | PR4 | Partly covered |
| FR4 | Cancel only own Pending application | none yet | n/a | PR5, PR6 | NOT TESTED |
| FR5 | Employee sees only own applications and balance | none yet | n/a | PR5 | NOT TESTED |
| FR6 | Only admin can process applications | test_approve_reject.py::test_employee_cannot_approve | PASS | PR5 | Partly covered (admin list view not tested) |
| FR7 | Approval sets Approved and deducts duration | test_approve_reject.py::test_approve_sets_status_and_deducts_duration | PASS | PR1 | Covered |
| FR8 | Rejection stores reason and sets Rejected | test_approve_reject.py::test_reject_stores_reason_and_keeps_balance | PASS | PR7 | Covered |
| FR9 | Processed application cannot be processed again | test_approve_reject.py::test_second_approval_does_not_deduct_again, test_reject_after_approval_is_refused | PASS | PR1 | Covered |
| FR10 | Approval and rejection create a notification | test_approve_reject.py::test_approve_creates_notification | PASS | PR1 | Partly covered (rejection notification not tested) |

## Business rules to tests

| Rule | Description | Tests | Result | Risks | Status |
|------|-------------|-------|--------|-------|--------|
| BR1 | Duration at least 1 day and not above balance | test_end_date_before_start_date_is_refused, test_leave_longer_than_balance_is_refused | XFAIL (DEF-001, DEF-002) | PR1, PR2 | Defect found. Boundary tests (3 points) still to add |
| BR2 | Overlap refused (same user, active status, dates overlap) | test_overlapping_application_is_refused | PASS (same dates only) | PR4 | Partly covered. Decision table still to add |
| BR3 | Only Pending can change state | test_second_approval_does_not_deduct_again, test_reject_after_approval_is_refused | PASS | PR1 | Partly covered. Cancel transitions still to add |
| BR4 | Rejection needs a non-empty reason | test_reject_with_empty_reason_is_refused | XFAIL (DEF-004) | PR7 | Defect found |

## Requirements coverage (current)

- Requirements with at least one test: FR1, FR2, FR3, FR6, FR7, FR8, FR9, FR10 = 8 of 10 = 80%.
- Not tested yet: FR4, FR5 (planned for the next test round).
- Partly covered: FR3, FR6, FR10.
- Metric used in the weekly report: requirements coverage = requirements with at least one executed test / total requirements.