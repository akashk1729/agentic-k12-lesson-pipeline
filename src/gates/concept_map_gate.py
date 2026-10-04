import json
from pathlib import Path

from src.gates.quote_gate import verify_quote


ROOT = Path(__file__).resolve().parent.parent.parent

ENGLISH_FILE = ROOT / "data" / "extracted" / "chapter4_english.json"
HINDI_FILE = ROOT / "data" / "extracted" / "chapter4_hindi.json"

CONCEPT_MAP_FILE = ROOT / "outputs" / "concept_map.json"
OUTPUT_FILE = ROOT / "outputs" / "concept_map_gate.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_book_text(data):
    """
    Combine all extracted textbook pages into one searchable
    textbook representation.
    """

    if isinstance(data, list):
        pages = data
    else:
        pages = data["pages"]

    return "\n".join(
        page.get("text", "")
        for page in pages
    )


def run_gate():

    concept_map = load_json(CONCEPT_MAP_FILE)

    english_data = load_json(ENGLISH_FILE)
    hindi_data = load_json(HINDI_FILE)

    english_text = get_book_text(english_data)
    hindi_text = get_book_text(hindi_data)

    results = []

    for concept in concept_map["concepts"]:

        english_result = verify_quote(
            concept["english"]["quote"],
            english_text,
            concept["concept_id"] + "_EN"
        )

        hindi_result = verify_quote(
            concept["hindi"]["quote"],
            hindi_text,
            concept["concept_id"] + "_HI"
        )

        results.append({
            "concept_id": concept["concept_id"],
            "english": english_result,
            "hindi": hindi_result,
        })

    passed = all(
        result["english"]["status"] == "PASS"
        and result["hindi"]["status"] == "PASS"
        for result in results
    )

    output = {
        "gate": "concept_map_quote_gate",
        "status": "PASS" if passed else "FAIL",
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
    print("CONCEPT MAP QUOTE GATE")
    print("=" * 60)
    print(f"Status: {output['status']}")

    for result in results:
        print(
            f"{result['concept_id']}: "
            f"EN={result['english']['status']} "
            f"HI={result['hindi']['status']}"
        )

    print("=" * 60)
    print(f"Gate output: {OUTPUT_FILE}")

    if not passed:
        raise SystemExit(
            "Concept map quote gate FAILED."
        )


if __name__ == "__main__":
    run_gate()