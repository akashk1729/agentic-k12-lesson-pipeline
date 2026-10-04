import json
from pathlib import Path

from src.concept_schema import ConceptMap
from src.script_schema import LessonScript, ScriptBeat


ROOT = Path(__file__).resolve().parent.parent

CONCEPT_MAP_FILE = ROOT / "outputs" / "concept_map.json"
OUTPUT_FILE = ROOT / "outputs" / "lesson_script.json"


def load_concept_map():
    with open(CONCEPT_MAP_FILE, "r", encoding="utf-8") as f:
        return ConceptMap.model_validate(json.load(f))


def make_script(concept_map):

    concepts = {
        c.concept_id: c
        for c in concept_map.concepts
    }

    beats = [
        ScriptBeat(
            beat_id="B1",
            order=1,
            concept_id="C4.3.1",
            narration=(
                "जब एक चुंबक को स्वतंत्र रूप से लटकाया जाता है, "
                "तो वह उत्तर-दक्षिण दिशा में ठहरता है। "
                "आइए इसे एक सरल प्रयोग से समझते हैं। "
                "चुंबक को इस तरह लटकाने पर उसके घूमने के बाद "
                "एक विशेष दिशा में ठहरने का गुण दिखाई देता है।"
            ),
            on_screen_text=(
                "स्वतंत्र रूप से लटका चुंबक\n"
                "उत्तर-दक्षिण दिशा में ठहरता है"
            ),
            source_quote=concepts["C4.3.1"].hindi.quote,
            source_page=concepts["C4.3.1"].hindi.page,
        ),

        ScriptBeat(
            beat_id="B2",
            order=2,
            concept_id="C4.3.2",
            narration=(
                "चुंबक के दो सिरों की भी विशेष पहचान होती है। "
                "जो सिरा उत्तर की ओर संकेत करता है, उसे उत्तरी ध्रुव "
                "कहा जाता है। दूसरा सिरा दक्षिण की ओर संकेत करता है, "
                "इसलिए उसे दक्षिणी ध्रुव कहा जाता है।"
            ),
            on_screen_text=(
                "उत्तरी ध्रुव\n"
                "दक्षिणी ध्रुव"
            ),
            source_quote=concepts["C4.3.2"].hindi.quote,
            source_page=concepts["C4.3.2"].hindi.page,
        ),

        ScriptBeat(
            beat_id="B3",
            order=3,
            concept_id="C4.3.3",
            narration=(
                "अब सवाल है कि स्वतंत्र रूप से लटका हुआ चुंबक "
                "उत्तर-दक्षिण दिशा में ही क्यों ठहरता है? "
                "पाठ के अनुसार, हमारी पृथ्वी स्वयं एक विशाल चुंबक "
                "की तरह व्यवहार करती है।"
            ),
            on_screen_text=(
                "पृथ्वी स्वयं\n"
                "एक विशाल चुंबक की तरह व्यवहार करती है"
            ),
            source_quote=concepts["C4.3.3"].hindi.quote,
            source_page=concepts["C4.3.3"].hindi.page,
        ),

        ScriptBeat(
            beat_id="B4",
            order=4,
            concept_id="C4.3.4",
            narration=(
                "स्वतंत्र रूप से लटके चुंबक के उत्तर-दक्षिण दिशा "
                "में ठहरने के इस गुण का उपयोग दिशाएँ जानने के लिए "
                "किया जाता है। यानी चुंबक की इस विशेषता की मदद से "
                "हम दिशा की पहचान कर सकते हैं।"
            ),
            on_screen_text=(
                "चुंबक के गुण का उपयोग\n"
                "दिशाएँ जानने के लिए"
            ),
            source_quote=concepts["C4.3.4"].hindi.quote,
            source_page=concepts["C4.3.4"].hindi.page,
        ),

        ScriptBeat(
            beat_id="B5",
            order=5,
            concept_id="C4.3.5",
            narration=(
                "इसी आधार पर दिशाएँ जानने के लिए चुंबकीय दिक्सूचक "
                "विकसित किया गया। इसमें सुई के आकार का एक चुंबक "
                "होता है, जो स्वतंत्र रूप से घूम सकता है। "
                "जब सुई घूमना बंद करती है, तो वह उत्तर-दक्षिण दिशा "
                "की ओर संकेत करती है।"
            ),
            on_screen_text=(
                "चुंबकीय दिक्सूचक\n"
                "स्वतंत्र रूप से घूमने वाली चुंबकीय सुई"
            ),
            source_quote=concepts["C4.3.5"].hindi.quote,
            source_page=concepts["C4.3.5"].hindi.page,
        ),

        ScriptBeat(
            beat_id="B6",
            order=6,
            concept_id="C4.3.1",
            narration=(
                "इस बात को याद रखने का एक आसान तरीका है। "
                "जब चुंबक स्वतंत्र रूप से लटका हो, तो उसे कुछ समय "
                "घूमने दें और फिर देखें कि वह किस दिशा में ठहरता है। "
                "पाठ में बताया गया है कि वह उत्तर-दक्षिण दिशा में "
                "ठहरता है।"
            ),
            on_screen_text=(
                "प्रयोग:\n"
                "चुंबक को स्वतंत्र रूप से लटकाएँ\n"
                "कुछ समय बाद उसकी दिशा देखें"
            ),
            source_quote=concepts["C4.3.1"].hindi.quote,
            source_page=concepts["C4.3.1"].hindi.page,
        ),

        ScriptBeat(
            beat_id="B7",
            order=7,
            concept_id="C4.3.4",
            narration=(
                "इस गुण का महत्व इसलिए है क्योंकि दिशा जानने के लिए "
                "हमें किसी स्थिर संदर्भ की आवश्यकता होती है। "
                "स्वतंत्र रूप से लटके चुंबक का उत्तर-दक्षिण दिशा में "
                "ठहरना हमें दिशा पहचानने का एक तरीका देता है। "
                "इसी गुण का उपयोग दिशाएँ जानने में किया जाता है।"
            ),
            on_screen_text=(
                "उत्तर-दक्षिण दिशा में ठहरने का गुण\n"
                "→ दिशाएँ जानने में उपयोग"
            ),
            source_quote=concepts["C4.3.4"].hindi.quote,
            source_page=concepts["C4.3.4"].hindi.page,
        ),

        ScriptBeat(
            beat_id="B8",
            order=8,
            concept_id="C4.3.5",
            narration=(
                "अब चुंबकीय दिक्सूचक को समझिए। "
                "इसमें सुई के आकार का एक चुंबक होता है जो "
                "स्वतंत्र रूप से घूम सकता है। "
                "दिक्सूचक की सुई उत्तर-दक्षिण दिशा की ओर संकेत करती है। "
                "इसलिए जब हमें किसी स्थान पर दिशा जाननी हो, "
                "तो चुंबकीय दिक्सूचक का उपयोग किया जा सकता है।"
            ),
            on_screen_text=(
                "चुंबकीय दिक्सूचक\n"
                "सुई → उत्तर-दक्षिण दिशा"
            ),
            source_quote=concepts["C4.3.5"].hindi.quote,
            source_page=concepts["C4.3.5"].hindi.page,
        ),
    ]

    return LessonScript(
        chapter=4,
        topic="Finding Directions with a Magnet",
        language="Hindi",
        beats=beats,
    )


def main():

    concept_map = load_concept_map()

    script = make_script(concept_map)

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
            script.model_dump(),
            f,
            ensure_ascii=False,
            indent=2
        )

    print("=" * 60)
    print("HINDI LESSON SCRIPT")
    print("=" * 60)
    print(f"Topic: {script.topic}")
    print(f"Beats: {len(script.beats)}")

    for beat in script.beats:
        print(
            f"{beat.beat_id} | "
            f"{beat.concept_id} | "
            f"Page {beat.source_page}"
        )

    print("=" * 60)
    print(f"Script written to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()