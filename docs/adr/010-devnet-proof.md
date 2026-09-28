# ADR-010 — Solana Devnet Network Selection for Hackathon Proof Anchoring

## Status
ACCEPTED

## Context
Konsyra anchors report SHA-256 digests on-chain to enable independent proof verification. Submitting transactions on Solana Mainnet-Beta requires real SOL tokens, mainnet wallet key management, risk of mainnet transaction fee volatility, and security risks during developer testing.

For the **Crypto World's Fair 2026** MVP, the proof mechanism must demonstrate full functional protocol anchoring without incurring mainnet transaction costs or managing production wallet funds.

## Decision
We decide to target **Solana Devnet** exclusively for report digest proof anchoring in the Konsyra MVP.

Fee-payer wallets used during development and hackathon demonstrations will use isolated Devnet test keypairs funded via Devnet faucets.

## Alternatives Considered
- **Solana Mainnet-Beta Anchoring:** Demonstrates mainnet execution, but introduces real capital costs, wallet security risks, and unnecessary overhead for a hackathon MVP.
- **Localnet (Local Solana Test Validator):** Fast for unit tests, but does not allow independent judges to verify proofs via public block explorers over the internet.

## Consequences

### Positive
- Zero production financial cost and zero risk of real fund loss.
- Allows judges and external users to verify transactions on public Solana Devnet explorers (e.g., Solscan Devnet / Solana Explorer Devnet).
- Completely isolates proof wallet secrets from production environments.

### Negative
- Devnet RPC nodes occasionally experience reset periods or transient network congestion.

## Revisit When
Post-hackathon (Phase 9+), when introducing optional Mainnet-Beta anchoring for production enterprise customers.
