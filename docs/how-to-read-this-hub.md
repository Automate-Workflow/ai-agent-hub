# How to Read This Hub

## What This Hub Is

The AI Agent Hub is a structured, sourced knowledge base about AI agent types, concepts, patterns,
protocols, frameworks, tools, use cases, risks, and evaluation methods. Every row in every dataset
is linked to at least one primary source. The goal is to give practitioners, researchers, and teams
a reliable reference point for navigating the AI agent ecosystem as it stands today.

The hub is organized as a set of interconnected CSV datasets, hand-crafted SVG diagrams, and a
static interactive explorer. All content is versioned and maintained under a formal data quality
process.

## What This Hub Is Not

- **Not a product recommendation engine.** Entries in frameworks.csv describe what tools exist and
  what they do; they do not rank, endorse, or recommend one over another. Evaluation is your job.
- **Not exhaustive.** The field moves extremely fast. New frameworks, protocols, and agent types
  emerge monthly. This hub covers what has been verified as of its last update date. The
  `next_review_date` field on each row tells you when it was last verified and when it is due for
  review.
- **Not a live tracker.** Data is updated in batches through the contribution and release process,
  not in real time. For rapidly changing information (e.g., framework version history), check the
  primary source directly.
- **Not legal, financial, or professional advice.** Use of information from this hub for consequential
  decisions is at your own risk. Always consult authoritative sources for critical choices.

## How to Navigate

### By Role

| Your role | Where to start |
|-----------|----------------|
| New to AI agents | Start with the Foundations learning path in `data/learning_paths.csv` |
| Developer building agents | Start with the Builder learning path; see `data/frameworks.csv` |
| Architect or tech lead | Start with the Architect learning path; see `data/patterns.csv` and `data/protocols.csv` |
| Security or governance focus | Start with the Security and Governance learning path; see `data/risks.csv` |
| Team lead evaluating adoption | Start with the Team Lead learning path; see `data/use_cases.csv` |

### By Learning Path

Five structured learning paths are defined in `data/learning_paths.csv`:

1. **Foundations** — Core concepts, terminology, and mental models for understanding AI agents
2. **Builder** — Hands-on frameworks, tools, and patterns for building agentic systems
3. **Architect** — System design, protocols, multi-agent topologies, and integration concerns
4. **Security and Governance** — Risks, mitigations, compliance considerations, and evaluation
5. **Team Lead** — Use cases, adoption strategies, ROI frameworks, and organizational readiness

Each path has ordered steps with difficulty levels and estimated reading time.

### By Search

The interactive explorer at the top of the repository's GitHub Pages site provides full-text search
across all datasets. You can filter by category, status, confidence, maturity, and difficulty.

### By Relationships

Every row ID can appear in `data/relationships.csv`. Each relationship has a `type` (e.g.,
`uses`, `implements`, `extends`, `contrasts_with`, `requires`) and a `weight`. Use the interactive
force graph to explore the relationship network visually, or query `relationships.csv` directly.

## Understanding Confidence Scores

Each row carries a `confidence` field with one of three values:

| Confidence | Meaning | How to use it |
|------------|---------|---------------|
| `high` | Confirmed by a primary source: official documentation, formal specification, or peer-reviewed paper | Reliable for direct reference; still verify before consequential decisions |
| `medium` | Confirmed by multiple reliable secondary sources, but no single primary source verified | Good for orientation; find a primary source before citing in formal work |
| `low` | Based on a single weak or tertiary source, or the claim is difficult to verify independently | Treat as a pointer for further research, not as a confirmed fact |

## Understanding Status Values

| Status | Meaning |
|--------|---------|
| `active` | Current, verified, and within review date |
| `needs-review` | Past `next_review_date`; content may be outdated; a maintainer review is pending |
| `deprecated` | Outdated or superseded; kept for 90 days for historical reference then removed |

Rows with status `needs-review` or `deprecated` are shown with a visual indicator in the
interactive explorer. Treat them with extra skepticism and check the primary source directly.

## When to Verify Yourself

This hub is a starting point, not an endpoint. Always verify claims from primary sources before:

- Making architectural decisions for production systems
- Citing this hub in published research or reports
- Advising a team or organization based on data here
- Selecting a tool, framework, or protocol for a critical use case

The `source_url` field on every row points directly to the primary source used to verify that
row. Use it.

## How to Find Related Items

1. **relationships.csv** — Contains all typed, weighted relationships between row IDs. Filter by
   `source_id` or `target_id` to find what a given entry connects to.
2. **Interactive explorer** — Click any node in the force graph to highlight its neighbors.
   The sidebar shows all relationships with their types and weights.
3. **source_ids field** — Several datasets include a `source_ids` field that references entries in
   `sources.csv`. This is the bibliographic layer, separate from the relationship graph.

## How to Contribute

If you find an error, a broken link, or want to suggest a new entry:

1. Read [CONTRIBUTING.md](../CONTRIBUTING.md) for the full process
2. Use the appropriate issue template on GitHub (correction, new concept, broken link, etc.)
3. If submitting a PR, run `validate_data.py` and `check_integrity.py` before submitting
4. Every claim needs a source URL — entries without verifiable sources are not accepted

Small corrections are very welcome and are the most common form of contribution. You do not need
to be an AI expert to contribute; you just need to be willing to find and cite primary sources.

