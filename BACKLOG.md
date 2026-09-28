# Konsyra Project Backlog

This backlog outlines the phased engineering roadmap for Konsyra leading up to the **Crypto World's Fair 2026** deadline (October 12, 2026).

---

## Phase Overview

```
Phase 0: Technical Risk (Solana Spike)  [ NEXT ]
    │
Phase 1: Core Domain Models & Invariants
    │
Phase 2: Source Adapters (Provider Independence)
    │
Phase 3: Quality Engine & Evidence Generation
    │
Phase 4: API Layer (FastAPI)
    │
Phase 5: Persistence Layer (PostgreSQL)
    │
Phase 6: Web Interface (Next.js)
    │
Phase 7: End-to-End Integration & Demo Harness
    │
Phase 8: Hackathon Delivery & Verification
```

---

## Phase 0 — Technical Risk (Solana Validation Spike)

> [!IMPORTANT]
> **Status:** Next Immediate Action (Post-Documentation Baseline).
> **Objective:** Validate the core cryptographic and reconciliation hypotheses on Solana Devnet before committing to web, API, or database infrastructure.

### Technical Spike Flow
$$\text{Query Source A} \longrightarrow \text{Query Source B} \longrightarrow \text{Normalize} \longrightarrow \text{Reconcile Signatures} \longrightarrow \text{Report} \longrightarrow \text{Canonical JCS Payload} \longrightarrow \text{SHA-256} \longrightarrow \text{Anchor Devnet} \longrightarrow \text{Retrieve} \longrightarrow \text{Verify Digest}$$

### Deliverables
- Minimal CLI script querying two independent Solana sources for a specified slot range.
- Verification of slot observation normalization schema.
- Deterministic transaction signature set reconciliation implementation.
- Spike verification of report payload canonicalization (JCS / RFC 8785) and SHA-256 hashing.
- Candidate minimal Solana transaction digest anchoring on Solana Devnet (evaluating Solana Memo Program or equivalent instruction; TO BE VALIDATED DURING PHASE 0).
- Independent retrieval and verification script demonstrating on-chain proof validation.

### Entry Condition
- Architecture Baseline v0.1 approved.

### Exit Condition (PASS / FAIL Evaluation)
- **PASS Criteria:**
  1. Two independent Solana sources successfully queried for identical slot ranges.
  2. Raw provider responses successfully mapped to normalized `SlotObservation` structs.
  3. Signature set reconciliation accurately detects matched vs. missing transaction signatures.
  4. Generated quality report produces an identical SHA-256 hash across multiple runs.
  5. Digest successfully submitted and confirmed on Solana Devnet.
  6. Devnet transaction successfully retrieved by signature and on-chain memo payload verified against local SHA-256 digest.
- **FAIL Criteria:** One or more central technical hypotheses cannot be demonstrated reliably enough to support MVP implementation.

### Non-Goals
- No web frontend, REST API, ORM, or PostgreSQL storage in Phase 0.

---

## Phase 1 — Core Domain Models & Invariants

### Objective
Establish pure Python domain entities, aggregate boundaries, and validation state machines without external infrastructure dependencies.

### Major Deliverables
- `ValidationRun` aggregate root and state machine (`PENDING` $\rightarrow$ `COLLECTING` $\rightarrow$ `VALIDATING` $\rightarrow$ `REPORT_READY` $\rightarrow$ `ANCHORED`).
- `ExecutionStatus` vs. `QualityStatus` (`PASS`, `FAIL`, `INCONCLUSIVE`) separation.
- Immutable domain value objects (`ValidationRange`, `SlotObservation`, `CheckResult`, `Divergence`, `Proof`).
- Comprehensive unit test suite for domain invariants.

### Entry Condition
- Phase 0 Technical Spike evaluated as **PASS**.

### Exit Condition
- Domain models implemented as pure, framework-agnostic Python classes with comprehensive unit coverage of domain invariants and state transitions.

---

## Phase 2 — Source Adapter Boundary

### Objective
Build provider-agnostic source adapters isolating raw provider formats, RPC rate limits, and network errors from core domain logic.

### Major Deliverables
- `SourceAdapter` abstract interface definition.
- Primary Solana RPC adapter (candidate strategy: `getBlocks` for block discovery and `getBlock` with `transactionDetails="signatures"`; TO BE VALIDATED DURING PHASE 0).
- Secondary Solana RPC / Indexer adapter (e.g., Helius, QuickNode, or secondary RPC).
- Provider response normalization transformer mapping to `SlotObservation`.
- Controlled error handling for network timeouts, provider rate limits, and RPC failures.

### Entry Condition
- Phase 1 domain models complete.

### Exit Condition
- Adapters pass contract tests against mocked responses and live testnet/devnet endpoints.

---

## Phase 3 — Quality Engine & Evidence Model

### Objective
Construct the deterministic Quality Engine executing checks and producing structured evidence payloads.

### Major Deliverables
- `QualityEngine` executor executing checks: Completeness, Uniqueness, Freshness, Reconciliation.
- Set-reconciliation engine for Solana slot transaction signatures.
- `Evidence` model detailing: *WHAT diverged*, *WHERE it diverged* (slot ID), and *BETWEEN WHICH sources*.
- Deterministic `QualityReport` generator.
- Payload canonicalization engine (RFC 8785) producing stable SHA-256 report digests.

### Entry Condition
- Phase 2 Source Adapters complete.

### Exit Condition
- Quality engine deterministic execution verified by unit tests across identical observations producing identical hashes.

---

## Phase 4 — API Layer

### Objective
Expose validation run lifecycle and proof operations via a modular FastAPI REST interface.

### Major Deliverables
- `POST /api/v1/validations` — Initiate a validation run.
- `GET /api/v1/validations/{id}` — Fetch run status and summary.
- `GET /api/v1/validations/{id}/report` — Retrieve full canonical Quality Report.
- `POST /api/v1/validations/{id}/anchor` — Submit report digest to Solana Devnet.
- `GET /api/v1/proofs/{signature}` — Fetch and verify on-chain proof details.

### Entry Condition
- Phase 3 Quality Engine complete.

### Exit Condition
- OpenAPI schema validated; contract integration tests passing.

---

## Phase 5 — Persistence Layer

### Objective
Implement relational persistence for validation history, observations, reports, and proofs using PostgreSQL.

### Major Deliverables
- Relational schema tables (`validation_runs`, `validation_sources`, `slot_observations`, `transaction_observations`, `check_results`, `quality_reports`, `proofs`).
- Repository interface implementations for `ValidationRun` storage.
- Alembic migration scripts.

### Entry Condition
- Phase 4 API contracts defined.

### Exit Condition
- Database repository tests pass cleanly against PostgreSQL container.

---

## Phase 6 — Web Interface

### Objective
Develop a modern, high-contrast Next.js web application for configuring runs, viewing live reconciliation evidence, and inspecting on-chain proofs.

### Major Deliverables
- Validation Configuration interface (Slot range, provider selection).
- Execution Progress view with state indicator (`COLLECTING`, `VALIDATING`, etc.).
- Evidence Explorer displaying side-by-side transaction signature diffs.
- Proof Inspector with direct links to Solana Explorer (Devnet).

### Entry Condition
- Phase 4 API and Phase 5 Persistence complete.

### Exit Condition
- Web interface communicates cleanly with FastAPI backend; full user journey executable from UI.

---

## Phase 7 — End-to-End Integration & Demo Harness

### Objective
Integrate all components into a modular monolith and create deterministic demo fixtures.

### Major Deliverables
- End-to-end integration test suite verifying full flow from trigger to on-chain proof.
- Deterministic Demo Fixture harness simulating provider discrepancies using captured real Solana slot data.
- Transparency UI toggle explicitly distinguishing LIVE provider runs from DETERMINISTIC DEMO runs.

### Entry Condition
- Phase 6 Web Interface complete.

### Exit Condition
- E2E tests pass reliably; demo harness works without external network dependency.

---

## Phase 8 — Hackathon Delivery & Verification

### Objective
Finalize submission package, pitch deck, documentation, and video demonstration for Crypto World's Fair 2026.

### Major Deliverables
- Final codebase audit and documentation polish.
- Production-ready README, architecture diagrams, and submission video.
- Verified test suite and zero open critical bugs.

### Entry Condition
- Phase 7 complete.

### Exit Condition
- Hackathon submission submitted before **2026-10-12**.
