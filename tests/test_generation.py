from __future__ import annotations

import unittest
from pathlib import Path

from hashmark.fixtures import load_fixtures
from scripts.generate_fe_vectors import (
    _constant_name,
    generate_constants,
    generate_engine,
    generate_runner,
)


class GenerationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixtures = load_fixtures(Path("vectors"))

    def test_native_runner_reuses_generated_digest_constants(self) -> None:
        constants = generate_constants(self.fixtures)
        runner = generate_runner(self.fixtures)
        for fixture in self.fixtures:
            name = _constant_name(fixture.id)
            self.assertIn(f"pub const {name}: u256 = 0x{fixture.expected_digest_hex}", constants)
            self.assertIn(f"generated_vectors::{name}", runner)
            self.assertNotIn(f"0x{fixture.expected_digest_hex}", runner)

    def test_each_digest_literal_has_one_generated_fe_definition(self) -> None:
        constants = generate_constants(self.fixtures)
        for fixture in self.fixtures:
            self.assertEqual(constants.count(f"0x{fixture.expected_digest_hex}"), 1)

    def test_native_runner_exposes_streaming_self_test(self) -> None:
        runner = generate_runner(self.fixtures)
        self.assertIn('args.get(1) == "--self-test"', runner)
        self.assertIn("conformance::streaming_suite()", runner)

    def test_native_runner_dispatches_evidence_modes(self) -> None:
        runner = generate_runner(self.fixtures)
        self.assertIn('"--evidence-json"', runner)
        self.assertIn('"--evidence-markdown"', runner)
        self.assertIn("engine::run_evidence_json(", runner)
        self.assertIn("engine::run_evidence_markdown(", runner)

    def test_engine_covers_every_fixture_by_constant(self) -> None:
        engine = generate_engine(self.fixtures)
        self.assertIn("pub fn run_evidence_json(", engine)
        self.assertIn("pub fn run_evidence_markdown(", engine)
        self.assertIn("evidence_render::json_vector(", engine)
        self.assertIn("evidence_render::markdown_vector(", engine)
        for fixture in self.fixtures:
            self.assertIn(f'"{fixture.id}"', engine)
            self.assertIn(f"generated_vectors::{_constant_name(fixture.id)}", engine)
            self.assertNotIn(f"0x{fixture.expected_digest_hex}", engine)

    def test_engine_runs_all_streaming_checks(self) -> None:
        engine = generate_engine(self.fixtures)
        for name in (
            "sha256_streaming_matches_one_shot",
            "keccak256_streaming_matches_one_shot",
            "sha256_uneven_partition_matches_one_shot",
            "keccak256_uneven_partition_matches_one_shot",
            "sha256_two_part_splits_match_one_shot",
            "keccak256_two_part_splits_match_one_shot",
        ):
            self.assertIn(f"conformance::{name}()", engine)


if __name__ == "__main__":
    unittest.main()
