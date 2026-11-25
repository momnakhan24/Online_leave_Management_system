# Traceability Matrix

Sources: docs/TEST_BASIS.md (requirements and rules), docs/RISK_REGISTER.md (risks), tests/team/ (tests).
Result key: PASS = test passes. XFAIL = test fails because of an open defect (marked in the test; see GitHub Issues).
Last updated: 101 tests, 89 passed, 12 xfailed (after commit c62c244 plus the rejection notification test).

## Requirements to tests

| Req | Requirement (short) | Tests (file::test) | Result | Risks | Status |
|-----|---------------------|--------------------|--------|-------|--------|
| FR1 | Employee can submit an application | test_apply_leave::test_apply_creates_pending_application, test_lifecycle_branches::test_apply_form_page_loads | PASS | PR2, PR3 | Covered |
| FR1 | (input validation) | test_apply_defects::test_invalid_date_text_does_not_crash | XFAIL (DEF-003) | PR3 | Defect found |
| FR2 | New application is Pending, balance unchanged | test_apply_leave::test_apply_creates_pending_application, test_apply_does_not_change_balance | PASS | PR1 | Covered |
| FR3 | Overlapping application is refused | test_apply_leave::test_overlapping_application_is_refused, test_lifecycle_branches::test_overlap_error_re_renders_form | PASS (same dates, start inside range) | PR4 | Partly covered: decision table for BR2 still to add |
| FR4 | Cancel only own Pending application | test_cancel_and_access::test_owner_cancels_pending_application, test_other_employee_cannot_cancel, test_approved_application_cannot_be_cancelled | PASS | PR5, PR6 | Covered |
| FR4 | (HTTP method) | test_cancel_and_access::test_cancel_by_plain_get_is_refused | XFAIL (DEF-005) | PR6 | Defect found |
| FR5 | Employee sees only own applications and balance | test_cancel_and_access::test_employee_cannot_view_another_employees_application, test_owner_and_admin_can_view_application; test_lifecycle_branches::test_balance_page_shows_own_balance, test_home_counts_pending_and_approved, test_notification_page_filters | PASS | PR5 | Covered |
| FR6 | Only admin can process and list applications | test_approve_reject::test_employee_cannot_approve; test_lifecycle_branches::test_reject_by_employee_is_refused, test_admin_list_denied_for_employee; test_pages_and_admin::test_calendar_denied_for_anonymous_and_employee, test_admin_screens_require_superuser | PASS | PR5 | Covered |
| FR7 | Approval sets Approved and deducts duration | test_approve_reject::test_approve_sets_status_and_deducts_duration; test_lifecycle_branches::test_approval_deducts_from_matching_balance (annual, sick, other) | PASS | PR1 | Covered |
| FR7 | (admin approval path) | test_pages_and_admin::test_admin_bulk_approve_deducts_balance | XFAIL (DEF-007) | PR1 | Defect found |
| FR7 | (HTTP method) | test_cancel_and_access::test_approve_by_plain_get_is_refused | XFAIL (DEF-005) | PR6 | Defect found |
| FR8 | Rejection stores reason and sets Rejected | test_approve_reject::test_reject_stores_reason_and_keeps_balance; test_lifecycle_branches::test_reject_by_get_is_refused; test_pages_and_admin::test_admin_bulk_reject_uses_default_reason, test_admin_change_form_reject_button_stores_reason | PASS | PR7 | Covered |
| FR9 | Processed application cannot be processed again | test_approve_reject::test_second_approval_does_not_deduct_again, test_reject_after_approval_is_refused; test_lifecycle_branches::test_reject_twice_keeps_first_reason; test_pages_and_admin::test_admin_bulk_actions_skip_processed_applications, test_admin_change_form_buttons_ignore_processed_applications | PASS | PR1 | Covered |
| FR10 | Approval and rejection create a notification | test_approve_reject::test_approve_creates_notification, test_reject_creates_notification; test_lifecycle_branches::test_approval_sends_email_to_employee, test_rejection_email_contains_reason; test_pages_and_admin::test_admin_bulk_approve_sets_status_and_notifies | PASS | PR1 | Covered |

## Business rules to tests

| Rule | Description | Tests | Result | Risks | Status |
|------|-------------|-------|--------|-------|--------|
| BR1 | Duration at least 1 day and not above balance | test_apply_defects::test_end_date_before_start_date_is_refused, test_leave_longer_than_balance_is_refused | XFAIL (DEF-001, DEF-002) | PR1, PR2 | Defect found. 3-point boundary tests still to add |
| BR2 | Overlap refused (same user, active status, dates overlap) | test_overlapping_application_is_refused, test_overlap_error_re_renders_form | PASS (limited cases) | PR4 | Partly covered. Decision table still to add |
| BR3 | Only Pending can change state | test_second_approval_does_not_deduct_again, test_reject_after_approval_is_refused, test_owner_cancels_pending_application, test_approved_application_cannot_be_cancelled, test_reject_twice_keeps_first_reason | PASS | PR1, PR5 | Partly covered. State transition tests from Rejected and Cancelled still to add |
| BR4 | Rejection needs a non-empty reason | test_approve_reject::test_reject_with_empty_reason_is_refused | XFAIL (DEF-004) | PR7 | Defect found |

## Defects to risks

| Defect | Summary | Requirement / rule | Risk | Detected by |
|--------|---------|--------------------|------|-------------|
| DEF-001 | End date before start date accepted | FR1, BR1 | PR2 | test_end_date_before_start_date_is_refused |
| DEF-002 | Leave longer than balance accepted | FR1, BR1 | PR1, PR2 | test_leave_longer_than_balance_is_refused |
| DEF-003 | Non-date input causes a 500 error | FR1 | PR3 | test_invalid_date_text_does_not_crash |
| DEF-004 | Rejection with empty reason accepted | FR8, BR4 | PR7 | test_reject_with_empty_reason_is_refused |
| DEF-005 | Approve and cancel change data on plain GET | FR4, FR7, BR3 | PR6 | test_approve_by_plain_get_is_refused, test_cancel_by_plain_get_is_refused |
| DEF-006 | Registration returns 500 after creating the account | registration | PR3 | test_register_creates_account_and_logs_in |
| DEF-007 | Admin approval does not deduct the balance | FR7 | PR1 | test_admin_bulk_approve_deducts_balance |
| DEF-008 | update_profile and update_contact pages crash (missing template) | profile pages | PR3 | test_edit_pages_load and two others |

## Requirements coverage (current)

- Requirements with at least one executed test: FR1 to FR10 = 10 of 10 = 100%.
- Fully covered with no known gap: 9 of 10 (FR3 is partly covered).
- Metric used in the weekly report: requirements coverage = requirements with at least one executed test / total requirements.

## Code coverage (coverage.py, statements and branches)

- Measured over users/ and leave_management_system/ (migrations, tests, asgi.py, wsgi.py and users/tests.py omitted: startup boilerplate and an empty file, no business logic).
- 632 of 675 statements covered = 93.6%. Branch partials: 0 in every file.
- Baseline before our tests: 47% (evidence 23 and 24).

| Uncovered lines | Code | Justification |
|-----------------|------|---------------|
| users/views.py 417-431 | admin_analytics | No URL routes to it, so it cannot run. |
| users/views.py 443-467 | manage_leave_types | No URL routes to it, so it cannot run. |
| users/views.py 484-487 | second half of register | Unreachable until DEF-006 is fixed: registration crashes before these lines. |