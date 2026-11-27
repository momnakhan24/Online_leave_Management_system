"""Start the app for the Playwright tests from a clean, seeded database.

Deletes db.sqlite3, migrates, seeds the synthetic accounts, then runs the server in
this process (so Playwright can stop it). Run from the project root.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "leave_management_system.settings")

database = os.path.join(ROOT, "db.sqlite3")
if os.path.exists(database):
    os.remove(database)

from django.core.management import execute_from_command_line  # noqa: E402

execute_from_command_line([sys.argv[0], "migrate", "--noinput"])
subprocess.check_call([sys.executable, os.path.join("scripts", "seed_data.py")])
execute_from_command_line([sys.argv[0], "runserver", "127.0.0.1:8000", "--noreload"])