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

All scripts live in the `scripts/` directory. Run them from the repository root.

### Windows PowerShell

```powershell
cd "C:\Projects\Org-Automate Workflow\ai-agent-hub"

# Validate all CSV schemas and field values
python scripts/validate_data.py

# Check cross-references and relationship integrity
python scripts/check_integrity.py

# Check all external URLs for broken links (slow; writes reports/link_report.json)
python scripts/check_links.py

# Build all generated SVG charts from CSV data
python scripts/build_charts.py

# Build the static site
python scripts/build_site.py
```

### Linux / macOS

```bash
cd path/to/ai-agent-hub

python scripts/validate_data.py
python scripts/check_integrity.py
python scripts/check_links.py
python scripts/build_charts.py
python scripts/build_site.py
```

### Setting Up a Local Environment

```powershell
# Windows PowerShell
cd "C:\Projects\Org-Automate Workflow\ai-agent-hub"
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

```bash
# Linux / macOS
cd path/to/ai-agent-hub
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## CI Pipeline Overview

The CI pipeline runs on every push to `main` and on every pull request. It is defined in
`.github/workflows/`.

| Workflow | Trigger | What it does |
|----------|---------|--------------|
| `validate.yml` | Push, PR | Runs `validate_data.py` and `check_integrity.py`; fails the PR if errors are found |
| `check-links.yml` | Scheduled (weekly), PR | Runs `check_links.py`; posts a summary comment on PRs with any broken links |
| `build.yml` | Push to `main`, PR | Runs `build_charts.py` and `build_site.py`; uploads the site artifact |
| `deploy.yml` | Push to `main` (after build passes) | Deploys the built site to GitHub Pages |

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
2. For each stale row, visit the `source_url` and verify the information is still accurate
3. If accurate: update `verified_date` to today and set a new `next_review_date`
4. If outdated: set `status` to `needs-review` and open an issue for investigation
5. If confirmed obsolete: set `status` to `deprecated` and add a note to the `notes` field
6. Run `validate_data.py` to confirm no schema errors were introduced
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
2. Open `reports/link_report.json` and filter for non-200 results
3. For each broken URL:
   - Check if the page has moved: search for the new canonical URL
   - Check the Wayback Machine (https://web.archive.org) for an archived version
   - If a replacement exists: update `source_url` or the relevant URL field in the CSV
   - If no replacement exists: set the row's `status` to `needs-review` and open an issue
4. Run `validate_data.py` after edits
5. Commit with message: `fix: update broken links from check_links report YYYY-MM-DD`

The `reports/link_report.json` file is excluded from version control by `.gitignore`.

