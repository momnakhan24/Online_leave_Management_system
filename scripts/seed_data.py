import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "leave_management_system.settings")

import django

django.setup()

from django.contrib.auth import get_user_model
from users.models import LeaveType, LeaveBalance

User = get_user_model()
PASSWORD = "Test@12345"

for name in ["Annual Leave", "Sick Leave", "Other Leave"]:
    LeaveType.objects.get_or_create(name=name)

for username in ["emp1", "emp2"]:
    user, created = User.objects.get_or_create(
        username=username,
        defaults={"email": f"{username}@example.test", "first_name": username},
    )
    if created:
        user.set_password(PASSWORD)
        user.save()

admin, created = User.objects.get_or_create(
    username="admin1",
    defaults={"email": "admin1@example.test", "is_staff": True, "is_superuser": True},
)
if created:
    admin.set_password(PASSWORD)
    admin.save()

print("Users:", list(User.objects.values_list("username", flat=True)))
print("Leave types:", list(LeaveType.objects.values_list("name", flat=True)))
b = LeaveBalance.objects.get(user__username="emp1")
print("emp1 balance (annual, sick, other):", b.annual_leave, b.sick_leave, b.other_leave)