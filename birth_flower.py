import argparse
import math
import os
from pathlib import Path

import imageio
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps


DESIGN_SIZE = (360, 640)
RENDER_SCALE = 3
FRAME_SIZE = (DESIGN_SIZE[0] * RENDER_SCALE, DESIGN_SIZE[1] * RENDER_SCALE)
FPS = 30
DURATION_SECONDS = 24
CODE_LINES = [
    "# birth_flower.py",
    "from particle_assemble import render",
    "",
    'DATE = "November 11"',
    'FLOWER = "Cotton Rose"',
    'MEANING = "Delicate Beauty"',
    "",
    'render("Cotton Rose.png", "Cotton Rose_anim.mp4",',
    '       mode="grow", rough=0.7, thresh=10)',
    'print(f"{DATE} - Happy Birthday Safiya!")',
    'print(f"Birth Flower: {FLOWER} ({MEANING})")',
]


class _ScaledDraw:
    def __init__(self, image: Image.Image) -> None:
        self._draw = ImageDraw.Draw(image)

    def text(self, xy, text, *, font, fill):
        x, y = xy
        self._draw.text(
            (round(x * RENDER_SCALE), round(y * RENDER_SCALE)),
            text,
            font=font,
            fill=fill,
        )

    def textbbox(self, xy, text, *, font):
        x, y = xy
        bounds = self._draw.textbbox(
            (round(x * RENDER_SCALE), round(y * RENDER_SCALE)),
            text,
            font=font,
        )
        return tuple(round(value / RENDER_SCALE) for value in bounds)

    def rectangle(self, xy, *, fill):
        self._draw.rectangle(_scale_box(xy), fill=fill)

    def ellipse(self, xy, *, fill):
        self._draw.ellipse(_scale_box(xy), fill=fill)

    def rounded_rectangle(self, xy, *, radius, fill):
        self._draw.rounded_rectangle(
            _scale_box(xy),
            radius=round(radius * RENDER_SCALE),
            fill=fill,
        )


def _scale_box(box):
    return tuple(round(value * RENDER_SCALE) for value in box)


def _pick_font(size: int, *, mono: bool = False, serif: bool = False) -> ImageFont.ImageFont:
    if mono:
        candidates = ["C:/Windows/Fonts/consola.ttf", "C:/Windows/Fonts/cour.ttf"]
    elif serif:
        candidates = ["C:/Windows/Fonts/georgiab.ttf", "C:/Windows/Fonts/timesbd.ttf"]
    else:
        candidates = ["C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/calibri.ttf"]
    for candidate in candidates:
        if os.path.exists(candidate):
            return ImageFont.truetype(candidate, size=size * RENDER_SCALE)
    return ImageFont.load_default()


def _clamp(value: float) -> float:
    return min(1.0, max(0.0, value))


def _smooth(value: float) -> float:
    value = _clamp(value)
    return value * value * (3 - 2 * value)


def load_flower_image(source_path: Path) -> Image.Image:
    if not source_path.is_file():
        raise FileNotFoundError(f"Flower image not found: {source_path}")
    return Image.open(source_path).convert("RGBA")


def _draw_code_editor(frame: Image.Image, elapsed: float) -> None:
    draw = _ScaledDraw(frame)
    draw.rectangle((0, 60, 360, 204), fill=(24, 24, 24))
    draw.rectangle((0, 60, 360, 80), fill=(39, 39, 39))
    draw.ellipse((9, 67, 16, 74), fill=(246, 91, 73))
    draw.ellipse((20, 67, 27, 74), fill=(245, 180, 65))
    draw.ellipse((31, 67, 38, 74), fill=(64, 190, 113))
    draw.rectangle((48, 62, 126, 79), fill=(29, 29, 29))
    draw.text((53, 65), "birth_flower.py", font=_pick_font(8), fill=(224, 224, 224))

    running = elapsed >= 3.2 and elapsed < 18.2
    button_color = (28, 155, 106) if not running else (65, 65, 65)
    draw.rounded_rectangle((291, 64, 350, 77), radius=3, fill=button_color)
    draw.text((302, 66), "■ Stop" if running else "▶ Run", font=_pick_font(7), fill=(242, 242, 242))

    font = _pick_font(8, mono=True)
    visible = min(len(CODE_LINES), max(1, int(max(0, elapsed - 0.3) / 0.24) + 1))
    for index, code in enumerate(CODE_LINES[:visible]):
        y = 84 + index * 10
        draw.text((12, y), str(index + 1), font=font, fill=(104, 112, 124))
        color = (205, 206, 211)
        if code.startswith(("DATE", "FLOWER", "MEANING")):
            color = (144, 189, 221)
        elif code.startswith("from "):
            color = (196, 159, 209)
        elif code.startswith("render("):
            color = (223, 200, 145)
        draw.text((32, y), code, font=font, fill=color)


def _draw_console(frame: Image.Image, elapsed: float, progress: float) -> None:
    draw = _ScaledDraw(frame)
    draw.rectangle((0, 204, 360, 231), fill=(18, 18, 18))
    font = _pick_font(7, mono=True)
    if elapsed < 3.2:
        return
    draw.text((5, 207), "$ .venv\\Scripts\\python.exe birth_flower.py", font=font, fill=(212, 212, 212))
    draw.text(
        (5, 216),
        "points 925,065  hairs 59,500  streaks 9,000",
        font=font,
        fill=(191, 191, 191),
    )
    draw.text((5, 224), "rendering", font=font, fill=(211, 211, 211))
    draw.rectangle((45, 224, 177, 229), fill=(48, 48, 48))
    draw.rectangle((45, 224, 45 + int(132 * progress), 229), fill=(73, 163, 221))
    draw.text((182, 222), f"{int(progress * 100):>3}%   {progress * 12:.1f}s", font=font, fill=(198, 198, 198))


def _draw_metric(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    label: str,
    value: str,
) -> None:
    draw.text((x, y), label, font=_pick_font(6), fill=(154, 154, 154))
    draw.text((x, y + 8), value, font=_pick_font(9), fill=(238, 238, 238))


def _draw_render_panel(
    frame: Image.Image,
    flower_image: Image.Image,
    elapsed: float,
    flower_name: str,
    meaning: str,
    date_text: str,
) -> None:
    panel_progress = _smooth((elapsed - 5.2) / 1.1)
    if panel_progress <= 0:
        return
    panel = Image.new("RGBA", FRAME_SIZE, (0, 0, 0, 0))
    draw = _ScaledDraw(panel)
    draw.rounded_rectangle((13, 244, 348, 537), radius=6, fill=(39, 39, 41, int(255 * panel_progress)))
    draw.rectangle((15, 258, 346, 269), fill=(32, 32, 33, int(255 * panel_progress)))
    draw.text((142, 260), "particles — preview", font=_pick_font(7), fill=(194, 194, 194, int(255 * panel_progress)))
    draw.ellipse((316, 263, 321, 268), fill=(242, 165, 77, int(255 * panel_progress)))
    draw.text((324, 260), "running" if elapsed < 18.2 else "done", font=_pick_font(5), fill=(224, 224, 224, int(255 * panel_progress)))

    _draw_metric(draw, 22, 277, "IMAGE", "Cotton Rose.png")
    _draw_metric(draw, 22, 309, "MOTION", "grow")
    _draw_metric(draw, 22, 341, "WIND", "0")
    _draw_metric(draw, 22, 373, "ROUGH", "0.7")
    _draw_metric(draw, 22, 405, "THRESH", "10")

    _draw_metric(draw, 265, 277, "POINTS", "0.93M")
    _draw_metric(draw, 265, 309, "HAIRS", "60k")
    frame_number = min(308, int(_smooth((elapsed - 6.0) / 11.5) * 308))
    _draw_metric(draw, 265, 341, "FRAME", f"{frame_number} / 308")
    _draw_metric(draw, 265, 373, "TIME", f"{_smooth((elapsed - 6) / 11.5) * 12:.1f}s")
    _draw_metric(draw, 265, 405, "FPS", "25.6")

    draw.rectangle((101, 270, 259, 529), fill=(0, 0, 0))
    title = "HAPPY BIRTHDAY" if elapsed >= 13.8 else "YOUR BIRTH FLOWER"
    title_font = _pick_font(6)
    title_width = draw.textbbox((0, 0), title, font=title_font)[2]
    draw.text(((360 - title_width) // 2, 281), title, font=title_font, fill=(225, 222, 230))
    subtitle_font = _pick_font(5)
    subtitle = date_text.upper()
    subtitle_width = draw.textbbox((0, 0), subtitle, font=subtitle_font)[2]
    draw.text(((360 - subtitle_width) // 2, 292), subtitle, font=subtitle_font, fill=(188, 184, 197))

    flower_progress = _smooth((elapsed - 7.0) / 8.6)
    if flower_progress > 0:
        max_size = (138 * RENDER_SCALE, 187 * RENDER_SCALE)
        flower = ImageOps.contain(flower_image, max_size, Image.Resampling.LANCZOS)
        target_width = max(1, int(flower.width * (0.28 + 0.72 * flower_progress)))
        target_height = max(1, int(flower.height * (0.28 + 0.72 * flower_progress)))
        flower = flower.resize((target_width, target_height), Image.Resampling.LANCZOS)
        if flower_progress < 0.99:
            alpha = flower.getchannel("A")
            alpha = alpha.point(lambda value: int(value * min(1, flower_progress * 1.7)))
            flower.putalpha(alpha)
        top = round((315 + 34 * (1 - flower_progress)) * RENDER_SCALE)
        panel.alpha_composite(flower, (FRAME_SIZE[0] // 2 - flower.width // 2, top))

    if elapsed >= 14:
        name_font = _pick_font(15, serif=True)
        name_width = draw.textbbox((0, 0), flower_name, font=name_font)[2]
        draw.text(((360 - name_width) // 2, 495), flower_name, font=name_font, fill=(246, 243, 250))
        meaning_font = _pick_font(6, serif=True)
        meaning_width = draw.textbbox((0, 0), meaning, font=meaning_font)[2]
        draw.text(((360 - meaning_width) // 2, 513), meaning, font=meaning_font, fill=(230, 224, 235))

    if elapsed >= 14.5:
        for index in range(34):
            phase = (elapsed * (0.17 + index % 4 * 0.025) + index * 0.31) % 1
            x = 106 + (index * 47 + int(phase * 23)) % 148
            y = 302 + int(phase * 207)
            radius = 1 if index % 4 else 2
            color = (255, 227, 188, 210) if index % 2 else (248, 177, 198, 195)
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)

    frame.alpha_composite(panel)


def build_frame(
    flower_image: Image.Image,
    elapsed: float,
    name: str,
    flower_name: str,
    meaning: str,
    date_text: str,
) -> Image.Image:
    frame = Image.new("RGBA", FRAME_SIZE, (27, 27, 28, 255))
    _draw_code_editor(frame, elapsed)
    render_progress = _smooth((elapsed - 3.2) / 14.8)
    _draw_console(frame, elapsed, render_progress)
    _draw_render_panel(frame, flower_image, elapsed, flower_name, meaning, date_text)

    if elapsed >= 20:
        fade = _smooth((elapsed - 20) / 2.8)
        overlay = Image.new("RGBA", FRAME_SIZE, (0, 0, 0, int(210 * fade)))
        frame.alpha_composite(overlay)
        if elapsed >= 21:
            draw = _ScaledDraw(frame)
            font = _pick_font(15, serif=True)
            greeting = f"Happy Birthday {name}!"
            width = draw.textbbox((0, 0), greeting, font=font)[2]
            draw.text(((360 - width) // 2, 317), greeting, font=font, fill=(245, 235, 243, int(255 * fade)))
            smaller = _pick_font(8)
            subline = f"{flower_name}  •  {meaning}"
            subwidth = draw.textbbox((0, 0), subline, font=smaller)[2]
            draw.text(((360 - subwidth) // 2, 338), subline, font=smaller, fill=(230, 211, 173, int(255 * fade)))

    return frame.convert("RGB")


def render_birthday_video(
    output_path: Path,
    source_path: Path,
    name: str,
    flower_name: str,
    meaning: str,
    date_text: str,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    flower_image = load_flower_image(source_path)
    writer = imageio.get_writer(
        output_path,
        format="FFMPEG",
        fps=FPS,
        codec="libx264",
        quality=9,
        pixelformat="yuv420p",
        macro_block_size=1,
    )
    try:
        for frame_index in range(FPS * DURATION_SECONDS):
            frame = build_frame(
                flower_image,
                frame_index / FPS,
                name,
                flower_name,
                meaning,
                date_text,
            )
            writer.append_data(np.asarray(frame))
    finally:
        writer.close()

    print(f"Created birthday animation at: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a reference-style birthday flower video.")
    parser.add_argument("--name", default="Safiya")
    parser.add_argument("--image", default="Cotton Rose.png")
    parser.add_argument("--flower", default="Cotton Rose")
    parser.add_argument("--meaning", default="Delicate Beauty")
    parser.add_argument("--date", default="November 11")
    parser.add_argument("--output", default="Cotton Rose_anim.mp4")
    args = parser.parse_args()

    render_birthday_video(
        Path(args.output),
        Path(args.image),
        args.name,
        args.flower,
        args.meaning,
        args.date,
    )


if __name__ == "__main__":
    main()
