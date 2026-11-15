# Cryptography and provenance

## Supported algorithms

Hashmark verifies Fe's existing SHA-256 and Ethereum Keccak-256 implementations. It does not implement compression rounds, padding, message schedules, or the Keccak permutation.

SHA-256 uses Python `hashlib.sha256` as its independent oracle. Ethereum Keccak-256 uses `Crypto.Hash.keccak.new(digest_bits=256)`. FIPS SHA3-256 is intentionally unsupported because its domain-separation padding differs from Ethereum Keccak-256.

Canonical checks include:

| Algorithm | Input | Expected digest |
| --- | --- | --- |
| SHA-256 | empty | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| SHA-256 | `abc` | `ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad` |
| Keccak-256 | empty | `c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470` |
| Keccak-256 | `abc` | `4e03657aea45a94fc7d47ba826c8d667c0d1e6e33a64a036ec44f58fa12d6c45` |

## Boundary corpus

SHA-256 vectors cover 0, 1, 2, 3, 55, 56, 57, 63, 64, 65, 119, 120, 127, 128, 129, 1,024, and 65,536 bytes. These lengths surround the 64-byte block and padding transitions.

Keccak-256 vectors cover 0, 1, 2, 3, 135, 136, 137, 271, 272, 273, 1,024, and 65,536 bytes. These lengths surround the 136-byte Keccak-256 rate.

Generated inputs use:

```text
byte[i] = (i * 131 + 17) mod 256
```

The generator is mirrored in Python and Fe. Reports store input length and SHA-256 rather than duplicating long inputs.

## Streaming checks

Both algorithms test one-shot hashing against 1-, 7-, and 31-byte chunks, their relevant block/rate boundaries, one byte below and above those boundaries, the uneven partition `[1, 2, 5, 13, 29, 64]`, zero-length updates, and every two-part split from 0 through 140 bytes. Fe's installed 26.6.0 source explicitly supports zero-length updates.

## Source ledger

### NIST SHA vectors

- Project: NIST Cryptographic Algorithm Validation Program.
- Source: https://csrc.nist.gov/Projects/cryptographic-algorithm-validation-program/secure-hashing
- Retrieved archive SHA-256: `929ef80b7b3418aca026643f6f248815913b60e01741a44bba9e118067f4c9b8`.
- Use: canonical and selected short-message cross-checks.
- Limitation: NIST states that using response files for informal verification does not constitute formal CAVP validation.

### Keccak/XKCP

- Project: Keccak Team / XKCP.
- Source: https://keccak.team/software.html
- Reproduction commit: `d20c8fcaecc543f816a0721d0dfc13b4cf27c14d`.
- Use: independent cross-check of every committed Keccak fixture during development.

Fixture metadata records a source name, HTTPS URL, document, case ID, usage note, and optional notes. Runtime tests never download source data.

## Non-claims

Passing Hashmark is not certification, formal validation, proof of implementation security, exhaustive testing, or endorsement by NIST, the Keccak Team, XKCP, PyCryptodome, or the Fe project.
