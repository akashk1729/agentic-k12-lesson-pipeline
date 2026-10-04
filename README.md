# K-12 Agentic Lesson Pipeline — Starter

Chapter selected:
- Class 6 Science Curiosity
- Chapter 4
- English: Exploring Magnets
- Hindi: चुंबकों को जानें

## Setup

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
```

## Run ingestion

```bash
python run.py
```

This creates:

- `data/extracted/chapter4_english.json`
- `data/extracted/chapter4_hindi.json`

## Next stages

1. Concept map agent
2. Topic plan
3. Hindi beat-level script
4. Deterministic quote/term/coverage gates
5. Reviewer agent
6. TTS + textbook figure visuals + subtitles
7. MP4 rendering

Do not add the LLM until the deterministic ingestion and gate tests are working.
