import os
import re
import csv
from bs4 import BeautifulSoup

# --- Configuration ---
RAW_TEXT_DIR = 'raw_text'
BASE_OUTPUT_DIR = 'The Scriptures'
USE_DETECTION_CSV = False  # CSV is for diagnostics only; not source of truth by default

# --- Define Output Directories ---
TANAK_DIR = os.path.join(BASE_OUTPUT_DIR, "The Tanak")
TORAH_DIR = os.path.join(TANAK_DIR, "The Torah")
PROPHETS_DIR = os.path.join(TANAK_DIR, "Prophets")
KETHUBIM_DIR = os.path.join(TANAK_DIR, "First Writings (Kethubim)")
NEW_TESTAMENT_DIR = os.path.join(BASE_OUTPUT_DIR, "New Testament")

# --- Book Categorization ---
# The tuple for each book is: (Abbreviation, Full Name, Output Directory)
ORDERED_BOOKS = [
    # The Torah
    ("Gen", "Bereshith (Genesis)", TORAH_DIR),
    ("Exod", "Shemoth (Exodus)", TORAH_DIR),
    ("Lev", "Wayiqra (Leviticus)", TORAH_DIR),
    ("Num", "Bemiḏbar (Numbers)", TORAH_DIR),
    ("Deut", "Deḇarim (Deuteronomy)", TORAH_DIR),

    # Prophets
    ("Josh", "Yehoshua (Joshua)", PROPHETS_DIR),
    ("Judg", "Shophetim (Judges)", PROPHETS_DIR),
    # If your source uses alternative labels for books, use BOOK_ALIASES below to map them.
    ("1Sam", "Shemu’ĕl 1 (1 Samuel)", PROPHETS_DIR),
    ("2Sam", "Shemu’ĕl 2 (2 Samuel)", PROPHETS_DIR),
    ("1Kgs", "Melaḵim 1 (1 Kings)", PROPHETS_DIR),
    ("2Kgs", "Melaḵim 2 (2 Kings)", PROPHETS_DIR),
    ("Isa", "Yeshayahu (Isaiah)", PROPHETS_DIR),
    ("Jer", "Yirmeyahu (Jeremiah)", PROPHETS_DIR),
    ("Ezek", "Yeḥezqĕl (Ezekiel)", PROPHETS_DIR),
    ("Dan", "Dani’ĕl (Daniel)", PROPHETS_DIR),
    ("Hos", "Hoshĕa (Hosea)", PROPHETS_DIR),
    ("Joel", "Yo’ĕl (Joel)", PROPHETS_DIR),
    ("Amos", "Amos (Amos)", PROPHETS_DIR),
    ("Obad", "Oḇaḏyah (Obadiah)", PROPHETS_DIR),
    ("Jonah", "Yonah (Jonah)", PROPHETS_DIR),
    ("Mic", "Miḵah (Micah)", PROPHETS_DIR),
    ("Nah", "Naḥum (Nahum)", PROPHETS_DIR),
    ("Hab", "Ḥaḇaqquq (Habakkuk)", PROPHETS_DIR),
    ("Zeph", "Tsephanyah (Zephaniah)", PROPHETS_DIR),
    ("Hag", "Ḥaggai (Haggai)", PROPHETS_DIR),
    ("Zech", "Zeḵaryah (Zechariah)", PROPHETS_DIR),
    ("Mal", "Mal’aḵi (Malachi)", PROPHETS_DIR),
    
    # Kethubim (First Writings)
    ("Ps", "Tehillim (Psalms)", KETHUBIM_DIR),
    ("Prov", "Mishlĕ (Proverbs)", KETHUBIM_DIR),
    ("Job", "Iyoḇ (Job)", KETHUBIM_DIR),
    ("Song", "Shir haShirim (Song of Songs)", KETHUBIM_DIR),
    ("Ruth", "Ruth (Ruth)", KETHUBIM_DIR),
    ("Lam", "Ĕyḵah (Lamentations)", KETHUBIM_DIR),
    ("Eccl", "Qoheleth (Ecclesiastes)", KETHUBIM_DIR),
    ("Esth", "Estĕr (Esther)", KETHUBIM_DIR),
    ("Ezra", "Ezra (Ezra)", KETHUBIM_DIR),
    ("Neh", "Neḥemyah (Nehemiah)", KETHUBIM_DIR),
    ("1Chr", "Diḇrĕ haYamim 1 (1 Chronicles)", KETHUBIM_DIR),
    ("2Chr", "Diḇrĕ haYamim 2 (2 Chronicles)", KETHUBIM_DIR),

    # New Testament
    ("Matt", "Mattithyahu (Matthew)", NEW_TESTAMENT_DIR),
    ("Mark", "Marqos (Mark)", NEW_TESTAMENT_DIR),
    ("Luke", "Luqas (Luke)", NEW_TESTAMENT_DIR),
    ("John", "Yoḥanan (John)", NEW_TESTAMENT_DIR),
    ("Acts", "Ma`aseh (Acts)", NEW_TESTAMENT_DIR),
    ("Rom", "Romiyim (Romans)", NEW_TESTAMENT_DIR),
    ("1Cor", "Qorintiyim 1 (1 Corinthians)", NEW_TESTAMENT_DIR),
    ("2Cor", "Qorintiyim 2 (2 Corinthians)", NEW_TESTAMENT_DIR),
    ("Gal", "Galatiyim (Galatians)", NEW_TESTAMENT_DIR),
    ("Eph", "Ephsiyim (Ephesians)", NEW_TESTAMENT_DIR),
    ("Phil", "Pilipiyim (Philippians)", NEW_TESTAMENT_DIR),
    ("Col", "Qolasim (Colossians)", NEW_TESTAMENT_DIR),
    ("1Thess", "Tas'loniqim 1 (1 Thessalonians)", NEW_TESTAMENT_DIR),
    ("2Thess", "Tas'loniqim 2 (2 Thessalonians)", NEW_TESTAMENT_DIR),
    ("1Tim", "Timotiyos 1 (1 Timothy)", NEW_TESTAMENT_DIR),
    ("2Tim", "Timotiyos 2 (2 Timothy)", NEW_TESTAMENT_DIR),
    ("Titus", "Titos (Titus)", NEW_TESTAMENT_DIR),
    ("Philem", "Pilemon (Philemon)", NEW_TESTAMENT_DIR),
    ("Heb", "Iḇ'rim (Hebrews)", NEW_TESTAMENT_DIR),
    ("James", "Ya`aqoḇ (James)", NEW_TESTAMENT_DIR),
    ("1Pet", "Kĕpha 1 (1 Peter)", NEW_TESTAMENT_DIR),
    ("2Pet", "Kĕpha 2 (2 Peter)", NEW_TESTAMENT_DIR),
    ("1John", "Yoḥanan 1 (1 John)", NEW_TESTAMENT_DIR),
    ("2John", "Yoḥanan 2 (2 John)", NEW_TESTAMENT_DIR),
    ("3John", "Yoḥanan 3 (3 John)", NEW_TESTAMENT_DIR),
    ("Jude", "Yehuḏah (Jude)", NEW_TESTAMENT_DIR),
    ("Rev", "Ḥazon (Revelation)", NEW_TESTAMENT_DIR)
]

# Create a mapping from book abbreviation to its full name, directory, and order index
BOOK_MAP = {abbr: (name, out_dir, i) for i, (abbr, name, out_dir) in enumerate(ORDERED_BOOKS)}

# Aliases that may appear in source text mapped to canonical abbreviations in ORDERED_BOOKS
BOOK_ALIASES = {
    # Judges
    "Rulers": "Judg",
    "Judges": "Judg",
    "Judges/Rulers": "Judg",
    "Shophetim": "Judg",
    "Sophetim": "Judg",
    # Psalms
    "Psalms": "Ps",
    "Psalm": "Ps",
    "Psa": "Ps",
    "Psm": "Ps",
    # Gospels common short forms
    "Mat": "Matt",
    "Mt": "Matt",
    "Mar": "Mark",
    "Mk": "Mark",
    "Luk": "Luke",
    "Lk": "Luke",
    "Joh": "John",
    "Jn": "John",
    # Kings/Chronicles full names
    "1Kings": "1Kgs",
    "2Kings": "2Kgs",
    "1Chronicles": "1Chr",
    "2Chronicles": "2Chr",
    # Corinthians/Thessalonians short forms
    "1Thes": "1Thess",
    "2Thes": "2Thess",
    # Philemon
    "Phlm": "Philem",
    # James
    "Jas": "James",
    # Hebrews
    "Iḇ'rim/Hebrews": "Heb",
    "Hebrew": "Heb",
}

# Build the list of keys to split on: canonical abbreviations plus alias labels
DERIVED_NAME_TO_ABBR = {}
derived_alias_keys = set()
for abbr, (full_name, _out_dir, _idx) in BOOK_MAP.items():
    if " (" in full_name and full_name.endswith(")"):
        heb_name = full_name.split(" (", 1)[0]
        com_name = full_name[full_name.find("(") + 1:-1]
    else:
        heb_name = full_name
        com_name = full_name
    DERIVED_NAME_TO_ABBR[heb_name] = abbr
    DERIVED_NAME_TO_ABBR[com_name] = abbr
    derived_alias_keys.add(heb_name)
    derived_alias_keys.add(com_name)

all_book_keys = sorted(list({*BOOK_MAP.keys(), *BOOK_ALIASES.keys(), *derived_alias_keys}), key=len, reverse=True)
escaped_keys = [re.escape(key) for key in all_book_keys]
split_pattern = r'(\s*(?:' + '|'.join(escaped_keys) + r')\s*\d+:\d+\s*)'
# Allow book tokens to include a '/'
ref_pattern = re.compile(r'([a-zA-Z0-9/]+)\s*(\d+):(\d+)')

def parse_and_import():
    """
    Parses the raw text files and creates the structured Obsidian vault.
    """
    # Create all necessary directories
    for book_abbr, book_info in BOOK_MAP.items():
        os.makedirs(book_info[1], exist_ok=True)
    
    print("Starting import...")
    detection_csv = 'book_detection.csv'
    if USE_DETECTION_CSV and os.path.exists(detection_csv):
        mapping = []
        with open(detection_csv, 'r', encoding='utf-8') as m:
            reader = csv.DictReader(m)
            for row in reader:
                abbr = (row.get('detected_abbr') or '').strip()
                fname = (row.get('filename') or '').strip()
                if abbr and fname:
                    mapping.append((fname, abbr))

        # Sort by canonical book order, then filename
        mapping.sort(key=lambda t: (BOOK_MAP.get(t[1], (None, None, 999))[2], t[0]))

        for filename, mapped_abbr in mapping:
            filepath = os.path.join(RAW_TEXT_DIR, filename)
            if not os.path.exists(filepath):
                continue
            print(f"Processing (detected) file: {filepath} -> {mapped_abbr}")
            with open(filepath, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'lxml')
                text = soup.get_text()
                text = ' '.join(text.splitlines())

                # Build file-specific split pattern using the mapped abbr and its aliases
                file_keys = [mapped_abbr] + [alias for alias, a in BOOK_ALIASES.items() if a == mapped_abbr]
                file_split_pattern = r'(\s*(?:' + '|'.join(re.escape(k) for k in file_keys) + r')\s*\d+:\d+\s*)'
                parts = re.split(file_split_pattern, text)
                # Fallback to global pattern if file-specific split finds too few parts
                if len(parts) < 3:
                    parts = re.split(split_pattern, text)

                for i in range(1, len(parts), 2):
                    ref_text = parts[i].strip()
                    if (i + 1) >= len(parts):
                        continue
                    verse_text = parts[i+1].strip()

                    ref_match = ref_pattern.search(ref_text)
                    if not ref_match:
                        continue

                    # Use the mapped canonical abbreviation for this file
                    book_abbr = mapped_abbr
                    chapter = ref_match.group(2)
                    verse = ref_match.group(3)

                    if book_abbr in BOOK_MAP:
                        book_name, output_dir, book_index = BOOK_MAP[book_abbr]
                        book_dir_name = f"{book_index + 1:02d} - {book_name}"
                        book_dir = os.path.join(output_dir, book_dir_name)

                        if " (" in book_name and book_name.endswith(")"):
                            hebrew_name = book_name.split(" (", 1)[0]
                            common_name = book_name[book_name.find("(") + 1:-1]
                        else:
                            hebrew_name = book_name
                            common_name = book_name
                    else:
                        continue

                    os.makedirs(book_dir, exist_ok=True)

                    chapter_filename = f"{common_name}_{hebrew_name}_{chapter}.md"
                    chapter_file = os.path.join(book_dir, chapter_filename)
                    with open(chapter_file, 'a', encoding='utf-8') as cf:
                        cf.write(f"<sup>{verse}</sup> {verse_text}\n\n")
    else:
        # Process files from the raw_text directory (original behavior)
        for filename in sorted(os.listdir(RAW_TEXT_DIR)):
            if filename.startswith('TS1998') and filename.endswith('.txt'):
                filepath = os.path.join(RAW_TEXT_DIR, filename)
                print(f"Processing file: {filepath}")
                with open(filepath, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f, 'lxml')
                    text = soup.get_text()
                    text = ' '.join(text.splitlines())

                    parts = re.split(split_pattern, text)
                    
                    for i in range(1, len(parts), 2):
                        ref_text = parts[i].strip()
                        if (i + 1) >= len(parts):
                            continue
                        verse_text = parts[i+1].strip()

                        ref_match = ref_pattern.search(ref_text)
                        if not ref_match:
                            continue

                        token = ref_match.group(1)
                        book_abbr = BOOK_ALIASES.get(token, DERIVED_NAME_TO_ABBR.get(token, token))
                        chapter = ref_match.group(2)
                        verse = ref_match.group(3)

                        if book_abbr in BOOK_MAP:
                            book_name, output_dir, book_index = BOOK_MAP[book_abbr]
                            book_dir_name = f"{book_index + 1:02d} - {book_name}"
                            book_dir = os.path.join(output_dir, book_dir_name)

                            if " (" in book_name and book_name.endswith(")"):
                                hebrew_name = book_name.split(" (", 1)[0]
                                common_name = book_name[book_name.find("(") + 1:-1]
                            else:
                                hebrew_name = book_name
                                common_name = book_name
                        else:
                            continue

                        os.makedirs(book_dir, exist_ok=True)

                        chapter_filename = f"{common_name}_{hebrew_name}_{chapter}.md"
                        chapter_file = os.path.join(book_dir, chapter_filename)
                        with open(chapter_file, 'a', encoding='utf-8') as cf:
                            cf.write(f"<sup>{verse}</sup> {verse_text}\n\n")

if __name__ == '__main__':
    parse_and_import()