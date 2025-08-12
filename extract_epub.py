
import os
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

def extract_epub_to_raw_text(epub_path, output_dir):
    """
    Extracts the text from an EPUB file and saves it as raw text files in the specified directory.

    Args:
        epub_path (str): The path to the EPUB file.
        output_dir (str): The directory where the raw text files will be saved.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    book = epub.read_epub(epub_path)

    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            # Use BeautifulSoup to parse the HTML and extract the text
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            text = soup.get_text()

            # Create a valid filename from the item's name
            filename = os.path.join(output_dir, f"{item.get_name().replace('/', '_')}.txt")

            # Save the extracted text to a file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(text)

            print(f"Extracted: {filename}")

if __name__ == '__main__':
    epub_file = 'TheScriptures-1998_ISR.epub'
    output_folder = 'raw_text'
    extract_epub_to_raw_text(epub_file, output_folder)
