"""Deterministic unit tests for signature set reconciliation."""

import pytest

from konsyra.spike.models import SlotObservation
from konsyra.spike.reconcile import reconcile_slot_signatures, run_reconciliation


def test_identical_signature_sets_pass():
    sigs = {"sig1", "sig2", "sig3"}
    obs_a = SlotObservation("source_a", 100, "hash1", 99, 1000, set(sigs))
    obs_b = SlotObservation("source_b", 100, "hash1", 99, 1000, set(sigs))

    divergence = reconcile_slot_signatures(obs_a, obs_b)
    assert divergence is None

    status, checks = run_reconciliation([obs_a], [obs_b], 100, 100)
    assert status == "PASS"
    reconcile_check = next(c for c in checks if c.check_type == "RECONCILIATION")
    assert reconcile_check.status == "PASS"
    assert len(reconcile_check.evidence) == 0


def test_source_a_missing_signature_fail():
    sigs_a = {"sig1", "sig2"}
    sigs_b = {"sig1", "sig2", "sig3"}
    obs_a = SlotObservation("source_a", 100, "hash1", 99, 1000, sigs_a)
    obs_b = SlotObservation("source_b", 100, "hash1", 99, 1000, sigs_b)

    divergence = reconcile_slot_signatures(obs_a, obs_b)
    assert divergence is not None
    assert divergence.slot == 100
    assert divergence.missing_in_source_a == ["sig3"]
    assert divergence.missing_in_source_b == []

    status, checks = run_reconciliation([obs_a], [obs_b], 100, 100)
    assert status == "FAIL"
    reconcile_check = next(c for c in checks if c.check_type == "RECONCILIATION")
    assert reconcile_check.status == "FAIL"
    assert len(reconcile_check.evidence) == 1
    assert reconcile_check.evidence[0]["missing_in_source_a"] == ["sig3"]


def test_source_b_missing_signature_fail():
    sigs_a = {"sig1", "sig2", "sig3"}
    sigs_b = {"sig1", "sig3"}
    obs_a = SlotObservation("source_a", 100, "hash1", 99, 1000, sigs_a)
    obs_b = SlotObservation("source_b", 100, "hash1", 99, 1000, sigs_b)

    divergence = reconcile_slot_signatures(obs_a, obs_b)
    assert divergence is not None
    assert divergence.slot == 100
    assert divergence.missing_in_source_a == []
    assert divergence.missing_in_source_b == ["sig2"]

    status, checks = run_reconciliation([obs_a], [obs_b], 100, 100)
    assert status == "FAIL"
    reconcile_check = next(c for c in checks if c.check_type == "RECONCILIATION")
    assert reconcile_check.status == "FAIL"
    assert len(reconcile_check.evidence) == 1
    assert reconcile_check.evidence[0]["missing_in_source_b"] == ["sig2"]


def test_provider_ordering_differs_same_result():
    sigs = {"sigA", "sigB", "sigC"}
    obs_a1 = SlotObservation("source_a", 100, "hash1", 99, 1000, set(sigs))
    obs_a2 = SlotObservation("source_a", 101, "hash2", 100, 1004, set(sigs))

    obs_b1 = SlotObservation("source_b", 100, "hash1", 99, 1000, set(sigs))
    obs_b2 = SlotObservation("source_b", 101, "hash2", 100, 1004, set(sigs))

    status1, checks1 = run_reconciliation([obs_a1, obs_a2], [obs_b1, obs_b2], 100, 101)
    status2, checks2 = run_reconciliation([obs_a2, obs_a1], [obs_b1, obs_b2], 100, 101)

    assert status1 == status2 == "PASS"
    assert [c.to_dict() for c in checks1] == [c.to_dict() for c in checks2]


def test_absent_slot_completeness_is_inconclusive():
    sigs = {"sig1"}
    obs_a = SlotObservation("source_a", 100, "hash1", 99, 1000, set(sigs))
    obs_b = SlotObservation("source_b", 100, "hash1", 99, 1000, set(sigs))

    # Range 100..101, slot 101 is missing observation in both sources
    status, checks = run_reconciliation([obs_a], [obs_b], 100, 101)
    assert status == "INCONCLUSIVE"
    completeness_check = next(c for c in checks if c.check_type == "COMPLETENESS")
    assert completeness_check.status == "INCONCLUSIVE"
    assert completeness_check.evidence[0]["absent_in_source_a"] == [101]
    assert completeness_check.evidence[0]["absent_in_source_b"] == [101]


def test_different_slots_cannot_be_reconciled():
    a = SlotObservation("a", 100, "hash", 99, 1000, {"sig"})
    b = SlotObservation("b", 101, "hash", 100, 1000, {"sig"})
    with pytest.raises(ValueError, match="cannot reconcile observations from different slots"):
        reconcile_slot_signatures(a, b)


@pytest.mark.parametrize("side", ["A", "B"])
def test_duplicate_observation_slot_rejected(side):
    obs = SlotObservation(side, 100, "hash", 99, 1000, {"sig"})
    other = SlotObservation(side, 100, "different", 99, 1000, {"different"})
    a, b = ([obs, other], []) if side == "A" else ([], [obs, other])
    with pytest.raises(ValueError, match=f"Source {side}: duplicate slot observation 100"):
        run_reconciliation(a, b, 100, 100)


@pytest.mark.parametrize("slots_a,slots_b", [
    ([100], []), ([], [100]), ([100], [101]), ([], [])
], ids=["source-a-only", "source-b-only", "disjoint-slots", "both-empty"])
def test_zero_common_slots_reconciliation_is_inconclusive(slots_a, slots_b):
    a = [SlotObservation("a", slot, "hash", slot - 1, 1000) for slot in slots_a]
    b = [SlotObservation("b", slot, "hash", slot - 1, 1000) for slot in slots_b]
    status, checks = run_reconciliation(a, b, 100, 101)
    check = next(c for c in checks if c.check_type == "RECONCILIATION")
    assert status == check.status == "INCONCLUSIVE"
    assert check.evidence == []
    assert check.summary == "Reconciled transaction signatures across 0 common slots."
