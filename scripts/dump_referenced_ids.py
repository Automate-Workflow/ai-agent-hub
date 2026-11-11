"""Identify all IDs referenced in data/*.csv that are not yet defined."""

from __future__ import annotations

import argparse
import pathlib
import sys

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import (
    DATASET_ORDER,
    DATASETS,
    PREFIX_TO_DATASET,
    REPORTS_DIR,
    configure_stdio,
    id_prefix,
    read_all_present,
    split_pipe,
    write_csv_rows,
)


def collect_reserved_ids() -> list[dict[str, str]]:
    """Collect every referenced ID not present in its target dataset."""
    present = read_all_present()
    defined_ids: set[str] = set()
    for name, rows in present.items():
        if name == "glossary_aliases":
            continue
        for row in rows:
            rid = row.get("id", "").strip()
            if rid:
                defined_ids.add(rid)

    records: list[dict[str, str]] = []
    for ds_name in DATASET_ORDER:
        rows = present.get(ds_name, [])
        if not rows:
            continue
        spec = DATASETS[ds_name]
        for row in rows:
            src_row_id = row.get("id") or row.get("alias") or ""
            for col in spec.ref_cols:
                raw_val = row.get(col, "").strip()
                if not raw_val:
                    continue
                for token in split_pipe(raw_val):
                    if token not in defined_ids:
                        pref = id_prefix(token)
                        target_ds = PREFIX_TO_DATASET.get(pref, "unknown")
                        target_file = (
                            f"data/{DATASETS[target_ds].filename}"
                            if target_ds in DATASETS
                            else "unknown"
                        )
                        records.append(
                            {
                                "id": token,
                                "prefix": pref,
                                "target_file": target_file,
                                "source_file": f"data/{spec.filename}",
                                "source_row_id": src_row_id,
                                "column": col,
                            }
                        )

    records.sort(
        key=lambda r: (
            r["prefix"],
            r["id"],
            r["source_file"],
            r["source_row_id"],
            r["column"],
        )
    )
    return records


def main(argv: list[str] | None = None) -> int:
    configure_stdio()
    parser = argparse.ArgumentParser(
        description="Write unresolved referenced IDs to reports/reserved_ids.csv."
    )
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        default=REPORTS_DIR / "reserved_ids.csv",
        help="Destination CSV path (default: reports/reserved_ids.csv).",
    )
    args = parser.parse_args(argv)

    records = collect_reserved_ids()
    fieldnames = ["id", "prefix", "target_file", "source_file", "source_row_id", "column"]
    write_csv_rows(args.output, fieldnames, records)
    unique_ids = sorted({r["id"] for r in records})
    print(f"Wrote {len(records)} reference occurrences ({len(unique_ids)} unique IDs) to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
