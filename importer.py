
import os
import re
from bs4 import BeautifulSoup

RAW_TEXT_DIR = 'raw_text'
TANAK_OUTPUT_DIR = os.path.join('The Scriptures', 'The Tanak')
NEW_TESTAMENT_OUTPUT_DIR = os.path.join('The Scriptures', 'New Testament')

# Ordered list of books to ensure correct sorting
ORDERED_BOOKS = [
    ("Gen", "Bereshith (Genesis)    בְּרֵאשִׁית", TANAK_OUTPUT_DIR),
    ("Exod", "Shemoth (Exodus)", TANAK_OUTPUT_DIR),
    ("Lev", "Wayiqra (Leviticus)", TANAK_OUTPUT_DIR),
    ("Num", "Bemiḏbar (Numbers)", TANAK_OUTPUT_DIR),
    ("Deut", "Deḇarim (Deuteronomy)", TANAK_OUTPUT_DIR),
    ("Josh", "Yehoshua (Joshua)", TANAK_OUTPUT_DIR),
    ("Judg", "Shophetim (Judges)", TANAK_OUTPUT_DIR),
    ("Ruth", "Ruth (Ruth)", TANAK_OUTPUT_DIR),
    ("1Sam", "Shemu’ĕl 1 (1 Samuel)", TANAK_OUTPUT_DIR),
    ("2Sam", "Shemu’ĕl 2 (2 Samuel)", TANAK_OUTPUT_DIR),
    ("1Kgs", "Melaḵim 1 (1 Kings)", TANAK_OUTPUT_DIR),
    ("2Kgs", "Melaḵim 2 (2 Kings)", TANAK_OUTPUT_DIR),
    ("1Chr", "Diḇrĕ haYamim 1 (1 Chronicles)", TANAK_OUTPUT_DIR),
    ("2Chr", "Diḇrĕ haYamim 2 (2 Chronicles)", TANAK_OUTPUT_DIR),
    ("Ezra", "Ezra (Ezra)", TANAK_OUTPUT_DIR),
    ("Neh", "Neḥemyah (Nehemiah)", TANAK_OUTPUT_DIR),
    ("Esth", "Estĕr (Esther)", TANAK_OUTPUT_DIR),
    ("Job", "Iyoḇ (Job)", TANAK_OUTPUT_DIR),
    ("Ps", "Tehillim (Psalms)", TANAK_OUTPUT_DIR),
    ("Prov", "Mishlĕ (Proverbs)", TANAK_OUTPUT_DIR),
    ("Eccl", "Qoheleth (Ecclesiastes)", TANAK_OUTPUT_DIR),
    ("Song", "Shir haShirim (Song of Songs)", TANAK_OUTPUT_DIR),
    ("Isa", "Yeshayahu (Isaiah)", TANAK_OUTPUT_DIR),
    ("Jer", "Yirmeyahu (Jeremiah)", TANAK_OUTPUT_DIR),
    ("Lam", "Ĕyḵah (Lamentations)", TANAK_OUTPUT_DIR),
    ("Ezek", "Yeḥezqĕl (Ezekiel)", TANAK_OUTPUT_DIR),
    ("Dan", "Dani’ĕl (Daniel)", TANAK_OUTPUT_DIR),
    ("Hos", "Hoshĕa (Hosea)", TANAK_OUTPUT_DIR),
    ("Joel", "Yo’ĕl (Joel)", TANAK_OUTPUT_DIR),
    ("Amos", "Amos (Amos)", TANAK_OUTPUT_DIR),
    ("Obad", "Oḇaḏyah (Obadiah)", TANAK_OUTPUT_DIR),
    ("Jonah", "Yonah (Jonah)", TANAK_OUTPUT_DIR),
    ("Mic", "Miḵah (Micah)", TANAK_OUTPUT_DIR),
    ("Nah", "Naḥum (Nahum)", TANAK_OUTPUT_DIR),
    ("Hab", "Ḥaḇaqquq (Habakkuk)", TANAK_OUTPUT_DIR),
    ("Zeph", "Tsephanyah (Zephaniah)", TANAK_OUTPUT_DIR),
    ("Hag", "Ḥaggai (Haggai)", TANAK_OUTPUT_DIR),
    ("Zech", "Zeḵaryah (Zechariah)", TANAK_OUTPUT_DIR),
    ("Mal", "Mal’aḵi (Malachi)", TANAK_OUTPUT_DIR),
    ("Matt", "Mattithyahu (Matthew)", NEW_TESTAMENT_OUTPUT_DIR),
    ("Mark", "Marqos (Mark)", NEW_TESTAMENT_OUTPUT_DIR),
    ("Luke", "Luqas (Luke)", NEW_TESTAMENT_OUTPUT_DIR),
    ("John", "Yoḥanan (John)", NEW_TESTAMENT_OUTPUT_DIR),
    ("Acts", "Ma`aseh (Acts)", NEW_TESTAMENT_OUTPUT_DIR),
    ("Rom", "Romiyim (Romans)", NEW_TESTAMENT_OUTPUT_DIR),
    ("1Cor", "Qorintiyim 1 (1 Corinthians)", NEW_TESTAMENT_OUTPUT_DIR),
    ("2Cor", "Qorintiyim 2 (2 Corinthians)", NEW_TESTAMENT_OUTPUT_DIR),
    ("Gal", "Galatiyim (Galatians)", NEW_TESTAMENT_OUTPUT_DIR),
    ("Eph", "Ephsiyim (Ephesians)", NEW_TESTAMENT_OUTPUT_DIR),
    ("Phil", "Pilipiyim (Philippians)", NEW_TESTAMENT_OUTPUT_DIR),
    ("Col", "Qolasim (Colossians)", NEW_TESTAMENT_OUTPUT_DIR),
    ("1Thess", "Tas'loniqim 1 (1 Thessalonians)", NEW_TESTAMENT_OUTPUT_DIR),
    ("2Thess", "Tas'loniqim 2 (2 Thessalonians)", NEW_TESTAMENT_OUTPUT_DIR),
    ("1Tim", "Timotiyos 1 (1 Timothy)", NEW_TESTAMENT_OUTPUT_DIR),
    ("2Tim", "Timotiyos 2 (2 Timothy)", NEW_TESTAMENT_OUTPUT_DIR),
    ("Titus", "Titos (Titus)", NEW_TESTAMENT_OUTPUT_DIR),
    ("Philem", "Pilemon (Philemon)", NEW_TESTAMENT_OUTPUT_DIR),
    ("Heb", "Iḇ'rim (Hebrews)", NEW_TESTAMENT_OUTPUT_DIR),
    ("James", "Ya`aqoḇ (James)", NEW_TESTAMENT_OUTPUT_DIR),
    ("1Pet", "Kĕpha 1 (1 Peter)", NEW_TESTAMENT_OUTPUT_DIR),
    ("2Pet", "Kĕpha 2 (2 Peter)", NEW_TESTAMENT_OUTPUT_DIR),
    ("1John", "Yoḥanan 1 (1 John)", NEW_TESTAMENT_OUTPUT_DIR),
    ("2John", "Yoḥanan 2 (2 John)", NEW_TESTAMENT_OUTPUT_DIR),
    ("3John", "Yoḥanan 3 (3 John)", NEW_TESTAMENT_OUTPUT_DIR),
    ("Jude", "Yehuḏah (Jude)", NEW_TESTAMENT_OUTPUT_DIR),
    ("Rev", "Ḥazon (Revelation)", NEW_TESTAMENT_OUTPUT_DIR)
]

BOOK_MAP = {abbr: (name, out_dir, i) for i, (abbr, name, out_dir) in enumerate(ORDERED_BOOKS)}

def parse_and_import():
    """
    Parses the raw text files and creates the Obsidian vault structure.
    """
    if not os.path.exists(TANAK_OUTPUT_DIR):
        os.makedirs(TANAK_OUTPUT_DIR)
    if not os.path.exists(NEW_TESTAMENT_OUTPUT_DIR):
        os.makedirs(NEW_TESTAMENT_OUTPUT_DIR)

    print(f"Starting import...")

    all_book_keys = sorted([book[0] for book in ORDERED_BOOKS], key=len, reverse=True)
    # Pattern to split the text by, but keep the delimiter (the verse ref)
    split_pattern = r'(\s*(?:' + '|'.join(all_book_keys) + r')\s+\d+:\d+\s*)'
    
    # Pattern to parse the verse reference itself
    ref_pattern = re.compile(r'([a-zA-Z0-9]+)\s*(\d+):(\d+)')

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

                    book_abbr = ref_match.group(1)
                    chapter = ref_match.group(2)
                    verse = ref_match.group(3)

                    if book_abbr in BOOK_MAP:
                        book_name, output_dir, book_index = BOOK_MAP[book_abbr]
                        # Format book directory with leading zero for sorting
                        book_dir_name = f"{book_index + 1:02d} - {book_name}"
                        book_dir = os.path.join(output_dir, book_dir_name)
                    else:
                        continue

                    os.makedirs(book_dir, exist_ok=True)

                    # Write to chapter file
                    chapter_file = os.path.join(book_dir, f"{book_abbr}_{chapter}.md")
                    with open(chapter_file, 'a', encoding='utf-8') as cf:
                        cf.write(f"<sup>{verse}</sup> {verse_text}\n")

if __name__ == '__main__':
    parse_and_import()
