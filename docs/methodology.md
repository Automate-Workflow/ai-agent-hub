# Methodology

This document describes how data in the AI Agent Hub is researched, written, verified, and
maintained. It exists to make the knowledge base's quality standards explicit and reproducible.

## Research Protocol

### Primary Source Priority Hierarchy

When researching an entry, sources are weighted in the following order:

1. **Official documentation** from the organization or project that created the concept, tool, or
   protocol (e.g., Anthropic's MCP specification, OpenAI's function calling docs, OWASP's LLM
   Top 10 publication)
2. **Formal specifications** published by standards bodies (e.g., IETF RFCs, W3C recommendations,
   ISO standards, OpenAPI Initiative specifications)
3. **Peer-reviewed research papers** from conferences such as NeurIPS, ICML, ACL, ICLR, or
   journals with standard academic review processes
4. **Authoritative secondary sources** such as well-established technical books, official blog
   posts from core contributors, or broadly cited survey papers
5. **Reliable tertiary sources** such as reputable technical publications, curated community
   resources, or widely cited practitioner writing — used only when higher-tier sources are absent

A row's confidence level reflects which tier of source was used to verify it.

### Research Process

Each new entry follows this process:

1. Identify the concept, tool, or pattern to be added
2. Locate at least one primary source (tier 1 or 2 above)
3. Write the definition using language from or consistent with the primary source
4. Record the `source_url`, `verified_date`, and `next_review_date`
5. Assign `confidence` and `status` according to the rules below
6. Run `validate_data.py` to check schema compliance
7. Run `check_integrity.py` to verify cross-references and relationship consistency

## Confidence Assignment

| Confidence | Criteria |
|------------|----------|
| `high` | The claim is confirmed by at least one tier 1 or tier 2 source (official documentation, specification, or peer-reviewed paper) where the exact term and definition are used |
| `medium` | The claim is confirmed by multiple tier 3 or tier 4 sources, or by a single tier 2 source where the exact term is not used but the concept is clearly described |
| `low` | The claim is supported by a single tier 4 or tier 5 source, or the concept is real but difficult to verify precisely from available sources |

Confidence is a property of the source verification, not of the concept's importance. A well-known
concept with only one weak source still gets `low` confidence.

## Status Assignment

| Status | Criteria |
|--------|----------|
| `active` | Entry has been verified against a primary source, `verified_date` is within the review window, and no known issues exist |
| `needs-review` | Entry has passed its `next_review_date` without being re-verified, or a community member has flagged the content as potentially outdated |
| `deprecated` | Entry has been confirmed as outdated, superseded, or incorrect; kept for 90 days then eligible for removal |

## Verification Date and Review Window Policy

The `next_review_date` is set at the time an entry is created or last verified, based on how
quickly that category of information typically changes:

| Category | Review window |
|----------|--------------|
| Frameworks, tools, protocols | 90 days from `verified_date` |
| Patterns, agent types, use cases | 180 days from `verified_date` |
| Foundational concepts, stable standards | 365 days from `verified_date` |
| Risks (OWASP LLM Top 10, NIST AI RMF) | 180 days from `verified_date` |

Review windows are guidance, not strict deadlines. High-velocity areas of the ecosystem (e.g.,
framework releases) may warrant shorter windows at maintainer discretion.

## How Rows Are Retired

The retirement process follows a structured lifecycle:

1. **Flagged**: A maintainer or community member identifies a row as potentially outdated and either
   opens an issue or sets `status` to `needs-review` in a PR.
2. **Reviewed**: A maintainer checks the primary source. If the information is still accurate, the
   row is updated with a new `verified_date` and `next_review_date` and returned to `active`.
3. **Deprecated**: If the information is confirmed outdated or superseded, the row's `status` is
   set to `deprecated` and a note is added to the `notes` field explaining why.
4. **Removed**: After 90 days in `deprecated` status, the row is eligible for removal in a cleanup
   PR. The CHANGELOG records what was removed and why.

Row IDs are never reused after a row is removed. This ensures that any external references to a
row ID remain traceable even if the row itself is gone.

## Error Reporting

Errors can be reported through:

- **GitHub Issues**: Use the [Correction issue template](https://github.com/Automate-Workflow/ai-agent-hub/issues/new?template=correction.yml)
- **Pull Requests**: Direct corrections with a source URL in the PR description

All corrections must include a primary source URL. Corrections without sources cannot be accepted,
as they cannot be independently verified.

## Limitations

- **Coverage is intentional, not exhaustive.** Entries are added when maintainers or contributors
  can verify them against a primary source. Gaps in coverage reflect verification capacity, not
  editorial judgment.
- **The field changes faster than any static dataset.** Even high-confidence, active rows may
  reflect a snapshot that is weeks or months old. Always check the `verified_date` and consult
  primary sources for critical decisions.
- **Relationships are sampled, not complete.** The relationships graph captures important
  connections but is not a complete ontology. Many valid relationships between entries exist that
  are not yet recorded.

