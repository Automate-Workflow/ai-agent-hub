# Contributing to AI Agent Hub

Thank you for your interest in contributing. This knowledge base is only as useful as the accuracy
and completeness of its data. Every verified correction, new entry, and broken link report makes it
more reliable for everyone.

---

## Philosophy

This hub is built on a few core principles:

- **Verifiability over completeness.** Every claim must be traceable to a primary source. An entry
  that cannot be verified is worse than a gap.
- **Plain language over jargon.** Definitions should be readable by a competent practitioner, not
  only by specialists in one subfield.
- **Precision over quantity.** A smaller, accurate dataset is more valuable than a large, noisy one.
- **Stability over speed.** Row IDs, once published, never change. This allows external systems to
  reference entries safely.

---

## Ways to Contribute

### 1. Data Corrections

Found an error in a definition, a wrong license, an incorrect date, or a factual inaccuracy?

- Open an issue using the **[Correction template](https://github.com/Automate-Workflow/ai-agent-hub/issues/new?template=correction.yml)**
- Or submit a pull request directly with the corrected row and a verifiable source

### 2. New Data Rows

Want to add or improve entries in the active datasets (`agent_types.csv`, `frameworks_tools.csv`,
`use_cases.csv`, `sources.csv`) or propose entries for upcoming datasets (`concepts.csv`,
`patterns.csv`, `protocols_standards.csv`, `risks_security.csv`, `evaluation.csv`,
`learning_paths.csv`, `resources.csv`, `relationships.csv`, `glossary_aliases.csv`)?

- Use an issue template to propose the entry first if you are unsure whether it fits
- Or submit a pull request with the new row following the schema and format rules for that CSV

### 3. New Sources and Learning Resources

Found a primary specification, paper, or documentation page that belongs in `data/sources.csv`
(or an educational resource for the planned `data/resources.csv`)?

- Use the **[New Resource template](https://github.com/Automate-Workflow/ai-agent-hub/issues/new?template=new_resource.yml)**

### 4. Broken Links

Found a URL that no longer works?

- Use the **[Broken Link template](https://github.com/Automate-Workflow/ai-agent-hub/issues/new?template=broken_link.yml)**

### 5. Diagram and Visual Contributions

If you want to propose a new SVG diagram, open an issue first to discuss scope, style, and whether
the content is already covered. All diagrams must follow project visual guidelines.

---

## Requirements for Data Contributions

### Every Claim Needs a Source

Every row in content CSVs must reference one or more rows in `data/sources.csv` via `source_ids`
(pipe-separated with `|`), and every row in `data/sources.csv` must include a verifiable `url`.
Entries without verifiable supporting sources will not be accepted. The source must be publicly
accessible and must clearly support the specific claim being made.

### Follow Controlled Vocabularies

Each CSV has fields with controlled vocabularies (e.g., `confidence` must be `high`, `medium`, or
`low`; `status` must be `active`, `needs-review`, or `deprecated`). Use only valid controlled
vocabulary values and pipe (`|`) delimiters for multi-value list fields.

### No Placeholder Text

Do not submit rows with placeholder text such as `TODO`, `TBD`, `lorem ipsum`, `example.com`,
synthetic `-01` placeholder dates, or uncited metrics. All submitted content must be final and
factually grounded.

---

## ID Format Rules

Row IDs are permanent. Once a row is published, its ID never changes, even if the content is
updated. This ensures external references remain valid.

| Dataset | Prefix | Format | Example | Status |
|---------|--------|--------|---------|--------|
| `data/concepts.csv` | `CP` | `CP-NNN` | `CP-042` | Planned |
| `data/agent_types.csv` | `AT` | `AT-NNN` | `AT-007` | Active |
| `data/patterns.csv` | `PT` | `PT-NNN` | `PT-015` | Planned |
| `data/protocols_standards.csv` | `PS` | `PS-NNN` | `PS-003` | Planned |
| `data/frameworks_tools.csv` | `FW` | `FW-NNN` | `FW-028` | Active |
| `data/use_cases.csv` | `UC` | `UC-NNN` | `UC-019` | Active |
| `data/risks_security.csv` | `RS` | `RS-NNN` | `RS-011` | Planned |
| `data/evaluation.csv` | `EV` | `EV-NNN` | `EV-006` | Planned |
| `data/learning_paths.csv` | `LP` | `LP-NNN` | `LP-022` | Planned |
| `data/resources.csv` | `RES` | `RES-NNN` | `RES-042` | Planned |
| `data/relationships.csv` | `RL` | `RL-NNN` | `RL-012` | Planned |
| `data/sources.csv` | `SRC` | `SRC-NNNN` | `SRC-0101` | Active |

Rules:
- Prefixes are fixed per dataset (`CP`, `AT`, `PT`, `PS`, `FW`, `UC`, `RS`, `EV`, `LP`, `RES`, `RL`, `SRC`)
- Use 3-digit zero-padded numbers as the baseline across datasets except `sources.csv`, which uses 4-digit padding (`SRC-NNNN`)
- Find the highest existing ID in the CSV and increment by 1
- Never reuse an ID after it has been assigned, even if the row is later removed

---

## Writing Style

- **Plain English.** Write for a competent practitioner, not for a specialist audience.
- **Concise definitions.** Target a maximum of 280 characters for primary definition fields; longer
  explanations belong in documentation under `docs/`.
- **No hype.** Do not use words like "revolutionary", "game-changing", "cutting-edge", or
  "industry-leading". Describe what something is and does, factually.
- **No marketing language.** Do not reproduce vendor marketing copy. Paraphrase from primary
  sources using neutral language.
- **Active voice.** Prefer "An agent observes its environment and selects actions" over "Actions
  are selected by the agent based on observations of its environment."
- **Present tense** for definitions. Use past tense only for historical statements.
- **Specific over vague.** "Uses chain-of-thought prompting to decompose problems into sub-steps"
  is better than "uses advanced reasoning techniques."

---

## Local Validation Checks

Automated validation scripts under `scripts/` are **planned and not yet present** in this
repository. Before submitting a pull request in the current development stage, verify your changes
using Python:

1. Validate `data/sources.csv` rows against `data/schema/sources.schema.json` using `jsonschema`.
2. Confirm every CSV uses UTF-8 encoding (no BOM), LF (`\n`) line endings, matching header column
   counts on every row, and pipe (`|`) separators for multi-value ID fields.
3. Confirm every `source_ids` value resolves to an active ID in `data/sources.csv`, and verify all
   modified or added URLs return live responses.

### Windows PowerShell

```powershell
cd "C:\Projects\Org-Automate Workflow\ai-agent-hub"
python -c "import csv,json,jsonschema; s=json.load(open('data/schema/sources.schema.json')); [jsonschema.validate(r,s) for r in csv.DictReader(open('data/sources.csv',encoding='utf-8'))]; print('sources.csv valid')"
```

### Linux / macOS

```bash
cd path/to/ai-agent-hub
python3 -c "import csv,json,jsonschema; s=json.load(open('data/schema/sources.schema.json')); [jsonschema.validate(r,s) for r in csv.DictReader(open('data/sources.csv',encoding='utf-8'))]; print('sources.csv valid')"
```

---

## Conventional Commits

All commits in this repository must follow the
[Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification.

| Type | When to use |
|------|-------------|
| `feat` | Adding a new script, tool, or site feature |
| `fix` | Fixing a bug in data, docs, scripts, or configuration |
| `chore` | Maintenance tasks (config updates, repository cleanup) |
| `docs` | Changes to documentation prose (`README.md`, `docs/`) |
| `data` | Adding or correcting rows in CSV datasets |
| `ci` | Changes to CI workflow files |

**Examples:**

```
data: add source SRC-0196 anthropic-agent-skills
fix(data): correct framework license FW-031 from MIT to Apache-2.0
fix(data): handle empty published_date in sources.csv
docs: update methodology source tiers
chore: update .gitignore rules
```

---

## Branch Naming

| Type of change | Branch name format | Example |
|----------------|--------------------|---------|
| New data row | `data/add-<category>-<brief-name>` | `data/add-agent-type-code-reviewer` |
| Data correction | `fix/correction-<row-id>` | `fix/correction-fw-031` |
| Documentation | `docs/update-<brief-name>` | `docs/update-methodology` |
| Script or tool | `feat/<brief-name>` | `feat/add-data-validator` |
| CI workflow | `ci/<brief-name>` | `ci/add-link-check-schedule` |

---

## Pull Request Checklist

Before submitting, verify all of the following:

- [ ] Every claim has a verifiable source in `data/sources.csv` referenced via `source_ids` (or a live `url` inside `data/sources.csv`)
- [ ] `data/sources.csv` validates against `data/schema/sources.schema.json`
- [ ] All edited CSV rows match their header column count and use `|` separators for list columns
- [ ] No placeholder text (`TODO`, `TBD`), synthetic `-01` dates, or uncited statistics
- [ ] All URLs in the PR are verified working at time of submission
- [ ] Writing follows the style guide in this document
- [ ] Commit messages follow Conventional Commits format
- [ ] Branch name follows the naming convention above
- [ ] The PR description explains what changed and why

---

## Review Process

A maintainer will review your pull request within 14 days of submission. Reviews focus on:

- Factual accuracy and source quality
- Schema compliance (ID format, controlled vocabulary)
- Writing style and conciseness
- Consistency with existing entries in the same category

If the reviewer requests changes, please respond within 14 days. PRs with no activity after 14
days of a change request may be closed and re-opened when you are ready to continue.

---

## Contributor Sign-Off

By submitting a contribution to this repository, you agree that:

> My contributions are licensed under the MIT License (for code, scripts, and CI workflows)
> and under the Creative Commons Attribution 4.0 International License (for data files,
> documentation, and prose), as defined in [LICENSE](LICENSE) and [LICENSE-DATA.md](LICENSE-DATA.md).

This applies to all pull requests and issue submissions that include substantive content.
