from pydantic import BaseModel
from typing import List


class SourceEvidence(BaseModel):
    quote: str
    page: int


class Concept(BaseModel):
    concept_id: str
    order: int
    concept: str

    english: SourceEvidence
    hindi: SourceEvidence


class ConceptMap(BaseModel):
    chapter: int
    title: str
    concepts: List[Concept]