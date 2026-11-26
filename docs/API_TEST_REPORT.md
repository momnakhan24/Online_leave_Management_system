# API Test Report

Spec: openapi/leave_api.yaml. Generator: scripts/generate_api_data.py. Data: tests/team/data/api_cases.json (50 cases).
Tests: tests/team/api/ (pytest + requests against a real HTTP server with login and CSRF).
Result file: evidence/reports/api_coverage.json (written by test_api_zz_spec_coverage.py).

## What is tested
| Technique | Where | Cases |
|-----------|-------|-------|
| Equivalence partitioning and 3-point BVA on every input | test_api_generated.py (consumes the generated data) | 50 |
| Cross-workflow read-back of the Leave Request and the Leave Balance after success and after rejection | test_api_rules.py | 3 |
| Repeated requests (no duplicate records, no double deduction) | test_api_rules.py | 4 |
| State transitions: 3 allowed and 9 disallowed (4 states x 3 actions) | test_api_rules.py | 12 |
| Decision tables: approve (2 conditions), cancel (2 conditions), overlap (4 conditions, 12 feasible rows) | test_api_rules.py | 20 |
| Access: anonymous, wrong role | test_api_rules.py | 3 |

## API coverage criteria (actual)
| Criterion | Target | Actual |
|-----------|--------|--------|
| Operations (path and method) called | 5 of 5 | 5 of 5 |
| Documented status codes observed | 11 of 11 | 11 of 11 |
| Generated EP and BVA cases executed | 50 of 50 | 50 of 50 |

## Endpoint weaknesses found
| Weakness | Evidence | Defect | Risk |
|----------|----------|--------|------|
| Non-date input to /apply/ returns an undocumented 500 | report key endpoint_weaknesses_undocumented_status_codes: applyLeave 500 | DEF-003 | PR3 |
| End date before start date accepted | generated cases durationDays min-1 and invalid_below_min | DEF-001 | PR2 |
| Duration above the balance accepted | generated cases durationDays max+1 and invalid_above_max | DEF-002 | PR1, PR2 |
| Empty or missing rejection reason accepted | generated cases rejection_reason minLength-1, invalid_empty, invalid_missing | DEF-004 | PR7 |
| Approve and cancel change data on GET | spec lists them as GET operations | DEF-005 | PR6 |
| Overlap check ignores Approved leave and partial overlaps | docs/MCC_MCDC.md | DEF-009 | PR4 |
| Validation failures return 200 or 404 instead of a 4xx validation status, so a client cannot tell why a request was refused | observed statuses in the report | (design note) | PR3 |

Cases the application gets wrong are marked xfail with the defect id; when a defect is fixed its tests start passing, strict xfail reports it, and the marker is removed.