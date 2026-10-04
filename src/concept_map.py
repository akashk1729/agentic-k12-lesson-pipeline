import json
from pathlib import Path

from src.concept_schema import (
    Concept,
    ConceptMap,
    SourceEvidence,
)


ROOT = Path(__file__).resolve().parent.parent

ENGLISH_FILE = ROOT / "data" / "extracted" / "chapter4_english.json"
HINDI_FILE = ROOT / "data" / "extracted" / "chapter4_hindi.json"

OUTPUT_FILE = ROOT / "outputs" / "concept_map.json"


def load_pages(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_pages(data):
    """
    Handles the extracted JSON whether the pages are stored directly
    as a list or under a 'pages' key.
    """
    if isinstance(data, list):
        return data

    if isinstance(data, dict) and "pages" in data:
        return data["pages"]

    raise ValueError("Unexpected extracted JSON format")


def find_page(pages, textbook_page):
    """
    Find a page using the printed textbook page number.
    """
    for page in pages:
        if page.get("textbook_page") == textbook_page:
            return page

    raise ValueError(
        f"Textbook page {textbook_page} was not found in extracted data."
    )


'''def extract_evidence(page, anchors):
    """
    Find evidence directly inside textbook text.

    We return the original text from the textbook extraction.
    Nothing is generated or paraphrased.
    """
    text = page.get("text", "")

    for anchor in anchors:
        index = text.lower().find(anchor.lower())

        if index != -1:
            # Take a useful surrounding chunk while preserving
            # the exact source text.
            start = max(0, index - 40)
            end = min(len(text), index + 500)

            return text[start:end].strip()

    raise ValueError(
        f"Could not find any of the anchors on textbook page "
        f"{page.get('textbook_page')}: {anchors}"
    )'''

def normalize_for_search(text):
    """
    Normalize PDF extraction artifacts for searching.

    This is only used to FIND evidence.
    The returned evidence remains the original textbook text.
    """

    import unicodedata
    import re

    text = unicodedata.normalize("NFKC", text)

    # Remove zero-width / formatting characters
    text = re.sub(r"[\u200b\u200c\u200d\ufeff]", "", text)

    # Remove whitespace between characters caused by PDF extraction.
    # Example:
    #     चं बक
    # becomes:
    #     चंबक
    text = re.sub(r"\s+", "", text)

    return text.lower()


def extract_evidence(page, anchors):
    """
    Find evidence inside the actual textbook extraction.

    Searching uses a normalized representation because Hindi PDF
    extraction can split Unicode words.

    The evidence returned is still the original extracted text.
    """

    original_text = page.get("text", "")

    normalized_text = normalize_for_search(original_text)

    for anchor in anchors:

        normalized_anchor = normalize_for_search(anchor)

        index = normalized_text.find(normalized_anchor)

        if index != -1:

            # Because normalization removes whitespace, the index
            # cannot directly be used on original_text.
            #
            # Instead, locate a distinctive portion of the anchor
            # in the original text where possible.

            anchor_words = anchor.split()

            for word in anchor_words:

                if len(word.strip()) >= 3:

                    original_index = original_text.find(
                        word.strip()
                    )

                    if original_index != -1:

                        start = max(
                            0,
                            original_index - 150
                        )

                        end = min(
                            len(original_text),
                            original_index + 700
                        )

                        return original_text[
                            start:end
                        ].strip()

            # Fallback: return the relevant page text.
            return original_text[:900].strip()

    raise ValueError(
        f"Could not find any of the anchors on textbook "
        f"page {page.get('textbook_page')}: {anchors}"
    )


def build_concept_map():
    english_data = load_pages(ENGLISH_FILE)
    hindi_data = load_pages(HINDI_FILE)

    english_pages = get_pages(english_data)
    hindi_pages = get_pages(hindi_data)

    # Topic: Finding Directions with a Magnet
    #
    # IMPORTANT:
    # The anchors below are only search terms.
    # The evidence stored in the concept map comes directly
    # from the extracted textbook.

    definitions = [
        {
            "concept_id": "C4.3.1",
            "order": 1,
            "concept": "A freely suspended magnet rests in the north-south direction",

            "english_page": 66,
            "english_anchors": [
                "A freely suspended magnet comes to rest along",
                "north-south direction",
            ],

            "hindi_page": 64,
            "hindi_anchors": [
                "स्वतंत्र रूप से लटका हुआ चुंबक",
                "उत्तर-दक्षिण दिशा",
            ],
        },

        {
            "concept_id": "C4.3.2",
            "order": 2,
            "concept": "The two ends of a magnet are called North and South poles",

            "english_page": 66,
            "english_anchors": [
                "North-seeking pole",
                "North pole",
                "South-seeking",
            ],

            "hindi_page": 64,
            "hindi_anchors": [
                "उत्तरी ध्रुव",
                "दक्षिणी ध्रुव",
                "उत्तरोन्मुखी ध्रुव",
            ],
        },

        {
            "concept_id": "C4.3.3",
            "order": 3,
            "concept": "Earth behaves like a giant magnet",

            "english_page": 66,
            "english_anchors": [
                "our Earth itself behaves like a giant magnet",
                "Earth itself behaves like a giant magnet",
            ],

            "hindi_page": 64,
            "hindi_anchors": [
    "विशाल चुंबक",
    "विशाल",
],
        },

        {
            "concept_id": "C4.3.4",
            "order": 4,
            "concept": "The north-south property of a magnet is used to find directions",

            "english_page": 66,
            "english_anchors": [
                "property of a freely suspended magnet",
                "used to find directions",
            ],

            "hindi_page": 64,
            "hindi_anchors": [
                "दिशाएँ जानने के लिए",
                "दिशाएँ ज्ञात करने",
            ],
        },

        {
            "concept_id": "C4.3.5",
            "order": 5,
            "concept": "A magnetic compass has a freely rotating magnetic needle",

            "english_page": 66,
            "english_anchors": [
                "magnetic compass was developed",
                "magnet in the shape of a needle",
                "needle of a magnetic compass indicates",
            ],

            "hindi_page": 64,
            "hindi_anchors": [
                "चुंबकीय दिक्सूचक",
                "सुई के आकार",
                "उत्तर-दक्षिण दिशा",
            ],
        },
    ]

    concepts = []

    for item in definitions:

        english_page = find_page(
            english_pages,
            item["english_page"]
        )

        hindi_page = find_page(
            hindi_pages,
            item["hindi_page"]
        )

        english_quote = extract_evidence(
            english_page,
            item["english_anchors"]
        )

        hindi_quote = extract_evidence(
            hindi_page,
            item["hindi_anchors"]
        )

        concept = Concept(
            concept_id=item["concept_id"],
            order=item["order"],
            concept=item["concept"],

            english=SourceEvidence(
                quote=english_quote,
                page=item["english_page"],
            ),

            hindi=SourceEvidence(
                quote=hindi_quote,
                page=item["hindi_page"],
            ),
        )

        concepts.append(concept)

    concept_map = ConceptMap(
        chapter=4,
        title="Finding Directions with a Magnet",
        concepts=concepts,
    )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            concept_map.model_dump(),
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(f"Concept map written to: {OUTPUT_FILE}")


if __name__ == "__main__":
    build_concept_map()