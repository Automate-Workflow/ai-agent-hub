# Governance

## Roles

### Owner

**ayushcmd** holds final decision authority over all aspects of this repository. The owner:

- Maintains the `main` branch and controls merge access
- Appoints and removes maintainers
- Holds veto authority over any change, regardless of review status
- Sets strategic direction and approves policy changes

### Maintainers

Appointed by the owner. Maintainers:

- Review and merge pull requests
- Triage and label issues
- Run releases and tag versions
- Enforce the Code of Conduct
- Conduct scheduled data freshness reviews

### Contributors

Anyone whose pull request has been merged. Contributors are credited in the CHANGELOG and may be
invited to become maintainers based on sustained, high-quality contributions.

## Decision Process

| Change type | Process |
|-------------|---------|
| Typos, broken links, single-row corrections | Any maintainer approves and merges |
| New data rows, new categories | Discussion in an issue, then 1 maintainer approval |
| Schema changes (new CSV columns, ID format) | Discussion in an issue + 2 maintainer approvals |
| Policy changes (governance, CoC, license) | Community discussion, then owner decides |
| Breaking changes to any public interface | Owner veto right on any PR |

## Deprecation of Data Rows

1. A maintainer sets the `status` field to `deprecated` in the relevant CSV and records a brief
   reason in the `notes` field.
2. The deprecated row remains in the CSV for 90 days to preserve historical reference and avoid
   breaking external links to row IDs.
3. After 90 days, the row may be removed in a labeled cleanup PR.
4. The CHANGELOG records what was removed and why in the relevant version section.

## Releases and Versioning

This project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html):

- **Patch** (x.x.N): data corrections, broken link fixes, typo fixes
- **Minor** (x.N.0): new data rows, new diagrams, new learning resources
- **Major** (N.0.0): schema changes, breaking changes to data structure, significant policy changes

Releases are tagged on `main` and documented in CHANGELOG.md.

## Conflict Resolution

Good-faith discussion in the relevant issue or pull request is the first step. If no consensus is
reached within 14 days of active discussion, the owner makes the final decision. All decisions are
recorded in the issue or PR thread for transparency.

## Amendments to This Document

Amendments to this governance document require a community discussion period of at least 7 days
before the owner finalizes any change.

