from __future__ import annotations

import unittest
from pathlib import Path

from hashmark.evidence import (
    evm_results,
    native_results,
    skipped_results,
    target_evidence,
    unavailable_target,
)
from hashmark.fe_runner import TargetRun
from hashmark.fixtures import load_fixtures
from hashmark.models import TargetEvidence
from hashmark.oracle import digest_hex
from hashmark.protocol import NativeRecord


class EvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(__file__).resolve().parent.parent
        self.fixture = next(item for item in load_fixtures(self.root / "vectors") if item.id == "sha256-abc")
        self.oracle = {self.fixture.id: digest_hex(self.fixture.algorithm, self.fixture.input_bytes)}

    def test_target_command_is_portable(self) -> None:
        internal = TargetRun("evm", "PASS", ("/tmp/fe", "test"), ("suite",), None)
        observed = target_evidence(internal, self.root, Path("/tmp/fe"))
        self.assertEqual(observed.command, ("fe", "test"))

    def test_evm_failure_preserves_target_diagnostic(self) -> None:
        target = TargetEvidence("evm", "FAIL", ("fe", "test"), (), "assertion failed")
        observed = evm_results((self.fixture,), self.oracle, target)[0]
        self.assertEqual((observed.status, observed.diagnostic), ("FAIL", "assertion failed"))

    def test_evm_oracle_mismatch_fails(self) -> None:
        target = TargetEvidence("evm", "PASS", ("fe", "test"), ("suite",), None)
        observed = evm_results((self.fixture,), {self.fixture.id: "00" * 32}, target)[0]
        self.assertEqual(observed.status, "FAIL")

    def test_native_mismatch_fails(self) -> None:
        record = NativeRecord(self.fixture.id, "sha256", 4, "00" * 32, "native", "fail")
        observed = native_results((self.fixture,), self.oracle, (record,))[0]
        self.assertEqual(observed.status, "FAIL")

    def test_native_match_passes(self) -> None:
        record = NativeRecord(
            self.fixture.id,
            "sha256",
            self.fixture.input_length_bytes,
            self.fixture.expected_digest_hex,
            "native",
            "pass",
        )
        observed = native_results((self.fixture,), self.oracle, (record,))[0]
        self.assertEqual(observed.status, "PASS")

    def test_skipped_and_unavailable_are_explicit(self) -> None:
        result = skipped_results((self.fixture,), "native", self.oracle, "unsupported")[0]
        target = unavailable_target("native", "unsupported")
        self.assertEqual((result.status, target.status), ("SKIPPED", "UNAVAILABLE"))

    def test_unavailable_evm_uses_sonatina_command(self) -> None:
        target = unavailable_target("evm", "missing")
        self.assertEqual(target.command[-1], "sonatina")


if __name__ == "__main__":
    unittest.main()
