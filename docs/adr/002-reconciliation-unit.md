# ADR-002 — Transaction Signature Set Per Slot as Primary Reconciliation Unit

## Status
ACCEPTED

## Context
Blockchain data validation can be performed at multiple granularity levels: whole block hashes, full transaction payload byte matching, account balance delta state validation, or transaction signature set matching.

For Solana data pipelines, missing transaction records during indexing or provider RPC ingestion represent a relevant failure mode. Full transaction payload comparison requires massive bandwidth, while block hash comparison alone cannot pinpoint *which* specific transactions were omitted by a provider.

## Decision
We decide to adopt the **transaction signature set per Solana slot** (`Set<string>`) as the primary reconciliation unit for the Konsyra MVP.

Reconciliation will compare signature sets across providers for each slot in a validation range, computing set differences ($\text{Signatures}_A \setminus \text{Signatures}_B$).

## Alternatives Considered
- **Block Header / Blockhash Comparison Only:** Extremely fast, but fails to identify individual omitted transactions if providers return different subsets of a block's transactions.
- **Full Transaction Payload & Account State Diff:** Provides complete state verification, but requires substantial bandwidth, RPC call depth, and complex parsing logic unsuitable for a lean MVP.

## Consequences

### Positive
- Surfaces explicit, actionable evidence (exact missing transaction signatures).
- Significantly reduces payload size and memory overhead compared to full block payload fetching.
- Focuses directly on the primary failure mode of blockchain indexers.

### Negative
- Does not catch deep transaction payload parsing errors (e.g., misparsed inner instruction logs) if the signature itself is present in both sources.

## Revisit When
Phase 3+ if users require deep transaction log or account state delta reconciliation.
