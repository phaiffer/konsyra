# ADR-003 — JSON Canonicalization Scheme (RFC 8785) for Report Hashing

## Status
PROPOSED

## Context
To produce verifiable on-chain proofs, Konsyra must compute a deterministic SHA-256 digest of its `QualityReport`. However, standard JSON serialization (`json.dumps()` in Python or `JSON.stringify()` in JavaScript) is non-deterministic across different runtimes due to key ordering differences, whitespace formatting, and floating-point number representations.

Relying on non-standard string representations (e.g. `str(dict)`) destroys cross-language reproducibility.

## Decision
We propose adopting **RFC 8785 (JSON Canonicalization Scheme - JCS)** to format the canonical `QualityReport` payload before computing SHA-256 cryptographic digests.

The pipeline will execute:
$$\text{QualityReport Payload} \longrightarrow \text{JCS (RFC 8785)} \longrightarrow \text{UTF-8 Bytes} \longrightarrow \text{SHA-256}$$

This decision is marked **PROPOSED** pending empirical confirmation during the Phase 0 Technical Spike.

## Alternatives Considered
- **Standard `json.dumps(sort_keys=True)`:** Simple, but formatting rules (e.g., whitespace around separators) vary slightly between Python, Node.js, and Rust implementations.
- **Protobuf / CBOR Serialization:** Highly canonical, but less human-readable and introduces additional schema compilation dependencies.

## Consequences

### Positive
- Adheres to an open IETF standard (RFC 8785) supported across major programming languages.
- Guarantees byte-for-byte identical SHA-256 hashes regardless of runtime environment.
- Allows external third parties to independently verify report digests using any JCS library.

### Negative
- Requires strict adherence to JCS string, number, and key-ordering rules during payload construction.

## Revisit When
Phase 0 Technical Spike, to empirically verify JCS serialization consistency between Python backend and verification tooling.
