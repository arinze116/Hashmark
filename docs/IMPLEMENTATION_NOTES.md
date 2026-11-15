# Implementation notes

Status labels in this document are factual confidence labels, not test outcomes.

## Verified baseline — 15 November 2026

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
- **Verified:** QEMU 10.2.3 plus an Ubuntu Noble x86-64 userspace can execute the exact Fe 26.6.0 compiler and linker without system changes.
- **Verified:** the emitted x86-64 Hashmark native runner executed under user-space QEMU and produced 32 passing `HASHMARK/1` vector records plus `SUMMARY 32 32 0`.
- **Verified:** native Fe test executables compile under the same emulation, but nested execution fails because the ARM64 host has no x86-64 binfmt handler. The host shell reports the emitted ELF as shell syntax. This is an environment execution limit, not recorded as a passing native test suite.
- **Verified:** the exact Fe source tag is `v26.6.0` at commit `5b3f96af2ab10df11bf847551f4b81d1fe481110`.
- **Verified:** `core::hash` exports `sha256`, `sha256_word`, `Sha256`, `keccak256`, `keccak256_word`, and `Keccak256`.
- **Verified:** both streaming states expose `new()`, `update(input, offset:, len:)`, `finish()`, and `finish_word()`.
- **Verified:** both streaming implementations explicitly accept zero-length updates.
- **Verified:** Python.org publishes CPython 3.15.2 and PyPI publishes PyCryptodome 4.4.0 with CPython 3.15-compatible AArch64 wheels.
- **Verified:** the installed `uv 0.12.6` catalogue did not offer CPython 3.15.2 for Linux AArch64, so the exact interpreter is built from the official CPython source tarball into a project-specific user directory.
- **Verified:** PyCryptodome 4.4.0 installs and passes SHA-256/Keccak oracle tests under the project-local CPython 3.15.2 interpreter.
- **Verified:** 105 Python tests pass. Coverage.py 7.17.3 cannot run on the project-local interpreter because that user-built Python lacks the optional `_sqlite3` module; the same suite measured 92% line coverage under the host Python 3.12.3 with the Python-version preflight patched only for measurement.
- **Verified:** GitHub Actions run `43756807882` measured the same 92% coverage under exact CPython 3.15.2 and passed all Fe, Python, integration and dependency-consistency jobs at source revision `fb45a89f64cbd237e92165029a5aafd2f0f88c0e`.
- **Verified:** the CI integration run produced 64/64 passing backend/vector results, 2/2 target suites and 32/32 native differential comparisons. Its deterministic evidence is committed under `reports/demo/`.
- **Verified:** generated report JSON validates against both Hashmark's fail-closed internal validator and the published Draft 2020-12 JSON Schema.
- **Verified:** desktop/tablet/mobile QA at 1440, 1024, 768, 375, and 320 pixels shows no page-level horizontal overflow. Target tables retain local scrolling.
- **Verified:** report text/status contrast ranges from 5.66:1 to 16.48:1. Structural borders are 3.08:1 or stronger against the report surface, satisfying the 3:1 non-text target.

## Intentional structure decisions

- The Fe project follows the official ingot convention under `src/`, rather than introducing a nested `fe/` project. This keeps `fe check`, `fe test`, and `fe build` aligned with the official starter.
- The default manifest target remains Sonatina/EVM. Native commands always pass `--backend native` explicitly.
- Local AArch64 Linux runs report native as unavailable rather than treating it as passed. GitHub Actions on x86-64 Linux is the authoritative clean native run for this repository.
- `.fe-version` records the exact requested compiler because Fe 26.6.0's ingot manifest has no verified compiler-version field. CI and preflight enforce the pin.
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
| https://fe-lang.org/contest/ | 2026-11-15 | Contest dates, rubric, starter link, AI disclosure and submission requirements |
| https://github.com/fe-lang/builders-challenge-starter | 2026-11-15 | Ingot layout and baseline CI commands |
| https://blog.fe-lang.org/posts/release-26-6/ | 2026-11-15 | Native effects, target configuration and Fe 26.6.0 release behavior |
| https://github.com/argotorg/fe/tree/v26.6.0/ingots/core/src/hash.fe | 2026-11-15 | Exact hash APIs, Keccak suffix, rates, streaming and empty-update behavior |
| https://csrc.nist.gov/Projects/cryptographic-algorithm-validation-program/secure-hashing | 2026-11-15 | SHA response vectors and informal-verification limitation |
| https://keccak.team/software.html | 2026-11-15 | XKCP provenance and Keccak reference resources |
| https://www.python.org/downloads/ | 2026-11-15 | CPython 3.15.2 release availability |
| https://pypi.org/project/pycryptodome/4.4.0/ | 2026-11-15 | PyCryptodome version and Python compatibility |
| https://pypi.org/project/coverage/7.17.3/ | 2026-11-15 | Coverage development tool version |
| https://pypi.org/project/jsonschema/4.26.0/ | 2026-11-15 | Draft 2020-12 report-schema validation tool version |
