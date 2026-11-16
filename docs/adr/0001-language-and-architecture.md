# ADR 0001: Fe-first conformance architecture

- Status: Accepted
- Date: 2026-11-15

## Context

Hashmark must make a meaningful Fe contribution, run equivalent checks on Fe's Sonatina/EVM and native backends, and independently verify native results without reimplementing either hash primitive.

## Decision

Use Fe 26.6.0 for the adapter layer, typed conformance results, deterministic vector generation, reusable streaming checks, backend tests, and native evidence runner. Use CPython 3.15.2 for fixture validation, process orchestration, independent oracles, protocol validation, and deterministic report generation. Use PyCryptodome 4.4.0 only for Ethereum Keccak-256; use `hashlib.sha256` for SHA-256.

The Fe source remains one official-style ingot under `src/`. The default Sonatina backend represents the local EVM target. `DigestCheck` preserves the reference and observed words behind a small reusable API. `conformance::streaming_suite()` is shared by Fe tests and the native runner's self-test mode. The native runner emits a strict line protocol that Python validates before producing evidence.

## Consequences

- Hashmark does not contain a second SHA-256 or Keccak implementation.
- Generated expected digests have one Fe definition consumed by both tests and the native runner.
- The independent oracle is isolated from Fe output values.
- EVM evidence is an aggregate test-run status where the Fe runner cannot expose per-vector values.
- Exact compiler and interpreter versions are enforced outside `fe.toml`, because no verified manifest field pins the compiler.
