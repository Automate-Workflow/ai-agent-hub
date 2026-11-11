# Maintenance Guide

## Who Maintains This Repository

The repository is maintained by **ayushcmd** (owner) and appointed maintainers from the
Automate Workflow organization. See [GOVERNANCE.md](../GOVERNANCE.md) for the full roles and
decision process.

Maintainer responsibilities include:
- Reviewing and merging pull requests within 14 days
- Running scheduled data freshness reviews
- Triaging and labeling issues
- Running the CI pipeline locally when needed
- Publishing new releases and updating CHANGELOG.md

---

## Running Scripts Locally

All scripts live in the `scripts/` directory and use Python 3.10+ standard library modules only
(no external `pip` packages or `requirements.txt` needed). Run them from the repository root.

### Windows PowerShell

```powershell
cd "C:\Projects\Org-Automate Workflow\ai-agent-hub"

# Validate all CSV schemas, field values, and qualitative constraints
python scripts/validate_data.py

# Check cross-references, cycles, orphan sources, and relationship edges
python scripts/check_integrity.py

# Check all external URLs (writes reports/link_report.md and reports/link_report.json)
python scripts/check_links.py

# Dump unresolved/reserved IDs (writes reports/reserved_ids.csv)
python scripts/dump_referenced_ids.py

# Build all generated SVG charts from CSV data
python scripts/build_charts.py

# Build generated markdown documentation and README sections
python scripts/build_docs.py

# Build the interactive graph JSON dataset
python scripts/build_graph.py

# Build interactive static explorer JSON datasets in site/data/
python scripts/build_site_data.py

# Print live dataset statistics
python scripts/stats.py
```

### Linux / macOS

```bash
cd path/to/ai-agent-hub

python3 scripts/validate_data.py
python3 scripts/check_integrity.py
python3 scripts/check_links.py
python3 scripts/build_charts.py
python3 scripts/build_docs.py
python3 scripts/build_graph.py
python3 scripts/build_site_data.py
python3 scripts/stats.py
```

### Local Environment Requirements

- Python `3.10` or newer (standard library only; no third-party virtual environment packages required)
- UTF-8 encoding with LF line endings

---

## CI Pipeline Overview

The CI pipeline runs on every push to `main` and on every pull request. It is defined in
`.github/workflows/`.

| Workflow | Trigger | What it does |
|----------|---------|--------------|
| `validate.yml` | Push, PR | Runs `validate_data.py`, `check_integrity.py`, and generator idempotence checks; fails if errors or uncommitted diffs are found |
| `links.yml` | Scheduled (weekly), Manual | Runs `check_links.py`, uploads the report artifact, and updates the broken-links tracking issue |
| `build.yml` | Push to `main`, PR | Runs `build_site_data.py` (and `build_graph.py`) and uploads the site build artifact |
| `pages.yml` | Push to `main`, Manual | Builds static assets/data and deploys `site/` to GitHub Pages |

A pull request must pass all workflows before it can be merged.

---

## Freshness Review Process

The `next_review_date` field on each row indicates when that row is due for re-verification.

### Finding Stale Rows (Windows PowerShell)

```powershell
# Print all rows past their next_review_date
python scripts/validate_data.py --stale
```

This outputs a table of row IDs, files, and how many days past review they are.

### Manual Review Steps

1. Run the stale check to identify rows past `next_review_date`
2. For each stale row, inspect its cited sources in `data/sources.csv` (`url`) and verify accuracy
3. If accurate: update `verified_date` to today and set a new `next_review_date`
4. If outdated: set `status` to `needs-review` and open an issue for investigation
5. If confirmed obsolete: set `status` to `deprecated` and update explanatory notes
6. Run `validate_data.py` and `check_integrity.py` to confirm no schema errors were introduced
7. Commit with message: `chore: freshness review YYYY-MM-DD`

---

## How to Update Data

1. Open the relevant CSV in a text editor that preserves LF line endings
2. Make your changes following the controlled vocabulary and ID format in `CONTRIBUTING.md`
3. Run `python scripts/validate_data.py` — fix any errors reported
4. Run `python scripts/check_integrity.py` — fix any cross-reference errors
5. If you added or changed visual data, run `python scripts/build_charts.py`
6. Commit using Conventional Commits format: `data: add concept CP-121 vector-database`
7. Push and open a PR; CI will validate automatically

---

## How to Deprecate Entries

1. In the relevant CSV, change the row's `status` field from `active` or `needs-review` to `deprecated`
2. Add a brief explanation to the `notes` field, e.g. `Deprecated 2027-03-15: superseded by CP-099`
3. Record the deprecation in the next release's CHANGELOG under the `Deprecated` section
4. After 90 days, the row is eligible for removal in a cleanup PR
5. The cleanup PR's CHANGELOG entry records the row ID and reason under `Removed`

Row IDs are never reused after removal.

---

## How to Handle Broken Links

The `check_links.py` script writes a JSON report to `reports/link_report.json` with every URL
it checked and the result (status code or error).

### Triage Process

1. Run `python scripts/check_links.py` to generate a fresh report
2. Open `reports/link_report.json` (or `reports/link_report.md`) and inspect broken URLs
3. For each broken URL:
   - Check if the page has moved: search for the new canonical URL
   - Check archival snapshots if no live canonical URL remains
   - If a replacement exists: update the `url` field in `data/sources.csv` (and matching URL fields such as `repo_or_docs_url`, `spec_url`, or `resources.csv` `url`)
   - If no replacement exists: set the citing row's `status` to `needs-review` and open an issue
4. Run `validate_data.py` after edits
5. Commit with message: `fix: update broken links from check_links report YYYY-MM-DD`

The `reports/link_report.json` file is excluded from version control by `.gitignore`.

