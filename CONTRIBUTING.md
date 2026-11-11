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
- Or submit a pull request directly with the corrected row and a source URL

### 2. New Data Rows

Want to add a new concept, agent type, pattern, protocol, framework, use case, risk, metric,
learning path step, or resource?

- Use the appropriate issue template to propose the entry first if you are unsure whether it fits
- Or submit a pull request with the new row following the schema for that CSV

### 3. New Learning Resources

Found a valuable paper, course, book, video, or repository that belongs in `data/resources.csv`?

- Use the **[New Resource template](https://github.com/Automate-Workflow/ai-agent-hub/issues/new?template=new_resource.yml)**

### 4. Broken Links

Found a URL that no longer works?

- Use the **[Broken Link template](https://github.com/Automate-Workflow/ai-agent-hub/issues/new?template=broken_link.yml)**

### 5. Diagram and Visual Contributions

If you want to propose a new SVG diagram, open an issue first to discuss scope, style, and whether
the content is already covered. All diagrams must match the established visual style.

---

## Requirements for Data Contributions

### Every Claim Needs a Source

Every row in every CSV must have a `source_url` or reference a row in `sources.csv` via
`source_ids`. Entries without a verifiable source URL will not be accepted. The source must be
publicly accessible and must clearly support the specific claim being made.

### Follow Controlled Vocabularies

Each CSV has fields with controlled vocabularies (e.g., `confidence` must be `high`, `medium`, or
`low`; `status` must be `active`, `needs-review`, or `deprecated`). Use only the values listed in
the schema documentation for that file. The validator will reject any other values.

### No Placeholder Text

Do not submit rows with placeholder text such as `TODO`, `TBD`, `lorem ipsum`, `example.com`,
or similar. All submitted content must be final and factually grounded.

---

## ID Format Rules

Row IDs are permanent. Once a row is published in a release, its ID never changes, even if the
content is updated. This ensures external references remain valid.

| Dataset | Prefix | Format | Example |
|---------|--------|--------|---------|
| concepts.csv | CP | CP-NNN | CP-042 |
| agent_types.csv | AT | AT-NNN | AT-007 |
| patterns.csv | PT | PT-NNN | PT-015 |
| protocols.csv | PR | PR-NNN | PR-003 |
| frameworks.csv | FW | FW-NNN | FW-028 |
| use_cases.csv | UC | UC-NNN | UC-019 |
| risks.csv | RK | RK-NNN | RK-011 |
| metrics.csv | MT | MT-NNN | MT-006 |
| learning_paths.csv | LP | LP-NNN | LP-022 |
| resources.csv | RL | RL-NNNN | RL-0042 |
| sources.csv | SRC | SRC-NNNN | SRC-0101 |
| relationships.csv | REL | REL-NNN | REL-012 |

Rules:
- Prefixes are fixed per dataset
- Use 3-digit padding for all datasets except resources and sources (4-digit)
- Find the highest existing ID in the CSV and increment by 1
- Never reuse an ID after it has been assigned, even if the row is later removed

---

## Writing Style

- **Plain English.** Write for a competent practitioner, not for a specialist audience.
- **Maximum 280 characters for definitions.** This matches the constraint of the interactive
  explorer's display. Longer explanations belong in `extended_description` or docs.
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

## Running Scripts Locally

Before submitting a pull request, run the validator and integrity checker to catch errors early.

### Windows PowerShell

```powershell
cd "C:\Projects\Org-Automate Workflow\ai-agent-hub"

# Validate CSV schemas and controlled vocabulary values
python scripts/validate_data.py

# Check cross-references and relationship integrity
python scripts/check_integrity.py
```

### Linux / macOS

```bash
cd path/to/ai-agent-hub

python scripts/validate_data.py
python scripts/check_integrity.py
```

Both scripts exit with code 0 on success and print a summary of any errors found. Fix all reported
errors before submitting your pull request.

---

## Conventional Commits

All commits in this repository must follow the
[Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification.

| Type | When to use |
|------|-------------|
| `feat` | Adding a new script, tool, or site feature |
| `fix` | Fixing a bug in a script or CI workflow |
| `chore` | Maintenance tasks (dependency updates, config changes) |
| `docs` | Changes to documentation prose (README, docs/) |
| `data` | Adding or correcting rows in CSV datasets |
| `ci` | Changes to CI workflow files |

**Examples:**

```
data: add concept CP-121 vector-database
data: correct framework license FW-033 from MIT to Apache-2.0
fix: handle empty source_url in validate_data.py
docs: update how-to-read-this-hub navigation section
ci: add scheduled link check workflow
chore: bump actions/checkout to v4
```

---

## Branch Naming

| Type of change | Branch name format | Example |
|----------------|--------------------|---------|
| New data row | `data/add-<category>-<brief-name>` | `data/add-concept-vector-database` |
| Data correction | `fix/correction-<row-id>` | `fix/correction-fw-033` |
| Documentation | `docs/update-<brief-name>` | `docs/update-methodology` |
| Script or tool | `feat/<brief-name>` | `feat/add-freshness-check` |
| CI workflow | `ci/<brief-name>` | `ci/add-link-check-schedule` |

---

## Pull Request Checklist

Before submitting, verify all of the following:

- [ ] Every claim has a source URL in `source_url` or referenced in `source_ids`
- [ ] `validate_data.py` passes with no errors
- [ ] `check_integrity.py` passes with no errors
- [ ] No placeholder text anywhere in the changes
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
- Writing style and character limits
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

