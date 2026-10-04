# Agentic K-12 Lesson Pipeline

An end-to-end, faithfulness-first pipeline for converting an NCERT Class 6 Science chapter into a validated Hindi educational lesson video with subtitles.

> **The generated lesson should stay grounded in the textbook, and unsupported claims should be caught before media generation.**

The implementation uses NCERT Class 6 Science *Curiosity*, Chapter 4 — **Exploring Magnets / चुंबकों को जानें**.

## 1. What This Project Does

The pipeline takes the English and Hindi editions of an NCERT chapter and produces:

1. Page-level textbook extraction
2. A concept map in printed textbook order
3. A lesson plan for a selected topic
4. A Hindi lesson script with beat-level citations
5. Deterministic faithfulness gates
6. Reviewer verdicts for every script beat
7. Hindi TTS narration
8. Textbook-derived visual material
9. An MP4 lesson video
10. SRT subtitles

Run the complete pipeline with:

```bash
python run.py
```

## 2. Source Material

**NCERT Class 6 Science — Curiosity**

- English: Chapter 4 — *Exploring Magnets*
- Hindi: Chapter 4 — *चुंबकों को जानें*

### Selected lesson topic

**Finding Directions with a Magnet**

The lesson covers:

- A freely suspended magnet settling in the north-south direction
- North and South poles
- Earth's magnetic behavior
- Using a magnet to find directions
- The magnetic compass and its freely rotating needle

## 3. Pipeline Architecture

```text
English + Hindi PDFs
        ↓
Page-level ingestion
        ↓
Concept map + source evidence
        ↓
Concept-map faithfulness gate
        ↓
Lesson plan
        ↓
Hindi beat-by-beat script
        ↓
Deterministic script gates
        ↓
Reviewer verification
        ↓
TTS + visuals + subtitles
        ↓
Final MP4 + SRT
```

## 4. Repository Structure

```text
agentic-k12-lesson-pipeline/
├── data/
│   ├── raw/
│   │   ├── english.pdf
│   │   └── hindi.pdf
│   └── extracted/
│       ├── chapter4_english.json
│       ├── chapter4_hindi.json
│       └── chapter_metadata.json
├── src/
│   ├── ingestion.py
│   ├── concept_schema.py
│   ├── concept_map.py
│   ├── lesson_plan.py
│   ├── script_schema.py
│   ├── script_agent.py
│   ├── reviewer.py
│   ├── media_pipeline_polished.py
│   └── gates/
│       ├── quote_gate.py
│       ├── concept_map_gate.py
│       └── script_gate.py
├── tests/
│   └── test_quote_gate.py
├── outputs/
│   └── iteration_03/
│       ├── concept_map.json
│       ├── concept_map_gate.json
│       ├── lesson_plan.json
│       ├── lesson_script.json
│       ├── script_gate.json
│       ├── reviewer_verdicts.json
│       ├── lesson_video_final.mp4
│       └── lesson_subtitles.srt
├── run.py
├── requirements.txt
├── README.md
└── SUBMISSION_NOTE.md
```

# 5. Setup

## Requirements

- Python 3.10+
- FFmpeg
- Internet access for Hindi TTS and automatic font setup
- Python packages listed in `requirements.txt`

The implementation was developed and tested on Windows using PowerShell.

## Install dependencies

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Verify FFmpeg:

```powershell
ffmpeg -version
```

# 6. One-Command Execution

After setup:

```powershell
python run.py
```

The command executes:

```text
[1/8] PDF INGESTION
[2/8] CONCEPT MAP
[3/8] CONCEPT MAP FAITHFULNESS GATE
[4/8] LESSON PLAN
[5/8] HINDI LESSON SCRIPT
[6/8] SCRIPT FAITHFULNESS GATE
[7/8] REVIEWER
[8/8] POLISHED VIDEO + SUBTITLES
```

A successful execution ends with:

```text
Final video duration: 181.0 seconds
Duration check: PASS

Everything completed successfully.
```

# 7. PDF Ingestion

The English and Hindi PDFs are processed page-by-page.

Each page stores:

- PDF page index
- printed page number when available
- extracted text

Outputs:

```text
data/extracted/chapter4_english.json
data/extracted/chapter4_hindi.json
```

# 8. Concept Map

The concept map identifies the concepts required for the selected lesson and preserves their printed order.

Each concept contains:

- Concept ID
- Printed order
- Concept description
- English evidence
- Hindi evidence
- Source quote
- Source page

The selected topic uses:

```text
C4.3.1 — A freely suspended magnet rests in north-south direction
C4.3.2 — The two ends of a magnet are called North and South poles
C4.3.3 — Earth behaves like a giant magnet
C4.3.4 — The north-south property of a magnet is used to find directions
C4.3.5 — A magnetic compass has a freely rotating magnetic needle
```

# 9. Deterministic Concept-Map Gate

For every concept, the gate checks whether the stored source evidence exists in the extracted textbook.

It verifies both English and Hindi evidence.

Example:

```text
C4.3.1: EN=PASS HI=PASS
C4.3.2: EN=PASS HI=PASS
C4.3.3: EN=PASS HI=PASS
C4.3.4: EN=PASS HI=PASS
C4.3.5: EN=PASS HI=PASS
```

If cited evidence cannot be found, the pipeline fails before continuing.

# 10. Lesson Planning

Current lesson:

```text
Topic:
Finding Directions with a Magnet

Language:
Hindi

Concepts:
C4.3.1
C4.3.2
C4.3.3
C4.3.4
C4.3.5

Target duration:
3–8 minutes
```

Stored in:

```text
outputs/iteration_03/lesson_plan.json
```

# 11. Hindi Lesson Script

Each beat contains:

- Beat ID
- Concept ID
- Hindi narration
- On-screen text
- Source quote
- Source page

Example:

```text
B1 → C4.3.1
B2 → C4.3.2
B3 → C4.3.3
B4 → C4.3.4
B5 → C4.3.5
...
```

The script uses terminology from the Hindi textbook edition.

# 12. Deterministic Script Gates

Before TTS or video generation, the script passes through deterministic validation.

The gates verify:

### Citation existence
The cited source quote must exist in the textbook.

### Citation-to-narration support
The narration must be supported by the cited source evidence.

### Planned concept coverage
Every planned concept must appear in the script.

### Number validation
Numbers appearing in the script are checked against the relevant source material.

### Directional terminology
Important directional terminology is checked against the source, including:

```text
उत्तर-दक्षिण
उत्तर
दक्षिण
पूर्व
पश्चिम
```

# 13. Planted Hallucination Test

The pipeline was tested with a deliberately introduced unsupported directional claim.

Changing the supported north-south statement to an unsupported directional claim causes the script gate to fail.

This demonstrates that the validation layer does more than check for the presence of citations: it also checks whether generated claims remain compatible with the cited textbook evidence.

The hallucinated version was rejected before media generation.

# 14. Reviewer

The reviewer provides a second validation layer.

Each beat receives one of:

```text
SUPPORTED
UNSUPPORTED
CONTRADICTS
```

The final reviewer output is:

```text
outputs/iteration_03/reviewer_verdicts.json
```

Final result:

```text
B1: SUPPORTED
B2: SUPPORTED
B3: SUPPORTED
B4: SUPPORTED
B5: SUPPORTED
B6: SUPPORTED
B7: SUPPORTED
B8: SUPPORTED

Status: CLEAN
```

Media generation occurs only after the validation stages complete successfully.

# 15. Media Generation

After validation, the pipeline generates:

- Hindi TTS narration
- textbook-derived visuals and presentation slides
- SRT subtitles
- final MP4

Final video duration:

```text
181.0 seconds
```

The duration check passes the required 3–8 minute range.

# 16. Generated Submission Artifacts

All final artifacts are under:

```text
outputs/iteration_03/
```

| Artifact | Purpose |
|---|---|
| `concept_map.json` | Ordered concepts with textbook evidence |
| `concept_map_gate.json` | Concept evidence validation |
| `lesson_plan.json` | Topic and required concept coverage |
| `lesson_script.json` | Hindi beat-by-beat script with citations |
| `script_gate.json` | Deterministic script validation |
| `reviewer_verdicts.json` | Beat-level reviewer classifications |
| `lesson_video_final.mp4` | Final Hindi lesson video |
| `lesson_subtitles.srt` | Final subtitles |

# 17. Tests

Run:

```powershell
python -m pytest
```

The tests include validation of the deterministic quote gate, including acceptance of valid source quotes and rejection of unsupported quotes.

# 18. Design Principles

### Faithfulness before generation
Source evidence is validated before downstream media generation.

### Deterministic gates
Critical faithfulness checks are implemented using deterministic logic rather than relying entirely on an LLM.

### Page-level provenance
Claims are associated with specific textbook pages and source quotes.

### Hindi-first terminology
The lesson is generated in Hindi while retaining terminology from the Hindi textbook edition.

### Failure visibility
The pipeline is designed to fail when required validation conditions are not satisfied instead of silently producing unsupported content.

# 19. Known Limitations

### PDF extraction quality
The Hindi PDF contains extraction/OCR artifacts, including unusual character spacing and split characters.

Normalized text is used for matching where necessary, while the extracted source evidence is retained rather than silently rewritten.

### Reviewer scope
The reviewer is implemented as a structured/deterministic verification component rather than a fully autonomous LLM reviewer with unrestricted reasoning.

### Static visual presentation
The current renderer uses a relatively simple slide/page-based visual presentation rather than a fully animated educational production.

### TTS dependency
Hindi narration depends on the configured TTS system and runtime/network availability.

### Single lesson configuration
This submission demonstrates the pipeline on one selected topic from Chapter 4. The architecture is intended to be reusable for other chapters and topics.

# 20. Reproducibility

```powershell
git clone https://github.com/akashk1729/agentic-k12-lesson-pipeline.git
cd agentic-k12-lesson-pipeline

python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install -r requirements.txt
python run.py
```

Outputs are written under:

```text
outputs/iteration_03/
```

# 21. Final Result

```text
PDF ingestion
      ↓
Concept mapping
      ↓
Concept evidence validation
      ↓
Lesson planning
      ↓
Hindi script generation
      ↓
Script faithfulness validation
      ↓
Reviewer verification
      ↓
TTS + visuals
      ↓
MP4 + subtitles
```

Final validation:

```text
Pipeline status: SUCCESS
Final video duration: 181.0 seconds
Duration check: PASS
Reviewer status: CLEAN
```

## Repository

https://github.com/akashk1729/agentic-k12-lesson-pipeline
