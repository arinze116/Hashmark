from __future__ import annotations

import unittest

from hashmark.protocol import ProtocolError, parse_protocol

RECORD = (
    "HASHMARK/1\tsha256-abc\tsha256\t3\t"
    "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    "\tnative\tpass\n"
)
SUMMARY = "HASHMARK/1\tSUMMARY\t1\t1\t0\n"


class ProtocolTests(unittest.TestCase):
    def test_valid_stream(self) -> None:
        run = parse_protocol((RECORD + SUMMARY).encode(), {"sha256-abc"})
        self.assertEqual(run.summary.passed, 1)
        self.assertEqual(run.records[0].vector_id, "sha256-abc")

    def test_truncated_stream_is_rejected(self) -> None:
        with self.assertRaisesRegex(ProtocolError, "truncated"):
            parse_protocol((RECORD + SUMMARY).encode()[:-1])

    def test_duplicate_result_is_rejected(self) -> None:
        stream = (RECORD + RECORD + "HASHMARK/1\tSUMMARY\t2\t2\t0\n").encode()
        with self.assertRaisesRegex(ProtocolError, "duplicate native result"):
            parse_protocol(stream)

    def test_missing_result_is_rejected(self) -> None:
        with self.assertRaisesRegex(ProtocolError, "result set mismatch"):
            parse_protocol((RECORD + SUMMARY).encode(), {"sha256-abc", "sha256-empty"})

    def test_unknown_protocol_version_is_rejected(self) -> None:
        stream = (RECORD + SUMMARY).replace("HASHMARK/1", "HASHMARK/2").encode()
        with self.assertRaisesRegex(ProtocolError, "unknown protocol prefix"):
            parse_protocol(stream)

    def test_bad_digest_is_rejected(self) -> None:
        stream = (RECORD.replace("ba7816", "zz7816") + SUMMARY).encode()
        with self.assertRaisesRegex(ProtocolError, "invalid digest"):
            parse_protocol(stream)

    def test_bad_backend_is_rejected(self) -> None:
        stream = (RECORD.replace("\tnative\t", "\tevm\t") + SUMMARY).encode()
        with self.assertRaisesRegex(ProtocolError, "invalid backend"):
            parse_protocol(stream)

    def test_inconsistent_summary_is_rejected(self) -> None:
        with self.assertRaisesRegex(ProtocolError, "summary does not match"):
            parse_protocol((RECORD + "HASHMARK/1\tSUMMARY\t1\t0\t1\n").encode())

    def test_unknown_algorithm_is_rejected(self) -> None:
        stream = (RECORD.replace("\tsha256\t", "\tsha3\t") + SUMMARY).encode()
        with self.assertRaisesRegex(ProtocolError, "unknown algorithm"):
            parse_protocol(stream)

    def test_invalid_integer_is_rejected(self) -> None:
        stream = (RECORD.replace("\t3\t", "\t-1\t") + SUMMARY).encode()
        with self.assertRaisesRegex(ProtocolError, "base-10 digits"):
            parse_protocol(stream)

    def test_missing_summary_is_rejected(self) -> None:
        with self.assertRaisesRegex(ProtocolError, "summary is missing"):
            parse_protocol(RECORD.encode())

    def test_empty_and_non_utf8_streams_are_rejected(self) -> None:
        with self.assertRaisesRegex(ProtocolError, "empty"):
            parse_protocol(b"")
        with self.assertRaisesRegex(ProtocolError, "UTF-8"):
            parse_protocol(b"\xff\n")

    def test_duplicate_summary_is_rejected(self) -> None:
        with self.assertRaisesRegex(ProtocolError, "duplicate summary"):
            parse_protocol((RECORD + SUMMARY + SUMMARY).encode())

    def test_record_after_summary_is_rejected(self) -> None:
        with self.assertRaisesRegex(ProtocolError, "after the summary"):
            parse_protocol((SUMMARY + RECORD).encode())

    def test_invalid_vector_identifier_is_rejected(self) -> None:
        stream = (RECORD.replace("sha256-abc", "../bad") + SUMMARY).encode()
        with self.assertRaisesRegex(ProtocolError, "invalid vector id"):
            parse_protocol(stream)

    def test_unknown_vector_identifier_is_rejected(self) -> None:
        with self.assertRaisesRegex(ProtocolError, "unknown vector id"):
            parse_protocol((RECORD + SUMMARY).encode(), {"sha256-empty"})

    def test_record_field_count_is_checked(self) -> None:
        stream = (RECORD.replace("\tnative\tpass", "\tpass") + SUMMARY).encode()
        with self.assertRaisesRegex(ProtocolError, "field count"):
            parse_protocol(stream)

    def test_duplicate_and_malformed_summary_are_rejected(self) -> None:
        malformed = "HASHMARK/1\tSUMMARY\t1\t1\n"
        with self.assertRaisesRegex(ProtocolError, "field count"):
            parse_protocol((RECORD + malformed).encode())


if __name__ == "__main__":
    unittest.main()
