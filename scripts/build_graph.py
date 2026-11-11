"""Build normalized graph JSON (nodes and relationship edges) for the interactive explorer."""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import (
    DATASET_ORDER,
    DATASETS,
    SITE_DIR,
    configure_stdio,
    read_all_present,
    write_text_lf,
)


def build_graph_payload() -> dict[str, object]:
    """Assemble deterministic sorted nodes and edges from CSVs."""
    present = read_all_present()
    nodes: list[dict[str, object]] = []
    node_ids: set[str] = set()

    for name in DATASET_ORDER:
        if name in ("sources", "relationships", "glossary_aliases"):
            continue
        spec = DATASETS[name]
        for row in present.get(name, []):
            nid = row.get("id", "").strip()
            if not nid:
                continue
            node_ids.add(nid)
            label = row.get(spec.label_col, "") or nid
            group = (
                row.get("category")
                or row.get("view")
                or row.get("kind")
                or row.get("industry")
                or row.get("path_name")
                or name
            )
            nodes.append(
                {
                    "id": nid,
                    "label": label,
                    "dataset": name,
                    "group": group,
                    "confidence": row.get("confidence", ""),
                    "status": row.get("status", ""),
                }
            )

    nodes.sort(key=lambda n: str(n["id"]))

    edges: list[dict[str, object]] = []
    for row in present.get("relationships", []):
        u = row.get("from_id", "").strip()
        v = row.get("to_id", "").strip()
        edges.append(
            {
                "id": row.get("id", ""),
                "source": u,
                "target": v,
                "relation": row.get("relation", ""),
                "note": row.get("note", ""),
                "confidence": row.get("confidence", ""),
                "endpoints_present": (u in node_ids and v in node_ids),
            }
        )

    edges.sort(key=lambda e: str(e["id"]))
    return {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges,
    }


def main(argv: list[str] | None = None) -> int:
    configure_stdio()
    parser = argparse.ArgumentParser(description="Build site/data/graph.json from CSVs.")
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        default=SITE_DIR / "data" / "graph.json",
        help="Output JSON path (default: site/data/graph.json).",
    )
    args = parser.parse_args(argv)

    payload = build_graph_payload()
    write_text_lf(args.output, json.dumps(payload, indent=2) + "\n")
    print(
        f"Wrote graph JSON ({payload['node_count']} nodes, {payload['edge_count']} edges) to {args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
