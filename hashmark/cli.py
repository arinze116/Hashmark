"""Hashmark command-line interface and exit-code boundary."""

from __future__ import annotations

import argparse
import os
import platform
import sys
from collections.abc import Sequence
from pathlib import Path

from hashmark.exit_codes import (
    EXIT_ARGUMENT,
    EXIT_EXECUTION,
    EXIT_REPORT,
    EXIT_TOOLCHAIN,
)
from hashmark.fe_runner import (
    FeRunnerError,
    RunnerProcessError,
    RunnerTimeoutError,
    ToolchainMissingError,
    discover_fe,
    require_fe_version,
)
from hashmark.fixtures import (
    ALGORITHMS,
    FixtureError,
    fixture_manifest_sha256,
    load_fixtures,
    select_fixtures,
)
from hashmark.oracle import OracleUnavailableError, pycryptodome_version
from hashmark.protocol import ProtocolError
from hashmark.report import ReportWriteError
from hashmark.schema import ReportValidationError
from hashmark.version import (
    PYCRYPTODOME_VERSION,
    PYTHON_VERSION,
    __version__,
)
from hashmark.workflow import execute_run


def _project_root() -> Path:
    """Locate the checked-out Fe project for editable or wheel installs."""

    package_parent = Path(__file__).resolve().parent.parent
    for candidate in (Path.cwd().resolve(), package_parent):
        if (candidate / "fe.toml").is_file() and (candidate / "vectors").is_dir():
            return candidate
    return package_parent


PROJECT_ROOT = _project_root()
DEFAULT_LIMIT_SECONDS = 120


def _environment_timeout() -> int:
    value = os.environ.get("HASHMARK_TIMEOUT_SECONDS")
    if value is None:
        return DEFAULT_LIMIT_SECONDS
    try:
        parsed = int(value)
    except ValueError:
        return DEFAULT_LIMIT_SECONDS
    return parsed if 1 <= parsed <= 600 else DEFAULT_LIMIT_SECONDS


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m hashmark",
        description="Verify Fe SHA-256 and Ethereum Keccak-256 and export reproducible evidence.",
        epilog=(
            "Examples:\n"
            "  python -m hashmark run --all\n"
            "  python -m hashmark run --algorithm sha256 --backend evm\n"
            "  python -m hashmark run --vector sha256-abc --format all --output-dir reports/single"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    commands = parser.add_subparsers(dest="command")
    commands.add_parser("version", help="show Hashmark and toolchain versions")

    list_parser = commands.add_parser("list", help="list algorithms and committed vectors")
    list_parser.add_argument("--algorithm", choices=sorted(ALGORITHMS))
    list_parser.add_argument("--vectors-dir", type=Path, default=PROJECT_ROOT / "vectors")

    validate = commands.add_parser("validate-vectors", help="validate fixtures and provenance")
    validate.add_argument("--vectors-dir", type=Path, default=PROJECT_ROOT / "vectors")

    run = commands.add_parser("run", help="run Fe targets, independent oracles, and reports")
    selector = run.add_mutually_exclusive_group(required=True)
    selector.add_argument("--all", action="store_true", dest="run_all", help="run every vector")
    selector.add_argument("--algorithm", choices=sorted(ALGORITHMS))
    selector.add_argument("--vector", help="run one exact vector ID")
    run.add_argument("--backend", choices=("native", "evm", "all"), default="all")
    run.add_argument("--format", choices=("terminal", "json", "markdown", "html", "all"), default="all")
    output = run.add_mutually_exclusive_group()
    output.add_argument("--output", type=Path, help="explicit path for one JSON, Markdown, or HTML report")
    output.add_argument("--output-dir", type=Path, help="directory for standard report filenames")
    run.add_argument("--vectors-dir", type=Path, default=PROJECT_ROOT / "vectors")
    run.add_argument("--timeout-seconds", type=int, default=_environment_timeout(), metavar="1..600")
    run.add_argument("--force", action="store_true", help="replace only existing Hashmark report files")
    return parser


def _print_error(code: str, message: str) -> None:
    print(f"ERROR {code}: {message}", file=sys.stderr)


def _version_command() -> int:
    has_error = platform.python_version() != PYTHON_VERSION
    print(f"hashmark {__version__}")
    print(f"python {platform.python_version()} (required {PYTHON_VERSION})")
    try:
        oracle_version = pycryptodome_version()
        print(f"pycryptodome {oracle_version} (required {PYCRYPTODOME_VERSION})")
        has_error = has_error or oracle_version != PYCRYPTODOME_VERSION
    except OracleUnavailableError as error:
        print(f"pycryptodome unavailable ({error})")
        has_error = True
    try:
        fe_binary = discover_fe()
        print(require_fe_version(fe_binary, PROJECT_ROOT))
    except ToolchainMissingError as error:
        print(f"fe unavailable ({error})")
        has_error = True
    return EXIT_TOOLCHAIN if has_error else 0


def _list_command(arguments: argparse.Namespace) -> int:
    fixtures = select_fixtures(load_fixtures(arguments.vectors_dir), algorithm=arguments.algorithm)
    print("ALGORITHM   VECTOR ID                       CATEGORY       BYTES")
    for fixture in fixtures:
        print(f"{fixture.algorithm:<11} {fixture.id:<31} {fixture.category:<14} {fixture.input_length_bytes:>6}")
    print(f"\n{len(fixtures)} vector(s)")
    return 0


def _validate_command(arguments: argparse.Namespace) -> int:
    fixtures = load_fixtures(arguments.vectors_dir)
    algorithms = ", ".join(f"{name}={sum(item.algorithm == name for item in fixtures)}" for name in sorted(ALGORITHMS))
    print(f"VALID: {len(fixtures)} vectors ({algorithms})")
    print(f"fixture manifest sha256: {fixture_manifest_sha256(arguments.vectors_dir)}")
    return 0


def _run_command(arguments: argparse.Namespace) -> int:
    if not 1 <= arguments.timeout_seconds <= 600:
        _print_error("INVALID_ARGUMENT", "--timeout-seconds must be between 1 and 600")
        return EXIT_ARGUMENT
    try:
        return execute_run(arguments, PROJECT_ROOT)
    except FixtureError as error:
        _print_error("INVALID_FIXTURE", str(error))
        return EXIT_ARGUMENT
    except (OracleUnavailableError, ToolchainMissingError) as error:
        _print_error("TOOLCHAIN_MISSING", str(error))
        return EXIT_TOOLCHAIN
    except RunnerTimeoutError as error:
        _print_error("RUNNER_TIMEOUT", str(error))
        return EXIT_EXECUTION
    except (RunnerProcessError, ProtocolError, FeRunnerError) as error:
        _print_error("RUNNER_FAILED", str(error))
        return EXIT_EXECUTION
    except (ReportWriteError, ReportValidationError, OSError, ValueError) as error:
        _print_error("REPORT_WRITE_FAILED", str(error))
        return EXIT_REPORT


def main(argv: Sequence[str] | None = None) -> int:
    """Run the Hashmark command-line interface."""

    parser = _parser()
    arguments = parser.parse_args(argv)
    if arguments.command is None:
        parser.print_help()
        return 0
    try:
        if arguments.command == "version":
            return _version_command()
        if arguments.command == "list":
            return _list_command(arguments)
        if arguments.command == "validate-vectors":
            return _validate_command(arguments)
        return _run_command(arguments)
    except FixtureError as error:
        _print_error("INVALID_FIXTURE", str(error))
        return EXIT_ARGUMENT
