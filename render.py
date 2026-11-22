#!/usr/bin/env python3
"""Render the 22 November 2026 front page from stories.json.

Layout learned from the top entries of the 18/19 Nov contests: a huge
serif date for the masthead, a coloured region bar, a big-numbers
strip, three lead stories each with a flat drawn picture, six smaller
picture cards, a world map with numbered pins next to numbered
one-line briefs, and a DATE CHECK box at the foot. The stories
themselves are the date-verified ones in stories.json — only the
presentation changed. No clock, no randomness, no network, so every
run writes identical bytes. Usage: python3 render.py [out-path]
(default entry.png beside this file).
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "stories.json")

PAGE = 1024
EDGE = 26
INNER = PAGE - 2 * EDGE

CREAM = (248, 244, 232)
BLACK = (20, 20, 20)
DIM = (70, 68, 62)
FAINT = (205, 200, 185)
CRIMSON = (176, 30, 36)
LEAF = (28, 88, 58)
SEA = (196, 218, 228)
SAND = (212, 196, 162)
SANDLINE = (148, 138, 118)
INKNAVY = (16, 30, 58)

FONTDIR = "/usr/share/fonts/truetype/dejavu"


def load(name, size):
    return ImageFont.truetype(os.path.join(FONTDIR, name), size)


def fit_lines(d, text, font, width, limit):
    """Greedy wrap; truncate with an ellipsis if over the limit."""
    out, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=font) <= width:
            cur = trial
        else:
            if cur:
                out.append(cur)
            cur = word
            if len(out) == limit:
                break
    if cur and len(out) < limit:
        out.append(cur)
    if len(out) == limit and out and len(" ".join(out)) < len(text):
        last = out[-1]
        while last and d.textlength(last + "…", font=font) > width:
            last = last.rsplit(" ", 1)[0] if " " in last else ""
        out[-1] = (last + "…") if last else "…"
    return out


def hline(d, x0, y, x1, w=1, colour=BLACK):
    d.line([(x0, y), (x1, y)], fill=colour, width=w)


# ------------------------------------------------------------ pictograms
def _tag(d, box, word):
    x0, y0, _, _ = box
    f = load("DejaVuSans-Bold.ttf", 10)
    tw = d.textlength(word, font=f)
    d.rectangle([x0, y0, x0 + tw + 12, y0 + 16], fill=(20, 20, 20))
    d.text((x0 + 6, y0 + 2), word, font=f, fill=(255, 255, 255))


def _burst(d, cx, cy, r, colour):
    import math
    pts = []
    for k in range(16):
        a = k * math.pi / 8
        rr = r if k % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=colour)


def ship_pic(d, box, word):
    x0, y0, x1, y1 = box
    h = y1 - y0
    wl = y0 + int(h * 0.52)
    d.rectangle([x0, y0, x1, wl], fill=(212, 226, 236))
    d.rectangle([x0, wl, x1, y1], fill=(166, 194, 214))
    _burst(d, x0 + int((x1 - x0) * 0.78), y0 + int(h * 0.20),
           max(8, int(h * 0.10)), CRIMSON)
    d.polygon([(x0 + 14, wl), (x1 - 14, wl), (x1 - 28, wl + int(h * 0.22)),
               (x0 + 28, wl + int(h * 0.22))], fill=(38, 46, 56))
    for i, c in enumerate([(176, 30, 36), (28, 76, 156), (198, 158, 38)]):
        bx = x0 + 24 + i * 50
        d.rectangle([bx, wl - int(h * 0.20), bx + 44, wl - 1], fill=c,
                    outline=(20, 20, 20), width=1)
    d.rectangle([x0 + 148, wl - int(h * 0.26), x0 + 162, wl - 1],
                fill=(20, 20, 20))
    _tag(d, box, word)


def drones_pic(d, box, word):
    x0, y0, x1, y1 = box
    h = y1 - y0
    d.rectangle(box, fill=INKNAVY)
    for sx, sy in [(18, 10), (54, 20), (98, 8), (142, 16), (72, 32), (122, 38)]:
        if sy < h - 4:
            d.ellipse([x0 + sx - 1, y0 + sy - 1, x0 + sx + 1, y0 + sy + 1],
                      fill=(255, 255, 255))
    d.polygon([(x0 + 22, y1), (x0 + 62, y0 + int(h * 0.30)), (x0 + 86, y1)],
              fill=(68, 88, 138))
    d.polygon([(x1 - 26, y1), (x1 - 68, y0 + int(h * 0.34)), (x1 - 92, y1)],
              fill=(68, 88, 138))
    for dx, dy in [(42, 44), (82, 36), (120, 48)]:
        if dy > h - 12:
            continue
        cx, cy = x0 + dx, y0 + dy
        d.ellipse([cx - 10, cy - 5, cx + 10, cy + 5], fill=(150, 155, 175))
        d.line([(cx - 14, cy - 6), (cx + 14, cy - 6)], fill=(240, 240, 240),
               width=2)
        d.line([(cx - 14, cy + 6), (cx + 14, cy + 6)], fill=(240, 240, 240),
               width=2)
    for bx in range(x0 + 8, x1 - 8, 18):
        d.rectangle([bx, y1 - 14, bx + 10, y1 - 5], fill=(38, 38, 58))
        d.rectangle([bx + 3, y1 - 11, bx + 7, y1 - 8], fill=(238, 198, 58))
    _tag(d, box, word)


def flags_pic(d, box, word):
    x0, y0, x1, y1 = box
    h = y1 - y0
    d.rectangle(box, fill=(220, 226, 233))
    for i, px in enumerate([x0 + 16, x0 + 68, x0 + 120]):
        top = y0 + (10 if i == 1 else 16)
        d.line([(px, top), (px, y0 + int(h * 0.62))], fill=(78, 68, 58), width=2)
        if i == 0:
            d.rectangle([px, top, px + 34, top + 20], fill=(255, 255, 255))
            for s in range(4):
                d.rectangle([px, top + s * 5, px + 34, top + s * 5 + 2],
                            fill=(176, 34, 34))
            d.rectangle([px, top, px + 14, top + 10], fill=(28, 58, 118))
        elif i == 1:
            d.rectangle([px, top, px + 34, top + 20], fill=(198, 28, 28))
            d.text((px + 4, top + 3), "★", font=load("DejaVuSans-Bold.ttf", 12),
                   fill=(255, 218, 0))
        else:
            d.rectangle([px, top, px + 34, top + 20], fill=(255, 255, 255))
            d.rectangle([px, top + 7, px + 34, top + 13], fill=(28, 58, 158))
            d.rectangle([px, top + 13, px + 34, top + 20], fill=(198, 28, 28))
    d.rectangle([x0 + 8, y0 + int(h * 0.66), x1 - 8, y0 + int(h * 0.72)],
                fill=(118, 83, 48))
    d.rectangle([x0 + 8, y0 + int(h * 0.72), x1 - 8, y1 - 6],
                fill=(148, 113, 73))
    _tag(d, box, word)


def globe_pic(d, box, word):
    x0, y0, x1, y1 = box
    h = y1 - y0
    d.rectangle(box, fill=(36, 108, 103))
    cx, cy = x0 + 46, (y0 + y1) // 2
    gr = max(15, h // 2 - 4)
    d.ellipse([cx - gr, cy - gr, cx + gr, cy + gr], fill=(68, 138, 198),
              outline=(255, 255, 255), width=2)
    for ox, oy, r in [(-9, -7, 7), (8, 4, 9), (-3, 12, 5)]:
        d.ellipse([cx + ox - r, cy + oy - r, cx + ox + r, cy + oy + r],
                  fill=(88, 178, 88))
    tx = x1 - 18
    d.rounded_rectangle([tx - 5, y0 + 16, tx + 5, y1 - 20], radius=5,
                        fill=(218, 218, 218))
    d.ellipse([tx - 9, y1 - 28, tx + 9, y1 - 10], fill=CRIMSON)
    d.rectangle([tx - 2, y0 + 22, tx + 2, y1 - 20], fill=CRIMSON)
    d.rectangle([x0 + 90, y0 + 16, x1 - 42, y0 + 36], fill=(255, 255, 255))
    d.text((x0 + 94, y0 + 19), "FOSSIL FUELS", font=load("DejaVuSans-Bold.ttf", 10),
           fill=CRIMSON)
    d.line([(x0 + 92, y0 + 27), (x1 - 44, y0 + 27)], fill=CRIMSON, width=2)
    d.text((x0 + 94, y0 + 40), "DEADLOCKED", font=load("DejaVuSans-Bold.ttf", 10),
           fill=(255, 255, 255))
    _tag(d, box, word)


def quake_pic(d, box, word):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(233, 228, 213))
    n = 12
    pts = []
    for i in range(n + 1):
        px = x0 + 10 + i * (x1 - x0 - 20) / n
        py = (y0 + y1) // 2 + (13 if i % 2 == 0 else -13) * (1 if i % 3 else 0.4)
        pts.append((px, py))
    d.line(pts, fill=CRIMSON, width=2, joint="curve")
    d.line([(x0 + 30, y1), (x0 + 60, y1 - 20), (x0 + 55, y1 - 36)],
           fill=(88, 78, 68), width=2)
    d.line([(x1 - 40, y1), (x1 - 70, y1 - 16), (x1 - 62, y1 - 30)],
           fill=(88, 78, 68), width=2)
    d.text((x1 - 46, y0 + 4), "6.7", font=load("DejaVuSans-Bold.ttf", 20),
           fill=BLACK)
    _tag(d, box, word)


def cyclone_pic(d, box, word):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(203, 223, 233))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2 + 4
    for r in (32, 24, 17, 10):
        d.arc([cx - r, cy - r, cx + r, cy + r], start=20, end=300,
              fill=(28, 78, 138), width=3)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(28, 78, 138))
    for dx in (-40, -28, 40, 52):
        d.line([(cx + dx, y0 + 10), (cx + dx - 4, y0 + 20)],
               fill=(88, 128, 168), width=2)
    _tag(d, box, word)


def chart_pic(d, box, word):
    x0, y0, x1, y1 = box
    h = y1 - y0
    d.rectangle(box, fill=(238, 236, 226))
    d.line([(x0 + 10, y0 + 14), (x0 + 10, y1 - 14)], fill=(110, 108, 100), width=1)
    d.line([(x0 + 10, y1 - 14), (x1 - 10, y1 - 14)], fill=(110, 108, 100), width=1)
    pts = [(x0 + 16 + i * (x1 - x0 - 32) / 6, y0 + 20 + i * (h - 40) / 6)
           for i in range(7)]
    d.line(pts, fill=CRIMSON, width=3, joint="curve")
    d.text((x1 - 52, y0 + 6), "−0.1%", font=load("DejaVuSans-Bold.ttf", 14),
           fill=CRIMSON)
    _tag(d, box, word)


def smoke_pic(d, box, word):
    x0, y0, x1, y1 = box
    h = y1 - y0
    d.rectangle(box, fill=(230, 220, 198))
    base = y1 - 4
    d.rectangle([x0 + 12, y0 + int(0.42 * h), x0 + 66, base], fill=(148, 138, 123))
    d.rectangle([x0 + 70, y0 + int(0.60 * h), x0 + 108, base], fill=(168, 158, 143))
    for ox, oy, r in [(120, 14, 8), (132, 6, 10), (118, 24, 6)]:
        if oy < h - 6:
            d.ellipse([x0 + ox - r, y0 + oy - r, x0 + ox + r, y0 + oy + r],
                      fill=(128, 128, 128))
    ty = y0 + int(0.52 * h)
    d.rectangle([x0 + 116, ty, x0 + 156, ty + 16], fill=(255, 255, 255),
                outline=(88, 88, 88), width=1)
    d.rectangle([x0 + 134, ty + 3, x0 + 140, ty + 13], fill=CRIMSON)
    d.rectangle([x0 + 129, ty + 6, x0 + 145, ty + 10], fill=CRIMSON)
    _tag(d, box, word)


PICTURES = {"ship": ship_pic, "drones": drones_pic, "flags": flags_pic,
            "globe": globe_pic, "quake": quake_pic, "cyclone": cyclone_pic,
            "chartdown": chart_pic, "smoke": smoke_pic}

# ------------------------------------------------------------ world map
# Continents as "lon,lat;lon,lat;..." strings, equirectangular.
MAP_SHAPES = [
    "-168,66;-140,70;-125,72;-110,73;-95,80;-85,66;-80,73;-65,60;-55,47;"
    "-60,45;-70,42;-75,35;-80,25;-85,30;-90,21;-97,16;-105,20;-115,30;"
    "-125,40;-125,49;-140,60;-155,58;-165,60",
    "-80,10;-75,5;-60,0;-50,0;-35,-8;-40,-20;-48,-28;-55,-35;-65,-40;"
    "-70,-50;-73,-40;-73,-30;-70,-18;-77,-12;-80,-5",
    "-17,15;-10,30;0,35;10,37;20,32;30,31;35,28;40,15;48,11;51,10;40,0;"
    "35,-18;30,-30;20,-35;15,-27;12,-18;13,-10;9,4;-8,5;-13,8;-17,12",
    "-10,36;-9,43;-2,48;0,50;5,53;8,57;10,59;18,56;21,55;24,58;28,60;"
    "30,62;30,70;25,71;18,69;12,65;5,60;5,58;0,50;-2,44;-5,36",
    "30,70;40,68;55,70;70,72;90,75;110,76;130,72;160,70;178,66;170,60;"
    "162,55;158,50;142,45;140,40;135,35;130,33;127,35;122,38;120,30;"
    "110,20;105,10;100,8;95,15;90,22;85,20;80,13;75,8;72,20;66,25;"
    "60,25;55,26;50,29;48,30;42,35;35,36;30,36",
    "113,-22;114,-30;115,-35;124,-33;129,-32;132,-32;135,-35;140,-38;"
    "145,-38;150,-37;153,-32;153,-27;150,-22;146,-19;142,-15;142,-11;"
    "136,-12;132,-11;130,-13;126,-14;122,-17;118,-20;114,-21",
]


def _project(lon, lat, box):
    x0, y0, x1, y1 = box
    return (x0 + (lon + 180) / 360 * (x1 - x0),
            y0 + (75 - lat) / 130 * (y1 - y0))


def paint_map(d, box, stories):
    d.rectangle(box, fill=SEA, outline=FAINT, width=1)
    for shape in MAP_SHAPES:
        pts = []
        for pair in shape.split(";"):
            lon, lat = pair.split(",")
            pts.append(_project(float(lon), float(lat), box))
        d.polygon(pts, fill=SAND, outline=SANDLINE)
    nf = load("DejaVuSans-Bold.ttf", 9)
    for i, st in enumerate(stories):
        px, py = _project(st["lon"], st["lat"], box)
        px += (i % 3 - 1) * 4
        py += ((i // 3) % 2) * 4 - 2
        if st["tier"] in ("lead", "card"):
            d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=CRIMSON,
                      outline=(255, 255, 255), width=1)
            d.text((px, py - 5), str(i + 1), font=nf, fill=(255, 255, 255),
                   anchor="ma")
        else:
            d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(88, 88, 88))


# ------------------------------------------------------------ story blocks
def source_badge(d, x, y, source, width):
    f = load("DejaVuSans-Bold.ttf", 9)
    word = ("CONFIRMED · " + source) if source != "Reported" else "REPORTED"
    bw = d.textlength(word, font=f) + 10
    bx = x + width - bw
    d.rounded_rectangle([bx, y, bx + bw, y + 16], radius=3,
                        fill=LEAF if source != "Reported" else (110, 108, 100))
    d.text((bx + 5, y + 2), word, font=f, fill=(255, 255, 255))
    return bx


def number_tag(d, x, y, n, place, source, width):
    d.ellipse([x, y - 1, x + 18, y + 17], fill=CRIMSON)
    d.text((x + 9, y + 1), str(n), font=load("DejaVuSans-Bold.ttf", 11),
           fill=(255, 255, 255), anchor="ma")
    d.text((x + 23, y + 1), place, font=load("DejaVuSans-Bold.ttf", 11),
           fill=BLACK)
    source_badge(d, x, y, source, width)
    return y + 20


def lead_block(d, st, n, x, y, w):
    PICTURES[st["pic"]](d, (x, y, x + w, y + 102), st["place"])
    y += 108
    y = number_tag(d, x, y, n, st["place"], st["source"], w)
    yy = y
    hf = load("DejaVuSerif-Bold.ttf", 22)
    for ln in fit_lines(d, st["headline"], hf, w, 3):
        d.text((x, yy), ln, font=hf, fill=BLACK)
        yy += 26
    df = load("DejaVuSans.ttf", 13)
    for ln in fit_lines(d, st["deck"], df, w, 3):
        d.text((x, yy + 2), ln, font=df, fill=DIM)
        yy += 17
    return yy + 4


def card_block(d, st, n, x, y, w):
    PICTURES[st["pic"]](d, (x, y, x + w, y + 52), st["place"])
    y += 57
    y = number_tag(d, x, y, n, st["place"], st["source"], w)
    yy = y
    hf = load("DejaVuSans-Bold.ttf", 15)
    for ln in fit_lines(d, st["headline"], hf, w, 2):
        d.text((x, yy), ln, font=hf, fill=BLACK)
        yy += 18
    df = load("DejaVuSans.ttf", 12)
    for ln in fit_lines(d, st["deck"], df, w, 2):
        d.text((x, yy), ln, font=df, fill=DIM)
        yy += 15
    return yy + 4


def brief_line(d, st, n, x, y, w):
    nf = load("DejaVuSans-Bold.ttf", 10)
    tf = load("DejaVuSans.ttf", 10)
    d.text((x, y), str(n), font=nf, fill=CRIMSON)
    nx = x + d.textlength(str(n) + " ", font=nf)
    lines = fit_lines(d, f"{st['place']}: {st['headline']}", tf, w - (nx - x), 1)
    d.text((nx, y), lines[0] if lines else "", font=tf, fill=BLACK)
    return y + 14


# ------------------------------------------------------------ page assembly
def build(data):
    img = Image.new("RGB", (PAGE, PAGE), CREAM)
    d = ImageDraw.Draw(img)
    y = 8
    kf = load("DejaVuSans-Bold.ttf", 11)
    d.text((EDGE, y), data["kicker_left"], font=kf, fill=CRIMSON)
    rw = d.textlength(data["kicker_right"], font=kf)
    d.text((PAGE - EDGE - rw, y), data["kicker_right"], font=kf, fill=BLACK)

    size = 84
    while size > 48:
        df = load("DejaVuSerif-Bold.ttf", size)
        if d.textlength(data["date"], font=df) <= INNER:
            break
        size -= 2
    d.text((PAGE // 2, 26), data["date"], font=df, fill=BLACK, anchor="ma")
    y = 26 + size + 6
    d.text((PAGE // 2, y), data["subdeck"], font=load("DejaVuSerif.ttf", 15),
           fill=CRIMSON, anchor="ma")
    y += 22
    hline(d, EDGE, y, PAGE - EDGE, 2)
    hline(d, EDGE, y + 4, PAGE - EDGE, 1)
    y += 10

    total = sum(c for _, c, _ in data["regions"])
    x = EDGE
    rf = load("DejaVuSans-Bold.ttf", 10)
    for name, count, colour in data["regions"]:
        seg = INNER * count / total
        d.rectangle([x, y, x + seg - 1, y + 20], fill=colour)
        lab = f"{name} {count}"
        if d.textlength(lab, font=rf) <= seg - 8:
            d.text((x + seg / 2, y + 4), lab, font=rf, fill=(255, 255, 255),
                   anchor="ma")
        x += seg
    y += 26

    d.text((EDGE, y), "THE DAY IN NUMBERS",
           font=load("DejaVuSans-Bold.ttf", 10), fill=CRIMSON)
    y += 14
    bf = load("DejaVuSans-Bold.ttf", 24)
    cf = load("DejaVuSans.ttf", 10)
    cw = INNER / len(data["numbers"])
    for i, (big, cap) in enumerate(data["numbers"]):
        cx = EDGE + i * cw
        d.text((cx + 4, y), big, font=bf, fill=CRIMSON)
        d.text((cx + 4, y + 27), cap, font=cf, fill=DIM)
        if i:
            d.line([(cx, y), (cx, y + 40)], fill=FAINT, width=1)
    y += 40
    hline(d, EDGE, y, PAGE - EDGE, 1)
    y += 8

    colw = (INNER - 2 * 18) // 3
    bottom = y
    for i, st in enumerate(data["leads"]):
        b = lead_block(d, st, i + 1, EDGE + i * (colw + 18), y, colw)
        bottom = max(bottom, b)
    y = bottom + 8
    hline(d, EDGE, y, PAGE - EDGE, 1)
    y += 8
    card_end = y
    for r in range(2):
        for c in range(3):
            st = data["cards"][r * 3 + c]
            b = card_block(d, st, 4 + r * 3 + c, EDGE + c * (colw + 18),
                           y + r * 148, colw)
            card_end = max(card_end, b)
    y = card_end + 6

    sf = load("DejaVuSans-Bold.ttf", 13)
    d.text((EDGE, y), "WHERE IT HAPPENED", font=sf, fill=CRIMSON)
    brief_x = EDGE + 312
    d.text((brief_x, y), "ALSO ON " + data["date"].upper(), font=sf, fill=CRIMSON)
    y += 18
    map_h = 150
    everything = data["leads"] + data["cards"] + data["briefs"]
    paint_map(d, (EDGE, y, EDGE + 296, y + map_h), everything)
    d.text((EDGE, y + map_h + 4), "Red numbers = pictured stories 1–9 · dots = briefs",
           font=load("DejaVuSans.ttf", 10), fill=(110, 108, 100))
    briefs = data["briefs"]
    half = (len(briefs) + 1) // 2
    bw = (PAGE - EDGE - brief_x - 16) // 2
    for i, st in enumerate(briefs[:half]):
        brief_line(d, st, 10 + i, brief_x, y + i * 14, bw)
    for i, st in enumerate(briefs[half:]):
        brief_line(d, st, 10 + half + i, brief_x + bw + 16, y + i * 14, bw)
    y = y + map_h + 22

    d.rectangle([EDGE, y, PAGE - EDGE, y + 44], outline=CRIMSON, width=2)
    d.text((EDGE + 8, y + 5), "DATE CHECK",
           font=load("DejaVuSans-Bold.ttf", 11), fill=CRIMSON)
    tx = EDGE + 8 + d.textlength("DATE CHECK  ",
                                 font=load("DejaVuSans-Bold.ttf", 11))
    yy = y + 5
    for ln in fit_lines(d, data["datecheck"], load("DejaVuSans.ttf", 11),
                        PAGE - EDGE - 8 - tx, 3):
        d.text((tx, yy), ln, font=load("DejaVuSans.ttf", 11), fill=BLACK)
        yy += 13
    y += 48
    d.text((PAGE // 2, y), data["footer"], font=load("DejaVuSans.ttf", 11),
           fill=(110, 108, 100), anchor="ma")
    print("final y:", y, "(limit 998)")
    return img


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "entry.png")
    with open(DATA, encoding="utf-8") as fh:
        data = json.load(fh)
    img = build(data)
    img.save(out, format="PNG", optimize=True)
    print(f"wrote {out} ({os.path.getsize(out)} bytes)")


if __name__ == "__main__":
    main()
