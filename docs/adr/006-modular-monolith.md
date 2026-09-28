# ADR-006 — Modular Monolith System Architecture

## Status
ACCEPTED

## Context
Designing early-stage software with microservices, event buses (e.g., Kafka), and distributed workers introduces operational overhead, network latency, distributed state management challenges, and deployment friction.

For the Konsyra MVP and hackathon delivery, system complexity must be minimized while maintaining clean code boundaries for future evolution.

## Decision
We decide to adopt a **Modular Monolith** architecture pattern for Konsyra.

The application will be built as a single deployable Python service (FastAPI) structured into distinct internal modules (`adapters`, `quality_engine`, `evidence_engine`, `proof_adapter`, `persistence`). Inter-module communication will occur via strictly typed Python interfaces rather than network calls.

## Alternatives Considered
- **Microservices Architecture:** Splitting ingestion, quality validation, and proof anchoring into separate microservices. Rejected due to high operational complexity and risk of missing hackathon deadlines.
- **Event-Driven Architecture with Message Queues (Kafka/RabbitMQ):** Introduces heavy infrastructure requirements unsuitable for a lean MVP.

## Consequences

### Positive
- Single codebase, simple local testing, and straightforward deployment.
- High developer velocity and fast iteration cycles during hackathon preparation.
- Clear module boundaries allow future extraction of microservices if scale demands it later.

### Negative
- Monolithic deployment requires scaling all components together initially.

## Revisit When
Post-hackathon (Phase 9+), if validation volume requires decoupled asynchronous worker pools.
