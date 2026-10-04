import asyncio
import json
import os
import subprocess
from pathlib import Path

import edge_tts
import fitz
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
ITERATION = os.environ.get("K12_ITERATION", "iteration_03")
OUTPUT = ROOT / "outputs" / ITERATION
MEDIA = OUTPUT / "media_polished"
SCRIPT = OUTPUT / "lesson_script.json"

VOICE = "hi-IN-SwaraNeural"
WIDTH, HEIGHT = 1280, 720
VISUAL_HOLD = 2.8

MEDIA.mkdir(parents=True, exist_ok=True)

# ---------- Fonts ----------
# The pipeline automatically downloads a known-good Devanagari font if
# Windows does not already have one. This removes the need for manual font setup.
import urllib.request

FONT_DIR = ROOT / "fonts"
FONT_DIR.mkdir(parents=True, exist_ok=True)
REGULAR_FONT_PATH = FONT_DIR / "NotoSansDevanagari-Regular.ttf"
BOLD_FONT_PATH = FONT_DIR / "NotoSansDevanagari-Bold.ttf"

FONT_URLS = {
    REGULAR_FONT_PATH: (
        "https://raw.githubusercontent.com/notofonts/noto-fonts/main/"
        "hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Regular.ttf"
    ),
    BOLD_FONT_PATH: (
        "https://raw.githubusercontent.com/notofonts/noto-fonts/main/"
        "hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Bold.ttf"
    ),
}

def download_font_if_missing(path, url):
    if path.exists() and path.stat().st_size > 50000:
        return True
    print(f"Hindi font missing. Downloading: {path.name}")
    try:
        urllib.request.urlretrieve(url, str(path))
        if path.exists() and path.stat().st_size > 50000:
            print(f"Downloaded: {path}")
            return True
    except Exception as exc:
        print(f"Could not download {path.name}: {exc}")
    return False

# Prefer the project-local font so the same rendering works on every machine.
regular_ok = download_font_if_missing(REGULAR_FONT_PATH, FONT_URLS[REGULAR_FONT_PATH])
bold_ok = download_font_if_missing(BOLD_FONT_PATH, FONT_URLS[BOLD_FONT_PATH])

# Windows fallback names, in case a suitable font is already installed.
WINDOWS_REGULAR = [
    r"C:\Windows\Fonts\NirmalaUI.ttf",
    r"C:\Windows\Fonts\Nirmala.ttf",
    r"C:\Windows\Fonts\mangal.ttf",
    r"C:\Windows\Fonts\NotoSansDevanagari-Regular.ttf",
]
WINDOWS_BOLD = [
    r"C:\Windows\Fonts\NirmalaUI-Bold.ttf",
    r"C:\Windows\Fonts\Nirmala-Bold.ttf",
    r"C:\Windows\Fonts\mangalb.ttf",
    r"C:\Windows\Fonts\NotoSansDevanagari-Bold.ttf",
]

def first_existing(paths):
    for p in paths:
        if Path(p).exists():
            return p
    return None

REGULAR = str(REGULAR_FONT_PATH) if regular_ok else first_existing(WINDOWS_REGULAR)
BOLD = str(BOLD_FONT_PATH) if bold_ok else first_existing(WINDOWS_BOLD) or REGULAR

if not REGULAR:
    raise RuntimeError(
        "Hindi font setup failed. Internet access was unavailable and no "
        "Devanagari font was found. Please run once with internet access, "
        "or put NotoSansDevanagari-Regular.ttf inside the project's fonts/ folder."
    )

# Pillow must have complex-text shaping support for correct Devanagari joining.
try:
    if not ImageFont.core.has_layout_engine():
        print("WARNING: Pillow was built without advanced text shaping. "
              "Hindi may not join correctly. Reinstall Pillow in the venv if needed.")
except Exception:
    pass

print(f"Hindi regular font: {REGULAR}")
print(f"Hindi bold font:    {BOLD}")

def font(size, bold=False):
    return ImageFont.truetype(BOLD if bold else REGULAR, size)

# ---------- Helpers ----------
def run(cmd):
    print(">", " ".join(map(str, cmd)))
    subprocess.run(cmd, check=True)

def ffprobe_duration(path):
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path)
    ], text=True).strip()
    return float(out)

def wrap_text(draw, text, fnt, max_width):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        test = word if not cur else cur + " " + word
        if draw.textbbox((0, 0), test, font=fnt)[2] <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines

def draw_wrapped(draw, text, xy, fnt, fill, max_width, spacing=8):
    x, y = xy
    for line in wrap_text(draw, text, fnt, max_width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += fnt.size + spacing
    return y

def rounded_rect(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

# ---------- Textbook ----------
def textbook_page_image(page_index=5):
    pdf_path = ROOT / "data" / "raw" / "hindi.pdf"
    doc = fitz.open(pdf_path)
    page = doc[page_index]
    pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0), alpha=False)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    doc.close()
    return img

BOOK_PAGE = textbook_page_image()

def fit_cover(img, box_w, box_h):
    ratio = max(box_w / img.width, box_h / img.height)
    nw, nh = int(img.width * ratio), int(img.height * ratio)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - box_w) // 2
    top = (nh - box_h) // 2
    return img.crop((left, top, left + box_w, top + box_h))

# ---------- Concept visuals ----------
def draw_magnet(draw, cx, cy, length=330, height=78, angle=0):
    # Draw on transparent layer so it can rotate.
    layer = Image.new("RGBA", (length + 80, height + 100), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x0, y0 = 40, 50
    d.rounded_rectangle((x0, y0, x0 + length, y0 + height),
                        radius=18, fill=(245, 245, 245), outline=(35, 35, 45), width=3)
    d.rectangle((x0, y0, x0 + length//2, y0 + height), fill=(205, 55, 55))
    d.rectangle((x0 + length//2, y0, x0 + length, y0 + height), fill=(70, 105, 190))
    f = font(34, True)
    d.text((x0 + length//4 - 15, y0 + 18), "N", font=f, fill="white")
    d.text((x0 + 3*length//4 - 15, y0 + 18), "S", font=f, fill="white")
    layer = layer.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
    x = int(cx - layer.width/2)
    y = int(cy - layer.height/2)
    return layer, (x, y)

def paste_magnet(base, angle=0):
    layer, pos = draw_magnet(ImageDraw.Draw(base), WIDTH//2 + 40, 430, angle=angle)
    base.alpha_composite(layer, pos)

def compass_visual(base):
    d = ImageDraw.Draw(base)
    cx, cy, r = 900, 365, 145
    d.ellipse((cx-r, cy-r, cx+r, cy+r), fill=(248,248,248), outline=(40,45,60), width=6)
    d.ellipse((cx-r+18, cy-r+18, cx+r-18, cy+r-18), outline=(150,155,165), width=3)
    # cardinal ticks
    f = font(30, True)
    for label, x, y in [("N",cx-16,cy-r+25),("S",cx-16,cy+r-58),
                        ("E",cx+r-55,cy-18),("W",cx-r+25,cy-18)]:
        d.text((x,y), label, font=f, fill=(45,45,55))
    # needle
    d.polygon([(cx,cy-105),(cx-18,cy+20),(cx,cy+8),(cx+18,cy+20)],
              fill=(205,55,55), outline=(45,45,55))
    d.polygon([(cx,cy+105),(cx-18,cy-20),(cx,cy-8),(cx+18,cy-20)],
              fill=(70,105,190), outline=(45,45,55))
    d.ellipse((cx-10,cy-10,cx+10,cy+10), fill=(45,45,55))

def earth_visual(base):
    d = ImageDraw.Draw(base)
    cx, cy, r = 900, 370, 155
    d.ellipse((cx-r,cy-r,cx+r,cy+r), fill=(215,225,235), outline=(50,60,75), width=5)
    # simple continents, intentionally schematic
    d.ellipse((cx-75,cy-55,cx-5,cy+10), fill=(110,150,105))
    d.ellipse((cx+10,cy-85,cx+75,cy-15), fill=(110,150,105))
    d.ellipse((cx+35,cy+15,cx+90,cy+70), fill=(110,150,105))
    f = font(28, True)
    d.text((cx-18, cy-r-38), "N", font=f, fill=(55,70,100))
    d.text((cx-18, cy+r+8), "S", font=f, fill=(55,70,100))
    d.text((cx-110, cy+190), "पृथ्वी", font=font(32, True), fill=(35,40,50))

def direction_visual(base):
    d = ImageDraw.Draw(base)
    cx, cy = 900, 370
    f = font(34, True)
    d.line((cx,cy,cx,cy-150), fill=(60,80,100), width=7)
    d.polygon([(cx,cy-185),(cx-22,cy-145),(cx+22,cy-145)], fill=(60,80,100))
    d.line((cx,cy,cx+160,cy), fill=(60,80,100), width=7)
    d.polygon([(cx+195,cy),(cx+155,cy-22),(cx+155,cy+22)], fill=(60,80,100))
    d.text((cx-20,cy-225),"उत्तर",font=f,fill=(45,55,70))
    d.text((cx+205,cy-20),"पूर्व",font=f,fill=(45,55,70))
    d.text((cx-20,cy+35),"दक्षिण",font=f,fill=(45,55,70))
    d.text((cx-240,cy-20),"पश्चिम",font=f,fill=(45,55,70))

def make_slide(beat, index, total):
    img = Image.new("RGBA", (WIDTH, HEIGHT), (14, 22, 40, 255))
    d = ImageDraw.Draw(img)

    # header
    d.text((52, 32), "चुंबक से दिशाएँ ज्ञात करना",
           font=font(38, True), fill=(245, 248, 252))
    d.text((1050, 44), f"{index}/{total}",
           font=font(25, True), fill=(180, 190, 205))

    # progress
    d.rounded_rectangle((52, 92, 1228, 100), radius=4, fill=(65, 80, 105))
    d.rounded_rectangle((52, 92, 52 + int(1176*index/total), 100),
                        radius=4, fill=(90, 165, 220))

    # textbook panel
    book_box = (52, 135, 510, 668)
    rounded_rect(d, book_box, 18, (247,248,250), outline=(100,110,125), width=2)
    crop = fit_cover(BOOK_PAGE, 438, 505)
    img.alpha_composite(crop.convert("RGBA"), (87, 158))
    d.text((78, 640), "पाठ्यपुस्तक: मुद्रित पृष्ठ 64",
           font=font(22, True), fill=(40,45,55))

    # right concept card
    rounded_rect(d, (555, 135, 1228, 668), 24, (25, 37, 60), outline=(72, 92, 120), width=2)

    cid = beat.get("concept_id","")
    if cid.endswith("1") or cid.endswith("2"):
        # magnet concept
        layer, pos = draw_magnet(d, 900, 375, angle=0)
        img.alpha_composite(layer, pos)
        d.text((650, 510), "स्वतंत्र रूप से लटका चुंबक",
               font=font(30, True), fill=(225,232,242))
        direction_visual(img)
    elif cid.endswith("3"):
        earth_visual(img)
    elif cid.endswith("4"):
        direction_visual(img)
        d.text((660, 535), "दिशाएँ जानने के लिए चुंबक के गुण का उपयोग",
               font=font(27, True), fill=(225,232,242))
    else:
        compass_visual(img)
        d.text((680, 540), "चुंबकीय दिक्सूचक",
               font=font(32, True), fill=(225,232,242))

    # narration/on-screen card
    rounded_rect(d, (575, 560, 1208, 650), 14, (12,20,35), outline=(65,82,105), width=1)
    on = beat.get("on_screen_text","").strip()
    draw_wrapped(d, on, (600, 578), font(25, True), (248,250,253), 570, spacing=4)

    # source / concept footer
    d.text((575, 665), f"स्रोत: {beat.get('source_page','')}  •  {cid}",
           font=font(20, False), fill=(165,176,195))

    return img.convert("RGB")

async def tts(text, out_path):
    communicate = edge_tts.Communicate(text, VOICE, rate="-8%")
    await communicate.save(str(out_path))

def make_segment(slide_path, audio_path, out_path):
    dur = ffprobe_duration(audio_path) + VISUAL_HOLD
    # Gentle zoom gives motion while preserving the exact slide content.
    vf = (
        f"zoompan=z='min(zoom+0.00035,1.035)':"
        f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"d=1:s={WIDTH}x{HEIGHT}:fps=25,"
        f"fade=t=in:st=0:d=0.35"
    )
    run([
        "ffmpeg","-y",
        "-loop","1","-i",str(slide_path),
        "-i",str(audio_path),
        "-vf",vf,
        "-af","apad",
        "-t",f"{dur:.3f}",
        "-c:v","libx264","-preset","veryfast","-crf","21",
        "-pix_fmt","yuv420p",
        "-c:a","aac","-b:a","160k",
        str(out_path)
    ])

def make_srt(beats, audio_durations):
    lines=[]
    t=0.0
    for i,(beat,dur) in enumerate(zip(beats,audio_durations),1):
        start=t
        end=t+dur
        def ts(x):
            ms=int(round(x*1000))
            h=ms//3600000; ms%=3600000
            m=ms//60000; ms%=60000
            s=ms//1000; ms%=1000
            return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
        lines += [str(i), f"{ts(start)} --> {ts(end)}",
                  beat["narration"].strip(), ""]
        t += dur + VISUAL_HOLD
    (OUTPUT/"lesson_subtitles.srt").write_text("\n".join(lines), encoding="utf-8")

async def main():
    script=json.loads(SCRIPT.read_text(encoding="utf-8"))
    beats=script["beats"]
    print(f"Using font: {REGULAR}")
    print(f"Rendering {len(beats)} beats...")

    durations=[]
    segments=[]

    for i,beat in enumerate(beats,1):
        audio=MEDIA/f"beat_{i:02d}.mp3"
        slide=MEDIA/f"beat_{i:02d}.png"
        seg=MEDIA/f"beat_{i:02d}.mp4"

        await tts(beat["narration"],audio)
        slide_img=make_slide(beat,i,len(beats))
        slide_img.save(slide, quality=95)

        ad=ffprobe_duration(audio)
        durations.append(ad)
        make_segment(slide,audio,seg)
        segments.append(seg)

    make_srt(beats,durations)

    concat=MEDIA/"concat.txt"
    concat.write_text("".join(f"file '{p.as_posix()}'\n" for p in segments), encoding="utf-8")

    final=OUTPUT/"lesson_video_polished.mp4"
    run([
        "ffmpeg","-y","-f","concat","-safe","0","-i",str(concat),
        "-c:v","libx264","-preset","veryfast","-crf","21",
        "-pix_fmt","yuv420p","-c:a","aac","-b:a","160k",
        str(final)
    ])

    print()
    print("DONE")
    print(f"Video: {final}")
    print(f"Subtitles: {OUTPUT/'lesson_subtitles.srt'}")
    print(f"Duration: {ffprobe_duration(final):.1f} sec")

if __name__=="__main__":
    asyncio.run(main())
