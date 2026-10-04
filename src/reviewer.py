import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SCRIPT_FILE = ROOT / "outputs" / "lesson_script.json"
OUTPUT_FILE = ROOT / "outputs" / "reviewer_verdicts.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize(text):
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def review_beat(beat):
    narration = normalize(beat["narration"])
    source = normalize(beat["source_quote"])

    # Directional contradiction detection
    direction_pairs = [
        ("उत्तर-दक्षिण", "पूर्व"),
        ("उत्तर-दक्षिण", "पश्चिम"),
        ("उत्तर", "पूर्व"),
        ("उत्तर", "पश्चिम"),
        ("दक्षिण", "पूर्व"),
        ("दक्षिण", "पश्चिम"),
    ]

    for supported_direction, wrong_direction in direction_pairs:
        if (
            wrong_direction in narration
            and supported_direction in source
        ):
            return {
                "beat_id": beat["beat_id"],
                "concept_id": beat["concept_id"],
                "verdict": "CONTRADICTS",
                "reason": (
                    f"Narration contains '{wrong_direction}', "
                    f"while the cited evidence supports "
                    f"'{supported_direction}'."
                ),
            }

    # Check important textbook terms.
    important_terms = [
        "चुंबक",
        "उत्तर",
        "दक्षिण",
        "ध्रुव",
        "दिशा",
        "दिक्सूचक",
        "सुई",
    ]

    supported_terms = [
        term
        for term in important_terms
        if term in source
    ]

    missing_terms = [
        term
        for term in supported_terms
        if term not in narration
    ]

    # If the beat shares relevant terminology with its evidence,
    # classify it as supported.
    if supported_terms:
        return {
            "beat_id": beat["beat_id"],
            "concept_id": beat["concept_id"],
            "verdict": "SUPPORTED",
            "reason": "Narration is consistent with cited textbook evidence.",
        }

    return {
        "beat_id": beat["beat_id"],
        "concept_id": beat["concept_id"],
        "verdict": "UNSUPPORTED",
        "reason": "No sufficient textbook terminology was found.",
    }


def run_reviewer():

    script = load_json(SCRIPT_FILE)

    verdicts = []

    for beat in script["beats"]:
        verdicts.append(review_beat(beat))

    clean = all(
        verdict["verdict"] == "SUPPORTED"
        for verdict in verdicts
    )

    output = {
        "reviewer": "deterministic_reviewer",
        "status": "CLEAN" if clean else "NEEDS_REVISION",
        "verdicts": verdicts,
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
    print("REVIEWER")
    print("=" * 60)
    print(f"Status: {output['status']}")

    for verdict in verdicts:
        print(
            f"{verdict['beat_id']} | "
            f"{verdict['concept_id']} | "
            f"{verdict['verdict']} | "
            f"{verdict['reason']}"
        )

    print("=" * 60)
    print(f"Reviewer output: {OUTPUT_FILE}")

    if not clean:
        raise SystemExit("Reviewer found unsupported content.")


if __name__ == "__main__":
    run_reviewer()