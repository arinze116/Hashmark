from __future__ import annotations

import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from hashmark.fixtures import fixture_manifest_sha256, load_fixtures
from hashmark.models import EvidenceResult, TargetEvidence
from hashmark.oracle import digest_hex
from hashmark.renderers import render_html, render_markdown
from hashmark.report import (
    ReportWriteError,
    build_report,
    canonical_json_bytes,
    portable_command,
    prepare_output_directory,
    source_revision,
    source_tree_sha256,
    write_report_bundle,
    write_report_file,
)
from hashmark.schema import ReportValidationError, validate_report_data


class ReportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(__file__).resolve().parent.parent
        self.fixture = next(item for item in load_fixtures(self.root / "vectors") if item.id == "sha256-abc")
        self.target = TargetEvidence("evm", "PASS", ("fe", "test"), ("sha256_known_answers",))

    def _report(self, *results: EvidenceResult) -> dict[str, object]:
        return build_report(
            results=results,
            target_runs=(self.target,),
            toolchain={"fe": "fe 26.6.0 (5b3f96a)", "python": "3.15.2", "pycryptodome": "4.4.0"},
            fixture_manifest_hash=fixture_manifest_sha256(self.root / "vectors"),
            project_root=self.root,
            run_configuration={"algorithms": ["sha256"], "backends": ["evm"], "selector": "sha256-abc"},
        )

    def _result(self, status: str = "PASS", fixture=None) -> EvidenceResult:
        selected = fixture or self.fixture
        oracle = digest_hex(selected.algorithm, selected.input_bytes)
        return EvidenceResult(selected, "evm", None, oracle, status, "evm_test_status")

    def test_canonical_json_is_deterministic(self) -> None:
        report = self._report(self._result())
        self.assertEqual(canonical_json_bytes(report), canonical_json_bytes(report))

    def test_summary_mismatch_is_rejected(self) -> None:
        report = self._report(self._result())
        report["summary"]["passed"] = 0
        with self.assertRaisesRegex(ReportValidationError, "summary"):
            validate_report_data(report)

    def test_unknown_top_level_field_is_rejected(self) -> None:
        report = self._report(self._result())
        report["unknown"] = True
        with self.assertRaisesRegex(ReportValidationError, "fields mismatch"):
            validate_report_data(report)

    def test_invalid_digest_and_source_url_are_rejected(self) -> None:
        report = self._report(self._result())
        report["results"][0]["input_sha256"] = "bad"
        with self.assertRaisesRegex(ReportValidationError, "input_sha256"):
            validate_report_data(report)
        report = self._report(self._result())
        report["results"][0]["source_url"] = "javascript:alert(1)"
        with self.assertRaisesRegex(ReportValidationError, "HTTPS"):
            validate_report_data(report)

    def test_passing_digest_mismatch_is_rejected(self) -> None:
        report = self._report(self._result())
        report["results"][0]["oracle_digest"] = "00" * 32
        with self.assertRaisesRegex(ReportValidationError, "oracle mismatch"):
            validate_report_data(report)

    def test_invalid_target_is_rejected(self) -> None:
        report = self._report(self._result())
        report["target_runs"][0]["backend"] = "wasm"
        with self.assertRaisesRegex(ReportValidationError, "target run"):
            validate_report_data(report)

    def test_inconsistent_overall_status_is_rejected(self) -> None:
        report = self._report(self._result())
        report["summary"]["status"] = "FAIL"
        with self.assertRaisesRegex(ReportValidationError, "overall status"):
            validate_report_data(report)

    def test_invalid_nested_metadata_is_rejected(self) -> None:
        mutations = (
            ("project", lambda report: report.__setitem__("project", {"name": "Hashmark"})),
            ("toolchain", lambda report: report.__setitem__("toolchain", {"fe": "26.6.0"})),
            ("configuration fields", lambda report: report["run_configuration"].__setitem__("extra", True)),
            ("algorithms", lambda report: report["run_configuration"].__setitem__("algorithms", ["sha3"])),
            ("backends", lambda report: report["run_configuration"].__setitem__("backends", ["wasm"])),
            ("selector", lambda report: report["run_configuration"].__setitem__("selector", "")),
        )
        for message, mutate in mutations:
            with self.subTest(message=message):
                report = self._report(self._result())
                mutate(report)
                with self.assertRaisesRegex(ReportValidationError, message):
                    validate_report_data(report)

    def test_invalid_target_fields_are_rejected(self) -> None:
        for field, value, message in (
            ("command", [1], "command"),
            ("test_identifiers", [1], "identifiers"),
            ("diagnostic", 42, "diagnostic"),
        ):
            with self.subTest(field=field):
                report = self._report(self._result())
                report["target_runs"][0][field] = value
                with self.assertRaisesRegex(ReportValidationError, message):
                    validate_report_data(report)

    def test_inconsistent_evidence_basis_is_rejected(self) -> None:
        report = self._report(self._result())
        report["results"][0]["evidence_basis"] = "native_digest"
        with self.assertRaisesRegex(ReportValidationError, "native digest"):
            validate_report_data(report)
        report = self._report(self._result())
        report["results"][0]["evidence_basis"] = "unavailable"
        with self.assertRaisesRegex(ReportValidationError, "must be skipped"):
            validate_report_data(report)

    def test_empty_results_are_rejected(self) -> None:
        report = self._report(self._result())
        report["results"] = []
        with self.assertRaisesRegex(ReportValidationError, "non-empty"):
            validate_report_data(report)

    def test_html_escapes_fixture_text_and_has_no_script(self) -> None:
        unsafe = replace(self.fixture, notes="<script>alert(1)</script>", source_name="NIST <unsafe>")
        output = render_html(self._report(self._result(fixture=unsafe)))
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", output)
        self.assertIn("NIST &lt;unsafe&gt;", output)
        self.assertNotIn("<script", output)
        self.assertIn('<span class="sr-only">PASS sha256-abc; sha256; known_answer; 3 bytes; evm backend</span>', output)

    def test_failure_appears_before_success(self) -> None:
        failed_fixture = replace(self.fixture, id="sha256-a-failure")
        passed_fixture = replace(self.fixture, id="sha256-z-pass")
        report = self._report(self._result("FAIL", failed_fixture), self._result("PASS", passed_fixture))
        markdown = render_markdown(report)
        html = render_html(report)
        self.assertLess(markdown.index("sha256-a-failure"), markdown.index("sha256-z-pass"))
        self.assertLess(html.index("sha256-a-failure"), html.index("sha256-z-pass"))

    def test_report_bundle_and_sidecar_match(self) -> None:
        report = self._report(self._result())
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            paths = write_report_bundle(report, output, ("json", "markdown", "html"))
            self.assertEqual(len(paths), 4)
            validate_report_data(json.loads((output / "hashmark-report.json").read_text()))
            sidecar_hash = (output / "hashmark-report.sha256").read_text().split()[0]
            import hashlib
            self.assertEqual(sidecar_hash, hashlib.sha256((output / "hashmark-report.json").read_bytes()).hexdigest())

    def test_unrelated_output_directory_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            (output / "owner.txt").write_text("preserve")
            with self.assertRaisesRegex(ReportWriteError, "unrelated"):
                prepare_output_directory(output, force=True)

    def test_nonempty_report_directory_requires_force(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            report = self._report(self._result())
            write_report_bundle(report, output, ("html",))
            with self.assertRaisesRegex(ReportWriteError, "--force"):
                prepare_output_directory(output, force=False)
            self.assertEqual(prepare_output_directory(output, force=True), output.resolve())

    def test_known_filename_with_unrelated_content_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            (output / "index.html").write_text("owner data")
            with self.assertRaisesRegex(ReportWriteError, "non-Hashmark"):
                prepare_output_directory(output, force=True)

    def test_single_report_formats_and_force(self) -> None:
        report = self._report(self._result())
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            markdown = output / "evidence.md"
            html = output / "evidence.html"
            json_path = output / "evidence.json"
            self.assertEqual(len(write_report_file(report, "markdown", markdown)), 1)
            self.assertEqual(len(write_report_file(report, "html", html)), 1)
            self.assertEqual(len(write_report_file(report, "json", json_path)), 2)
            with self.assertRaisesRegex(ReportWriteError, "already exists"):
                write_report_file(report, "markdown", markdown)
            write_report_file(report, "markdown", markdown, force=True)

    def test_unsupported_single_format_is_rejected(self) -> None:
        report = self._report(self._result())
        with tempfile.TemporaryDirectory() as temporary, self.assertRaisesRegex(
            ReportWriteError, "unsupported",
        ):
            write_report_file(report, "xml", Path(temporary) / "report.xml")

    def test_force_refuses_unrelated_single_file(self) -> None:
        report = self._report(self._result())
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "evidence.md"
            destination.write_text("owner data")
            with self.assertRaisesRegex(ReportWriteError, "non-Hashmark"):
                write_report_file(report, "markdown", destination, force=True)

    def test_force_accepts_complete_generated_bundle(self) -> None:
        report = self._report(self._result())
        protocol = (
            b"HASHMARK/1\tsha256-abc\tsha256\t3\t"
            b"ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad\tnative\tpass\n"
            b"HASHMARK/1\tSUMMARY\t1\t1\t0\n"
        )
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            write_report_bundle(report, output, ("json", "markdown", "html"), native_protocol=protocol)
            self.assertEqual(prepare_output_directory(output, force=True), output.resolve())

    def test_bundle_includes_fe_evidence_and_allows_force(self) -> None:
        report = self._report(self._result())
        fe_evidence = (
            b'{\n  "project": "Hashmark",\n  "protocol": "HASHMARK/FE-EVIDENCE/1"\n}\n'
        )
        fe_markdown = "# Hashmark Fe evidence — native\n".encode("utf-8")
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            paths = write_report_bundle(
                report,
                output,
                ("json", "markdown", "html"),
                fe_evidence=fe_evidence,
                fe_report_markdown=fe_markdown,
            )
            names = {path.name for path in paths}
            self.assertIn("fe-evidence.json", names)
            self.assertIn("fe-report.md", names)
            self.assertEqual((output / "fe-evidence.json").read_bytes(), fe_evidence)
            self.assertEqual((output / "fe-report.md").read_bytes(), fe_markdown)
            self.assertEqual(prepare_output_directory(output, force=True), output.resolve())

    def test_inconsistent_derived_summaries_are_rejected(self) -> None:
        report = self._report(self._result())
        report["summary"]["target_suites"]["passed"] = 0
        with self.assertRaisesRegex(ReportValidationError, "target suite"):
            validate_report_data(report)
        report = self._report(self._result())
        report["summary"]["differential_comparisons"]["total"] = 1
        with self.assertRaisesRegex(ReportValidationError, "differential"):
            validate_report_data(report)

    def test_portable_command_strips_machine_paths(self) -> None:
        command = portable_command((str(self.root / "out" / "native" / "hashmark"), "--all"), self.root)
        self.assertEqual(command, ("out/native/hashmark", "--all"))

    def test_source_metadata_is_stable(self) -> None:
        self.assertEqual(len(source_tree_sha256(self.root)), 64)
        self.assertTrue(source_revision(self.root))

    def test_source_revision_falls_back_when_git_is_unavailable(self) -> None:
        with patch("hashmark.report.subprocess.run", side_effect=FileNotFoundError):
            self.assertEqual(source_revision(self.root), "UNCOMMITTED")


if __name__ == "__main__":
    unittest.main()
