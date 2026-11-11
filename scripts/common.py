"""Shared paths, dataset definitions, CSV/JSON helpers, and constants for AI Agent Hub."""

from __future__ import annotations

import csv
import datetime as _dt
import json
import pathlib
import re
import sys
from dataclasses import dataclass
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
SCHEMA_DIR = DATA_DIR / "schema"
DOCS_DIR = ROOT / "docs"
DIAGRAMS_DIR = ROOT / "diagrams"
CHARTS_DIR = ROOT / "charts"
ASSETS_DIR = ROOT / "assets"
SITE_DIR = ROOT / "site"
REPORTS_DIR = ROOT / "reports"
SEED_DIR = ROOT / ".seed"

PALETTE = {
    "primary": "#B91C1C",
    "bright": "#DC2626",
    "dark": "#7F1D1D",
    "tint": "#FEE2E2",
    "soft": "#FEF2F2",
    "ink": "#111827",
    "muted": "#6B7280",
    "border": "#E5E7EB",
    "white": "#FFFFFF",
    "amber": "#B45309",
    "amber_bg": "#FEF3C7",
    "green": "#15803D",
    "green_bg": "#DCFCE7",
}

FONT_STACK = "Segoe UI, Roboto, Helvetica, Arial, sans-serif"

CONFIDENCE_VALUES = ("high", "medium", "low")
STATUS_VALUES = ("active", "needs-review", "deprecated")

DISALLOWED_WORKFLOW_TERM = "\x6e" + "8" + "\x6e"
EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF\u2600-\u27BF]")
PLACEHOLDER_RE = re.compile(
    rf"(\bTODO\b|\bTBD\b|\bFIXME\b|lorem\s+ipsum|example\.com|\b{DISALLOWED_WORKFLOW_TERM}\b)",
    re.IGNORECASE,
)

# Columns where bare digits or numeric metric claims are forbidden (qualitative prose only).
STRICT_NO_DIGIT_COLS = frozenset(
    {
        "expected_value",
        "why_it_matters",
        "strengths",
        "why_it_helps",
        "what_it_measures",
        "tradeoffs",
        "when_to_use",
        "when_not_to_use",
        "intent",
    }
)

# Columns checked against percent / multiplier quantitative claim patterns.
METRIC_CLAIM_COLS = frozenset(
    {
        "definition",
        "how_it_works",
        "description",
        "limitations",
        "best_for",
        "not_ideal_for",
        "main_risks",
        "purpose",
        "common_mistakes",
        "objective",
        "outcome",
    }
)

METRIC_CLAIM_RE = re.compile(
    r"(\b\d+(?:\.\d+)?\s*%|\b\d+(?:\.\d+)?\s*(?:percent|percentage)\b|\b\d+(?:\.\d+)?x\s+(?:faster|slower|higher|lower|more|less|improvement|reduction|roi|cheaper|better)\b|\b(?:save|saves|reduce|reduces|increase|increases|cut|cuts|boost|boosts)\s+(?:up\s+to\s+|by\s+)?\d+(?:\.\d+)?\s*%)",
    re.IGNORECASE,
)

PREFIX_TO_DATASET = {
    "CP": "concepts",
    "AT": "agent_types",
    "PT": "patterns",
    "PS": "protocols_standards",
    "FW": "frameworks_tools",
    "UC": "use_cases",
    "RS": "risks_security",
    "EV": "evaluation",
    "LP": "learning_paths",
    "RES": "resources",
    "RL": "relationships",
    "SRC": "sources",
}


@dataclass(frozen=True)
class DatasetSpec:
    name: str
    filename: str
    prefix: str | None
    min_target: int
    max_target: int | None
    label_col: str
    list_cols: tuple[str, ...]
    ref_cols: dict[str, tuple[str, ...]]
    review_days: int | None = None


DATASET_ORDER = (
    "sources",
    "concepts",
    "agent_types",
    "patterns",
    "protocols_standards",
    "frameworks_tools",
    "use_cases",
    "risks_security",
    "evaluation",
    "learning_paths",
    "resources",
    "relationships",
    "glossary_aliases",
)

ENTITY_PREFIXES = ("CP", "AT", "PT", "PS", "FW", "UC", "RS", "EV", "LP", "RES")
GRAPH_REQUIRED_PREFIXES = ("CP", "AT", "PT", "PS", "FW", "RS", "EV")

DATASETS: dict[str, DatasetSpec] = {
    "sources": DatasetSpec(
        name="sources",
        filename="sources.csv",
        prefix="SRC",
        min_target=150,
        max_target=None,
        label_col="title",
        list_cols=(),
        ref_cols={},
        review_days=None,
    ),
    "concepts": DatasetSpec(
        name="concepts",
        filename="concepts.csv",
        prefix="CP",
        min_target=120,
        max_target=160,
        label_col="term",
        list_cols=("related_ids", "prerequisite_ids", "source_ids"),
        ref_cols={
            "related_ids": ENTITY_PREFIXES,
            "prerequisite_ids": ("CP",),
            "source_ids": ("SRC",),
        },
        review_days=365,
    ),
    "agent_types": DatasetSpec(
        name="agent_types",
        filename="agent_types.csv",
        prefix="AT",
        min_target=35,
        max_target=45,
        label_col="name",
        list_cols=("parent_id", "key_concept_ids", "related_pattern_ids", "source_ids"),
        ref_cols={
            "parent_id": ("AT",),
            "key_concept_ids": ("CP",),
            "related_pattern_ids": ("PT",),
            "source_ids": ("SRC",),
        },
        review_days=180,
    ),
    "patterns": DatasetSpec(
        name="patterns",
        filename="patterns.csv",
        prefix="PT",
        min_target=30,
        max_target=None,
        label_col="name",
        list_cols=("related_concept_ids", "related_type_ids", "source_ids"),
        ref_cols={
            "related_concept_ids": ("CP",),
            "related_type_ids": ("AT",),
            "source_ids": ("SRC",),
        },
        review_days=180,
    ),
    "protocols_standards": DatasetSpec(
        name="protocols_standards",
        filename="protocols_standards.csv",
        prefix="PS",
        min_target=12,
        max_target=None,
        label_col="name",
        list_cols=("related_concept_ids", "source_ids"),
        ref_cols={
            "related_concept_ids": ("CP",),
            "source_ids": ("SRC",),
        },
        review_days=90,
    ),
    "frameworks_tools": DatasetSpec(
        name="frameworks_tools",
        filename="frameworks_tools.csv",
        prefix="FW",
        min_target=50,
        max_target=None,
        label_col="name",
        list_cols=("supported_protocol_ids", "related_concept_ids", "source_ids"),
        ref_cols={
            "supported_protocol_ids": ("PS",),
            "related_concept_ids": ("CP",),
            "source_ids": ("SRC",),
        },
        review_days=90,
    ),
    "use_cases": DatasetSpec(
        name="use_cases",
        filename="use_cases.csv",
        prefix="UC",
        min_target=70,
        max_target=None,
        label_col="use_case",
        list_cols=("agent_type_ids", "pattern_ids", "concept_ids", "risk_ids", "source_ids"),
        ref_cols={
            "agent_type_ids": ("AT",),
            "pattern_ids": ("PT",),
            "concept_ids": ("CP",),
            "risk_ids": ("RS",),
            "source_ids": ("SRC",),
        },
        review_days=180,
    ),
    "risks_security": DatasetSpec(
        name="risks_security",
        filename="risks_security.csv",
        prefix="RS",
        min_target=40,
        max_target=None,
        label_col="risk",
        list_cols=("related_concept_ids", "source_ids"),
        ref_cols={
            "related_concept_ids": ("CP",),
            "source_ids": ("SRC",),
        },
        review_days=180,
    ),
    "evaluation": DatasetSpec(
        name="evaluation",
        filename="evaluation.csv",
        prefix="EV",
        min_target=30,
        max_target=None,
        label_col="name",
        list_cols=("applies_to_type_ids", "related_concept_ids", "source_ids"),
        ref_cols={
            "applies_to_type_ids": ("AT",),
            "related_concept_ids": ("CP",),
            "source_ids": ("SRC",),
        },
        review_days=365,
    ),
    "learning_paths": DatasetSpec(
        name="learning_paths",
        filename="learning_paths.csv",
        prefix="LP",
        min_target=100,
        max_target=None,
        label_col="title",
        list_cols=("prerequisite_ids", "concept_ids", "resource_ids", "source_ids"),
        ref_cols={
            "prerequisite_ids": ("LP",),
            "concept_ids": ("CP",),
            "resource_ids": ("RES",),
            "source_ids": ("SRC",),
        },
        review_days=365,
    ),
    "resources": DatasetSpec(
        name="resources",
        filename="resources.csv",
        prefix="RES",
        min_target=150,
        max_target=None,
        label_col="title",
        list_cols=("topics", "concept_ids", "source_ids"),
        ref_cols={
            "concept_ids": ("CP",),
            "source_ids": ("SRC",),
        },
        review_days=365,
    ),
    "relationships": DatasetSpec(
        name="relationships",
        filename="relationships.csv",
        prefix="RL",
        min_target=600,
        max_target=None,
        label_col="note",
        list_cols=("source_ids",),
        ref_cols={
            "from_id": ENTITY_PREFIXES,
            "to_id": ENTITY_PREFIXES,
            "source_ids": ("SRC",),
        },
        review_days=None,
    ),
    "glossary_aliases": DatasetSpec(
        name="glossary_aliases",
        filename="glossary_aliases.csv",
        prefix=None,
        min_target=1,
        max_target=None,
        label_col="alias",
        list_cols=(),
        ref_cols={
            "canonical_id": ENTITY_PREFIXES + ("SRC",),
        },
        review_days=None,
    ),
}


def configure_stdio() -> None:
    """Ensure UTF-8 stdout/stderr on Windows terminals."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def split_pipe(value: str) -> list[str]:
    """Split a pipe-delimited string into stripped non-empty items."""
    if not value:
        return []
    return [part.strip() for part in value.split("|") if part.strip()]


def id_prefix(row_id: str) -> str:
    """Extract the uppercase alphabetic prefix from an ID like CP-001 or SRC-0001."""
    if "-" not in row_id:
        return ""
    return row_id.split("-", 1)[0]


def load_schema(dataset_name: str) -> dict[str, Any]:
    """Load the JSON Schema object for a dataset."""
    path = SCHEMA_DIR / f"{dataset_name}.schema.json"
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def read_csv_rows(dataset_name: str) -> tuple[list[str], list[dict[str, str]]]:
    """Read header and dict rows from a CSV dataset if it exists."""
    spec = DATASETS[dataset_name]
    path = DATA_DIR / spec.filename
    if not path.exists():
        return [], []
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        header = list(reader.fieldnames or [])
        rows = [dict(row) for row in reader]
    return header, rows


def read_all_present() -> dict[str, list[dict[str, str]]]:
    """Load all existing CSV datasets keyed by dataset name."""
    out: dict[str, list[dict[str, str]]] = {}
    for name in DATASET_ORDER:
        _, rows = read_csv_rows(name)
        if rows:
            out[name] = rows
    return out


def write_csv_rows(
    path: pathlib.Path,
    fieldnames: list[str],
    rows: list[dict[str, Any]],
) -> None:
    """Write rows in UTF-8 without BOM using LF line endings."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_text_lf(path: pathlib.Path, content: str) -> None:
    """Write text normalized to LF line endings in UTF-8 without BOM."""
    path.parent.mkdir(parents=True, exist_ok=True)
    clean = content.replace("\r\n", "\n").replace("\r", "\n")
    path.write_text(clean, encoding="utf-8", newline="\n")


def parse_iso_date(value: str) -> _dt.date | None:
    """Parse strict YYYY-MM-DD date string."""
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value or ""):
        return None
    try:
        return _dt.date.fromisoformat(value)
    except ValueError:
        return None
