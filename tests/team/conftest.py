import pytest
from django.contrib.auth import get_user_model
from django.test import Client

from users.models import LeaveType

PASSWORD = "Test@12345"


@pytest.fixture(autouse=True)
def fast_password_hasher(settings):
    """Use a fast hasher in tests only (the real hasher is deliberately slow)."""
    settings.PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]


@pytest.fixture
def leave_types(db):
    for name in ["Annual Leave", "Sick Leave", "Other Leave"]:
        LeaveType.objects.get_or_create(name=name)


@pytest.fixture
def employee(db, leave_types):
    return get_user_model().objects.create_user(
        username="emp1", password=PASSWORD, email="emp1@example.test"
    )


@pytest.fixture
def employee_client(employee):
    client = Client()
    assert client.login(username="emp1", password=PASSWORD)
    return client


@pytest.fixture
def admin_user(db):
    return get_user_model().objects.create_superuser(
        username="admin1", password=PASSWORD, email="admin1@example.test"
    )


@pytest.fixture
def admin_client(admin_user):
    client = Client()
    assert client.login(username="admin1", password=PASSWORD)
    return client


@pytest.fixture
def pending_application(employee):
    """One Pending 3-day Annual Leave application (1 to 3 December 2026)."""
    from users.models import LeaveApplication

    return LeaveApplication.objects.create(
        user=employee,
        leave_type=LeaveType.objects.get(name="Annual Leave"),
        start_date="2026-12-01",
        end_date="2026-12-03",
        message="Family event",
    )


@pytest.fixture
def other_employee_client(db, leave_types):
    get_user_model().objects.create_user(
        username="emp2", password=PASSWORD, email="emp2@example.test"
    )
    client = Client()
    assert client.login(username="emp2", password=PASSWORD)
    return client