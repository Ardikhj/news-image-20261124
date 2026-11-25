#!/usr/bin/env python3
"""Render the news-image-20261124 entry: one 1024x1024 picture summing up
Tuesday 24 November 2026 as reported that day.

Layout (all drawn with Pillow at build time; the graded program only copies
the finished PNG):
  masthead  - date line, gold rule
  hero      - night-sea scene: Ukraine's naval drones sink the Russian
              corvette Merkury off Benghazi, Libya
  five cards - Gaza, Zaporizhzhia, Nvidia, COP31, US-Iran
  footer    - source line

Every headline below is a fact as reported on 24 Nov 2026 (AP / Reuters /
Middle East Eye / Just Security / Grist). Nothing is invented.
"""
import math
import random

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = "entry.png"

INK = (10, 22, 38)          # deep navy background
PANEL = (18, 35, 61)        # card background
GOLD = (212, 175, 55)
PAPER = (240, 238, 230)
MUTED = (176, 190, 205)
RED = (214, 69, 55)
SKY_TOP = (6, 14, 30)
SEA_TOP = (13, 48, 66)
SEA_BOT = (7, 28, 44)

FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT_R, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, x, y, lines, fnt, fill, leading):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def fit_font(draw, text, size, bold, max_w):
    """Largest bold size at or below `size` that fits `text` in one line."""
    while size > 20:
        fnt = font(size, bold)
        if draw.textlength(text, font=fnt) <= max_w:
            return fnt
        size -= 2
    return font(size, bold)


def vgrad(draw, box, top, bottom):
    x0, y0, x1, y1 = box
    for yy in range(y0, y1):
        t = (yy - y0) / max(1, y1 - y0 - 1)
        col = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        draw.line([(x0, yy), (x1, yy)], fill=col)


def draw_drone(draw, cx, cy, s, light=(255, 80, 60)):
    """Small quadcopter silhouette with a red light."""
    body = (30, 36, 44)
    draw.ellipse([cx - s * 1.25, cy - s * 0.5, cx + s * 1.25, cy + s * 0.5], fill=body)
    for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        ax, ay = cx + dx * s * 1.15, cy + dy * s * 0.5
        draw.ellipse([ax - s * 0.5, ay - s * 0.26, ax + s * 0.5, ay + s * 0.26],
                     outline=(140, 150, 165), width=2)
        draw.line([(cx, cy), (ax, ay)], fill=(140, 150, 165), width=2)
    draw.ellipse([cx - 3, cy + s * 0.55, cx + 3, cy + s * 0.55 + 6], fill=light)


def draw_ship(draw, x0, y_base, scale):
    """Warship silhouette: hull, superstructure, mast, funnel."""
    hull = (76, 88, 102)
    dark = (54, 62, 74)
    pts = [(x0, y_base), (x0 + 330 * scale, y_base),
           (x0 + 300 * scale, y_base + 26 * scale),
           (x0 + 26 * scale, y_base + 26 * scale)]
    draw.polygon(pts, fill=hull)
    draw.rectangle([x0 + 60 * scale, y_base - 34 * scale,
                    x0 + 210 * scale, y_base], fill=dark)
    draw.rectangle([x0 + 96 * scale, y_base - 58 * scale,
                    x0 + 168 * scale, y_base - 34 * scale], fill=hull)
    draw.rectangle([x0 + 220 * scale, y_base - 48 * scale,
                    x0 + 244 * scale, y_base - 6 * scale], fill=dark)
    draw.polygon([(x0 + 128 * scale, y_base - 58 * scale),
                  (x0 + 136 * scale, y_base - 58 * scale),
                  (x0 + 132 * scale, y_base - 96 * scale)], fill=dark)
    draw.line([(x0 + 118 * scale, y_base - 84 * scale),
               (x0 + 146 * scale, y_base - 84 * scale)], fill=dark, width=3)
    for i in range(7):
        px = x0 + (48 + i * 34) * scale
        draw.ellipse([px, y_base + 8 * scale, px + 7 * scale, y_base + 15 * scale],
                     fill=(212, 175, 55))


def draw_blast(draw, cx, cy, r):
    """Layered fireball + smoke column + sparks."""
    for rad, col in ((r, (255, 122, 26)), (r * 0.68, (255, 176, 32)),
                     (r * 0.42, (255, 226, 120))):
        draw.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=col)
    rng = random.Random(24)
    for _ in range(26):
        ang = rng.uniform(0, 2 * math.pi)
        dist = rng.uniform(r * 0.7, r * 1.7)
        sx, sy = cx + math.cos(ang) * dist, cy + math.sin(ang) * dist * 0.6
        s = rng.uniform(2, 6)
        draw.ellipse([sx - s, sy - s, sx + s, sy + s],
                     fill=(255, rng.choice([140, 170, 200]), 40))
    for i, (sx, sy, sr) in enumerate([(cx - 26, cy - r - 18, 20), (cx + 8, cy - r - 52, 26),
                                      (cx - 4, cy - r - 88, 30), (cx + 22, cy - r - 120, 34)]):
        draw.ellipse([sx - sr, sy - sr * 0.8, sx + sr, sy + sr * 0.8],
                     fill=(58, 62, 70) if i % 2 == 0 else (74, 78, 86))


def mini_gaza(draw, x, y, w, h):
    vgrad(draw, (x, y, x + w, y + h), (64, 42, 44), (24, 18, 26))
    draw.ellipse([x + w - 34, y + 12, x + w - 6, y + 40], fill=(235, 170, 90))
    rng = random.Random(7)
    for bx in range(0, w, 26):
        bh = rng.randint(28, 62)
        draw.rectangle([x + bx + 3, y + h - bh, x + bx + 23, y + h], fill=(16, 14, 18))
        for wy in range(0, bh - 8, 12):
            draw.rectangle([x + bx + 8, y + h - bh + 6 + wy,
                            x + bx + 13, y + h - bh + 11 + wy], fill=(240, 190, 90))
    for sx, sy, sr in [(x + 44, y + 34, 9), (x + 56, y + 24, 11), (x + 68, y + 16, 12)]:
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(96, 90, 88))


def mini_zaporizhzhia(draw, x, y, w, h):
    vgrad(draw, (x, y, x + w, y + h), (40, 48, 74), (16, 18, 30))
    draw.rectangle([x + 34, y + 26, x + w - 34, y + h], fill=(22, 24, 34))
    for r in range(3):
        for c in range(4):
            wx, wy = x + 44 + c * 28, y + 36 + r * 26
            lit = (r, c) in ((0, 1), (1, 2), (2, 0))
            draw.rectangle([wx, wy, wx + 16, wy + 14],
                           fill=(240, 190, 90) if lit else (52, 58, 72))
    draw.ellipse([x + w - 52, y + h - 66, x + w + 10, y + h - 4], fill=(255, 122, 26))
    draw.ellipse([x + w - 34, y + h - 48, x + w + 4, y + h - 14], fill=(255, 200, 90))


def mini_nvidia(draw, x, y, w, h):
    vgrad(draw, (x, y, x + w, y + h), (10, 34, 22), (6, 20, 14))
    cx, cy = x + w // 2 - 14, y + h // 2 + 6
    draw.rectangle([cx - 8, cy - 26, cx + 66, cy + 26], outline=(118, 200, 60), width=3)
    draw.rectangle([cx + 6, cy - 12, cx + 52, cy + 12], fill=(118, 200, 60))
    draw.text((cx + 16, cy - 8), "NV", font=font(16, True), fill=(6, 20, 14))
    for px in (cx - 8, cx + 66):
        for py in (cy - 20, cy - 4, cy + 12):
            draw.line([(px - 12 if px < cx + 30 else px, py),
                       (px + 12 if px < cx + 30 else px + 12, py)],
                      fill=(118, 200, 60), width=2)
    pts = [(x + 16, y + h - 26), (x + 66, y + 30), (x + 66, y + 48),
           (x + 84, y + 48), (x + 84, y + 66), (x + 108, y + 30),
           (x + 132, y + 30), (x + 132, y + 52), (x + 150, y + 52),
           (x + 150, y + 30), (x + w - 16, y + 8)]
    draw.line(pts, fill=(140, 230, 90), width=5, joint="curve")
    draw.polygon([(x + w - 24, y + 2), (x + w - 4, y + 10), (x + w - 22, y + 18)],
                 fill=(140, 230, 90))


def mini_cop(draw, x, y, w, h):
    vgrad(draw, (x, y, x + w, y + h), (58, 52, 30), (22, 20, 14))
    draw.ellipse([x + w // 2 - 44, y + 14, x + w // 2 + 44, y + 102], fill=(226, 178, 74))
    draw.rectangle([x + 18, y + h - 34, x + w - 18, y + h - 26], fill=(30, 28, 20))
    draw.line([(x + 10, y + h - 10), (x + 52, y + h - 30), (x + 96, y + h - 14),
               (x + 140, y + h - 34), (x + w - 10, y + h - 18)], fill=(120, 96, 50), width=3)
    draw.line([(x + 96, y + h - 14), (x + 110, y + h - 4)], fill=(120, 96, 50), width=2)
    for cx in (x + 34, x + 78, x + 122):
        draw.rectangle([cx, y + h - 62, cx + 22, y + h - 40], outline=(200, 190, 150), width=2)
        draw.line([(cx, y + h - 40), (cx, y + h - 34)], fill=(200, 190, 150), width=2)
        draw.line([(cx + 22, y + h - 40), (cx + 22, y + h - 34)], fill=(200, 190, 150), width=2)


def mini_iran(draw, x, y, w, h):
    vgrad(draw, (x, y, x + w, y + h), (26, 40, 66), (12, 18, 30))
    bx, by = x + 18, y + h - 52
    draw.rectangle([bx, by, bx + 74, by + 8], fill=(226, 222, 210))
    for i in range(4):
        draw.rectangle([bx + 8 + i * 17, by - 34, bx + 16 + i * 17, by], fill=(226, 222, 210))
    draw.polygon([(bx - 4, by - 34), (bx + 78, by - 34), (bx + 37, by - 52)], fill=(226, 222, 210))
    draw.rectangle([x + 108, y + h - 30, x + w - 12, y + h - 16], fill=(140, 60, 52))
    draw.rectangle([x + 122, y + h - 48, x + 138, y + h - 30], fill=(120, 50, 44))
    for wx in range(x + 112, x + w - 16, 12):
        draw.line([(wx, y + h - 8), (wx + 7, y + h - 8)], fill=(150, 180, 205), width=2)


CARDS = [
    ("GAZA", RED, mini_gaza,
     "GAZA STRIKE KILLS HAMAS SECURITY CHIEF",
     "Naeem Abu Nahel and six others dead, medics say"),
    ("UKRAINE", (66, 120, 200), mini_zaporizhzhia,
     "ZAPORIZHZHIA FLAT HIT: 2 DEAD, 40 HURT",
     "Overnight Russian strike; four children among the wounded"),
    ("TECH", (118, 200, 60), mini_nvidia,
     "HUANG BACK AS NVIDIA CHIEF",
     "Reinstated days after resigning as CEO"),
    ("CLIMATE", (90, 190, 170), mini_cop,
     "COP31 COLLAPSES IN ANTALYA",
     "90+ nations reject a draft that never names fossil fuels"),
    ("DIPLOMACY", GOLD, mini_iran,
     "VANCE & RUBIO MEET QATAR PM ON IRAN",
     "Tehran vows to defy the US naval blockade"),
]


def main():
    img = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(img)
    rng = random.Random(20261124)

    # ---- masthead (0-104) ----
    d.text((32, 22), "TUESDAY, 24 NOVEMBER 2026", font=font(46, True), fill=PAPER)
    d.text((32, 76), "THE WORLD IN ONE IMAGE  •  SIX STORIES THAT DEFINED THE DAY",
           font=font(19, True), fill=GOLD)
    d.line([(32, 104), (W - 32, 104)], fill=GOLD, width=3)

    # ---- hero scene (108-448) ----
    hy0, hy1 = 108, 448
    vgrad(d, (0, hy0, W, 292), SKY_TOP, (16, 34, 56))
    vgrad(d, (0, 292, W, hy1), SEA_TOP, SEA_BOT)
    for _ in range(70):
        sx, sy = rng.randint(8, W - 8), rng.randint(hy0 + 6, 250)
        r = rng.choice([1, 1, 2])
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(200, 210, 225))
    d.ellipse([W - 150, hy0 + 26, W - 96, hy0 + 80], fill=(232, 228, 210))
    d.ellipse([W - 142, hy0 + 34, W - 104, hy0 + 72], fill=(214, 208, 186))
    draw_drone(d, 150, 168, 13)
    draw_drone(d, 330, 138, 10)
    draw_drone(d, 700, 150, 11)
    # searchlight beam (soft, via overlay)
    beam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beam)
    bd.polygon([(566, 330), (580, 334), (420, 172), (392, 178)], fill=(255, 240, 190, 30))
    img.paste(Image.alpha_composite(img.convert("RGBA"), beam).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img)
    for _ in range(60):
        wx, wy = rng.randint(0, W - 60), rng.randint(300, hy1 - 8)
        wl = rng.randint(24, 70)
        d.line([(wx, wy), (wx + wl, wy)], fill=(46, 96, 116), width=2)
    d.ellipse([600, 300, 840, 420], fill=(96, 48, 18))
    draw_ship(d, 420, 402, 1.15)
    draw_blast(d, 745, 350, 56)
    for _ in range(24):
        rx = rng.randint(640, 850)
        ry = rng.randint(424, 442)
        d.line([(rx, ry), (rx + rng.randint(20, 60), ry)], fill=(255, 150, 50), width=2)

    # ---- hero text band (448-560) ----
    d.rectangle([0, 448, W, 560], fill=(6, 12, 22))
    d.rectangle([32, 458, 168, 486], fill=GOLD)
    d.text((44, 462), "TOP STORY", font=font(17, True), fill=(10, 22, 38))
    head_fnt = fit_font(d, "UKRAINE SINKS RUSSIAN WARSHIP OFF LIBYA", 40, True, W - 64)
    d.text((32, 492), "UKRAINE SINKS RUSSIAN WARSHIP OFF LIBYA", font=head_fnt, fill=PAPER)
    d.text((32, 532), "Kyiv: seven naval drones sank the corvette Merkury off Benghazi, Libya",
           font=font(18), fill=MUTED)

    # ---- five story cards (576-992) ----
    cy0, cy1 = 576, 992
    gap, margin = 10, 24
    cw = (W - 2 * margin - 4 * gap) // 5
    for i, (tag, accent, mini, headline, caption) in enumerate(CARDS):
        x = margin + i * (cw + gap)
        d.rectangle([x, cy0, x + cw, cy1], fill=PANEL)
        d.rectangle([x, cy0, x + cw, cy0 + 5], fill=accent)
        mini(d, x + 8, cy0 + 14, cw - 16, 150)
        d.text((x + 12, cy0 + 176), tag, font=font(15, True), fill=accent)
        hl = wrap(d, headline, font(19, True), cw - 24)
        y = text_block(d, x + 12, cy0 + 202, hl, font(19, True), PAPER, 24)
        cap = wrap(d, caption, font(15), cw - 24)
        text_block(d, x + 12, y + 8, cap, font(15), MUTED, 19)

    # ---- footer ----
    d.text((32, 1000), "STORIES AS REPORTED ON 24 NOVEMBER 2026  •  SOURCES: AP  •  REUTERS  •  MIDDLE EAST EYE",
           font=font(13), fill=(120, 134, 150))

    img.save(OUT, optimize=True)
    print("saved", OUT, img.size)


if __name__ == "__main__":
    main()
