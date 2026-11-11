"""Validate all CSV files in data/ against JSON Schemas and content rules."""

from __future__ import annotations

import argparse
import csv
import datetime as _dt
import pathlib
import re
import sys
from typing import Any

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import (
    DATA_DIR,
    DATASET_ORDER,
    DATASETS,
    EMOJI_RE,
    METRIC_CLAIM_COLS,
    METRIC_CLAIM_RE,
    PLACEHOLDER_RE,
    STRICT_NO_DIGIT_COLS,
    configure_stdio,
    load_schema,
    parse_iso_date,
    read_csv_rows,
    split_pipe,
)


def _token_set(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]{3,}", text.lower())}


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def validate_row_against_schema(
    row: dict[str, str],
    schema: dict[str, Any],
    row_id: str,
) -> list[str]:
    """Validate one CSV dictionary row against Draft 2020-12 string-typed schema."""
    errs: list[str] = []
    props = schema.get("properties", {})
    req = set(schema.get("required", []))
    allow_extra = schema.get("additionalProperties", True)

    for rcol in req:
        if rcol not in row:
            errs.append(f"{row_id}: missing required key {rcol!r}")

    if allow_extra is False:
        extra = set(row.keys()) - set(props.keys())
        if extra:
            errs.append(f"{row_id}: unexpected columns {sorted(extra)}")

    for col, val in row.items():
        if col not in props:
            continue
        p = props[col]
        if not isinstance(val, str):
            errs.append(f"{row_id}.{col}: expected string")
            continue
        min_len = p.get("minLength")
        if min_len is not None and len(val) < min_len:
            errs.append(f"{row_id}.{col}: length {len(val)} < minLength {min_len}")
        max_len = p.get("maxLength")
        if max_len is not None and len(val) > max_len:
            errs.append(f"{row_id}.{col}: length {len(val)} > maxLength {max_len}")
        enum = p.get("enum")
        if enum is not None and val not in enum:
            errs.append(f"{row_id}.{col}: {val!r} not in allowed vocabulary {enum}")
        pat = p.get("pattern")
        if pat is not None and not re.search(pat, val):
            errs.append(f"{row_id}.{col}: {val!r} fails pattern {pat!r}")
    return errs


def validate_all(
    today: _dt.date,
    check_stale_only: bool = False,
) -> tuple[list[str], list[str], list[str]]:
    """Run full validation and return (errors, warnings, stale_rows)."""
    errors: list[str] = []
    warnings: list[str] = []
    stale_rows: list[str] = []

    _, src_rows = read_csv_rows("sources")
    source_reliability: dict[str, str] = {}
    seen_src_urls: dict[str, str] = {}
    for row in src_rows:
        sid = row.get("id", "").strip()
        rel = row.get("reliability", "").strip()
        if sid:
            source_reliability[sid] = rel

    for ds_name in DATASET_ORDER:
        spec = DATASETS[ds_name]
        csv_path = DATA_DIR / spec.filename
        if not csv_path.exists():
            continue

        raw = csv_path.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf") or raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
            errors.append(f"{spec.filename}: contains UTF BOM")
        if b"\r" in raw:
            errors.append(f"{spec.filename}: contains CR/CRLF line endings (LF required)")

        schema = load_schema(ds_name)
        expected_cols = list(schema["properties"].keys())

        with csv_path.open("r", encoding="utf-8", newline="") as fh:
            raw_rows = list(csv.reader(fh))
        if not raw_rows:
            errors.append(f"{spec.filename}: file is empty")
            continue
        header = raw_rows[0]
        if header != expected_cols:
            errors.append(
                f"{spec.filename}: header mismatch: got {header}, expected {expected_cols}"
            )
            continue

        for line_no, raw_row in enumerate(raw_rows[1:], start=2):
            if len(raw_row) != len(expected_cols):
                errors.append(
                    f"{spec.filename}:{line_no}: expected {len(expected_cols)} columns, got {len(raw_row)}"
                )

        _, dict_rows = read_csv_rows(ds_name)
        seen_ids: set[str] = set()
        seen_norm_labels: dict[str, str] = {}
        seen_res_urls: dict[str, str] = {}
        prose_vectors: list[tuple[str, str, set[str]]] = []

        for idx, row in enumerate(dict_rows, start=2):
            row_id = row.get("id") or row.get("alias") or f"line-{idx}"
            if len(row) != len(expected_cols):
                continue

            if ds_name == "glossary_aliases":
                key_id = row.get("alias", "").strip().lower()
            else:
                key_id = row.get("id", "").strip()
            if key_id in seen_ids:
                errors.append(f"{spec.filename}: duplicate identifier {key_id!r}")
            else:
                seen_ids.add(key_id)

            errors.extend(validate_row_against_schema(row, schema, f"{spec.filename}:{row_id}"))

            # List separator checks
            for lcol in spec.list_cols:
                val = row.get(lcol, "")
                if "," in val or ";" in val:
                    errors.append(
                        f"{spec.filename}:{row_id}.{lcol}: invalid list delimiter (use '|' only): {val!r}"
                    )
                if " | " in val or val.startswith(" ") or val.endswith(" "):
                    errors.append(
                        f"{spec.filename}:{row_id}.{lcol}: extra spaces in pipe list: {val!r}"
                    )

            # Placeholder, disallowed term, emoji checks
            for col, val in row.items():
                if EMOJI_RE.search(val):
                    errors.append(f"{spec.filename}:{row_id}.{col}: emoji detected")
                if PLACEHOLDER_RE.search(val):
                    errors.append(f"{spec.filename}:{row_id}.{col}: forbidden term/placeholder in {val!r}")

            # Duplicate URL check for sources & resources
            if ds_name == "sources":
                url = row.get("url", "").strip()
                notes = row.get("notes", "")
                if url in seen_src_urls and "alias_of:" not in notes:
                    errors.append(
                        f"sources.csv:{row_id}: duplicate URL {url!r} (already {seen_src_urls[url]}; add 'alias_of: {seen_src_urls[url]}' if intentional)"
                    )
                else:
                    seen_src_urls.setdefault(url, row_id)

                pd = row.get("published_date", "").strip()
                if pd:
                    if pd.endswith("-01"):
                        errors.append(
                            f"sources.csv:{row_id}: synthetic '-01' day placeholder in published_date={pd!r}"
                        )
                    pdt = parse_iso_date(pd)
                    if pdt and pdt > today:
                        errors.append(f"sources.csv:{row_id}: future published_date {pd!r}")
                ad = parse_iso_date(row.get("accessed_date", ""))
                if ad and ad > today:
                    errors.append(f"sources.csv:{row_id}: future accessed_date {row.get('accessed_date')!r}")

            if ds_name == "resources":
                url = row.get("url", "").strip()
                if url in seen_res_urls:
                    errors.append(
                        f"resources.csv:{row_id}: duplicate URL {url!r} (already {seen_res_urls[url]})"
                    )
                else:
                    seen_res_urls[url] = row_id

            # Confidence honesty check (high requires >=1 primary source)
            if "confidence" in row and "source_ids" in row:
                if row["confidence"] == "high":
                    sids = split_pipe(row["source_ids"])
                    has_primary = any(source_reliability.get(s) == "primary" for s in sids)
                    if not has_primary:
                        errors.append(
                            f"{spec.filename}:{row_id}: confidence=high without a primary source in sources.csv ({sids})"
                        )

            # Date checks
            if "verified_date" in row:
                vd = parse_iso_date(row.get("verified_date", ""))
                if not vd:
                    errors.append(f"{spec.filename}:{row_id}: invalid verified_date {row.get('verified_date')!r}")
                elif vd > today:
                    errors.append(f"{spec.filename}:{row_id}: future verified_date {vd}")
                if "next_review_date" in row:
                    nr = parse_iso_date(row.get("next_review_date", ""))
                    if not nr:
                        errors.append(f"{spec.filename}:{row_id}: invalid next_review_date")
                    elif vd and nr < vd:
                        errors.append(f"{spec.filename}:{row_id}: next_review_date {nr} < verified_date {vd}")
                    elif nr and nr < today and row.get("status") == "active":
                        days_past = (today - nr).days
                        stale_rows.append(f"{spec.filename}:{row_id} ({days_past}d past {nr})")

            # Qualitative digit & metric claim checks
            for col, val in row.items():
                if col in STRICT_NO_DIGIT_COLS and re.search(r"\d", val):
                    errors.append(
                        f"{spec.filename}:{row_id}.{col}: digits disallowed in qualitative column: {val!r}"
                    )
                elif col in METRIC_CLAIM_COLS and METRIC_CLAIM_RE.search(val):
                    errors.append(
                        f"{spec.filename}:{row_id}.{col}: uncited numeric/percent claim: {val!r}"
                    )

            # Near-duplicate checks within dataset
            if ds_name not in ("relationships", "use_cases", "learning_paths", "glossary_aliases"):
                lbl = row.get(spec.label_col, "").strip()
                norm_lbl = re.sub(r"[^a-z0-9]", "", lbl.lower())
                if norm_lbl and norm_lbl in seen_norm_labels:
                    errors.append(
                        f"{spec.filename}:{row_id}: duplicate normalized label {lbl!r} (same as {seen_norm_labels[norm_lbl]})"
                    )
                elif norm_lbl:
                    seen_norm_labels[norm_lbl] = row_id

            if ds_name in ("concepts", "agent_types", "patterns", "risks_security", "evaluation"):
                prose_field = (
                    row.get("definition")
                    or row.get("intent")
                    or row.get("description")
                    or row.get("what_it_measures")
                    or ""
                )
                cat = row.get("category") or row.get("view") or row.get("kind") or ""
                vec = _token_set(prose_field)
                if len(vec) >= 6:
                    for prev_id, prev_cat, prev_vec in prose_vectors:
                        if cat == prev_cat and _jaccard(vec, prev_vec) >= 0.85:
                            errors.append(
                                f"{spec.filename}:{row_id}: near-duplicate description to {prev_id}"
                            )
                    prose_vectors.append((row_id, cat, vec))

    if check_stale_only:
        return [], warnings, stale_rows
    return errors, warnings, stale_rows


def main(argv: list[str] | None = None) -> int:
    configure_stdio()
    parser = argparse.ArgumentParser(description="Validate AI Agent Hub CSV datasets and schemas.")
    parser.add_argument(
        "--today",
        default=_dt.date.today().isoformat(),
        help="Reference ISO date YYYY-MM-DD (default: today).",
    )
    parser.add_argument(
        "--stale",
        action="store_true",
        help="Only print rows past their next_review_date and exit 0 if none.",
    )
    parser.add_argument(
        "--fail-on-warnings",
        action="store_true",
        help="Treat validation warnings as a failing exit code.",
    )
    args = parser.parse_args(argv)
    ref_date = parse_iso_date(args.today)
    if not ref_date:
        print(f"ERROR: invalid --today date {args.today!r}", file=sys.stderr)
        return 2

    errors, warnings, stale = validate_all(ref_date, check_stale_only=args.stale)
    if args.stale:
        print(f"Stale rows as of {ref_date}: {len(stale)}")
        for item in stale:
            print(f"  - {item}")
        return 1 if stale else 0

    for w in warnings:
        print(f"WARN: {w}")
    for e in errors:
        print(f"ERROR: {e}")

    print(
        f"Validation finished against {ref_date}: {len(errors)} error(s), {len(warnings)} warning(s), {len(stale)} stale."
    )
    if errors or (args.fail_on_warnings and warnings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
