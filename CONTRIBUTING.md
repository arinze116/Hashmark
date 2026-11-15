# Contributing to Hashmark

Hashmark accepts focused changes that preserve deterministic, fail-closed evidence.

## Development setup

Use Fe 26.6.0, Python 3.15.2, and PyCryptodome 4.4.0 exactly. Install development dependencies with:

```console
python -m pip install -r requirements-dev.txt -e .
```

Before opening a change, run:

```console
fe fmt --check
fe check
fe test --backend sonatina
fe test --backend native
python -m coverage run -m unittest discover -s tests -v
python -m coverage report
python -m hashmark validate-vectors
```

## Adding vectors

Every vector needs stable provenance and must follow [the fixture schema](docs/VECTOR_FORMAT.md). Expected values must be calculated independently and checked against an authoritative source. Do not download fixtures during a test run.

After editing vectors, regenerate `src/generated_vectors.fe` with `python scripts/generate_fe_vectors.py`, inspect the diff, and run the full matrix. Generated Fe constants and JSON fixtures must not drift.

## Change standards

- Do not reimplement SHA-256 or Keccak-256.
- Do not substitute FIPS SHA3-256 for Ethereum Keccak-256.
- Do not weaken fixture, protocol, subprocess, or report validation.
- Add behavior-focused tests for every failure path.
- Keep report output deterministic and free of timestamps, host paths, and random identifiers.
- Preserve the informal-verification disclaimer.

Security-sensitive reports should be sent privately to the repository owner before public disclosure. Hashmark requires no secrets, wallets, RPC credentials, or production access.
