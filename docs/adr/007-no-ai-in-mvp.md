# ADR-007 — Strict Exclusion of AI / LLMs from Core Validation Engine

## Status
ACCEPTED

## Context
Many modern software projects incorporate artificial intelligence (LLMs, RAG, machine learning anomaly detection) into their core logic. However, LLMs are probabilistic, non-deterministic, and prone to hallucinations.

Data reliability and cryptographic auditability require 100% deterministic, mathematically reproducible verification. Incorporating AI into validation decisions undermines trust in audit reports.

## Decision
We decide to **strictly exclude AI, LLMs, and machine learning models** from the core validation engine, evidence generation, canonicalization, and proof workflows of Konsyra.

All validation logic must rely exclusively on deterministic set operations, explicit schema checks, and cryptographic hashing algorithms.

## Alternatives Considered
- **LLM-Based Anomaly Explanations:** Using an LLM to summarize why data diverged. Rejected for MVP because non-deterministic text generation can introduce misleading or inaccurate audit claims.
- **ML-Based Heuristic Data Quality Scoring:** Using machine learning to predict data completeness scores. Rejected in favor of exact set reconciliation.

## Consequences

### Positive
- Guarantees 100% deterministic, reproducible validation results across all runs.
- Maintains mathematical rigour and audit credibility required for data reliability software.
- Eliminates external LLM API cost, latency, and rate-limit risks.

### Negative
- Excludes promotional "AI-powered" marketing buzzwords for the hackathon.

## Revisit When
Post-hackathon, strictly as an optional natural language UI commentary layer built on top of—never inside—the deterministic evidence payload.
