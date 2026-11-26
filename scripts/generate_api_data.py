"""Generate equivalence classes and 3-point boundary values from an OpenAPI spec.

Usage:
  python scripts/generate_api_data.py SPEC.yaml OUT.json
  python scripts/generate_api_data.py --diff OLD.json NEW.json

Rules (applied to every input found in request bodies and path parameters):
  enum            EP: each valid value, a value outside the enum, empty, missing
  format: date    EP: a valid date, non-date text, an impossible date, empty, missing
  integer         EP: below minimum, inside range, above maximum, non-integer text
                  BVA: min-1, min, min+1 and max-1, max, max+1 (only the limits that exist)
  string          EP: typical value, empty (when minLength > 0), missing (when required)
                  BVA: minLength-1, minLength, minLength+1 and the same for maxLength
  x-durationDays  a derived input (end date minus start date plus 1) treated as integer
"""
import json
import sys

import yaml

TYPICAL_DATE = "2027-01-04"


def resolve(spec, node):
    while isinstance(node, dict) and "$ref" in node:
        target = spec
        for part in node["$ref"].lstrip("#/").split("/"):
            target = target[part]
        node = target
    return node


def case(op, name, technique, klass, value, valid, note=""):
    safe = str(klass).replace(" ", "_")
    return {
        "id": f"{op['operationId']}.{name}.{technique}.{safe}",
        "operation": op["operationId"], "method": op["method"], "path": op["path"],
        "input": name, "technique": technique, "class": klass,
        "value": value, "valid": valid, "note": note,
    }


def integer_cases(op, name, lo, hi, as_text=True):
    out = []
    if lo is not None:
        out.append(case(op, name, "EP", "invalid_below_min", lo - 5, False))
    inside = (lo + hi) // 2 if (lo is not None and hi is not None) else (lo or 0) + 5
    out.append(case(op, name, "EP", "valid_inside", inside, True))
    if hi is not None:
        out.append(case(op, name, "EP", "invalid_above_max", hi + 5 * hi, False))
    if as_text:
        out.append(case(op, name, "EP", "invalid_not_integer", "abc", False))
    if lo is not None:
        out += [case(op, name, "BVA", "min-1", lo - 1, False),
                case(op, name, "BVA", "min", lo, True),
                case(op, name, "BVA", "min+1", lo + 1, True)]
    if hi is not None:
        out += [case(op, name, "BVA", "max-1", hi - 1, True),
                case(op, name, "BVA", "max", hi, True),
                case(op, name, "BVA", "max+1", hi + 1, False)]
    return out


def string_cases(op, name, schema, required):
    out = []
    if "enum" in schema:
        for value in schema["enum"]:
            out.append(case(op, name, "EP", f"valid_{value}", value, True))
        out.append(case(op, name, "EP", "invalid_not_in_enum", "Unknown Leave", False))
        out.append(case(op, name, "EP", "invalid_empty", "", False))
    elif schema.get("format") == "date":
        out.append(case(op, name, "EP", "valid_date", TYPICAL_DATE, True))
        out.append(case(op, name, "EP", "invalid_text", "notadate", False))
        out.append(case(op, name, "EP", "invalid_impossible_date", "2027-02-30", False))
        out.append(case(op, name, "EP", "invalid_empty", "", False))
    else:
        lo, hi = schema.get("minLength"), schema.get("maxLength")
        out.append(case(op, name, "EP", "valid_typical", "x" * ((lo or 1) + 4), True))
        if lo:
            out.append(case(op, name, "EP", "invalid_empty", "", False))
            for length, label, valid in [(lo - 1, "minLength-1", False), (lo, "minLength", True),
                                         (lo + 1, "minLength+1", True)]:
                out.append(case(op, name, "BVA", label, "x" * length, valid, f"length {length}"))
        if hi:
            for length, label, valid in [(hi - 1, "maxLength-1", True), (hi, "maxLength", True),
                                         (hi + 1, "maxLength+1", False)]:
                out.append(case(op, name, "BVA", label, "x" * length, valid, f"length {length}"))
            out.append(case(op, name, "EP", "invalid_above_maxLength", "x" * (hi * 2), False))
    if required:
        out.append(case(op, name, "EP", "invalid_missing", None, False))
    return out


def generate(spec_path):
    with open(spec_path, encoding="utf-8") as handle:
        spec = yaml.safe_load(handle)
    cases = []
    for path, methods in spec["paths"].items():
        for method, definition in methods.items():
            op = {"operationId": definition["operationId"], "method": method.upper(), "path": path}
            for parameter in definition.get("parameters", []):
                parameter = resolve(spec, parameter)
                schema = parameter["schema"]
                if schema["type"] == "integer":
                    cases += integer_cases(op, parameter["name"], schema.get("minimum"),
                                           schema.get("maximum"))
            body = definition.get("requestBody", {}).get("content", {})
            for media in body.values():
                schema = resolve(spec, media["schema"])
                required = schema.get("required", [])
                for name, prop in schema.get("properties", {}).items():
                    cases += string_cases(op, name, prop, name in required) \
                        if prop["type"] == "string" else []
                if "x-durationDays" in schema:
                    limits = schema["x-durationDays"]
                    cases += integer_cases(op, "durationDays", limits.get("minimum"),
                                           limits.get("maximum"), as_text=False)
    return {"spec": spec_path, "spec_version": spec["info"]["version"],
            "total": len(cases), "cases": cases}


def diff(old_path, new_path):
    old = {c["id"]: c for c in json.load(open(old_path, encoding="utf-8"))["cases"]}
    new = {c["id"]: c for c in json.load(open(new_path, encoding="utf-8"))["cases"]}
    lines = [f"cases: {len(old)} -> {len(new)}"]
    for key in sorted(set(old) | set(new)):
        if key not in new:
            lines.append(f"REMOVED  {key}")
        elif key not in old:
            lines.append(f"ADDED    {key}  value={new[key]['value']!r} valid={new[key]['valid']}")
        elif (old[key]["value"], old[key]["valid"]) != (new[key]["value"], new[key]["valid"]):
            lines.append(f"CHANGED  {key}  {old[key]['value']!r}/{old[key]['valid']} -> "
                         f"{new[key]['value']!r}/{new[key]['valid']}")
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--diff":
        print(diff(sys.argv[2], sys.argv[3]))
    elif len(sys.argv) == 3:
        result = generate(sys.argv[1])
        with open(sys.argv[2], "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2)
        by = {}
        for c in result["cases"]:
            by[(c["operation"], c["technique"])] = by.get((c["operation"], c["technique"]), 0) + 1
        print(f"{result['spec']}: {result['total']} cases written to {sys.argv[2]}")
        for (op, tech), n in sorted(by.items()):
            print(f"  {op:14s} {tech:4s} {n}")
    else:
        sys.exit(__doc__)