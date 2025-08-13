import os
import csv
import glob
import re
from typing import Dict, List, Tuple, Optional

# Reuse configuration and mappings from importer.py
from importer import ORDERED_BOOKS, BOOK_ALIASES, BOOK_MAP, RAW_TEXT_DIR


def build_alias_index() -> Dict[str, str]:
    """Build a case-insensitive alias->abbr map from ORDERED_BOOKS and BOOK_ALIASES."""
    alias_to_abbr: Dict[str, str] = {}

    # Start with provided aliases
    for alias, abbr in BOOK_ALIASES.items():
        alias_to_abbr[alias.lower()] = abbr

    # Add canonical abbreviations and names
    for abbr, (full_name, _out_dir, _idx) in BOOK_MAP.items():
        # abbr itself
        alias_to_abbr.setdefault(abbr.lower(), abbr)
        # Hebrew and common names from "Hebrew (Common)"
        hebrew_name: str
        common_name: str
        if " (" in full_name and full_name.endswith(")"):
            hebrew_name = full_name.split(" (", 1)[0]
            common_name = full_name[full_name.find("(") + 1:-1]
        else:
            hebrew_name = full_name
            common_name = full_name
        alias_to_abbr.setdefault(hebrew_name.lower(), abbr)
        alias_to_abbr.setdefault(common_name.lower(), abbr)

        # Add a few safe variants without diacritics/apostrophes to improve matching
        normalized_variants = set()
        for variant in (hebrew_name, common_name):
            v = variant
            v = v.replace("’", "'")
            v = v.replace("`", "'")
            v = v.replace("ḏ", "d").replace("ḵ", "k").replace("ḥ", "h").replace("ĕ", "e").replace("ḇ", "b").replace("ṣ", "s").replace("ṭ", "t").replace("ś", "s").replace("š", "s").replace("û", "u").replace("ō", "o").replace("á", "a").replace("í", "i").replace("ú", "u").replace("ó", "o").replace("è", "e").replace("é", "e")
            normalized_variants.add(v)
        for v in normalized_variants:
            alias_to_abbr.setdefault(v.lower(), abbr)

    return alias_to_abbr


def read_lines_5_and_6(filepath: str) -> str:
    """Return concatenated lines 5-6 (1-indexed) or as many as available up to that point."""
    lines: List[str] = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f):
                if i > 5:  # zero-indexed, line 6 is i==5
                    break
                lines.append(line.strip())
    except Exception as e:
        return f"<read_error: {e}>"

    # Return lines 5 and 6 if present, else join what we have
    if len(lines) >= 6:
        return f"{lines[4]} {lines[5]}".strip()
    return " ".join(lines).strip()


def detect_book_from_snippet(snippet: str, alias_index: Dict[str, str]) -> Optional[Tuple[str, str]]:
    """Return (abbr, matched_alias) if detected in the snippet, preferring longest alias match."""
    if not snippet:
        return None
    lower_snippet = snippet.lower()

    # Sort aliases by length descending to prefer more specific matches
    candidates = sorted(alias_index.keys(), key=len, reverse=True)

    for alias in candidates:
        if alias and alias in lower_snippet:
            return alias_index[alias], alias

    return None


def main(output_csv: str = "book_detection.csv") -> None:
    alias_index = build_alias_index()

    rows: List[List[str]] = []
    header = [
        "filename",
        "detected_abbr",
        "hebrew_name",
        "common_name",
        "full_name",
        "matched_alias",
        "snippet",
    ]
    rows.append(header)

    pattern = os.path.join(RAW_TEXT_DIR, "*.txt")

    for filepath in sorted(glob.glob(pattern)):
        snippet = read_lines_5_and_6(filepath)
        detection = detect_book_from_snippet(snippet, alias_index)

        detected_abbr = matched_alias = ""
        hebrew_name = common_name = full_name = ""

        if detection is not None:
            detected_abbr, matched_alias = detection
            if detected_abbr in BOOK_MAP:
                full_name, _out_dir, _idx = BOOK_MAP[detected_abbr]
                if " (" in full_name and full_name.endswith(")"):
                    hebrew_name = full_name.split(" (", 1)[0]
                    common_name = full_name[full_name.find("(") + 1:-1]
                else:
                    hebrew_name = full_name
                    common_name = full_name
            else:
                full_name = detected_abbr

        rows.append([
            os.path.basename(filepath),
            detected_abbr,
            hebrew_name,
            common_name,
            full_name,
            matched_alias,
            snippet,
        ])

    with open(output_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    print(f"Wrote detection to {output_csv} ({len(rows)-1} files)")


if __name__ == "__main__":
    main() 