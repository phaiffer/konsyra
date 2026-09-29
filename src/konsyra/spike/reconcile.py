"""Deterministic set-reconciliation logic for Solana slot observations."""

from typing import Literal
from konsyra.spike.models import CheckResult, Divergence, SlotObservation


def reconcile_slot_signatures(
    obs_a: SlotObservation, obs_b: SlotObservation
) -> Divergence | None:
    """Perform deterministic signature set reconciliation for a single slot across two observations.

    Returns a Divergence object detailing missing signatures if a discrepancy exists,
    or None if signature sets match perfectly.
    """
    if obs_a.slot != obs_b.slot:
        raise ValueError("cannot reconcile observations from different slots")

    sigs_a = obs_a.transaction_signatures
    sigs_b = obs_b.transaction_signatures

    missing_a = sorted(list(sigs_b - sigs_a))
    missing_b = sorted(list(sigs_a - sigs_b))

    if missing_a or missing_b:
        return Divergence(
            slot=obs_a.slot,
            source_a_id=obs_a.source_id,
            source_b_id=obs_b.source_id,
            source_a_signature_count=len(sigs_a),
            source_b_signature_count=len(sigs_b),
            missing_in_source_a=missing_a,
            missing_in_source_b=missing_b,
        )

    return None


def run_reconciliation(
    observations_a: list[SlotObservation],
    observations_b: list[SlotObservation],
    start_slot: int,
    end_slot: int,
) -> tuple[Literal["PASS", "FAIL", "INCONCLUSIVE"], list[CheckResult]]:
    """Executes deterministic checks across observations from Source A and Source B.

    Returns (overall_quality_status, list_of_check_results).
    """
    # Validate both collections before creating maps; never overwrite evidence.
    for side, observations in (("A", observations_a), ("B", observations_b)):
        seen = set()
        duplicates = set()
        for obs in observations:
            if obs.slot in seen:
                duplicates.add(obs.slot)
            seen.add(obs.slot)
        if duplicates:
            raise ValueError(f"Source {side}: duplicate slot observation {min(duplicates)}")

    map_a = {obs.slot: obs for obs in observations_a}
    map_b = {obs.slot: obs for obs in observations_b}

    all_target_slots = list(range(start_slot, end_slot + 1))
    common_slots = sorted(list(set(map_a.keys()) & set(map_b.keys())))

    divergences: list[Divergence] = []

    # 1. Completeness check relative to requested slot range
    missing_slots_a = [s for s in all_target_slots if s not in map_a]
    missing_slots_b = [s for s in all_target_slots if s not in map_b]

    completeness_evidence = []
    if missing_slots_a or missing_slots_b:
        completeness_evidence.append(
            {
                "absent_in_source_a": missing_slots_a,
                "absent_in_source_b": missing_slots_b,
            }
        )
        # Missing integer slot observations are marked INCONCLUSIVE because absence semantics (skipped slots) remain unresolved
        completeness_status: Literal["PASS", "FAIL", "INCONCLUSIVE"] = "INCONCLUSIVE"
        completeness_summary = (
            f"Evaluated slots [{start_slot}, {end_slot}]. Some slot observations were absent "
            "(marked INCONCLUSIVE as skipped slot semantics are unresolved)."
        )
    else:
        completeness_status = "PASS"
        completeness_summary = f"All integer slots in range [{start_slot}, {end_slot}] observed by both sources."

    check_completeness = CheckResult(
        check_type="COMPLETENESS",
        status=completeness_status,
        summary=completeness_summary,
        evidence=completeness_evidence,
    )

    # 2. Reconciliation check across common slots
    for slot in common_slots:
        div = reconcile_slot_signatures(map_a[slot], map_b[slot])
        if div:
            divergences.append(div)

    reconcile_status: Literal["PASS", "FAIL", "INCONCLUSIVE"]
    if not common_slots:
        reconcile_status = "INCONCLUSIVE"
    elif divergences:
        reconcile_status = "FAIL"
    else:
        reconcile_status = "PASS"
    check_reconciliation = CheckResult(
        check_type="RECONCILIATION",
        status=reconcile_status,
        summary=f"Reconciled transaction signatures across {len(common_slots)} common slots.",
        evidence=[d.to_dict() for d in divergences],
    )

    checks = [check_completeness, check_reconciliation]

    # Overall Quality Status evaluation
    if any(c.status == "FAIL" for c in checks):
        overall_status: Literal["PASS", "FAIL", "INCONCLUSIVE"] = "FAIL"
    elif any(c.status == "INCONCLUSIVE" for c in checks) or not common_slots:
        overall_status = "INCONCLUSIVE"
    else:
        overall_status = "PASS"

    return overall_status, checks
