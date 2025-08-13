import os
import json
import re
import sys

# Ensure project root is on sys.path so we can import importer.py
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from importer import ORDERED_BOOKS, TORAH_DIR, PROPHETS_DIR, KETHUBIM_DIR, NEW_TESTAMENT_DIR

# --- Configuration ---
SOURCE_DIR = os.path.join(ROOT_DIR, 'The Scriptures')
VIEWER_DIR = os.path.dirname(__file__)
OUTPUT_HTML_FILE = os.path.join(VIEWER_DIR, 'index.html')

# --- Markdown to HTML Conversion ---
def parse_markdown_to_html(text):
    """Converts specific Markdown syntax to HTML."""
    text = re.sub(r'\[\[(?:[^\]|]+\|)?([^\]]+)\]\]', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', text)
    return text

# --- Data Parsing Functions ---
def parse_verse_line(line):
    """Parses a single line of scripture text and its Markdown content."""
    match = re.match(r'^\s*<sup>(\d+)</sup>\s*(.*?)(?:\s*\^([a-zA-Z0-9\-]+))?\s*$ ', line)
    if not match:
        match = re.match(r'^\s*<sup>(\d+)</sup>\s*(.*?)(?:\s*\^([a-zA-Z0-9\-]+))?\s*$', line)
    if not match:
        return None

    verse_num = int(match.group(1))
    raw_text = match.group(2).strip()
    block_id = match.group(3)

    processed_text = parse_markdown_to_html(raw_text)

    return {
        "verse": verse_num,
        "text": processed_text,
        "id": block_id if block_id else f"v{verse_num}"
    }


def parse_chapter_files(book_dir: str) -> dict:
    data = {}
    try:
        for entry in sorted(os.scandir(book_dir), key=lambda e: e.name):
            if entry.is_file() and entry.name.lower().endswith('.md'):
                base = os.path.splitext(entry.name)[0]
                m = re.search(r'_(\d+)$', base)
                chapter_key = m.group(1) if m else base
                with open(entry.path, 'r', encoding='utf-8') as f:
                    verses = [p for p in (parse_verse_line(line) for line in f) if p]
                if verses:
                    data[chapter_key] = verses
    except Exception as e:
        print(f"Error parsing book directory {book_dir}: {e}")
    return data


def to_abs(path_like: str) -> str:
    return path_like if os.path.isabs(path_like) else os.path.join(ROOT_DIR, path_like)


def build_scripture_data() -> dict:
    data = {
        "The Tanak": {
            "The Torah": {},
            "Prophets": {},
            "First Writings (Kethubim)": {},
        },
        "New Testament": {}
    }

    dir_to_section = {
        to_abs(TORAH_DIR): ("The Tanak", "The Torah"),
        to_abs(PROPHETS_DIR): ("The Tanak", "Prophets"),
        to_abs(KETHUBIM_DIR): ("The Tanak", "First Writings (Kethubim)"),
        to_abs(NEW_TESTAMENT_DIR): ("New Testament", None),
    }

    for index, (abbr, full_name, out_dir_rel) in enumerate(ORDERED_BOOKS, start=1):
        out_dir = to_abs(out_dir_rel)
        division, subsection = dir_to_section.get(out_dir, (None, None))
        if division is None:
            continue
        book_dir_name = f"{index:02d} - {full_name}"
        book_path = os.path.join(out_dir, book_dir_name)
        if not os.path.isdir(book_path):
            # Skip missing books silently to allow partial builds
            continue
        chapters = parse_chapter_files(book_path)
        if not chapters:
            continue
        if division == "New Testament":
            data[division][book_dir_name] = chapters
        else:
            data[division][subsection][book_dir_name] = chapters

    return data

# --- HTML Generation Function ---
def build_html_file(scripture_data):
    """Injects data and scripts into the HTML file."""
    print("Reading template files...")
    try:
        with open(os.path.join(VIEWER_DIR, 'style.css'), 'r', encoding='utf-8') as f:
            css_content = f.read()
        with open(os.path.join(VIEWER_DIR, 'script.js'), 'r', encoding='utf-8') as f:
            js_content = f.read()
    except Exception as e:
        print(f"Error reading template files: {e}")
        return

    data_as_json_string = json.dumps(scripture_data, ensure_ascii=False, indent=2)

    html_content = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>Scripture Viewer</title>
    <style>\n{css_content}\n</style>
</head>
<body>
    <div class=\"container\">
        <div class=\"pane navigation-pane\">
            <h2>Navigation</h2>
            <div id=\"navigation-tree\"></div>
        </div>
        <div class=\"pane content-pane\">
            <h1 id=\"chapter-title\">Welcome</h1>
            <div id=\"chapter-content\">
                <p>Select a chapter from the navigation menu to begin reading.</p>
            </div>
        </div>
        <div class=\"pane search-pane\">
            <h2>Search</h2>
            <input type=\"text\" id=\"search-input\" placeholder=\"Search for keywords or try gen1:1, 1tim 2:5...\">
            <div id=\"search-results\"></div>
        </div>
    </div>

    <script>
    // Injected data from build.py
    const scriptureData = {data_as_json_string};

    // Injected script from script.js
{js_content}
    </script>
</body>
</html>"""

    try:
        with open(OUTPUT_HTML_FILE, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Successfully created self-contained HTML file at: {OUTPUT_HTML_FILE}")
    except Exception as e:
        print(f"Error writing final HTML file: {e}")

# --- Main Execution ---
def main():
    print(f"Starting scan in: {SOURCE_DIR}")
    scripture_data = build_scripture_data()
    build_html_file(scripture_data)

if __name__ == '__main__':
    main()
