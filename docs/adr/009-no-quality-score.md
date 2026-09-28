# ADR-009 — Explicit Quality Status Over Arbitrary Numerical Quality Score

## Status
ACCEPTED

## Context
Many data quality monitoring tools output synthetic numerical scores (e.g., `Data Quality Score = 97.4%`).

In blockchain data pipelines, arbitrary percentage scores create a false sense of security. A dataset missing 2% of transaction signatures might receive a "98% Quality Score", yet fail completely for accounting, auditing, or smart contract execution.

A single missing transaction can invalidate financial state balance calculations.

## Decision
We decide to **prohibit arbitrary numerical quality scores** in Konsyra.

Instead, Konsyra will strictly output explicit, discrete `QualityStatus` results:
- **`PASS`:** All deterministic checks passed with zero discrepancies found across sources.
- **`FAIL`:** One or more deterministic checks detected divergence (e.g., missing transaction signature).
- **`INCONCLUSIVE`:** Observations could not be fully reconciled due to provider slot data unavailability.

## Alternatives Considered
- **Weighted Percentage Quality Score (0 - 100%):** User-friendly vanity metric, but misleading and non-rigorous for cryptographic data validation.
- **Graded Letter Scale (A, B, C, F):** Subjective and ambiguous.

## Consequences

### Positive
- Enforces rigorous binary data integrity standards required for financial and audit workloads.
- Eliminates subjective thresholds or artificial quality heuristics.
- Forces explicit surfacing of exact missing record evidence when status is `FAIL`.

### Negative
- Users accustomed to high-level percentage dashboards must adapt to strict status outcomes.

## Revisit When
Never. Arbitrary percentage scores contradict Konsyra's core product principle (*Evidence Before Inference*).
