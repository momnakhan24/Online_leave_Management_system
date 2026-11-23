import pytest
from django.contrib.auth import get_user_model
from django.test import Client

from users.models import LeaveType

PASSWORD = "Test@12345"


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