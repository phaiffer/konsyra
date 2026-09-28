# Konsyra

> **Trust your on-chain data. Prove it.**

Konsyra is an open-source data reliability layer that independently validates and reconciles blockchain-derived data against multiple sources, detects inconsistencies, produces deterministic evidence, and enables the integrity of validation reports to be independently verified.

Developed by [PhaifferTech](https://github.com/phaiffertech) for the **Crypto World's Fair 2026** (Deadline: October 12, 2026).

---

## Project Status

> [!IMPORTANT]
> **Current Phase: Architecture Baseline v0.1 / Technical Spike Planning**
> This repository is currently in the initial design and architectural baseline phase. No production code, API endpoints, or database schemas have been implemented yet. Implementation will begin with **Phase 0 (Solana Validation Spike)**.

---

## Problem

Applications, data pipelines, and indexers consuming blockchain data rely on downstream transformations:

$$\text{Blockchain} \longrightarrow \text{RPC / Indexer} \longrightarrow \text{Parser} \longrightarrow \text{Transformation} \longrightarrow \text{Database} \longrightarrow \text{API / Analytics}$$

Even when the underlying L1/L2 ledger is consistent, derived data layers can introduce:
- Missing slot records or omitted transaction signatures
- Duplicate or out-of-order records
- Stale or delayed observations
- Provider-specific parsing discrepancies

A dataset can pass internal database integrity checks while remaining incomplete relative to the network. Konsyra addresses a fundamental question:

*How do you know the on-chain data your application depends on is actually complete and consistent?*

---

## Approach

Konsyra operates downstream of data providers and indexers, functioning as an independent validator:

```
Source A (RPC / Indexer) ─────┐
                             │
Source B (RPC / Indexer) ─────┼───> [ Konsyra Quality Engine ] ───> Deterministic Evidence
                             │
Target Dataset / Parser ─────┘
```

1. **Provider Agnostic Collection:** Collect observations from two or more independent sources for a given range (e.g., Solana slot range).
2. **Deterministic Reconciliation:** Normalize observations into standardized schemas and run set-reconciliation checks (e.g., matching transaction signature sets per slot).
3. **Explicit Evidence Generation:** Pinpoint exact missing or divergent records without relying on heuristics or artificial quality scores.
4. **On-Chain Cryptographic Proof:** Produce a canonical validation report, hash the payload via SHA-256, and anchor the cryptographic digest on-chain (Solana Devnet) for public verification.

---

## Initial Scope (MVP)

For the Crypto World's Fair 2026 MVP, Konsyra focuses strictly on:
- **Blockchain:** Solana
- **Reconciliation Unit:** Transaction signature set per Solana slot
- **Checks:** Completeness, Uniqueness, Freshness, Reconciliation
- **Proof Mechanism:** Solana Devnet digest anchoring
- **Proof Verification:** Independent validation of report digest against on-chain transaction record

---

## Documentation Roadmap

- **[PRODUCT.md](docs/product/PRODUCT.md):** Core vision, problem definition, product principles, user persona, and positioning.
- **[MVP.md](docs/product/MVP.md):** Scope boundaries, primary user journey, Definition of Done, and hackathon execution guardrails.
- **[ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md):** Detailed system design, container architecture, Quality Engine boundary, canonicalization, and proof models.
- **[Architectural Diagrams](docs/architecture/diagrams/README.md):** Mermaid diagrams for System Context, Container Architecture, Pipeline, and Proof Flow.
- **[Architectural Decision Records (ADRs)](docs/adr/):** Key architectural choices (ADR-001 through ADR-010).
- **[BACKLOG.md](BACKLOG.md):** Phased roadmap from Phase 0 Technical Spike through Hackathon Delivery.
- **[CONTRIBUTING.md](CONTRIBUTING.md):** Guidelines for branching, commit standards, and workflow rules.

---

## License

This project is licensed under the **Apache License 2.0**. See the [`LICENSE`](LICENSE) file for details.

---

*Konsyra is an initiative by PhaifferTech.*
