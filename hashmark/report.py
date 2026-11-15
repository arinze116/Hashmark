"""Deterministic Hashmark report construction and atomic file output."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

from hashmark.models import EvidenceResult, TargetEvidence, result_sort_key
from hashmark.renderers import render_html, render_markdown
from hashmark.schema import validate_report_data
from hashmark.version import PROJECT_NAME, REPORT_SCHEMA_VERSION, __version__

REPORT_FILENAMES = frozenset(
    {"hashmark-report.json", "hashmark-report.md", "index.html", "hashmark-report.sha256", "native-protocol.log"},
)
SOURCE_PATTERNS = (
    ".github/workflows/**/*.yml",
    "hashmark/**/*.py",
    "reports/schema/**/*.json",
    "scripts/**/*.py",
    "src/**/*.fe",
    "tests/**/*.py",
)
SOURCE_FILES = (
    ".coveragerc",
    ".fe-version",
    ".python-version",
    "fe.toml",
    "pyproject.toml",
    "requirements-dev.txt",
    "requirements.txt",
)
LIMITATIONS = (
    "Informal conformance testing only; this is not formal NIST CAVP validation or certification.",
    "Passing vectors are not a security audit, proof of cryptographic security, or exhaustive testing.",
    "Fe 26.6.0 is not production-ready; Hashmark records observed behavior for this pinned compiler.",
    "The Fe EVM test runner exposes test status and identifiers, not per-vector runtime digest output.",
)


class ReportWriteError(OSError):
    """Raised when deterministic report artefacts cannot be written safely."""


def source_revision(project_root: Path) -> str:
    """Return the full Git revision or a deterministic uncommitted marker."""

    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=project_root, capture_output=True, check=False, text=True,
    )
    revision = completed.stdout.strip()
    return revision if completed.returncode == 0 and len(revision) == 40 else "UNCOMMITTED"


def source_tree_sha256(project_root: Path) -> str:
    """Fingerprint executable source, tests, and toolchain declarations."""

    paths = {project_root / name for name in SOURCE_FILES}
    for pattern in SOURCE_PATTERNS:
        paths.update(project_root.glob(pattern))
    state = hashlib.sha256()
    for path in sorted(item for item in paths if item.is_file()):
        relative = path.relative_to(project_root).as_posix().encode("utf-8")
        payload = path.read_bytes()
        state.update(len(relative).to_bytes(4, "big"))
        state.update(relative)
        state.update(len(payload).to_bytes(8, "big"))
        state.update(payload)
    return state.hexdigest()


def portable_command(command: Iterable[str], project_root: Path, fe_binary: Path | None = None) -> tuple[str, ...]:
    """Remove machine-specific absolute paths from a recorded command."""

    root = project_root.resolve()
    fe_path = fe_binary.resolve() if fe_binary is not None else None
    portable: list[str] = []
    for argument in command:
        candidate = Path(argument)
        if fe_path is not None and candidate == fe_path:
            portable.append("fe")
            continue
        if candidate.is_absolute():
            try:
                portable.append((Path(".") / candidate.resolve().relative_to(root)).as_posix())
            except ValueError:
                portable.append(candidate.name)
        else:
            portable.append(argument)
    return tuple(portable)


def _scope_counts(results: tuple[EvidenceResult, ...], field: str) -> dict[str, dict[str, int]]:
    values = sorted({getattr(item.fixture, field) if field == "algorithm" else getattr(item, field) for item in results})
    counts: dict[str, dict[str, int]] = {}
    for value in values:
        scoped = [
            item for item in results
            if (getattr(item.fixture, field) if field == "algorithm" else getattr(item, field)) == value
        ]
        counts[value] = {
            "failed": sum(item.status == "FAIL" for item in scoped),
            "passed": sum(item.status == "PASS" for item in scoped),
            "skipped": sum(item.status == "SKIPPED" for item in scoped),
            "total": len(scoped),
        }
    return counts


def _summary(results: tuple[EvidenceResult, ...], targets: tuple[TargetEvidence, ...]) -> dict[str, Any]:
    passed = sum(item.status == "PASS" for item in results)
    failed = sum(item.status == "FAIL" for item in results)
    skipped = sum(item.status == "SKIPPED" for item in results)
    native_comparisons = [item for item in results if item.fe_digest is not None]
    comparison_passes = sum(item.status == "PASS" for item in native_comparisons)
    overall = "PASS" if failed == skipped == 0 and all(item.status == "PASS" for item in targets) else "FAIL"
    return {
        "by_algorithm": _scope_counts(results, "algorithm"),
        "by_backend": _scope_counts(results, "backend"),
        "differential_comparisons": {
            "passed": comparison_passes,
            "total": len(native_comparisons),
        },
        "failed": failed,
        "passed": passed,
        "skipped": skipped,
        "status": overall,
        "target_suites": {
            "passed": sum(item.status == "PASS" for item in targets),
            "total": len(targets),
        },
        "total": len(results),
    }


def build_report(
    *,
    results: Iterable[EvidenceResult],
    target_runs: Iterable[TargetEvidence],
    toolchain: Mapping[str, str],
    fixture_manifest_hash: str,
    project_root: Path,
    run_configuration: Mapping[str, Any],
) -> dict[str, Any]:
    """Build and validate one canonical report dictionary."""

    ordered_results = tuple(sorted(results, key=result_sort_key))
    ordered_targets = tuple(sorted(target_runs, key=lambda item: item.backend))
    report = {
        "fixture_manifest_sha256": fixture_manifest_hash,
        "limitations": list(LIMITATIONS),
        "project": {"name": PROJECT_NAME, "version": __version__},
        "results": [item.to_dict() for item in ordered_results],
        "run_configuration": dict(run_configuration),
        "schema_version": REPORT_SCHEMA_VERSION,
        "source_revision": source_revision(project_root),
        "source_tree_sha256": source_tree_sha256(project_root),
        "summary": _summary(ordered_results, ordered_targets),
        "target_runs": [item.to_dict() for item in ordered_targets],
        "toolchain": dict(toolchain),
    }
    return validate_report_data(report)


def canonical_json_bytes(report: Mapping[str, Any]) -> bytes:
    """Serialize report data with stable ordering and LF line endings."""

    validate_report_data(report)
    return (json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except OSError as error:
        if "temporary" in locals():
            temporary.unlink(missing_ok=True)
        raise ReportWriteError(f"could not write {path}: {error}") from error


def prepare_output_directory(path: Path, *, force: bool) -> Path:
    """Create a safe output directory without deleting unrelated files."""

    resolved = path.expanduser().resolve()
    resolved.mkdir(parents=True, exist_ok=True)
    entries = [item for item in resolved.iterdir() if item.name not in {".DS_Store"}]
    if not entries:
        return resolved
    unknown = sorted(item.name for item in entries if item.name not in REPORT_FILENAMES)
    if unknown:
        raise ReportWriteError(f"output directory contains unrelated files: {', '.join(unknown)}")
    if not force:
        raise ReportWriteError("output directory is not empty; pass --force to replace Hashmark reports")
    for item in entries:
        if not _is_generated_report_file(item):
            raise ReportWriteError(f"refusing to replace a non-Hashmark file: {item}")
    return resolved


def _is_hashmark_report(path: Path, report_format: str) -> bool:
    """Return whether an existing file is recognizably generated by Hashmark."""

    try:
        if path.stat().st_size > 10 * 1024 * 1024:
            return False
        if report_format == "json":
            value = json.loads(path.read_text(encoding="utf-8"))
            project = value.get("project") if isinstance(value, dict) else None
            return isinstance(project, dict) and project.get("name") == PROJECT_NAME
        prefix = path.read_text(encoding="utf-8")[:4096]
    except (OSError, UnicodeError, json.JSONDecodeError):
        return False
    if report_format == "markdown":
        return prefix.startswith("# Hashmark evidence report — ")
    if report_format == "html":
        has_doctype = prefix.startswith(("<!DOCTYPE html>", "<!doctype html>"))
        return has_doctype and "<title>Hashmark evidence report — " in prefix
    return False


def _is_hashmark_sidecar(path: Path, report_name: str) -> bool:
    try:
        parts = path.read_text(encoding="ascii").strip().split()
    except (OSError, UnicodeError):
        return False
    return (
        len(parts) == 2
        and len(parts[0]) == 64
        and all(character in "0123456789abcdef" for character in parts[0])
        and parts[1] == report_name
    )


def _is_generated_report_file(path: Path) -> bool:
    formats = {
        "hashmark-report.json": "json",
        "hashmark-report.md": "markdown",
        "index.html": "html",
    }
    if path.name in formats:
        return _is_hashmark_report(path, formats[path.name])
    if path.name == "hashmark-report.sha256":
        return _is_hashmark_sidecar(path, "hashmark-report.json")
    if path.name == "native-protocol.log":
        try:
            from hashmark.protocol import parse_protocol

            parse_protocol(path.read_bytes())
        except (OSError, ValueError):
            return False
        return True
    return False


def write_report_bundle(
    report: Mapping[str, Any],
    output_directory: Path,
    formats: Iterable[str],
    *,
    force: bool = False,
    native_protocol: bytes | None = None,
) -> tuple[Path, ...]:
    """Write selected report formats and return their paths."""

    directory = prepare_output_directory(output_directory, force=force)
    selected = frozenset(formats)
    json_payload = canonical_json_bytes(report)
    payloads: dict[str, bytes] = {}
    if "json" in selected:
        payloads["hashmark-report.json"] = json_payload
        digest = hashlib.sha256(json_payload).hexdigest()
        payloads["hashmark-report.sha256"] = f"{digest}  hashmark-report.json\n".encode("ascii")
    if "markdown" in selected:
        payloads["hashmark-report.md"] = render_markdown(report).encode("utf-8")
    if "html" in selected:
        payloads["index.html"] = render_html(report).encode("utf-8")
    if native_protocol is not None:
        payloads["native-protocol.log"] = native_protocol
    if not payloads:
        return ()
    paths: list[Path] = []
    for name in sorted(payloads):
        destination = directory / name
        _atomic_write(destination, payloads[name])
        paths.append(destination)
    return tuple(paths)


def write_report_file(
    report: Mapping[str, Any],
    report_format: str,
    destination: Path,
    *,
    force: bool = False,
) -> tuple[Path, ...]:
    """Write one explicitly named report and its JSON hash sidecar when applicable."""

    path = destination.expanduser().resolve()
    if path.exists():
        if not force:
            raise ReportWriteError(f"output file already exists: {path}; pass --force to replace it")
        if not _is_hashmark_report(path, report_format):
            raise ReportWriteError(f"refusing to replace a non-Hashmark file: {path}")
    sidecar = path.with_suffix(".sha256") if report_format == "json" else None
    if sidecar is not None and sidecar.exists():
        if not force:
            raise ReportWriteError(f"hash sidecar already exists: {sidecar}; pass --force to replace it")
        if not _is_hashmark_sidecar(sidecar, path.name):
            raise ReportWriteError(f"refusing to replace a non-Hashmark sidecar: {sidecar}")
    if report_format == "json":
        payload = canonical_json_bytes(report)
    elif report_format == "markdown":
        payload = render_markdown(report).encode("utf-8")
    elif report_format == "html":
        payload = render_html(report).encode("utf-8")
    else:
        raise ReportWriteError(f"unsupported single report format: {report_format}")
    _atomic_write(path, payload)
    paths = [path]
    if report_format == "json":
        assert sidecar is not None
        digest = hashlib.sha256(payload).hexdigest()
        _atomic_write(sidecar, f"{digest}  {path.name}\n".encode("ascii"))
        paths.append(sidecar)
    return tuple(paths)
