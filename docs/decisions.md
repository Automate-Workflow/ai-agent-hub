# Architecture and Knowledge Engineering Decisions

This log records methodological and implementation decisions made while building the AI Agent Hub repository (`Automate-Workflow/ai-agent-hub`) as of `2026-11-11`.

---

## DEC-001: Stdlib-Only Python 3.10+ Scripts (`scripts/`)

- **Context**: `CONTRIBUTING.md`, `docs/maintenance.md`, and early design notes originally mixed references to `requirements.txt` and external third-party packages (`jsonschema`, etc.), while automation scripts must run reliably in CI and locally on Windows/macOS/Linux without dependency drift.
- **Decision**: All scripts in `scripts/` (`common.py`, `validate_data.py`, `check_integrity.py`, `check_links.py`, `build_docs.py`, `build_charts.py`, `build_graph.py`, `build_site_data.py`, `stats.py`, and `dump_referenced_ids.py`) use Python 3.10+ standard library modules only (`csv`, `json`, `re`, `argparse`, `pathlib`, `urllib`, `xml.etree.ElementTree`, etc.) and have zero third-party `pip` dependencies.
- **Consequence**: `requirements.txt` is omitted; contributors and GitHub Actions workflows only need Python 3.10+.

## DEC-002: String-Typed CSV JSON Schemas (`data/schema/*.schema.json`)

- **Context**: `data/schema/sources.schema.json` represents CSV columns as JSON Schema `"type": "string"` with regex `pattern`, `enum`, `minLength`, and `maxLength` constraints so `csv.DictReader` rows validate directly without custom coercion.
- **Decision**: All 13 JSON Schemas under `data/schema/` use Draft 2020-12 with `"type": "string"`, `"additionalProperties": false`, pipe (`|`) regex validation for multi-value ID list columns, and regex patterns for integer/decimal CSV columns (`step`, `estimated_hours`).
- **Consequence**: Rows read via standard `csv.DictReader` validate identically under both `scripts/validate_data.py` (stdlib schema validator) and third-party JSON Schema validators.

## DEC-003: Canonical Naming, Reserved IDs, and `SRC-0158` Alias

- **Context**: Existing datasets (`agent_types.csv`, `frameworks_tools.csv`, `use_cases.csv`) reference pre-assigned IDs (`CP-*`, `PT-*`, `PS-*`, `RS-*`), with occasional semantic drift between files. Additionally, `SRC-0040` and `SRC-0158` both resolve to OpenAI's Assistants migration URL after the 2026-08-26 API shutdown.
- **Decision**: Preserve permanent IDs (`SRC-0158` marked `alias_of: SRC-0040` in `notes` rather than deleting or renumbering existing `SRC-*` IDs). When populating `concepts.csv`, `patterns.csv`, `protocols_standards.csv`, `risks_security.csv`, and `evaluation.csv`, align IDs cleanly and explicitly remap any mismatched legacy references in `agent_types.csv`, `frameworks_tools.csv`, or `use_cases.csv` so every cross-reference points to a semantically matching canonical row.
- **Consequence**: Zero dangling or semantically mismatched IDs while preserving historical `SRC-*` ID stability.

## DEC-004: Generated Interactive Site Data (`site/data/*.json`)

- **Context**: `site/data/` is listed in `.gitignore`. `build.yml` and `pages.yml` build the site data artifact, while local offline opening of `site/index.html` from the filesystem requires JSON data files when run locally.
- **Decision**: Keep `site/data/` gitignored per `.gitignore`, provide `python scripts/build_site_data.py` (invoked by `build.yml` and `pages.yml`) to generate `site/data/*.json` deterministically from `data/*.csv`, and verify local offline functionality by generating `site/data/` locally (with fallback inline/fetch behavior clearly documented in `site/` and `docs/`). Also build `site/graph.json` cleanly via `scripts/build_graph.py` alongside `build_site_data.py`.
- **Consequence**: Zero committed generated JSON bloat in git history, deterministic CI artifact builds, and working local explorer after running `build_site_data.py`.

## DEC-005: Bot-Gated URLs and Qualitative Style Rules

- **Context**: Several primary publishers (e.g., OpenAI `openai.com` web pages, Milvus docs Cloudflare challenge, vLLM ReadTheDocs rate limits, ISO.org, OWASP GenAI Cloudflare) return HTTP 403/429 to automated HTTP clients despite being live via browser/search. Meanwhile, qualitative fields (`expected_value`, `why_it_matters`, `strengths`, etc.) previously contained uncited numeric claims.
- **Decision**: `scripts/check_links.py` maintains an explicit, audited `known_bot_gated` URL/domain table verified live via web search/fetch; those URLs are reported distinctly as `gated` (warning/info) rather than broken failures, while true 404/5xx/DNS/TLS failures fail the link check. `validate_data.py` rejects quantitative percentages, multipliers, or numeric statistics in designated qualitative prose columns (allowing technical standard identifiers such as `ISO/IEC`, `HTTP`, `JSON`, `OAuth 2.0`, `RFC 6749`, `v2`, `UTF-8`, or explicit year dates where appropriate).
- **Consequence**: Automated checks reliably catch fabricated statistics and real dead links without false failures on bot-protected primary sites.

## DEC-006: Confidence, Review Windows, and Learning Path Estimates

- **Context**: `docs/methodology.md` defines source-based confidence and review intervals (`90` days for frameworks/tools/protocols, `180` days for patterns/agent types/use cases/risks, `365` days for foundational concepts/stable standards/evaluation/resources unless tool-specific).
- **Decision**: Set `verified_date` to `2026-11-11` on verified entries and compute `next_review_date` per category review window (`2027-02-09` or `+90d`, `2027-05-10` or `+180d`, `2027-11-11` `+365d` — specifically consistent calendar offsets from `2026-11-11`: `+90d = 2027-02-09` or `2027-02-11` as existing data uses, accepting any valid `verified_date <= next_review_date` within window). Label `learning_paths.estimated_hours` explicitly in `data/README.md` as rough practitioner study-time estimates rather than empirical measurements.
- **Consequence**: Clear freshness tracking and transparent caveats across all datasets.
