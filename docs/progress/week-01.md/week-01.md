# Weekly Progress Report: week 01

Period: 21/11/2026 to 26/11/2026

## Planned vs actual
| Area | Planned (expected hours) | Actual hours | Status |
|------|--------------------------|--------------|--------|
| 1. Setup and scope | 5.2 | (fill in) | Done |
| 2. Test management documents | 16.3 | (fill in) | Test basis, risk register, exit criteria, traceability and test plan done. Weekly reports started |
| 4. Unit and white-box tests | 18.7 | (fill in) | In progress: 101 tests, coverage 47% to 93.6% |
| 11. Defects (logging) | part of 16.3 | (fill in) | 8 defects logged |
Not started this week: static analysis, API tests and generator, Playwright, security, performance, mutation and CI.

## Work completed
- Fork, baseline tag, setup and reset scripts, synthetic seed data.
- Test basis, risk register (9 product, 2 project), exit criteria (6), traceability, test plan.
- 101 automated tests: 89 passing, 12 expected failures that each point to a logged defect.
- 8 defects logged in GitHub Issues with severity, priority, status, category and triage decision.

## Control actions
| Problem seen | Action taken |
|--------------|--------------|
| pytest collected fewer tests than expected because a test file was saved in the wrong folder (happened twice) | Check the "collected N items" line and the folder listing after adding every test file |
| Coverage was 47% against a 100% target | Split work into batches by risk, and wrote tests for the leave lifecycle and admin paths first |
| Unrouted code in views.py cannot be reached by tests | Record it as justified uncovered code instead of testing unreachable code |
| Internet dropped during pushes | Commit locally first and retry the push |
| SonarQube not started by the teammate who owns it | Moved test management and unit tests forward; SonarQube set up next |

## GQM metrics
Goal: decide whether the leave lifecycle is ready for release (link: docs/EXIT_CRITERIA.md).

| Question | Metric | Value this week | Reading |
|----------|--------|-----------------|---------|
| How many defects are there for the code size? | Defect density = defects / thousand statements | 8 / 0.675 = 11.9 | High. Two defects are linked to the Critical risks (PR1, PR2) |
| Are all requirements tested? | Requirements coverage = requirements with a test / total | 10 / 10 = 100% | Good, but FR3 is only partly covered |
| Is the code exercised? | Statement coverage | 93.6% | Remaining gaps are justified unreachable code |
| Are fixes holding? | Reopen rate = reopened / fixed defects | 0 / 0 (no defect fixed yet) | Not measurable until the first fix pull request |

## Next week
SonarQube metrics and hand-calculated complexity, OpenAPI spec and generator, EP and 3-point boundary tests, decision tables for BR2, state transition tests, first fix pull request.