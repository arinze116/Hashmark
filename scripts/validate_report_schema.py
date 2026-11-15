"""Validate a Hashmark JSON report against the published JSON Schema."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from jsonschema import Draft202012Validator

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    """Validate one report path and return zero on success."""

    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    arguments = parser.parse_args()
    schema_path = PROJECT_ROOT / "reports" / "schema" / "hashmark-report.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    report = json.loads(arguments.report.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(report)
    print(f"VALID: {arguments.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
