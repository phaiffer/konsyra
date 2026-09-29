"""Data models for Phase 0 Solana Validation Spike."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal


@dataclass
class SlotObservation:
    """Normalized observation of a single Solana slot from an infrastructure source."""

    source_id: str
    slot: int
    blockhash: str
    parent_slot: int
    block_time: int | None
    transaction_signatures: set[str] = field(default_factory=set)
    observed_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class SlotAbsent:
    """Records a null block result without inferring skipped-slot semantics."""

    source_id: str
    slot: int
    reason: str = "RESULT_NULL"


@dataclass
class FetchFailure:
    """Preserves network/HTTP failures or RPC errors with unresolved domain meaning."""

    source_id: str
    slot: int
    error_type: Literal["NETWORK_ERROR", "HTTP_ERROR", "RPC_ERROR"]
    message: str
    code: int | None = None


FetchResult = SlotObservation | SlotAbsent | FetchFailure


@dataclass
class Divergence:
    """Explicit evidence payload detailing transaction signature discrepancies between two sources for a slot."""

    slot: int
    source_a_id: str
    source_b_id: str
    source_a_signature_count: int
    source_b_signature_count: int
    missing_in_source_a: list[str] = field(default_factory=list)
    missing_in_source_b: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "slot": self.slot,
            "source_a_id": self.source_a_id,
            "source_b_id": self.source_b_id,
            "source_a_signature_count": self.source_a_signature_count,
            "source_b_signature_count": self.source_b_signature_count,
            "missing_in_source_a": sorted(self.missing_in_source_a),
            "missing_in_source_b": sorted(self.missing_in_source_b),
        }


@dataclass
class CheckResult:
    """Result of a deterministic check executed by the Quality Engine."""

    check_type: Literal["COMPLETENESS", "RECONCILIATION"]
    status: Literal["PASS", "FAIL", "INCONCLUSIVE"]
    summary: str
    evidence: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "check_type": self.check_type,
            "status": self.status,
            "summary": self.summary,
            "evidence": self.evidence,
        }
