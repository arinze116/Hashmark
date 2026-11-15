"""Typed immutable evidence models shared by the CLI and report renderers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from hashmark.fixtures import Fixture


@dataclass(frozen=True, slots=True)
class EvidenceResult:
    """One fixture result on one requested backend."""

    fixture: Fixture
    backend: str
    fe_digest: str | None
    oracle_digest: str
    status: str
    evidence_basis: str
    diagnostic: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return the stable public report representation."""

        return {
            "algorithm": self.fixture.algorithm,
            "backend": self.backend,
            "category": self.fixture.category,
            "diagnostic": self.diagnostic,
            "evidence_basis": self.evidence_basis,
            "expected_digest": self.fixture.expected_digest_hex,
            "fe_digest": self.fe_digest,
            "input_length_bytes": self.fixture.input_length_bytes,
            "input_sha256": self.fixture.input_sha256,
            "notes": self.fixture.notes,
            "oracle_digest": self.oracle_digest,
            "source_case_id": self.fixture.source_case_id,
            "source_document": self.fixture.source_document,
            "source_name": self.fixture.source_name,
            "source_url": self.fixture.source_url,
            "status": self.status,
            "vector_id": self.fixture.id,
        }


@dataclass(frozen=True, slots=True)
class TargetEvidence:
    """Aggregate evidence from one Fe target invocation."""

    backend: str
    status: str
    command: tuple[str, ...]
    test_identifiers: tuple[str, ...]
    diagnostic: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return the stable public report representation."""

        return {
            "backend": self.backend,
            "command": list(self.command),
            "diagnostic": self.diagnostic,
            "status": self.status,
            "test_identifiers": list(self.test_identifiers),
        }


def result_sort_key(result: EvidenceResult) -> tuple[str, str, str]:
    """Return the canonical ordering for deterministic reports."""

    return result.fixture.algorithm, result.fixture.id, result.backend
