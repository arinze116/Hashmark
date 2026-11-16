# Judge demo script

Target duration: 2 minutes 30 seconds. The demo uses no network, wallet, chain, or hosted service.

## 0:00–0:10 — Pitch

Show the README title and say:

> Hashmark makes Fe's built-in SHA-256 and Ethereum Keccak-256 independently verifiable across native and EVM targets.

## 0:10–0:35 — One command

Run on x86-64 Linux:

```console
python -m hashmark run --all --backend all --format all --output-dir reports/demo
```

Point out the exact vector/backend count, target-suite count, native differential comparisons, and report paths.

## 0:35–1:10 — Evidence report

Open `reports/demo/index.html`. Show overall status, the native/EVM target matrix, and the separate SHA-256 and Ethereum Keccak-256 sections.

Expand `sha256-boundary-56` and `keccak256-boundary-136`. Explain that these inputs cross the SHA-256 padding boundary and Keccak rate boundary. Compare expected, Fe, and independent oracle values. Note that EVM records intentionally show aggregate suite evidence rather than a fabricated per-vector digest.

## 1:10–1:40 — Streaming and source traceability

Show the Fe `DigestCheck` API, streaming suite names, and fixture provenance fields. Explain one-shot versus fixed chunks, uneven chunks, zero-length updates, and every two-part split through 140 bytes. On a supported native host, `out/native/hashmark --self-test` runs the same reusable streaming suite directly.

## 1:40–2:15 — Controlled failure

Run:

```console
python scripts/generate_failure_demo.py
```

Open `reports/demo-failure/index.html`. Show that the command exits non-zero, the failure appears before successful evidence, and expected/oracle disagreement is visible. The script mutates only a temporary fixture copy.

## 2:15–2:30 — Close

Show the limitations section and say:

> Hashmark does not claim formal certification. It gives Fe developers deterministic, independently checked evidence they can rerun and extend.

## Fallback

If the live toolchain is unavailable, open the committed passing and controlled-failure reports, then show their JSON, native protocol log, toolchain versions, source revision, and exact reproduction commands. Captured artefacts must match the stated commit and must never be presented as a live run.
