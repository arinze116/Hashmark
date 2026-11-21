from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from hashmark.fe_evidence import STREAMING_CHECK_NAMES
from hashmark.fe_runner import (
    CommandResult,
    ConformanceFailureError,
    RunnerProcessError,
    RunnerTimeoutError,
    ToolchainMissingError,
    discover_fe,
    native_supported_locally,
    require_fe_version,
    run_command,
    run_evm_tests,
    run_native,
)
from hashmark.fixtures import Fixture, load_fixtures
from hashmark.protocol import ProtocolError


def _abc_fixture() -> Fixture:
    return next(item for item in load_fixtures(Path("vectors")) if item.id == "sha256-abc")


def _fe_evidence_bytes(fixture: Fixture, fe_digest: str | None = None) -> bytes:
    digest = fe_digest if fe_digest is not None else fixture.expected_digest_hex
    document = {
        "backend": "native",
        "complete_catalogue": True,
        "engine": "fe",
        "fe_version": "26.6.0",
        "project": "Hashmark",
        "protocol": "HASHMARK/FE-EVIDENCE/1",
        "results": [
            {
                "algorithm": fixture.algorithm,
                "category": fixture.category,
                "expected_digest": fixture.expected_digest_hex,
                "fe_digest": digest,
                "input_length_bytes": fixture.input_length_bytes,
                "input_sha256": fixture.input_sha256,
                "status": "PASS" if digest == fixture.expected_digest_hex else "FAIL",
                "vector_id": fixture.id,
            },
        ],
        "streaming_checks": [{"name": name, "status": "PASS"} for name in STREAMING_CHECK_NAMES],
        "summary": {
            "failed": 0 if digest == fixture.expected_digest_hex else 1,
            "passed": 1 if digest == fixture.expected_digest_hex else 0,
            "status": "PASS" if digest == fixture.expected_digest_hex else "FAIL",
            "streaming_passed": 6,
            "streaming_total": 6,
            "total": 1,
        },
        "target": "native",
    }
    return (json.dumps(document, indent=2, sort_keys=True) + "\n").encode("utf-8")


class FeRunnerTests(unittest.TestCase):
    def test_exact_version_is_accepted(self) -> None:
        result = CommandResult(("fe", "--version"), 0, b"fe 26.6.0 (5b3f96a)\n", b"", 0.1)
        with tempfile.TemporaryDirectory() as temporary, patch(
            "hashmark.fe_runner.run_command", return_value=result,
        ):
            observed = require_fe_version(Path("/tmp/fe"), Path(temporary))
        self.assertEqual(observed, "fe 26.6.0 (5b3f96a)")

    def test_wrong_version_is_rejected(self) -> None:
        result = CommandResult(("fe", "--version"), 0, b"fe 26.5.0 (abc1234)\n", b"", 0.1)
        with tempfile.TemporaryDirectory() as temporary, patch(
            "hashmark.fe_runner.run_command", return_value=result,
        ), self.assertRaisesRegex(ToolchainMissingError, "requires Fe 26.6.0"):
            require_fe_version(Path("/tmp/fe"), Path(temporary))

    def test_supported_native_platforms(self) -> None:
        with patch("hashmark.fe_runner.platform.system", return_value="Linux"), patch(
            "hashmark.fe_runner.platform.machine", return_value="x86_64",
        ):
            self.assertTrue(native_supported_locally())

    def test_unsupported_native_platforms(self) -> None:
        with patch("hashmark.fe_runner.platform.system", return_value="Linux"), patch(
            "hashmark.fe_runner.platform.machine", return_value="aarch64",
        ):
            self.assertFalse(native_supported_locally())
        with patch("hashmark.fe_runner.platform.system", return_value="Darwin"), patch(
            "hashmark.fe_runner.platform.machine", return_value="x86_64",
        ):
            self.assertFalse(native_supported_locally())
        with patch("hashmark.fe_runner.platform.system", return_value="Darwin"), patch(
            "hashmark.fe_runner.platform.machine", return_value="arm64",
        ):
            self.assertTrue(native_supported_locally())

    def test_discover_fe_rejects_missing_explicit_path(self) -> None:
        with self.assertRaisesRegex(ToolchainMissingError, "not usable"):
            discover_fe("/definitely/not/fe")

    def test_discover_fe_accepts_executable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            executable = Path(temporary) / "fe"
            executable.write_text("#!/bin/sh\nexit 0\n")
            executable.chmod(0o700)
            self.assertEqual(discover_fe(str(executable)), executable.resolve())

    def test_run_command_captures_success(self) -> None:
        result = run_command([sys.executable, "-c", "print('ok')"], 5, Path.cwd())
        self.assertEqual((result.returncode, result.stdout), (0, b"ok\n"))

    def test_run_command_times_out(self) -> None:
        with self.assertRaises(RunnerTimeoutError):
            run_command([sys.executable, "-c", "import time; time.sleep(1)"], 0.01, Path.cwd())

    def test_run_command_rejects_oversized_stdout(self) -> None:
        with self.assertRaisesRegex(RunnerProcessError, "32 KiB"):
            run_command([sys.executable, "-c", "print('x' * 40000)"], 5, Path.cwd())

    def test_unidentifiable_version_is_rejected(self) -> None:
        result = CommandResult(("fe", "--version"), 1, b"", b"bad", 0.1)
        with tempfile.TemporaryDirectory() as temporary, patch(
            "hashmark.fe_runner.run_command", return_value=result,
        ), self.assertRaisesRegex(ToolchainMissingError, "could not identify"):
            require_fe_version(Path("/tmp/fe"), Path(temporary))

    def test_evm_pass_collects_identifiers(self) -> None:
        result = CommandResult(("fe", "test"), 0, b"PASS  [0.1s] suite_b\nPASS  [0.1s] suite_a\n", b"", 0.1)
        with patch("hashmark.fe_runner.run_command", return_value=result):
            observed = run_evm_tests(Path("/tmp/fe"), Path.cwd(), 10, "sha256")
        self.assertEqual(observed.test_identifiers, ("suite_a", "suite_b"))

    def test_evm_assertion_failure_is_conformance_status(self) -> None:
        result = CommandResult(("fe", "test"), 1, b"FAIL  [0.1s] suite\n", b"assertion", 0.1)
        with patch("hashmark.fe_runner.run_command", return_value=result):
            observed = run_evm_tests(Path("/tmp/fe"), Path.cwd(), 10)
        self.assertEqual(observed.status, "FAIL")

    def test_evm_process_failure_is_rejected(self) -> None:
        result = CommandResult(("fe", "test"), 1, b"", b"compile failed", 0.1)
        with patch(
            "hashmark.fe_runner.run_command", return_value=result,
        ), self.assertRaisesRegex(RunnerProcessError, "compile failed"):
            run_evm_tests(Path("/tmp/fe"), Path.cwd(), 10)

    def test_native_build_and_protocol_success(self) -> None:
        fixture = _abc_fixture()
        record = (
            b"HASHMARK/1\tsha256-abc\tsha256\t3\t"
            b"ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad\tnative\tpass\n"
            b"HASHMARK/1\tSUMMARY\t1\t1\t0\n"
        )
        success = CommandResult(("fe",), 0, b"", b"", 0.1)
        runner = CommandResult(("hashmark",), 0, record, b"", 0.1)
        evidence = CommandResult(("hashmark",), 0, _fe_evidence_bytes(fixture), b"", 0.1)
        markdown = CommandResult(("hashmark",), 0, "# Hashmark Fe evidence — native\n".encode("utf-8"), b"", 0.1)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            executable = root / "out" / "native" / "hashmark"
            executable.parent.mkdir(parents=True)
            executable.write_bytes(b"binary")
            with patch("hashmark.fe_runner.native_supported_locally", return_value=True), patch(
                "hashmark.fe_runner.run_command",
                side_effect=(success, success, runner, evidence, markdown),
            ):
                observed = run_native(Path("/tmp/fe"), root, (fixture,), 10)
        self.assertEqual(observed.protocol.summary.passed, 1)
        self.assertIsNotNone(observed.fe_evidence)
        self.assertEqual(observed.fe_evidence.summary.status, "PASS")
        self.assertEqual(observed.fe_evidence_bytes, evidence.stdout)
        self.assertEqual(observed.fe_report_markdown, markdown.stdout)
        self.assertEqual(observed.target.status, "PASS")

    def test_native_evidence_disagreement_is_rejected(self) -> None:
        fixture = _abc_fixture()
        record = (
            b"HASHMARK/1\tsha256-abc\tsha256\t3\t"
            b"ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad\tnative\tpass\n"
            b"HASHMARK/1\tSUMMARY\t1\t1\t0\n"
        )
        success = CommandResult(("fe",), 0, b"", b"", 0.1)
        runner = CommandResult(("hashmark",), 0, record, b"", 0.1)
        evidence = CommandResult(("hashmark",), 1, _fe_evidence_bytes(fixture, "00" * 32), b"", 0.1)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            executable = root / "out" / "native" / "hashmark"
            executable.parent.mkdir(parents=True)
            executable.write_bytes(b"binary")
            with patch("hashmark.fe_runner.native_supported_locally", return_value=True), patch(
                "hashmark.fe_runner.run_command", side_effect=(success, success, runner, evidence),
            ), self.assertRaisesRegex(ProtocolError, "disagree"):
                run_native(Path("/tmp/fe"), root, (fixture,), 10)

    def test_native_test_assertion_failure_is_distinct(self) -> None:
        failed = CommandResult(("fe",), 1, b"FAIL  [0.1s] suite\n", b"", 0.1)
        with tempfile.TemporaryDirectory() as temporary, patch(
            "hashmark.fe_runner.native_supported_locally", return_value=True,
        ), patch(
            "hashmark.fe_runner.run_command", return_value=failed,
        ), self.assertRaises(ConformanceFailureError):
            run_native(Path("/tmp/fe"), Path(temporary), (_abc_fixture(),), 10)

    def test_native_build_failure_is_rejected(self) -> None:
        success = CommandResult(("fe",), 0, b"", b"", 0.1)
        failed = CommandResult(("fe",), 1, b"", b"link failed", 0.1)
        with tempfile.TemporaryDirectory() as temporary, patch(
            "hashmark.fe_runner.native_supported_locally", return_value=True,
        ), patch(
            "hashmark.fe_runner.run_command", side_effect=(success, failed),
        ), self.assertRaisesRegex(RunnerProcessError, "link failed"):
            run_native(Path("/tmp/fe"), Path(temporary), (_abc_fixture(),), 10)


if __name__ == "__main__":
    unittest.main()
