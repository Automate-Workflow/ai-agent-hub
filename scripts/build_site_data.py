"""Generate JSON bundles in site/data/ for the offline interactive explorer."""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from build_graph import build_graph_payload
from common import DATASET_ORDER, DATASETS, SITE_DIR, configure_stdio, read_csv_rows, write_text_lf
from stats import compute_stats


def build_site_data(output_dir: pathlib.Path) -> None:
    """Export per-dataset JSON files, search index, graph.json, and summary.json."""
    output_dir.mkdir(parents=True, exist_ok=True)
    search_items: list[dict[str, object]] = []

    for name in DATASET_ORDER:
        spec = DATASETS[name]
        _, rows = read_csv_rows(name)
        write_text_lf(output_dir / f"{name}.json", json.dumps(rows, indent=2) + "\n")
        if name in ("sources", "relationships", "glossary_aliases"):
            continue
        for row in rows:
            rid = row.get("id", "")
            label = row.get(spec.label_col, "")
            summary = (
                row.get("definition")
                or row.get("intent")
                or row.get("purpose")
                or row.get("expected_value")
                or row.get("description")
                or row.get("what_it_measures")
                or row.get("objective")
                or row.get("why_it_helps")
                or row.get("best_for")
                or ""
            )
            cat = (
                row.get("category")
                or row.get("view")
                or row.get("kind")
                or row.get("industry")
                or row.get("path_name")
                or name
            )
            search_items.append(
                {
                    "id": rid,
                    "dataset": name,
                    "title": label,
                    "category": cat,
                    "difficulty": row.get("difficulty") or row.get("level") or "",
                    "confidence": row.get("confidence", ""),
                    "status": row.get("status", ""),
                    "summary": summary[:280],
                }
            )

    search_items.sort(key=lambda item: str(item["id"]))
    write_text_lf(output_dir / "index.json", json.dumps(search_items, indent=2) + "\n")

    graph_payload = build_graph_payload()
    write_text_lf(output_dir / "graph.json", json.dumps(graph_payload, indent=2) + "\n")

    stats_payload = compute_stats()
    write_text_lf(output_dir / "summary.json", json.dumps(stats_payload, indent=2) + "\n")


def main(argv: list[str] | None = None) -> int:
    configure_stdio()
    parser = argparse.ArgumentParser(description="Build site/data/*.json bundles from data/*.csv.")
    parser.add_argument(
        "--output-dir",
        type=pathlib.Path,
        default=SITE_DIR / "data",
        help="Destination directory (default: site/data).",
    )
    args = parser.parse_args(argv)
    build_site_data(args.output_dir)
    print(f"Generated interactive explorer data bundles in {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
