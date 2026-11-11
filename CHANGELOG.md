# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] — 2026-11-11

### Added

- **Complete Relational Knowledge Base (`data/`)**: 13 validated CSV datasets totaling **2,065 rows** governed by strict JSON Schema Draft 2020-12 definitions and cross-referential integrity guarantees:
  - `data/sources.csv`: **272** primary and secondary references verified against live URLs (`234` primary, `38` secondary)
  - `data/concepts.csv`: **136** core concepts (`CP-001` to `CP-136`) across 11 categories with acyclic prerequisite DAGs
  - `data/agent_types.csv`: **40** agent types spanning `decision_logic`, `job`, and `architecture` views
  - `data/patterns.csv`: **35** design patterns linked directly to master SVG architecture diagrams
  - `data/protocols_standards.csv`: **16** transport, schema, auth, tool (`MCP`), agent (`A2A`), commerce (`ACP`), observability (`OTel`), and governance specifications
  - `data/frameworks_tools.csv`: **55** audited frameworks, vector databases, tracers, eval tools, sandboxes, and inference tools with verified licenses
  - `data/use_cases.csv`: **83** industry use cases across 15 sectors with qualitative expected value and mapped risks
  - `data/risks_security.csv`: **42** risk entries covering OWASP LLM 2025, OWASP Agentic Top 10 (`ASI01`–`ASI10`), MITRE ATLAS, NIST AI RMF / 600-1 / 100-2e2025, and EU AI Act obligations
  - `data/evaluation.csv`: **32** metrics, testing methods, standard benchmarks, tooling suites, and CI processes
  - `data/learning_paths.csv`: **105** progressive steps across 5 role tracks (`Foundations`, `Builder`, `Architect`, `Security and Governance`, `Team Lead`)
  - `data/resources.csv`: **267** curated learning resources spanning docs, papers, courses, books, videos, repos, specs, tools, and newsletters
  - `data/relationships.csv`: **922** directed typed edges across all 10 allowed relation verbs with zero isolated core nodes
  - `data/glossary_aliases.csv`: **60** synonym and acronym mappings to canonical entity IDs
- **Standard-Library Automation (`scripts/`)**: 10 zero-dependency Python `3.10+` scripts for schema validation, integrity checking, HTTP link auditing, chart generation, doc synthesis, graph building, site bundling, and summary telemetry
- **Red-Theme Visual System (`assets/`, `diagrams/`, `charts/`)**:
  - 21 brand SVGs (`logo.svg`, `banner.svg`, `divider.svg`, `social-preview.svg`, 11 `64x64` category icons with `2.5px` strokes, 6 status/difficulty badges)
  - 13 master SVG architecture diagrams in `diagrams/` including the data-driven `risk-heatmap.svg`
  - 8 data-driven SVG charts in `charts/`
- **Comprehensive Documentation (`README.md`, `docs/`)**: Full visual `README.md`, 10 overview guides with embedded Mermaid diagrams, guides on methodology and maintenance, plus 176 auto-generated concept and agent-type pages
- **Offline Interactive Explorer (`site/`)**: Zero-CDN static web explorer featuring global search with alias resolution, multi-facet filters, clickable detail inspector, pan/zoom neighborhood Knowledge Graph canvas, and persistent `localStorage` learning path tracker
- **CI Automation (`.github/workflows/`)**: SHA-pinned GitHub Actions workflows for schema/integrity validation, weekly link checks, artifact build checks, and GitHub Pages deployment
- **Governance & Dual Licensing**: `LICENSE` (MIT for code), `LICENSE-DATA.md` (CC BY 4.0 for data and documentation), `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `SUPPORT.md`, `GOVERNANCE.md`, `CITATION.cff` (`v1.0.0`), and `ROADMAP.md`
