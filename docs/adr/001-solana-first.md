# ADR-001 — Target Solana as Initial Blockchain Target

## Status
ACCEPTED

## Context
Konsyra is an open-source data reliability layer designed to reconcile blockchain-derived data across multiple independent sources. To deliver a compelling MVP for the **Crypto World's Fair 2026** within a constrained timeframe, the project must select a single high-throughput target blockchain network rather than attempting multi-chain support prematurely.

Solana presents unique data reliability challenges for data engineers: high transaction volume, fast slot times (~400ms), slot skips by cluster leaders, and variations in RPC provider index caching.

## Decision
We decide to focus strictly on **Solana** as the initial blockchain network target for the Konsyra MVP. Multi-chain support (e.g., Ethereum, EVM L2s) is explicitly deferred to post-hackathon releases.

## Alternatives Considered
- **Ethereum Mainnet / EVM L2s:** Slower block times and lower transaction density per block make set-reconciliation less latency-sensitive during short demonstration runs.
- **Multi-Chain Scope from Day 1:** Introducing abstract multi-chain interfaces upfront increases engineering complexity and dilutes focus on the core Solana reconciliation wedge.

## Consequences

### Positive
- Concentrates engineering effort on a single, high-throughput ecosystem with real data reliability pain points.
- Allows optimization of domain entities (`SlotObservation`, slot ranges) specifically around Solana slot semantics.
- Keeps hackathon scope tightly focused and executable before deadline.

### Negative
- Applications requiring Ethereum or EVM L2 data verification cannot use Konsyra in Phase 0/MVP.
- Domain models must be audited later when expanding to non-slot block architectures.

## Revisit When
Post-hackathon (Phase 9+), when expanding Konsyra to support EVM-based blockchains.
