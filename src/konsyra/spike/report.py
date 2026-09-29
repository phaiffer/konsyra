"""Deterministic Quality Report payload formatting, canonical JSON serialization, and hashing."""

import hashlib
from typing import Any
import rfc8785
from konsyra.spike.models import CheckResult


def build_canonical_payload(
    start_slot: int,
    end_slot: int,
    sources: list[dict[str, str]],
    quality_status: str,
    checks: list[CheckResult],
) -> dict[str, Any]:
    """Builds the canonical Quality Report dictionary.

    Volatile execution metadata (local execution latency, temporary file paths,
    local UUIDs, logging timestamps) is explicitly excluded from this payload
    to guarantee deterministic SHA-256 digests across independent runs.
    """
    formatted_sources = sorted(
        [{"provider_name": s.get("provider_name", ""), "source_id": s["source_id"]} for s in sources],
        key=lambda x: (x["source_id"], x["provider_name"]),
    )

    # Evidence objects use canonical bytes as a stable total ordering. This
    # sorts only report evidence arrays, not arbitrary nested JSON arrays.
    formatted_checks = []
    for check in checks:
        formatted = check.to_dict()
        formatted["evidence"] = sorted(
            check.evidence, key=rfc8785.dumps
        )
        formatted_checks.append(formatted)
    formatted_checks.sort(
        key=lambda c: (c["check_type"], rfc8785.dumps(c))
    )
    evidence_items = sorted(
        [ev for check in formatted_checks for ev in check["evidence"]],
        key=rfc8785.dumps,
    )

    return {
        "report_schema_version": "0.1.0",
        "validator_version": "0.1.0-alpha",
        "network": "solana",
        "validation_range": {
            "start_slot": start_slot,
            "end_slot": end_slot,
        },
        "sources": formatted_sources,
        "quality_status": quality_status,
        "checks": formatted_checks,
        "evidence": evidence_items,
    }


def canonicalize_payload(payload: dict[str, Any]) -> bytes:
    """Serializes the payload dictionary into deterministic canonical UTF-8 JSON bytes using RFC 8785 (JCS)."""
    return rfc8785.dumps(payload)


def compute_payload_sha256(payload: dict[str, Any]) -> str:
    """Computes the 64-character hexadecimal SHA-256 digest of the canonical JSON payload."""
    canonical_bytes = canonicalize_payload(payload)
    return hashlib.sha256(canonical_bytes).hexdigest()
