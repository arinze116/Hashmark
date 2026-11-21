from __future__ import annotations

import json
import unittest
from pathlib import Path

from hashmark.fe_evidence import (
    STREAMING_CHECK_NAMES,
    FeEvidenceError,
    parse_fe_evidence,
)
from hashmark.fixtures import Fixture, load_fixtures


def _document(fixtures: list[Fixture]) -> dict[str, object]:
    return {
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
                "fe_digest": fixture.expected_digest_hex,
                "input_length_bytes": fixture.input_length_bytes,
                "input_sha256": fixture.input_sha256,
                "status": "PASS",
                "vector_id": fixture.id,
            }
            for fixture in fixtures
        ],
        "streaming_checks": [{"name": name, "status": "PASS"} for name in STREAMING_CHECK_NAMES],
        "summary": {
            "failed": 0,
            "passed": len(fixtures),
            "status": "PASS",
            "streaming_passed": 6,
            "streaming_total": 6,
            "total": len(fixtures),
        },
        "target": "native",
    }


def _encode(document: dict[str, object]) -> bytes:
    return (json.dumps(document, indent=2, sort_keys=True) + "\n").encode("utf-8")


class FeEvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixtures = load_fixtures(Path("vectors"))
        self.document = _document(self.fixtures)

    def _parse(self, document: dict[str, object]):
        return parse_fe_evidence(_encode(document), self.fixtures, complete_catalogue=True)

    def test_valid_document_is_accepted(self) -> None:
        observed = self._parse(self.document)
        self.assertEqual(len(observed.results), 32)
        self.assertEqual(observed.summary.status, "PASS")
        self.assertEqual(observed.summary.streaming_passed, 6)
        self.assertTrue(observed.complete_catalogue)
        self.assertEqual(observed.results[0].fe_digest, observed.results[0].expected_digest)

    def test_truncated_output_is_rejected(self) -> None:
        with self.assertRaisesRegex(FeEvidenceError, "truncated"):
            parse_fe_evidence(_encode(self.document)[:-1], self.fixtures, complete_catalogue=True)

    def test_wrong_protocol_is_rejected(self) -> None:
        self.document["protocol"] = "HASHMARK/2"
        with self.assertRaisesRegex(FeEvidenceError, "protocol"):
            self._parse(self.document)

    def test_wrong_fe_version_is_rejected(self) -> None:
        self.document["fe_version"] = "26.5.0"
        with self.assertRaisesRegex(FeEvidenceError, "requires Fe 26.6.0"):
            self._parse(self.document)

    def test_scope_mismatch_is_rejected(self) -> None:
        with self.assertRaisesRegex(FeEvidenceError, "catalogue scope"):
            parse_fe_evidence(_encode(self.document), self.fixtures, complete_catalogue=False)

    def test_tampered_fe_digest_status_is_rejected(self) -> None:
        self.document["results"][0]["fe_digest"] = "00" * 32
        with self.assertRaisesRegex(FeEvidenceError, "status is inconsistent"):
            self._parse(self.document)

    def test_tampered_expected_digest_is_rejected(self) -> None:
        self.document["results"][0]["expected_digest"] = "00" * 32
        with self.assertRaisesRegex(FeEvidenceError, "expected digest mismatch"):
            self._parse(self.document)

    def test_tampered_input_fingerprint_is_rejected(self) -> None:
        self.document["results"][0]["input_sha256"] = "00" * 32
        with self.assertRaisesRegex(FeEvidenceError, "input fingerprint mismatch"):
            self._parse(self.document)

    def test_unknown_vector_is_rejected(self) -> None:
        self.document["results"][0]["vector_id"] = "sha256-nope"
        with self.assertRaisesRegex(FeEvidenceError, "unknown vector"):
            self._parse(self.document)

    def test_missing_vector_is_rejected(self) -> None:
        self.document["results"] = self.document["results"][:-1]
        with self.assertRaisesRegex(FeEvidenceError, "result count"):
            self._parse(self.document)

    def test_streaming_order_is_enforced(self) -> None:
        checks = self.document["streaming_checks"]
        checks[0], checks[1] = checks[1], checks[0]
        with self.assertRaisesRegex(FeEvidenceError, "streaming check order"):
            self._parse(self.document)

    def test_summary_mismatch_is_rejected(self) -> None:
        self.document["summary"]["passed"] = 0
        with self.assertRaisesRegex(FeEvidenceError, "summary does not match"):
            self._parse(self.document)

    def test_failing_vector_with_consistent_summary_is_accepted(self) -> None:
        result = self.document["results"][0]
        result["fe_digest"] = "00" * 32
        result["status"] = "FAIL"
        self.document["summary"].update(
            {"failed": 1, "passed": len(self.fixtures) - 1, "status": "FAIL"},
        )
        observed = self._parse(self.document)
        self.assertEqual(observed.summary.status, "FAIL")
        self.assertEqual(observed.results[0].status, "FAIL")

    def test_unexpected_top_level_field_is_rejected(self) -> None:
        self.document["extra"] = True
        with self.assertRaisesRegex(FeEvidenceError, "unexpected fields"):
            self._parse(self.document)


if __name__ == "__main__":
    unittest.main()
