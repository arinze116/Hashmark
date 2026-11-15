"""Independent digest implementations used as Hashmark's oracle."""

from __future__ import annotations

import hashlib
from importlib.metadata import PackageNotFoundError, version


class OracleUnavailableError(RuntimeError):
    """Raised when the required independent oracle is unavailable."""


def sha256_digest(data: bytes) -> bytes:
    """Return the SHA-256 digest calculated by Python's hashlib."""

    return hashlib.sha256(data).digest()


def keccak256_digest(data: bytes) -> bytes:
    """Return Ethereum Keccak-256, which is distinct from SHA3-256."""

    try:
        from Crypto.Hash import keccak
    except ImportError as error:
        raise OracleUnavailableError(
            "PyCryptodome is required for the Ethereum Keccak-256 oracle",
        ) from error
    state = keccak.new(digest_bits=256)
    state.update(data)
    return state.digest()


def digest(algorithm: str, data: bytes) -> bytes:
    """Return an independent digest for a supported algorithm."""

    if algorithm == "sha256":
        return sha256_digest(data)
    if algorithm == "keccak256":
        return keccak256_digest(data)
    raise ValueError(f"unsupported oracle algorithm: {algorithm}")


def digest_hex(algorithm: str, data: bytes) -> str:
    """Return a supported digest as canonical lowercase hexadecimal."""

    return digest(algorithm, data).hex()


def pycryptodome_version() -> str:
    """Return the installed PyCryptodome distribution version."""

    try:
        return version("pycryptodome")
    except PackageNotFoundError as error:
        raise OracleUnavailableError("PyCryptodome is not installed") from error
