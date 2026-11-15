"""Fail-closed validation for Hashmark evidence report dictionaries."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

from hashmark.version import REPORT_SCHEMA_VERSION

HEX_32_PATTERN = re.compile(r"^[0-9a-f]{64}$")
RESULT_STATUSES = frozenset({"PASS", "FAIL", "SKIPPED"})
TARGET_STATUSES = frozenset({"PASS", "FAIL", "NOT_RUN", "UNAVAILABLE"})
RESULT_FIELDS = frozenset(
    {
        "algorithm", "backend", "category", "diagnostic", "evidence_basis", "expected_digest",
        "fe_digest", "input_length_bytes", "input_sha256", "notes", "oracle_digest", "source_case_id",
        "source_document", "source_name", "source_url", "status", "vector_id",
    },
)
TARGET_FIELDS = frozenset({"backend", "command", "diagnostic", "status", "test_identifiers"})
SUMMARY_FIELDS = frozenset(
    {
        "by_algorithm", "by_backend", "differential_comparisons", "failed", "passed", "skipped",
        "status", "target_suites", "total",
    },
)
TOP_LEVEL_FIELDS = frozenset(
    {
        "fixture_manifest_sha256",
        "limitations",
        "project",
        "results",
        "run_configuration",
        "schema_version",
        "source_revision",
        "source_tree_sha256",
        "summary",
        "target_runs",
        "toolchain",
    },
)


class ReportValidationError(ValueError):
    """Raised when report data violates a trust invariant."""


def _mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ReportValidationError(f"{field} must be an object")
    return value


def _sequence(value: Any, field: str) -> list[Any]:
    if not isinstance(value, list):
        raise ReportValidationError(f"{field} must be an array")
    return value


def _digest(value: Any, field: str, *, nullable: bool = False) -> None:
    if value is None and nullable:
        return
    if not isinstance(value, str) or HEX_32_PATTERN.fullmatch(value) is None:
        raise ReportValidationError(f"{field} must be 64 lowercase hexadecimal characters")


def _validate_result(value: Any) -> None:
    result = _mapping(value, "result")
    missing = RESULT_FIELDS - result.keys()
    unknown = result.keys() - RESULT_FIELDS
    if missing or unknown:
        raise ReportValidationError(f"result fields mismatch; missing={sorted(missing)}, unknown={sorted(unknown)}")
    if result["status"] not in RESULT_STATUSES:
        raise ReportValidationError("result has an unknown status")
    if result["backend"] not in {"native", "evm"}:
        raise ReportValidationError("result has an unknown backend")
    if result["algorithm"] not in {"sha256", "keccak256"}:
        raise ReportValidationError("result has an unknown algorithm")
    if result["category"] not in {"known_answer", "boundary", "streaming", "long_message"}:
        raise ReportValidationError("result has an unknown category")
    if not isinstance(result["input_length_bytes"], int) or result["input_length_bytes"] < 0:
        raise ReportValidationError("result input length is invalid")
    _digest(result["expected_digest"], "expected_digest")
    _digest(result["oracle_digest"], "oracle_digest")
    _digest(result["input_sha256"], "input_sha256")
    _digest(result["fe_digest"], "fe_digest", nullable=True)
    source_url = result["source_url"]
    parsed = urlparse(source_url) if isinstance(source_url, str) else None
    if parsed is None or parsed.scheme != "https" or not parsed.netloc:
        raise ReportValidationError("result source URL must be HTTPS")
    for field in ("vector_id", "source_name", "source_document", "source_case_id"):
        if not isinstance(result[field], str) or not result[field]:
            raise ReportValidationError(f"result {field} must be a non-empty string")
    if result["notes"] is not None and not isinstance(result["notes"], str):
        raise ReportValidationError("result notes must be a string or null")
    if result["diagnostic"] is not None and not isinstance(result["diagnostic"], str):
        raise ReportValidationError("result diagnostic must be a string or null")
    basis = result["evidence_basis"]
    if basis not in {"native_digest", "evm_test_status", "unavailable"}:
        raise ReportValidationError("result has an unknown evidence basis")
    if basis == "native_digest" and (result["backend"] != "native" or result["fe_digest"] is None):
        raise ReportValidationError("native digest evidence requires a native Fe digest")
    if basis == "evm_test_status" and (result["backend"] != "evm" or result["fe_digest"] is not None):
        raise ReportValidationError("EVM test evidence cannot claim a per-vector Fe digest")
    if basis == "unavailable" and result["status"] != "SKIPPED":
        raise ReportValidationError("unavailable evidence must be skipped")
    if result["status"] == "PASS" and result["oracle_digest"] != result["expected_digest"]:
        raise ReportValidationError("passing result has an oracle mismatch")
    if (
        result["status"] == "PASS"
        and result["fe_digest"] is not None
        and result["fe_digest"] != result["expected_digest"]
    ):
        raise ReportValidationError("passing result has a Fe mismatch")


def _validate_target(value: Any) -> None:
    target = _mapping(value, "target run")
    missing = TARGET_FIELDS - target.keys()
    unknown = target.keys() - TARGET_FIELDS
    if missing or unknown:
        raise ReportValidationError(f"target fields mismatch; missing={sorted(missing)}, unknown={sorted(unknown)}")
    if target.get("backend") not in {"native", "evm"}:
        raise ReportValidationError("target run has an unknown backend")
    if target.get("status") not in TARGET_STATUSES:
        raise ReportValidationError("target run has an unknown status")
    if not isinstance(target.get("command"), list) or not all(isinstance(item, str) for item in target["command"]):
        raise ReportValidationError("target command must be an array")
    if not isinstance(target.get("test_identifiers"), list) or not all(
        isinstance(item, str) for item in target["test_identifiers"]
    ):
        raise ReportValidationError("target test identifiers must be an array")
    if target["diagnostic"] is not None and not isinstance(target["diagnostic"], str):
        raise ReportValidationError("target diagnostic must be a string or null")


def _validate_metadata(report: dict[str, Any]) -> None:
    project = _mapping(report["project"], "project")
    toolchain = _mapping(report["toolchain"], "toolchain")
    configuration = _mapping(report["run_configuration"], "run configuration")
    if set(project) != {"name", "version"} or not all(isinstance(value, str) and value for value in project.values()):
        raise ReportValidationError("project metadata is invalid")
    if set(toolchain) != {"fe", "python", "pycryptodome"} or not all(
        isinstance(value, str) and value for value in toolchain.values()
    ):
        raise ReportValidationError("toolchain metadata is invalid")
    if set(configuration) != {"algorithms", "backends", "selector"}:
        raise ReportValidationError("run configuration fields are invalid")
    if not isinstance(configuration["algorithms"], list) or not set(configuration["algorithms"]) <= {
        "sha256", "keccak256",
    }:
        raise ReportValidationError("run configuration algorithms are invalid")
    if not isinstance(configuration["backends"], list) or not set(configuration["backends"]) <= {"native", "evm"}:
        raise ReportValidationError("run configuration backends are invalid")
    if not isinstance(configuration["selector"], str) or not configuration["selector"]:
        raise ReportValidationError("run configuration selector is invalid")


def _validate_summary(summary: dict[str, Any], results: list[dict[str, Any]], targets: list[dict[str, Any]]) -> None:
    if set(summary) != SUMMARY_FIELDS:
        raise ReportValidationError("report summary fields are invalid")
    counts = {status: sum(item["status"] == status for item in results) for status in RESULT_STATUSES}
    observed = (summary.get("total"), summary.get("passed"), summary.get("failed"), summary.get("skipped"))
    expected = (len(results), counts["PASS"], counts["FAIL"], counts["SKIPPED"])
    if observed != expected:
        raise ReportValidationError("report summary does not match its result records")
    expected_status = "PASS" if counts["FAIL"] == counts["SKIPPED"] == 0 and all(
        target["status"] == "PASS" for target in targets
    ) else "FAIL"
    if summary.get("status") != expected_status:
        raise ReportValidationError("report overall status is inconsistent")
    suites = _mapping(summary["target_suites"], "target suites")
    comparisons = _mapping(summary["differential_comparisons"], "differential comparisons")
    if suites != {"passed": sum(item["status"] == "PASS" for item in targets), "total": len(targets)}:
        raise ReportValidationError("target suite summary is inconsistent")
    native_results = [item for item in results if item["fe_digest"] is not None]
    expected_comparisons = {
        "passed": sum(item["status"] == "PASS" for item in native_results),
        "total": len(native_results),
    }
    if comparisons != expected_comparisons:
        raise ReportValidationError("differential comparison summary is inconsistent")


def validate_report_data(value: Any) -> dict[str, Any]:
    """Validate a complete report and return it unchanged."""

    report = _mapping(value, "report")
    missing = TOP_LEVEL_FIELDS - report.keys()
    unknown = report.keys() - TOP_LEVEL_FIELDS
    if missing or unknown:
        raise ReportValidationError(
            f"report fields mismatch; missing={sorted(missing)}, unknown={sorted(unknown)}",
        )
    if report["schema_version"] != REPORT_SCHEMA_VERSION:
        raise ReportValidationError("unsupported report schema version")
    _validate_metadata(report)
    _digest(report["fixture_manifest_sha256"], "fixture manifest hash")
    _digest(report["source_tree_sha256"], "source tree hash")
    results = _sequence(report["results"], "results")
    targets = _sequence(report["target_runs"], "target_runs")
    limitations = _sequence(report["limitations"], "limitations")
    if not results or not targets or not limitations:
        raise ReportValidationError("report results, target runs, and limitations must be non-empty")
    for result in results:
        _validate_result(result)
    for target in targets:
        _validate_target(target)

    _validate_summary(_mapping(report["summary"], "summary"), results, targets)
    return report
