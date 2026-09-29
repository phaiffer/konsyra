"""Deterministic unit tests for candidate Solana proof payload generation and verification."""

import pytest
from konsyra.spike.proof import (
    build_proof_memo_payload,
    extract_digest_from_memo_payload,
    validate_sha256_digest,
    verify_proof_digest,
)


def test_proof_payload_generation_deterministic_expected_payload():
    digest = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    expected = "KONSYRA:v0.1:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    memo_payload = build_proof_memo_payload(digest)
    assert memo_payload == expected


def test_verification_local_digest_equals_extracted_digest_verified():
    local_digest = "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2"
    memo_payload = f"KONSYRA:v0.1:{local_digest}"

    assert verify_proof_digest(local_digest, memo_payload) is True

    # Check extraction helper directly
    extracted = extract_digest_from_memo_payload(memo_payload)
    assert extracted == local_digest.lower()


def test_verification_local_digest_not_equals_extracted_digest_not_verified():
    local_digest = "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2"
    tampered_payload = "KONSYRA:v0.1:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"

    assert verify_proof_digest(local_digest, tampered_payload) is False


def test_invalid_sha256_digest_rejected():
    # Short length
    with pytest.raises(ValueError, match="64 hexadecimal characters"):
        validate_sha256_digest("abc123short")

    # Long length
    with pytest.raises(ValueError, match="64 hexadecimal characters"):
        validate_sha256_digest("a" * 65)

    # Non-hex characters
    with pytest.raises(ValueError, match="64 hexadecimal characters"):
        validate_sha256_digest("z" * 64)
