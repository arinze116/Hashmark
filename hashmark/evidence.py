"""Derive report evidence from validated Fe target outcomes."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Protocol

from hashmark.fixtures import Fixture
from hashmark.models import EvidenceResult, TargetEvidence
from hashmark.report import portable_command


class NativeRecordLike(Protocol):
    """Fields required from a validated native protocol record."""

    vector_id: str
    input_length_bytes: int
    digest_hex: str
    status: str


class TargetRunLike(Protocol):
    """Fields required from a Fe target execution."""

    backend: str
    status: str
    command: tuple[str, ...]
    test_identifiers: tuple[str, ...]
    diagnostic: str | None


def target_evidence(
    target: TargetRunLike,
    project_root: Path,
    fe_binary: Path,
) -> TargetEvidence:
    """Convert an internal target execution to portable report evidence."""

    return TargetEvidence(
        backend=target.backend,
        status=target.status,
        command=portable_command(target.command, project_root, fe_binary),
        test_identifiers=target.test_identifiers,
        diagnostic=target.diagnostic,
    )


def evm_results(
    fixtures: Iterable[Fixture],
    oracle_digests: Mapping[str, str],
    target: TargetEvidence,
) -> list[EvidenceResult]:
    """Represent aggregate EVM test evidence for each selected fixture."""

    results = []
    for fixture in fixtures:
        oracle_matches = oracle_digests[fixture.id] == fixture.expected_digest_hex
        passed = target.status == "PASS" and oracle_matches
        diagnostic = None if passed else target.diagnostic or "expected digest does not match the independent oracle"
        results.append(
            EvidenceResult(
                fixture=fixture,
                backend="evm",
                fe_digest=None,
                oracle_digest=oracle_digests[fixture.id],
                status="PASS" if passed else "FAIL",
                evidence_basis="evm_test_status",
                diagnostic=diagnostic,
            ),
        )
    return results


def native_results(
    fixtures: Iterable[Fixture],
    oracle_digests: Mapping[str, str],
    records: Iterable[NativeRecordLike],
) -> list[EvidenceResult]:
    """Compare validated native digests with fixtures and the independent oracle."""

    records_by_id = {record.vector_id: record for record in records}
    results = []
    for fixture in fixtures:
        record = records_by_id[fixture.id]
        passed = (
            record.status == "pass"
            and record.digest_hex == fixture.expected_digest_hex
            and record.digest_hex == oracle_digests[fixture.id]
            and record.input_length_bytes == fixture.input_length_bytes
        )
        results.append(
            EvidenceResult(
                fixture=fixture,
                backend="native",
                fe_digest=record.digest_hex,
                oracle_digest=oracle_digests[fixture.id],
                status="PASS" if passed else "FAIL",
                evidence_basis="native_digest",
                diagnostic=None if passed else "Fe, fixture, oracle, or input length mismatch",
            ),
        )
    return results


def skipped_results(
    fixtures: Iterable[Fixture],
    backend: str,
    oracle_digests: Mapping[str, str],
    diagnostic: str,
) -> list[EvidenceResult]:
    """Create explicit skipped records for an unavailable target."""

    return [
        EvidenceResult(
            fixture=fixture,
            backend=backend,
            fe_digest=None,
            oracle_digest=oracle_digests[fixture.id],
            status="SKIPPED",
            evidence_basis="unavailable",
            diagnostic=diagnostic,
        )
        for fixture in fixtures
    ]


def unavailable_target(backend: str, diagnostic: str) -> TargetEvidence:
    """Create explicit target evidence when a requested backend cannot run."""

    return TargetEvidence(
        backend=backend,
        status="UNAVAILABLE",
        command=("fe", "test", "--backend", "sonatina" if backend == "evm" else "native"),
        test_identifiers=(),
        diagnostic=diagnostic,
    )
