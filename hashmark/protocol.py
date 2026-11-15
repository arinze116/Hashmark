"""Strict parser for the deterministic HASHMARK/1 native protocol."""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass

from hashmark.fixtures import ALGORITHMS, ID_PATTERN
from hashmark.version import PROTOCOL_PREFIX

DIGEST_PATTERN = re.compile(r"^[0-9a-f]{64}$")
SAFE_FIELD_PATTERN = re.compile(r"^[a-z0-9._-]+$")
MAX_PROTOCOL_BYTES = 32 * 1024 * 1024


class ProtocolError(ValueError):
    """Raised when native output is incomplete, malformed, or inconsistent."""


@dataclass(frozen=True, slots=True)
class NativeRecord:
    """One validated native vector result."""

    vector_id: str
    algorithm: str
    input_length_bytes: int
    digest_hex: str
    backend: str
    status: str


@dataclass(frozen=True, slots=True)
class ProtocolSummary:
    """The validated final native summary record."""

    total: int
    passed: int
    failed: int


@dataclass(frozen=True, slots=True)
class ProtocolRun:
    """A complete validated native protocol stream."""

    records: tuple[NativeRecord, ...]
    summary: ProtocolSummary


def _parse_uint(value: str, field: str) -> int:
    if not value or not value.isascii() or not value.isdecimal():
        raise ProtocolError(f"{field} must be base-10 digits")
    parsed = int(value)
    if parsed > 1_048_576:
        raise ProtocolError(f"{field} is out of bounds")
    return parsed


def _parse_record(fields: list[str], known_ids: set[str] | None) -> NativeRecord:
    if len(fields) != 7:
        raise ProtocolError("native record has the wrong field count")
    _, vector_id, algorithm, input_length, digest_hex, backend, status = fields
    if ID_PATTERN.fullmatch(vector_id) is None:
        raise ProtocolError(f"invalid vector id in native record: {vector_id}")
    if known_ids is not None and vector_id not in known_ids:
        raise ProtocolError(f"unknown vector id in native record: {vector_id}")
    if algorithm not in ALGORITHMS:
        raise ProtocolError(f"unknown algorithm in native record: {algorithm}")
    if DIGEST_PATTERN.fullmatch(digest_hex) is None:
        raise ProtocolError(f"invalid digest in native record: {vector_id}")
    if backend != "native":
        raise ProtocolError(f"invalid backend in native record: {backend}")
    if status not in {"pass", "fail"} or SAFE_FIELD_PATTERN.fullmatch(status) is None:
        raise ProtocolError(f"invalid status in native record: {status}")
    return NativeRecord(
        vector_id=vector_id,
        algorithm=algorithm,
        input_length_bytes=_parse_uint(input_length, "input length"),
        digest_hex=digest_hex,
        backend=backend,
        status=status,
    )


def _parse_summary(fields: list[str]) -> ProtocolSummary:
    if len(fields) != 5 or fields[1] != "SUMMARY":
        raise ProtocolError("summary record has the wrong field count")
    return ProtocolSummary(
        total=_parse_uint(fields[2], "summary total"),
        passed=_parse_uint(fields[3], "summary passed"),
        failed=_parse_uint(fields[4], "summary failed"),
    )


def parse_protocol(stdout: bytes, known_ids: Iterable[str] | None = None) -> ProtocolRun:
    """Parse a complete protocol stream and reject any inconsistency."""

    if not stdout or len(stdout) > MAX_PROTOCOL_BYTES:
        raise ProtocolError("native protocol output is empty or exceeds the size limit")
    if not stdout.endswith(b"\n"):
        raise ProtocolError("native protocol output is truncated")
    try:
        text = stdout.decode("utf-8", errors="strict")
    except UnicodeDecodeError as error:
        raise ProtocolError("native protocol output is not UTF-8") from error

    allowed_ids = set(known_ids) if known_ids is not None else None
    records: list[NativeRecord] = []
    seen: set[str] = set()
    summary: ProtocolSummary | None = None
    for line_number, line in enumerate(text.splitlines(), start=1):
        fields = line.split("\t")
        if not fields or fields[0] != PROTOCOL_PREFIX:
            raise ProtocolError(f"line {line_number}: unknown protocol prefix")
        if len(fields) > 1 and fields[1] == "SUMMARY":
            if summary is not None:
                raise ProtocolError("duplicate summary record")
            summary = _parse_summary(fields)
            continue
        if summary is not None:
            raise ProtocolError("native record appears after the summary")
        record = _parse_record(fields, allowed_ids)
        if record.vector_id in seen:
            raise ProtocolError(f"duplicate native result: {record.vector_id}")
        seen.add(record.vector_id)
        records.append(record)

    if summary is None:
        raise ProtocolError("native protocol summary is missing")
    if allowed_ids is not None and seen != allowed_ids:
        missing = sorted(allowed_ids - seen)
        unexpected = sorted(seen - allowed_ids)
        raise ProtocolError(f"native result set mismatch; missing={missing}, unexpected={unexpected}")
    passed = sum(record.status == "pass" for record in records)
    failed = len(records) - passed
    if (summary.total, summary.passed, summary.failed) != (len(records), passed, failed):
        raise ProtocolError("native summary does not match its result records")
    return ProtocolRun(records=tuple(records), summary=summary)
