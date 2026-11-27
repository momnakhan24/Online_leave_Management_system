"""HTTP client helpers for the API level tests (real HTTP with requests, CSRF handled)."""
import json
from pathlib import Path

import pytest
import requests

from conftest import PASSWORD

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "api_cases.json"
SPEC_FILE = Path(__file__).resolve().parents[3] / "openapi" / "leave_api.yaml"

# Everything the tests observe, used by the API coverage criteria test.
OBSERVED = set()          # (operationId, status_code)
EXECUTED_CASES = set()    # ids of generated cases that were executed


def load_cases(operation):
    with open(DATA_FILE, encoding="utf-8") as handle:
        return [c for c in json.load(handle)["cases"] if c["operation"] == operation]


class ApiSession(requests.Session):
    """requests session that logs in through the form and sends the CSRF header."""

    def __init__(self, base_url):
        super().__init__()
        
        self.base_url = base_url.replace("localhost", "127.0.0.1")

    def login(self, username, password=PASSWORD):
        self.get(self.base_url + "/accounts/login/")
        response = self.post(
            self.base_url + "/accounts/login/",
            data={"username": username, "password": password},
            headers={"X-CSRFToken": self.cookies.get("csrftoken", "")},
            allow_redirects=False,
        )
        assert response.status_code == 302, "login failed"
        return self

    def call(self, operation, method, path, data=None):
        """Send one request without following redirects and record what was observed."""
        headers = {"X-CSRFToken": self.cookies.get("csrftoken", "")}
        response = self.request(method, self.base_url + path, data=data, headers=headers,
                                allow_redirects=False)
        OBSERVED.add((operation, response.status_code))
        return response


@pytest.fixture
def emp_api(live_server, employee):
    return ApiSession(live_server.url).login("emp1")


@pytest.fixture
def other_api(live_server, other_employee_client):
    return ApiSession(live_server.url).login("emp2")


@pytest.fixture
def admin_api(live_server, admin_user):
    return ApiSession(live_server.url).login("admin1")


@pytest.fixture
def anonymous_api(live_server):
    return ApiSession(live_server.url)