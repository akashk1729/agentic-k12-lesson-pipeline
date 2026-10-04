from pydantic import BaseModel
from typing import List


class ScriptBeat(BaseModel):
    beat_id: str
    order: int
    concept_id: str

    narration: str
    on_screen_text: str

    source_quote: str
    source_page: int


class LessonScript(BaseModel):
    chapter: int
    topic: str
    language: str
    beats: List[ScriptBeat]