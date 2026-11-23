# Test Basis: Leave Application Lifecycle

Baseline: upstream commit e64e3bc51b58c8cfc4f07105189b63121bb7f438
Sources: upstream README (R), source code review (C), team assumption (A).

## Module and roles
Module: leave applications (apply, cancel, approve, reject).

| Role | How identified | Allowed |
|------|----------------|---------|
| Employee (emp1, emp2) | normal user | apply, cancel own Pending application, view own applications, view own balance |
| Admin (admin1) | is_superuser | view all applications, approve, reject, view any application, team calendar |

## Workflows

### W1: Apply for leave (employee)
- Start: logged-in employee emp1, annual balance 20, no applications.
- Action: submit leave type, start date, end date and message at /apply/.
- Expected: a Pending application is created, a success message is shown, the balance is unchanged.

### W2: Approve or reject leave (admin)
- Start: one Pending application exists, logged in as admin1.
- Action: approve it, or reject it with a reason, at /leaves/admin/{id}/approve/ or /reject/.
- Expected (approve): status Approved, approved_by and approved_at set, balance reduced by the duration, notification created.
- Expected (reject): status Rejected, reason stored, rejected_by and rejected_at set, notification created.

## Shared records
| Record | W1 | W2 |
|--------|----|----|
| LeaveApplication.status | creates it as Pending; overlap rule reads it | reads it, changes it to Approved or Rejected |
| LeaveBalance | reads it (display only, via /balance/) | changes it on approval |

Value chosen for registration: LeaveApplication.status (W1 creates it, W2 changes it, and the W1 overlap rule depends on it).

## Routes (HTTP endpoints under test)
| Route | Method | Purpose |
|-------|--------|---------|
| /accounts/login/ | GET, POST | log in |
| /apply/ | GET, POST | submit application |
| /leave/{id}/cancel/ | GET | cancel own Pending application |
| /leave/{id}/ | GET | view application detail |
| /balance/ | GET | view own balance |
| /leaves/admin/ | GET | list all applications (admin) |
| /leaves/admin/{id}/approve/ | GET | approve (admin) |
| /leaves/admin/{id}/reject/ | POST | reject with reason (admin) |

## Functional requirements
| ID | Workflow | Requirement | Source |
|----|----------|-------------|--------|
| FR1 | W1 | An employee can submit an application with a leave type, start date, end date and message. | R, C |
| FR2 | W1 | A new application is created with status Pending and the balance is unchanged. | C |
| FR3 | W1 | An application overlapping the same user's existing application is refused with an error message and no record is created. | R |
| FR4 | W1 | An employee can cancel only their own Pending application. | R, C |
| FR5 | W1 | An employee can view only their own applications and balance. | C |
| FR6 | W2 | Only an admin can view the list of all applications. | C |
| FR7 | W2 | Approving a Pending application sets status Approved and deducts the duration from the matching balance. | R, C |
| FR8 | W2 | Rejecting a Pending application stores the reason and sets status Rejected. | R, C |
| FR9 | W2 | An application that is not Pending cannot be approved or rejected again, and nothing changes. | C |
| FR10 | W2 | Approval and rejection each create a notification for the employee. | R, C |

## Business rules

### BR1: Leave duration and balance limit (boundary)
- duration = end date minus start date plus 1 day.
- A valid application has duration of at least 1 day and no more than the remaining balance of that leave type.
- Source: R (balance tracking, auto-deduction) plus A: the limits are an assumption, because the README does not state them.
- Boundaries to test: end = start minus 1 day, end = start, end = start plus 1 day; duration = balance minus 1, = balance, = balance plus 1.

### BR2: Overlap prevention (decision with 3 conditions)
- An application is refused if ALL of these are true: (a) same user, (b) the existing application is active, (c) the date ranges overlap.
- Source: R (duplicate and overlap prevention) plus A: active means Pending or Approved, because approved leave occupies the dates.

### BR3: Status change (state rule)
- Allowed: Pending to Approved (admin), Pending to Rejected (admin), Pending to Cancelled (owner only).
- Approved, Rejected and Cancelled are final. Any further action on them is refused and changes nothing.
- Source: R, C.

### BR4: Mandatory rejection reason (decision)
- Rejecting requires a non-empty reason. An empty or blank reason is refused and the status stays Pending.
- Source: R ("Mandatory reason field when rejecting").

## Test environment
See SETUP.md. Reset with .\reset_db.ps1 before each run.