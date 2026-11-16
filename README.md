# `##✓` Hashmark

> Reproducible cryptographic evidence for Fe.

Hashmark independently checks Fe 26.6.0's built-in SHA-256 and Ethereum Keccak-256 implementations across native and EVM targets, then turns each vector into inspectable JSON, Markdown, and offline HTML evidence.

[![CI](https://github.com/arinze116/Hashmark/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/arinze116/Hashmark/actions/workflows/ci.yml)

| Authoritative x86-64 CI summary | Offline evidence report |
| --- | --- |
| ![GNOME Terminal showing Hashmark passing 64 of 64 backend-vector checks, two of two target suites and 32 of 32 differential comparisons](docs/assets/hashmark-terminal-summary.png) | ![Hashmark offline report showing PASS, 64 executed results, native and EVM target suites, and 32 differential comparisons](docs/assets/hashmark-report-overview.png) |
| Actual terminal capture from the passing integration job. | Actual self-contained HTML report downloaded from the same CI run. |

**Status:** Fe 26.6.0 · SHA-256 + Ethereum Keccak-256 · native + EVM · Python 3.15.2 oracle · [v1.0.0 release CI passing](https://github.com/arinze116/Hashmark/actions/runs/43757276440) · MIT

**Run:** `python -m hashmark run --all --backend all --format all --output-dir reports/local`

[Open the committed all-backend report](reports/demo/index.html) or inspect its [canonical JSON](reports/demo/hashmark-report.json).

## Why Hashmark exists

A plausible digest is not evidence of correctness. Padding bugs, byte-order mistakes, finalisation errors, and streaming defects often appear only at exact block or rate boundaries. A single `abc` assertion cannot show whether the same implementation behaves correctly for empty input, multi-block messages, split updates, or another compiler target.

Hashmark provides a Fe-first conformance workflow:

- thin adapters over `core::hash`; no cryptographic primitive is reimplemented;
- 32 committed vectors covering known answers, boundaries, and 1 KiB/64 KiB messages;
- ten shared Fe suites on Sonatina/EVM and native backends;
- independent `hashlib.sha256` and PyCryptodome Keccak-256 oracles;
- a strict `HASHMARK/1` native result protocol;
- deterministic JSON, Markdown, and self-contained HTML evidence;
- fail-closed fixture, protocol, subprocess, and report validation.

Hashmark is informal conformance testing. It is not NIST CAVP validation, a security audit, certification, or exhaustive proof.

## Ten-second run

On x86-64 Linux with Fe 26.6.0 and Python 3.15.2 installed:

```console
python3.15 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt -e .
python -m hashmark run --all --backend all --format all --output-dir reports/local
```

The report opens offline at `reports/local/index.html`. Hashmark refuses to overwrite a non-empty output directory unless `--force` is supplied, and even then it replaces only known Hashmark report files.

## Evidence at a glance

The committed corpus contains 32 vectors: 19 SHA-256 and 13 Ethereum Keccak-256. A complete two-backend run produces 64 backend/vector evidence records, two target-suite outcomes, and 32 native Fe-versus-oracle digest comparisons.

Published v1.0.0 evidence, verified by the pinned x86-64 workflow:

| Check | Result | Evidence |
| --- | ---: | --- |
| Full backend/vector run | 64/64 pass | [Release CI integration run](https://github.com/arinze116/Hashmark/actions/runs/43757276440) |
| Fe target suites | 2/2 pass | ten shared tests on Sonatina/EVM and native |
| Native differential comparisons | 32/32 pass | committed `HASHMARK/1` protocol log |
| Python tests | 105 pass | CPython 3.15.2 CI job |
| Python line coverage | 92% | Coverage.py 7.17.3; `hashmark/__main__.py` excluded |
| Deterministic reports | byte-identical | JSON, Markdown, HTML, sidecar, and native protocol compared twice |

The final-audit branch additionally passes 108 Python tests at 92% line coverage, ten Sonatina/EVM Fe suites, native IR compilation on AArch64 Linux, and an x86-64 native executable run under isolated QEMU with 32/32 vectors plus the shared streaming self-test. These audit-branch results are local evidence until that commit is pushed and CI runs.

The x86-64 GitHub Actions job is authoritative because Fe 26.6.0 does not execute native tests on ARM64 Linux. A skipped or unavailable target is never counted as passing.

## Evidence screenshots

| Expanded boundary evidence | Controlled negative test |
| --- | --- |
| ![Expanded native SHA-256 boundary vector showing identical expected, Fe and independent oracle digests](docs/assets/hashmark-vector-detail.png) | ![Controlled failure report placing the corrupted SHA-256 expected digest before successful evidence](docs/assets/hashmark-controlled-failure.png) |
| `sha256-boundary-56` exposes the exact input fingerprint and three digest values. | A disposable mutation exits non-zero and produces failure-first evidence. |

![Mobile Hashmark report at 375 pixels showing a responsive summary and locally scrollable target table](docs/assets/hashmark-report-mobile.png)

The mobile report retains the same status text and evidence hierarchy without page-level horizontal overflow.

## Architecture

```mermaid
flowchart LR
    V[Committed vectors + provenance] --> P[Strict Python fixture loader]
    P --> O[Independent Python oracle]
    P --> F[Shared generated Fe constants]
    F --> E[Sonatina / EVM test suites]
    F --> N[Native Fe tests + runner]
    N --> R[HASHMARK/1 parser]
    O --> C[Evidence comparison]
    E --> C
    R --> C
    C --> J[Canonical JSON]
    J --> M[Markdown]
    J --> H[Offline HTML]
```

The Python layer orchestrates and reports; it does not replace Fe as the implementation under test. The same Fe adapter and vector constants feed both compiler backends. EVM evidence records aggregate suite status because the Fe EVM runner does not expose per-vector return digests. Native evidence carries each actual Fe digest.

Read [Architecture](docs/ARCHITECTURE.md) and [ADR 0001](docs/adr/0001-language-and-architecture.md) for the complete rationale.

## Fe-specific contribution

Hashmark exercises `core::hash::{sha256, Sha256, keccak256, Keccak256}` directly. Its reusable Fe API returns a typed result that preserves both the expected and observed digest:

```fe
let check = sha256::check(input.span(), generated_vectors::SHA256_BOUNDARY_56)
assert!(check.passes())
let observed = check.observed()
```

The same API supports one-shot, fixed-chunk, and explicit-empty-update checks. `conformance::streaming_suite()` covers uneven partitions and every two-part split through 140 bytes. The generated native runner consumes the same `generated_vectors` constants as the Fe tests, so expected digests are not duplicated in a second generated source.

`fe test --backend sonatina` and `fe test --backend native` compile the same source rather than maintaining target-specific vector suites. The native executable also exposes `--self-test` as a direct target-neutral streaming check for constrained or cross-emulated environments.

Fe calls its local EVM execution backend `sonatina`; Hashmark presents it as `evm` in its public CLI and reports. No contract, wallet, RPC endpoint, testnet, or mainnet deployment is involved.

## SHA-256, Keccak-256, and SHA3-256

Hashmark supports:

- SHA-256 as specified by NIST;
- Ethereum Keccak-256 with Keccak's legacy domain suffix;
- not FIPS SHA3-256.

PyCryptodome's `Crypto.Hash.keccak.new(digest_bits=256)` is the independent Keccak oracle. A regression test proves that Keccak-256(`abc`) differs from `hashlib.sha3_256(b"abc")`.

## Verification method

1. Validate every fixture before invoking Fe.
2. Compute the oracle digest from the fixture bytes, never from Fe output.
3. Run the requested Fe backend.
4. Parse native records with exact field, identifier, digest, uniqueness, and summary checks.
5. Compare fixture, Fe, and oracle values.
6. Validate the report invariants before writing it atomically.
7. Write stable, sorted artefacts without timestamps, host paths, randomness, or elapsed time.

SHA-256 canonical vectors are traced to NIST CAVP material. Keccak vectors were reproduced against XKCP commit `d20c8fcaecc543f816a0721d0dfc13b4cf27c14d`. Deterministic boundary inputs use `byte[i] = (i * 131 + 17) mod 256`. See [Cryptography and provenance](docs/CRYPTOGRAPHY.md) and [Vector format](docs/VECTOR_FORMAT.md).

## CLI reference

```console
python -m hashmark --help
python -m hashmark version
python -m hashmark list [--algorithm sha256|keccak256]
python -m hashmark validate-vectors
python -m hashmark run --all [--backend native|evm|all]
python -m hashmark run --algorithm sha256
python -m hashmark run --vector sha256-abc
python -m hashmark run --all --format all --output-dir reports/local
```

`--format` accepts `terminal`, `json`, `markdown`, `html`, or `all`. `--timeout-seconds` accepts 1–600. `HASHMARK_FE_BIN`, `HASHMARK_TIMEOUT_SECONDS`, `HASHMARK_OUTPUT_DIR`, and `NO_COLOR` are optional; no secrets or `.env` file are required.

| Exit | Meaning |
| ---: | --- |
| 0 | every requested check completed and passed |
| 1 | conformance mismatch or Fe assertion failure |
| 2 | invalid argument or fixture |
| 3 | missing or wrong toolchain/dependency |
| 4 | timeout, process failure, or invalid native protocol |
| 5 | report validation or write failure |

## Add a vector

1. Add the fixture to the correct JSON document under `vectors/sha256/` or `vectors/keccak256/`.
2. Include the authoritative HTTPS source, document, case ID, and usage note.
3. Run `python -m hashmark validate-vectors`.
4. Regenerate Fe constants with `python scripts/generate_fe_vectors.py`.
5. Run the exact vector, then the full Python and Fe suites.

Never edit an expected digest merely to make a failing suite green. Check the source vector and independent oracle first. See [Contributing](CONTRIBUTING.md).

## Toolchain and platform support

The project requires exact versions:

- Fe `26.6.0 (5b3f96a)`;
- Python `3.15.2`;
- PyCryptodome `4.4.0`.

Install Fe with the official versioned installer:

```console
curl -fsSL https://raw.githubusercontent.com/argotorg/fe/v26.6.0/feup/feup.sh -o /tmp/feup.sh
echo "b2dffd2d9d5b1a07d18e9321f57ab08442cc50df4a6004ee2fb538963812ee78  /tmp/feup.sh" | sha256sum --check --strict
bash /tmp/feup.sh --version v26.6.0 --no-modify-path
export PATH="$HOME/.fe/bin:$PATH"
```

| Host | EVM | Native |
| --- | --- | --- |
| x86-64 Linux | supported | supported |
| AArch64 macOS | supported | supported by Fe 26.6.0 |
| AArch64 Linux | supported | use the x86-64 CI job |
| Windows | use WSL2 | use WSL2 on x86-64 |

## Tests and CI

```console
fe fmt --check
fe check
fe test --backend sonatina
fe test --backend native
python -m pip install -r requirements-dev.txt -e .
python -m coverage run -m unittest discover -s tests -v
python -m coverage report
python -m hashmark validate-vectors
python scripts/generate_fe_vectors.py
git diff --exit-code -- src/generated_vectors.fe src/native_runner.fe
```

The pinned GitHub Actions workflow runs separate Fe, Python, integration, and dependency-consistency jobs. Integration generates the full report twice, compares every artefact byte-for-byte, validates report invariants, and uploads the evidence directory.

For a compiler-only build on any release platform, run `fe build --backend native --emit ir --out-dir out/native-ir`. On x86-64 Linux or AArch64 macOS, `fe build --backend native --emit executable --out-dir out/native` produces the runnable `hashmark` program.

## Limitations and non-claims

- Passing Hashmark does not provide formal NIST CAVP validation or certification.
- Hashmark is not a security audit, proof of cryptographic security, or exhaustive input test.
- Fe 26.6.0 describes itself as not production-ready; this project records observed behavior for that pinned compiler.
- That general maturity warning does not affect contest eligibility: the official challenge permits Fe 26.5.0 or later, native or EVM projects, and working prototypes with documented limitations.
- EVM records carry aggregate Fe test evidence rather than fabricated per-vector EVM digests.
- The standard corpus is deterministic and bounded; fuzzing and benchmarking are outside the MVP.

## Contest and AI-assistance disclosure

Hashmark was built for the [Fe Builders Challenge](https://fe-lang.org/contest/) during the official build window. Repository history begins on 15 November 2026 and contains no pre-contest source; the entrant must still confirm that there is no undisclosed off-repository starting work. An autonomous OpenAI coding agent assisted with research, implementation, tests, documentation, and reproducibility work under the project owner's direction. The responsible human entrant must review, understand, and be able to explain the code, architecture, evidence model, and limitations.

Hashmark copies no cryptographic implementation. It calls Fe `core::hash`, Python `hashlib`, and PyCryptodome; generated boundary inputs are Hashmark code, while NIST and XKCP materials are attributed reference data. Research references and exact source decisions are recorded in [Implementation notes](docs/IMPLEMENTATION_NOTES.md).

## Licence

Hashmark source is available under the [MIT licence](LICENSE). Third-party names, links, and vector provenance remain attributable to their respective projects and do not imply endorsement.
