"""Strict loading and validation for committed Hashmark vectors."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from hashmark.version import FIXTURE_SCHEMA_VERSION

ALGORITHMS = frozenset({"sha256", "keccak256"})
CATEGORIES = frozenset({"known_answer", "boundary", "streaming", "long_message"})
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
HEX_PATTERN = re.compile(r"^[0-9a-f]*$")
MAX_FIXTURES = 10_000
MAX_INPUT_BYTES = 1_048_576
MAX_NOTES_CHARS = 1_000

REQUIRED_FIELDS = frozenset(
    {
        "schema_version",
        "id",
        "algorithm",
        "category",
        "input_hex",
        "expected_digest_hex",
        "input_length_bytes",
        "source_name",
        "source_url",
        "source_document",
        "source_case_id",
        "licence_or_usage_note",
        "notes",
    },
)


class FixtureError(ValueError):
    """Raised when fixture data cannot be trusted."""


@dataclass(frozen=True, slots=True)
class Fixture:
    """A validated immutable conformance vector."""

    schema_version: int
    id: str
    algorithm: str
    category: str
    input_hex: str
    expected_digest_hex: str
    input_length_bytes: int
    source_name: str
    source_url: str
    source_document: str
    source_case_id: str
    licence_or_usage_note: str
    notes: str | None

    @property
    def input_bytes(self) -> bytes:
        """Return the decoded vector input."""

        return bytes.fromhex(self.input_hex)

    @property
    def input_sha256(self) -> str:
        """Return the content fingerprint used in evidence reports."""

        return hashlib.sha256(self.input_bytes).hexdigest()


def _require_mapping(value: Any, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FixtureError(f"{context} must be a JSON object")
    return value


def _require_string(record: dict[str, Any], field: str, maximum: int) -> str:
    value = record.get(field)
    if not isinstance(value, str) or not value or len(value) > maximum:
        raise FixtureError(f"{field} must be a non-empty string of at most {maximum} characters")
    return value


def _validate_hex(value: Any, field: str, expected_bytes: int | None = None) -> str:
    if not isinstance(value, str) or len(value) % 2 or HEX_PATTERN.fullmatch(value.lower()) is None:
        raise FixtureError(f"{field} must be even-length hexadecimal")
    canonical = value.lower()
    if expected_bytes is not None and len(canonical) != expected_bytes * 2:
        raise FixtureError(f"{field} must encode exactly {expected_bytes} bytes")
    return canonical


def _validate_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        raise FixtureError("source_url must be an absolute HTTPS URL")
    return value


def parse_fixture(record_value: Any, source: Path) -> Fixture:
    """Validate one fixture record and return its typed representation."""

    record = _require_mapping(record_value, str(source))
    missing = REQUIRED_FIELDS - record.keys()
    unknown = record.keys() - REQUIRED_FIELDS
    if missing:
        raise FixtureError(f"{source}: missing fields: {', '.join(sorted(missing))}")
    if unknown:
        raise FixtureError(f"{source}: unknown fields: {', '.join(sorted(unknown))}")
    if record["schema_version"] != FIXTURE_SCHEMA_VERSION:
        raise FixtureError(f"{source}: unsupported fixture schema version")

    fixture_id = _require_string(record, "id", 64)
    if ID_PATTERN.fullmatch(fixture_id) is None:
        raise FixtureError(f"{source}: invalid fixture id: {fixture_id}")
    algorithm = record["algorithm"]
    if algorithm not in ALGORITHMS:
        raise FixtureError(f"{source}: unsupported algorithm: {algorithm}")
    category = record["category"]
    if category not in CATEGORIES:
        raise FixtureError(f"{source}: unsupported category: {category}")

    input_hex = _validate_hex(record["input_hex"], "input_hex")
    input_length = record["input_length_bytes"]
    if not isinstance(input_length, int) or isinstance(input_length, bool):
        raise FixtureError(f"{source}: input_length_bytes must be an integer")
    if not 0 <= input_length <= MAX_INPUT_BYTES or len(input_hex) // 2 != input_length:
        raise FixtureError(f"{source}: input length does not match input_hex")
    expected = _validate_hex(record["expected_digest_hex"], "expected_digest_hex", 32)
    if expected != record["expected_digest_hex"]:
        raise FixtureError(f"{source}: expected_digest_hex must be lowercase and unprefixed")

    notes = record["notes"]
    if notes is not None and (not isinstance(notes, str) or len(notes) > MAX_NOTES_CHARS):
        raise FixtureError(f"{source}: notes must be null or at most {MAX_NOTES_CHARS} characters")
    return Fixture(
        schema_version=FIXTURE_SCHEMA_VERSION,
        id=fixture_id,
        algorithm=algorithm,
        category=category,
        input_hex=input_hex,
        expected_digest_hex=expected,
        input_length_bytes=input_length,
        source_name=_require_string(record, "source_name", 120),
        source_url=_validate_url(_require_string(record, "source_url", 500)),
        source_document=_require_string(record, "source_document", 200),
        source_case_id=_require_string(record, "source_case_id", 120),
        licence_or_usage_note=_require_string(record, "licence_or_usage_note", 500),
        notes=notes,
    )


def _load_document(path: Path) -> list[Fixture]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise FixtureError(f"could not parse {path}: {error}") from error
    document = _require_mapping(raw, str(path))
    if set(document) != {"schema_version", "vectors"}:
        raise FixtureError(f"{path}: document fields must be schema_version and vectors")
    if document["schema_version"] != FIXTURE_SCHEMA_VERSION:
        raise FixtureError(f"{path}: unsupported document schema version")
    values = document["vectors"]
    if not isinstance(values, list) or not values:
        raise FixtureError(f"{path}: vectors must be a non-empty array")
    return [parse_fixture(value, path) for value in values]


def fixture_paths(root: Path) -> list[Path]:
    """Return fixture documents in deterministic order."""

    return sorted(path for algorithm in sorted(ALGORITHMS) for path in (root / algorithm).glob("*.json"))


def load_fixtures(root: Path = Path("vectors")) -> list[Fixture]:
    """Load all fixture files and reject duplicate or misplaced records."""

    paths = fixture_paths(root)
    if not paths:
        raise FixtureError(f"no fixture files found under {root}")
    fixtures: list[Fixture] = []
    seen: dict[str, Path] = {}
    for path in paths:
        for fixture in _load_document(path):
            if fixture.algorithm != path.parent.name:
                raise FixtureError(f"{path}: {fixture.id} is in the wrong algorithm directory")
            if fixture.id in seen:
                raise FixtureError(f"duplicate fixture id {fixture.id}: {seen[fixture.id]} and {path}")
            seen[fixture.id] = path
            fixtures.append(fixture)
            if len(fixtures) > MAX_FIXTURES:
                raise FixtureError(f"fixture count exceeds {MAX_FIXTURES}")
    return sorted(fixtures, key=lambda item: (item.algorithm, item.id))


def select_fixtures(
    fixtures: Iterable[Fixture],
    *,
    algorithm: str | None = None,
    vector_id: str | None = None,
) -> list[Fixture]:
    """Select fixtures by one exact algorithm or vector identifier."""

    if algorithm is not None and algorithm not in ALGORITHMS:
        raise FixtureError(f"unsupported algorithm: {algorithm}")
    selected = [
        item
        for item in fixtures
        if (algorithm is None or item.algorithm == algorithm)
        and (vector_id is None or item.id == vector_id)
    ]
    if vector_id is not None and not selected:
        raise FixtureError(f"unknown vector id: {vector_id}")
    if not selected:
        raise FixtureError("fixture selection produced no results")
    return selected


def fixture_manifest_sha256(root: Path = Path("vectors")) -> str:
    """Hash every fixture document path and byte sequence deterministically."""

    state = hashlib.sha256()
    for path in fixture_paths(root):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        state.update(len(relative).to_bytes(4, "big"))
        state.update(relative)
        data = path.read_bytes()
        state.update(len(data).to_bytes(8, "big"))
        state.update(data)
    return state.hexdigest()
