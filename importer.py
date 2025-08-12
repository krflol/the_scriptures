
import os
import re

RAW_TEXT_DIR = 'raw_text'
TANAK_OUTPUT_DIR = os.path.join('The Scriptures', 'The Tanak')
NEW_TESTAMENT_OUTPUT_DIR = os.path.join('The Scriptures', 'New Testament')

TANAK_BOOK_MAP = {
    "Gen": "Bereshith (Genesis)    בְּרֵאשִׁית",
    "Exod": "Shemoth (Exodus)",
    "Lev": "Wayiqra (Leviticus)",
    "Num": "Bemiḏbar (Numbers)",
    "Deut": "Deḇarim (Deuteronomy)",
    "Josh": "Yehoshua (Joshua)",
    "Judg": "Shophetim (Judges)",
    "Ruth": "Ruth (Ruth)",
    "1Sam": "Shemu’ĕl 1 (1 Samuel)",
    "2Sam": "Shemu’ĕl 2 (2 Samuel)",
    "1Kgs": "Melaḵim 1 (1 Kings)",
    "2Kgs": "Melaḵim 2 (2 Kings)",
    "1Chr": "Diḇrĕ haYamim 1 (1 Chronicles)",
    "2Chr": "Diḇrĕ haYamim 2 (2 Chronicles)",
    "Ezra": "Ezra (Ezra)",
    "Neh": "Neḥemyah (Nehemiah)",
    "Esth": "Estĕr (Esther)",
    "Job": "Iyoḇ (Job)",
    "Ps": "Tehillim (Psalms)",
    "Prov": "Mishlĕ (Proverbs)",
    "Eccl": "Qoheleth (Ecclesiastes)",
    "Song": "Shir haShirim (Song of Songs)",
    "Isa": "Yeshayahu (Isaiah)",
    "Jer": "Yirmeyahu (Jeremiah)",
    "Lam": "Ĕyḵah (Lamentations)",
    "Ezek": "Yeḥezqĕl (Ezekiel)",
    "Dan": "Dani’ĕl (Daniel)",
    "Hos": "Hoshĕa (Hosea)",
    "Joel": "Yo’ĕl (Joel)",
    "Amos": "Amos (Amos)",
    "Obad": "Oḇaḏyah (Obadiah)",
    "Jonah": "Yonah (Jonah)",
    "Mic": "Miḵah (Micah)",
    "Nah": "Naḥum (Nahum)",
    "Hab": "Ḥaḇaqquq (Habakkuk)",
    "Zeph": "Tsephanyah (Zephaniah)",
    "Hag": "Ḥaggai (Haggai)",
    "Zech": "Zeḵaryah (Zechariah)",
    "Mal": "Mal’aḵi (Malachi)",
}

NEW_TESTAMENT_BOOK_MAP = {
    "Matt": "Mattithyahu (Matthew)",
    "Mark": "Marqos (Mark)",
    "Luke": "Luqas (Luke)",
    "John": "Yoḥanan (John)",
    "Acts": "Ma`aseh (Acts)",
    "Rom": "Romiyim (Romans)",
    "1Cor": "Qorintiyim 1 (1 Corinthians)",
    "2Cor": "Qorintiyim 2 (2 Corinthians)",
    "Gal": "Galatiyim (Galatians)",
    "Eph": "Ephsiyim (Ephesians)",
    "Phil": "Pilipiyim (Philippians)",
    "Col": "Qolasim (Colossians)",
    "1Thess": "Tas'loniqim 1 (1 Thessalonians)",
    "2Thess": "Tas'loniqim 2 (2 Thessalonians)",
    "1Tim": "Timotiyos 1 (1 Timothy)",
    "2Tim": "Timotiyos 2 (2 Timothy)",
    "Titus": "Titos (Titus)",
    "Philem": "Pilemon (Philemon)",
    "Heb": "Iḇ'rim (Hebrews)",
    "James": "Ya`aqoḇ (James)",
    "1Pet": "Kĕpha 1 (1 Peter)",
    "2Pet": "Kĕpha 2 (2 Peter)",
    "1John": "Yoḥanan 1 (1 John)",
    "2John": "Yoḥanan 2 (2 John)",
    "3John": "Yoḥanan 3 (3 John)",
    "Jude": "Yehuḏah (Jude)",
    "Rev": "Ḥazon (Revelation)"
}

def parse_and_import():
    """
    Parses the raw text files and creates the Obsidian vault structure.
    """
    if not os.path.exists(TANAK_OUTPUT_DIR):
        os.makedirs(TANAK_OUTPUT_DIR)
    if not os.path.exists(NEW_TESTAMENT_OUTPUT_DIR):
        os.makedirs(NEW_TESTAMENT_OUTPUT_DIR)

    print(f"Starting import...")

    tanak_keys = '|'.join(TANAK_BOOK_MAP.keys())
    tanak_verse_pattern = re.compile(r'^(?P<book>' + tanak_keys + r')\s(?P<chapter>\d+):(?P<verse>\d+)\s(?P<text>.*)')

    nt_keys = '|'.join(NEW_TESTAMENT_BOOK_MAP.keys())
    nt_verse_pattern = re.compile(r'^(?P<book>' + nt_keys + r')\s(?P<chapter>\d+):(?P<verse>\d+)\s(?P<text>.*)')

    start_processing = False
    for filename in sorted(os.listdir(RAW_TEXT_DIR)):
        if filename == 'TS1998 HTML on 4 December 2011 Ver1.13_split_003.htm.txt':
            start_processing = True

        if start_processing and filename.startswith('TS1998') and filename.endswith('.txt'):
            filepath = os.path.join(RAW_TEXT_DIR, filename)
            print(f"Processing file: {filepath}")
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    # print(f"Processing line: {line}")
                    tanak_match = tanak_verse_pattern.match(line)
                    nt_match = nt_verse_pattern.match(line)

                    if tanak_match:
                        # print(f"Tanak match found: {line}")
                        book_abbr = tanak_match.group("book")
                        current_book = TANAK_BOOK_MAP[book_abbr]
                        output_dir = TANAK_OUTPUT_DIR
                        chapter = tanak_match.group("chapter")
                        verse = tanak_match.group("verse")
                        text = tanak_match.group("text").strip()
                    elif nt_match:
                        # print(f"New Testament match found: {line}")
                        book_abbr = nt_match.group("book")
                        current_book = NEW_TESTAMENT_BOOK_MAP[book_abbr]
                        output_dir = NEW_TESTAMENT_OUTPUT_DIR
                        chapter = nt_match.group("chapter")
                        verse = nt_match.group("verse")
                        text = nt_match.group("text").strip()
                    else:
                        # print(f"No match for line: {line}")
                        continue

                    # Create book directory if it doesn't exist
                    book_dir = os.path.join(output_dir, current_book)
                    if not os.path.exists(book_dir):
                        print(f"Creating directory: {book_dir}")
                        os.makedirs(book_dir)

                    # Write to chapter file
                    chapter_file = os.path.join(book_dir, f"{chapter}.md")
                    with open(chapter_file, 'a', encoding='utf-8') as cf:
                        cf.write(f"<sup>{verse}</sup> {text}\n")

if __name__ == '__main__':
    parse_and_import()
