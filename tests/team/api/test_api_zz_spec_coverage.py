"""API coverage criteria, checked against the OpenAPI spec after all API tests have run.

This file sorts last in the folder, so it sees what the other API tests did.
Criteria: (1) every operation (path and method) was called, (2) every documented status
code was observed for its operation, (3) every generated EP and BVA case was executed.
Undocumented status codes are written to the report as endpoint weaknesses.
"""
import json
from pathlib import Path

import yaml

from api_helpers import DATA_FILE, EXECUTED_CASES, OBSERVED, SPEC_FILE

REPORT = Path(__file__).resolve().parents[3] / "evidence" / "reports" / "api_coverage.json"


def test_api_coverage_criteria():
    spec = yaml.safe_load(open(SPEC_FILE, encoding="utf-8"))
    documented = {}
    for path, methods in spec["paths"].items():
        for method, definition in methods.items():
            documented[definition["operationId"]] = {
                "operation": f"{method.upper()} {path}",
                "statuses": sorted(int(code) for code in definition["responses"]),
            }

    observed = {}
    for operation, status in OBSERVED:
        observed.setdefault(operation, set()).add(status)

    never_called = [op for op in documented if op not in observed]
    missing_statuses = {
        op: sorted(set(info["statuses"]) - observed.get(op, set()))
        for op, info in documented.items()
        if set(info["statuses"]) - observed.get(op, set())
    }
    weaknesses = {
        op: sorted(observed[op] - set(info["statuses"]))
        for op, info in documented.items()
        if op in observed and observed[op] - set(info["statuses"])
    }
    all_cases = {c["id"] for c in json.load(open(DATA_FILE, encoding="utf-8"))["cases"]}
    cases_not_run = sorted(all_cases - EXECUTED_CASES)

    report = {
        "operations_documented": len(documented),
        "operations_called": len(documented) - len(never_called),
        "status_codes_documented": sum(len(i["statuses"]) for i in documented.values()),
        "status_codes_observed_as_documented": sum(
            len(set(i["statuses"]) & observed.get(op, set())) for op, i in documented.items()),
        "generated_cases": len(all_cases),
        "generated_cases_executed": len(all_cases) - len(cases_not_run),
        "endpoint_weaknesses_undocumented_status_codes": weaknesses,
        "never_called": never_called,
        "documented_status_never_observed": missing_statuses,
        "generated_cases_not_run": cases_not_run,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")

    assert never_called == []
    assert missing_statuses == {}
    assert cases_not_run == []