"""Review the age and outcome of evidence against a small control register."""
import argparse
import csv
from datetime import date
from pathlib import Path


def read_csv(path, fields):
    with path.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames != fields:
            raise ValueError(f"{path.name}: expected columns {', '.join(fields)}")
        rows = list(reader)
    if any(None in row or any(not v or not v.strip() for v in row.values()) for row in rows):
        raise ValueError(f"{path.name}: incomplete row or extra field")
    return rows


def review(controls, evidence, as_of):
    register = {}
    for control in controls:
        key = control["control_id"]
        days = int(control["max_age_days"])
        if key in register or days < 0:
            raise ValueError(f"Duplicate control or negative review interval: {key}")
        register[key] = (control["owner"], days)
    if not register:
        raise ValueError("Empty control register")
    latest = {}
    seen = set()
    for record in evidence:
        key = record["control_id"]
        observed = date.fromisoformat(record["checked_on"])
        if key not in register or record["result"] not in ("pass", "fail"):
            raise ValueError(f"Unknown control or result: {key}")
        if (key, observed) in seen:
            raise ValueError(f"Ambiguous observations for {key} on {observed}")
        seen.add((key, observed))
        if observed <= as_of and (key not in latest or observed > latest[key][0]):
            latest[key] = (observed, record["result"], record["reference"])
    report = []
    for key, (owner, days) in register.items():
        status, age, reference = "missing", None, "-"
        if key in latest:
            observed, result, reference = latest[key]
            age = (as_of - observed).days
            if result == "fail":
                status = "failed"
            elif age > days:
                status = "stale"
            else:
                status = "current"
        report.append((key, owner, status, age, reference))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("controls", type=Path)
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--as-of", required=True, type=date.fromisoformat)
    args = parser.parse_args()
    try:
        controls = read_csv(args.controls, ["control_id", "owner", "max_age_days"])
        evidence = read_csv(args.evidence, ["control_id", "checked_on", "result", "reference"])
        rows = review(controls, evidence, args.as_of)
    except (OSError, ValueError, csv.Error) as error:
        parser.exit(2, f"Input error: {error}\n")
    print("CONTROL     OWNER          STATUS     AGE (DAYS)  REFERENCE")
    for key, owner, status, age, reference in rows:
        age_text = "-" if age is None else str(age)
        print(f"{key:11} {owner:14} {status:10} {age_text:11} {reference}")


if __name__ == "__main__":
    main()
