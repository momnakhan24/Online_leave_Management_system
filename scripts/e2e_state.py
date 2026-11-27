"""Read or change the database for the Playwright tests (preconditions and postconditions).

  python scripts/e2e_state.py reset
  python scripts/e2e_state.py state
  python scripts/e2e_state.py create USER "Leave Type" START END STATUS
Prints one JSON line.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "leave_management_system.settings")

import django  # noqa: E402

django.setup()

from django.contrib.auth import get_user_model  # noqa: E402
from users.models import LeaveApplication, LeaveBalance, LeaveType, Notification  # noqa: E402


def state():
    return {
        "applications": [
            {"id": a.id, "user": a.user.username, "type": a.leave_type.name,
             "start": str(a.start_date), "end": str(a.end_date), "status": a.status,
             "reason": a.rejection_reason or ""}
            for a in LeaveApplication.objects.order_by("id")
        ],
        "balances": {
            b.user.username: {"annual": b.annual_leave, "sick": b.sick_leave, "other": b.other_leave}
            for b in LeaveBalance.objects.all()
        },
        "notifications": Notification.objects.count(),
    }


action = sys.argv[1] if len(sys.argv) > 1 else "state"
if action == "reset":
    LeaveApplication.objects.all().delete()
    Notification.objects.all().delete()
    for balance in LeaveBalance.objects.all():
        balance.annual_leave, balance.sick_leave, balance.other_leave = 20, 10, 5
        balance.save()
    print(json.dumps(state()))
elif action == "create":
    user, leave_type, start, end, status = sys.argv[2:7]
    application = LeaveApplication.objects.create(
        user=get_user_model().objects.get(username=user),
        leave_type=LeaveType.objects.get(name=leave_type),
        start_date=start, end_date=end, message="seeded by test", status=status)
    print(json.dumps({"id": application.id}))
else:
    print(json.dumps(state()))