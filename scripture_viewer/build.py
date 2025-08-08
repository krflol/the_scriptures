import os
import json
import re

# --- Configuration ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SOURCE_DIR = os.path.join(ROOT_DIR, 'The Tanak')
VIEWER_DIR = os.path.dirname(__file__)
OUTPUT_HTML_FILE = os.path.join(VIEWER_DIR, 'index.html')

# --- Markdown to HTML Conversion ---
def parse_markdown_to_html(text):
    """Converts specific Markdown syntax to HTML."""
    # Convert Obsidian-style wikilinks [[note|display]] or [[note]] to display text
    text = re.sub(r'\[\[(?:[^\]|]+\|)?([^\]]+)\]\]', r'\1', text)
    # Convert standard Markdown links [text](url) to <a href="url">text</a>
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', text)
    return text

# --- Data Parsing Functions ---
def parse_verse_line(line):
    """Parses a single line of scripture text and its Markdown content."""
    match = re.match(r'\s*<sup>(\d+)</sup>(.*?)(\s*\^([a-zA-Z0-9\-]+))?$\s*', line)
    if not match:
        return None

    verse_num = int(match.group(1))
    raw_text = match.group(2).strip()
    block_id = match.group(4)

    # Convert Markdown content within the verse text to HTML
    processed_text = parse_markdown_to_html(raw_text)

    return {
        "verse": verse_num,
        "text": processed_text, # Use the processed HTML content
        "id": block_id if block_id else f"v{verse_num}"
    }

def process_directory(path):
    """Recursively processes directories to build the scripture data."""
    data = {}
    for entry in sorted(os.scandir(path), key=lambda e: e.name):
        if entry.is_dir():
            data[entry.name] = process_directory(entry.path)
        elif entry.name.endswith('.md'):
            chapter_number = os.path.splitext(entry.name)[0]
            try:
                with open(entry.path, 'r', encoding='utf-8') as f:
                    verses = [p for p in (parse_verse_line(line) for line in f) if p]
                    if verses:
                        data[chapter_number] = verses
            except Exception as e:
                print(f"Error processing file {entry.path}: {e}")
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
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Scripture Viewer</title>
    <style>\n{css_content}\n</style>
</head>
<body>
    <div class="container">
        <div class="pane navigation-pane">
            <h2>Navigation</h2>
            <div id="navigation-tree"></div>
        </div>
        <div class="pane content-pane">
            <h1 id="chapter-title">Welcome</h1>
            <div id="chapter-content">
                <p>Select a chapter from the navigation menu to begin reading.</p>
            </div>
        </div>
        <div class="pane search-pane">
            <h2>Search</h2>
            <input type="text" id="search-input" placeholder="Search for keywords...">
            <div id="search-results"></div>
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
    """Main function to build the HTML file."""
    print(f"Starting scan in: {SOURCE_DIR}")
    scripture_data = process_directory(SOURCE_DIR)
    build_html_file(scripture_data)

if __name__ == '__main__':
    main()
