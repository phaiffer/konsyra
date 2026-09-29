"""Candidate Solana Devnet digest anchoring and proof verification module."""

import base58
import httpx
from typing import Optional
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.instruction import Instruction
from solders.message import MessageV0
from solders.transaction import VersionedTransaction
from solders.hash import Hash

# Standard Solana Memo Program ID
SOLANA_MEMO_PROGRAM_ID = Pubkey.from_string("MemoSqs4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcY")


HEX_DIGEST_CHARS = set("0123456789abcdefABCDEF")


def validate_sha256_digest(digest: str) -> str:
    """Validates that a string is exactly 64 hexadecimal characters representing a SHA-256 digest."""
    clean = digest.strip()
    if len(clean) != 64 or not set(clean).issubset(HEX_DIGEST_CHARS):
        raise ValueError("SHA-256 digest must be exactly 64 hexadecimal characters.")
    return clean.lower()


def build_proof_memo_payload(sha256_digest: str) -> str:
    """Builds the candidate memo transaction payload encoding the SHA-256 report digest.

    Candidate Format: KONSYRA:v0.1:<SHA256_HEX_DIGEST>
    (TO BE VALIDATED DURING PHASE 0)
    """
    valid_digest = validate_sha256_digest(sha256_digest)
    return f"KONSYRA:v0.1:{valid_digest}"


def extract_digest_from_memo_payload(memo_payload: str) -> Optional[str]:
    """Extracts the 64-character SHA-256 digest from a candidate memo payload string."""
    cleaned = memo_payload.strip()
    if cleaned.startswith("KONSYRA:v0.1:"):
        candidate = cleaned.split("KONSYRA:v0.1:")[-1].strip()
        try:
            return validate_sha256_digest(candidate)
        except ValueError:
            return None
    if len(cleaned) == 64:
        try:
            return validate_sha256_digest(cleaned)
        except ValueError:
            return None
    return None


def verify_proof_digest(local_digest: str, extracted_memo_payload: str) -> bool:
    """Verifies that an extracted on-chain memo payload matches the expected local report SHA-256 digest.

    Returns True if digests match (VERIFIED), False otherwise (NOT VERIFIED).
    Enforces principle: Integrity of report representation != absolute truth of ledger.
    """
    try:
        clean_local = validate_sha256_digest(local_digest)
    except ValueError:
        return False

    extracted_digest = extract_digest_from_memo_payload(extracted_memo_payload)
    if extracted_digest is None:
        return False
    return clean_local == extracted_digest


def anchor_digest_on_devnet(rpc_url: str, private_key_b58: str, sha256_digest: str) -> str:
    """Submits a candidate Memo transaction to Solana Devnet carrying the report SHA-256 digest.

    Returns the transaction signature string on success.
    """
    # Parse fee-payer keypair from Base58 or JSON byte array
    if private_key_b58.startswith("[") and private_key_b58.endswith("]"):
        import json
        byte_list = json.loads(private_key_b58)
        keypair = Keypair.from_bytes(bytes(byte_list))
    else:
        keypair = Keypair.from_base58_string(private_key_b58)

    memo_text = build_proof_memo_payload(sha256_digest)
    memo_bytes = memo_text.encode("utf-8")

    instruction = Instruction(
        program_id=SOLANA_MEMO_PROGRAM_ID,
        data=memo_bytes,
        accounts=[],
    )

    # Fetch latest blockhash via httpx JSON-RPC
    headers = {"Content-Type": "application/json"}
    with httpx.Client(timeout=10.0) as client:
        blockhash_resp = client.post(
            rpc_url,
            json={"jsonrpc": "2.0", "id": 1, "method": "getLatestBlockhash", "params": []},
            headers=headers,
        ).json()

        if "error" in blockhash_resp:
            raise RuntimeError(f"RPC getLatestBlockhash failed: {blockhash_resp['error']}")

        recent_blockhash_str = blockhash_resp["result"]["value"]["blockhash"]
        recent_blockhash = Hash.from_string(recent_blockhash_str)

        msg = MessageV0.try_compile(
            payer=keypair.pubkey(),
            instructions=[instruction],
            address_lookup_table_accounts=[],
            recent_blockhash=recent_blockhash,
        )

        tx = VersionedTransaction(msg, [keypair])
        raw_tx_bytes = bytes(tx)
        encoded_tx = base58.b58encode(raw_tx_bytes).decode("utf-8")

        send_resp = client.post(
            rpc_url,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "sendTransaction",
                "params": [encoded_tx, {"encoding": "base58"}],
            },
            headers=headers,
        ).json()

        if "error" in send_resp:
            raise RuntimeError(f"RPC sendTransaction failed: {send_resp['error']}")

        return send_resp["result"]


def retrieve_proof_from_devnet(rpc_url: str, tx_signature_b58: str) -> str:
    """Candidate retrieval and Memo extraction from transaction log strings.

    Not yet validated against a successful live Konsyra Devnet transaction.
    The live gate must validate confirmation, retrieval, and extraction behavior.
    """
    headers = {"Content-Type": "application/json"}
    params = [
        tx_signature_b58,
        {"encoding": "json", "maxSupportedTransactionVersion": 0},
    ]

    with httpx.Client(timeout=10.0) as client:
        resp = client.post(
            rpc_url,
            json={"jsonrpc": "2.0", "id": 1, "method": "getTransaction", "params": params},
            headers=headers,
        ).json()

        if "error" in resp:
            raise RuntimeError(f"RPC getTransaction failed: {resp['error']}")

        result = resp.get("result")
        if not result:
            raise ValueError(f"Transaction signature {tx_signature_b58} not found on Devnet.")

        log_messages = result.get("meta", {}).get("logMessages", [])
        memo_content = ""

        for log in log_messages:
            if "Program log: Memo" in log:
                memo_content = log.split('): "')[-1].rstrip('"')
                break

        if not memo_content:
            for log in log_messages:
                if "KONSYRA:v0.1:" in log:
                    memo_content = "KONSYRA:v0.1:" + log.split("KONSYRA:v0.1:")[-1].split('"')[0]
                    break

        if not memo_content:
            raise ValueError(f"Memo payload could not be extracted from transaction logs for {tx_signature_b58}.")

        return memo_content
