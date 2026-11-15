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

Hashmark directly exercises Fe 26.6.0 `core::hash` one-shot and streaming APIs. The same Fe source runs on Sonatina/EVM and native backends, while a strict native protocol exposes exact Fe digests for differential comparison with independent Python references.

## Evidence summary

- 32 committed vectors: 19 SHA-256 and 13 Ethereum Keccak-256.
- Ten shared Fe suites for known answers, boundaries, long messages, chunk partitions, empty updates, and every two-part split through 140 bytes.
- Independent SHA-256 and Keccak-256 Python oracles.
- Deterministic JSON, Markdown, and offline HTML reports.
- Negative fixture, protocol, mutation, timeout, and report-write tests.
- Pinned clean-checkout CI for x86-64 native and EVM execution.

## AI and reused-work disclosure draft

An autonomous OpenAI coding agent assisted with research, implementation, testing, documentation, and reproducibility work under the project owner's direction. The responsible human entrant reviewed the submitted code and can explain the architecture, evidence model, source provenance, and limitations.

Hashmark does not reuse a custom cryptographic implementation. It calls Fe `core::hash`, Python `hashlib`, and PyCryptodome. NIST and XKCP materials are used as attributed reference sources.

Entrant confirmation required:

- [ ] Accurate team members and responsible contact.
- [ ] Work was completed within the eligible build window.
- [ ] Any pre-existing or reused work is fully disclosed.
- [ ] AI-assistance wording is accepted and accurate.
- [ ] Public repository and licence are correct.

## Judged revision

- Full commit SHA: `PENDING_FINAL_COMMIT`
- CI run URL: `PENDING_APPROVED_PUSH`
- Passing report: `reports/demo/`
- Controlled failure report: `reports/demo-failure/`
- Demo recording: optional; not yet produced

## Human-only actions

Register before 18 November 2026, 00:59 WAT using a reachable email. Submit through the private link before 25 November 2026, 00:59 WAT. Do not invent contact, team, eligibility, declaration, payout, or tax details.
