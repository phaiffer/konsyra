"""RPC Data Collector for Hypothesis 1 (Solana Slot Discovery) & Hypothesis 2 (Normalization)."""

import logging
from datetime import datetime, timezone
import httpx
from konsyra.spike.models import FetchFailure, FetchResult, SlotAbsent, SlotObservation

logger = logging.getLogger(__name__)


def query_rpc_json(rpc_url: str, method: str, params: list) -> dict:
    """Executes a JSON-RPC HTTP POST request to a Solana endpoint."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params,
    }
    headers = {"Content-Type": "application/json"}
    with httpx.Client(timeout=10.0) as client:
        response = client.post(rpc_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()


def fetch_confirmed_blocks(
    rpc_url: str, start_slot: int, end_slot: int
) -> list[int]:
    """Candidate Strategy H1: Discovers confirmed slots in range using getBlocks(start_slot, end_slot).

    (TO BE VALIDATED DURING PHASE 0)
    """
    res = query_rpc_json(rpc_url, "getBlocks", [start_slot, end_slot])
    if "error" in res:
        raise RuntimeError(f"RPC getBlocks error: {res['error']}")
    return res.get("result", [])


def fetch_slot_observation(
    rpc_url: str, source_id: str, slot: int
) -> FetchResult:
    """Candidate Strategy H1/H2: Ingests observation for a slot using getBlock with transactionDetails="signatures".

    Returns:
    - SlotObservation: successful block observation
    - SlotAbsent: provider returned result null; reason preserved without inferred semantics
    - FetchFailure: network, HTTP, or explicit RPC error; unexpected Python exceptions propagate
    """
    params = [
        slot,
        {
            "encoding": "json",
            "transactionDetails": "signatures",
            "rewards": False,
            "maxSupportedTransactionVersion": 0,
        },
    ]

    try:
        res = query_rpc_json(rpc_url, "getBlock", params)
    except httpx.HTTPStatusError as e:
        return FetchFailure(
            source_id=source_id,
            slot=slot,
            error_type="HTTP_ERROR",
            message=str(e),
            code=e.response.status_code,
        )
    except httpx.RequestError as e:
        return FetchFailure(
            source_id=source_id,
            slot=slot,
            error_type="NETWORK_ERROR",
            message=str(e),
        )

    if "error" in res:
        err = res["error"]
        err_msg = str(err.get("message") if isinstance(err, dict) else err)
        err_code = err.get("code") if isinstance(err, dict) else None

        # Preserve unresolved RPC evidence without inferring slot absence.
        return FetchFailure(
            source_id=source_id,
            slot=slot,
            error_type="RPC_ERROR",
            message=err_msg,
            code=err_code,
        )

    result = res.get("result")
    if result is None:
        return SlotAbsent(
            source_id=source_id,
            slot=slot,
            reason="RESULT_NULL",
        )

    blockhash = result.get("blockhash", "")
    parent_slot = result.get("parentSlot", 0)
    block_time = result.get("blockTime")
    signatures_list = result.get("signatures", [])

    return SlotObservation(
        source_id=source_id,
        slot=slot,
        blockhash=blockhash,
        parent_slot=parent_slot,
        block_time=block_time,
        transaction_signatures=set(signatures_list),
        observed_at=datetime.now(timezone.utc).isoformat(),
    )
