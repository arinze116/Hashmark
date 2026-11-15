# Hashmark evidence report — PASS

> Informal conformance evidence only; not formal certification or a security audit.

## Summary

| Total | Passed | Failed | Skipped | Target suites | Differential comparisons |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 64 | 64 | 0 | 0 | 2/2 | 32/32 |

## Target matrix

| Backend | Status | Test identifiers | Diagnostic |
| --- | --- | --- | --- |
| evm | **PASS** | `keccak256_generated_vectors`, `keccak256_known_answers`, `keccak256_streaming_matches_one_shot`, `keccak256_two_part_splits_match_one_shot`, `keccak256_uneven_partition_matches_one_shot`, `sha256_generated_vectors`, `sha256_known_answers`, `sha256_streaming_matches_one_shot`, `sha256_two_part_splits_match_one_shot`, `sha256_uneven_partition_matches_one_shot` | — |
| native | **PASS** | `keccak256_generated_vectors`, `keccak256_known_answers`, `keccak256_streaming_matches_one_shot`, `keccak256_two_part_splits_match_one_shot`, `keccak256_uneven_partition_matches_one_shot`, `sha256_generated_vectors`, `sha256_known_answers`, `sha256_streaming_matches_one_shot`, `sha256_two_part_splits_match_one_shot`, `sha256_uneven_partition_matches_one_shot` | — |
## SHA-256 results

### PASS: `sha256-abc` / evm

- Category: `known_answer`
- Input length: 3 bytes
- Input SHA-256: `ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad`
- Expected: `ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad`
- Fe: `not exposed by EVM runner`
- Oracle: `ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad`
- Evidence basis: `evm_test_status`
- Source: [NIST FIPS 180-4](https://doi.org/10.6028/NIST.FIPS.180-4) — message abc
- Notes: Canonical SHA-256 example.

### PASS: `sha256-abc` / native

- Category: `known_answer`
- Input length: 3 bytes
- Input SHA-256: `ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad`
- Expected: `ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad`
- Fe: `ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad`
- Oracle: `ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad`
- Evidence basis: `native_digest`
- Source: [NIST FIPS 180-4](https://doi.org/10.6028/NIST.FIPS.180-4) — message abc
- Notes: Canonical SHA-256 example.

### PASS: `sha256-boundary-1` / evm

- Category: `boundary`
- Input length: 1 bytes
- Input SHA-256: `4a64a107f0cb32536e5bce6c98c393db21cca7f4ea187ba8c4dca8b51d4ea80a`
- Expected: `4a64a107f0cb32536e5bce6c98c393db21cca7f4ea187ba8c4dca8b51d4ea80a`
- Fe: `not exposed by EVM runner`
- Oracle: `4a64a107f0cb32536e5bce6c98c393db21cca7f4ea187ba8c4dca8b51d4ea80a`
- Evidence basis: `evm_test_status`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=1; block-or-rate=64
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `sha256-boundary-1` / native

- Category: `boundary`
- Input length: 1 bytes
- Input SHA-256: `4a64a107f0cb32536e5bce6c98c393db21cca7f4ea187ba8c4dca8b51d4ea80a`
- Expected: `4a64a107f0cb32536e5bce6c98c393db21cca7f4ea187ba8c4dca8b51d4ea80a`
- Fe: `4a64a107f0cb32536e5bce6c98c393db21cca7f4ea187ba8c4dca8b51d4ea80a`
- Oracle: `4a64a107f0cb32536e5bce6c98c393db21cca7f4ea187ba8c4dca8b51d4ea80a`
- Evidence basis: `native_digest`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=1; block-or-rate=64
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `sha256-boundary-119` / evm

- Category: `boundary`
- Input length: 119 bytes
- Input SHA-256: `3244509f8746f6fb511ca8a72a292a4d7d12e456cce283c03f169dbbcb0d512e`
- Expected: `3244509f8746f6fb511ca8a72a292a4d7d12e456cce283c03f169dbbcb0d512e`
- Fe: `not exposed by EVM runner`
- Oracle: `3244509f8746f6fb511ca8a72a292a4d7d12e456cce283c03f169dbbcb0d512e`
- Evidence basis: `evm_test_status`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=119; block-or-rate=64
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `sha256-boundary-119` / native

- Category: `boundary`
- Input length: 119 bytes
- Input SHA-256: `3244509f8746f6fb511ca8a72a292a4d7d12e456cce283c03f169dbbcb0d512e`
- Expected: `3244509f8746f6fb511ca8a72a292a4d7d12e456cce283c03f169dbbcb0d512e`
- Fe: `3244509f8746f6fb511ca8a72a292a4d7d12e456cce283c03f169dbbcb0d512e`
- Oracle: `3244509f8746f6fb511ca8a72a292a4d7d12e456cce283c03f169dbbcb0d512e`
- Evidence basis: `native_digest`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=119; block-or-rate=64
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `sha256-boundary-120` / evm

- Category: `boundary`
- Input length: 120 bytes
- Input SHA-256: `c5236e50172da3b69c903dcd3b3bb8ce855182f79364d1b59ed36367aa25e468`
- Expected: `c5236e50172da3b69c903dcd3b3bb8ce855182f79364d1b59ed36367aa25e468`
- Fe: `not exposed by EVM runner`
- Oracle: `c5236e50172da3b69c903dcd3b3bb8ce855182f79364d1b59ed36367aa25e468`
- Evidence basis: `evm_test_status`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=120; block-or-rate=64
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `sha256-boundary-120` / native

- Category: `boundary`
- Input length: 120 bytes
- Input SHA-256: `c5236e50172da3b69c903dcd3b3bb8ce855182f79364d1b59ed36367aa25e468`
- Expected: `c5236e50172da3b69c903dcd3b3bb8ce855182f79364d1b59ed36367aa25e468`
- Fe: `c5236e50172da3b69c903dcd3b3bb8ce855182f79364d1b59ed36367aa25e468`
- Oracle: `c5236e50172da3b69c903dcd3b3bb8ce855182f79364d1b59ed36367aa25e468`
- Evidence basis: `native_digest`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=120; block-or-rate=64
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `sha256-boundary-127` / evm

- Category: `boundary`
- Input length: 127 bytes
- Input SHA-256: `b4f5398bf618d741f2ab0f6e2fcde06f4949c20d476b5f6e1d4bf8618bc8973a`
- Expected: `b4f5398bf618d741f2ab0f6e2fcde06f4949c20d476b5f6e1d4bf8618bc8973a`
- Fe: `not exposed by EVM runner`
- Oracle: `b4f5398bf618d741f2ab0f6e2fcde06f4949c20d476b5f6e1d4bf8618bc8973a`
- Evidence basis: `evm_test_status`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=127; block-or-rate=64
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `sha256-boundary-127` / native

- Category: `boundary`
- Input length: 127 bytes
- Input SHA-256: `b4f5398bf618d741f2ab0f6e2fcde06f4949c20d476b5f6e1d4bf8618bc8973a`
- Expected: `b4f5398bf618d741f2ab0f6e2fcde06f4949c20d476b5f6e1d4bf8618bc8973a`
- Fe: `b4f5398bf618d741f2ab0f6e2fcde06f4949c20d476b5f6e1d4bf8618bc8973a`
- Oracle: `b4f5398bf618d741f2ab0f6e2fcde06f4949c20d476b5f6e1d4bf8618bc8973a`
- Evidence basis: `native_digest`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=127; block-or-rate=64
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `sha256-boundary-128` / evm

- Category: `boundary`
- Input length: 128 bytes
- Input SHA-256: `ed045c7c319e0c9286e1dea21c80bfd4a08eca43e02e13ee8a7a2c8b4b2baec9`
- Expected: `ed045c7c319e0c9286e1dea21c80bfd4a08eca43e02e13ee8a7a2c8b4b2baec9`
- Fe: `not exposed by EVM runner`
- Oracle: `ed045c7c319e0c9286e1dea21c80bfd4a08eca43e02e13ee8a7a2c8b4b2baec9`
- Evidence basis: `evm_test_status`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=128; block-or-rate=64
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `sha256-boundary-128` / native

- Category: `boundary`
- Input length: 128 bytes
- Input SHA-256: `ed045c7c319e0c9286e1dea21c80bfd4a08eca43e02e13ee8a7a2c8b4b2baec9`
- Expected: `ed045c7c319e0c9286e1dea21c80bfd4a08eca43e02e13ee8a7a2c8b4b2baec9`
- Fe: `ed045c7c319e0c9286e1dea21c80bfd4a08eca43e02e13ee8a7a2c8b4b2baec9`
- Oracle: `ed045c7c319e0c9286e1dea21c80bfd4a08eca43e02e13ee8a7a2c8b4b2baec9`
- Evidence basis: `native_digest`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=128; block-or-rate=64
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `sha256-boundary-129` / evm

- Category: `boundary`
- Input length: 129 bytes
- Input SHA-256: `d6f2fca0407b3f98c9ce29ae92a6cdf489506450fdbb29172f6b18987bc685db`
- Expected: `d6f2fca0407b3f98c9ce29ae92a6cdf489506450fdbb29172f6b18987bc685db`
- Fe: `not exposed by EVM runner`
- Oracle: `d6f2fca0407b3f98c9ce29ae92a6cdf489506450fdbb29172f6b18987bc685db`
- Evidence basis: `evm_test_status`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=129; block-or-rate=64
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `sha256-boundary-129` / native

- Category: `boundary`
- Input length: 129 bytes
- Input SHA-256: `d6f2fca0407b3f98c9ce29ae92a6cdf489506450fdbb29172f6b18987bc685db`
- Expected: `d6f2fca0407b3f98c9ce29ae92a6cdf489506450fdbb29172f6b18987bc685db`
- Fe: `d6f2fca0407b3f98c9ce29ae92a6cdf489506450fdbb29172f6b18987bc685db`
- Oracle: `d6f2fca0407b3f98c9ce29ae92a6cdf489506450fdbb29172f6b18987bc685db`
- Evidence basis: `native_digest`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=129; block-or-rate=64
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `sha256-boundary-2` / evm

- Category: `boundary`
- Input length: 2 bytes
- Input SHA-256: `b27fc04e05a940672b77fb0d1aaf6a1f6e3675603da78e6791a66b6523c46fd4`
- Expected: `b27fc04e05a940672b77fb0d1aaf6a1f6e3675603da78e6791a66b6523c46fd4`
- Fe: `not exposed by EVM runner`
- Oracle: `b27fc04e05a940672b77fb0d1aaf6a1f6e3675603da78e6791a66b6523c46fd4`
- Evidence basis: `evm_test_status`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=2; block-or-rate=64
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `sha256-boundary-2` / native

- Category: `boundary`
- Input length: 2 bytes
- Input SHA-256: `b27fc04e05a940672b77fb0d1aaf6a1f6e3675603da78e6791a66b6523c46fd4`
- Expected: `b27fc04e05a940672b77fb0d1aaf6a1f6e3675603da78e6791a66b6523c46fd4`
- Fe: `b27fc04e05a940672b77fb0d1aaf6a1f6e3675603da78e6791a66b6523c46fd4`
- Oracle: `b27fc04e05a940672b77fb0d1aaf6a1f6e3675603da78e6791a66b6523c46fd4`
- Evidence basis: `native_digest`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=2; block-or-rate=64
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `sha256-boundary-3` / evm

- Category: `boundary`
- Input length: 3 bytes
- Input SHA-256: `abf0f7ab4223b86bbafb06e42d0caf0e889d27619b946d440a128bb405b7c5a3`
- Expected: `abf0f7ab4223b86bbafb06e42d0caf0e889d27619b946d440a128bb405b7c5a3`
- Fe: `not exposed by EVM runner`
- Oracle: `abf0f7ab4223b86bbafb06e42d0caf0e889d27619b946d440a128bb405b7c5a3`
- Evidence basis: `evm_test_status`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=3; block-or-rate=64
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `sha256-boundary-3` / native

- Category: `boundary`
- Input length: 3 bytes
- Input SHA-256: `abf0f7ab4223b86bbafb06e42d0caf0e889d27619b946d440a128bb405b7c5a3`
- Expected: `abf0f7ab4223b86bbafb06e42d0caf0e889d27619b946d440a128bb405b7c5a3`
- Fe: `abf0f7ab4223b86bbafb06e42d0caf0e889d27619b946d440a128bb405b7c5a3`
- Oracle: `abf0f7ab4223b86bbafb06e42d0caf0e889d27619b946d440a128bb405b7c5a3`
- Evidence basis: `native_digest`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=3; block-or-rate=64
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `sha256-boundary-55` / evm

- Category: `boundary`
- Input length: 55 bytes
- Input SHA-256: `59aaae80b8e7958f5757b4ac9274f1fd57ec0dc7aa8349319102316781b92006`
- Expected: `59aaae80b8e7958f5757b4ac9274f1fd57ec0dc7aa8349319102316781b92006`
- Fe: `not exposed by EVM runner`
- Oracle: `59aaae80b8e7958f5757b4ac9274f1fd57ec0dc7aa8349319102316781b92006`
- Evidence basis: `evm_test_status`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=55; block-or-rate=64
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `sha256-boundary-55` / native

- Category: `boundary`
- Input length: 55 bytes
- Input SHA-256: `59aaae80b8e7958f5757b4ac9274f1fd57ec0dc7aa8349319102316781b92006`
- Expected: `59aaae80b8e7958f5757b4ac9274f1fd57ec0dc7aa8349319102316781b92006`
- Fe: `59aaae80b8e7958f5757b4ac9274f1fd57ec0dc7aa8349319102316781b92006`
- Oracle: `59aaae80b8e7958f5757b4ac9274f1fd57ec0dc7aa8349319102316781b92006`
- Evidence basis: `native_digest`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=55; block-or-rate=64
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `sha256-boundary-56` / evm

- Category: `boundary`
- Input length: 56 bytes
- Input SHA-256: `dca902d31487ffab357ce36cc5abc6947fbb69127ec04c468ba5687268c4bf7c`
- Expected: `dca902d31487ffab357ce36cc5abc6947fbb69127ec04c468ba5687268c4bf7c`
- Fe: `not exposed by EVM runner`
- Oracle: `dca902d31487ffab357ce36cc5abc6947fbb69127ec04c468ba5687268c4bf7c`
- Evidence basis: `evm_test_status`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=56; block-or-rate=64
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `sha256-boundary-56` / native

- Category: `boundary`
- Input length: 56 bytes
- Input SHA-256: `dca902d31487ffab357ce36cc5abc6947fbb69127ec04c468ba5687268c4bf7c`
- Expected: `dca902d31487ffab357ce36cc5abc6947fbb69127ec04c468ba5687268c4bf7c`
- Fe: `dca902d31487ffab357ce36cc5abc6947fbb69127ec04c468ba5687268c4bf7c`
- Oracle: `dca902d31487ffab357ce36cc5abc6947fbb69127ec04c468ba5687268c4bf7c`
- Evidence basis: `native_digest`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=56; block-or-rate=64
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `sha256-boundary-57` / evm

- Category: `boundary`
- Input length: 57 bytes
- Input SHA-256: `ca0042f1f8b6a02ba5a30af121a9b69daa34b07bb22b2b320c05abe21df875a0`
- Expected: `ca0042f1f8b6a02ba5a30af121a9b69daa34b07bb22b2b320c05abe21df875a0`
- Fe: `not exposed by EVM runner`
- Oracle: `ca0042f1f8b6a02ba5a30af121a9b69daa34b07bb22b2b320c05abe21df875a0`
- Evidence basis: `evm_test_status`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=57; block-or-rate=64
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `sha256-boundary-57` / native

- Category: `boundary`
- Input length: 57 bytes
- Input SHA-256: `ca0042f1f8b6a02ba5a30af121a9b69daa34b07bb22b2b320c05abe21df875a0`
- Expected: `ca0042f1f8b6a02ba5a30af121a9b69daa34b07bb22b2b320c05abe21df875a0`
- Fe: `ca0042f1f8b6a02ba5a30af121a9b69daa34b07bb22b2b320c05abe21df875a0`
- Oracle: `ca0042f1f8b6a02ba5a30af121a9b69daa34b07bb22b2b320c05abe21df875a0`
- Evidence basis: `native_digest`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=57; block-or-rate=64
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `sha256-boundary-63` / evm

- Category: `boundary`
- Input length: 63 bytes
- Input SHA-256: `b8e655e9e7ad413b96f0a371eb1d6db71dcca27f4eee35892517cbe4bfaa6f9a`
- Expected: `b8e655e9e7ad413b96f0a371eb1d6db71dcca27f4eee35892517cbe4bfaa6f9a`
- Fe: `not exposed by EVM runner`
- Oracle: `b8e655e9e7ad413b96f0a371eb1d6db71dcca27f4eee35892517cbe4bfaa6f9a`
- Evidence basis: `evm_test_status`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=63; block-or-rate=64
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `sha256-boundary-63` / native

- Category: `boundary`
- Input length: 63 bytes
- Input SHA-256: `b8e655e9e7ad413b96f0a371eb1d6db71dcca27f4eee35892517cbe4bfaa6f9a`
- Expected: `b8e655e9e7ad413b96f0a371eb1d6db71dcca27f4eee35892517cbe4bfaa6f9a`
- Fe: `b8e655e9e7ad413b96f0a371eb1d6db71dcca27f4eee35892517cbe4bfaa6f9a`
- Oracle: `b8e655e9e7ad413b96f0a371eb1d6db71dcca27f4eee35892517cbe4bfaa6f9a`
- Evidence basis: `native_digest`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=63; block-or-rate=64
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `sha256-boundary-64` / evm

- Category: `boundary`
- Input length: 64 bytes
- Input SHA-256: `e5146be62accc56709594cb45c651b361df94f622cbb09b91ea3ca7a2060bd53`
- Expected: `e5146be62accc56709594cb45c651b361df94f622cbb09b91ea3ca7a2060bd53`
- Fe: `not exposed by EVM runner`
- Oracle: `e5146be62accc56709594cb45c651b361df94f622cbb09b91ea3ca7a2060bd53`
- Evidence basis: `evm_test_status`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=64; block-or-rate=64
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `sha256-boundary-64` / native

- Category: `boundary`
- Input length: 64 bytes
- Input SHA-256: `e5146be62accc56709594cb45c651b361df94f622cbb09b91ea3ca7a2060bd53`
- Expected: `e5146be62accc56709594cb45c651b361df94f622cbb09b91ea3ca7a2060bd53`
- Fe: `e5146be62accc56709594cb45c651b361df94f622cbb09b91ea3ca7a2060bd53`
- Oracle: `e5146be62accc56709594cb45c651b361df94f622cbb09b91ea3ca7a2060bd53`
- Evidence basis: `native_digest`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=64; block-or-rate=64
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `sha256-boundary-65` / evm

- Category: `boundary`
- Input length: 65 bytes
- Input SHA-256: `4b6c6774f0cbcd776a90e187b9494e04ca880c0afe3ea1c5cad51c8bbcb41f74`
- Expected: `4b6c6774f0cbcd776a90e187b9494e04ca880c0afe3ea1c5cad51c8bbcb41f74`
- Fe: `not exposed by EVM runner`
- Oracle: `4b6c6774f0cbcd776a90e187b9494e04ca880c0afe3ea1c5cad51c8bbcb41f74`
- Evidence basis: `evm_test_status`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=65; block-or-rate=64
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `sha256-boundary-65` / native

- Category: `boundary`
- Input length: 65 bytes
- Input SHA-256: `4b6c6774f0cbcd776a90e187b9494e04ca880c0afe3ea1c5cad51c8bbcb41f74`
- Expected: `4b6c6774f0cbcd776a90e187b9494e04ca880c0afe3ea1c5cad51c8bbcb41f74`
- Fe: `4b6c6774f0cbcd776a90e187b9494e04ca880c0afe3ea1c5cad51c8bbcb41f74`
- Oracle: `4b6c6774f0cbcd776a90e187b9494e04ca880c0afe3ea1c5cad51c8bbcb41f74`
- Evidence basis: `native_digest`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=65; block-or-rate=64
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `sha256-empty` / evm

- Category: `known_answer`
- Input length: 0 bytes
- Input SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Expected: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Fe: `not exposed by EVM runner`
- Oracle: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Evidence basis: `evm_test_status`
- Source: [NIST CAVP](https://csrc.nist.gov/CSRC/media/Projects/Cryptographic-Algorithm-Validation-Program/documents/shs/shabytetestvectors.zip) — Len = 0
- Notes: FIPS 180-4 SHA-256 empty-message response vector.

### PASS: `sha256-empty` / native

- Category: `known_answer`
- Input length: 0 bytes
- Input SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Expected: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Fe: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Oracle: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Evidence basis: `native_digest`
- Source: [NIST CAVP](https://csrc.nist.gov/CSRC/media/Projects/Cryptographic-Algorithm-Validation-Program/documents/shs/shabytetestvectors.zip) — Len = 0
- Notes: FIPS 180-4 SHA-256 empty-message response vector.

### PASS: `sha256-long-1k` / evm

- Category: `long_message`
- Input length: 1024 bytes
- Input SHA-256: `575383deff0775797e1ff4c82da069141937c843a81cbe50959a96bcfa88140e`
- Expected: `575383deff0775797e1ff4c82da069141937c843a81cbe50959a96bcfa88140e`
- Fe: `not exposed by EVM runner`
- Oracle: `575383deff0775797e1ff4c82da069141937c843a81cbe50959a96bcfa88140e`
- Evidence basis: `evm_test_status`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=1024; block-or-rate=64
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `sha256-long-1k` / native

- Category: `long_message`
- Input length: 1024 bytes
- Input SHA-256: `575383deff0775797e1ff4c82da069141937c843a81cbe50959a96bcfa88140e`
- Expected: `575383deff0775797e1ff4c82da069141937c843a81cbe50959a96bcfa88140e`
- Fe: `575383deff0775797e1ff4c82da069141937c843a81cbe50959a96bcfa88140e`
- Oracle: `575383deff0775797e1ff4c82da069141937c843a81cbe50959a96bcfa88140e`
- Evidence basis: `native_digest`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=1024; block-or-rate=64
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `sha256-long-64k` / evm

- Category: `long_message`
- Input length: 65536 bytes
- Input SHA-256: `d8f32a3b4c195f65444e342b0c61bdaf114802e84ab7821a1f88e3f66ea15100`
- Expected: `d8f32a3b4c195f65444e342b0c61bdaf114802e84ab7821a1f88e3f66ea15100`
- Fe: `not exposed by EVM runner`
- Oracle: `d8f32a3b4c195f65444e342b0c61bdaf114802e84ab7821a1f88e3f66ea15100`
- Evidence basis: `evm_test_status`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=65536; block-or-rate=64
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `sha256-long-64k` / native

- Category: `long_message`
- Input length: 65536 bytes
- Input SHA-256: `d8f32a3b4c195f65444e342b0c61bdaf114802e84ab7821a1f88e3f66ea15100`
- Expected: `d8f32a3b4c195f65444e342b0c61bdaf114802e84ab7821a1f88e3f66ea15100`
- Fe: `d8f32a3b4c195f65444e342b0c61bdaf114802e84ab7821a1f88e3f66ea15100`
- Oracle: `d8f32a3b4c195f65444e342b0c61bdaf114802e84ab7821a1f88e3f66ea15100`
- Evidence basis: `native_digest`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=65536; block-or-rate=64
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `sha256-nist-short-d3` / evm

- Category: `known_answer`
- Input length: 1 bytes
- Input SHA-256: `28969cdfa74a12c82f3bad960b0b000aca2ac329deea5c2328ebc6f2ba9802c1`
- Expected: `28969cdfa74a12c82f3bad960b0b000aca2ac329deea5c2328ebc6f2ba9802c1`
- Fe: `not exposed by EVM runner`
- Oracle: `28969cdfa74a12c82f3bad960b0b000aca2ac329deea5c2328ebc6f2ba9802c1`
- Evidence basis: `evm_test_status`
- Source: [NIST CAVP](https://csrc.nist.gov/CSRC/media/Projects/Cryptographic-Algorithm-Validation-Program/documents/shs/shabytetestvectors.zip) — Len = 8; Msg = d3
- Notes: Selected byte-oriented NIST short-message vector.

### PASS: `sha256-nist-short-d3` / native

- Category: `known_answer`
- Input length: 1 bytes
- Input SHA-256: `28969cdfa74a12c82f3bad960b0b000aca2ac329deea5c2328ebc6f2ba9802c1`
- Expected: `28969cdfa74a12c82f3bad960b0b000aca2ac329deea5c2328ebc6f2ba9802c1`
- Fe: `28969cdfa74a12c82f3bad960b0b000aca2ac329deea5c2328ebc6f2ba9802c1`
- Oracle: `28969cdfa74a12c82f3bad960b0b000aca2ac329deea5c2328ebc6f2ba9802c1`
- Evidence basis: `native_digest`
- Source: [NIST CAVP](https://csrc.nist.gov/CSRC/media/Projects/Cryptographic-Algorithm-Validation-Program/documents/shs/shabytetestvectors.zip) — Len = 8; Msg = d3
- Notes: Selected byte-oriented NIST short-message vector.

## Ethereum Keccak-256 results

### PASS: `keccak256-abc` / evm

- Category: `known_answer`
- Input length: 3 bytes
- Input SHA-256: `ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad`
- Expected: `4e03657aea45a94fc7d47ba826c8d667c0d1e6e33a64a036ec44f58fa12d6c45`
- Fe: `not exposed by EVM runner`
- Oracle: `4e03657aea45a94fc7d47ba826c8d667c0d1e6e33a64a036ec44f58fa12d6c45`
- Evidence basis: `evm_test_status`
- Source: [Keccak Team / XKCP](https://github.com/XKCP/XKCP) — --ethereum over abc
- Notes: Cross-checked with XKCP commit d20c8fcaecc543f816a0721d0dfc13b4cf27c14d.

### PASS: `keccak256-abc` / native

- Category: `known_answer`
- Input length: 3 bytes
- Input SHA-256: `ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad`
- Expected: `4e03657aea45a94fc7d47ba826c8d667c0d1e6e33a64a036ec44f58fa12d6c45`
- Fe: `4e03657aea45a94fc7d47ba826c8d667c0d1e6e33a64a036ec44f58fa12d6c45`
- Oracle: `4e03657aea45a94fc7d47ba826c8d667c0d1e6e33a64a036ec44f58fa12d6c45`
- Evidence basis: `native_digest`
- Source: [Keccak Team / XKCP](https://github.com/XKCP/XKCP) — --ethereum over abc
- Notes: Cross-checked with XKCP commit d20c8fcaecc543f816a0721d0dfc13b4cf27c14d.

### PASS: `keccak256-boundary-1` / evm

- Category: `boundary`
- Input length: 1 bytes
- Input SHA-256: `4a64a107f0cb32536e5bce6c98c393db21cca7f4ea187ba8c4dca8b51d4ea80a`
- Expected: `0552ab8dc52e1cf9328ddb97e0966b9c88de9cca97f48b0110d7800982596158`
- Fe: `not exposed by EVM runner`
- Oracle: `0552ab8dc52e1cf9328ddb97e0966b9c88de9cca97f48b0110d7800982596158`
- Evidence basis: `evm_test_status`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=1; block-or-rate=136
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `keccak256-boundary-1` / native

- Category: `boundary`
- Input length: 1 bytes
- Input SHA-256: `4a64a107f0cb32536e5bce6c98c393db21cca7f4ea187ba8c4dca8b51d4ea80a`
- Expected: `0552ab8dc52e1cf9328ddb97e0966b9c88de9cca97f48b0110d7800982596158`
- Fe: `0552ab8dc52e1cf9328ddb97e0966b9c88de9cca97f48b0110d7800982596158`
- Oracle: `0552ab8dc52e1cf9328ddb97e0966b9c88de9cca97f48b0110d7800982596158`
- Evidence basis: `native_digest`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=1; block-or-rate=136
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `keccak256-boundary-135` / evm

- Category: `boundary`
- Input length: 135 bytes
- Input SHA-256: `0037dd589349fd42056bf9487b07db552bd78ef4e156e8ca0dd3428b86415f07`
- Expected: `37842a4806a4a3d4eaa4a1789235a5b66b5d1901bf8388cfc1a599b2286cb56f`
- Fe: `not exposed by EVM runner`
- Oracle: `37842a4806a4a3d4eaa4a1789235a5b66b5d1901bf8388cfc1a599b2286cb56f`
- Evidence basis: `evm_test_status`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=135; block-or-rate=136
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `keccak256-boundary-135` / native

- Category: `boundary`
- Input length: 135 bytes
- Input SHA-256: `0037dd589349fd42056bf9487b07db552bd78ef4e156e8ca0dd3428b86415f07`
- Expected: `37842a4806a4a3d4eaa4a1789235a5b66b5d1901bf8388cfc1a599b2286cb56f`
- Fe: `37842a4806a4a3d4eaa4a1789235a5b66b5d1901bf8388cfc1a599b2286cb56f`
- Oracle: `37842a4806a4a3d4eaa4a1789235a5b66b5d1901bf8388cfc1a599b2286cb56f`
- Evidence basis: `native_digest`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=135; block-or-rate=136
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `keccak256-boundary-136` / evm

- Category: `boundary`
- Input length: 136 bytes
- Input SHA-256: `e5e4c62fb9786988e90a6cc91698b3b9e3a2179ebae3466674800da4a9d7d70b`
- Expected: `317e60199b8b3851917e74926b7690d755cd27cd50c4a5abb3075fe252b6de55`
- Fe: `not exposed by EVM runner`
- Oracle: `317e60199b8b3851917e74926b7690d755cd27cd50c4a5abb3075fe252b6de55`
- Evidence basis: `evm_test_status`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=136; block-or-rate=136
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `keccak256-boundary-136` / native

- Category: `boundary`
- Input length: 136 bytes
- Input SHA-256: `e5e4c62fb9786988e90a6cc91698b3b9e3a2179ebae3466674800da4a9d7d70b`
- Expected: `317e60199b8b3851917e74926b7690d755cd27cd50c4a5abb3075fe252b6de55`
- Fe: `317e60199b8b3851917e74926b7690d755cd27cd50c4a5abb3075fe252b6de55`
- Oracle: `317e60199b8b3851917e74926b7690d755cd27cd50c4a5abb3075fe252b6de55`
- Evidence basis: `native_digest`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=136; block-or-rate=136
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `keccak256-boundary-137` / evm

- Category: `boundary`
- Input length: 137 bytes
- Input SHA-256: `bf66a13e68481fcf295ae3ad83da398687ae3ffabdd3e0ff09e8440ba83a1442`
- Expected: `4f17b9c92046ceb9694fbe867db52a6d0672ce2c2c720803be77258c62107c54`
- Fe: `not exposed by EVM runner`
- Oracle: `4f17b9c92046ceb9694fbe867db52a6d0672ce2c2c720803be77258c62107c54`
- Evidence basis: `evm_test_status`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=137; block-or-rate=136
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `keccak256-boundary-137` / native

- Category: `boundary`
- Input length: 137 bytes
- Input SHA-256: `bf66a13e68481fcf295ae3ad83da398687ae3ffabdd3e0ff09e8440ba83a1442`
- Expected: `4f17b9c92046ceb9694fbe867db52a6d0672ce2c2c720803be77258c62107c54`
- Fe: `4f17b9c92046ceb9694fbe867db52a6d0672ce2c2c720803be77258c62107c54`
- Oracle: `4f17b9c92046ceb9694fbe867db52a6d0672ce2c2c720803be77258c62107c54`
- Evidence basis: `native_digest`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=137; block-or-rate=136
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `keccak256-boundary-2` / evm

- Category: `boundary`
- Input length: 2 bytes
- Input SHA-256: `b27fc04e05a940672b77fb0d1aaf6a1f6e3675603da78e6791a66b6523c46fd4`
- Expected: `4010befd47b38289f2a4da8fd1ad3af0bc5fe286d9c9616d99534a04bac339ed`
- Fe: `not exposed by EVM runner`
- Oracle: `4010befd47b38289f2a4da8fd1ad3af0bc5fe286d9c9616d99534a04bac339ed`
- Evidence basis: `evm_test_status`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=2; block-or-rate=136
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `keccak256-boundary-2` / native

- Category: `boundary`
- Input length: 2 bytes
- Input SHA-256: `b27fc04e05a940672b77fb0d1aaf6a1f6e3675603da78e6791a66b6523c46fd4`
- Expected: `4010befd47b38289f2a4da8fd1ad3af0bc5fe286d9c9616d99534a04bac339ed`
- Fe: `4010befd47b38289f2a4da8fd1ad3af0bc5fe286d9c9616d99534a04bac339ed`
- Oracle: `4010befd47b38289f2a4da8fd1ad3af0bc5fe286d9c9616d99534a04bac339ed`
- Evidence basis: `native_digest`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=2; block-or-rate=136
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `keccak256-boundary-271` / evm

- Category: `boundary`
- Input length: 271 bytes
- Input SHA-256: `617d57683c54eed9607a39ed57f35058545b34da428144723046842890d7d443`
- Expected: `cdf35022e028099c49c1373cd7375ef6fc6bb9d927250f1b1f739190dbd30c6f`
- Fe: `not exposed by EVM runner`
- Oracle: `cdf35022e028099c49c1373cd7375ef6fc6bb9d927250f1b1f739190dbd30c6f`
- Evidence basis: `evm_test_status`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=271; block-or-rate=136
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `keccak256-boundary-271` / native

- Category: `boundary`
- Input length: 271 bytes
- Input SHA-256: `617d57683c54eed9607a39ed57f35058545b34da428144723046842890d7d443`
- Expected: `cdf35022e028099c49c1373cd7375ef6fc6bb9d927250f1b1f739190dbd30c6f`
- Fe: `cdf35022e028099c49c1373cd7375ef6fc6bb9d927250f1b1f739190dbd30c6f`
- Oracle: `cdf35022e028099c49c1373cd7375ef6fc6bb9d927250f1b1f739190dbd30c6f`
- Evidence basis: `native_digest`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=271; block-or-rate=136
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `keccak256-boundary-272` / evm

- Category: `boundary`
- Input length: 272 bytes
- Input SHA-256: `3aae5b6939acb26387e1d10ff54a22eabd869108d76d3c00ec776233f05a60e9`
- Expected: `2fe8d923d96d25f4f3edf77eadcae30e130c0bbe5cfb7771c74306c5dc2bd7d3`
- Fe: `not exposed by EVM runner`
- Oracle: `2fe8d923d96d25f4f3edf77eadcae30e130c0bbe5cfb7771c74306c5dc2bd7d3`
- Evidence basis: `evm_test_status`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=272; block-or-rate=136
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `keccak256-boundary-272` / native

- Category: `boundary`
- Input length: 272 bytes
- Input SHA-256: `3aae5b6939acb26387e1d10ff54a22eabd869108d76d3c00ec776233f05a60e9`
- Expected: `2fe8d923d96d25f4f3edf77eadcae30e130c0bbe5cfb7771c74306c5dc2bd7d3`
- Fe: `2fe8d923d96d25f4f3edf77eadcae30e130c0bbe5cfb7771c74306c5dc2bd7d3`
- Oracle: `2fe8d923d96d25f4f3edf77eadcae30e130c0bbe5cfb7771c74306c5dc2bd7d3`
- Evidence basis: `native_digest`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=272; block-or-rate=136
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `keccak256-boundary-273` / evm

- Category: `boundary`
- Input length: 273 bytes
- Input SHA-256: `5945a073804ecb5e7fe7d9044bd9ac6e61fdc73d522678587063aade92512067`
- Expected: `327d102dcc70d465cd1ae7423e322c01e0efa34888f7e19311a4f4425bf38d6d`
- Fe: `not exposed by EVM runner`
- Oracle: `327d102dcc70d465cd1ae7423e322c01e0efa34888f7e19311a4f4425bf38d6d`
- Evidence basis: `evm_test_status`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=273; block-or-rate=136
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `keccak256-boundary-273` / native

- Category: `boundary`
- Input length: 273 bytes
- Input SHA-256: `5945a073804ecb5e7fe7d9044bd9ac6e61fdc73d522678587063aade92512067`
- Expected: `327d102dcc70d465cd1ae7423e322c01e0efa34888f7e19311a4f4425bf38d6d`
- Fe: `327d102dcc70d465cd1ae7423e322c01e0efa34888f7e19311a4f4425bf38d6d`
- Oracle: `327d102dcc70d465cd1ae7423e322c01e0efa34888f7e19311a4f4425bf38d6d`
- Evidence basis: `native_digest`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=273; block-or-rate=136
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `keccak256-boundary-3` / evm

- Category: `boundary`
- Input length: 3 bytes
- Input SHA-256: `abf0f7ab4223b86bbafb06e42d0caf0e889d27619b946d440a128bb405b7c5a3`
- Expected: `e239c45a6a249ef578a6e4c732fcf24d94d453c6b84f9db4f3d1decd03dcd6ab`
- Fe: `not exposed by EVM runner`
- Oracle: `e239c45a6a249ef578a6e4c732fcf24d94d453c6b84f9db4f3d1decd03dcd6ab`
- Evidence basis: `evm_test_status`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=3; block-or-rate=136
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `keccak256-boundary-3` / native

- Category: `boundary`
- Input length: 3 bytes
- Input SHA-256: `abf0f7ab4223b86bbafb06e42d0caf0e889d27619b946d440a128bb405b7c5a3`
- Expected: `e239c45a6a249ef578a6e4c732fcf24d94d453c6b84f9db4f3d1decd03dcd6ab`
- Fe: `e239c45a6a249ef578a6e4c732fcf24d94d453c6b84f9db4f3d1decd03dcd6ab`
- Oracle: `e239c45a6a249ef578a6e4c732fcf24d94d453c6b84f9db4f3d1decd03dcd6ab`
- Evidence basis: `native_digest`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=3; block-or-rate=136
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `keccak256-empty` / evm

- Category: `known_answer`
- Input length: 0 bytes
- Input SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Expected: `c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470`
- Fe: `not exposed by EVM runner`
- Oracle: `c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470`
- Evidence basis: `evm_test_status`
- Source: [Keccak Team / XKCP](https://github.com/XKCP/XKCP) — --ethereum over empty input
- Notes: Cross-checked with XKCP commit d20c8fcaecc543f816a0721d0dfc13b4cf27c14d.

### PASS: `keccak256-empty` / native

- Category: `known_answer`
- Input length: 0 bytes
- Input SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Expected: `c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470`
- Fe: `c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470`
- Oracle: `c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470`
- Evidence basis: `native_digest`
- Source: [Keccak Team / XKCP](https://github.com/XKCP/XKCP) — --ethereum over empty input
- Notes: Cross-checked with XKCP commit d20c8fcaecc543f816a0721d0dfc13b4cf27c14d.

### PASS: `keccak256-long-1k` / evm

- Category: `long_message`
- Input length: 1024 bytes
- Input SHA-256: `575383deff0775797e1ff4c82da069141937c843a81cbe50959a96bcfa88140e`
- Expected: `2f5106d246674d98b6ae93d84eb96a4cae92dd057c3d3fcb7d30b060db675c87`
- Fe: `not exposed by EVM runner`
- Oracle: `2f5106d246674d98b6ae93d84eb96a4cae92dd057c3d3fcb7d30b060db675c87`
- Evidence basis: `evm_test_status`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=1024; block-or-rate=136
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `keccak256-long-1k` / native

- Category: `long_message`
- Input length: 1024 bytes
- Input SHA-256: `575383deff0775797e1ff4c82da069141937c843a81cbe50959a96bcfa88140e`
- Expected: `2f5106d246674d98b6ae93d84eb96a4cae92dd057c3d3fcb7d30b060db675c87`
- Fe: `2f5106d246674d98b6ae93d84eb96a4cae92dd057c3d3fcb7d30b060db675c87`
- Oracle: `2f5106d246674d98b6ae93d84eb96a4cae92dd057c3d3fcb7d30b060db675c87`
- Evidence basis: `native_digest`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=1024; block-or-rate=136
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `keccak256-long-64k` / evm

- Category: `long_message`
- Input length: 65536 bytes
- Input SHA-256: `d8f32a3b4c195f65444e342b0c61bdaf114802e84ab7821a1f88e3f66ea15100`
- Expected: `c8d035295f3de4cd6eb96b194331b5a9b49edad223dc82c51bd5e8130163254b`
- Fe: `not exposed by EVM runner`
- Oracle: `c8d035295f3de4cd6eb96b194331b5a9b49edad223dc82c51bd5e8130163254b`
- Evidence basis: `evm_test_status`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=65536; block-or-rate=136
- Notes: byte[i] = (i * 131 + 17) mod 256

### PASS: `keccak256-long-64k` / native

- Category: `long_message`
- Input length: 65536 bytes
- Input SHA-256: `d8f32a3b4c195f65444e342b0c61bdaf114802e84ab7821a1f88e3f66ea15100`
- Expected: `c8d035295f3de4cd6eb96b194331b5a9b49edad223dc82c51bd5e8130163254b`
- Fe: `c8d035295f3de4cd6eb96b194331b5a9b49edad223dc82c51bd5e8130163254b`
- Oracle: `c8d035295f3de4cd6eb96b194331b5a9b49edad223dc82c51bd5e8130163254b`
- Evidence basis: `native_digest`
- Source: [Hashmark deterministic boundary generator](https://github.com/arinze116/Hashmark/blob/main/docs/VECTOR_FORMAT.md) — length=65536; block-or-rate=136
- Notes: byte[i] = (i * 131 + 17) mod 256

## Provenance

- Source revision: `fb45a89f64cbd237e92165029a5aafd2f0f88c0e`
- Source tree SHA-256: `c119a58f8fd3319d70fd6b7fe70ba08d643882291fc446d94fbf51c6f0baeadf`
- Fixture manifest SHA-256: `ca87eb6406a88008c7224cf14ca8f1ba5a522b371c7fcd9ecb59a8d7eef00804`
- Fe: `fe 26.6.0 (5b3f96a)`
- Python: `3.15.2`
- PyCryptodome: `4.4.0`
- Report schema: `1`

## Limitations

- Informal conformance testing only; this is not formal NIST CAVP validation or certification.
- Passing vectors are not a security audit, proof of cryptographic security, or exhaustive testing.
- Fe 26.6.0 is not production-ready; Hashmark records observed behavior for this pinned compiler.
- The Fe EVM test runner exposes test status and identifiers, not per-vector runtime digest output.

## Reproduce

```console
python -m hashmark run --all --backend all --format all --output-dir reports/local
```
