# Test Plan: Leave Application Lifecycle

Version 1.0. System under test: Online Leave Management System (Django 5.1, SQLite), baseline commit e64e3bc51b58c8cfc4f07105189b63121bb7f438.
Related documents: SETUP.md, docs/TEST_BASIS.md, docs/RISK_REGISTER.md, docs/EXIT_CRITERIA.md, docs/TRACEABILITY.md.

## 1. Scope
In scope: Workflow 1 (employee applies for and cancels leave) and Workflow 2 (admin approves or rejects leave). Requirements FR1 to FR10 and business rules BR1 to BR4 in docs/TEST_BASIS.md. Shared records: LeaveApplication.status and LeaveBalance.
Out of scope: registration, profile pages, notices, awards, the analytics page (not routed in the code), email delivery, and the production deployment.

## 2. Approach by risk level
Risk levels come from docs/RISK_REGISTER.md. The level decides technique and depth.

| Level | Risks | Techniques and depth |
|-------|-------|----------------------|
| Critical (20-25) | PR1, PR2 | Unit tests with full MCC and MC/DC on the balance and date rules. API tests with equivalence partitioning and 3-point boundary values on every input. Mutation testing. Read back the balance after every success and rejection. |
| High (12-19) | PR3, PR4, PR5, PR6, PR7, PR8 | Decision tables and state transition tests, API and browser tests, role checks in Playwright, ZAP passive scan, dependency audit. |
| Medium (6-11) | PR9 | Lighthouse and axe-core scans, one keyboard test. |
| Low (1-5) | none yet | Smoke checks only. |

Test levels: unit (pytest, coverage.py), API and integration (pytest and Requests, generated EP and BVA data), browser end to end (Playwright with Chromium), static analysis (SonarQube), mutation (mutmut), performance (k6), security (OWASP ZAP passive, pip-audit).

## 3. Roles and ownership
| Area | Owner | Responsibilities |
|------|-------|------------------|
| 1 | Momna Khan | SonarQube, white-box unit tests, mutation testing, CI quality gate |
| 2 | Aimen Tasneem | API testing, OpenAPI spec, test data generator |
| 3 | Aliyah Ashraf | Use case tests, usability and accessibility, security, performance |
| Shared | All | Test plan, risk register, traceability, defect log, progress reports, final report |
Every member commits their own work under their own name.

## 4. Environment
- Windows PC, Python 3.12.0, Django 5.1, pytest 9.2.0, pytest-django 4.14.0, Docker 29.8.0 (SonarQube Community Build), Node v24 (Playwright).
- Application runs locally at http://127.0.0.1:8000 (see SETUP.md). Unit and API-level tests use pytest-django's temporary test database.
- Tool versions are pinned in requirements-dev.txt and recorded in the report.

## 5. Test data
- Synthetic only. Seed script scripts/seed_data.py creates employees emp1 and emp2 and admin admin1 (password in SETUP.md), leave types Annual, Sick and Other, and a starting balance of 20 annual, 10 sick, 5 other days.
- Reset before every manual or browser run with .\reset_db.ps1. Automated tests create their own data through fixtures in tests/team/conftest.py.
- The upstream database (real-looking accounts) is not used and is no longer tracked.

## 6. Schedule
Dates are filled in once the submission deadline is known (relative weeks from the announcement).

| Week | Activities | Owner |
|------|-----------|-------|
| 1 | Setup, scope, test basis, risk register, exit criteria, traceability, test plan, first tests | All |
| 2 | SonarQube analysis and CFG complexity, white-box unit tests, OpenAPI spec | 1, 2 |
| 3 | Generator, API tests, MCC and MC/DC, use case specifications | 1, 2, 3 |
| 4 | Playwright tests, usability and accessibility, mutation testing | 1, 3 |
| 5 | Security, performance and recovery, CI pipeline, blocked pull request, fix pull request | 1, 3 |
| 6 | Defect analysis, completion report, final package, viva preparation | All |

Weekly progress reports are kept in docs/progress/ (planned vs actual, control actions, metrics: defect density, requirements coverage, reopen rate).

## 7. Entry criteria
- Baseline commit tagged and repository reachable.
- Application starts and the seed script runs from a clean reset.
- Requirements, rules and test basis written.
- Test tools installed and the smoke test passes.

## 8. Exit criteria
See docs/EXIT_CRITERIA.md (EC1 to EC6). The three release criteria are EC1, EC2 and EC3.

## 9. Suspension and resumption
Suspend testing when: the application will not start or the reset script fails; the CI or tool environment is unavailable; a defect blocks more than 30% of planned tests from running.
Resume when: the environment starts cleanly from a reset, the smoke test passes, and the blocking defect is fixed or worked around and recorded.

## 10. Risks
Product risks: docs/RISK_REGISTER.md (PR1 to PR9). Project risks PJ1 (unstable internet) and PJ2 (teammates new to tools) are tracked there with mitigations.

## 11. Estimation (three-point, hours)
Expected = (Optimistic + 4 x Most likely + Pessimistic) / 6. Actual hours are filled in as work finishes and compared in the completion report.

| Area | O | M | P | Expected | Actual |
|------|---|---|---|----------|--------|
| 1. Setup and scope | 3 | 5 | 8 | 5.2 | |
| 2. Test management documents | 10 | 16 | 24 | 16.3 | |
| 3. Static analysis | 3 | 5 | 8 | 5.2 | |
| 4. Unit and white-box tests | 12 | 18 | 28 | 18.7 | |
| 5. API tests and data generation | 14 | 22 | 34 | 22.7 | |
| 6. Use case and browser tests | 10 | 16 | 24 | 16.3 | |
| 7. Usability and accessibility | 5 | 8 | 12 | 8.2 | |
| 8. Security | 5 | 8 | 12 | 8.2 | |
| 9. Performance and recovery | 5 | 8 | 14 | 8.5 | |
| 10. Mutation and CI gate | 12 | 18 | 28 | 18.7 | |
| 11. Defects, reports, viva preparation | 10 | 16 | 24 | 16.3 | |
| Total | 89 | 140 | 216 | 144.2 | |

## 12. Revision history
| Version | Date | Change |
|---------|------|--------|
| 1.0 | 11/24/2026 | First version |