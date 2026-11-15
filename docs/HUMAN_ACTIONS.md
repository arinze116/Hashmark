# Human actions

Hashmark requires no secrets, paid services, blockchain account, or deployment.

## Approval-gated repository actions

- Approve the first push of `feat/hashmark-conformance-lab` to `https://github.com/arinze116/Hashmark`.
- After the x86-64 workflow passes, approve any merge to `main`, `v1.0.0` tag, or GitHub release. No force-push is needed or permitted.
- Download the authoritative CI evidence artefact, place its passing files under `reports/demo/`, and capture the four required real screenshots under `docs/assets/`. These cannot be generated honestly on the ARM64 development host because Fe 26.6.0 cannot execute its nested native test binaries there.

## Required before the registration deadline

- Register **Hashmark** by 18 November 2026, 00:59 WAT (17 November 2026, 23:59 UTC).
- Supply a reachable entrant email, accurate team membership, and the responsible human contact.
- Suggested one-sentence idea: **Hashmark independently verifies Fe's SHA-256 and Ethereum Keccak-256 implementations across native and EVM targets, then turns every test into reproducible evidence.**

## Required before the submission deadline

- Use the private submission link sent to the registered contact.
- Verify the declarations in `docs/SUBMISSION.md`, especially team membership, pre-existing work, reused code, and AI assistance.
- Replace `PENDING_FINAL_COMMIT` and `PENDING_APPROVED_PUSH` in `docs/SUBMISSION.md` with the exact judged commit and passing CI URL.
- Submit the public repository URL and the exact judged commit SHA by 25 November 2026, 00:59 WAT (24 November 2026, 23:59 UTC).

## Only if the project wins

- Provide the organiser with the entrant's own payout address and any required tax/payment information. No address or personal declaration will be invented by the agent.
