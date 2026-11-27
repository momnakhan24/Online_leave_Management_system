# Use Case Specifications

Derived from docs/TEST_BASIS.md. Automated in tests/team/e2e/ (Playwright). Every flow checks what the screen shows
and the stored records (read back with scripts/e2e_state.py). Test ids in the last column are the Playwright test names.

| UC | Name | Actor | Workflow | Owner |
|----|------|-------|----------|-------|
| UC1 | Apply for leave | Employee | W1 | Member 1 |
| UC2 | Cancel leave | Employee | W1 | Member 1 |
| UC3 | Approve leave | Admin | W2 | Member 2 |
| UC4 | Reject leave | Admin | W2 | Member 2 |
| UC5 | View balance after a decision | Employee (and Admin) | W1 and W2 | Member 3 |
| UC6 | Log in and out | Employee, Admin | both | Member 3 |

## UC1 Apply for leave (FR1, FR2, FR3; BR1, BR2)
Precondition: emp1 is a user with balance 20 annual, 10 sick, 5 other. Postcondition (success): one Pending application exists and the balance is unchanged.
| Flow | Steps and expected result | Test |
|------|---------------------------|------|
| Main | Open Apply, choose Annual Leave, 1 to 3 March 2027, give a reason, submit. The success message shows; one Pending application; annual balance 20. | UC1-M |
| A1 | Same with Sick Leave. Pending sick application; sick balance 10. | UC1-A1 |
| A2 | Start date equals end date (one day). Accepted. | UC1-A2 |
| E1 | Dates overlap an existing Pending application. An error says the dates overlap; nothing new is stored. | UC1-E1 |
| E2 | Reason left empty. The browser blocks the submit; nothing is stored. | UC1-E2 |

## UC2 Cancel leave (FR4; BR3)
Precondition: emp1 has a Pending application. Postcondition (success): status Cancelled, balance unchanged.
| Flow | Steps and expected result | Test |
|------|---------------------------|------|
| Main | Open the application, press Cancel Application, confirm. Message "cancelled successfully"; status Cancelled. | UC2-M |
| A1 | Dismiss the confirmation. Status stays Pending. | UC2-A1 |
| A2 | After cancelling, apply for the same dates again. Accepted; one Cancelled and one Pending record. | UC2-A2 |
| E1 | The application is Approved. No cancel button; the direct address shows "Only pending leave applications can be cancelled"; status stays Approved. | UC2-E1 |
| E2 | emp2 opens or cancels emp1's application. Both return 404; status stays Pending. | UC2-E2 |

## UC3 Approve leave (FR6, FR7, FR9; BR1, BR3)
Precondition: admin1 is logged in; a Pending application exists. Postcondition (success): status Approved, the matching balance reduced by the duration, a notification stored.
| Flow | Steps and expected result | Test |
|------|---------------------------|------|
| Main | Open the admin list, press Approve on a 3-day annual leave, confirm. Message shown; Approved; annual balance 17; one notification. | UC3-M |
| A1 | Approve a 2-day sick leave. Sick balance 8; annual stays 20. | UC3-A1 |
| A2 | Filter the list by Pending, then approve. The list shows one row; both applications end Approved; emp2 balance 18. | UC3-A2 |
| E1 | Dismiss the confirmation. Status stays Pending; balance 20. | UC3-E1 |
| E2 | Open the approve address of a Rejected application. Message "already been processed"; status stays Rejected; balance 20. | UC3-E2 |

## UC4 Reject leave (FR8; BR3, BR4)
Precondition: admin1 is logged in; a Pending application exists. Postcondition (success): status Rejected, reason stored, balances unchanged.
| Flow | Steps and expected result | Test |
|------|---------------------------|------|
| Main | Press Reject, type a reason, confirm. Message "rejected"; status Rejected; reason stored; balance 20. | UC4-M |
| A1 | The employee opens the application afterwards and sees the status and the reason. | UC4-A1 |
| A2 | Reject a sick leave. Balances stay 20, 10, 5. | UC4-A2 |
| E1 | Submit the dialog with an empty reason. The browser blocks it; status stays Pending. | UC4-E1 |
| E2 | Close the dialog with Cancel. Status stays Pending. | UC4-E2 |

## UC5 View balance after a decision (shared record; FR5, FR6, FR7)
Precondition: a Pending application exists. Postcondition: the balance page agrees with the stored balance.
| Flow | Steps and expected result | Test |
|------|---------------------------|------|
| Main | Admin approves a 3-day annual leave, the employee opens Balance. Annual shows 17. | UC5-M |
| A1 | Admin rejects instead. Annual shows 20. | UC5-A1 |
| A2 | Admin approves a 2-day sick leave. Sick shows 8; annual 20. | UC5-A2 |
| E1 | An anonymous visitor opens Balance. Redirected to the login page. | UC5-E1 |
| E2 | An employee opens the admin list. 404. | UC5-E2 |

## UC6 Log in and out (FR5, FR6)
Precondition: seeded users exist. Postcondition: the session exists only while logged in.
| Flow | Steps and expected result | Test |
|------|---------------------------|------|
| Main | emp1 logs in. The dashboard shows "Welcome, emp1!". | UC6-M |
| A1 | admin1 logs in and lands on the admin site. | UC6-A1 |
| A2 | emp1 logs out. The login page shows, and the balance page asks for a new login. | UC6-A2 |
| E1 | Wrong password. A message says the username and password were not accepted; still on the login page; no session. | UC6-E1 |
| E2 | Unknown user. The same message. | UC6-E2 |