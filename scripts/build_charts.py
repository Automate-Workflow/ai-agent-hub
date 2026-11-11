"""Generate red-theme SVG charts in charts/ (and optional data-driven risk heatmap) from CSV data."""

from __future__ import annotations

import argparse
import collections
import html
import pathlib
import sys

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import (
    CHARTS_DIR,
    DATASET_ORDER,
    DATASETS,
    DIAGRAMS_DIR,
    FONT_STACK,
    PALETTE,
    configure_stdio,
    read_all_present,
    write_text_lf,
)


def _esc(text: str) -> str:
    return html.escape(str(text), quote=True)


def _svg_header(width: int, height: int, title: str, desc: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img">',
        f"  <title>{_esc(title)}</title>",
        f"  <desc>{_esc(desc)}</desc>",
        f'  <rect width="{width}" height="{height}" rx="12" fill="{PALETTE["white"]}" stroke="{PALETTE["border"]}" stroke-width="1"/>',
        f'  <rect x="0" y="0" width="{width}" height="6" rx="3" fill="{PALETTE["primary"]}"/>',
    ]


def render_hbar_chart(
    title: str,
    subtitle: str,
    desc: str,
    rows: list[tuple[str, int, int | None]],
    width: int = 920,
) -> str:
    """Render deterministic horizontal bar chart with optional dashed target marker."""
    row_h = 34
    top_pad = 84
    bottom_pad = 36
    left_label = 210
    right_pad = 72
    bar_w = width - left_label - right_pad
    height = max(220, top_pad + bottom_pad + max(len(rows), 1) * row_h)

    max_val = max([max(v, t or 0) for _, v, t in rows] + [1])
    lines = _svg_header(width, height, title, desc)
    lines.append(
        f'  <text x="28" y="38" font-family="{FONT_STACK}" font-size="20" font-weight="700" fill="{PALETTE["ink"]}">{_esc(title)}</text>'
    )
    lines.append(
        f'  <text x="28" y="60" font-family="{FONT_STACK}" font-size="13" fill="{PALETTE["muted"]}">{_esc(subtitle)}</text>'
    )

    if not rows:
        lines.append(
            f'  <text x="{width // 2}" y="{height // 2}" text-anchor="middle" font-family="{FONT_STACK}" font-size="14" fill="{PALETTE["muted"]}">No rows available yet.</text>'
        )
    else:
        for idx, (label, val, target) in enumerate(rows):
            y = top_pad + idx * row_h
            bw = round((val / max_val) * bar_w, 1) if val > 0 else 0.0
            lines.append(
                f'  <text x="{left_label - 12}" y="{y + 18}" text-anchor="end" font-family="{FONT_STACK}" font-size="12.5" font-weight="500" fill="{PALETTE["ink"]}">{_esc(label)}</text>'
            )
            lines.append(
                f'  <rect x="{left_label}" y="{y + 4}" width="{bar_w}" height="20" rx="4" fill="{PALETTE["soft"]}"/>'
            )
            if bw > 0:
                fill = PALETTE["primary"] if (target is None or val >= target) else PALETTE["bright"]
                lines.append(
                    f'  <rect x="{left_label}" y="{y + 4}" width="{bw}" height="20" rx="4" fill="{fill}"/>'
                )
            if target is not None and target > 0:
                tx = left_label + round((target / max_val) * bar_w, 1)
                lines.append(
                    f'  <line x1="{tx}" y1="{y + 1}" x2="{tx}" y2="{y + 27}" stroke="{PALETTE["dark"]}" stroke-width="2" stroke-dasharray="3,2"/>'
                )
            lbl_txt = f"{val} / {target}+" if target is not None else str(val)
            lines.append(
                f'  <text x="{left_label + bar_w + 8}" y="{y + 18}" font-family="{FONT_STACK}" font-size="12" font-weight="600" fill="{PALETTE["ink"]}">{_esc(lbl_txt)}</text>'
            )

    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def render_stacked_chart(
    title: str,
    subtitle: str,
    desc: str,
    series: list[tuple[str, str]],
    rows: list[tuple[str, dict[str, int]]],
    width: int = 920,
) -> str:
    """Render deterministic horizontal stacked bar chart."""
    row_h = 34
    top_pad = 104
    bottom_pad = 36
    left_label = 210
    right_pad = 64
    bar_w = width - left_label - right_pad
    height = max(240, top_pad + bottom_pad + max(len(rows), 1) * row_h)

    max_total = max([sum(counts.values()) for _, counts in rows] + [1])
    lines = _svg_header(width, height, title, desc)
    lines.append(
        f'  <text x="28" y="38" font-family="{FONT_STACK}" font-size="20" font-weight="700" fill="{PALETTE["ink"]}">{_esc(title)}</text>'
    )
    lines.append(
        f'  <text x="28" y="58" font-family="{FONT_STACK}" font-size="13" fill="{PALETTE["muted"]}">{_esc(subtitle)}</text>'
    )

    lx = 28
    for key, color in series:
        lines.append(f'  <rect x="{lx}" y="72" width="12" height="12" rx="2" fill="{color}"/>')
        lines.append(
            f'  <text x="{lx + 18}" y="82" font-family="{FONT_STACK}" font-size="12" fill="{PALETTE["ink"]}">{_esc(key)}</text>'
        )
        lx += 28 + len(key) * 8 + 16

    if not rows:
        lines.append(
            f'  <text x="{width // 2}" y="{height // 2}" text-anchor="middle" font-family="{FONT_STACK}" font-size="14" fill="{PALETTE["muted"]}">No rows available yet.</text>'
        )
    else:
        for idx, (label, counts) in enumerate(rows):
            y = top_pad + idx * row_h
            total = sum(counts.values())
            lines.append(
                f'  <text x="{left_label - 12}" y="{y + 18}" text-anchor="end" font-family="{FONT_STACK}" font-size="12.5" font-weight="500" fill="{PALETTE["ink"]}">{_esc(label)}</text>'
            )
            lines.append(
                f'  <rect x="{left_label}" y="{y + 4}" width="{bar_w}" height="20" rx="4" fill="{PALETTE["soft"]}"/>'
            )
            cur_x = float(left_label)
            for key, color in series:
                c = counts.get(key, 0)
                if c <= 0:
                    continue
                seg_w = (c / max_total) * bar_w
                lines.append(
                    f'  <rect x="{round(cur_x, 1)}" y="{y + 4}" width="{round(seg_w, 1)}" height="20" fill="{color}"/>'
                )
                cur_x += seg_w
            lines.append(
                f'  <text x="{left_label + bar_w + 8}" y="{y + 18}" font-family="{FONT_STACK}" font-size="12" font-weight="600" fill="{PALETTE["ink"]}">{total}</text>'
            )

    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def render_risk_heatmap(risk_rows: list[dict[str, str]]) -> str:
    """Render data-driven likelihood x impact matrix SVG from risks_security.csv."""
    width, height = 1200, 620
    lines = _svg_header(
        width,
        height,
        "AI Agent Risk Likelihood vs Impact Matrix",
        "Data-driven risk matrix summarizing entries from data/risks_security.csv.",
    )
    lines.append(
        f'  <text x="40" y="46" font-family="{FONT_STACK}" font-size="24" font-weight="700" fill="{PALETTE["ink"]}">AI Agent Risk Heatmap (Likelihood vs Impact)</text>'
    )
    lines.append(
        f'  <text x="40" y="70" font-family="{FONT_STACK}" font-size="14" fill="{PALETTE["muted"]}">Counts computed directly from {len(risk_rows)} verified entries in data/risks_security.csv</text>'
    )

    impacts = ["critical", "high", "medium", "low"]
    likelihoods = ["high", "medium", "low"]
    grid: dict[tuple[str, str], list[str]] = collections.defaultdict(list)
    for r in risk_rows:
        grid[(r.get("likelihood", "medium"), r.get("impact", "medium"))].append(r.get("id", ""))

    cell_fills = {
        ("high", "critical"): PALETTE["dark"],
        ("high", "high"): PALETTE["primary"],
        ("medium", "critical"): PALETTE["primary"],
        ("high", "medium"): PALETTE["bright"],
        ("medium", "high"): PALETTE["bright"],
        ("low", "critical"): PALETTE["bright"],
        ("medium", "medium"): "#FCA5A5",
        ("low", "high"): "#FCA5A5",
        ("high", "low"): "#FCA5A5",
        ("low", "medium"): PALETTE["tint"],
        ("medium", "low"): PALETTE["tint"],
        ("low", "low"): PALETTE["soft"],
    }

    start_x, start_y, cw, ch = 180, 130, 235, 130
    for ci, imp in enumerate(impacts):
        cx = start_x + ci * cw + cw // 2
        lines.append(
            f'  <text x="{cx}" y="112" text-anchor="middle" font-family="{FONT_STACK}" font-size="15" font-weight="700" fill="{PALETTE["ink"]}">Impact: {imp.title()}</text>'
        )

    for ri, lik in enumerate(likelihoods):
        cy = start_y + ri * ch
        lines.append(
            f'  <text x="{start_x - 18}" y="{cy + ch // 2 + 5}" text-anchor="end" font-family="{FONT_STACK}" font-size="14" font-weight="700" fill="{PALETTE["ink"]}">Likelihood: {lik.title()}</text>'
        )
        for ci, imp in enumerate(impacts):
            cx = start_x + ci * cw
            ids = sorted(grid.get((lik, imp), []))
            bg = cell_fills.get((lik, imp), PALETTE["soft"])
            fg = PALETTE["white"] if bg in (PALETTE["dark"], PALETTE["primary"], PALETTE["bright"]) else PALETTE["ink"]
            lines.append(
                f'  <rect x="{cx + 4}" y="{cy + 4}" width="{cw - 8}" height="{ch - 8}" rx="8" fill="{bg}" stroke="{PALETTE["white"]}" stroke-width="2"/>'
            )
            lines.append(
                f'  <text x="{cx + cw // 2}" y="{cy + 56}" text-anchor="middle" font-family="{FONT_STACK}" font-size="28" font-weight="700" fill="{fg}">{len(ids)}</text>'
            )
            sample = ", ".join(ids[:4]) + ("..." if len(ids) > 4 else "")
            lines.append(
                f'  <text x="{cx + cw // 2}" y="{cy + 88}" text-anchor="middle" font-family="{FONT_STACK}" font-size="11.5" fill="{fg}">{_esc(sample or "None")}</text>'
            )

    lines.append(
        f'  <text x="40" y="575" font-family="{FONT_STACK}" font-size="12.5" fill="{PALETTE["muted"]}">Generated deterministically by scripts/build_charts.py from data/risks_security.csv</text>'
    )
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def generate_all_charts(output_dir: pathlib.Path, with_risk_heatmap: bool = False) -> list[pathlib.Path]:
    """Build all 8 SVG charts into output_dir and optionally update diagrams/risk-heatmap.svg."""
    output_dir.mkdir(parents=True, exist_ok=True)
    present = read_all_present()
    written: list[pathlib.Path] = []

    # 1. Entries per dataset
    ds_rows = [
        (DATASETS[n].filename.replace(".csv", ""), len(present.get(n, [])), DATASETS[n].min_target)
        for n in DATASET_ORDER
    ]
    p1 = output_dir / "entries-per-dataset.svg"
    write_text_lf(
        p1,
        render_hbar_chart(
            "Entries per Dataset vs Target",
            "Actual verified rows compared to minimum specification targets (dashed lines)",
            "Bar chart of row counts across all 13 AI Agent Hub datasets.",
            ds_rows,
        ),
    )
    written.append(p1)

    # 2. Concepts by category
    cp_counts = collections.Counter(r.get("category", "") for r in present.get("concepts", []))
    cp_rows = [(k, cp_counts[k], None) for k in sorted(cp_counts) if k]
    p2 = output_dir / "concepts-by-category.svg"
    write_text_lf(
        p2,
        render_hbar_chart(
            "Concepts by Category",
            "Distribution across concept taxonomy domains in data/concepts.csv",
            "Concept counts per category.",
            cp_rows,
        ),
    )
    written.append(p2)

    # 3. Agent types by view and maturity
    at_rows_raw = present.get("agent_types", [])
    by_view: dict[str, collections.Counter[str]] = collections.defaultdict(collections.Counter)
    for r in at_rows_raw:
        by_view[r.get("view", "unknown")][r.get("maturity", "unknown")] += 1
    p3 = output_dir / "agent-types-breakdown.svg"
    write_text_lf(
        p3,
        render_stacked_chart(
            "Agent Types by Lens and Maturity",
            "Breakdown across decision_logic, job, and architecture views in data/agent_types.csv",
            "Stacked bar chart of agent types by view and maturity.",
            [("established", PALETTE["dark"]), ("growing", PALETTE["primary"]), ("emerging", PALETTE["bright"])],
            [(v, dict(by_view[v])) for v in sorted(by_view)],
        ),
    )
    written.append(p3)

    # 4. Frameworks by category and open-source status
    fw_rows_raw = present.get("frameworks_tools", [])
    by_cat: dict[str, collections.Counter[str]] = collections.defaultdict(collections.Counter)
    for r in fw_rows_raw:
        by_cat[r.get("category", "unknown")][r.get("open_source", "unknown")] += 1
    p4 = output_dir / "frameworks-by-category-oss.svg"
    write_text_lf(
        p4,
        render_stacked_chart(
            "Frameworks and Tools by Category and License Model",
            "Stacked by OSI open_source=yes, partial (open-core/SDK), and no (proprietary/source-available)",
            "Frameworks stacked by category and open-source classification.",
            [("yes", PALETTE["primary"]), ("partial", PALETTE["bright"]), ("no", PALETTE["muted"])],
            [(c, dict(by_cat[c])) for c in sorted(by_cat)],
        ),
    )
    written.append(p4)

    # 5. Use cases by industry
    uc_counts = collections.Counter(r.get("industry", "") for r in present.get("use_cases", []))
    p5 = output_dir / "use-cases-by-industry.svg"
    write_text_lf(
        p5,
        render_hbar_chart(
            "Use Cases by Industry",
            "Coverage across vertical sectors in data/use_cases.csv",
            "Use case counts per industry sector.",
            [(k, uc_counts[k], None) for k in sorted(uc_counts) if k],
        ),
    )
    written.append(p5)

    # 6. Risks by category and impact
    rs_rows_raw = present.get("risks_security", [])
    by_rcat: dict[str, collections.Counter[str]] = collections.defaultdict(collections.Counter)
    for r in rs_rows_raw:
        by_rcat[r.get("category", "unknown")][r.get("impact", "unknown")] += 1
    p6 = output_dir / "risks-by-category-impact.svg"
    write_text_lf(
        p6,
        render_stacked_chart(
            "Risks by Category and Impact Severity",
            "Distribution across security, privacy, reliability, cost, legal, ethics, and operational domains",
            "Stacked bar chart of risks by category and impact level.",
            [
                ("critical", PALETTE["dark"]),
                ("high", PALETTE["primary"]),
                ("medium", PALETTE["bright"]),
                ("low", "#FCA5A5"),
            ],
            [(c, dict(by_rcat[c])) for c in sorted(by_rcat)],
        ),
    )
    written.append(p6)

    # 7. Source reliability and confidence mix
    src_rel = collections.Counter(r.get("reliability", "") for r in present.get("sources", []))
    conf_all: collections.Counter[str] = collections.Counter()
    for name in DATASET_ORDER:
        for r in present.get(name, []):
            c = r.get("confidence", "")
            if c:
                conf_all[c] += 1
    p7 = output_dir / "source-reliability-confidence.svg"
    write_text_lf(
        p7,
        render_hbar_chart(
            "Source Reliability and Content Confidence Mix",
            "Source reliability tiers (sources.csv) and content row confidence levels",
            "Bar chart summarizing source reliability and confidence counts.",
            [
                ("sources: primary", src_rel.get("primary", 0), None),
                ("sources: secondary", src_rel.get("secondary", 0), None),
                ("sources: tertiary", src_rel.get("tertiary", 0), None),
                ("rows: high confidence", conf_all.get("high", 0), None),
                ("rows: medium confidence", conf_all.get("medium", 0), None),
                ("rows: low confidence", conf_all.get("low", 0), None),
            ],
        ),
    )
    written.append(p7)

    # 8. Freshness and verification status
    stat_all: collections.Counter[str] = collections.Counter()
    rev_years: collections.Counter[str] = collections.Counter()
    for name in DATASET_ORDER:
        for r in present.get(name, []):
            st = r.get("status", "")
            if st:
                stat_all[st] += 1
            nr = r.get("next_review_date", "")
            if len(nr) >= 7:
                rev_years[nr[:7]] += 1
    rows8 = [
        ("status: active", stat_all.get("active", 0), None),
        ("status: needs-review", stat_all.get("needs-review", 0), None),
        ("status: deprecated", stat_all.get("deprecated", 0), None),
    ] + [(f"due {ym}", rev_years[ym], None) for ym in sorted(rev_years)]
    p8 = output_dir / "freshness-status.svg"
    write_text_lf(
        p8,
        render_hbar_chart(
            "Verification Status and Next Review Schedule",
            "Distribution of row status values and scheduled next review months",
            "Status and review window distribution across datasets.",
            rows8,
        ),
    )
    written.append(p8)

    if with_risk_heatmap:
        hm_path = DIAGRAMS_DIR / "risk-heatmap.svg"
        write_text_lf(hm_path, render_risk_heatmap(rs_rows_raw))
        written.append(hm_path)

    return written


def main(argv: list[str] | None = None) -> int:
    configure_stdio()
    parser = argparse.ArgumentParser(description="Generate red-theme SVG charts from CSV data.")
    parser.add_argument(
        "--output-dir",
        type=pathlib.Path,
        default=CHARTS_DIR,
        help="Target chart output directory (default: charts).",
    )
    parser.add_argument(
        "--with-risk-heatmap",
        action="store_true",
        help="Also generate/update diagrams/risk-heatmap.svg from risks_security.csv.",
    )
    args = parser.parse_args(argv)
    written = generate_all_charts(args.output_dir, with_risk_heatmap=args.with_risk_heatmap)
    print(f"Generated {len(written)} SVG chart(s) in {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
