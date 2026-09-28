# ADR-008 — Rejection of Custom Solana Indexer for MVP

## Status
ACCEPTED

## Context
Building a custom Solana validator node or indexer plugin (e.g. Geyser plugin) to parse raw block files requires significant infrastructure budget, hardware setup, storage capacity, and specialized engineering time.

Konsyra's core value proposition is **independent data validation**, not building alternative data extraction pipelines.

## Decision
We decide to **reject building a custom Solana indexer or Geyser plugin** for the Konsyra MVP.

Konsyra will consume data exclusively from existing standard JSON-RPC endpoints (candidate strategy using `getBlocks` for block discovery and `getBlock` with `transactionDetails="signatures"`; TO BE VALIDATED DURING PHASE 0) provided by commercial or public infrastructure providers.

## Alternatives Considered
- **Custom Geyser Plugin Development:** Provides ultra-fast raw streaming data, but requires managing high-spec Solana validator nodes beyond hackathon resources.
- **Self-Hosted Indexer Stack (e.g., Yellowstone-gRPC):** Powerful streaming alternative, but adds heavy operational setup overhead.

## Consequences

### Positive
- Zero infrastructure maintenance cost for custom Solana validator or streaming nodes.
- Preserves focus entirely on the cross-provider reconciliation layer.
- Allows Konsyra to run efficiently against any standard RPC provider.

### Negative
- Subject to public or commercial RPC rate limits and bandwidth bottlenecks when requesting large slot ranges.

## Revisit When
Post-hackathon, if enterprise users require high-throughput streaming validation via gRPC Geyser feeds.
