# Changelog

All notable project changes are documented here.

## 1.1.0 — 2026-11-21

- Moved evidence evaluation into Fe: a generated engine (`src/engine.fe`) evaluates every vector with the typed `DigestCheck` API and runs the six streaming conformance checks inside the native Fe program.
- Added a hand-written Fe evidence renderer (`src/evidence_render.fe`) and two native program modes, `--evidence-json` and `--evidence-markdown`, emitting a deterministic `HASHMARK/FE-EVIDENCE/1` JSON document and a Markdown report directly from Fe.
- Added a strict Python validator (`hashmark/fe_evidence.py`) that checks the Fe evidence document field-by-field against the committed fixtures; the native runner cross-checks it against the `HASHMARK/1` protocol stream and fails closed on any disagreement.
- Report bundles now include `fe-evidence.json` and `fe-report.md` alongside the existing artefacts, and CI byte-compares them across two runs.
- Python test suite grows from 109 to 128 tests, including Fe evidence parser, tamper, and cross-stream disagreement cases.

## Unreleased — final compliance audit

- Added a typed Fe `DigestCheck` conformance result and reusable streaming suite.
- Removed duplicated expected digests from the generated native runner and aggregate arrays.
- Added a native `--self-test` mode and generation-drift tests/CI enforcement.
- Made report source-revision detection deterministic when Git is unavailable.
- Updated contest, release, disclosure, and reproducibility documentation from current official sources.

## 1.0.0 — 2026-11-15

- Added Fe 26.6.0 SHA-256 and Ethereum Keccak-256 adapters.
- Added 32 attributed known-answer, boundary, and long-message vectors.
- Added shared Sonatina/EVM and native Fe conformance suites, including streaming partitions.
- Added a strict native evidence protocol and independent Python oracles.
- Added deterministic JSON, Markdown, and offline HTML reports.
- Added fail-closed fixture, protocol, report, and subprocess validation.
- Added pinned CI, negative tests, controlled mutation coverage, and judge documentation.
