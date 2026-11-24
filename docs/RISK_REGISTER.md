# Risk Register

Scoring: Likelihood (L) 1-5 x Impact (I) 1-5 = Score.
Levels: Low 1-5, Medium 6-11, High 12-19, Critical 20-25.
Higher level means more techniques and deeper coverage (see Approach column).
Evidence: D = defect already logged, T = confirmed by running the app, S = from source review, to be tested.

## Product risks

| ID | Risk | L | I | Score | Level | Approach (technique and depth) | Evidence / links |
|----|------|---|---|-------|-------|--------------------------------|------------------|
| PR1 | Leave balance becomes wrong: deduction is clamped at 0 instead of refusing, and the two approval paths (custom view and Django admin) may behave differently | 4 | 5 | 20 | Critical | Unit: full MCC and MC/DC on the balance rule. API: BVA on duration vs balance. Read back the balance after every success and rejection. Mutation testing on this module. | DEF-002, T, S |
| PR2 | Invalid dates accepted (end before start, very long ranges) | 5 | 4 | 20 | Critical | BVA with 3 points on every date limit, EP on date groups. Unit and API levels. | DEF-001, DEF-002, T |
| PR4 | Overlap rule can be bypassed (checks only the new start date, and only Pending applications) | 4 | 4 | 16 | High | Decision table of all condition combinations, MC/DC, API test with repeated requests. | S, FR3, BR2 |
| PR6 | State-changing actions work on GET (approve, cancel), so a link can change data (CSRF-style risk) | 4 | 4 | 16 | High | Security checks in Playwright and API tests. ZAP passive scan. Source review of method checks. | T (approve), S (cancel) |
| PR8 | Insecure configuration: DEBUG on, secret key committed, old dependencies | 4 | 4 | 16 | High | pip-audit, ZAP passive scan, settings review. | S |
| PR7 | Application rejected with an empty reason | 5 | 3 | 15 | High | Decision table (reason present or blank), EP, unit and API tests. | DEF-004, BR4 |
| PR5 | A normal employee performs admin actions or sees other users' data | 3 | 5 | 15 | High | Access matrix, Playwright role checks (one allowed and one denied per action), API tests with the wrong role. | FR5, FR6 |
| PR3 | Unexpected input causes a server error (500) instead of a clear message | 4 | 3 | 12 | High | EP with one invalid value per test, API negative tests, error handling review. | DEF-003, T |
| PR9 | Screens are hard to use with a keyboard or screen reader | 3 | 3 | 9 | Medium | Lighthouse and axe-core on both key screens, one keyboard navigation test. | to be tested |

## Project risks

| ID | Risk | L | I | Score | Level | Mitigation |
|----|------|---|---|-------|-------|------------|
| PJ1 | Unstable internet interrupts pushes, installs and Docker downloads (seen during this project) | 4 | 3 | 12 | High | Commit locally often and push when the connection is stable. Download Docker images early. |
| PJ2 | Teammates are new to the tools or unavailable, so areas slip behind schedule | 3 | 4 | 12 | High | Weekly progress report. Each member owns one area from the start. Shared documents are started early. |