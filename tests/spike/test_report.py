"""Deterministic unit tests for Quality Report canonicalization and SHA-256 hashing."""

from konsyra.spike.models import CheckResult, Divergence
from konsyra.spike.report import (
    build_canonical_payload,
    canonicalize_payload,
    compute_payload_sha256,
)


def test_canonical_report_generated_twice_identical_digest():
    sources = [
        {"source_id": "source_b", "provider_name": "QuickNode"},
        {"source_id": "source_a", "provider_name": "Alchemy"},
    ]
    check = CheckResult(
        check_type="RECONCILIATION",
        status="FAIL",
        summary="Found 1 divergence",
        evidence=[
            Divergence(
                slot=100,
                source_a_id="source_a",
                source_b_id="source_b",
                source_a_signature_count=3,
                source_b_signature_count=2,
                missing_in_source_a=[],
                missing_in_source_b=["sig_x"],
            ).to_dict()
        ],
    )

    payload1 = build_canonical_payload(100, 105, sources, "FAIL", [check])
    payload2 = build_canonical_payload(100, 105, sources, "FAIL", [check])

    bytes1 = canonicalize_payload(payload1)
    bytes2 = canonicalize_payload(payload2)

    digest1 = compute_payload_sha256(payload1)
    digest2 = compute_payload_sha256(payload2)

    assert bytes1 == bytes2
    assert digest1 == digest2
    assert len(digest1) == 64


def test_canonicalization_sorts_sources_checks_and_evidence():
    sources = [
        {"source_id": "source_z", "provider_name": "Z"},
        {"source_id": "source_a", "provider_name": "A"},
    ]
    evidence = [
        Divergence(101, "source_a", "source_z", 2, 1, [], ["sig_y"]).to_dict(),
        Divergence(100, "source_a", "source_z", 2, 1, [], ["sig_x"]).to_dict(),
    ]
    completeness = CheckResult("COMPLETENESS", "INCONCLUSIVE", "Missing slots", [
        {"absent_in_source_a": [102], "absent_in_source_b": []}
    ])
    check1 = CheckResult("RECONCILIATION", "FAIL", "Two divergences", evidence)
    check2 = CheckResult("RECONCILIATION", "FAIL", "Two divergences", list(reversed(evidence)))
    payload1 = build_canonical_payload(100, 102, sources, "FAIL", [check1, completeness])
    payload2 = build_canonical_payload(100, 102, list(reversed(sources)), "FAIL", [completeness, check2])
    assert canonicalize_payload(payload1) == canonicalize_payload(payload2)
    assert compute_payload_sha256(payload1) == compute_payload_sha256(payload2)
    assert check1.evidence == evidence  # Input order is not mutated.
    assert len(payload1["evidence"]) == 3


def test_representative_quality_report_reproducibility():
    sources_a = [
        {"source_id": "source_quicknode", "provider_name": "QuickNode"},
        {"source_id": "source_alchemy", "provider_name": "Alchemy"},
    ]
    sources_b = list(reversed(sources_a))

    div_evidence = Divergence(
        slot=300000000,
        source_a_id="source_alchemy",
        source_b_id="source_quicknode",
        source_a_signature_count=3,
        source_b_signature_count=2,
        missing_in_source_a=[],
        missing_in_source_b=["sig_divergence_1"],
    ).to_dict()

    tx_evidence = {"tx_signature": "5xY123456789abcdefghijklmnopqrstuvwxyz"}

    completeness_check = CheckResult(
        check_type="COMPLETENESS",
        status="PASS",
        summary="All slots present in range",
        evidence=[],
    )

    reconciliation_check_1 = CheckResult(
        check_type="RECONCILIATION",
        status="FAIL",
        summary="1 divergence found",
        evidence=[div_evidence, tx_evidence],
    )

    reconciliation_check_2 = CheckResult(
        check_type="RECONCILIATION",
        status="FAIL",
        summary="1 divergence found",
        evidence=[tx_evidence, div_evidence],  # Reversed evidence input order
    )

    payload1 = build_canonical_payload(
        300000000, 300000005, sources_a, "FAIL", [reconciliation_check_1, completeness_check]
    )
    payload2 = build_canonical_payload(
        300000000, 300000005, sources_b, "FAIL", [completeness_check, reconciliation_check_2]
    )

    bytes1 = canonicalize_payload(payload1)
    bytes2 = canonicalize_payload(payload2)

    digest1 = compute_payload_sha256(payload1)
    digest2 = compute_payload_sha256(payload2)

    assert bytes1 == bytes2
    assert digest1 == digest2
    assert len(digest1) == 64
