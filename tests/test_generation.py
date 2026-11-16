from __future__ import annotations

import unittest
from pathlib import Path

from hashmark.fixtures import load_fixtures
from scripts.generate_fe_vectors import _constant_name, generate_constants, generate_runner


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

    def test_native_runner_exposes_streaming_self_test(self) -> None:
        runner = generate_runner(self.fixtures)
        self.assertIn('args.get(1) == "--self-test"', runner)
        self.assertIn("conformance::streaming_suite()", runner)


if __name__ == "__main__":
    unittest.main()
