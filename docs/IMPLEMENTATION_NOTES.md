# Implementation notes

Status labels in this document are factual confidence labels, not test outcomes.

## Verified baseline — 15–16 November 2026

- **Verified:** the local checkout and `arinze116/Hashmark` remote were empty before implementation. There was no starting commit to preserve.
- **Verified:** all implementation commits were created on `feat/hashmark-conformance-lab`; no direct development commit was made on `main`.
- **Verified:** the host is Ubuntu 24.04.5 LTS on AArch64.
- **Verified:** `fe 26.6.0 (5b3f96a)` is installed at `/home/ubuntu/.fe/bin/fe`.
- **Verified:** the official contest starter is `https://github.com/fe-lang/builders-challenge-starter`, commit `f9d9aa92a03af82c2bbb0dc2e0810244eb13e686` when inspected.
- **Verified:** the starter uses a standard ingot with `fe.toml`, `src/lib.fe`, and `src/tests.fe`.
- **Verified:** Fe 26.6.0 names its EVM execution backend `sonatina`; Hashmark's user-facing backend name `evm` maps to `fe test --backend sonatina`.
- **Verified:** native tests use `fe test --backend native`; native executables use `fe build --backend native --emit executable`.
- **Verified:** Fe 26.6.0 refuses native test/executable emission on this AArch64 Linux host with `native test execution supports x86-64 Linux and AArch64 macOS`. Sonatina/EVM tests run locally; required native evidence must run on an x86-64 Linux CI runner.
- **Verified:** Docker is installed, but x86-64 containers fail with `exec format error` because host binfmt/QEMU emulation is not configured. Hashmark does not modify system-wide emulation settings.
- **Verified:** QEMU 10.2.1 in an isolated Ubuntu 26.04 ARM64 container can execute the exact Fe 26.6.0 x86-64 compiler; an ARM64-hosted x86 cross-linker produces the native executable without host package or binfmt changes.
- **Verified:** the final-audit x86-64 Hashmark native runner executed under user-space QEMU and produced 32 passing `HASHMARK/1` vector records plus `SUMMARY 32 32 0`; `--self-test` also produced `HASHMARK/SELFTEST/1 pass` for the shared streaming suite.
- **Verified:** native Fe test executables compile under the same emulation, but nested execution fails because the ARM64 host has no x86-64 binfmt handler. The host shell reports the emitted ELF as shell syntax. This is an environment execution limit, not recorded as a passing native test suite.
- **Verified:** the exact Fe source tag is `v26.6.0` at commit `5b3f96af2ab10df11bf847551f4b81d1fe481110`.
- **Verified:** `core::hash` exports `sha256`, `sha256_word`, `Sha256`, `keccak256`, `keccak256_word`, and `Keccak256`.
- **Verified:** both streaming states expose `new()`, `update(input, offset:, len:)`, `finish()`, and `finish_word()`.
- **Verified:** both streaming implementations explicitly accept zero-length updates.
- **Verified:** Python.org publishes CPython 3.15.2 and PyPI publishes PyCryptodome 4.4.0 with CPython 3.15-compatible AArch64 wheels.
- **Verified:** the installed `uv 0.12.6` catalogue did not offer CPython 3.15.2 for Linux AArch64, so the exact interpreter is built from the official CPython source tarball into a project-specific user directory.
- **Verified:** PyCryptodome 4.4.0 installs and passes SHA-256/Keccak oracle tests under the project-local CPython 3.15.2 interpreter.
- **Verified:** the published v1.0.0 suite had 105 Python tests. The final-audit branch has 109 tests and 92% line coverage under the official `python:3.15.2-slim` ARM64 image with Git installed; vector validation and `pip check` also pass.
- **Verified:** GitHub Actions release run `43757276440` measured 92% coverage under exact CPython 3.15.2 and passed all Fe, Python, integration and dependency-consistency jobs at source revision `3b5c3a6151b1f3acb1a63bdc09d0e214af80dad0`.
- **Verified:** the CI integration run produced 64/64 passing backend/vector results, 2/2 target suites and 32/32 native differential comparisons. Its deterministic evidence is committed under `reports/demo/`.
- **Verified:** generated report JSON validates against both Hashmark's fail-closed internal validator and the published Draft 2020-12 JSON Schema.
- **Verified:** desktop/tablet/mobile QA at 1440, 1024, 768, 375, and 320 pixels shows no page-level horizontal overflow. Target tables retain local scrolling.
- **Verified:** report text/status contrast ranges from 5.66:1 to 16.48:1. Structural borders are 3.08:1 or stronger against the report surface, satisfying the 3:1 non-text target.
- **Verified:** as of 16 November 2026, GitHub lists Fe `v26.6.0` (published 10 November 2026, commit `5b3f96a...`) as the newest stable release. No newer stable release is available to recommend.
- **Verified:** the official Fe guide still states that Fe is not production-ready because of known bugs, a limited standard library, and sometimes sub-optimal bytecode. The official contest separately allows Fe 26.5.0 or later, native or EVM projects, and working prototypes with documented limitations.

## Fe-core evidence engine — 21 November 2026

- **Verified:** v1.1.0 moves evaluation and evidence rendering into Fe. `scripts/generate_fe_vectors.py` now also generates `src/engine.fe` from the fixtures; the hand-written `src/evidence_render.fe` formats the engine's `HASHMARK/FE-EVIDENCE/1` JSON and Markdown documents. The native program exposes `--evidence-json` and `--evidence-markdown`, each optionally followed by `--algorithm` or `--vector`.
- **Verified:** the amd64 Fe 26.6.0 compiler under the isolated QEMU setup builds the rewritten program; `--evidence-json` reports 32/32 vectors and 6/6 streaming checks passing, the strict Python validator accepts the real Fe output, selector modes return the correct subsets with `complete_catalogue: false`, and the pre-existing `HASHMARK/1` and `--self-test` modes are unchanged.
- **Verified:** GitHub Actions run `44898673751` passes all four jobs at commit `6dd33ada6ca6eaa0bec10f87b289b46ac21c1b7d`, including the generated-source drift check over `src/engine.fe` and byte-identical `fe-evidence.json`/`fe-report.md` across two integration runs.
- **Verified:** Fe 26.6.0 string literals longer than roughly 32 bytes are `DynString(N)`, not `String<N>`; passing a long literal (for example a 33+ character check name) into a `String<N>` parameter is a type error. The renderer therefore prints the six fixed streaming-check names from an index dispatch instead of receiving them as parameters.
- **Verified:** in this isolated QEMU-user setup the guest's first user argument is consumed as the program-name slot (an x86-64 `echo alpha beta gamma` prints only `beta gamma`). The emulation wrapper therefore passes the program name explicitly as the first argument; on native x86-64 the standard argv layout applies and no placeholder is needed.
- **Verified:** Python suite is 128 tests, all passing locally under CPython 3.15.2; the Fe evidence parser rejects tampered digests, fingerprints, summaries, streaming order, and catalogue-scope mismatches.

## Intentional structure decisions

- The Fe project follows the official ingot convention under `src/`, rather than introducing a nested `fe/` project. This keeps `fe check`, `fe test`, and `fe build` aligned with the official starter.
- The default manifest target remains Sonatina/EVM. Native commands always pass `--backend native` explicitly.
- Local AArch64 Linux runs report native as unavailable rather than treating it as passed. GitHub Actions on x86-64 Linux is the authoritative clean native run for this repository.
- `.fe-version` records the exact requested compiler because Fe 26.6.0's ingot manifest has no verified compiler-version field. CI and preflight enforce the pin.
- `src/generated_vectors.fe` is the only generated Fe definition of expected digest values. Each digest literal appears once; aggregate arrays reference the canonical named constants. The test suite and native runner both consume those constants, and CI regenerates the files and requires a clean diff.
- `DigestCheck` is a small Fe-native result type rather than a duplicate hashing layer. It exposes expected/observed words and a pass predicate while still delegating all hashing to `core::hash`.
- Runtime Python code uses only the standard library and PyCryptodome. Coverage and `jsonschema` are pinned development-only dependencies.
- `reports/demo/` is imported from the successful x86-64 CI artefact. Final screenshots under `docs/assets/` show that report and its actual CI terminal summary; the ARM64 host did not fabricate an integrated native pass.

## CI supply-chain pins

- `actions/checkout` v6.0.1 commit `8e8c483db84b4bee98b60c0593521ed34d9990e8`.
- `actions/setup-python` v6.1.0 commit `83679a892e2d95755f2dac6acb0bfd1e9ac5d548`.
- `actions/upload-artifact` v7.0.2 commit `cf430e030ddbb5b0abf93d22962f4752f3646cd9`.
- Feup script is fetched from the Fe `v26.6.0` tag and checked against SHA-256 `b2dffd2d9d5b1a07d18e9321f57ab08442cc50df4a6004ee2fb538963812ee78` before execution.

## Source ledger

| Source | Accessed | Verified claim |
| --- | --- | --- |
| https://fe-lang.org/ | 2026-11-16 | Current Fe 26.6 feature summary, integrated toolchain, standard library and native-backend status |
| https://fe-lang.org/contest/ | 2026-11-16 | Every contest requirement, eligibility rule, deadline, rubric weight, AI policy and submission process |
| https://fe-lang.org/getting-started/installation/ | 2026-11-16 | Exact 26.6.0 installer, supported release platforms and source-build instructions |
| https://fe-lang.org/getting-started/what-is-fe/ | 2026-11-16 | Current language capabilities and the official non-production-ready qualification |
| https://fe-lang.org/ingots/project-structure/ | 2026-11-16 | Required `fe.toml`, `[ingot]`, `src/` and `src/lib.fe` project structure |
| https://fe-lang.org/ingots/package-manager/ | 2026-11-16 | Current `fe build`, `fe check`, metadata and experimental native-output behavior |
| https://fe-lang.org/testing/unit-testing/ | 2026-11-16 | Current built-in test and assertion behavior |
| https://fe-lang.org/testing/runner/ | 2026-11-16 | Current `fe test` runner, filtering, output and Osaka EVM-test context |
| https://blog.fe-lang.org/ | 2026-11-16 | Current official post index; 26.6.0 is the latest release post |
| https://blog.fe-lang.org/posts/release-26-6/ | 2026-11-16 | Native effects/I/O, C interop, destructors, `HashMap`, `core::hash`, storage packing and upgrade notes |
| https://blog.fe-lang.org/posts/release-26-5/ | 2026-11-16 | Mutable value semantics, closures, native release binaries and standard-library expansion |
| https://github.com/argotorg/fe | 2026-11-16 | Public compiler repository, Apache-2.0 licence, current default branch and official source |
| https://github.com/argotorg/fe/releases/tag/v26.6.0 | 2026-11-16 | Exact release date, assets, tag and complete 26.6.0 changelog |
| https://github.com/fe-lang/builders-challenge-starter | 2026-11-15 | Ingot layout and baseline CI commands |
| https://github.com/argotorg/fe/blob/v26.6.0/ingots/core/src/hash.fe | 2026-11-16 | Exact hash APIs, target-neutral software implementation, Keccak suffix, rates, streaming and empty-update behavior |
| https://csrc.nist.gov/Projects/cryptographic-algorithm-validation-program/secure-hashing | 2026-11-15 | SHA response vectors and informal-verification limitation |
| https://keccak.team/software.html | 2026-11-15 | XKCP provenance and Keccak reference resources |
| https://www.python.org/downloads/ | 2026-11-15 | CPython 3.15.2 release availability |
| https://pypi.org/project/pycryptodome/4.4.0/ | 2026-11-15 | PyCryptodome version and Python compatibility |
| https://pypi.org/project/coverage/7.17.3/ | 2026-11-15 | Coverage development tool version |
| https://pypi.org/project/jsonschema/4.26.0/ | 2026-11-15 | Draft 2020-12 report-schema validation tool version |
