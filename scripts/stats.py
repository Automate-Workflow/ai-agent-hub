"""Print live summary counts, quality breakdowns, and target progress across datasets."""

from __future__ import annotations

import argparse
import collections
import json
import pathlib
import sys

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import DATASET_ORDER, DATASETS, configure_stdio, read_all_present


def compute_stats() -> dict[str, object]:
    """Compute per-dataset and global metrics directly from data/*.csv."""
    present = read_all_present()
    datasets_out: dict[str, dict[str, object]] = {}
    conf_total: collections.Counter[str] = collections.Counter()
    status_total: collections.Counter[str] = collections.Counter()
    rel_total: collections.Counter[str] = collections.Counter()

    for name in DATASET_ORDER:
        spec = DATASETS[name]
        rows = present.get(name, [])
        conf_c = collections.Counter(r.get("confidence", "") for r in rows if r.get("confidence"))
        stat_c = collections.Counter(r.get("status", "") for r in rows if r.get("status"))
        rel_c = collections.Counter(r.get("reliability", "") for r in rows if r.get("reliability"))
        conf_total.update(conf_c)
        status_total.update(stat_c)
        rel_total.update(rel_c)
        datasets_out[name] = {
            "filename": spec.filename,
            "rows": len(rows),
            "min_target": spec.min_target,
            "max_target": spec.max_target,
            "confidence": dict(conf_c),
            "status": dict(stat_c),
            "reliability": dict(rel_c),
        }

    return {
        "total_rows": sum(len(present.get(n, [])) for n in DATASET_ORDER),
        "datasets_present": len(present),
        "datasets_expected": len(DATASET_ORDER),
        "confidence_totals": dict(conf_total),
        "status_totals": dict(status_total),
        "source_reliability_totals": dict(rel_total),
        "datasets": datasets_out,
    }


def main(argv: list[str] | None = None) -> int:
    configure_stdio()
    parser = argparse.ArgumentParser(description="Compute live statistics for AI Agent Hub CSVs.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output instead of text table.")
    args = parser.parse_args(argv)

    summary = compute_stats()
    if args.json:
        print(json.dumps(summary, indent=2))
        return 0

    print(
        f"AI Agent Hub Stats — {summary['datasets_present']}/{summary['datasets_expected']} datasets, {summary['total_rows']} total rows"
    )
    print(f"{'Dataset':<22} {'Rows':>6} {'Target':>10} {'High':>6} {'Med':>6} {'Low':>6} {'Active':>7}")
    print("-" * 70)
    ds_map = summary["datasets"]
    assert isinstance(ds_map, dict)
    for name in DATASET_ORDER:
        d = ds_map[name]
        tgt = f"{d['min_target']}-{d['max_target']}" if d["max_target"] else f"{d['min_target']}+"
        c = d["confidence"]
        s = d["status"]
        print(
            f"{name:<22} {d['rows']:>6} {tgt:>10} {c.get('high',0):>6} {c.get('medium',0):>6} {c.get('low',0):>6} {s.get('active',0):>7}"
        )
    print("-" * 70)
    print("Source reliability:", summary["source_reliability_totals"])
    print("Confidence totals:", summary["confidence_totals"])
    print("Status totals:", summary["status_totals"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
