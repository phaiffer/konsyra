# Konsyra Architectural Diagrams

This directory contains visual architecture models for Konsyra using standard [Mermaid.js](https://mermaid.js.org/) notation. These diagrams are rendered directly within GitHub Markdown.

---

## 1. System Context Diagram (C4 Level 1)

Describes how Konsyra fits into the broader Web3 data ecosystem alongside engineers, data sources, and the Solana network.

```mermaid
graph TD
    User["👤 Blockchain Data Engineer"]

    subgraph Konsyra System
        Engine["🛡️ Konsyra Data Reliability Layer"]
    end

    subgraph External Data Providers
        SourceA["⚡ Solana Source A (Primary RPC)"]
        SourceB["⚡ Solana Source B (Secondary RPC/Indexer)"]
    end

    subgraph Blockchain Ledger
        Devnet["⛓️ Solana Devnet (Proof Ledger)"]
    end

    User -->|"Configures runs & inspects evidence"| Engine
    Engine -->|"Queries slot observations & signatures"| SourceA
    Engine -->|"Queries slot observations & signatures"| SourceB
    Engine -->|"Anchors SHA-256 digest & verifies proof"| Devnet
```

---

## 2. Container Architecture Diagram (C4 Level 2 — Planned Stack)

Illustrates the internal modular monolith structure, component boundaries, and persistence layer.

```mermaid
graph TB
    subgraph Client Layer
        WebUI["🖥️ Next.js Web Application (React / TypeScript)"]
    end

    subgraph Backend Application (FastAPI Modular Monolith)
        API["🔌 REST API Router (FastAPI)"]

        subgraph Internal Domain Modules
            AdapterMod["🔌 Source Adapter Boundary"]
            QualityMod["⚙️ Quality & Evidence Engine"]
            ProofMod["⛓️ Solana Proof Module"]
        end
    end

    subgraph Storage
        Postgres[(🗄️ PostgreSQL Database)]
    end

    subgraph External Systems
        ProviderA["Source A RPC"]
        ProviderB["Source B RPC"]
        SolanaDevnet["Solana Devnet"]
    end

    WebUI -->|"REST / JSON"| API
    API -->|"Persists runs, reports & proofs"| Postgres
    API -->|"Triggers ingestion"| AdapterMod
    API -->|"Executes checks"| QualityMod
    API -->|"Triggers anchoring"| ProofMod

    AdapterMod -->|"JSON-RPC"| ProviderA
    AdapterMod -->|"JSON-RPC"| ProviderB
    ProofMod -->|"Memo Transaction"| SolanaDevnet
```

---

## 3. Validation Pipeline Flow Diagram

Illustrates the step-by-step lifecycle of a validation run from provider data ingestion to report canonicalization.

```mermaid
sequenceDiagram
    autonumber
    actor Engineer as Data Engineer / API
    participant Adapter as Source Adapters
    participant Quality as Quality Engine
    participant Evidence as Evidence Engine
    participant Canon as Canonicalizer (RFC 8785)
    participant Solana as Solana Devnet

    Engineer->>Adapter: Trigger validation (start_slot, end_slot)
    par Fetch Source A
        Adapter->>Adapter: Query Source A observations
    and Fetch Source B
        Adapter->>Adapter: Query Source B observations
    end
    Adapter-->>Quality: Deliver normalized SlotObservations

    Quality->>Quality: Run Completeness, Uniqueness & Freshness Checks
    Quality->>Quality: Reconcile Transaction Signature Sets per Slot

    alt Divergence Detected
        Quality->>Evidence: Flag missing signatures
        Evidence-->>Quality: Output explicit diff evidence payload
    end

    Quality->>Canon: Generate Quality Report & Canonicalize JCS
    Canon->>Canon: Compute SHA-256 Digest
    Canon-->>Engineer: Return QualityReport + SHA-256 Digest

    Engineer->>Solana: Submit SHA-256 Digest via Memo Transaction
    Solana-->>Engineer: Return Transaction Signature (Proof)
```

---

## 4. Solana Proof Anchoring & Verification Flow Diagram

Shows how cryptographic report digests are anchored on-chain and independently verified.

> [!NOTE]
> The Solana Memo Program is the **candidate / proposed** anchoring mechanism (see ADR-004). Final transaction and memo payload structure is **TO BE VALIDATED DURING PHASE 0**.

```mermaid
flowchart LR
    subgraph Local Environment
        Report["📄 Quality Report"] --> Canon["JCS Serialization (RFC 8785)"]
        Canon --> LocalHash["🔒 SHA-256 Digest (Digest A)"]
    end

    subgraph Solana Devnet Ledger
        LocalHash -->|"Memo Transaction Payload"| Tx["⛓️ Solana Transaction"]
        Tx --> Block["📦 Confirmed Block"]
    end

    subgraph Independent Verifier
        TxSig["🔑 Transaction Signature"] --> FetchTx["Fetch Tx from Devnet"]
        FetchTx --> ExtractMemo["Extract Memo String"]
        ExtractMemo --> OnChainHash["🔑 Extracted SHA-256 (Digest B)"]

        LocalHash --> Match{"Digest A == Digest B?"}
        OnChainHash --> Match
        Match -->|YES| Valid["✅ INTEGRITY VERIFIED"]
        Match -->|NO| Invalid["❌ INTEGRITY FAILED"]
    end
```
