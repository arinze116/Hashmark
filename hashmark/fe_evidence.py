"""Strict validation for the Fe-generated HASHMARK/FE-EVIDENCE/1 document.

The Fe native engine evaluates the vector catalogue and emits its evidence
as JSON. This module is the fail-closed reader for that document: every
field is checked against the committed fixtures before any value is used.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from hashmark.fixtures import ALGORITHMS, CATEGORIES, Fixture
from hashmark.protocol import DIGEST_PATTERN
from hashmark.version import FE_VERSION, PROJECT_NAME

FE_EVIDENCE_PROTOCOL = "HASHMARK/FE-EVIDENCE/1"
MAX_EVIDENCE_BYTES = 1024 * 1024

STREAMING_CHECK_NAMES = (
    "sha256_streaming_matches_one_shot",
    "keccak256_streaming_matches_one_shot",
    "sha256_uneven_partition_matches_one_shot",
    "keccak256_uneven_partition_matches_one_shot",
    "sha256_two_part_splits_match_one_shot",
    "keccak256_two_part_splits_match_one_shot",
)

_DOCUMENT_KEYS = frozenset(
    {
        "backend",
        "complete_catalogue",
        "engine",
        "fe_version",
        "project",
        "protocol",
        "results",
        "streaming_checks",
        "summary",
        "target",
    },
)
_RESULT_KEYS = frozenset(
    {
        "algorithm",
        "category",
        "expected_digest",
        "fe_digest",
        "input_length_bytes",
        "input_sha256",
        "status",
        "vector_id",
    },
)
_STREAMING_KEYS = frozenset({"name", "status"})
_SUMMARY_KEYS = frozenset(
    {"failed", "passed", "status", "streaming_passed", "streaming_total", "total"},
)


class FeEvidenceError(ValueError):
    """Raised when Fe evidence is malformed or disagrees with the fixtures."""


@dataclass(frozen=True, slots=True)
class FeVectorEvidence:
    """One vector result emitted by the Fe engine."""

    vector_id: str
    algorithm: str
    category: str
    input_length_bytes: int
    input_sha256: str
    expected_digest: str
    fe_digest: str
    status: str


@dataclass(frozen=True, slots=True)
class FeStreamingCheck:
    """One streaming conformance check emitted by the Fe engine."""

    name: str
    status: str


@dataclass(frozen=True, slots=True)
class FeEvidenceSummary:
    """The Fe engine's own summary of its evidence document."""

    total: int
    passed: int
    failed: int
    streaming_passed: int
    streaming_total: int
    status: str


@dataclass(frozen=True, slots=True)
class FeEvidenceDocument:
    """A complete validated Fe evidence document."""

    results: tuple[FeVectorEvidence, ...]
    streaming_checks: tuple[FeStreamingCheck, ...]
    summary: FeEvidenceSummary
    complete_catalogue: bool


def _require_keys(value: Any, keys: frozenset[str], context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FeEvidenceError(f"{context} must be a JSON object")
    if set(value) != keys:
        raise FeEvidenceError(f"{context} has unexpected fields: {sorted(set(value) ^ keys)}")
    return value


def _require_count(value: Any, context: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise FeEvidenceError(f"{context} must be a non-negative integer")
    return value


def _parse_result(value: Any, fixture: Fixture) -> FeVectorEvidence:
    record = _require_keys(value, _RESULT_KEYS, f"result for {fixture.id}")
    if record["vector_id"] != fixture.id:
        raise FeEvidenceError(f"result vector_id mismatch: {record['vector_id']}")
    if record["algorithm"] != fixture.algorithm or record["algorithm"] not in ALGORITHMS:
        raise FeEvidenceError(f"result algorithm mismatch for {fixture.id}")
    if record["category"] != fixture.category or record["category"] not in CATEGORIES:
        raise FeEvidenceError(f"result category mismatch for {fixture.id}")
    if record["input_length_bytes"] != fixture.input_length_bytes:
        raise FeEvidenceError(f"result input length mismatch for {fixture.id}")
    if record["input_sha256"] != fixture.input_sha256:
        raise FeEvidenceError(f"result input fingerprint mismatch for {fixture.id}")
    if record["expected_digest"] != fixture.expected_digest_hex:
        raise FeEvidenceError(f"result expected digest mismatch for {fixture.id}")
    fe_digest = record["fe_digest"]
    if not isinstance(fe_digest, str) or DIGEST_PATTERN.fullmatch(fe_digest) is None:
        raise FeEvidenceError(f"result Fe digest is malformed for {fixture.id}")
    expected_status = "PASS" if fe_digest == fixture.expected_digest_hex else "FAIL"
    if record["status"] != expected_status:
        raise FeEvidenceError(f"result status is inconsistent for {fixture.id}")
    return FeVectorEvidence(
        vector_id=fixture.id,
        algorithm=fixture.algorithm,
        category=fixture.category,
        input_length_bytes=fixture.input_length_bytes,
        input_sha256=fixture.input_sha256,
        expected_digest=fixture.expected_digest_hex,
        fe_digest=fe_digest,
        status=expected_status,
    )


def parse_fe_evidence(
    data: bytes,
    fixtures: Iterable[Fixture],
    *,
    complete_catalogue: bool,
) -> FeEvidenceDocument:
    """Parse one Fe evidence document and validate it against the fixtures."""

    if not data or len(data) > MAX_EVIDENCE_BYTES:
        raise FeEvidenceError("Fe evidence is empty or exceeds the size limit")
    if not data.endswith(b"\n"):
        raise FeEvidenceError("Fe evidence output is truncated")
    try:
        text = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError as error:
        raise FeEvidenceError("Fe evidence is not UTF-8") from error
    try:
        document = json.loads(text)
    except json.JSONDecodeError as error:
        raise FeEvidenceError(f"Fe evidence is not valid JSON: {error}") from error

    root = _require_keys(document, _DOCUMENT_KEYS, "Fe evidence document")
    if root["protocol"] != FE_EVIDENCE_PROTOCOL:
        raise FeEvidenceError("Fe evidence protocol is not recognised")
    if root["engine"] != "fe" or root["project"] != PROJECT_NAME:
        raise FeEvidenceError("Fe evidence was not produced by the Hashmark Fe engine")
    if root["fe_version"] != FE_VERSION:
        raise FeEvidenceError(f"Fe evidence requires Fe {FE_VERSION}")
    if root["backend"] != "native" or root["target"] != "native":
        raise FeEvidenceError("Fe evidence must describe the native target")
    if root["complete_catalogue"] is not complete_catalogue:
        raise FeEvidenceError("Fe evidence catalogue scope does not match the run selection")

    fixture_list = list(fixtures)
    fixtures_by_id = {item.id: item for item in fixture_list}
    raw_results = root["results"]
    if not isinstance(raw_results, list) or len(raw_results) != len(fixture_list):
        raise FeEvidenceError("Fe evidence result count does not match the selection")
    results: list[FeVectorEvidence] = []
    seen: set[str] = set()
    for value in raw_results:
        if not isinstance(value, dict) or value.get("vector_id") not in fixtures_by_id:
            raise FeEvidenceError("Fe evidence contains an unknown vector result")
        vector_id = value["vector_id"]
        if vector_id in seen:
            raise FeEvidenceError(f"Fe evidence duplicates vector result: {vector_id}")
        seen.add(vector_id)
        results.append(_parse_result(value, fixtures_by_id[vector_id]))
    if seen != set(fixtures_by_id):
        raise FeEvidenceError("Fe evidence result set does not match the selection")

    raw_streaming = root["streaming_checks"]
    if not isinstance(raw_streaming, list) or len(raw_streaming) != len(STREAMING_CHECK_NAMES):
        raise FeEvidenceError("Fe evidence streaming checks are incomplete")
    streaming: list[FeStreamingCheck] = []
    for value, expected_name in zip(raw_streaming, STREAMING_CHECK_NAMES, strict=True):
        record = _require_keys(value, _STREAMING_KEYS, f"streaming check {expected_name}")
        if record["name"] != expected_name:
            raise FeEvidenceError(f"streaming check order mismatch: {record['name']}")
        if record["status"] not in {"PASS", "FAIL"}:
            raise FeEvidenceError(f"streaming check status is invalid: {expected_name}")
        streaming.append(FeStreamingCheck(expected_name, record["status"]))

    summary = _require_keys(root["summary"], _SUMMARY_KEYS, "Fe evidence summary")
    total = _require_count(summary["total"], "summary total")
    passed = _require_count(summary["passed"], "summary passed")
    failed = _require_count(summary["failed"], "summary failed")
    streaming_passed = _require_count(summary["streaming_passed"], "summary streaming_passed")
    streaming_total = _require_count(summary["streaming_total"], "summary streaming_total")
    observed_passed = sum(item.status == "PASS" for item in results)
    observed_streaming = sum(item.status == "PASS" for item in streaming)
    if (total, passed, failed) != (len(results), observed_passed, len(results) - observed_passed):
        raise FeEvidenceError("Fe evidence summary does not match its vector results")
    if (streaming_total, streaming_passed) != (len(streaming), observed_streaming):
        raise FeEvidenceError("Fe evidence summary does not match its streaming checks")
    expected_summary_status = "PASS" if failed == 0 and streaming_passed == len(streaming) else "FAIL"
    if summary["status"] != expected_summary_status:
        raise FeEvidenceError("Fe evidence summary status is inconsistent")
    return FeEvidenceDocument(
        results=tuple(results),
        streaming_checks=tuple(streaming),
        summary=FeEvidenceSummary(
            total=total,
            passed=passed,
            failed=failed,
            streaming_passed=streaming_passed,
            streaming_total=streaming_total,
            status=expected_summary_status,
        ),
        complete_catalogue=complete_catalogue,
    )
