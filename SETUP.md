# Project Setup (Leave Management System)

## Upstream reference
- Upstream repository: https://github.com/ahmednule/Online_leave_Management_system
- Licence: MIT
- Baseline commit: e64e3bc51b58c8cfc4f07105189b63121bb7f438
- Baseline tag: baseline-e64e3bc
- Our fork: https://github.com/momnakhan24/Online_leave_Management_system

## Environment
- Windows, Python 3.12.0, Git 2.52, Node v24
- Django 5.1 with SQLite (see requirements.txt)

## Install
```
git clone https://github.com/momnakhan24/Online_leave_Management_system.git
cd Online_leave_Management_system
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Seed test data and reset
`reset_db.ps1` deletes db.sqlite3, runs the migrations, then runs scripts/seed_data.py.
Run it to start from a known state and before every test run:
```
.\reset_db.ps1
```

## Start the application
```
python manage.py runserver
```
Open http://127.0.0.1:8000/

## Synthetic test accounts (created by the seed script)
| Username | Role     | Password   |
|----------|----------|------------|
| emp1     | Employee | Test@12345 |
| emp2     | Employee | Test@12345 |
| admin1   | Admin    | Test@12345 |

Leave types: Annual Leave, Sick Leave, Other Leave.
New employees start with a balance of 20 annual, 10 sick and 5 other days.

## Notes
- db.sqlite3 and __pycache__ are not tracked. The upstream database contained real-looking accounts, so we replaced it with synthetic data.
- The original upstream state can be restored with: `git checkout baseline-e64e3bc`