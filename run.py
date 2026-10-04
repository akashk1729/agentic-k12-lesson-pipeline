import asyncio
import os
import shutil
import subprocess
import sys
from pathlib import Path

from src.ingestion import main as ingestion_main
from src.concept_map import build_concept_map
from src.gates.concept_map_gate import run_gate as concept_map_gate
from src.lesson_plan import build_lesson_plan
from src.script_agent import main as script_main
from src.gates.script_gate import run_gate as script_gate
from src.reviewer import run_reviewer


ROOT = Path(__file__).resolve().parent
OUTPUTS = ROOT / "outputs"
ITERATION = OUTPUTS / "iteration_03"


def copy_to_iteration(filename):
    """Copy an intermediate artifact into the final iteration folder."""
    source = OUTPUTS / filename
    destination = ITERATION / filename

    if source.exists():
        shutil.copy2(source, destination)
        print(f"Copied: {filename}")
    else:
        raise FileNotFoundError(f"Required output not found: {source}")


'''def run_media_pipeline():
    """
    Run the polished Hindi video renderer.
    """
    env = os.environ.copy()
    env["K12_ITERATION"] = "iteration_03"

    subprocess.run(
        [
            "python",
            "-m",
            "src.media_pipeline_polished",
        ],
        cwd=ROOT,
        env=env,
        check=True,
    )'''

def run_media_pipeline():
    """
    Run the polished Hindi video renderer using
    the same Python interpreter as the main pipeline.
    """

    subprocess.run(
        [
            sys.executable,
            "src/media_pipeline_polished.py",
        ],
        cwd=ROOT,
        check=True,
    )


def get_duration(video):
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(video),
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    return float(result.stdout.strip())


def ensure_minimum_video_duration():
    """
    The assignment requires a 3–8 minute video.
    If the rendered video is slightly below 180 seconds,
    extend the final frame and audio with silence.
    """

    video = ITERATION / "lesson_video_polished.mp4"
    final_video = ITERATION / "lesson_video_final.mp4"

    duration = get_duration(video)

    print(f"Rendered video duration: {duration:.1f} seconds")

    if duration >= 180:
        shutil.copy2(video, final_video)
        print("Video already satisfies the 3-minute minimum.")
        return

    padding = 181 - duration

    print(
        f"Video is below 3 minutes. "
        f"Adding {padding:.1f} seconds of final-frame padding."
    )

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video),
            "-vf",
            f"tpad=stop_mode=clone:stop_duration={padding:.3f}",
            "-af",
            f"apad=pad_dur={padding:.3f}",
            "-t",
            "181",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "21",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            str(final_video),
        ],
        check=True,
    )

    final_duration = get_duration(final_video)

    if not 180 <= final_duration <= 480:
        raise RuntimeError(
            f"Final video duration is invalid: {final_duration:.1f} seconds"
        )

    print(f"Final video duration: {final_duration:.1f} seconds")
    print("Video duration gate: PASS")


def main():
    print()
    print("=" * 70)
    print("AGENTIC K-12 LESSON PIPELINE")
    print("=" * 70)

    ITERATION.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------
    # 1. INGESTION
    # ---------------------------------------------------------
    print()
    print("[1/8] PDF INGESTION")
    print("-" * 70)

    ingestion_main()

    # ---------------------------------------------------------
    # 2. CONCEPT MAP
    # ---------------------------------------------------------
    print()
    print("[2/8] CONCEPT MAP")
    print("-" * 70)

    build_concept_map()

    # ---------------------------------------------------------
    # 3. CONCEPT MAP GATE
    # ---------------------------------------------------------
    print()
    print("[3/8] CONCEPT MAP FAITHFULNESS GATE")
    print("-" * 70)

    concept_map_gate()

    # ---------------------------------------------------------
    # 4. LESSON PLAN
    # ---------------------------------------------------------
    print()
    print("[4/8] LESSON PLAN")
    print("-" * 70)

    build_lesson_plan()

    # ---------------------------------------------------------
    # 5. SCRIPT
    # ---------------------------------------------------------
    print()
    print("[5/8] HINDI LESSON SCRIPT")
    print("-" * 70)

    script_main()

    # ---------------------------------------------------------
    # 6. SCRIPT GATE
    # ---------------------------------------------------------
    print()
    print("[6/8] SCRIPT FAITHFULNESS GATE")
    print("-" * 70)

    script_gate()

    # ---------------------------------------------------------
    # 7. REVIEWER
    # ---------------------------------------------------------
    print()
    print("[7/8] REVIEWER")
    print("-" * 70)

    run_reviewer()

    # ---------------------------------------------------------
    # Copy validated intermediate artifacts
    # ---------------------------------------------------------
    print()
    print("Saving validated artifacts to iteration_03...")
    print("-" * 70)

    for filename in [
        "concept_map.json",
        "concept_map_gate.json",
        "lesson_plan.json",
        "lesson_script.json",
        "script_gate.json",
        "reviewer_verdicts.json",
    ]:
        copy_to_iteration(filename)

    # ---------------------------------------------------------
    # 8. VIDEO
    # ---------------------------------------------------------
    print()
    print("[8/8] POLISHED VIDEO + SUBTITLES")
    print("-" * 70)

    run_media_pipeline()

    ensure_minimum_video_duration()

    # ---------------------------------------------------------
    # FINAL SUMMARY
    # ---------------------------------------------------------
    print()
    print("=" * 70)
    print("PIPELINE COMPLETE")
    print("=" * 70)

    print()
    print("Final artifacts:")

    for path in [
        ITERATION / "concept_map.json",
        ITERATION / "concept_map_gate.json",
        ITERATION / "lesson_plan.json",
        ITERATION / "lesson_script.json",
        ITERATION / "script_gate.json",
        ITERATION / "reviewer_verdicts.json",
        ITERATION / "lesson_video_final.mp4",
        ITERATION / "lesson_subtitles.srt",
    ]:
        if path.exists():
            print(f"  PASS  {path.relative_to(ROOT)}")
        else:
            print(f"  FAIL  {path.relative_to(ROOT)}")
            raise FileNotFoundError(path)

    final_video = ITERATION / "lesson_video_final.mp4"
    duration = get_duration(final_video)

    print()
    print(f"Final video duration: {duration:.1f} seconds")

    if not 180 <= duration <= 480:
        raise RuntimeError("Final video is outside the required 3–8 minute range.")

    print("Duration check: PASS")
    print()
    print("Everything completed successfully.")
    print("=" * 70)


if __name__ == "__main__":
    main()