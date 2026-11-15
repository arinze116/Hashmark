from __future__ import annotations

import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from hashmark.fixtures import (
    FixtureError,
    fixture_manifest_sha256,
    load_fixtures,
    select_fixtures,
)
from hashmark.oracle import digest_hex


class FixtureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = {
            "schema_version": 1,
            "id": "sha256-test",
            "algorithm": "sha256",
            "category": "known_answer",
            "input_hex": "616263",
            "expected_digest_hex": digest_hex("sha256", b"abc"),
            "input_length_bytes": 3,
            "source_name": "NIST",
            "source_url": "https://example.com/vector",
            "source_document": "Example",
            "source_case_id": "abc",
            "licence_or_usage_note": "Reference data",
            "notes": None,
        }

    def _write(self, root: Path, records: list[dict[str, object]]) -> None:
        directory = root / "sha256"
        directory.mkdir(parents=True)
        payload = {"schema_version": 1, "vectors": records}
        (directory / "vectors.json").write_text(json.dumps(payload), encoding="utf-8")

    def test_committed_fixtures_match_oracles(self) -> None:
        fixtures = load_fixtures(Path("vectors"))
        self.assertEqual(len(fixtures), 32)
        for fixture in fixtures:
            self.assertEqual(
                digest_hex(fixture.algorithm, fixture.input_bytes),
                fixture.expected_digest_hex,
            )

    def test_manifest_hash_is_stable(self) -> None:
        first = fixture_manifest_sha256(Path("vectors"))
        second = fixture_manifest_sha256(Path("vectors"))
        self.assertEqual(first, second)

    def test_duplicate_id_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write(root, [self.fixture, deepcopy(self.fixture)])
            with self.assertRaisesRegex(FixtureError, "duplicate fixture id"):
                load_fixtures(root)

    def test_invalid_hex_is_rejected(self) -> None:
        invalid = deepcopy(self.fixture)
        invalid["input_hex"] = "xyz"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write(root, [invalid])
            with self.assertRaisesRegex(FixtureError, "even-length hexadecimal"):
                load_fixtures(root)

    def test_odd_length_hex_is_rejected(self) -> None:
        invalid = deepcopy(self.fixture)
        invalid["input_hex"] = "0"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write(root, [invalid])
            with self.assertRaisesRegex(FixtureError, "even-length hexadecimal"):
                load_fixtures(root)

    def test_wrong_digest_size_is_rejected(self) -> None:
        invalid = deepcopy(self.fixture)
        invalid["expected_digest_hex"] = "00" * 31
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write(root, [invalid])
            with self.assertRaisesRegex(FixtureError, "exactly 32 bytes"):
                load_fixtures(root)

    def test_oversized_digest_is_rejected(self) -> None:
        invalid = deepcopy(self.fixture)
        invalid["expected_digest_hex"] = "00" * 33
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write(root, [invalid])
            with self.assertRaisesRegex(FixtureError, "exactly 32 bytes"):
                load_fixtures(root)

    def test_unsupported_algorithm_is_rejected(self) -> None:
        invalid = deepcopy(self.fixture)
        invalid["algorithm"] = "sha3"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write(root, [invalid])
            with self.assertRaisesRegex(FixtureError, "unsupported algorithm"):
                load_fixtures(root)

    def test_wrong_length_is_rejected(self) -> None:
        invalid = deepcopy(self.fixture)
        invalid["input_length_bytes"] = 4
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write(root, [invalid])
            with self.assertRaisesRegex(FixtureError, "input length"):
                load_fixtures(root)

    def test_non_https_provenance_is_rejected(self) -> None:
        invalid = deepcopy(self.fixture)
        invalid["source_url"] = "http://example.com/vector"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write(root, [invalid])
            with self.assertRaisesRegex(FixtureError, "HTTPS"):
                load_fixtures(root)

    def test_missing_field_is_rejected(self) -> None:
        invalid = deepcopy(self.fixture)
        del invalid["source_name"]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write(root, [invalid])
            with self.assertRaisesRegex(FixtureError, "missing fields"):
                load_fixtures(root)

    def test_unknown_field_is_rejected(self) -> None:
        invalid = deepcopy(self.fixture)
        invalid["extra"] = True
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write(root, [invalid])
            with self.assertRaisesRegex(FixtureError, "unknown fields"):
                load_fixtures(root)

    def test_uppercase_expected_digest_is_rejected(self) -> None:
        invalid = deepcopy(self.fixture)
        invalid["expected_digest_hex"] = str(invalid["expected_digest_hex"]).upper()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write(root, [invalid])
            with self.assertRaisesRegex(FixtureError, "lowercase"):
                load_fixtures(root)

    def test_invalid_notes_are_rejected(self) -> None:
        invalid = deepcopy(self.fixture)
        invalid["notes"] = 42
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write(root, [invalid])
            with self.assertRaisesRegex(FixtureError, "notes"):
                load_fixtures(root)

    def test_empty_fixture_root_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary, self.assertRaisesRegex(
            FixtureError, "no fixture files",
        ):
            load_fixtures(Path(temporary))

    def test_misplaced_fixture_is_rejected(self) -> None:
        invalid = deepcopy(self.fixture)
        invalid["algorithm"] = "keccak256"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write(root, [invalid])
            with self.assertRaisesRegex(FixtureError, "wrong algorithm directory"):
                load_fixtures(root)

    def test_selection_rejects_empty_and_unknown_values(self) -> None:
        fixtures = load_fixtures(Path("vectors"))
        with self.assertRaisesRegex(FixtureError, "unsupported algorithm"):
            select_fixtures(fixtures, algorithm="sha3")
        with self.assertRaisesRegex(FixtureError, "unknown vector"):
            select_fixtures(fixtures, vector_id="missing")


if __name__ == "__main__":
    unittest.main()
