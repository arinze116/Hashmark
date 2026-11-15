# Hashmark evidence report — FAIL

> Informal conformance evidence only; not formal certification or a security audit.

## Summary

| Total | Passed | Failed | Skipped | Target suites | Differential comparisons |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0 | 1 | 0 | 1/1 | 0/0 |

## Target matrix

| Backend | Status | Test identifiers | Diagnostic |
| --- | --- | --- | --- |
| evm | **PASS** | `keccak256_generated_vectors`, `keccak256_known_answers`, `keccak256_streaming_matches_one_shot`, `keccak256_two_part_splits_match_one_shot`, `keccak256_uneven_partition_matches_one_shot`, `sha256_generated_vectors`, `sha256_known_answers`, `sha256_streaming_matches_one_shot`, `sha256_two_part_splits_match_one_shot`, `sha256_uneven_partition_matches_one_shot` | — |

## Failures and skipped evidence

### FAIL: `sha256-abc` on evm

- Expected: `0000000000000000000000000000000000000000000000000000000000000000`
- Fe: `not exposed by EVM runner`
- Oracle: `ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad`
- Diagnostic: expected digest does not match the independent oracle

## SHA-256 results

### FAIL: `sha256-abc` / evm

- Category: `known_answer`
- Input length: 3 bytes
- Input SHA-256: `ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad`
- Expected: `0000000000000000000000000000000000000000000000000000000000000000`
- Fe: `not exposed by EVM runner`
- Oracle: `ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad`
- Evidence basis: `evm_test_status`
- Source: [NIST FIPS 180-4](https://doi.org/10.6028/NIST.FIPS.180-4) — message abc
- Notes: Canonical SHA-256 example.

## Provenance

- Source revision: `UNCOMMITTED`
- Source tree SHA-256: `72910a9b175fdd7f5241707468f0b0ec117fa576b0fddb2cf7e96ec7a3816039`
- Fixture manifest SHA-256: `9321ceae1d02799403e24a4aafc61a298e67bf8b6bd63838dd5a4326e772d2f3`
- Fe: `fe 26.6.0 (5b3f96a)`
- Python: `3.15.2`
- PyCryptodome: `4.4.0`
- Report schema: `1`

## Limitations

- Informal conformance testing only; this is not formal NIST CAVP validation or certification.
- Passing vectors are not a security audit, proof of cryptographic security, or exhaustive testing.
- Fe 26.6.0 is not production-ready; Hashmark records observed behavior for this pinned compiler.
- The Fe EVM test runner exposes test status and identifiers, not per-vector runtime digest output.

## Reproduce

```console
python -m hashmark run --all --backend all --format all --output-dir reports/local
```
