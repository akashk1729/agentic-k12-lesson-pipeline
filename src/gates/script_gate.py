import json
import re
from pathlib import Path

from src.gates.quote_gate import quote_exists


ROOT = Path(__file__).resolve().parent.parent.parent

BOOK_ENGLISH = ROOT / "data" / "extracted" / "chapter4_english.json"
BOOK_HINDI = ROOT / "data" / "extracted" / "chapter4_hindi.json"

SCRIPT_FILE = ROOT / "outputs" / "lesson_script.json"
PLAN_FILE = ROOT / "outputs" / "lesson_plan.json"

OUTPUT_FILE = ROOT / "outputs" / "script_gate.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_book_text(data):
    if isinstance(data, list):
        pages = data
    else:
        pages = data["pages"]

    return "\n".join(
        page.get("text", "")
        for page in pages
    )


def normalize(text):
    return re.sub(
        r"\s+",
        " ",
        text
    ).strip().lower()


def extract_numbers(text):
    return re.findall(
        r"\b\d+(?:\.\d+)?\b",
        text
    )

def check_narration_against_quote(beat):
    """
    Deterministic contradiction check.

    The narration must preserve the key directional/factual
    terminology of the cited textbook evidence.
    """

    narration = beat["narration"]
    source_quote = beat["source_quote"]

    # Normalize whitespace only.
    narration = re.sub(r"\s+", " ", narration).strip()
    source_quote = re.sub(r"\s+", " ", source_quote).strip()

    unsupported_terms = []

    # Directional claims are especially important for this topic.
    directional_terms = [
        "उत्तर-दक्षिण",
        "उत्तर",
        "दक्षिण",
        "पूर्व",
        "पश्चिम",
    ]

    narration_directions = [
        term
        for term in directional_terms
        if term in narration
    ]

    quote_directions = [
        term
        for term in directional_terms
        if term in source_quote
    ]

    # If narration makes a directional claim that differs
    # from the cited evidence, reject it.
    if narration_directions:

        for direction in narration_directions:

            if direction not in quote_directions:

                unsupported_terms.append(direction)

    return unsupported_terms

def check_numbers(script_text, book_text):
    """
    Deterministic check:
    Every number appearing in the script must also appear
    somewhere in the textbook.
    """

    script_numbers = extract_numbers(script_text)
    book_numbers = extract_numbers(book_text)

    unsupported = [
        number
        for number in script_numbers
        if number not in book_numbers
    ]

    return list(dict.fromkeys(unsupported))


def check_concepts(script, lesson_plan):
    """
    Every concept planned for the lesson must occur
    in at least one script beat.
    """

    planned = {
        concept["concept_id"]
        for concept in lesson_plan["concepts"]
    }

    covered = {
        beat["concept_id"]
        for beat in script["beats"]
    }

    missing = sorted(planned - covered)

    return missing


def run_gate():

    script = load_json(SCRIPT_FILE)
    lesson_plan = load_json(PLAN_FILE)

    english_data = load_json(BOOK_ENGLISH)
    hindi_data = load_json(BOOK_HINDI)

    english_text = get_book_text(english_data)
    hindi_text = get_book_text(hindi_data)

    results = []

        # ---------------------------------------------------------
    # 0. Check narration against cited evidence
    # ---------------------------------------------------------

    for beat in script["beats"]:

        unsupported_terms = check_narration_against_quote(
            beat
        )

        results.append({
            "beat_id": beat["beat_id"],
            "check": "narration_supported_by_citation",
            "status": (
                "PASS"
                if not unsupported_terms
                else "FAIL"
            ),
            "concept_id": beat["concept_id"],
            "unsupported_terms": unsupported_terms,
        })

    # ---------------------------------------------------------
    # 1. Check every cited source quote
    # ---------------------------------------------------------

    for beat in script["beats"]:

        quote = beat["source_quote"]

        quote_pass = quote_exists(
            quote,
            hindi_text
        )

        results.append({
            "beat_id": beat["beat_id"],
            "check": "source_quote_exists",
            "status": "PASS" if quote_pass else "FAIL",
            "concept_id": beat["concept_id"],
        })

    # ---------------------------------------------------------
    # 2. Check that every planned concept is covered
    # ---------------------------------------------------------

    missing_concepts = check_concepts(
        script,
        lesson_plan
    )

    results.append({
        "check": "planned_concepts_covered",
        "status": (
            "PASS"
            if not missing_concepts
            else "FAIL"
        ),
        "missing_concepts": missing_concepts,
    })

    # ---------------------------------------------------------
    # 3. Check numbers
    # ---------------------------------------------------------

    script_text = " ".join(
        beat["narration"] + " " +
        beat["on_screen_text"]
        for beat in script["beats"]
    )

    unsupported_numbers = check_numbers(
        script_text,
        hindi_text
    )

    results.append({
        "check": "numbers_supported",
        "status": (
            "PASS"
            if not unsupported_numbers
            else "FAIL"
        ),
        "unsupported_numbers": unsupported_numbers,
    })

    # ---------------------------------------------------------
    # Final result
    # ---------------------------------------------------------

    failed = [
        result
        for result in results
        if result["status"] == "FAIL"
    ]

    status = "PASS" if not failed else "FAIL"

    output = {
        "gate": "script_faithfulness_gate",
        "status": status,
        "results": results,
    }

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            output,
            f,
            ensure_ascii=False,
            indent=2
        )

    print("=" * 60)
    print("SCRIPT FAITHFULNESS GATE")
    print("=" * 60)

    print(f"Status: {status}")
    print()

    for result in results:
        print(result)

    print("=" * 60)
    print(f"Gate output: {OUTPUT_FILE}")

    if status == "FAIL":
        raise SystemExit(
            "Script faithfulness gate FAILED."
        )


if __name__ == "__main__":
    run_gate()