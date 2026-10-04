import asyncio
import json
import subprocess
from pathlib import Path

import edge_tts
import fitz
from PIL import Image, ImageDraw, ImageFont

import os

ROOT = Path(__file__).resolve().parent.parent

ITERATION = os.environ.get("K12_ITERATION", "final")

OUTPUT = ROOT / "outputs" / ITERATION
OUTPUT.mkdir(parents=True, exist_ok=True)

MEDIA = OUTPUT / "media"
SCRIPT = OUTPUT / "lesson_script.json"

VOICE = "hi-IN-SwaraNeural"

WIDTH, HEIGHT = 1280, 720

# Extra visual hold after narration.
# 3.5 seconds × 8 beats adds ~28 seconds.
VISUAL_HOLD = 3.5

MEDIA.mkdir(parents=True, exist_ok=True)


def run(command):
    subprocess.run(command, check=True)


def duration_seconds(path):
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path)
        ],
        capture_output=True,
        text=True,
        check=True
    )

    return float(result.stdout.strip())


def timestamp(seconds):
    milliseconds = round(seconds * 1000)

    hours, remainder = divmod(milliseconds, 3600000)
    minutes, remainder = divmod(remainder, 60000)
    secs, millis = divmod(remainder, 1000)

    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"


def find_font():
    candidates = [
        Path("C:/Windows/Fonts/Nirmala.ttf"),
        Path("C:/Windows/Fonts/mangal.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
    ]

    for path in candidates:
        if path.exists():
            return str(path)

    raise FileNotFoundError("No suitable font found.")


FONT_PATH = find_font()


async def generate_audio(beat, index):
    path = MEDIA / f"beat_{index:02}.mp3"

    communicate = edge_tts.Communicate(
        beat["narration"],
        VOICE,
        rate="-10%"
    )

    await communicate.save(str(path))

    return path


def render_textbook_page():
    pdf = fitz.open(ROOT / "data" / "raw" / "hindi.pdf")

    # PDF page 6 corresponds to the relevant textbook section.
    page = pdf[5]

    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))

    path = MEDIA / "textbook_page.png"
    pix.save(str(path))

    pdf.close()

    return path


def make_slide(beat, index, textbook_image):

    canvas = Image.new(
        "RGB",
        (WIDTH, HEIGHT),
        "#101b2b"
    )

    draw = ImageDraw.Draw(canvas)

    title_font = ImageFont.truetype(
        FONT_PATH,
        42
    )

    body_font = ImageFont.truetype(
        FONT_PATH,
        30
    )

    small_font = ImageFont.truetype(
        FONT_PATH,
        23
    )

    draw.text(
        (55, 35),
        "चुंबकों से दिशाएँ जानना",
        font=title_font,
        fill="white"
    )

    source = Image.open(
        textbook_image
    ).convert("RGB")

    source.thumbnail(
        (550, 540)
    )

    x = 55 + (550 - source.width) // 2
    y = 115 + (540 - source.height) // 2

    canvas.paste(
        source,
        (x, y)
    )

    draw.multiline_text(
        (650, 185),
        beat["on_screen_text"],
        font=body_font,
        fill="#ffffff",
        spacing=18
    )

    draw.text(
        (650, 590),
        f"स्रोत: पाठ्यपुस्तक, पृष्ठ {beat['source_page']}",
        font=small_font,
        fill="#c5d5e8"
    )

    path = MEDIA / f"slide_{index:02}.png"

    canvas.save(path)

    return path


async def main():

    print(f"Using iteration: {ITERATION}")
    print(f"Output directory: {OUTPUT}")

    with open(
        SCRIPT,
        encoding="utf-8"
    ) as f:

        script = json.load(f)

    beats = script["beats"]

    textbook_image = render_textbook_page()

    subtitles = []
    segments = []

    elapsed = 0.0

    for index, beat in enumerate(
        beats,
        start=1
    ):

        print(
            f"Processing beat "
            f"{index}/{len(beats)}"
        )

        audio = await generate_audio(
            beat,
            index
        )

        slide = make_slide(
            beat,
            index,
            textbook_image
        )

        audio_duration = duration_seconds(
            audio
        )

        segment_duration = (
            audio_duration
            + VISUAL_HOLD
        )

        segment = (
            MEDIA
            / f"segment_{index:02}.mp4"
        )

        # Generate each segment with a fixed
        # video duration and padded audio.
        run([
            "ffmpeg",
            "-y",

            "-loop",
            "1",

            "-framerate",
            "25",

            "-i",
            str(slide),

            "-i",
            str(audio),

            "-t",
            str(segment_duration),

            "-c:v",
            "libx264",

            "-preset",
            "veryfast",

            "-pix_fmt",
            "yuv420p",

            "-c:a",
            "aac",

            "-ar",
            "44100",

            "-af",
            "apad",

            "-shortest",

            "-movflags",
            "+faststart",

            str(segment)
        ])

        segments.append(segment)

        # Subtitle only covers the actual narration.
        # The remaining VISUAL_HOLD seconds are intentionally
        # silent visual time.
        subtitles.append(
            f"{index}\n"
            f"{timestamp(elapsed)} --> "
            f"{timestamp(elapsed + audio_duration)}\n"
            f"{beat['narration']}\n"
        )

        elapsed += segment_duration

    # --------------------------------------------------
    # Write subtitles
    # --------------------------------------------------

    subtitle_path = (
        OUTPUT
        / "lesson_subtitles.srt"
    )

    subtitle_path.write_text(
        "\n".join(subtitles),
        encoding="utf-8"
    )

    # --------------------------------------------------
    # Create concat file
    # --------------------------------------------------

    concat_file = (
        MEDIA
        / "segments.txt"
    )

    concat_file.write_text(
        "\n".join(
            f"file '{segment.name}'"
            for segment in segments
        ),
        encoding="utf-8"
    )

    final_video = (
        OUTPUT
        / "lesson_video.mp4"
    )

    # --------------------------------------------------
    # Final concatenation
    #
    # Re-encode instead of -c copy.
    # This avoids the non-monotonic DTS problem
    # observed in the previous iteration.
    # --------------------------------------------------

    run([
        "ffmpeg",
        "-y",

        "-f",
        "concat",

        "-safe",
        "0",

        "-i",
        str(concat_file),

        "-c:v",
        "libx264",

        "-preset",
        "medium",

        "-pix_fmt",
        "yuv420p",

        "-c:a",
        "aac",

        "-ar",
        "44100",

        "-movflags",
        "+faststart",

        str(final_video)
    ])

    final_duration = duration_seconds(
        final_video
    )

    print()
    print("MEDIA PIPELINE COMPLETE")
    print(f"Video: {final_video}")
    print(f"Subtitles: {subtitle_path}")
    print(
        f"Duration: "
        f"{final_duration:.1f} seconds"
    )

    if not 180 <= final_duration <= 480:

        print(
            "WARNING: Video is outside the "
            "required 3–8 minute duration."
        )

    else:

        print(
            "PASS: Video duration is within "
            "the required 3–8 minute range."
        )


if __name__ == "__main__":
    asyncio.run(main())