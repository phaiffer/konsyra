# ADR-005 — Provider-Agnostic Source Adapter Boundary

## Status
ACCEPTED

## Context
Blockchain data providers (Alchemy, QuickNode, Helius, Triton, public Solana RPC nodes) expose different JSON-RPC extension methods, rate-limiting rules, authentication schemes, and custom block formats.

If the core domain or Quality Engine directly invokes HTTP RPC endpoints or parses raw provider JSON, the validation system becomes tightly coupled to specific vendors, breaking provider independence.

## Decision
We decide to establish a strict **Provider-Agnostic Source Adapter Boundary**.

All external provider data must be ingested through dedicated `SourceAdapter` implementations that transform raw RPC responses into a standardized internal `SlotObservation` domain model.

The Quality Engine will never consume raw JSON-RPC responses, HTTP clients, API keys, or provider SDKs directly.

## Alternatives Considered
- **Direct RPC Fetches Inside Quality Engine:** Simplifies early prototype code, but leaks network, authentication, and provider-specific JSON details into core domain logic.
- **Generic Universal Provider Abstraction Library:** Writing a complex third-party multi-chain library upfront leads to overengineering.

## Consequences

### Positive
- Complete isolation of core domain logic from provider API changes, rate limits, or network failures.
- Enables easy addition of new Solana RPC providers or indexers by implementing a clean interface.
- Facilitates unit testing of the Quality Engine using pure mocked `SlotObservation` structs.

### Negative
- Requires maintaining adapter mapping code for each supported RPC provider.

## Revisit When
Phase 2, when implementing contract test suites for initial Solana RPC adapters.
