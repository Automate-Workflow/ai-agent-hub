# Data Dictionary (`data/`)

This directory contains the normalized, relational CSV datasets and JSON Schemas backing AI Agent Hub.

---

## Global Conventions

- **Encoding and Line Endings**: All files use UTF-8 without BOM and LF (`\n`) line endings.
- **CSV Quoting**: Standard RFC 4180 CSV with comma delimiter, double quotes (`"`) around fields containing commas or quotes.
- **List Separator**: Multi-value ID or topic columns MUST use the pipe character (`|`) with no spaces around pipes (for example, `CP-001|CP-004`). Commas or semicolons inside ID list fields are rejected by `scripts/validate_data.py`.
- **Date Format**: ISO 8601 `YYYY-MM-DD` (verified against `2026-11-11`). In `sources.csv`, `published_date` may be `""` (empty string) when an exact day is not confirmed at the source; synthetic `-01` placeholder days are forbidden.
- **ID Formats**: IDs are permanent and never reused even if a row is deprecated or removed:
  - `concepts.csv`: `CP-NNN` (e.g. `CP-001`)
  - `agent_types.csv`: `AT-NNN` (e.g. `AT-001`)
  - `patterns.csv`: `PT-NNN` (e.g. `PT-001`)
  - `protocols_standards.csv`: `PS-NNN` (e.g. `PS-001`)
  - `frameworks_tools.csv`: `FW-NNN` (e.g. `FW-001`)
  - `use_cases.csv`: `UC-NNN` (e.g. `UC-001`)
  - `risks_security.csv`: `RS-NNN` (e.g. `RS-001`)
  - `evaluation.csv`: `EV-NNN` (e.g. `EV-001`)
  - `learning_paths.csv`: `LP-NNN` (e.g. `LP-001`)
  - `resources.csv`: `RES-NNN` (e.g. `RES-001`)
  - `relationships.csv`: `RL-NNNN` (e.g. `RL-0001`)
  - `sources.csv`: `SRC-NNNN` (e.g. `SRC-0001`)
  - `glossary_aliases.csv`: Maps string `alias` to `canonical_id` (no separate prefix)

### Confidence Values

| Value | Meaning |
|---|---|
| `high` | Directly verified by at least one `primary` source (`official_docs`, `standard`, `paper`, `book`, `repo`, or vendor engineering/specification doc in `sources.csv`) supporting the exact claim. |
| `medium` | Supported by `secondary` sources or inferred from closely related primary docs without exact terminology match. |
| `low` | Supported by a single weak/tertiary source or provisional evidence pending primary verification. |

### Status Values

| Value | Meaning |
|---|---|
| `active` | Verified against listed sources and within `next_review_date`. |
| `needs-review` | Past `next_review_date`, weakly sourced, or flagged for verification. |
| `deprecated` | Superseded, shut down, archived, or rebranded (kept with explanatory notes). |

### Review Window Policy

- **90 days**: `frameworks_tools.csv`, `protocols_standards.csv` (fast-moving tooling and specs).
- **180 days**: `agent_types.csv`, `patterns.csv`, `use_cases.csv`, `risks_security.csv`.
- **365 days**: `concepts.csv`, `evaluation.csv`, `resources.csv` (foundational concepts and stable benchmarks/guides).

---

## Dataset Schemas

### 1. `data/sources.csv` (`data/schema/sources.schema.json`)

| Column | Required | Type / Allowed Values | Description |
|---|---|---|---|
| `id` | Yes | `SRC-NNNN` | Unique permanent source ID. |
| `title` | Yes | String (1..512) | Document, paper, repo, or specification title. |
| `publisher` | Yes | String (1..256) | Organization or venue. |
| `author` | Yes | String (1..512) | Author(s) or organization (`et al.` for 3+). |
| `url` | Yes | Canonical HTTP/HTTPS URI | Verified live canonical URL. Duplicate URLs require an `alias_of: SRC-NNNN` marker in `notes`. |
| `source_type` | Yes | `official_docs` \| `paper` \| `standard` \| `book` \| `course` \| `report` \| `blog` \| `repo` | Material type. |
| `published_date` | Yes | `YYYY-MM-DD` or `""` | Exact publication date if known; `""` if unknown. |
| `accessed_date` | Yes | `YYYY-MM-DD` | Date last checked live. |
| `reliability` | Yes | `primary` \| `secondary` \| `tertiary` | Evidence tier (`high` confidence requires >= 1 `primary`). |
| `notes` | Yes | String (0..1024) | Scope, deprecation, archival, or `alias_of:` annotation. |

### 2. `data/concepts.csv` (`data/schema/concepts.schema.json`)

| Column | Required | Type / Allowed Values | Description |
|---|---|---|---|
| `id` | Yes | `CP-NNN` | Concept identifier. |
| `term` | Yes | String (2..120) | Canonical term. |
| `category` | Yes | `foundations` \| `reasoning` \| `tools_and_actions` \| `memory_and_knowledge` \| `orchestration` \| `protocols` \| `safety_and_security` \| `evaluation_and_ops` \| `models` \| `interfaces` \| `business` | Domain group. |
| `definition` | Yes | String (10..280) | Plain-language definition (strict max 280 chars). |
| `why_it_matters` | Yes | Qualitative prose | Relevance to AI agent engineering (no uncited metrics). |
| `how_it_works` | Yes | String | Mechanism summary. |
| `common_mistakes` | Yes | String | Frequent engineering or conceptualization errors. |
| `example` | Yes | String | Concrete illustrative example. |
| `related_ids` | No (`""`) | Pipe-separated entity IDs | Related entries (`CP-*`, etc.). |
| `prerequisite_ids` | No (`""`) | Pipe-separated `CP-NNN` | Conceptual prerequisites (acyclic). |
| `difficulty` | Yes | `beginner` \| `intermediate` \| `advanced` | Conceptual level. |
| `source_ids` | Yes | Pipe-separated `SRC-NNNN` | Supporting sources. |
| `confidence`, `status` | Yes | Enum | Verification metadata. |
| `verified_date`, `next_review_date` | Yes | `YYYY-MM-DD` | Freshness dates (365-day policy window). |

### 3. `data/agent_types.csv` (`data/schema/agent_types.schema.json`)

| Column | Required | Type / Allowed Values | Description |
|---|---|---|---|
| `id` | Yes | `AT-NNN` | Agent type identifier. |
| `name` | Yes | String (2..120) | Snake_case or canonical type name. |
| `view` | Yes | `decision_logic` \| `job` \| `architecture` | Classification lens. |
| `parent_id` | No (`""`) | Pipe-separated `AT-NNN` or `""` | Parent type within taxonomy (acyclic). |
| `definition` | Yes | String (10..280) | Plain-language summary. |
| `how_it_works` | Yes | String | Execution loop / operating model. |
| `strengths`, `limitations` | Yes | Qualitative prose | Qualitative advantages and tradeoffs (no uncited numbers). |
| `typical_examples` | Yes | String | Representative systems or applications. |
| `key_concept_ids` | Yes | Pipe-separated `CP-NNN` | Core related concepts. |
| `related_pattern_ids` | Yes | Pipe-separated `PT-NNN` | Associated design patterns. |
| `maturity` | Yes | `established` \| `growing` \| `emerging` | Adoption maturity. |
| `difficulty` | Yes | `beginner` \| `intermediate` \| `advanced` | Implementation complexity. |
| `source_ids` | Yes | Pipe-separated `SRC-NNNN` | Supporting sources. |
| `confidence`, `status` | Yes | Enum | Verification metadata. |
| `verified_date`, `next_review_date` | Yes | `YYYY-MM-DD` | Freshness dates (180-day policy window). |

### 4. `data/patterns.csv` (`data/schema/patterns.schema.json`)

| Column | Required | Type / Allowed Values | Description |
|---|---|---|---|
| `id` | Yes | `PT-NNN` | Pattern identifier. |
| `name` | Yes | String (2..120) | Canonical pattern name. |
| `category` | Yes | `workflow` \| `routing` \| `tool_loop` \| `orchestration` \| `quality` \| `safety` \| `memory` \| `retrieval` | Architectural pattern family. |
| `intent` | Yes | Qualitative prose | Problem solved by the pattern. |
| `structure` | Yes | String | Component flow and control structure. |
| `when_to_use`, `when_not_to_use` | Yes | Qualitative prose | Applicability guidance. |
| `tradeoffs` | Yes | Qualitative prose | Latency, cost, reliability, and complexity tradeoffs. |
| `example` | Yes | String | Practical example. |
| `diagram_file` | No (`""`) | `diagrams/<slug>.svg` or `""` | Associated master SVG path. |
| `related_concept_ids` | Yes | Pipe-separated `CP-NNN` | Core concepts. |
| `related_type_ids` | Yes | Pipe-separated `AT-NNN` | Agent types implementing the pattern. |
| `source_ids` | Yes | Pipe-separated `SRC-NNNN` | Supporting sources. |
| `confidence`, `status` | Yes | Enum | Verification metadata. |
| `verified_date`, `next_review_date` | Yes | `YYYY-MM-DD` | Freshness dates (180-day policy window). |

### 5. `data/protocols_standards.csv` (`data/schema/protocols_standards.schema.json`)

| Column | Required | Type / Allowed Values | Description |
|---|---|---|---|
| `id` | Yes | `PS-NNN` | Protocol or standard identifier. |
| `name` | Yes | String (2..140) | Specification name. |
| `kind` | Yes | `agent_protocol` \| `tool_protocol` \| `api_spec` \| `schema_standard` \| `auth_standard` \| `observability_standard` \| `commerce_protocol` \| `transport_protocol` \| `management_standard` | Specification kind. |
| `steward` | Yes | String | Maintainer or standards body. |
| `purpose`, `how_it_works` | Yes | String | Technical summary. |
| `transport_and_auth` | Yes | String | Wire transport and authentication model. |
| `adoption_level` | Yes | `widespread` \| `growing` \| `emerging` \| `experimental` | Observed adoption tier. |
| `strengths`, `limitations` | Yes | Qualitative prose | Technical strengths and constraints. |
| `spec_url` | Yes | Canonical HTTP/HTTPS URI | Official specification URL. |
| `related_concept_ids` | Yes | Pipe-separated `CP-NNN` | Related concepts. |
| `source_ids` | Yes | Pipe-separated `SRC-NNNN` | Supporting sources. |
| `confidence`, `status` | Yes | Enum | Verification metadata. |
| `verified_date`, `next_review_date` | Yes | `YYYY-MM-DD` | Freshness dates (90-day policy window). |

### 6. `data/frameworks_tools.csv` (`data/schema/frameworks_tools.schema.json`)

| Column | Required | Type / Allowed Values | Description |
|---|---|---|---|
| `id` | Yes | `FW-NNN` | Framework or tool identifier. |
| `name` | Yes | String | Tool/project name. |
| `category` | Yes | `agent_framework` \| `orchestration` \| `vector_store` \| `observability` \| `evaluation` \| `guardrails` \| `memory` \| `inference` \| `browser_or_computer_use` \| `coding_agent_tool` \| `data_loader` | Stack layer. |
| `maintainer` | Yes | String | Stewarding organization or author. |
| `license` | Yes | String | SPDX or split OSS/proprietary license summary verified from repo. |
| `primary_language` | Yes | String | Primary implementation language(s) or `API` / `Multi`. |
| `open_source` | Yes | `yes` \| `no` \| `partial` | `yes` if fully OSI open source; `partial` for open-core/SDK-only OSS; `no` for proprietary/source-available (e.g. ELv2). |
| `maturity` | Yes | `established` \| `growing` \| `emerging` | Ecosystem maturity. |
| `best_for`, `not_ideal_for` | Yes | Qualitative prose | Qualitative fit notes. |
| `repo_or_docs_url` | Yes | Canonical HTTP/HTTPS URI | Official documentation or repository URL. |
| `supported_protocol_ids` | No (`""`) | Pipe-separated `PS-NNN` | Supported protocols/standards. |
| `related_concept_ids` | Yes | Pipe-separated `CP-NNN` | Related concepts. |
| `source_ids` | Yes | Pipe-separated `SRC-NNNN` | Supporting sources. |
| `confidence`, `status` | Yes | Enum | Verification metadata. |
| `verified_date`, `next_review_date` | Yes | `YYYY-MM-DD` | Freshness dates (90-day policy window). |

### 7. `data/use_cases.csv` (`data/schema/use_cases.schema.json`)

| Column | Required | Type / Allowed Values | Description |
|---|---|---|---|
| `id` | Yes | `UC-NNN` | Use case identifier. |
| `industry` | Yes | 18 vertical sector enums (`customer_support` through `software_engineering`) | Target industry sector. |
| `use_case` | Yes | String | Concise workflow/use case title. |
| `agent_type_ids` | Yes | Pipe-separated `AT-NNN` | Implementing agent types. |
| `pattern_ids` | Yes | Pipe-separated `PT-NNN` | Applied patterns. |
| `concept_ids` | Yes | Pipe-separated `CP-NNN` | Core concepts. |
| `risk_ids` | Yes | Pipe-separated `RS-NNN` | Primary risks. |
| `human_oversight_level` | Yes | `approval` \| `review` \| `supervised` \| `autonomous` | Required human control posture. |
| `maturity` | Yes | `established` \| `growing` \| `emerging` | Production deployment maturity. |
| `expected_value` | Yes | Qualitative prose | Expected qualitative benefit (no uncited stats). |
| `main_risks`, `example_scenario` | Yes | String | Risk summary and operational example. |
| `source_ids` | Yes | Pipe-separated `SRC-NNNN` | Supporting sources. |
| `confidence`, `status` | Yes | Enum | Verification metadata. |
| `verified_date`, `next_review_date` | Yes | `YYYY-MM-DD` | Freshness dates (180-day policy window). |

### 8. `data/risks_security.csv` (`data/schema/risks_security.schema.json`)

| Column | Required | Type / Allowed Values | Description |
|---|---|---|---|
| `id` | Yes | `RS-NNN` | Risk identifier. |
| `risk` | Yes | String | Concise risk name. |
| `category` | Yes | `security` \| `privacy` \| `reliability` \| `cost` \| `legal` \| `ethics` \| `operational` | Risk domain. |
| `description` | Yes | String | Technical risk explanation. |
| `attack_or_failure_scenario` | Yes | String | Realistic failure or threat path. |
| `likelihood` | Yes | `high` \| `medium` \| `low` | Qualitative likelihood rating. |
| `impact` | Yes | `critical` \| `high` \| `medium` \| `low` | Qualitative impact severity. |
| `detection`, `mitigations` | Yes | String | Monitoring signals and controls. |
| `related_concept_ids` | Yes | Pipe-separated `CP-NNN` | Related concepts. |
| `source_ids` | Yes | Pipe-separated `SRC-NNNN` | Supporting sources (OWASP, NIST, MITRE ATLAS, arXiv). |
| `confidence`, `status` | Yes | Enum | Verification metadata. |
| `verified_date`, `next_review_date` | Yes | `YYYY-MM-DD` | Freshness dates (180-day policy window). |

### 9. `data/evaluation.csv` (`data/schema/evaluation.schema.json`)

| Column | Required | Type / Allowed Values | Description |
|---|---|---|---|
| `id` | Yes | `EV-NNN` | Evaluation entry identifier. |
| `name` | Yes | String | Metric, method, benchmark, tool, or process name. |
| `kind` | Yes | `metric` \| `method` \| `benchmark` \| `tool` \| `process` | Classification. |
| `what_it_measures` | Yes | Qualitative prose | Target property evaluated (no uncited numbers). |
| `how_to_run` | Yes | String | Practical evaluation procedure. |
| `strengths`, `limitations` | Yes | Qualitative prose | Qualitative pros and failure modes. |
| `applies_to_type_ids` | Yes | Pipe-separated `AT-NNN` | Applicable agent types. |
| `related_concept_ids` | Yes | Pipe-separated `CP-NNN` | Related concepts. |
| `source_ids` | Yes | Pipe-separated `SRC-NNNN` | Supporting sources. |
| `confidence`, `status` | Yes | Enum | Verification metadata. |
| `verified_date`, `next_review_date` | Yes | `YYYY-MM-DD` | Freshness dates (365-day policy window). |

### 10. `data/learning_paths.csv` (`data/schema/learning_paths.schema.json`)

| Column | Required | Type / Allowed Values | Description |
|---|---|---|---|
| `id` | Yes | `LP-NNN` | Learning step identifier. |
| `path_name` | Yes | `Foundations` \| `Builder` \| `Architect` \| `Security and Governance` \| `Team Lead` | Track name. |
| `step` | Yes | Positive integer string (`1`, `2`, ...) | Ordered step within track. |
| `title`, `objective` | Yes | String | Step title and learning goal. |
| `prerequisite_ids` | No (`""`) | Pipe-separated `LP-NNN` or `""` | Prior steps (strictly acyclic). |
| `concept_ids` | Yes | Pipe-separated `CP-NNN` | Covered concepts. |
| `resource_ids` | Yes | Pipe-separated `RES-NNN` | Recommended study resources. |
| `estimated_hours` | Yes | Decimal/integer string | **Rough study-time estimate** in hours (not an empirical measurement). |
| `outcome` | Yes | String | Practical skill/milestone after completing step. |
| `source_ids` | Yes | Pipe-separated `SRC-NNNN` | Supporting references. |
| `confidence`, `status` | Yes | Enum | Verification metadata. |
| `verified_date` | Yes | `YYYY-MM-DD` | Date step curriculum was verified. |

### 11. `data/resources.csv` (`data/schema/resources.schema.json`)

| Column | Required | Type / Allowed Values | Description |
|---|---|---|---|
| `id` | Yes | `RES-NNN` | Learning resource identifier. |
| `title` | Yes | String | Exact resource title. |
| `kind` | Yes | `doc` \| `paper` \| `course` \| `book` \| `video` \| `repo` \| `spec` \| `tool` \| `newsletter` | Format. |
| `publisher` | Yes | String | Author/publisher/organization. |
| `url` | Yes | Canonical HTTP/HTTPS URI | Verified working destination link. |
| `level` | Yes | `beginner` \| `intermediate` \| `advanced` | Reader prerequisite level. |
| `free` | Yes | `yes` \| `no` \| `partial` | Cost availability. |
| `topics` | Yes | Pipe-separated lowercase tags | Topic tags (`|`). |
| `concept_ids` | Yes | Pipe-separated `CP-NNN` | Concepts taught. |
| `why_it_helps` | Yes | Qualitative prose | Educational value for learners. |
| `source_ids` | Yes | Pipe-separated `SRC-NNNN` | Backing source entry in `sources.csv`. |
| `confidence`, `status` | Yes | Enum | Verification metadata. |
| `verified_date`, `next_review_date` | Yes | `YYYY-MM-DD` | Freshness dates (365-day policy window). |

### 12. `data/relationships.csv` (`data/schema/relationships.schema.json`)

| Column | Required | Type / Allowed Values | Description |
|---|---|---|---|
| `id` | Yes | `RL-NNNN` | Relationship edge identifier. |
| `from_id` | Yes | Entity ID (`CP`, `AT`, `PT`, `PS`, `FW`, `UC`, `RS`, `EV`, `LP`, `RES`) | Edge origin node. |
| `relation` | Yes | `requires` \| `part_of` \| `implements` \| `enables` \| `mitigates` \| `measures` \| `uses` \| `contrasts_with` \| `specializes` \| `example_of` | Directed edge predicate. |
| `to_id` | Yes | Entity ID (`CP`, `AT`, `PT`, `PS`, `FW`, `UC`, `RS`, `EV`, `LP`, `RES`) | Edge target node (`to_id != from_id`). |
| `note` | Yes | String (5..500) | Concise rationale for edge. |
| `source_ids` | Yes | Pipe-separated `SRC-NNNN` | Supporting sources. |
| `confidence` | Yes | `high` \| `medium` \| `low` | Verification level. |
| `verified_date` | Yes | `YYYY-MM-DD` | Date verified. |

### 13. `data/glossary_aliases.csv` (`data/schema/glossary_aliases.schema.json`)

| Column | Required | Type / Allowed Values | Description |
|---|---|---|---|
| `alias` | Yes | String (1..120) | Abbreviation, acronym, or synonym (unique). |
| `canonical_id` | Yes | Valid row ID (`CP-NNN`, `AT-NNN`, ..., `SRC-NNNN`) | Canonical dataset entry. |
| `note` | Yes | String (0..500) | Disambiguation context. |
