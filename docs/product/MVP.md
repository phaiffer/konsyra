# Hackathon MVP Specification — Konsyra

> **Event:** Crypto World's Fair 2026
> **Submission Deadline:** October 12, 2026
> **Status:** Architecture Scope Boundary (Scope Creep Guardrail)

---

## 1. MVP Objective

Deliver a lean, functional, and audit-ready data reliability layer that proves the feasibility of cross-provider reconciliation and cryptographic digest anchoring on Solana Devnet.

The MVP must demonstrate that two independent data sources reading the same Solana slot range can be deterministically compared, discrepancies explicitly surfaced as machine-readable evidence, and report digests permanently anchored on-chain for tamper-evident verification.

---

## 2. Primary User Journey

$$\text{1. Select Slot Range \& Sources} \longrightarrow \text{2. Collect Observations} \longrightarrow \text{3. Normalize Data} \longrightarrow \text{4. Run Deterministic Checks}$$
$$\downarrow$$
$$\text{5. Reconcile Signatures} \longrightarrow \text{6. Surface Divergence Evidence} \longrightarrow \text{7. Generate Canonical Report} \longrightarrow \text{8. Anchor SHA-256 Digest}$$
$$\downarrow$$
$$\text{9. Retrieve On-Chain Proof} \longrightarrow \text{10. Verify Integrity}$$

---

## 3. Required Checks

The MVP supports **strictly four deterministic checks**:

1. **Completeness Check:** Verifies that all expected slots within the specified `[start_slot, end_slot]` range are observed by each source.
2. **Uniqueness Check:** Verifies that no duplicate transaction signatures exist within a single slot observation.
3. **Freshness Check:** Verifies that slot timestamps fall within an acceptable drift threshold relative to observation time.
4. **Reconciliation Check (Primary MVP Check):** Compares the transaction signature set observed by Source A against Source B for each slot in the validation range.

---

## 4. Reconciliation Unit

- **Target Unit:** Transaction signature set per Solana slot (`Set<string>`).
- **Example Scenario:**

```
Slot: 421928383

Source A Observed Signatures:
  - 5K8...abc
  - 3X9...def
  - 7P2...ghi

Source B Observed Signatures:
  - 5K8...abc
  - 7P2...ghi

Reconciliation Outcome:
  QualityStatus: FAIL
  Divergence Detected:
    missing_in_source_b: ["3X9...def"]
```

---

## 5. Evidence Requirements

When a check fails or detects divergence, Konsyra must output explicit, structured evidence. Generic error messages (e.g., *"Data mismatch detected"*) are **strictly prohibited**.

Evidence payloads must answer three core questions:
1. **WHAT diverged?** (Missing signature array, missing slot ID, timestamp discrepancy).
2. **WHERE did it diverge?** (Exact Solana slot number and blockhash).
3. **BETWEEN WHICH sources?** (Source A ID vs. Source B ID).

---

## 6. Report Requirements

Quality Reports produced by the Quality Engine must be:
- **Deterministic:** Re-running the report generator over identical inputs produces byte-for-byte identical output.
- **Versioned:** Includes `report_schema_version` and `validator_version`.
- **Machine-Readable:** Structured JSON representation.
- **Separated Metadata vs. Canonical Payload:** Volatile execution metadata (e.g., local execution latency, local run UUID) must be decoupled from the canonical hash payload so that hashing remains deterministic across independent validators.

---

## 7. Proof Requirements

- **Network:** Solana Devnet.
- **Mechanism:** Minimal Solana transaction containing the 32-byte SHA-256 digest of the canonical report payload (candidate mechanism: Solana Memo Program or minimal instruction payload; TO BE VALIDATED DURING PHASE 0).
- **Proof Retrieval:** Given the transaction signature on Devnet, Konsyra must retrieve the transaction, extract the memo payload, and confirm it matches the computed SHA-256 hash of the local Quality Report.
- **Principle Enforcement:** The proof verifies **Integrity of Report Representation**, NOT absolute truth of external blockchain state.

---

## 8. Demo Strategy & Modes

To guarantee a bulletproof live hackathon presentation without relying on unpredictable public RPC behavior during judging, Konsyra supports two operational modes:

### 1. LIVE Mode
Queries live RPC nodes (e.g., Solana Mainnet/Devnet endpoints) in real time.

### 2. DETERMINISTIC DEMO FIXTURE Mode
Ingests real, captured Solana slot observations where a transaction signature has been intentionally omitted in a controlled mock provider fixture.

> [!IMPORTANT]
> **Transparency Rule:** The UI and reports must explicitly display a visual indicator when running in `DETERMINISTIC DEMO FIXTURE` mode. Simulating provider discrepancies must be declared transparently and never disguised as a live provider failure.

---

## 9. Definition of Done (DoD)

The MVP is considered **DONE** when the following 12 steps execute reliably:

1. [ ] Configure two independent Solana sources.
2. [ ] Select target Solana slot range.
3. [ ] Collect raw observations from both sources.
4. [ ] Normalize observations into standardized `SlotObservation` structs.
5. [ ] Run deterministic completeness, uniqueness, and freshness checks.
6. [ ] Reconcile transaction signature sets per slot.
7. [ ] Surfacing exact, explicit evidence for any detected divergence.
8. [ ] Generate deterministic Quality Report.
9. [ ] Compute SHA-256 hash of canonical JCS payload (RFC 8785).
10. [ ] Anchor SHA-256 digest on Solana Devnet.
11. [ ] Retrieve proof transaction from Devnet by signature.
12. [ ] Verify retrieved on-chain digest against local report digest.

> [!CAUTION]
> **Freeze Rule:** Once these 12 steps pass reliably, **STOP ADDING FEATURES**. Reallocate all remaining hackathon time to testing, UI/UX refinement, documentation, video recording, and pitch preparation.

---

## 10. Out of Scope for Hackathon MVP

- AI models, LLM agents, RAG pipelines, or ML anomaly detection.
- Multi-chain support (Ethereum, EVM, L2s).
- Custom Solana smart contract / Rust program development.
- Custom indexer / custom RPC node deployment.
- Kafka, Spark, Flink, Airflow, or heavy streaming infrastructure.
- Automatic dataset repair or database mutation.
- Synthetic numerical quality scores (e.g., `Quality = 98.4%`).
- Production mainnet token transaction fees.

---

## 11. Known Risks & Mitigation

| Risk | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| Solana Public RPC Rate Limits | High | Use secondary fallback endpoints & local response caching during testing. |
| Solana Skipped Slot Semantics | Medium | Document protocol skipped slot behavior; validate in Phase 0. |
| Devnet RPC Uninstability | Medium | Support retry logic and fallback to deterministic fixture verification. |

---

## 12. Open Questions (Phase 0 Verification Items)

- `[ ]` Evaluate candidate RPC strategy (`getBlocks` for block discovery and `getBlock` with `transactionDetails="signatures"`) memory consumption and throughput for 100-slot ranges (TO BE VALIDATED DURING PHASE 0).
- `[ ]` Confirm candidate Memo Program byte structure for Devnet anchoring transaction (TO BE VALIDATED DURING PHASE 0).
- `[ ]` Validate JCS canonicalization (RFC 8785) formatting rules in Python (TO BE VALIDATED DURING PHASE 0).
