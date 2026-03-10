#!/usr/bin/env python3
"""
Parse a Mondial-style table description TXT into the JSON schema you use for
column-combo generation.

Expected TXT format (blocks separated by "--"):

Mondial_Country: the countries (and similar areas) of the world with some data.
name: the country name
code: the car code
...
--
Mondial_Economy: economical information about the countries.
country: the country code
GDP: gross domestic product (in million $)
...

Notes:
- Lines without ":" are treated as a continuation of the previous column description.
- Adds the Spider-style first column entry: [-1, "*"] with description "*".
- Infers column_types with simple heuristics (text/number/time).
"""

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional


NUMERIC_HINTS = {
    "area", "population", "gdp", "agriculture", "service", "industry",
    "inflation", "unemployment", "percentage", "height", "depth", "length",
    "elevation", "gmtoffset", "offset", "latitude", "longitude",
    "sourceelevation", "estuarelevation", "estuaryelevation",
    "sourcelatitude", "sourcelongitude", "estuarylatitude", "estuarylongitude",
    "mortality", "growth", "year"
}
TIME_HINTS = {"date", "datetime", "time", "established", "independence"}


def normalize_table_name(table_name_original: str) -> str:
    """
    Matches your earlier convention:
      Mondial_Country -> country
      Mondial_borders -> borders
    """
    t = table_name_original.strip()
    if t.lower().startswith("mondial_"):
        t = t[len("Mondial_"):]  # preserve original casing of the rest
    return t.strip().lower()


def infer_col_type(col_name: str, col_desc: str) -> str:
    """
    Conservative heuristics: returns 'text', 'number', or 'time'
    """
    n = (col_name or "").strip().lower()
    d = (col_desc or "").strip().lower()

    # time
    if any(h in n for h in TIME_HINTS) or any(h in d for h in TIME_HINTS):
        return "time"

    # number
    # name-based hints (contains)
    if any(h in n for h in NUMERIC_HINTS):
        return "number"

    # desc-based hints
    if any(k in d for k in ["number", "percent", "percentage", "rate", "total area", "height", "depth", "length", "elevation"]):
        return "number"

    return "text"


def split_blocks(txt: str) -> List[str]:
    """
    Splits by lines containing only '--' (optionally with surrounding whitespace).
    """
    # Normalize newlines and split on separator lines
    lines = txt.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    blocks: List[List[str]] = []
    current: List[str] = []
    for line in lines:
        if line.strip() == "--":
            if current:
                blocks.append(current)
                current = []
        else:
            current.append(line)
    if current:
        blocks.append(current)

    # Convert to block strings, remove empty-leading/trailing lines
    out = []
    for b in blocks:
        bb = "\n".join([ln.rstrip() for ln in b]).strip()
        if bb:
            out.append(bb)
    return out


def parse_block(block: str) -> Tuple[str, str, List[Tuple[str, str]]]:
    """
    Returns (table_name_original, table_overview, [(col_name, col_desc), ...])

    Handles wrapped descriptions: lines without ':' are appended to previous col_desc.
    """
    lines = [ln.strip() for ln in block.split("\n") if ln.strip()]
    if not lines:
        raise ValueError("Empty block encountered")

    # First line: TableName: overview...
    m = re.match(r"^([^:]+)\s*:\s*(.*)$", lines[0])
    if not m:
        raise ValueError(f"Block header not in 'Table: desc' format: {lines[0]}")
    table_name_original = m.group(1).strip()
    table_overview = m.group(2).strip()

    cols: List[Tuple[str, str]] = []
    current_col: Optional[str] = None
    current_desc_parts: List[str] = []

    for ln in lines[1:]:
        if ":" in ln:
            # flush previous
            if current_col is not None:
                cols.append((current_col, " ".join(current_desc_parts).strip()))
            # start new
            c, d = ln.split(":", 1)
            current_col = c.strip()
            current_desc_parts = [d.strip()]
        else:
            # continuation
            if current_col is None:
                # stray line before any column; attach to table overview (rare)
                table_overview = (table_overview + " " + ln).strip()
            else:
                current_desc_parts.append(ln.strip())

    if current_col is not None:
        cols.append((current_col, " ".join(current_desc_parts).strip()))

    return table_name_original, table_overview, cols


def txt_to_dataset_json(
    txt_path: Path,
    db_id: str,
    db_overview: str = "",
    value_enums: str = "",
) -> List[dict]:
    """
    Produces a list with a single db object in your expected schema.
    """
    raw = txt_path.read_text(encoding="utf-8", errors="replace")
    blocks = split_blocks(raw)

    table_names_original: List[str] = []
    table_names: List[str] = []

    # Start with Spider-style '*' pseudo-column
    column_descriptions: List[str] = ["*"]
    column_names: List[List[object]] = [[-1, "*"]]
    column_types: List[str] = ["text"]

    # Parse each table block
    for tidx, block in enumerate(blocks):
        t_orig, _t_overview, cols = parse_block(block)
        table_names_original.append(t_orig)
        table_names.append(normalize_table_name(t_orig))

        for col_name, col_desc in cols:
            column_descriptions.append(col_desc if col_desc else col_name)
            column_names.append([tidx, col_name])
            column_types.append(infer_col_type(col_name, col_desc))

    db_obj = {
        "column_descriptions": column_descriptions,
        "column_names": column_names,
        "column_types": column_types,
        "db_id": db_id,
        "db_overview": db_overview,
        "foreign_keys": [],
        "primary_keys": [],
        "table_names": table_names,
        "table_names_original": table_names_original,
        "value_enums": value_enums,
    }

    return [db_obj]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_txt", required=True, help="Path to input .txt schema description")
    ap.add_argument("--out_json", required=True, help="Path to output .json")
    ap.add_argument("--db_id", required=True, help="Database id (e.g. mondial)")
    ap.add_argument("--db_overview", default="", help="Optional database overview text")
    ap.add_argument("--value_enums", default="", help="Optional value_enums string")
    args = ap.parse_args()

    out = txt_to_dataset_json(
        txt_path=Path(args.in_txt),
        db_id=args.db_id,
        db_overview=args.db_overview,
        value_enums=args.value_enums,
    )

    out_path = Path(args.out_json)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Wrote: {out_path} (tables: {len(out[0]['table_names'])}, columns: {len(out[0]['column_names']) - 1})")


if __name__ == "__main__":
    main()
