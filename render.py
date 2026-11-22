#!/usr/bin/env python3
"""Draw the 22 November 2026 front page from stories.json.

Pure Pillow drawing: no network, no clock, no randomness, so two runs
produce byte-identical PNGs. Run: python3 render.py [out-path]
Default output is entry.png next to this file.
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "stories.json")

W = H = 1024
MARGIN = 26
PAPER = (248, 244, 232)
INK = (20, 20, 20)
GREY = (110, 108, 100)
FAINT = (205, 200, 185)
RED = (176, 30, 36)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


SERIF_B = font("DejaVuSerif-Bold.ttf", 54)
SANS_B = font("DejaVuSans-Bold.ttf", 17)
SANS = font("DejaVuSans.ttf", 12)
KICK = font("DejaVuSans-Bold.ttf", 13)
HEAD = font("DejaVuSans-Bold.ttf", 15)
DATE_F = font("DejaVuSans-Bold.ttf", 16)
LEAD_H = font("DejaVuSans-Bold.ttf", 30)
LEAD_D = font("DejaVuSans.ttf", 15)
FOOT_F = font("DejaVuSans.ttf", 11)
SECT_F = font("DejaVuSans-Bold.ttf", 14)


def wrap(draw, text, fnt, width):
    """Greedy word wrap measured with the real font; returns lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_tanker(draw, x0, y0, x1, y1):
    """Small flat pictogram: a tanker under a red burst, for the lead."""
    draw.rectangle([x0, y0, x1, y1], outline=FAINT, width=1)
    # sky band
    draw.rectangle([x0 + 1, y0 + 1, x1 - 1, y0 + 34], fill=(214, 228, 238))
    # burst
    cx, cy = (x0 + x1) // 2 + 38, y0 + 26
    for dx, dy in [(0, -12), (9, -8), (12, 0), (9, 8), (0, 12),
                   (-9, 8), (-12, 0), (-9, -8)]:
        draw.line([cx, cy, cx + dx, cy + dy], fill=RED, width=3)
    draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=RED)
    # sea
    draw.rectangle([x0 + 1, y0 + 62, x1 - 1, y1 - 1], fill=(168, 196, 216))
    # hull
    draw.polygon([(x0 + 12, y0 + 62), (x1 - 12, y0 + 62),
                  (x1 - 26, y0 + 84), (x0 + 26, y0 + 84)], fill=(40, 48, 58))
    # containers
    for i, c in enumerate([(176, 30, 36), (29, 78, 158), (200, 160, 40)]):
        bx = x0 + 22 + i * 52
        draw.rectangle([bx, y0 + 40, bx + 46, y0 + 61], fill=c,
                       outline=(20, 20, 20), width=1)
    # funnel with smoke
    draw.rectangle([x0 + 150, y0 + 34, x0 + 164, y0 + 61], fill=(20, 20, 20))
    for r, ox in [(5, -6), (7, -14), (9, -24)]:
        draw.ellipse([x0 + 150 + ox - r, y0 + 30 - r,
                      x0 + 150 + ox + r, y0 + 30 + r],
                     outline=GREY, width=2)
    draw.text((x0 + 8, y1 - 20), "STRAIT OF HORMUZ", font=KICK, fill=INK)


def count_stories(data):
    total = 1  # the lead
    for col in data["columns"]:
        for sec in col["sections"]:
            total += len(sec["stories"])
    return total


def draw_masthead(draw, data):
    y = MARGIN
    draw.text((W // 2, y), data["masthead"], font=SERIF_B, fill=INK,
              anchor="ma")
    y += 74
    left = data["date"].upper()
    right = f"{count_stories(data)} STORIES FROM ONE DAY"
    draw.text((MARGIN, y), left, font=DATE_F, fill=INK)
    tw = draw.textlength(right, font=DATE_F)
    draw.text((W - MARGIN - tw, y), right, font=DATE_F, fill=RED)
    y += 26
    draw.line([MARGIN, y, W - MARGIN, y], fill=INK, width=3)
    draw.line([MARGIN, y + 5, W - MARGIN, y + 5], fill=INK, width=1)
    return y + 12


def draw_lead(draw, lead):
    y = 132
    draw.text((MARGIN, y), lead["kicker"], font=KICK, fill=RED)
    y += 22
    text_w = W - 2 * MARGIN - 216
    lines = wrap(draw, lead["headline"], LEAD_H, text_w)[:2]
    for ln in lines:
        draw.text((MARGIN, y), ln, font=LEAD_H, fill=INK)
        y += 36
    y += 4
    for ln in wrap(draw, lead["deck"], LEAD_D, text_w):
        draw.text((MARGIN, y), ln, font=LEAD_D, fill=(60, 58, 52))
        y += 20
    draw_tanker(draw, W - MARGIN - 196, 132, W - MARGIN, 250)
    return 262


def draw_story(draw, x, y, width, story):
    for ln in wrap(draw, story["headline"], SANS_B, width)[:2]:
        draw.text((x, y), ln, font=SANS_B, fill=INK)
        y += 21
    for ln in wrap(draw, story["deck"], SANS, width)[:2]:
        draw.text((x, y), ln, font=SANS, fill=(70, 68, 62))
        y += 15
    return y + 7


def draw_column(draw, x, width, top, bottom, sections):
    y = top
    for sec in sections:
        draw.text((x, y), sec["name"], font=SECT_F, fill=sec["color"])
        y += 20
        draw.line([x, y, x + width, y], fill=sec["color"], width=2)
        y += 8
        for i, story in enumerate(sec["stories"]):
            y = draw_story(draw, x, y, width, story)
            if i < len(sec["stories"]) - 1:
                draw.line([x, y - 3, x + width, y - 3], fill=FAINT, width=1)
        y += 6
    if y > bottom + 2:
        print(f"WARNING: column at x={x} overflows by {y - bottom}px",
              file=sys.stderr)
    return y


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "entry.png")
    with open(DATA, encoding="utf-8") as fh:
        data = json.load(fh)
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    draw_masthead(draw, data)
    grid_top = draw_lead(draw, data["lead"])
    col_w = (W - 2 * MARGIN - 2 * 18) // 3
    xs = [MARGIN, MARGIN + col_w + 18, MARGIN + 2 * (col_w + 18)]
    for x, col in zip(xs, data["columns"]):
        draw_column(draw, x, col_w, grid_top, 986, col["sections"])
    draw.line([MARGIN, 990, W - MARGIN, 990], fill=INK, width=2)
    draw.text((W // 2, 997), data["footer"], font=FOOT_F, fill=GREY,
              anchor="ma")
    img.save(out, format="PNG")
    print(f"wrote {out} ({os.path.getsize(out)} bytes)")


if __name__ == "__main__":
    main()
