from __future__ import annotations

import io
import json
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from hashmark.cli import main
from hashmark.fe_runner import NativeRun, TargetRun
from hashmark.fixtures import load_fixtures
from hashmark.protocol import NativeRecord, ProtocolRun, ProtocolSummary
from tests.test_cli import PASSING_EVM


class EndToEndTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(__file__).resolve().parent.parent

    def _run_with_mocked_evm(self, arguments: list[str]) -> int:
        with (
            patch("hashmark.workflow.discover_fe", return_value=Path("/tmp/fe")),
            patch("hashmark.workflow.require_fe_version", return_value="fe 26.6.0 (5b3f96a)"),
            patch("hashmark.workflow.run_evm_tests", return_value=PASSING_EVM),
            redirect_stdout(io.StringIO()),
        ):
            return main(arguments)

    def test_controlled_mutation_fails_and_writes_failure_report(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            vectors = base / "vectors"
            output = base / "report"
            shutil.copytree(self.root / "vectors", vectors)
            fixture_path = vectors / "sha256" / "known-answer.json"
            document = json.loads(fixture_path.read_text())
            document["vectors"][1]["expected_digest_hex"] = "00" * 32
            fixture_path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
            code = self._run_with_mocked_evm([
                "run", "--vector", "sha256-abc", "--backend", "evm", "--format", "all",
                "--vectors-dir", str(vectors), "--output-dir", str(output),
            ])
            self.assertEqual(code, 1)
            report = json.loads((output / "hashmark-report.json").read_text())
            self.assertEqual(report["summary"]["status"], "FAIL")
            self.assertEqual(report["results"][0]["status"], "FAIL")
            html = (output / "index.html").read_text()
            self.assertLess(html.index("Failures and skipped evidence"), html.index("SHA-256"))

    def test_two_runs_are_byte_for_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            first = base / "first"
            second = base / "second"
            common = ["run", "--vector", "sha256-abc", "--backend", "evm", "--format", "all"]
            self.assertEqual(self._run_with_mocked_evm(common + ["--output-dir", str(first)]), 0)
            self.assertEqual(self._run_with_mocked_evm(common + ["--output-dir", str(second)]), 0)
            for name in ("hashmark-report.json", "hashmark-report.md", "hashmark-report.sha256", "index.html"):
                self.assertEqual((first / name).read_bytes(), (second / name).read_bytes())

    def test_mocked_all_backend_run_passes_with_native_digests(self) -> None:
        fixtures = load_fixtures(self.root / "vectors")
        records = tuple(
            NativeRecord(
                fixture.id,
                fixture.algorithm,
                fixture.input_length_bytes,
                fixture.expected_digest_hex,
                "native",
                "pass",
            )
            for fixture in fixtures
        )
        native = NativeRun(
            ProtocolRun(records, ProtocolSummary(len(records), len(records), 0)),
            TargetRun("native", "PASS", (str(self.root / "out/native/hashmark"), "--all"), tuple(item.id for item in fixtures), None),
            b"protocol\n",
        )
        with (
            patch("hashmark.workflow.discover_fe", return_value=Path("/tmp/fe")),
            patch("hashmark.workflow.require_fe_version", return_value="fe 26.6.0 (5b3f96a)"),
            patch("hashmark.workflow.run_evm_tests", return_value=PASSING_EVM),
            patch("hashmark.workflow.run_native", return_value=native),
            redirect_stdout(io.StringIO()),
        ):
            code = main(["run", "--all", "--backend", "all", "--format", "terminal"])
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
