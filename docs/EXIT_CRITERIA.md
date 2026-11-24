# Exit Criteria

Each criterion is measurable and tied to the risk register (docs/RISK_REGISTER.md).
The three criteria marked RELEASE are the ones reported as actual versus target in the final release or hold decision.
Targets marked "provisional" will be confirmed or adjusted from evidence and the change recorded in this file.

| ID | Type | Criterion (measurable) | Target | Linked risks | Release criterion |
|----|------|------------------------|--------|--------------|-------------------|
| EC1 | Functional | Every test case for the Critical and High risks that target the balance, dates, overlap and rejection rules has been executed and passes. Open defects of severity critical or major that are linked to those risks are fixed and verified. | 100% of those tests pass and 0 open critical or major defects linked to PR1, PR2, PR4, PR7 | PR1, PR2, PR4, PR7 | RELEASE |
| EC2 | Functional | Statement and branch coverage of the server-side business logic, measured with coverage.py, and requirements coverage from the traceability matrix. | 100% statement, 100% branch (any uncovered line justified in writing) and 100% of FR1 to FR10 traced to at least one passing test | PR1, PR2, PR4 | RELEASE |
| EC3 | Security | Role checks and state-changing actions behave as the access matrix says. At least 4 automated checks across the two roles, including 1 allowed and 1 denied action. Approve and cancel must not change data on a plain GET request. | 100% of access checks match the expected result and 0 state changes caused by GET | PR5, PR6 | RELEASE |
| EC4 | Performance | p95 response time and unexpected failure rate for the chosen operation, from k6 runs with 1 user and with 5 or more users. | p95 at most 500 ms and under 1% unexpected failures (provisional, justified in the performance section before testing) | PR1 (operation under load) | no |
| EC5 | Usability / accessibility | axe-core and Lighthouse results on the key screen of each workflow after the fix. | 0 serious or critical axe violations on the fixed screen and Lighthouse accessibility score of at least 90 (provisional) | PR9 | no |
| EC6 | Quality | Mutation score on the business-rule module, measured with mutmut. | At least 80% (provisional, to be justified from the first mutation run) | PR1, PR2, PR4 | no |

## Notes
- EC1 and EC2 are tied to the two highest risks (PR1 and PR2, both Critical).
- EC3 is tied to PR5 and PR6, both High.
- A criterion that is not met is reported as a residual risk in the test completion report, with a release or hold recommendation.