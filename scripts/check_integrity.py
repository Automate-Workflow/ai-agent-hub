"""Check cross-dataset referential integrity, cycles, orphan sources, and graph coverage."""

from __future__ import annotations

import argparse
import collections
import pathlib
import sys

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import (
    DATASET_ORDER,
    DATASETS,
    GRAPH_REQUIRED_PREFIXES,
    PREFIX_TO_DATASET,
    ROOT,
    configure_stdio,
    id_prefix,
    read_all_present,
    split_pipe,
)

ALLOWED_RELATIONS = frozenset(
    {
        "requires",
        "part_of",
        "implements",
        "enables",
        "mitigates",
        "measures",
        "uses",
        "contrasts_with",
        "specializes",
        "example_of",
    }
)


def _find_cycles(adj: dict[str, list[str]]) -> list[list[str]]:
    """Detect directed cycles using standard 3-color DFS."""
    state: dict[str, int] = {}  # 0=unvisited, 1=visiting, 2=done
    cycles: list[list[str]] = []

    def dfs(node: str, stack: list[str]) -> None:
        state[node] = 1
        stack.append(node)
        for nxt in adj.get(node, []):
            st = state.get(nxt, 0)
            if st == 1:
                idx = stack.index(nxt)
                cycles.append(stack[idx:] + [nxt])
            elif st == 0 and nxt in adj:
                dfs(nxt, stack)
        stack.pop()
        state[node] = 2

    for n in sorted(adj):
        if state.get(n, 0) == 0:
            dfs(n, [])
    return cycles


def check_integrity(allow_missing_datasets: bool = False) -> list[str]:
    """Run all relational, cycle, orphan, and edge checks. Return error strings."""
    errors: list[str] = []
    present = read_all_present()

    missing_datasets = [name for name in DATASET_ORDER if name not in present]
    if missing_datasets and not allow_missing_datasets:
        errors.append(
            f"Missing datasets ({len(missing_datasets)}): {', '.join(missing_datasets)}"
        )

    defined_by_ds: dict[str, set[str]] = {}
    all_defined: set[str] = set()
    for name, rows in present.items():
        if name == "glossary_aliases":
            continue
        ids = {r.get("id", "").strip() for r in rows if r.get("id", "").strip()}
        defined_by_ds[name] = ids
        all_defined |= ids

    cited_sources: set[str] = set()

    # 1. Dangling cross-references & allowed prefix checks
    for ds_name in DATASET_ORDER:
        rows = present.get(ds_name, [])
        if not rows:
            continue
        spec = DATASETS[ds_name]
        for row in rows:
            row_id = row.get("id") or row.get("alias") or ""
            for col, allowed_prefixes in spec.ref_cols.items():
                for token in split_pipe(row.get(col, "")):
                    pref = id_prefix(token)
                    if pref not in allowed_prefixes:
                        errors.append(
                            f"{spec.filename}:{row_id}.{col}: ID {token!r} prefix {pref!r} not in allowed {allowed_prefixes}"
                        )
                    elif token not in all_defined:
                        errors.append(
                            f"{spec.filename}:{row_id}.{col}: dangling reference {token!r} (target dataset missing or ID undefined)"
                        )
                    elif pref == "SRC":
                        cited_sources.add(token)

            if ds_name == "patterns":
                df = row.get("diagram_file", "").strip()
                if df and not (ROOT / df).exists():
                    errors.append(
                        f"patterns.csv:{row_id}.diagram_file: referenced SVG {df!r} does not exist"
                    )

    # 2. Cycle checks: concepts.prerequisite_ids, learning_paths.prerequisite_ids, agent_types.parent_id
    for ds_name, col in (
        ("concepts", "prerequisite_ids"),
        ("learning_paths", "prerequisite_ids"),
        ("agent_types", "parent_id"),
    ):
        if ds_name not in present:
            continue
        adj: dict[str, list[str]] = {}
        for row in present[ds_name]:
            rid = row["id"]
            adj[rid] = [t for t in split_pipe(row.get(col, "")) if t]
            if rid in adj[rid]:
                errors.append(f"{ds_name}.csv:{rid}.{col}: self-reference cycle")
        for cyc in _find_cycles(adj):
            errors.append(f"{ds_name}.csv: circular {col} cycle: {' -> '.join(cyc)}")

    # 3. Orphan sources check
    if "sources" in present:
        all_src_ids = defined_by_ds.get("sources", set())
        orphans = sorted(all_src_ids - cited_sources)
        if orphans:
            errors.append(
                f"sources.csv: {len(orphans)} orphan source(s) never cited: {', '.join(orphans[:20])}{' ...' if len(orphans) > 20 else ''}"
            )

    # 4. Relationship edge checks & isolated entity detection
    if "relationships" in present:
        rel_rows = present["relationships"]
        seen_triples: set[tuple[str, str, str]] = set()
        edge_nodes: set[str] = set()
        for row in rel_rows:
            rid = row["id"]
            u = row["from_id"]
            rel = row["relation"]
            v = row["to_id"]
            if rel not in ALLOWED_RELATIONS:
                errors.append(f"relationships.csv:{rid}: invalid relation {rel!r}")
            if u == v:
                errors.append(f"relationships.csv:{rid}: self-loop on {u!r}")
            triple = (u, rel, v)
            if triple in seen_triples:
                errors.append(f"relationships.csv:{rid}: duplicate edge {triple}")
            else:
                seen_triples.add(triple)
            edge_nodes.add(u)
            edge_nodes.add(v)

        for pref in GRAPH_REQUIRED_PREFIXES:
            ds_name = PREFIX_TO_DATASET[pref]
            if ds_name in defined_by_ds:
                isolated = sorted(defined_by_ds[ds_name] - edge_nodes)
                if isolated:
                    errors.append(
                        f"{ds_name}.csv: {len(isolated)} isolated entity ID(s) with no edge in relationships.csv: {', '.join(isolated[:15])}{' ...' if len(isolated) > 15 else ''}"
                    )
    elif not allow_missing_datasets:
        errors.append("relationships.csv: missing; all entity rows lack relationship edges")

    # 5. Glossary aliases uniqueness check
    if "glossary_aliases" in present:
        seen_aliases: collections.Counter[str] = collections.Counter(
            r["alias"].strip().lower() for r in present["glossary_aliases"]
        )
        dups = [a for a, c in seen_aliases.items() if c > 1]
        if dups:
            errors.append(f"glossary_aliases.csv: duplicate aliases {dups}")

    return errors


def main(argv: list[str] | None = None) -> int:
    configure_stdio()
    parser = argparse.ArgumentParser(
        description="Check cross-references, cycles, orphans, and relationship graph integrity."
    )
    parser.add_argument(
        "--allow-missing-datasets",
        action="store_true",
        help="Only check references targeting already-present CSVs (for intermediate authoring).",
    )
    args = parser.parse_args(argv)

    errors = check_integrity(allow_missing_datasets=args.allow_missing_datasets)
    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        print(f"Integrity check failed with {len(errors)} error(s).")
        return 1
    print("Integrity check passed with 0 errors.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
