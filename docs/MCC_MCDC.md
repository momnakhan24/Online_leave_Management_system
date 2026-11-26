# MCC and MC/DC Analysis

Critical rules (both are compound Boolean decisions with two or more conditions).
Tests: tests/team/test_mcc_mcdc.py. Baseline commit e64e3bc.

## Rule A: overlap prevention (BR2), `apply()` in users/views.py
The code refuses the application when one existing record satisfies all four conditions:

| Cond | Meaning | In the code |
|------|---------|-------------|
| C1 | existing application belongs to the same user | `user=request.user` |
| C2 | existing application is Pending | `status='Pending'` |
| C3 | existing start date <= new start date | `start_date__lte=start_date` |
| C4 | existing end date >= new start date | `end_date__gte=start_date` |

Decision: refused = C1 AND C2 AND C3 AND C4.

### MCC truth table (all 2^4 = 16 combinations, all executed)
| Row | C1 | C2 | C3 | C4 | Expected outcome | Test id (test_overlap_rule_all_16_combinations) |
|-----|----|----|----|----|------------------|------------------------------------------------|
| R01 | T | T | T | T | **refused** | R01_TTTT |
| R02 | T | T | T | F | created | R02_TTTF |
| R03 | T | T | F | T | created | R03_TTFT |
| R04 | T | T | F | F | created | R04_TTFF |
| R05 | T | F | T | T | created | R05_TFTT |
| R06 | T | F | T | F | created | R06_TFTF |
| R07 | T | F | F | T | created | R07_TFFT |
| R08 | T | F | F | F | created | R08_TFFF |
| R09 | F | T | T | T | created | R09_FTTT |
| R10 | F | T | T | F | created | R10_FTTF |
| R11 | F | T | F | T | created | R11_FTFT |
| R12 | F | T | F | F | created | R12_FTFF |
| R13 | F | F | T | T | created | R13_FFTT |
| R14 | F | F | T | F | created | R14_FFTF |
| R15 | F | F | F | T | created | R15_FFFT |
| R16 | F | F | F | F | created | R16_FFFF |

Notes:
- Rows with C3 = F and C4 = F (R04, R08, R12, R16) cannot occur with valid data: an existing record that starts after the new start date and also ends before it would end before it starts. They are executed anyway by inserting an end-before-start record directly in the database. That is possible only because of DEF-001, so these four rows document an invalid state and are not requirements.
- For C2 = F the existing record has status Rejected (a status that is inactive under the code and under BR2).
- A new application is judged by whether a record with the new start date was created for the user.

### MC/DC pairs (derived from the MCC table)
Each pair changes exactly one condition and changes the outcome, with the other conditions fixed.

| Condition shown independent | Pair (rows) | Condition values | Outcomes |
|-----------------------------|-------------|------------------|----------|
| C1 | R01 and R09 | TTTT vs FTTT | refused vs created |
| C2 | R01 and R05 | TTTT vs TFTT | refused vs created |
| C3 | R01 and R03 | TTTT vs TTFT | refused vs created |
| C4 | R01 and R02 | TTTT vs TTTF | refused vs created |

Minimum MC/DC set = n + 1 = 5 tests: R01, R02, R03, R05, R09. All five are among the 16 MCC tests. test_overlap_rule_mcdc_pairs checks that each pair differs in exactly one condition and flips the outcome.

### Result and defect found
The implemented decision matches the table, so all 16 tests pass. The analysis exposes two gaps against BR2 (logged as DEF-009):
- Only Pending records block (C2), so a new application can overlap an Approved one. Test: test_overlap_with_approved_leave_is_refused.
- Only the new start date is compared with the existing range (C3, C4), so a new range that starts before an existing one but runs into it is accepted. Test: test_new_range_that_runs_into_existing_leave_is_refused.

## Rule B: viewing an application (FR5), `leave_detail()` in users/views.py
Code: `if leave.user != request.user and not request.user.is_superuser: raise Http404`.
A = viewer is not the owner. B = viewer is not an admin. Decision: denied = A AND B.

| Row | A | B | Case | Expected | Test id (test_detail_access_rule_all_4_combinations) |
|-----|---|---|------|----------|-------|
| R1 | T | T | employee views another's application | denied (404) | TT_denied |
| R2 | T | F | admin views an employee's application | allowed (200) | TF_admin_views_other |
| R3 | F | T | employee views own application | allowed (200) | FT_owner_views_own |
| R4 | F | F | admin views own application | allowed (200) | FF_admin_views_own |

MC/DC pairs: A is shown independent by R1 and R3 (B = T fixed). B is shown independent by R1 and R2 (A = T fixed). Minimum set = 3 tests (R1, R2, R3). R4 completes the MCC.

## The other two business rules
- BR3 (state change) and BR4 (rejection reason) are single-condition decisions, so MCC equals plain branch coverage. They are covered by test_approve_reject.py, test_cancel_and_access.py and test_lifecycle_branches.py (see docs/TRACEABILITY.md).
- BR1 (duration and balance) is covered by the boundary tests to be added in the API test level, and its present defects are DEF-001 and DEF-002.