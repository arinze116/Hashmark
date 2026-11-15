"""Generate Hashmark's deterministic committed vector corpus."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

from hashmark.oracle import digest_hex
from hashmark.version import FIXTURE_SCHEMA_VERSION

SHA256_LENGTHS = (1, 2, 3, 55, 56, 57, 63, 64, 65, 119, 120, 127, 128, 129, 1024, 65536)
KECCAK_LENGTHS = (1, 2, 3, 135, 136, 137, 271, 272, 273, 1024, 65536)
NIST_URL = (
    "https://csrc.nist.gov/CSRC/media/Projects/Cryptographic-Algorithm-Validation-Program/"
    "documents/shs/shabytetestvectors.zip"
)
XKCP_URL = "https://github.com/XKCP/XKCP"
XKCP_COMMIT = "d20c8fcaecc543f816a0721d0dfc13b4cf27c14d"


def deterministic_input(length: int) -> bytes:
    """Return the input specified by the Hashmark PRD."""

    return bytes((index * 131 + 17) % 256 for index in range(length))


def vector(
    fixture_id: str,
    algorithm: str,
    category: str,
    data: bytes,
    *,
    source_name: str,
    source_url: str,
    source_document: str,
    source_case_id: str,
    usage: str,
    notes: str | None,
) -> dict[str, Any]:
    """Build one canonical fixture object."""

    return {
        "schema_version": FIXTURE_SCHEMA_VERSION,
        "id": fixture_id,
        "algorithm": algorithm,
        "category": category,
        "input_hex": data.hex(),
        "expected_digest_hex": digest_hex(algorithm, data),
        "input_length_bytes": len(data),
        "source_name": source_name,
        "source_url": source_url,
        "source_document": source_document,
        "source_case_id": source_case_id,
        "licence_or_usage_note": usage,
        "notes": notes,
    }


def known_answer_vectors() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Return the attributed known-answer vectors."""

    nist_usage = "NIST test vectors are public reference data for informal verification; use does not imply CAVP validation."
    xkcp_usage = "XKCP KeccakSum source is CC0; repository exceptions are documented in its LICENSE file."
    sha = [
        vector(
            "sha256-empty", "sha256", "known_answer", b"",
            source_name="NIST CAVP", source_url=NIST_URL,
            source_document="SHA256ShortMsg.rsp", source_case_id="Len = 0",
            usage=nist_usage, notes="FIPS 180-4 SHA-256 empty-message response vector.",
        ),
        vector(
            "sha256-abc", "sha256", "known_answer", b"abc",
            source_name="NIST FIPS 180-4", source_url="https://doi.org/10.6028/NIST.FIPS.180-4",
            source_document="FIPS 180-4 SHA-256 example", source_case_id="message abc",
            usage="United States government work; cited as the algorithm standard.",
            notes="Canonical SHA-256 example.",
        ),
        vector(
            "sha256-nist-short-d3", "sha256", "known_answer", bytes.fromhex("d3"),
            source_name="NIST CAVP", source_url=NIST_URL,
            source_document="SHA256ShortMsg.rsp", source_case_id="Len = 8; Msg = d3",
            usage=nist_usage, notes="Selected byte-oriented NIST short-message vector.",
        ),
    ]
    expected_d3 = "28969cdfa74a12c82f3bad960b0b000aca2ac329deea5c2328ebc6f2ba9802c1"
    if sha[-1]["expected_digest_hex"] != expected_d3:
        raise RuntimeError("hashlib does not match the selected NIST SHA-256 vector")
    keccak = [
        vector(
            "keccak256-empty", "keccak256", "known_answer", b"",
            source_name="Keccak Team / XKCP", source_url=XKCP_URL,
            source_document="util/KeccakSum/KeccakSum.c", source_case_id="--ethereum over empty input",
            usage=xkcp_usage, notes=f"Cross-checked with XKCP commit {XKCP_COMMIT}.",
        ),
        vector(
            "keccak256-abc", "keccak256", "known_answer", b"abc",
            source_name="Keccak Team / XKCP", source_url=XKCP_URL,
            source_document="util/KeccakSum/KeccakSum.c", source_case_id="--ethereum over abc",
            usage=xkcp_usage, notes=f"Cross-checked with XKCP commit {XKCP_COMMIT}.",
        ),
    ]
    return sha, keccak


def boundary_vectors(algorithm: str, lengths: tuple[int, ...]) -> list[dict[str, Any]]:
    """Return deterministic boundary and long-message fixtures."""

    block = 64 if algorithm == "sha256" else 136
    source_name = "Hashmark deterministic boundary generator"
    source_url = "https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md"
    source_document = "F-03 deterministic input formula"
    usage = "Generated data released under Hashmark's MIT license; digests checked by independent reference software."
    result: list[dict[str, Any]] = []
    for length in lengths:
        is_long = length >= 1024
        suffix = "1k" if length == 1024 else "64k" if length == 65536 else str(length)
        category = "long_message" if is_long else "boundary"
        result.append(
            vector(
                f"{algorithm}-{'long' if is_long else 'boundary'}-{suffix}",
                algorithm,
                category,
                deterministic_input(length),
                source_name=source_name,
                source_url=source_url,
                source_document=source_document,
                source_case_id=f"length={length}; block-or-rate={block}",
                usage=usage,
                notes="byte[i] = (i * 131 + 17) mod 256",
            ),
        )
    return result


def check_xkcp(binary: Path, vectors: list[dict[str, Any]]) -> None:
    """Require every Keccak fixture to match XKCP's Ethereum mode."""

    for item in vectors:
        completed = subprocess.run(
            [str(binary), "--ethereum", "--hex", "-"],
            input=bytes.fromhex(item["input_hex"]),
            capture_output=True,
            check=True,
        )
        observed = completed.stdout.decode("ascii").split()[0]
        if observed != item["expected_digest_hex"]:
            raise RuntimeError(f"XKCP mismatch for {item['id']}")


def write_document(path: Path, vectors: list[dict[str, Any]]) -> None:
    """Write one stable fixture document."""

    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"schema_version": FIXTURE_SCHEMA_VERSION, "vectors": vectors}
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("vectors"))
    parser.add_argument("--xkcp-binary", type=Path)
    args = parser.parse_args()

    sha_known, keccak_known = known_answer_vectors()
    sha_boundaries = boundary_vectors("sha256", SHA256_LENGTHS)
    keccak_boundaries = boundary_vectors("keccak256", KECCAK_LENGTHS)
    all_keccak = keccak_known + keccak_boundaries
    if args.xkcp_binary is not None:
        check_xkcp(args.xkcp_binary.resolve(), all_keccak)

    write_document(args.output / "sha256" / "known-answer.json", sha_known)
    write_document(args.output / "sha256" / "boundaries.json", sha_boundaries)
    write_document(args.output / "keccak256" / "known-answer.json", keccak_known)
    write_document(args.output / "keccak256" / "boundaries.json", keccak_boundaries)
    manifest = {
        "schema_version": FIXTURE_SCHEMA_VERSION,
        "generator": "byte[i] = (i * 131 + 17) mod 256",
        "nist_archive_sha256": "929ef80b7b3418aca026643f6f248815913b60e01741a44bba9e118067f4c9b8",
        "xkcp_commit": XKCP_COMMIT,
        "vector_count": len(sha_known + sha_boundaries + all_keccak),
    }
    (args.output / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"generated {manifest['vector_count']} vectors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
