# ADR-004 — Minimal Solana Transaction Anchoring for Verification Proofs

## Status
PROPOSED

## Context
Konsyra requires a mechanism to anchor validation report SHA-256 digests on-chain so that report existence and immutability can be independently verified. Developing a custom Solana smart program (in Rust/Anchor) introduces deployment overhead, security audit requirements, and unnecessary complexity for the MVP.

The MVP needs a lightweight, reliable method to commit a 32-byte hash payload to the Solana ledger.

## Decision
We propose utilizing **minimal Solana transaction digest anchoring** (evaluating the standard Solana Memo Program `MemoSqs4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcY` or equivalent minimal instruction) on **Solana Devnet**.

The transaction payload will encode the format: `KONSYRA:v0.1:<SHA256_HEX_DIGEST>`.

This decision is marked **PROPOSED** pending technical confirmation during the Phase 0 Technical Spike.

## Alternatives Considered
- **Custom Solana Program (Rust/Anchor):** Offers custom on-chain state storage, but adds significant engineering risk and deployment friction for a hackathon MVP.
- **Off-Chain IPFS / Arweave Storage Only:** Decentralized, but does not provide immediate transaction confirmation timestamps on the target Solana ledger.

## Consequences

### Positive
- Zero custom smart contract code to deploy, audit, or maintain.
- Reuses Solana's standard Memo Program infrastructure.
- Inexpensive transaction fee cost and instant confirmation on Devnet.

### Negative
- Proof payload is immutable on-chain text, requiring off-chain indexers or RPC fetch calls to inspect.

## Revisit When
Phase 0 Technical Spike, to empirically test Memo transaction submission, confirmation latency, and payload retrieval via standard RPC.
