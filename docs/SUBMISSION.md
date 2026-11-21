# Fe Builders Challenge submission draft

This document prepares non-personal submission material. The entrant must verify all declarations and supply the private submission link, contact details, team membership, and legal/payment information.

## Project

- Name: Hashmark
- Tagline: Reproducible cryptographic evidence for Fe
- Repository: https://github.com/arinze116/Hashmark
- Contest: https://fe-lang.org/contest/
- Category fit: cryptography, developer tooling, reusable Fe library

## One-sentence pitch

Hashmark independently verifies Fe's SHA-256 and Ethereum Keccak-256 implementations across native and EVM targets, then turns every test into reproducible evidence.

## Fe-specific highlight

Hashmark directly exercises Fe 26.6.0 `core::hash` one-shot and streaming APIs through a typed `DigestCheck` result. The same generated reference constants and reusable streaming suite run on Sonatina/EVM and native backends, while a strict native protocol exposes exact Fe digests for differential comparison with independent Python references.

Since v1.1.0 the centre of the project is Fe itself: a generated Fe engine evaluates the whole catalogue inside the native program and a hand-written Fe renderer emits the evidence as JSON and Markdown (`HASHMARK/FE-EVIDENCE/1`). Python no longer computes the verdict; it validates the Fe-emitted document fail-closed against the committed fixtures and cross-checks it against the native protocol stream.

## Evidence summary

- 32 committed vectors: 19 SHA-256 and 13 Ethereum Keccak-256.
- Ten shared Fe suites for known answers, boundaries, long messages, chunk partitions, empty updates, and every two-part split through 140 bytes.
- Fe-emitted evidence: `fe-evidence.json` and `fe-report.md` produced by the native Fe program itself, byte-identical across repeated CI runs.
- Independent SHA-256 and Keccak-256 Python oracles.
- Deterministic JSON, Markdown, and offline HTML reports.
- Negative fixture, protocol, mutation, timeout, and report-write tests.
- Pinned clean-checkout CI for x86-64 native and EVM execution.

## Pre-existing work, reused code, and AI disclosure draft

**Pre-existing work:** repository history begins on 15 November 2026, inside the contest build window, and contains no pre-contest source. The entrant must confirm that there is no undisclosed off-repository starting work.

**Reused code and data:** Hashmark copies no cryptographic implementation. It calls Fe `core::hash`, Python `hashlib`, and PyCryptodome. NIST and XKCP materials are used as attributed reference data; generated boundary inputs and the conformance/reporting code are Hashmark work.

**AI assistance:** an autonomous OpenAI coding agent assisted with official-source research, implementation, testing, documentation, and reproducibility work under the project owner's direction. The v1.1.0 Fe-core evidence engine (generated engine, Fe evidence renderer, strict Python validator, and tests) was implemented by Muse (Meta) under the project owner's direction. The entrant must review the submitted code and confirm that they can explain the architecture, evidence model, source provenance, and limitations.

Entrant confirmation required:

- [ ] Accurate team members and responsible contact.
- [ ] Work was completed within the eligible build window.
- [ ] Any pre-existing or reused work is fully disclosed.
- [ ] AI-assistance wording is accepted and accurate.
- [ ] Public repository and licence are correct.

## Published release baseline

- Full `v1.0.0` release and judged commit SHA: `3b5c3a6151b1f3acb1a63bdc09d0e214af80dad0`
- Passing release CI run: https://github.com/arinze116/Hashmark/actions/runs/43757276440
- Release: https://github.com/arinze116/Hashmark/releases/tag/v1.0.0
- Release evidence source revision: `3b5c3a6151b1f3acb1a63bdc09d0e214af80dad0`
- Committed fallback report source revision: `fb45a89f64cbd237e92165029a5aafd2f0f88c0e`
- Passing report: `reports/demo/`
- Controlled failure report: `reports/demo-failure/`
- Demo recording: optional; not yet produced

The final audit may recommend a later commit. Do not submit a later local commit until it is pushed to the public repository and its CI result is verified. The exact recommended candidate is recorded in `docs/FINAL_AUDIT.md`; the v1.0.0 tag must remain on the commit above.

## Fe-core rewrite candidate (v1.1.0)

- Fe-core rewrite commit: `6dd33ada6ca6eaa0bec10f87b289b46ac21c1b7d` (evidence evaluation and rendering moved into Fe).
- Passing CI for that commit: https://github.com/arinze116/Hashmark/actions/runs/44898673751 (all four jobs).
- The submitted commit is the head of branch `submission/hashmark-fe-core-20261121`, which adds this documentation on top of the rewrite commit; its exact SHA is recorded in the owner's submission pack because a document cannot contain its own commit hash. Submit that SHA, not the v1.0.0 tag commit.

## Human-only actions

Register before 18 November 2026, 00:59 WAT using a reachable email. Submit through the private link before 25 November 2026, 00:59 WAT. Do not invent contact, team, eligibility, declaration, payout, or tax details.
