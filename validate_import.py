import os
import re
import glob
from typing import Dict, Tuple, List
from bs4 import BeautifulSoup
from importer import RAW_TEXT_DIR, ORDERED_BOOKS, BOOK_ALIASES, BOOK_MAP, TANAK_DIR, NEW_TESTAMENT_DIR

REF_RE = re.compile(r'(\b[\w/]+)\s*(\d+):(\d+)')


def scan_raw_for_book_chapter(book_keys: List[str]) -> Dict[Tuple[int, int], int]:
    """Return {(chapter, verse): count} seen for provided book tokens across raw files."""
    counts: Dict[Tuple[int, int], int] = {}
    pattern = re.compile(r'(?:' + '|'.join(re.escape(k) for k in book_keys) + r')\s*(\d+):(\d+)')

    for path in glob.glob(os.path.join(RAW_TEXT_DIR, '*.txt')):
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            text = BeautifulSoup(f, 'lxml').get_text()
        for m in pattern.finditer(text):
            ch = int(m.group(1))
            vs = int(m.group(2))
            counts[(ch, vs)] = counts.get((ch, vs), 0) + 1
    return counts


def expected_book_keys(abbr: str) -> List[str]:
    keys = [abbr]
    for alias, a in BOOK_ALIASES.items():
        if a == abbr:
            keys.append(alias)
    # Add derived Hebrew/Common names
    full_name, _out, _idx = BOOK_MAP[abbr]
    if ' (' in full_name and full_name.endswith(')'):
        heb = full_name.split(' (', 1)[0]
        com = full_name[full_name.find('(')+1:-1]
        keys.extend([heb, com])
    else:
        keys.append(full_name)
    return keys


def find_output_dir_for_book(abbr: str) -> str:
    full_name, out_dir, idx = BOOK_MAP[abbr]
    book_dir_name = f"{idx + 1:02d} - {full_name}"
    return os.path.join(out_dir, book_dir_name)


def check_book(abbr: str, chapter_to_check: int = None) -> List[str]:
    issues: List[str] = []
    keys = expected_book_keys(abbr)
    raw_counts = scan_raw_for_book_chapter(keys)

    out_dir = find_output_dir_for_book(abbr)
    if not os.path.isdir(out_dir):
        issues.append(f"OUTPUT DIR MISSING: {out_dir}")
        return issues

    # Detect chapters present in output
    chapter_files = [f for f in os.listdir(out_dir) if f.endswith('.md')]
    present_chapters: Dict[int, str] = {}
    for fn in chapter_files:
        m = re.search(r'_(\d+)\.md$', fn)
        if m:
            present_chapters[int(m.group(1))] = fn

    if chapter_to_check is not None:
        if (chapter_to_check, 1) not in raw_counts:
            issues.append(f"RAW MISSING CHAPTER {abbr} {chapter_to_check}")
        if chapter_to_check not in present_chapters:
            issues.append(f"OUTPUT MISSING CHAPTER {abbr} {chapter_to_check}")
    else:
        # Basic sanity: at least one verse in raw must exist
        if not raw_counts:
            issues.append(f"RAW NO MATCHES for {abbr}")
        if not present_chapters:
            issues.append(f"OUTPUT NO CHAPTERS for {abbr}")

    return issues


def main() -> None:
    problems: List[str] = []

    # Focus on Genesis 6 explicitly
    problems.extend(check_book('Gen', chapter_to_check=6))

    # Quick scan of a few more
    for abbr in ['Exod', 'Ps', 'Matt']:
        problems.extend(check_book(abbr))

    if problems:
        print("Validation issues:")
        for p in problems:
            print("- ", p)
    else:
        print("Validation passed: key chapters and outputs found.")


if __name__ == '__main__':
    main() 