# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added

- Core CSV datasets under `data/`:
  - `data/sources.csv`: 194 primary sources with canonical URLs, reliability ratings, and access dates
  - `data/agent_types.csv`: 40 agent type entries spanning decision logic, role, and architecture lenses
  - `data/frameworks_tools.csv`: 55 agent frameworks and infrastructure tools with verified repository licenses and statuses
  - `data/use_cases.csv`: 83 industry use cases across 18 sectors with qualitative value descriptions and verified mappings
- JSON Schema definition for sources validation: `data/schema/sources.schema.json`
- Foundational documentation in `docs/`: `index.md`, `how-to-read-this-hub.md`, `methodology.md`, `maintenance.md`
- Project governance and policy files: `README.md` (placeholder), `LICENSE` (MIT), `LICENSE-DATA.md` (CC BY 4.0 summary and legal-code link), `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `SUPPORT.md`, `GOVERNANCE.md`, `CITATION.cff`, `ROADMAP.md`
- Repository formatting and GitHub templates: `.editorconfig`, `.gitattributes`, `.gitignore`, `.github/CODEOWNERS`, `.github/FUNDING.yml`, `.github/dependabot.yml`, `.github/PULL_REQUEST_TEMPLATE.md`, and issue forms in `.github/ISSUE_TEMPLATE/`

### Planned (Pre-v1.0.0)

- Remaining CSV datasets (`concepts.csv`, `patterns.csv`, `protocols_standards.csv`, `risks_security.csv`, `evaluation.csv`, `learning_paths.csv`, `resources.csv`, `relationships.csv`, `glossary_aliases.csv`) and corresponding JSON Schemas
- Validation and integrity scripts under `scripts/`
- Hand-crafted SVG diagrams, generated charts, static interactive explorer site, and CI workflows

---

<!-- Released versions will appear below this line once v1.0.0 is tagged. -->
