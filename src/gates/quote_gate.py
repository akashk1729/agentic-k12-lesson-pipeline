import re
import unicodedata


def normalize_text(text: str) -> str:
    """
    Normalize text for deterministic quote matching.

    We ignore differences caused by:
    - Unicode representation
    - line breaks
    - multiple spaces
    - non-breaking spaces
    """

    text = unicodedata.normalize("NFKC", text)

    # Remove soft hyphen
    text = text.replace("\u00ad", "")

    # Convert all whitespace sequences to one space
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def quote_exists(quote: str, book_text: str) -> bool:
    """
    Check whether the quoted textbook evidence
    occurs in the extracted textbook text.
    """

    normalized_quote = normalize_text(quote)
    normalized_book = normalize_text(book_text)

    return normalized_quote in normalized_book


def verify_quote(quote: str, book_text: str, concept_id: str):
    """
    Return a structured gate result.
    """

    if quote_exists(quote, book_text):
        return {
            "concept_id": concept_id,
            "status": "PASS",
            "reason": "Quote found in textbook."
        }

    return {
        "concept_id": concept_id,
        "status": "FAIL",
        "reason": "Quoted evidence was not found in textbook."
    }