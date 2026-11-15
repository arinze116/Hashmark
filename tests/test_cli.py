from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from hashmark.cli import main
from hashmark.fe_runner import (
    ConformanceFailureError,
    RunnerProcessError,
    RunnerTimeoutError,
    TargetRun,
    ToolchainMissingError,
)
from hashmark.oracle import OracleUnavailableError

PASSING_EVM = TargetRun(
    backend="evm",
    status="PASS",
    command=("/tmp/fe", "test", "--backend", "sonatina"),
    test_identifiers=("sha256_known_answers",),
    diagnostic=None,
)


class CliTests(unittest.TestCase):
    def test_help_and_list_succeed(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output), self.assertRaisesRegex(SystemExit, "0"):
            main(["--help"])
        self.assertIn("Verify Fe SHA-256", output.getvalue())
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(["list", "--algorithm", "sha256"]), 0)
        self.assertIn("sha256-abc", output.getvalue())

    def test_validate_vectors_succeeds(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            code = main(["validate-vectors"])
        self.assertEqual(code, 0)
        self.assertIn("VALID: 32 vectors", output.getvalue())

    def test_version_succeeds_for_exact_toolchain(self) -> None:
        with (
            patch("hashmark.cli.discover_fe", return_value=Path("/tmp/fe")),
            patch("hashmark.cli.require_fe_version", return_value="fe 26.6.0 (5b3f96a)"),
            redirect_stdout(io.StringIO()),
        ):
            self.assertEqual(main(["version"]), 0)

    def test_no_command_prints_help(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(main([]), 0)
        self.assertIn("usage:", output.getvalue())

    def test_unknown_vector_exits_two(self) -> None:
        with redirect_stderr(io.StringIO()):
            code = main(["run", "--vector", "not-a-vector", "--backend", "evm", "--format", "terminal"])
        self.assertEqual(code, 2)

    def test_invalid_timeout_exits_two(self) -> None:
        with redirect_stderr(io.StringIO()):
            code = main(["run", "--all", "--timeout-seconds", "0", "--format", "terminal"])
        self.assertEqual(code, 2)

    def test_missing_fe_exits_three_with_partial_summary(self) -> None:
        output = io.StringIO()
        with patch("hashmark.workflow.discover_fe", side_effect=ToolchainMissingError("missing")), redirect_stdout(output):
            code = main(["run", "--vector", "sha256-abc", "--backend", "evm", "--format", "terminal"])
        self.assertEqual(code, 3)
        self.assertIn("UNAVAILABLE", output.getvalue())
        self.assertIn("SKIPPED", output.getvalue())

    def test_timeout_exits_four_with_failure_summary(self) -> None:
        output = io.StringIO()
        with (
            patch("hashmark.workflow.discover_fe", return_value=Path("/tmp/fe")),
            patch("hashmark.workflow.require_fe_version", return_value="fe 26.6.0 (5b3f96a)"),
            patch("hashmark.workflow.run_evm_tests", side_effect=RunnerTimeoutError("timed out")),
            redirect_stdout(output),
        ):
            code = main(["run", "--vector", "sha256-abc", "--backend", "evm", "--format", "terminal"])
        self.assertEqual(code, 4)
        self.assertIn("FAIL", output.getvalue())

    def test_unrelated_output_file_exits_five(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            (output / "owner-file.txt").write_text("preserve")
            with (
                patch("hashmark.workflow.discover_fe", return_value=Path("/tmp/fe")),
                patch("hashmark.workflow.require_fe_version", return_value="fe 26.6.0 (5b3f96a)"),
                patch("hashmark.workflow.run_evm_tests", return_value=PASSING_EVM),
                redirect_stderr(io.StringIO()),
            ):
                code = main([
                    "run", "--vector", "sha256-abc", "--backend", "evm", "--format", "json",
                    "--output-dir", str(output), "--force",
                ])
            self.assertEqual(code, 5)
            self.assertEqual((output / "owner-file.txt").read_text(), "preserve")

    def test_version_fails_when_oracle_is_missing(self) -> None:
        with (
            patch("hashmark.cli.pycryptodome_version", side_effect=OracleUnavailableError("missing")),
            patch("hashmark.cli.discover_fe", return_value=Path("/tmp/fe")),
            patch("hashmark.cli.require_fe_version", return_value="fe 26.6.0 (5b3f96a)"),
            redirect_stdout(io.StringIO()),
        ):
            code = main(["version"])
        self.assertEqual(code, 3)

    def test_version_fails_for_wrong_oracle_version(self) -> None:
        with (
            patch("hashmark.cli.pycryptodome_version", return_value="4.3.0"),
            patch("hashmark.cli.discover_fe", return_value=Path("/tmp/fe")),
            patch("hashmark.cli.require_fe_version", return_value="fe 26.6.0 (5b3f96a)"),
            redirect_stdout(io.StringIO()),
        ):
            code = main(["version"])
        self.assertEqual(code, 3)

    def test_native_conformance_failure_exits_one(self) -> None:
        output = io.StringIO()
        with (
            patch("hashmark.workflow.discover_fe", return_value=Path("/tmp/fe")),
            patch("hashmark.workflow.require_fe_version", return_value="fe 26.6.0 (5b3f96a)"),
            patch("hashmark.workflow.run_native", side_effect=ConformanceFailureError("assertion failed")),
            redirect_stdout(output),
        ):
            code = main(["run", "--vector", "sha256-abc", "--backend", "native", "--format", "terminal"])
        self.assertEqual(code, 1)
        self.assertIn("native FAIL", output.getvalue())

    def test_native_process_failure_exits_four(self) -> None:
        with (
            patch("hashmark.workflow.discover_fe", return_value=Path("/tmp/fe")),
            patch("hashmark.workflow.require_fe_version", return_value="fe 26.6.0 (5b3f96a)"),
            patch("hashmark.workflow.run_native", side_effect=RunnerProcessError("crashed")),
            redirect_stdout(io.StringIO()),
        ):
            code = main(["run", "--vector", "sha256-abc", "--backend", "native", "--format", "terminal"])
        self.assertEqual(code, 4)

    def test_terminal_format_rejects_output_path(self) -> None:
        with (
            patch("hashmark.workflow.discover_fe", return_value=Path("/tmp/fe")),
            patch("hashmark.workflow.require_fe_version", return_value="fe 26.6.0 (5b3f96a)"),
            patch("hashmark.workflow.run_evm_tests", return_value=PASSING_EVM),
            redirect_stderr(io.StringIO()),
        ):
            code = main([
                "run", "--vector", "sha256-abc", "--backend", "evm", "--format", "terminal",
                "--output-dir", "/tmp/not-used",
            ])
        self.assertEqual(code, 5)


if __name__ == "__main__":
    unittest.main()
