import json
import re
from pathlib import Path

import fitz


ROOT = Path(__file__).resolve().parent.parent

RAW_DIR = ROOT / "data" / "raw"
OUTPUT_DIR = ROOT / "data" / "extracted"


def extract_textbook_page(text: str):
    """
    Extract the printed textbook page number from the
    bottom of the PDF page.

    Example:
        Curiosity | Textbook of Science | Grade 6
        66
        Reprint 2026-27

    returns:
        66
    """

    # Look for a standalone number near the end of the page.
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    # Search from the bottom because the printed page number
    # normally appears near the bottom of the textbook page.
    for line in reversed(lines):
        if re.fullmatch(r"\d{1,3}", line):
            return int(line)

    return None


def extract_pdf(pdf_path: Path, language: str):
    """
    Extract every PDF page while preserving:
    - PDF page number
    - printed textbook page number
    - language
    - extracted text
    """

    document = fitz.open(pdf_path)

    pages = []

    for pdf_index, page in enumerate(document):

        text = page.get_text("text")

        textbook_page = extract_textbook_page(text)

        pages.append(
            {
                "pdf_page": pdf_index + 1,
                "textbook_page": textbook_page,
                "language": language,
                "text": text,
            }
        )

    return pages


def save_json(data, output_path: Path):

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )


def main():

    english_pdf = RAW_DIR / "english.pdf"
    hindi_pdf = RAW_DIR / "hindi.pdf"

    english_output = (
        OUTPUT_DIR / "chapter4_english.json"
    )

    hindi_output = (
        OUTPUT_DIR / "chapter4_hindi.json"
    )

    english_pages = extract_pdf(
        english_pdf,
        "english"
    )

    hindi_pages = extract_pdf(
        hindi_pdf,
        "hindi"
    )

    save_json(
        english_pages,
        english_output
    )

    save_json(
        hindi_pages,
        hindi_output
    )

    print(
        f"English pages extracted: {len(english_pages)}"
    )

    print(
        f"Hindi pages extracted: {len(hindi_pages)}"
    )

    print(
        "Textbook page numbers detected automatically."
    )


if __name__ == "__main__":
    main()