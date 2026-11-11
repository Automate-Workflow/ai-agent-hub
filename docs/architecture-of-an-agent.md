# Architecture of an AI Agent

![Agent Anatomy Diagram](../diagrams/agent-anatomy.svg)

A production AI agent combines a foundation reasoning model with curated working context, validated action schemas, persistent memory, security guardrails, and telemetry observability. Rather than treating intelligence solely as a monolithic prompt, modern architectures decompose execution into deterministic software loops surrounding bounded stochastic reasoning steps.

## 1. The Iterative Agent Loop

Stateless single-turn calls ([`PT-001`](patterns.md)) execute one prompt and stop. By contrast, a ReAct or tool-calling agent ([`CP-060`](concepts/CP-060.md), [`CP-022`](concepts/CP-022.md)) alternates model reasoning with external tool execution until an explicit stop criterion or budget guard terminates the run.

![Agent Execution Loop](../diagrams/agent-loop.svg)

### Tool Execution Sequence

```mermaid
sequenceDiagram
    autonumber
    participant U as User / Trigger
    participant G as Input Guardrail & Context Builder
    participant M as LLM Reasoning Core
    participant V as Schema & Policy Validator
    participant H as Human Approval Gate
    participant T as Sandboxed Tool / MCP Server

    U->>G: Submit task request
    G->>G: Screen injection + assemble RAG & memory
    G->>M: Send system policy, messages & tool schemas
    M-->>V: Emit structured tool call + arguments
    V->>V: Validate JSON Schema & least-privilege scope
    alt High-risk mutation or spend
        V->>H: Pause checkpoint & request signoff
        H-->>V: Approved by operator
    end
    V->>T: Dispatch scoped tool execution
    T-->>G: Return tool observation + error/result text
    G->>M: Compact history + feed observation
    M-->>U: Final grounded response + inline citations
```

![Divider](../assets/divider.svg)

## 2. Autonomy Levels & Human Control

Designers explicitly bound how much operational latitude an agent holds based on failure blast radius ([`CP-102`](concepts/CP-102.md)). High-impact mutations require resumable human-in-the-loop interrupts ([`CP-078`](concepts/CP-078.md)), while read-only exploration and verifiable test suites can iterate autonomously inside isolated microVM sandboxes ([`CP-030`](concepts/CP-030.md)).

![Autonomy & Oversight Ladder](../diagrams/autonomy-ladder.svg)

![Divider](../assets/divider.svg)

## 3. Retrieval & Grounding Pipeline

To connect models with fresh, access-controlled institutional knowledge without retraining model weights, agents pair offline ETL ingestion with online hybrid dense/keyword search, cross-encoder reranking, corrective quality evaluation, and cryptographic inline citations ([`CP-035`](concepts/CP-035.md), [`CP-040`](concepts/CP-040.md), [`CP-039`](concepts/CP-039.md), [`CP-136`](concepts/CP-136.md)).

![RAG & Grounding Pipeline](../diagrams/rag-pipeline.svg)

---

**Next Steps:** Explore the 40 concrete classifications in [Agent Types](agent-types.md), inspect the 35 reusable designs in [Design Patterns](patterns.md), or examine [Open Protocols](protocols.md).
