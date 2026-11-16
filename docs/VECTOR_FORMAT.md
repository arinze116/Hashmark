# Vector format

Fixtures are UTF-8 JSON documents under `vectors/sha256/` and `vectors/keccak256/`. Each document contains a schema version and a non-empty `vectors` array.

```json
{
  "schema_version": 1,
  "vectors": [
    {
      "schema_version": 1,
      "id": "sha256-abc",
      "algorithm": "sha256",
      "category": "known_answer",
      "input_hex": "616263",
      "expected_digest_hex": "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
      "input_length_bytes": 3,
      "source_name": "NIST CAVP",
      "source_url": "https://csrc.nist.gov/Projects/cryptographic-algorithm-validation-program/secure-hashing",
      "source_document": "SHA-256 byte-oriented response vectors",
      "source_case_id": "abc",
      "licence_or_usage_note": "Public reference vector for informal verification.",
      "notes": null
    }
  ]
}
```

## Fields

| Field | Rule |
| --- | --- |
| `schema_version` | integer `1` |
| `id` | unique safe ASCII `[a-z0-9][a-z0-9._-]{0,63}` |
| `algorithm` | `sha256` or `keccak256` |
| `category` | `known_answer`, `boundary`, `streaming`, or `long_message` |
| `input_hex` | even-length hexadecimal; normalized to lowercase |
| `expected_digest_hex` | exactly 64 lowercase, unprefixed hexadecimal characters |
| `input_length_bytes` | 0–1,048,576 and equal to decoded input length |
| `source_name` | non-empty, at most 120 characters |
| `source_url` | absolute HTTPS URL |
| `source_document` | non-empty, at most 200 characters |
| `source_case_id` | non-empty, at most 120 characters |
| `licence_or_usage_note` | non-empty, at most 500 characters |
| `notes` | `null` or at most 1,000 characters |

Unknown and missing fields fail validation. IDs must be unique across both algorithm directories. A fixture placed in the wrong directory fails. Documents, vectors, and reports cannot be empty.

## Workflow

```console
python -m hashmark validate-vectors
python scripts/generate_fe_vectors.py
git diff --exit-code -- src/generated_vectors.fe src/native_runner.fe
fe fmt --check
fe test --backend sonatina
fe test --backend native
python -m hashmark run --vector <vector-id> --backend all --format all --output-dir reports/single
```

Do not modify an expected digest to silence a failure. Recheck the authoritative source and independent oracle first.
