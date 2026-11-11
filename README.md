<p align="center">
  <img src="assets/logo.svg" width="92" alt="AI Agent Hub logo" />
</p>

<h1 align="center">AI Agent Hub</h1>

<p align="center">
  <strong>The standalone, primary-sourced, visual knowledge base for AI agents — types, concepts, architectures, patterns, open protocols, tooling, safety risks, evaluations, and guided learning paths.</strong>
</p>

<p align="center">
  <img src="assets/badges/active.svg" alt="Verified Active" />
  <a href="LICENSE"><img src="https://img.shields.io/badge/Code_License-MIT-B91C1C.svg" alt="MIT Code License" /></a>
  <a href="LICENSE-DATA.md"><img src="https://img.shields.io/badge/Data_%26_Docs-CC_BY_4.0-7F1D1D.svg" alt="CC BY 4.0 License" /></a>
  <a href="docs/index.md"><img src="https://img.shields.io/badge/Docs-Explore_Guides-DC2626.svg" alt="Docs Index" /></a>
</p>

<p align="center">
  <img src="assets/banner.svg" alt="AI Agent Hub Banner" width="100%" />
</p>

<p align="center">
  <a href="docs/architecture-of-an-agent.md">Agent Anatomy</a> ·
  <a href="docs/agent-types.md">Agent Types</a> ·
  <a href="docs/concepts.md">136 Concepts</a> ·
  <a href="docs/patterns.md">35 Patterns</a> ·
  <a href="docs/protocols.md">Open Protocols</a> ·
  <a href="docs/frameworks.md">55 Frameworks</a> ·
  <a href="docs/security.md">Safety & Risks</a> ·
  <a href="docs/learning-paths.md">Learning Paths</a> ·
  <a href="site/index.html">Interactive Explorer</a>
</p>

---

## What Is AI Agent Hub?

AI Agent Hub is an open, standalone, vendor-neutral engineering reference curated around one goal: providing a **verifiable single map** connecting how autonomous AI agents reason, invoke tools, maintain memory, interoperate over open protocols, fail safely, and get evaluated in production.

✅ Every conceptual definition, risk mitigation, framework license, and enterprise use case is backed by explicit `SRC-*` citations in [`data/sources.csv`](data/sources.csv), continuously verified against live links and strict schema validation as of **2026-11-11**.

> **Important Scope Guarantee**: This repository is 100% standalone. It contains no external workflow-vendor lock-in and makes zero references to any sister repository.

![Divider](assets/divider.svg)

## Live Knowledge Base Statistics

All counts and metrics below are regenerated deterministically from the 13 normalized CSV tables in [`data/`](data/README.md) via `scripts/build_docs.py` and `scripts/build_charts.py`:

<!-- STATS:START -->
| Dataset | Rows | Target |
|---|---|---|
| `sources.csv` | 272 | 150+ |
| `concepts.csv` | 136 | 120-160 |
| `agent_types.csv` | 40 | 35-45 |
| `patterns.csv` | 35 | 30+ |
| `protocols_standards.csv` | 16 | 12+ |
| `frameworks_tools.csv` | 55 | 50+ |
| `use_cases.csv` | 83 | 70+ |
| `risks_security.csv` | 42 | 40+ |
| `evaluation.csv` | 32 | 30+ |
| `learning_paths.csv` | 105 | 100+ |
| `resources.csv` | 267 | 150+ |
| `relationships.csv` | 922 | 600+ |
| `glossary_aliases.csv` | 60 | 1+ |
<!-- STATS:END -->

<p align="center">
  <img src="charts/entries-per-dataset.svg" alt="Entries per dataset vs targets" width="49%" />
  <img src="charts/source-reliability-confidence.svg" alt="Source reliability and confidence mix" width="49%" />
</p>

![Divider](assets/divider.svg)

## Agent Anatomy & Execution Loop

A modern agent separates **probabilistic model reasoning** from **deterministic software orchestration, schema enforcement, sandbox isolation, and audit telemetry**.

<p align="center">
  <img src="diagrams/agent-anatomy.svg" alt="Anatomy of a Production AI Agent" width="100%" />
</p>

<p align="center">
  <img src="diagrams/agent-loop.svg" alt="Single Call vs Bounded ReAct Agent Loop" width="100%" />
</p>

```mermaid
sequenceDiagram
    participant Caller
    participant Context as Context & Guardrails
    participant Model as LLM Reasoning Core
    participant Tools as Scoped MCP / Sandbox Tools
    Caller->>Context: Request + Identity Scope
    Context->>Model: System Policy + Grounded RAG + Tool Schemas
    loop Bounded Iteration (max steps & budget)
        Model-->>Tools: Validated JSON Tool Invocation
        Tools-->>Model: Sandboxed Observation Result
    end
    Model-->>Caller: Verified Answer with Source Citations
```

Full walkthrough in [docs/architecture-of-an-agent.md](docs/architecture-of-an-agent.md).

![Divider](assets/divider.svg)

## Taxonomy of AI Agents

Agents are categorized through **three independent lenses** in [`data/agent_types.csv`](data/agent_types.csv) (`AT-001` to `AT-040`) so classical control theory, user domain roles, and runtime coordination architectures remain cleanly separated.

<p align="center">
  <img src="diagrams/agent-landscape.svg" alt="AI Agent Landscape Across 3 Lenses" width="100%" />
</p>

Browse all 40 per-type dossiers in [docs/agent-types.md](docs/agent-types.md).

![Divider](assets/divider.svg)

## Should You Build an Agent? (Engineering Decision Tree)

Before deploying multi-turn autonomous loops, match system complexity strictly to determinism, latency, and blast-radius requirements.

<p align="center">
  <img src="diagrams/decision-tree.svg" alt="Engineering Decision Tree for AI Agents" width="100%" />
</p>

![Divider](assets/divider.svg)

## Core Concept Pillars (`CP-001` to `CP-136`)

Every concept carries an acyclic prerequisite chain, failure pitfalls, primary papers or official documentation, and typed directed edges in the knowledge graph.

| Pillar | Visual Domain | Quick Link |
|---|---|---|
| Foundations & Prompting | ![Foundations](assets/icons/foundations.svg) | [docs/concepts.md](docs/concepts.md) |
| Models & Inference Optimization | ![Models](assets/icons/models.svg) | [docs/concepts.md](docs/concepts.md) |
| Deliberate Reasoning & Search | ![Reasoning](assets/icons/reasoning.svg) | [docs/concepts.md](docs/concepts.md) |
| Tools, Schemas & Code Sandboxes | ![Tools](assets/icons/tools-and-actions.svg) | [docs/concepts.md](docs/concepts.md) |
| Memory Systems & Hybrid RAG | ![Memory](assets/icons/memory-and-knowledge.svg) | [docs/concepts.md](docs/concepts.md) |
| Orchestration & Durable Execution | ![Orchestration](assets/icons/orchestration.svg) | [docs/concepts.md](docs/concepts.md) |
| Wire & Agent Protocols | ![Protocols](assets/icons/protocols.svg) | [docs/protocols.md](docs/protocols.md) |
| Security & Governance Controls | ![Security](assets/icons/safety-and-security.svg) | [docs/security.md](docs/security.md) |
| Evals, Tracing & Operations | ![Evals](assets/icons/evaluation-and-ops.svg) | [docs/evaluation.md](docs/evaluation.md) |
| Multimodal, Browser & Voice UIs | ![Interfaces](assets/icons/interfaces.svg) | [docs/concepts.md](docs/concepts.md) |
| Enterprise Commerce & Compliance | ![Business](assets/icons/business.svg) | [docs/use-cases.md](docs/use-cases.md) |

<p align="center">
  <img src="diagrams/concept-map.svg" alt="AI Agent Concept Map" width="100%" />
</p>

![Divider](assets/divider.svg)

## Design Patterns & Multi-Agent Topologies

Compare all **35 cataloged patterns** ([docs/patterns.md](docs/patterns.md)) from single-turn structured calls and corrective RAG up to centralized supervisors, decentralized swarm handoffs, and durable checkpointing.

<p align="center">
  <img src="diagrams/multi-agent-topologies.svg" alt="Six Multi-Agent Coordination Topologies" width="100%" />
</p>

![Divider](assets/divider.svg)

## Open Protocols & Interoperability Stack

Modern agent stacks converge on **MCP (`PS-001`)** for model-to-tool connectivity, **A2A (`PS-002`)** for cross-vendor agent collaboration, **OAuth 2.1 + PKCE + RFC 9728 (`PS-006`/`PS-014`)** for delegated authorization, **JSON Schema / OpenAPI (`PS-004`/`PS-003`)** for action contracts, and **OpenTelemetry (`PS-007`)** for portable traces.

<p align="center">
  <img src="diagrams/protocol-stack.svg" alt="Open Protocol Stack" width="100%" />
</p>

Full specification matrix in [docs/protocols.md](docs/protocols.md).

![Divider](assets/divider.svg)

## Memory, Retrieval (RAG), Frameworks & Industry Adoption

<p align="center">
  <img src="diagrams/rag-pipeline.svg" alt="Two-Track RAG & Grounding Pipeline" width="100%" />
</p>

<p align="center">
  <img src="charts/frameworks-by-category-oss.svg" alt="Frameworks by category and OSS license" width="49%" />
  <img src="charts/use-cases-by-industry.svg" alt="Industry use cases distribution" width="49%" />
</p>

Explore all 55 audited libraries in [docs/frameworks.md](docs/frameworks.md) and 83 sector workloads in [docs/use-cases.md](docs/use-cases.md).

![Divider](assets/divider.svg)

## Safety, Security, Evaluation & Freshness

Agent security demands defense-in-depth across prompt boundaries, OAuth delegation scopes, microVM sandboxes, memory provenance, and continuous red-teaming ([docs/security.md](docs/security.md), [docs/evaluation.md](docs/evaluation.md)).

<p align="center">
  <img src="diagrams/security-layers.svg" alt="Defense-in-Depth Security Architecture" width="100%" />
</p>

<p align="center">
  <img src="diagrams/risk-heatmap.svg" alt="Risk Likelihood vs Impact Matrix" width="49%" />
  <img src="charts/freshness-status.svg" alt="Freshness and review schedule" width="49%" />
</p>

![Divider](assets/divider.svg)

## Guided Learning Paths & Interactive Explorer

Follow structured roadmaps across **5 role tracks** (`Foundations`, `Builder`, `Architect`, `Security and Governance`, `Team Lead`) backed by **267 verified resources** ([docs/learning-paths.md](docs/learning-paths.md)), or open [`site/index.html`](site/index.html) offline to search every dataset and navigate the interactive relationship graph.

<p align="center">
  <img src="diagrams/learning-roadmap.svg" alt="Five-Track Learning Roadmap" width="100%" />
</p>

![Divider](assets/divider.svg)

## Quick Local Commands (Zero Third-Party Dependencies)

Every validation, integrity, link check, chart generation, and site bundling script runs with Python `3.10+` standard library only:

```bash
# Validate all 13 CSV schemas, confidence rules, dates, and qualitative standards
python scripts/validate_data.py

# Verify cross-references, DAG acyclicity, zero orphan sources, and graph connectivity
python scripts/check_integrity.py

# Regenerate all 8 SVG charts and the data-driven risk heatmap
python scripts/build_charts.py --with-risk-heatmap

# Regenerate marker-managed tables, README stats, and 176 concept/type pages
python scripts/build_docs.py

# Build offline JSON/JS graph and search bundles for site/
python scripts/build_site_data.py
```

![Divider](assets/divider.svg)

## Repository Map & Governance

```text
ai-agent-hub/
├── assets/          # Logo, banner, divider, social card, 11 icons, 6 badges
├── charts/          # 8 deterministic data-driven SVG charts
├── data/            # 13 relational CSV datasets + Draft 2020-12 JSON Schemas
├── diagrams/        # 13 master architectural & risk-matrix SVGs
├── docs/            # Topic guides, 136 concept pages, 40 type pages, methodology
├── reports/         # Reserved ID audit & live HTTP link verification reports
├── scripts/         # 10 Python 3.10+ stdlib validation, link & build scripts
└── site/            # Offline interactive knowledge browser & graph explorer
```

- **Evidence & Citation Rules**: [docs/methodology.md](docs/methodology.md)
- **Review Policy & Maintenance**: [docs/maintenance.md](docs/maintenance.md)
- **Contributing Guide**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Security Policy**: [SECURITY.md](SECURITY.md)
- **Governance & Ownership**: [GOVERNANCE.md](GOVERNANCE.md) — Maintained by `@ayushcmd` ([Automate Workflow](GOVERNANCE.md), `ayush_24a12res897@iitp.ac.in`)

## Licensing

This repository applies clean dual licensing:

- **Code** (`scripts/`, CI workflows, and `site/` code): [MIT License](LICENSE)
- **Data & Documentation** (`data/*.csv`, `docs/`, `diagrams/`, `charts/`, `assets/`, and README prose): [Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE-DATA.md)
