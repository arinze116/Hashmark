from __future__ import annotations

import hashlib
import unittest

from hashmark.oracle import keccak256_digest, pycryptodome_version, sha256_digest


class OracleTests(unittest.TestCase):
    def test_sha256_empty(self) -> None:
        self.assertEqual(
            sha256_digest(b"").hex(),
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        )

    def test_sha256_abc(self) -> None:
        self.assertEqual(
            sha256_digest(b"abc").hex(),
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
        )

    def test_keccak256_empty(self) -> None:
        self.assertEqual(
            keccak256_digest(b"").hex(),
            "c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470",
        )

    def test_keccak256_abc(self) -> None:
        self.assertEqual(
            keccak256_digest(b"abc").hex(),
            "4e03657aea45a94fc7d47ba826c8d667c0d1e6e33a64a036ec44f58fa12d6c45",
        )

    def test_keccak_is_not_sha3(self) -> None:
        self.assertNotEqual(keccak256_digest(b"abc"), hashlib.sha3_256(b"abc").digest())

    def test_pinned_distribution_version(self) -> None:
        self.assertEqual(pycryptodome_version(), "4.4.0")


if __name__ == "__main__":
    unittest.main()
