# Konsyra Phase 0 — Technical Spike Findings & Evidence

> **Phase:** Phase 0 — Solana Validation Spike
> **Initial Spike Date:** 2026-09-28
> **Gate C — RFC 8785 / JCS Technical Experiment:** 2026-09-29 (no network experiments)
> **Environment:** Windows (PowerShell), Python 3.12.10, Pytest 9.1.1, solders 0.29.0, httpx 0.28.1, rfc8785 0.1.4, base58 2.1.1
> **Overall Phase 0 Status:** **PARTIAL (Not Approved for Phase 1 Transition Yet)**

---

## 1. Executive Summary

Phase 0 executed a technical spike to empirically evaluate the core hypotheses of the Konsyra Architecture Baseline v0.1.

**Overall Phase 0 Result: PARTIAL**

While the core local deterministic reconciliation, payload structuring, SHA-256 hashing, digest matching logic, and RFC 8785 (JCS) canonical serialization (H4) were proven deterministically via unit tests, the spike **cannot be declared PASS** because:
1. **Single Real Source Tested:** Live collection was executed against only one real public RPC endpoint (`https://api.mainnet-beta.solana.com`). Ingesting from the same endpoint under two logical source labels does not constitute cross-provider independent validation.
2. **Devnet Anchoring Incomplete:** Live Devnet memo transaction submission and retrieval were not completed due to public Devnet faucet rate limits.

---

## 2. Environment & Dependency Register

- **Python Runtime:** Python 3.12.10 (CPython 64-bit)
- **Dependencies Installed:**
  - `httpx` (0.28.1) — Lightweight HTTP client for JSON-RPC 2.0 calls.
  - `rfc8785` (0.1.4) — IETF RFC 8785 / JSON Canonicalization Scheme (JCS) implementation.
  - `solders` (0.29.0) — Solana Rust bindings for Keypair, Instruction, and VersionedTransaction.
  - `base58` (2.1.1) — Base58 encoding/decoding helper.
  - `pytest` (9.1.1) — Unit testing framework.

*Note: `canonicaljson` was removed from project dependencies and replaced with `rfc8785` during Gate C.*

---

## 3. Detailed Hypothesis Evaluations

### Hypothesis 1 — Solana Slot Discovery
- **Evaluation:** **PARTIAL** (local mocked behavior tested; prior single-source live findings only)
- **Strategy Tested:** `getBlocks(start_slot, end_slot)` followed by `getBlock(slot, transactionDetails="signatures")`.
- **Empirical Findings:**
  - Prior spike reported (not revalidated in this local pass): `getBlocks(300000000, 300000005)` on Solana Mainnet-Beta successfully returned confirmed slot integers: `[300000000, 300000001, 300000002, 300000003, 300000004, 300000005]`.
  - Prior spike reported (not revalidated in this local pass): `getBlock(300000000, transactionDetails="signatures")` returned 2,541 transaction signature strings.
  - Local mocked tests distinguish response outcomes; they do not establish live absence semantics:
    - `SlotObservation`: Successful block observation.
    - `SlotAbsent`: `result: null`, with reason `RESULT_NULL`; no skipped-slot meaning is inferred.
    - `FetchFailure`: Network and HTTP failures, or explicit RPC errors preserving code, message, source ID, and slot. Codes `-32007`/`-32004` and messages containing `not found`/`skipped` remain unresolved `RPC_ERROR` evidence.
    - Unexpected Python exceptions propagate instead of becoming network failures.
  - Stable live RPC absence semantics and independent-provider behavior remain unvalidated.

---

### Hypothesis 2 — Normalized Observation
- **Evaluation:** **PASS**
- **Contract Verified:**
  ```python
  SlotObservation(
      source_id="fixture-source-a",
      slot=300000000,
      blockhash="...",
      parent_slot=299999999,
      block_time=1700000000,
      transaction_signatures=set([...]),
      observed_at="2026-09-28T20:00:00+00:00"
  )
  ```
- **Findings:** Tested fixture provider responses can be normalized into `SlotObservation` structs. Preserved distinction between observations, absent slots, and fetch failures without freezing a premature `status` enum.

---

### Hypothesis 3 — Deterministic Set Reconciliation
- **Evaluation:** **PASS** (Local Fixtures)
- **Empirical Findings:**
  - Signature set differences ($\text{Signatures}_A \setminus \text{Signatures}_B$) are computed deterministically regardless of signature order.
  - Source labels in local fixtures are logical identifiers, not evidence of independent live providers.
  - Controlled divergence injection accurately isolates missing transaction signatures per slot:
    ```json
    {
      "slot": 421928381,
      "source_a_id": "fixture-source-a",
      "source_b_id": "fixture-source-b",
      "source_a_signature_count": 3,
      "source_b_signature_count": 2,
      "missing_in_source_a": [],
      "missing_in_source_b": ["3X9P421928381m1n2o3p4q5r6s7t8u9v0w1x2y3z4a5b6c7d8e9f0g1h2i3j4k5"]
    }
    ```
  - Local tests reject reconciliation across different slots and duplicate observations within either source collection. Zero common slots yields an INCONCLUSIVE reconciliation check and a summary reporting zero comparisons.
  - Uniqueness and Freshness evaluations were removed from active evaluation to focus strictly on the central reconciliation hypothesis.

---

### Hypothesis 4 — Deterministic Report Payload & Canonicalization
- **Evaluation:** **PASS** (Validated via Gate C Technical Experiment)
- **Empirical Findings:**
  - **Canonical Serialization Package:** Selected and migrated to `rfc8785` (0.1.4), implementing IETF RFC 8785 (JSON Canonicalization Scheme / JCS). `canonicaljson` has been uninstalled and removed from dependencies.
  - **Architectural Boundary Preserved:**
    - Domain/report layer (`report.py`) defines semantic structure and deterministic ordering of `sources` (by `source_id`, `provider_name`), `checks` (by `check_type`, canonical bytes tie-breaker), and `evidence` (by canonical bytes).
    - `rfc8785.dumps()` is strictly responsible for canonical JSON byte serialization.
  - **JCS Conformance Tests (`tests/spike/test_rfc8785.py`):**
    - **Object property ordering:** Object keys serialize in lexicographical order (e.g. `{"b": 2, "a": 1}` -> `b'{"a":1,"b":2}'`).
    - **Whitespace independence:** Output contains zero insignificant whitespace (no spaces after `:` or `,`).
    - **Unicode behavior:** UTF-8 encoded bytes output directly without unnecessary `\uXXXX` escaping (e.g. `b'{"network":"solana_\xf0\x9f\x8c\x9e","status":"V\xc3\xa1lid"}'`).
    - **JSON Primitives & Nested Objects:** Verified deterministic output for `null`, `true`/`false`, `integer`, `string`, `array`, `object`, and deeply nested dictionaries.
    - **Numeric Safety:** Recursive payload verification (`assert_no_floats`) confirms representative Konsyra Quality Reports contain no floating-point numbers.
    - **Invalid Values:** Non-canonical floats (`NaN`, `+inf`, `-inf`) fail explicitly with `rfc8785.FloatDomainError` (subclass of `CanonicalizationError`).
    - **Integer Domain Safety:** Integers outside $[-2^{53}+1, 2^{53}-1]$ (e.g., $2^{53} = 9007199254740992$) fail explicitly with `rfc8785.IntegerDomainError` (subclass of `CanonicalizationError`). Solana slot numbers ($300000000$, $421928381$) remain safely within the safe integer domain.
  - **Quality Report Reproducibility:**
    - Representative Quality Report (validation range, 2 sources, completeness check, reconciliation check, divergence evidence, transaction signature evidence, quality status) generates identical canonical bytes and SHA-256 digests across input ordering variations.
    - Input objects are not mutated.
  - **Frozen Canonicalization Vector:** Added frozen vector test in `test_rfc8785.py` enforcing expected canonical bytes and frozen SHA-256 digest (`285debe97ab5b90a2233daa877696dd359d12571684beea97be32122e8b6757f`).
  - **Legacy Comparison (`canonicaljson` vs `rfc8785`):**
    - For the representative Konsyra Quality Report payload, `canonicaljson` and `rfc8785` produced identical canonical UTF-8 bytes (751 bytes) and identical SHA-256 digests.
    - Migration did not alter the digest for the tested Phase 0 report. Application code now strictly imports `rfc8785`.

---

### Hypothesis 5 — Solana Devnet Digest Anchoring
- **Evaluation:** **PARTIAL**
- **Candidate Mechanism:** Solana Memo Program (`MemoSqs4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcY`)
- **Candidate Payload Format:** `KONSYRA:v0.1:<SHA256_HEX_DIGEST>`
- **Empirical Findings:**
  - `solders` transaction assembly (`MessageV0` + `VersionedTransaction`) is implemented as a candidate mechanism; no transaction-assembly unit test currently validates it.
  - Existing unit tests cover digest validation, candidate memo payload formatting, digest extraction from supplied strings, and local digest comparison.
  - SHA-256 digest input validation (`validate_sha256_digest`) enforces exactly 64 hexadecimal characters.
  - Live Devnet submission remains **PARTIAL** because public RPC faucet rate limits prevented funding a fresh test keypair live during the spike. A persistent pre-funded Devnet wallet is required for live testing. ADR-004 remains `PROPOSED`.

---

### Hypothesis 6 — Independent Proof Verification
- **Evaluation:** **PARTIAL**
- **Empirical Findings:**
  - Unit tests prove local digest comparison logic (`verify_proof_digest` returns `True` for matching digests and `False` for tampered digests).
  - Classified as **PARTIAL** because the full end-to-end live flow (`anchor on Devnet -> confirm tx -> retrieve tx -> extract memo -> compare`) was not completed live on chain.
  - Retrieval and Memo extraction from transaction log strings remain candidate mechanisms, unproven against a successful live Konsyra Devnet transaction. Local string extraction tests do not validate RPC retrieval or log parsing.
  - Digest matching establishes representation integrity only, not ledger truth: **Integrity != Truth**.

---

## 4. Summary of Remaining Blockers for Full PASS

1. **Two Real Independent RPC Sources:** Test live collection against two distinct commercial/public RPC providers (e.g., QuickNode + Helius or Alchemy + Triton).
2. **Live Devnet Proof Anchor & Retrieval:** Submit a live Memo transaction to Solana Devnet using a pre-funded test wallet, confirm it, retrieve the transaction by signature via RPC, and verify the extracted digest.

---

## 5. Next Steps

- **Do NOT proceed to Phase 1 yet.**
- Await human review of this Gate C technical experiment pass.
