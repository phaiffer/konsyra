"""Phase 0 Solana Validation Spike CLI Execution Harness."""

import argparse
import sys
from konsyra.spike.models import SlotObservation
from konsyra.spike.reconcile import run_reconciliation
from konsyra.spike.report import (
    build_canonical_payload,
    compute_payload_sha256,
)
from konsyra.spike.proof import (
    build_proof_memo_payload,
    verify_proof_digest,
)


def create_mock_fixtures(
    start_slot: int = 421928380, count: int = 3, inject_divergence: bool = True
) -> tuple[list[SlotObservation], list[SlotObservation]]:
    """Creates deterministic test observations for Source A and Source B using neutral fixture labels.

    If inject_divergence is True, Source B will miss one transaction signature
    in the middle slot to simulate a controlled provider discrepancy.
    """
    obs_a = []
    obs_b = []

    for i in range(count):
        slot = start_slot + i
        sigs = {
            f"5K8X{slot}a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6",
            f"3X9P{slot}m1n2o3p4q5r6s7t8u9v0w1x2y3z4a5b6c7d8e9f0g1h2i3j4k5",
            f"7P2Q{slot}z1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5",
        }

        obs_a.append(
            SlotObservation(
                source_id="fixture-source-a",
                slot=slot,
                blockhash=f"BlockhashA_{slot}",
                parent_slot=slot - 1,
                block_time=1700000000 + i * 4,
                transaction_signatures=set(sigs),
            )
        )

        # In Source B, simulate controlled missing signature in middle slot
        sigs_b = set(sigs)
        if inject_divergence and i == 1:
            missing_sig = f"3X9P{slot}m1n2o3p4q5r6s7t8u9v0w1x2y3z4a5b6c7d8e9f0g1h2i3j4k5"
            sigs_b.remove(missing_sig)

        obs_b.append(
            SlotObservation(
                source_id="fixture-source-b",
                slot=slot,
                blockhash=f"BlockhashB_{slot}",
                parent_slot=slot - 1,
                block_time=1700000000 + i * 4,
                transaction_signatures=sigs_b,
            )
        )

    return obs_a, obs_b


def main():
    parser = argparse.ArgumentParser(description="Konsyra Phase 0 Solana Validation Spike Harness")
    parser.add_argument("--start-slot", type=int, default=421928380, help="Start slot")
    parser.add_argument("--end-slot", type=int, default=421928382, help="End slot")
    parser.add_argument(
        "--inject-divergence",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Inject controlled fixture divergence for simulation testing",
    )
    args = parser.parse_args()

    print("=" * 70)
    print("KONSYRA PHASE 0 — SOLANA VALIDATION SPIKE HARNESS")
    if args.inject_divergence:
        print("MODE: CONTROLLED / SIMULATED PROVIDER DIVERGENCE (Fixture Mode)")
    else:
        print("MODE: IDENTICAL FIXTURES (No Divergence)")
    print("=" * 70)

    obs_a, obs_b = create_mock_fixtures(
        start_slot=args.start_slot,
        count=(args.end_slot - args.start_slot + 1),
        inject_divergence=args.inject_divergence,
    )

    print(f"\n[1] Ingested Fixture Observations:")
    print(f"    Source A ({obs_a[0].source_id}): {len(obs_a)} slots observed.")
    print(f"    Source B ({obs_b[0].source_id}): {len(obs_b)} slots observed.")

    print(f"\n[2] Executing Deterministic Set Reconciliation...")
    quality_status, checks = run_reconciliation(
        obs_a, obs_b, args.start_slot, args.end_slot
    )

    sources_info = [
        {"source_id": obs_a[0].source_id, "provider_name": "Controlled Fixture A"},
        {"source_id": obs_b[0].source_id, "provider_name": "Controlled Fixture B"},
    ]

    print(f"    Overall QualityStatus: {quality_status}")
    for c in checks:
        print(f"    - {c.check_type}: {c.status} ({c.summary})")
        if c.evidence:
            print(f"      Explicit Evidence: {c.evidence}")

    print(f"\n[3] Generating Deterministic Canonical Report & SHA-256 Digest...")
    payload = build_canonical_payload(
        args.start_slot, args.end_slot, sources_info, quality_status, checks
    )
    digest = compute_payload_sha256(payload)
    memo_payload = build_proof_memo_payload(digest)

    print(f"    Report SHA-256 Digest: {digest}")
    print(f"    Candidate Memo Payload: {memo_payload}")

    print(f"\n[4] Deterministic Verification Check:")
    is_verified = verify_proof_digest(digest, memo_payload)
    print(f"    Local Digest vs Extracted Memo Digest Match: {'VERIFIED' if is_verified else 'NOT VERIFIED'}")

    print("=" * 70)


if __name__ == "__main__":
    main()
