import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CONCEPT_MAP_FILE = ROOT / "outputs" / "concept_map.json"
OUTPUT_FILE = ROOT / "outputs" / "lesson_plan.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_lesson_plan():

    concept_map = load_json(CONCEPT_MAP_FILE)

    # We deliberately select ONE topic from Chapter 4.
    selected_topic = "Finding Directions with a Magnet"

    # Concepts are referenced by concept_id rather than rewritten.
    selected_concepts = [
        "C4.3.1",
        "C4.3.2",
        "C4.3.3",
        "C4.3.4",
        "C4.3.5",
    ]

    concept_lookup = {
        concept["concept_id"]: concept
        for concept in concept_map["concepts"]
    }

    concepts = []

    for concept_id in selected_concepts:

        if concept_id not in concept_lookup:
            raise ValueError(
                f"Planned concept {concept_id} "
                "does not exist in concept map."
            )

        concept = concept_lookup[concept_id]

        concepts.append({
            "concept_id": concept["concept_id"],
            "order": concept["order"],
            "concept": concept["concept"],
            "english_page": concept["english"]["page"],
            "hindi_page": concept["hindi"]["page"],
        })

    lesson_plan = {
        "chapter": 4,
        "topic": selected_topic,
        "language": "Hindi",
        "target_duration_seconds": {
            "minimum": 180,
            "maximum": 480
        },
        "concepts": concepts
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
            lesson_plan,
            f,
            ensure_ascii=False,
            indent=2
        )

    print("=" * 60)
    print("LESSON PLAN")
    print("=" * 60)
    print(f"Topic: {selected_topic}")
    print("Language: Hindi")
    print()
    print("Concepts:")

    for concept in concepts:
        print(
            f"  {concept['order']}. "
            f"{concept['concept_id']} - "
            f"{concept['concept']}"
        )

    print()
    print("Target duration: 3–8 minutes")
    print("=" * 60)
    print(f"Lesson plan written to: {OUTPUT_FILE}")


if __name__ == "__main__":
    build_lesson_plan()