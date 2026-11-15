"""End-to-end Hashmark conformance workflow orchestration."""

from __future__ import annotations

import argparse
import os
import platform
from dataclasses import dataclass
from pathlib import Path
from time import monotonic

from hashmark.evidence import (
    evm_results,
    native_results,
    skipped_results,
    target_evidence,
    unavailable_target,
)
from hashmark.exit_codes import (
    EXIT_ARGUMENT,
    EXIT_CONFORMANCE,
    EXIT_EXECUTION,
    EXIT_TOOLCHAIN,
)
from hashmark.fe_runner import (
    ConformanceFailureError,
    RunnerProcessError,
    RunnerTimeoutError,
    ToolchainMissingError,
    discover_fe,
    require_fe_version,
    run_evm_tests,
    run_native,
)
from hashmark.fixtures import (
    Fixture,
    fixture_manifest_sha256,
    load_fixtures,
    select_fixtures,
)
from hashmark.models import EvidenceResult, TargetEvidence
from hashmark.oracle import digest_hex, pycryptodome_version
from hashmark.protocol import ProtocolError
from hashmark.report import (
    ReportWriteError,
    build_report,
    write_report_bundle,
    write_report_file,
)
from hashmark.version import PYCRYPTODOME_VERSION, PYTHON_VERSION


@dataclass(frozen=True, slots=True)
class RunSelection:
    """Normalized vector and backend selection."""

    fixtures: tuple[Fixture, ...]
    backends: tuple[str, ...]
    native_arguments: tuple[str, ...]
    evm_filter: str | None
    label: str


@dataclass(frozen=True, slots=True)
class BackendOutcome:
    """Evidence and exit status produced by one requested backend."""

    target: TargetEvidence
    results: tuple[EvidenceResult, ...]
    exit_code: int
    native_protocol: bytes | None = None


def require_python_toolchain() -> None:
    """Require the exact Python and independent-oracle versions."""

    detected = platform.python_version()
    if detected != PYTHON_VERSION:
        raise ToolchainMissingError(f"Hashmark requires Python {PYTHON_VERSION}; detected {detected}")
    oracle_version = pycryptodome_version()
    if oracle_version != PYCRYPTODOME_VERSION:
        raise ToolchainMissingError(
            f"Hashmark requires PyCryptodome {PYCRYPTODOME_VERSION}; detected {oracle_version}",
        )


def _selection(arguments: argparse.Namespace, fixtures: list[Fixture]) -> RunSelection:
    selected = select_fixtures(fixtures, algorithm=arguments.algorithm, vector_id=arguments.vector)
    backends = ("native", "evm") if arguments.backend == "all" else (arguments.backend,)
    if arguments.algorithm is not None:
        return RunSelection(
            tuple(selected), backends, ("--algorithm", arguments.algorithm), arguments.algorithm, arguments.algorithm,
        )
    if arguments.vector is not None:
        return RunSelection(tuple(selected), backends, ("--vector", arguments.vector), None, arguments.vector)
    return RunSelection(tuple(selected), backends, ("--all",), None, "all")


def _report_paths(
    arguments: argparse.Namespace,
    report: dict[str, object],
    native_protocol: bytes | None,
    project_root: Path,
) -> tuple[Path, ...]:
    if arguments.format == "terminal":
        if arguments.output is not None or arguments.output_dir is not None:
            raise ReportWriteError("--output and --output-dir cannot be used with terminal format")
        return ()
    if arguments.output is not None:
        if arguments.format == "all":
            raise ReportWriteError("--output requires json, markdown, or html format; use --output-dir with all")
        return write_report_file(report, arguments.format, arguments.output, force=arguments.force)
    output_directory = arguments.output_dir
    if output_directory is None:
        output_directory = Path(os.environ.get("HASHMARK_OUTPUT_DIR", "reports/latest"))
    if not output_directory.is_absolute():
        output_directory = project_root / output_directory
    formats = ("json", "markdown", "html") if arguments.format == "all" else (arguments.format,)
    return write_report_bundle(
        report,
        output_directory,
        formats,
        force=arguments.force,
        native_protocol=native_protocol,
    )


def _print_summary(report: dict[str, object], elapsed: float, paths: tuple[Path, ...]) -> None:
    summary = report["summary"]
    print(f"HASHMARK {summary['status']}")
    print(
        f"vectors/backends: {summary['total']}  passed: {summary['passed']}  "
        f"failed: {summary['failed']}  skipped: {summary['skipped']}",
    )
    suites = summary["target_suites"]
    comparisons = summary["differential_comparisons"]
    print(
        f"target suites: {suites['passed']}/{suites['total']}  "
        f"differential: {comparisons['passed']}/{comparisons['total']}",
    )
    for target in report["target_runs"]:
        print(f"{target['backend']:<6} {target['status']}")
    for item in report["results"]:
        if item["status"] != "PASS":
            print(f"{item['status']:<7} {item['backend']:<6} {item['vector_id']}: {item['diagnostic'] or 'mismatch'}")
    print(f"elapsed: {elapsed:.3f}s")
    for path in paths:
        print(f"report: {path}")


def _unavailable_backends(
    selection: RunSelection,
    oracle_digests: dict[str, str],
    error: ToolchainMissingError,
) -> tuple[list[TargetEvidence], list[EvidenceResult]]:
    targets = []
    results = []
    for backend in selection.backends:
        target = unavailable_target(backend, str(error))
        targets.append(target)
        results.extend(skipped_results(selection.fixtures, backend, oracle_digests, str(error)))
    return targets, results


def _failed_backend(
    backend: str,
    fixtures: tuple[Fixture, ...],
    oracle_digests: dict[str, str],
    error: Exception,
    exit_code: int,
) -> BackendOutcome:
    compiler_backend = "sonatina" if backend == "evm" else "native"
    target = TargetEvidence(backend, "FAIL", ("fe", "test", "--backend", compiler_backend), (), str(error))
    results = tuple(skipped_results(fixtures, backend, oracle_digests, str(error)))
    return BackendOutcome(target, results, exit_code)


def _run_evm_backend(
    selection: RunSelection,
    oracle_digests: dict[str, str],
    fe_binary: Path,
    project_root: Path,
    timeout_seconds: int,
) -> BackendOutcome:
    try:
        internal = run_evm_tests(fe_binary, project_root, timeout_seconds, selection.evm_filter)
    except (RunnerTimeoutError, RunnerProcessError) as error:
        return _failed_backend("evm", selection.fixtures, oracle_digests, error, EXIT_EXECUTION)
    target = target_evidence(internal, project_root, fe_binary)
    results = tuple(evm_results(selection.fixtures, oracle_digests, target))
    exit_code = 0 if target.status == "PASS" else EXIT_CONFORMANCE
    return BackendOutcome(target, results, exit_code)


def _run_native_backend(
    selection: RunSelection,
    oracle_digests: dict[str, str],
    fe_binary: Path,
    project_root: Path,
    timeout_seconds: int,
) -> BackendOutcome:
    try:
        internal = run_native(
            fe_binary,
            project_root,
            {item.id for item in selection.fixtures},
            timeout_seconds,
            selection.native_arguments,
        )
    except ToolchainMissingError as error:
        target = unavailable_target("native", str(error))
        results = tuple(skipped_results(selection.fixtures, "native", oracle_digests, str(error)))
        return BackendOutcome(target, results, EXIT_TOOLCHAIN)
    except ConformanceFailureError as error:
        return _failed_backend("native", selection.fixtures, oracle_digests, error, EXIT_CONFORMANCE)
    except (RunnerTimeoutError, RunnerProcessError, ProtocolError) as error:
        return _failed_backend("native", selection.fixtures, oracle_digests, error, EXIT_EXECUTION)
    target = target_evidence(internal.target, project_root, fe_binary)
    results = tuple(native_results(selection.fixtures, oracle_digests, internal.protocol.records))
    has_failure = target.status != "PASS" or any(item.status == "FAIL" for item in results)
    return BackendOutcome(target, results, EXIT_CONFORMANCE if has_failure else 0, internal.raw_stdout)


def execute_run(arguments: argparse.Namespace, project_root: Path) -> int:
    """Execute one validated CLI run and return its process exit code."""

    if not 1 <= arguments.timeout_seconds <= 600:
        return EXIT_ARGUMENT
    started = monotonic()
    fixtures = load_fixtures(arguments.vectors_dir)
    selection = _selection(arguments, fixtures)
    require_python_toolchain()
    oracle_digests = {item.id: digest_hex(item.algorithm, item.input_bytes) for item in selection.fixtures}
    results: list[EvidenceResult] = []
    targets: list[TargetEvidence] = []
    native_protocol: bytes | None = None
    exit_code = 0

    try:
        fe_binary = discover_fe()
        fe_text = require_fe_version(fe_binary, project_root)
    except ToolchainMissingError as error:
        fe_binary = Path("fe")
        fe_text = "unavailable"
        exit_code = EXIT_TOOLCHAIN
        targets, results = _unavailable_backends(selection, oracle_digests, error)
    else:
        if "evm" in selection.backends:
            outcome = _run_evm_backend(selection, oracle_digests, fe_binary, project_root, arguments.timeout_seconds)
            targets.append(outcome.target)
            results.extend(outcome.results)
            exit_code = max(exit_code, outcome.exit_code)
        if "native" in selection.backends:
            outcome = _run_native_backend(selection, oracle_digests, fe_binary, project_root, arguments.timeout_seconds)
            targets.append(outcome.target)
            results.extend(outcome.results)
            native_protocol = outcome.native_protocol
            exit_code = max(exit_code, outcome.exit_code)

    report = build_report(
        results=results,
        target_runs=targets,
        toolchain={"fe": fe_text, "python": platform.python_version(), "pycryptodome": pycryptodome_version()},
        fixture_manifest_hash=fixture_manifest_sha256(arguments.vectors_dir),
        project_root=project_root,
        run_configuration={
            "algorithms": sorted({item.algorithm for item in selection.fixtures}),
            "backends": list(selection.backends),
            "selector": selection.label,
        },
    )
    paths = _report_paths(arguments, report, native_protocol, project_root)
    _print_summary(report, monotonic() - started, paths)
    return exit_code if exit_code else (0 if report["summary"]["status"] == "PASS" else EXIT_CONFORMANCE)
