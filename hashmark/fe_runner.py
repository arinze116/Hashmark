"""Safe Fe compiler discovery and subprocess orchestration."""

from __future__ import annotations

import os
import platform
import re
import shutil
import subprocess
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from time import monotonic

from hashmark.fe_evidence import FeEvidenceDocument, FeEvidenceError, parse_fe_evidence
from hashmark.fixtures import Fixture
from hashmark.protocol import ProtocolError, ProtocolRun, parse_protocol
from hashmark.version import FE_VERSION

FE_VERSION_PATTERN = re.compile(r"^fe (?P<version>\d+\.\d+\.\d+) \([0-9a-f]+\)$")
STDOUT_LIMIT = 32 * 1024
STDERR_LIMIT = 8 * 1024


class FeRunnerError(RuntimeError):
    """Base error for Fe discovery and execution."""


class ToolchainMissingError(FeRunnerError):
    """Raised when the pinned Fe toolchain cannot be used."""


class RunnerTimeoutError(FeRunnerError):
    """Raised when a Fe child process exceeds its deadline."""


class RunnerProcessError(FeRunnerError):
    """Raised when Fe execution fails unexpectedly."""


class ConformanceFailureError(FeRunnerError):
    """Raised when a Fe test process completes with assertion failures."""


@dataclass(frozen=True, slots=True)
class CommandResult:
    """A bounded subprocess result."""

    command: tuple[str, ...]
    returncode: int
    stdout: bytes
    stderr: bytes
    duration_seconds: float


@dataclass(frozen=True, slots=True)
class TargetRun:
    """Aggregate evidence for one Fe backend command."""

    backend: str
    status: str
    command: tuple[str, ...]
    test_identifiers: tuple[str, ...]
    diagnostic: str | None


@dataclass(frozen=True, slots=True)
class NativeRun:
    """A validated native runner invocation."""

    protocol: ProtocolRun
    target: TargetRun
    raw_stdout: bytes
    fe_evidence: FeEvidenceDocument | None = None
    fe_evidence_bytes: bytes | None = None
    fe_report_markdown: bytes | None = None


def discover_fe(explicit: str | None = None) -> Path:
    """Resolve the requested Fe executable without shell interpolation."""

    candidate = explicit or os.environ.get("HASHMARK_FE_BIN") or shutil.which("fe")
    if candidate is None:
        fallback = Path.home() / ".fe" / "bin" / "fe"
        candidate = str(fallback) if fallback.is_file() else None
    if candidate is None:
        raise ToolchainMissingError("Fe 26.6.0 was not found; install it with feup")
    path = Path(candidate).expanduser().resolve()
    if not path.is_file() or not os.access(path, os.X_OK):
        raise ToolchainMissingError(f"Fe executable is not usable: {path}")
    return path


def _bounded_diagnostic(data: bytes) -> str | None:
    if not data:
        return None
    return data[-STDERR_LIMIT:].decode("utf-8", errors="replace")


def run_command(command: Sequence[str], timeout_seconds: int, cwd: Path) -> CommandResult:
    """Run a bounded command with an explicit timeout and no shell."""

    started = monotonic()
    try:
        completed = subprocess.run(
            list(command), cwd=cwd, capture_output=True, timeout=timeout_seconds, check=False,
        )
    except subprocess.TimeoutExpired as error:
        raise RunnerTimeoutError(f"command timed out after {timeout_seconds}s: {command[0]}") from error
    if len(completed.stdout) > STDOUT_LIMIT:
        raise RunnerProcessError("Fe stdout exceeded the 32 KiB safety limit")
    return CommandResult(
        command=tuple(command),
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr[-STDERR_LIMIT:],
        duration_seconds=monotonic() - started,
    )


def require_fe_version(fe_binary: Path, project_root: Path, timeout_seconds: int = 30) -> str:
    """Require the exact compiler version declared by Hashmark."""

    result = run_command([str(fe_binary), "--version"], timeout_seconds, project_root)
    version_text = result.stdout.decode("utf-8", errors="replace").strip()
    match = FE_VERSION_PATTERN.fullmatch(version_text)
    if result.returncode != 0 or match is None:
        raise ToolchainMissingError(f"could not identify Fe compiler: {version_text or 'no output'}")
    detected = match.group("version")
    if detected != FE_VERSION:
        raise ToolchainMissingError(f"Hashmark requires Fe {FE_VERSION}; detected {detected}")
    return version_text


def run_evm_tests(
    fe_binary: Path,
    project_root: Path,
    timeout_seconds: int,
    filter_pattern: str | None = None,
) -> TargetRun:
    """Run the Fe Sonatina backend, exposed to users as the EVM backend."""

    command = [str(fe_binary), "test", "--backend", "sonatina"]
    if filter_pattern is not None:
        command.extend(["--filter", filter_pattern])
    result = run_command(command, timeout_seconds, project_root)
    output = result.stdout.decode("utf-8", errors="replace")
    identifiers = tuple(sorted(set(re.findall(r"^PASS\s+\[[^]]+\]\s+(.+)$", output, re.MULTILINE))))
    if result.returncode != 0 and re.search(r"^FAIL\s+\[[^]]+\]", output, re.MULTILINE) is None:
        raise RunnerProcessError(_bounded_diagnostic(result.stderr) or "EVM Fe tests did not complete")
    status = "PASS" if result.returncode == 0 else "FAIL"
    return TargetRun(
        backend="evm",
        status=status,
        command=tuple(command),
        test_identifiers=identifiers,
        diagnostic=_bounded_diagnostic(result.stderr) if result.returncode else None,
    )


def native_supported_locally() -> bool:
    """Return whether Fe 26.6.0 can emit native executables on this host."""

    machine = platform.machine().lower()
    system = platform.system().lower()
    return (system == "linux" and machine in {"x86_64", "amd64"}) or (
        system == "darwin" and machine in {"arm64", "aarch64"}
    )


def _require_evidence_agreement(document: FeEvidenceDocument, protocol: ProtocolRun) -> None:
    """Require the Fe evidence document and the HASHMARK/1 stream to agree."""

    records = {record.vector_id: record for record in protocol.records}
    if len(records) != len(document.results):
        raise ProtocolError("Fe evidence and native protocol result counts differ")
    for result in document.results:
        record = records.get(result.vector_id)
        if record is None:
            raise ProtocolError(f"Fe evidence result is missing from the native protocol: {result.vector_id}")
        if record.digest_hex != result.fe_digest or record.input_length_bytes != result.input_length_bytes:
            raise ProtocolError(f"Fe evidence and native protocol disagree for {result.vector_id}")
        if (record.status == "pass") != (result.status == "PASS"):
            raise ProtocolError(f"Fe evidence and native protocol statuses disagree for {result.vector_id}")


def _evidence_arguments(mode: str, selector: tuple[str, ...]) -> list[str]:
    if selector == ("--all",):
        return [mode]
    return [mode, *selector]


def run_native(
    fe_binary: Path,
    project_root: Path,
    fixtures: tuple[Fixture, ...],
    timeout_seconds: int,
    selector: tuple[str, ...] = ("--all",),
) -> NativeRun:
    """Build and execute the native runner, then validate every record."""

    if not native_supported_locally():
        raise ToolchainMissingError(
            "Fe 26.6.0 native execution requires x86-64 Linux or AArch64 macOS; "
            "use the x86-64 GitHub Actions job from this AArch64 Linux host",
        )
    test_command = [str(fe_binary), "test", "--backend", "native"]
    test_result = run_command(test_command, timeout_seconds, project_root)
    test_output = test_result.stdout.decode("utf-8", errors="replace")
    if test_result.returncode != 0:
        error_type = (
            ConformanceFailureError
            if re.search(r"^FAIL\s+\[[^]]+\]", test_output, re.MULTILINE)
            else RunnerProcessError
        )
        raise error_type(_bounded_diagnostic(test_result.stderr) or "native Fe tests failed")
    test_identifiers = tuple(sorted(set(re.findall(r"^PASS\s+\[[^]]+\]\s+(.+)$", test_output, re.MULTILINE))))

    out_dir = project_root / "out" / "native"
    build_command = [
        str(fe_binary), "build", "--backend", "native", "--emit", "executable", "--out-dir", str(out_dir),
    ]
    build_result = run_command(build_command, timeout_seconds, project_root)
    if build_result.returncode != 0:
        raise RunnerProcessError(_bounded_diagnostic(build_result.stderr) or "native Fe build failed")
    executable = out_dir / "hashmark"
    if not executable.is_file():
        raise RunnerProcessError(f"native runner was not produced at {executable}")
    runner_command = [str(executable), *selector]
    runner_result = run_command(runner_command, timeout_seconds, project_root)
    protocol = parse_protocol(runner_result.stdout, {item.id for item in fixtures})
    if runner_result.returncode not in {0, 1}:
        raise RunnerProcessError(_bounded_diagnostic(runner_result.stderr) or "native runner crashed")

    evidence_command = [str(executable), *_evidence_arguments("--evidence-json", selector)]
    evidence_result = run_command(evidence_command, timeout_seconds, project_root)
    if evidence_result.returncode not in {0, 1}:
        raise RunnerProcessError(_bounded_diagnostic(evidence_result.stderr) or "Fe evidence run crashed")
    try:
        document = parse_fe_evidence(
            evidence_result.stdout, fixtures, complete_catalogue=selector == ("--all",),
        )
    except FeEvidenceError as error:
        raise ProtocolError(str(error)) from error
    _require_evidence_agreement(document, protocol)
    if (evidence_result.returncode == 0) != (document.summary.status == "PASS"):
        raise RunnerProcessError("Fe evidence exit code disagrees with its summary")

    markdown_command = [str(executable), *_evidence_arguments("--evidence-markdown", selector)]
    markdown_result = run_command(markdown_command, timeout_seconds, project_root)
    if markdown_result.returncode != evidence_result.returncode:
        raise RunnerProcessError("Fe evidence Markdown run disagrees with the JSON run")
    if not markdown_result.stdout.startswith(b"# Hashmark Fe evidence"):
        raise RunnerProcessError("Fe evidence Markdown output is malformed")

    status = (
        "PASS"
        if runner_result.returncode == 0
        and protocol.summary.failed == 0
        and document.summary.status == "PASS"
        else "FAIL"
    )
    return NativeRun(
        protocol=protocol,
        target=TargetRun(
            backend="native",
            status=status,
            command=tuple(runner_command),
            test_identifiers=test_identifiers,
            diagnostic=_bounded_diagnostic(runner_result.stderr),
        ),
        raw_stdout=runner_result.stdout,
        fe_evidence=document,
        fe_evidence_bytes=evidence_result.stdout,
        fe_report_markdown=markdown_result.stdout,
    )
