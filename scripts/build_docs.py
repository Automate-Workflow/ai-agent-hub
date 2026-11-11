"""Deterministically update generated markdown sections and item pages from CSV datasets."""

from __future__ import annotations

import argparse
import collections
import pathlib
import re
import sys

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import (
    DATASET_ORDER,
    DATASETS,
    DOCS_DIR,
    ROOT,
    configure_stdio,
    read_all_present,
    read_csv_rows,
    split_pipe,
    write_text_lf,
)
from stats import compute_stats


def _replace_marker_block(text: str, marker: str, body: str) -> str:
    start = f"<!-- {marker}:START -->"
    end = f"<!-- {marker}:END -->"
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    replacement = f"{start}\n{body.rstrip()}\n{end}"
    return pattern.sub(lambda _: replacement, text)


def _table(headers: list[str], rows: list[list[str]]) -> str:
    esc = lambda s: str(s).replace("|", "\\|").replace("\n", " ")
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        out.append("| " + " | ".join(esc(c) for c in row) + " |")
    return "\n".join(out)


def _render_stats_block(stats: dict[str, object]) -> str:
    ds_map = stats["datasets"]
    assert isinstance(ds_map, dict)
    rows: list[list[str]] = []
    for name in DATASET_ORDER:
        d = ds_map[name]
        tgt = f"{d['min_target']}-{d['max_target']}" if d["max_target"] else f"{d['min_target']}+"
        rows.append([f"`{d['filename']}`", str(d["rows"]), tgt])
    return _table(["Dataset", "Rows", "Target"], rows)


def _render_overview_table(dataset_name: str) -> str:
    _, rows = read_csv_rows(dataset_name)
    if not rows:
        return "_No entries populated yet._"
    if dataset_name == "agent_types":
        return _table(
            ["ID", "Type", "Lens", "Maturity", "Difficulty", "Confidence", "Status"],
            [
                [f"[{r['id']}](types/{r['id']}.md)", f"`{r['name']}`", r["view"], r["maturity"], r["difficulty"], r["confidence"], r["status"]]
                for r in sorted(rows, key=lambda x: x["id"])
            ],
        )
    if dataset_name == "concepts":
        return _table(
            ["ID", "Term", "Category", "Difficulty", "Definition", "Confidence"],
            [
                [f"[{r['id']}](concepts/{r['id']}.md)", r["term"], r["category"], r["difficulty"], r["definition"], r["confidence"]]
                for r in sorted(rows, key=lambda x: x["id"])
            ],
        )
    if dataset_name == "patterns":
        return _table(
            ["ID", "Pattern", "Category", "Intent", "Diagram", "Confidence"],
            [
                [
                    r["id"],
                    r["name"],
                    r["category"],
                    r["intent"],
                    f"[SVG](../{r['diagram_file']})" if r.get("diagram_file") else "-",
                    r["confidence"],
                ]
                for r in sorted(rows, key=lambda x: x["id"])
            ],
        )
    if dataset_name == "protocols_standards":
        return _table(
            ["ID", "Name", "Kind", "Steward", "Adoption", "Confidence"],
            [
                [r["id"], f"[{r['name']}]({r['spec_url']})", r["kind"], r["steward"], r["adoption_level"], r["confidence"]]
                for r in sorted(rows, key=lambda x: x["id"])
            ],
        )
    if dataset_name == "frameworks_tools":
        return _table(
            ["ID", "Name", "Category", "License", "Open Source", "Status"],
            [
                [r["id"], f"[{r['name']}]({r['repo_or_docs_url']})", r["category"], r["license"], r["open_source"], r["status"]]
                for r in sorted(rows, key=lambda x: x["id"])
            ],
        )
    if dataset_name == "use_cases":
        return _table(
            ["ID", "Industry", "Use Case", "Oversight", "Maturity", "Confidence"],
            [
                [r["id"], r["industry"], r["use_case"], r["human_oversight_level"], r["maturity"], r["confidence"]]
                for r in sorted(rows, key=lambda x: x["id"])
            ],
        )
    if dataset_name == "risks_security":
        return _table(
            ["ID", "Risk", "Category", "Likelihood", "Impact", "Confidence"],
            [
                [r["id"], r["risk"], r["category"], r["likelihood"], r["impact"], r["confidence"]]
                for r in sorted(rows, key=lambda x: x["id"])
            ],
        )
    if dataset_name == "evaluation":
        return _table(
            ["ID", "Name", "Kind", "What It Measures", "Confidence"],
            [
                [r["id"], r["name"], r["kind"], r["what_it_measures"], r["confidence"]]
                for r in sorted(rows, key=lambda x: x["id"])
            ],
        )
    if dataset_name == "learning_paths":
        return _table(
            ["ID", "Path", "Step", "Title", "Est. Hours", "Confidence"],
            [
                [r["id"], r["path_name"], r["step"], r["title"], r["estimated_hours"], r["confidence"]]
                for r in sorted(rows, key=lambda x: (x["path_name"], int(x["step"]), x["id"]))
            ],
        )
    return "_See CSV data file._"


def _build_detail_pages(
    present: dict[str, list[dict[str, str]]],
    dry_run: bool,
) -> int:
    """Generate deterministic per-item markdown pages under docs/concepts/ and docs/types/."""
    written = 0
    src_map = {r["id"]: r for r in present.get("sources", [])}
    label_map: dict[str, str] = {}
    for name, rows in present.items():
        if name in ("sources", "relationships", "glossary_aliases"):
            continue
        col = DATASETS[name].label_col
        for r in rows:
            label_map[r["id"]] = r.get(col, r["id"])

    edges_by_node: dict[str, list[tuple[str, str, str]]] = collections.defaultdict(list)
    for rel in present.get("relationships", []):
        u, p, v = rel["from_id"], rel["relation"], rel["to_id"]
        edges_by_node[u].append(("outgoing", p, v))
        edges_by_node[v].append(("incoming", p, u))

    def fmt_sources(sids_raw: str) -> list[str]:
        out = []
        for s in split_pipe(sids_raw):
            sr = src_map.get(s)
            if sr:
                out.append(f"- `{s}`: [{sr['title']}]({sr['url']}) ({sr['publisher']}, {sr['reliability']})")
            else:
                out.append(f"- `{s}`")
        return out or ["- None recorded"]

    def fmt_ref(target_id: str, from_dir: str) -> str:
        lbl = label_map.get(target_id, target_id)
        if target_id.startswith("CP-"):
            href = f"{target_id}.md" if from_dir == "concepts" else f"../concepts/{target_id}.md"
            return f"[`{target_id}`]({href}) ({lbl})"
        if target_id.startswith("AT-"):
            href = f"{target_id}.md" if from_dir == "types" else f"../types/{target_id}.md"
            return f"[`{target_id}`]({href}) ({lbl})"
        return f"`{target_id}` ({lbl})"

    # Concepts subpages (only if concepts.csv AND docs/concepts.md overview exist, or explicitly populated)
    concepts = sorted(present.get("concepts", []), key=lambda r: r["id"])
    if concepts and (DOCS_DIR / "concepts.md").exists():
        cdir = DOCS_DIR / "concepts"
        for i, r in enumerate(concepts):
            cid = r["id"]
            cat_slug = r["category"].replace("_", "-")
            prereqs = [f"- {fmt_ref(p, 'concepts')}" for p in split_pipe(r.get("prerequisite_ids", ""))]
            rel_edges = [
                f"- {d}: `{pred}` -> {fmt_ref(other, 'concepts')}"
                for d, pred, other in sorted(edges_by_node.get(cid, []))[:20]
            ]
            nav = []
            if i > 0:
                nav.append(f"[Previous: {concepts[i-1]['id']}]({concepts[i-1]['id']}.md)")
            nav.append("[All Concepts](../concepts.md)")
            if i + 1 < len(concepts):
                nav.append(f"[Next: {concepts[i+1]['id']}]({concepts[i+1]['id']}.md)")

            badges_line = (
                f"![{r['category']}](../../assets/icons/{cat_slug}.svg) "
                f"![{r['difficulty']}](../../assets/badges/{r['difficulty']}.svg) "
                f"![{r['status']}](../../assets/badges/{r['status']}.svg)"
            )
            lines = [
                f"# {cid}: {r['term']}",
                "",
                badges_line,
                "",
                f"**Category:** `{r['category']}` | **Difficulty:** `{r['difficulty']}` | **Confidence:** `{r['confidence']}` | **Status:** `{r['status']}` | **Verified:** `{r['verified_date']}`",
                "",
                "## Definition",
                "",
                r["definition"],
                "",
                "## Why It Matters",
                "",
                r["why_it_matters"],
                "",
                "## How It Works",
                "",
                r["how_it_works"],
                "",
                "## Example",
                "",
                r["example"],
                "",
                "## Common Mistakes",
                "",
                r["common_mistakes"],
                "",
                "## Prerequisites",
                "",
                *(prereqs or ["- None"]),
                "",
                "## Related Items",
                "",
                *(rel_edges or ["- None recorded in relationships.csv yet"]),
                "",
                "## Sources",
                "",
                *fmt_sources(r.get("source_ids", "")),
                "",
                "---",
                "",
                " | ".join(nav),
                "",
            ]
            if not dry_run:
                write_text_lf(cdir / f"{cid}.md", "\n".join(lines))
            written += 1

    # Agent type subpages
    types = sorted(present.get("agent_types", []), key=lambda r: r["id"])
    if types and (DOCS_DIR / "agent-types.md").exists():
        tdir = DOCS_DIR / "types"
        for i, r in enumerate(types):
            aid = r["id"]
            rel_edges = [
                f"- {d}: `{pred}` -> {fmt_ref(other, 'types')}"
                for d, pred, other in sorted(edges_by_node.get(aid, []))[:20]
            ]
            nav = []
            if i > 0:
                nav.append(f"[Previous: {types[i-1]['id']}]({types[i-1]['id']}.md)")
            nav.append("[All Agent Types](../agent-types.md)")
            if i + 1 < len(types):
                nav.append(f"[Next: {types[i+1]['id']}]({types[i+1]['id']}.md)")

            badges_line = (
                f"![{r['difficulty']}](../../assets/badges/{r['difficulty']}.svg) "
                f"![{r['status']}](../../assets/badges/{r['status']}.svg)"
            )
            lines = [
                f"# {aid}: {r['name']}",
                "",
                badges_line,
                "",
                f"**Lens:** `{r['view']}` | **Maturity:** `{r['maturity']}` | **Difficulty:** `{r['difficulty']}` | **Confidence:** `{r['confidence']}` | **Status:** `{r['status']}` | **Verified:** `{r['verified_date']}`",
                "",
                "## Definition",
                "",
                r["definition"],
                "",
                "## How It Works",
                "",
                r["how_it_works"],
                "",
                "## Strengths",
                "",
                r["strengths"],
                "",
                "## Limitations",
                "",
                r["limitations"],
                "",
                "## Typical Examples",
                "",
                r["typical_examples"],
                "",
                "## Related Items",
                "",
                *(rel_edges or ["- None recorded in relationships.csv yet"]),
                "",
                "## Sources",
                "",
                *fmt_sources(r.get("source_ids", "")),
                "",
                "---",
                "",
                " | ".join(nav),
                "",
            ]
            if not dry_run:
                write_text_lf(tdir / f"{aid}.md", "\n".join(lines))
            written += 1

    return written


def build_docs(dry_run: bool = False) -> tuple[int, int]:
    """Update marker blocks in README/docs and build detail pages. Return (docs_updated, pages_written)."""
    present = read_all_present()
    stats = compute_stats()
    stats_md = _render_stats_block(stats)

    targets = [ROOT / "README.md"] + sorted(DOCS_DIR.glob("*.md"))
    updated = 0

    table_markers = {
        "TABLE_AGENT_TYPES": "agent_types",
        "TABLE_CONCEPTS": "concepts",
        "TABLE_PATTERNS": "patterns",
        "TABLE_PROTOCOLS": "protocols_standards",
        "TABLE_FRAMEWORKS": "frameworks_tools",
        "TABLE_USE_CASES": "use_cases",
        "TABLE_RISKS": "risks_security",
        "TABLE_EVALUATION": "evaluation",
        "TABLE_LEARNING_PATHS": "learning_paths",
    }

    for path in targets:
        if not path.exists():
            continue
        orig = path.read_text(encoding="utf-8")
        new_txt = orig
        if "<!-- STATS:START -->" in new_txt:
            new_txt = _replace_marker_block(new_txt, "STATS", stats_md)
        for marker, ds_name in table_markers.items():
            if f"<!-- {marker}:START -->" in new_txt:
                new_txt = _replace_marker_block(new_txt, marker, _render_overview_table(ds_name))
        if new_txt != orig:
            if not dry_run:
                write_text_lf(path, new_txt)
            updated += 1

    pages = _build_detail_pages(present, dry_run=dry_run)
    return updated, pages


def main(argv: list[str] | None = None) -> int:
    configure_stdio()
    parser = argparse.ArgumentParser(description="Build marker-managed markdown tables and item pages.")
    parser.add_argument("--dry-run", action="store_true", help="Compute updates without writing files.")
    args = parser.parse_args(argv)

    updated, pages = build_docs(dry_run=args.dry_run)
    mode = "Dry-run" if args.dry_run else "Updated"
    print(f"{mode}: {updated} overview/README file(s) changed, {pages} detail page(s) processed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

