# Product Overview — Konsyra

> **Company:** PhaifferTech
> **Tagline:** Trust your on-chain data. Prove it.
> **Target Event:** Crypto World's Fair 2026 (Deadline: October 12, 2026)

---

## 1. Product Definition

**Konsyra is an open-source data reliability layer that independently validates and reconciles blockchain-derived data against multiple sources, detects inconsistencies, produces deterministic evidence, and enables the integrity of validation reports to be independently verified.**

> [!IMPORTANT]
> **Core Distinction:** Konsyra does not provide blockchain data. Konsyra independently verifies blockchain-derived data regardless of where that data originated.

---

## 2. Problem Statement

Modern Web3 infrastructure depends heavily on off-chain indexing pipelines to transform raw ledger bytes into queryable databases:

$$\text{Blockchain Ledger} \longrightarrow \text{RPC / Indexer} \longrightarrow \text{Parser} \longrightarrow \text{Transformation} \longrightarrow \text{Database} \longrightarrow \text{Application}$$

While the primary blockchain protocol maintains consensus integrity, downstream data systems may experience data inconsistencies:
- **Omitted Transactions:** Indexers or RPC nodes dropping logs or signature records during network congestion or re-indexing.
- **Provider Divergence:** Discrepancies between commercial RPC providers due to node client version differences, custom filtering, or non-standard RPC parsing.
- **Freshness & Latency Gaps:** Downstream databases falling behind block height without alerting application layers.
- **Transformation Inconsistencies:** Custom ETL pipelines misinterpreting complex smart contract log events.

Downstream systems often pass internal schema validations because the ingested data is syntactically valid—yet incomplete.

**The Central Question:**
*How do you know the on-chain data your application depends on is actually complete and consistent?*

---

## 3. Target User Persona

### Primary Persona: Blockchain Data Engineer / Backend Engineer

- **Role:** Maintains data pipelines, indexing services, accounting systems, or analytics databases fed by blockchain RPCs or indexers.
- **Pain Point:** May encounter unexplained missing records in downstream applications, spends hours debugging whether the issue stems from the RPC node, indexer, parser, or database, and lacks independent evidence to prove data integrity to auditors or stakeholders.
- **Need:** An automated, independent validation layer that compares observations across multiple providers, flags missing or inconsistent records immediately, and provides deterministic cryptographic proof of validation runs.

---

## 4. Primary User Story

> **As a blockchain data engineer,**
> **I want to** validate blockchain-derived data against an independent source,
> **so that** I can detect missing or inconsistent records before downstream applications consume incorrect data.

---

## 5. Current Workflow vs. Proposed Workflow

### Current Workflow (Unverified Pipeline)
1. Ingest data from a single RPC endpoint or indexer into PostgreSQL.
2. Run downstream SQL queries assuming 100% completeness.
3. Discover missing transaction records weeks later via user support tickets or accounting reconciliation discrepancies.
4. Manually compare database rows against block explorers without reproducible evidence.

### Proposed Workflow with Konsyra
1. Configure Konsyra with two independent data sources (e.g., Primary RPC + Secondary RPC/Indexer).
2. Konsyra fetches raw observations for a target slot range, normalizes them, and performs set reconciliation.
3. If divergence occurs, Konsyra isolates exact missing signatures and generates an immutable, machine-readable Evidence Report.
4. Konsyra anchors the SHA-256 digest of the canonical report on Solana Devnet.
5. Downstream applications consume validated data or halt pipelines when `QualityStatus == FAIL`.

---

## 6. Value Proposition

- **Independent Verification:** Eliminates single-provider vendor lock-in and trust assumptions.
- **Deterministic Evidence:** Generates exact diffs (e.g., *Signature X missing in Provider B for Slot Y*) rather than vague error messages.
- **Cryptographic Auditability:** Produces canonical SHA-256 report digests anchored on-chain for tamper-evident verification.
- **Early Discrepancy Detection:** Intercepts corrupted or incomplete observations before they pollute analytical warehouses or downstream financial ledgers.

---

## 7. Product Principles

1. **Evidence Before Inference:** Always present explicit, reproducible diffs over probabilistic guesses.
2. **Deterministic Validation Before AI Reasoning:** Core data quality checks must be 100% deterministic and reproducible. AI models must not participate in core validation logic.
3. **Provider Independence:** Konsyra remains strictly neutral and provider-agnostic.
4. **Reproducibility:** Given the same observations and report definition, any party must be able to reproduce the exact canonical payload hash.
5. **Explicit Failure States:** Systems fail and data diverges. Failures must be explicitly typed, never swallowed or hidden behind default fallbacks.
6. **Blockchain Used Only Where It Adds Value:** Blockchain is used exclusively for immutable timestamping and digest anchoring, not as a general database.
7. **Integrity is Not Truth:** An on-chain proof guarantees that a validation report has not been tampered with since creation; it does not guarantee that the underlying providers observed absolute truth.
8. **Keep the Hackathon MVP Small:** Focus strictly on doing one core job exceptionally well—Solana transaction set reconciliation.
9. **Prefer Composition Over Rebuilding:** Rely on standard RPC endpoints and existing infrastructure rather than building custom indexers.
10. **Avoid Unnecessary Distributed Architecture:** Build a clean Modular Monolith first.
11. **Quality Failures vs. System Failures:** Distinguish system execution errors (e.g., HTTP 500) from data quality failures (e.g., missing transaction signature).
12. **Enable Future Evolution Without Premature Feature Bloat:** Design abstractions to accommodate future multi-chain or real-time validation without building them into the initial MVP.

---

## 8. Competitive Positioning

Konsyra occupies a distinct position downstream of data providers and indexers:

```
[ Raw Ledger ] ──> [ RPC Nodes / Indexers ] ──> [ Konsyra Data Reliability ] ──> [ Applications / Data Warehouses ]
```

| Feature / Category | RPC Providers (Alchemy, QuickNode) | Indexers (The Graph, Goldsky) | Data Observability (Monte Carlo, Datadog) | Konsyra |
| :--- | :--- | :--- | :--- | :--- |
| **Primary Function** | Serve RPC responses | Parse and index smart contract state | Monitor DB schemas & table freshness | Independent multi-source data reconciliation |
| **Verification** | Single source | Single indexer pipeline | Internal metrics | Cross-provider set-reconciliation |
| **Evidence Output** | JSON-RPC payload | GraphQL entity | Alert notifications | Canonical Quality Report + On-Chain Proof |
| **On-Chain Proof** | None | None | None | Solana Devnet digest anchoring |

---

## 9. Business Direction & Go-to-Market Hypothesis

- **Phase 1 (Hackathon Open-Source Baseline):** Open-source core engine allowing data engineers to self-host and audit local pipelines.
- **Go-to-Market Hypothesis:** Blockchain data teams managing accounting, DeFi analytics, and bridge monitors experience acute pain around data completeness. Offering a self-hosted validation tool builds developer trust.
- **Future Vision (Post-Hackathon):** Managed reliability API, continuous multi-provider monitoring assertions, and enterprise SLA reporting.

---

## 10. Success Criteria (Hackathon MVP)

1. Successfully reconcile transaction signature sets between two independent Solana sources across a user-defined slot range.
2. Detect controlled transaction omissions using deterministic demo fixtures.
3. Output exact, machine-readable evidence detailing missing signatures.
4. Calculate a stable SHA-256 digest using JSON Canonicalization Scheme (RFC 8785).
5. Successfully anchor the digest to Solana Devnet and independently verify the proof transaction.

---

## 11. Non-Goals (Out of Scope for MVP)

- AI-assisted anomaly detection or RAG agents.
- Multi-chain support (Ethereum, EVM, L2s).
- Custom Solana indexer or custom Solana smart program development.
- Automatic data repair or automated database mutation.
- Synthetic Quality Scores (e.g., "97% Quality Score").

---

## 12. Open Questions (To Be Validated During Phase 0)

1. *Solana Skipped Slots:* How to best distinguish between a legitimately skipped slot (protocol-level empty slot) and a provider failing to return slot data? (TO BE VALIDATED DURING PHASE 0)
2. *RPC Collection Strategy:* Does querying `getBlocks` vs. `getBlock` with `transactionDetails="signatures"` introduce RPC cost/performance bottlenecks over large slot ranges? (TO BE VALIDATED DURING PHASE 0)
3. *Devnet Memo Program Payload:* What is the optimal candidate transaction payload format for Solana Devnet digest anchoring? (TO BE VALIDATED DURING PHASE 0)
