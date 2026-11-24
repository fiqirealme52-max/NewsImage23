#!/usr/bin/env python3
"""Draw the News 23 front page: "The World in One Day - 23 November 2026".

Fresh implementation written November 2026. Renders a 1024x1024 newspaper
front page with PIL: 40 stories, 6 regions, masthead, timeline, pin map,
22 briefs, date-check box. Run: python3 draw.py  ->  writes entry.png
in the current directory.
"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

# --- palette: cream newsprint, black ink, dark red, flat scene colours ---
CREAM = (250, 243, 228)
PAPER = (247, 240, 224)
INK = (26, 26, 26)
RED = (179, 39, 30)
DARKRED = (158, 28, 32)
NAVY = (15, 30, 47)
MIDNAVY = (24, 48, 74)
SKY = (168, 205, 225)
PALESKY = (198, 222, 235)
GREEN = (46, 160, 90)
BRIGHTGREEN = (74, 222, 120)
ORANGE = (232, 120, 40)
GOLD = (214, 164, 32)
WHITE = (255, 255, 255)
GREY = (120, 120, 118)
LIGHTGREY = (205, 205, 200)
BROWN = (122, 84, 52)
TAN = (216, 186, 140)
MAPBG = (232, 240, 244)
MAPDOT = (96, 140, 165)

# --- fonts ---
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIFB = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIFI = "/usr/share/fonts/truetype/noto/NotoSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANSB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

_font_cache = {}


def F(path, size):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


def text_w(d, s, fnt):
    return d.textlength(s, font=fnt)


def wrap(d, text, fnt, maxw):
    """Greedy word wrap. Returns a list of lines that fit maxw."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_w(d, trial, fnt) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_size(path, text, maxw, start, step=0.5, minimum=7.0):
    """Largest font size (<= start) at which text fits maxw. Uses a scratch
    draw context so callers never have to guess a size."""
    probe = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    size = start
    while size > minimum:
        if probe.textlength(text, font=ImageFont.truetype(path, size)) <= maxw:
            return size
        size -= step
    return minimum


def draw_text(d, xy, s, fnt, fill, anchor="la"):
    d.text(xy, s, font=fnt, fill=fill, anchor=anchor)


def centered(d, cx, y, s, fnt, fill):
    d.text((cx, y), s, font=fnt, fill=fill, anchor="ma")


def rect(d, x0, y0, x1, y1, fill=None, outline=None, width=1):
    d.rectangle([x0, y0, x1, y1], fill=fill, outline=outline, width=width)


def hline(d, x0, x1, y, fill=INK, width=2):
    d.line([(x0, y), (x1, y)], fill=fill, width=width)


def chip(d, x, y, label, size=10):
    """Small white verification chip with a thin dark outline."""
    fnt = F(SANSB, size)
    w = int(text_w(d, label, fnt)) + 12
    h = size + 8
    d.rounded_rectangle([x, y, x + w, y + h], radius=3,
                        fill=WHITE, outline=INK, width=1)
    d.text((x + 6, y + 4), label, font=fnt, fill=INK)
    return w


def header_band(d, x, y, w, left, right, h=22, size=13):
    """Red card header: number + kind on the left, day tag on the right."""
    rect(d, x, y, x + w, y + h, fill=DARKRED)
    draw_text(d, (x + 8, y + 4), left, F(SANSB, size), WHITE)
    draw_text(d, (x + w - 8, y + 4), right, F(SANSB, size), WHITE, anchor="ra")


def scene_label(d, x, y, s, fill, size=12, bg=None):
    """Bold label drawn on top of a scene, optionally on a solid chip."""
    fnt = F(SANSB, size)
    if bg is not None:
        w = int(text_w(d, s, fnt)) + 8
        rect(d, x - 2, y - 2, x + w, y + size + 4, fill=bg)
    draw_text(d, (x, y), s, fnt, fill)


def person(d, x, y, shirt, pants=(30, 30, 30), skin=(232, 188, 150),
           h=16, arm_up=False):
    """Tiny flat person: head, torso, legs. (x, y) is the top of the head."""
    d.ellipse([x - 3, y, x + 3, y + 6], fill=skin)
    d.rectangle([x - 3, y + 7, x + 3, y + 7 + h // 2], fill=shirt)
    d.rectangle([x - 3, y + 7 + h // 2, x, y + 7 + h], fill=pants)
    d.rectangle([x, y + 7 + h // 2, x + 3, y + 7 + h], fill=pants)
    if arm_up:
        d.rectangle([x + 3, y + 7, x + 7, y + 10], fill=shirt)


def stars(d, x0, y0, x1, y1, n, seed=7):
    """Deterministic scatter of tiny white stars inside a rectangle."""
    import random
    rnd = random.Random(seed)
    for _ in range(n):
        sx = rnd.randint(x0 + 2, x1 - 2)
        sy = rnd.randint(y0 + 2, y1 - 2)
        r = rnd.choice([1, 1, 2])
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=WHITE)


def building(d, x, y, w, h, fill=(40, 60, 86), lit=True):
    rect(d, x, y, x + w, y + h, fill=fill)
    if lit:
        for wy in range(y + 6, y + h - 4, 10):
            for wx in range(x + 4, x + w - 4, 10):
                if (wx + wy) % 20 == 0:
                    rect(d, wx, wy, wx + 4, wy + 5, fill=(255, 214, 110))


# ---------------------------------------------------------------- top -----
MX = 14            # left/right margin
RX = 1010          # right edge of content
CW = RX - MX       # content width = 996


def draw_top(d):
    # kicker line
    draw_text(d, (MX, 8), "THE WORLD IN ONE DAY", F(SANSB, 19), RED)
    draw_text(d, (RX, 10),
              "40 STORIES \u00b7 6 REGIONS \u00b7 MONDAY 23 NOVEMBER 2026 "
              "\u00b7 WIRES TO 06:49 UTC TUE",
              F(SANSB, 12), INK, anchor="ra")
    hline(d, MX, RX, 28, width=2)
    # giant serif masthead
    centered(d, 512, 32, "Monday 23 November 2026", F(SERIFB, 60), INK)
    hline(d, MX, RX, 96, width=2)
    # red italic subline with the three leads (shrunk until it fits)
    sub = ("Nvidia brings Huang back as shares soar 31% \u00b7 "
           "Russian warship sunk off Benghazi \u00b7 "
           "COP31 collapses with no deal")
    centered(d, 512, 100, sub, F(SERIFI, fit_size(SERIFI, sub, 980, 20)),
             RED)
    # HOUR BY HOUR timeline band
    y0, y1 = 124, 146
    rect(d, MX, y0, RX, y1, outline=INK, width=1)
    items = [
        ("05:23", "Dymer 11th body"),
        ("05:30", "Taiex +2.16%"),
        ("06:30", "Kospi \u22123.31%"),
        ("08:38", "COP31 failure reported"),
        ("14:30", "Nasdaq opens"),
        ("19:45", "Monza kicks off"),
        ("20:00", "Brentford kicks off"),
        ("21:00", "NVDA +31.5% close"),
    ]
    tf, lf = F(SANSB, 10), F(SANS, 10)
    label = "HOUR BY HOUR, UTC"
    lx = MX + 6
    avail = RX - 6 - (lx + text_w(d, label, tf) + 10)
    # shrink the item font until all eight items fit the band
    size = 10.0
    while size > 7.5:
        widths = [text_w(d, t + " " + s, F(SANSB, size)) for t, s in items]
        if sum(widths) + 7 * 4 <= avail:
            break
        size -= 0.5
    tf = F(SANSB, size)
    lf = F(SANS, size)
    draw_text(d, (lx, y0 + 6), label, tf, RED)
    widths = [text_w(d, t + " " + s, tf) for t, s in items]
    gap = max(4, (avail - sum(widths)) / 7)
    x = lx + text_w(d, label, tf) + 10
    for (t, s), w in zip(items, widths):
        draw_text(d, (x, y0 + 6), t + " ", tf, RED)
        draw_text(d, (x + text_w(d, t + " ", tf), y0 + 6), s, lf, INK)
        x += w + gap


def draw_number_strip(d):
    y0, y1 = 150, 196
    cells = [
        ("40", "STORIES"),
        ("6", "REGIONS"),
        ("+31%", "NVIDIA, MON"),
        ("404", "FLIGHTS CANCELLED"),
        ("+2.16%", "TAIEX, MON"),
        ("104", "MATCHES, 2035 WORLD CUP"),
    ]
    bw = CW / 6
    for i, (big, small) in enumerate(cells):
        x0 = MX + i * bw
        x1 = x0 + bw
        rect(d, x0, y0, x1, y1, outline=INK, width=1)
        centered(d, (x0 + x1) / 2, y0 + 3, big, F(SERIFB, 33), INK)
        centered(d, (x0 + x1) / 2, y0 + 34, small, F(SANSB, 10), INK)


def draw_region_strip(d):
    y0, y1 = 198, 222
    cells = [
        ("EUROPE 17", (31, 78, 156)),
        ("ASIA 7", (230, 120, 40)),
        ("N. AMERICA 9", (0, 128, 128)),
        ("MIDDLE EAST 2", (172, 40, 40)),
        ("OCEANIA 2", (128, 90, 180)),
        ("AFRICA 3", (0, 130, 110)),
    ]
    bw = CW / 6
    for i, (label, col) in enumerate(cells):
        x0 = MX + i * bw
        x1 = x0 + bw
        rect(d, x0, y0, x1, y1, fill=col, outline=INK, width=1)
        centered(d, (x0 + x1) / 2, y0 + 5, label, F(SANSB, 14), WHITE)


# ------------------------------------------------------------- scenes -----
def sc_chart_up(d, x, y, w, h):
    rect(d, x, y, x + w, y + h, fill=NAVY)
    stars(d, x, y, x + w, y + h, 14, seed=11)
    for gy in range(y + 14, y + h - 8, 14):
        d.line([(x + 4, gy), (x + w - 4, gy)], fill=(38, 62, 92), width=1)
    pts = [(x + 4, y + h - 18), (x + w * 0.22, y + h - 34),
           (x + w * 0.42, y + h - 48), (x + w * 0.58, y + h - 30),
           (x + w * 0.74, y + h - 52), (x + w - 6, y + 16)]
    d.line(pts, fill=BRIGHTGREEN, width=3, joint="curve")
    # city skyline with lit windows along the bottom, left and right
    building(d, x + 8, y + h - 30, 18, 30, fill=(40, 60, 86))
    building(d, x + 30, y + h - 22, 14, 22, fill=(52, 72, 100))
    building(d, x + w // 2 - 6, y + h - 26, 16, 26, fill=(40, 60, 86))
    building(d, x + w - 78, y + h - 34, 20, 34, fill=(40, 60, 86))
    building(d, x + w - 52, y + h - 26, 18, 26, fill=(40, 60, 86))
    building(d, x + w - 28, y + h - 40, 20, 40, fill=(40, 60, 86))
    person(d, x + 30, y + h - 30, (120, 80, 60), h=14, arm_up=True)
    person(d, x + w // 2 + 8, y + h - 30, (30, 90, 60), h=14, arm_up=True)
    person(d, x + w - 100, y + h - 28, (30, 90, 60), h=14)
    scene_label(d, x + 6, y + 6, "NVDA +31.5%", BRIGHTGREEN, size=13)
    draw_text(d, (x + w - 100, y + 6), "NASDAQ +6.5%", F(SANSB, 12),
              (200, 210, 225), anchor="ra")


def sc_ship(d, x, y, w, h):
    rect(d, x, y, x + w, y + h, fill=(12, 24, 44))
    stars(d, x, y, x + w, y + h - 20, 16, seed=23)
    # moon, kept clear of the top-right chip
    d.ellipse([x + w - 156, y + 6, x + w - 134, y + 28],
              fill=(235, 228, 200))
    d.ellipse([x + w - 152, y + 10, x + w - 142, y + 20],
              fill=(210, 200, 170))
    # two smokestacks, leaning right, with drifting smoke
    for sx, sh in [(x + 96, 26), (x + 128, 32)]:
        d.polygon([(sx, y + h - 46), (sx + 12, y + h - 46),
                   (sx + 16, y + h - 46 - sh), (sx + 4, y + h - 46 - sh)],
                  fill=(52, 56, 66))
    for ex, ey, er in [(x + 110, y + h - 86, 10), (x + 132, y + h - 96, 8),
                       (x + 154, y + h - 88, 11)]:
        d.ellipse([ex - er, ey - er // 2, ex + er, ey + er // 2],
                  fill=(120, 122, 128))
    # capsized hull: long dark wedge, bow up on the right
    d.polygon([(x + 16, y + h - 30), (x + w * 0.60, y + h - 44),
               (x + w - 18, y + h - 22), (x + w - 26, y + h - 14),
               (x + 28, y + h - 14)], fill=(30, 34, 44))
    # deck stripe + lit portholes
    d.line([(x + 30, y + h - 28), (x + w - 30, y + h - 24)],
           fill=(70, 78, 92), width=2)
    for px in range(x + 48, x + w - 60, 26):
        d.ellipse([px, y + h - 26, px + 4, y + h - 22], fill=(255, 214, 110))
    # fire glow at the waterline, mid-ship
    fx = x + w * 0.62
    d.ellipse([fx - 20, y + h - 48, fx + 20, y + h - 22],
              fill=(255, 150, 50))
    d.polygon([(fx - 16, y + h - 30), (fx, y + h - 54),
               (fx + 16, y + h - 30)], fill=(255, 110, 30))
    d.polygon([(fx - 9, y + h - 30), (fx, y + h - 48),
               (fx + 9, y + h - 30)], fill=(255, 210, 90))
    # sea: horizontal streaks, orange reflection under the fire
    for i, yy in enumerate(range(y + h - 14, y + h - 2, 4)):
        col = ORANGE if i % 3 == 0 else (52, 96, 140)
        d.line([(x + 8 + (i % 2) * 10, yy),
                (x + w - 8 - (i % 2) * 6, yy)], fill=col, width=2)
    # two drifting drone silhouettes
    d.ellipse([x + 26, y + 20, x + 36, y + 27], fill=GREY)
    d.ellipse([x + w - 70, y + 30, x + w - 60, y + 37], fill=GREY)


def sc_conference(d, x, y, w, h):
    rect(d, x, y, x + w, y + h, fill=(150, 110, 70))
    # wall panels
    for i in range(5):
        px = x + 8 + i * (w - 16) // 5
        rect(d, px, y + 6, px + (w - 16) // 5 - 6, y + h - 46,
             fill=(196, 158, 104), outline=(120, 88, 56), width=1)
    # ceiling lights
    for cx in (x + 30, x + w - 30):
        d.ellipse([cx - 8, y + 2, cx + 8, y + 8], fill=(255, 230, 150))
    # big wall clock, kept clear of the people standing below
    cx, cy = x + w // 2, y + 22
    d.ellipse([cx - 20, cy - 16, cx + 20, cy + 16], fill=WHITE, outline=INK, width=2)
    d.line([(cx, cy), (cx, cy - 11)], fill=INK, width=2)
    d.line([(cx, cy), (cx + 9, cy)], fill=INK, width=2)
    scene_label(d, cx - 34, cy + 18, "2 DAYS OVER", DARKRED, size=12)
    # chairs behind the long table
    for cx in [0.10, 0.28, 0.48, 0.68, 0.88]:
        bx = x + int(w * cx)
        rect(d, bx - 8, y + h - 46, bx + 8, y + h - 30, fill=(96, 66, 40))
    # long table with a white nameplate and a red gavel line
    rect(d, x + 10, y + h - 30, x + w - 10, y + h - 16, fill=(96, 66, 40))
    rect(d, x + w // 2 - 40, y + h - 28, x + w // 2 + 40, y + h - 18,
         fill=WHITE)
    d.line([(x + w // 2 - 32, y + h - 25), (x + w // 2 + 32, y + h - 25)],
           fill=RED, width=2)
    d.line([(x + w // 2 - 32, y + h - 21), (x + w // 2 + 8, y + h - 21)],
           fill=RED, width=2)
    # darker floor band below the table
    rect(d, x, y + h - 16, x + w, y + h, fill=(110, 76, 46))
    for i, sx in enumerate([0.08, 0.24, 0.40, 0.56, 0.72, 0.90]):
        person(d, x + int(w * sx), y + h - 56,
               [(40, 70, 120), (150, 40, 40), (40, 110, 60), (90, 70, 130),
                (30, 90, 90), (140, 110, 40)][i],
               h=18)


def sc_rescue(d, x, y, w, h):
    rect(d, x, y, x + w, y + h, fill=(96, 88, 104))
    d.ellipse([x + w - 30, y + 4, x + w - 8, y + 20], fill=(255, 214, 130))
    # rubble mounds
    d.polygon([(x, y + h), (x + 30, y + h - 26), (x + 62, y + h)], fill=(70, 64, 72))
    d.polygon([(x + w - 62, y + h), (x + w - 30, y + h - 30), (x + w, y + h)],
              fill=(70, 64, 72))
    # searchlight beams
    d.polygon([(x + 14, y + 20), (x + 34, y + 20), (x + 62, y + h - 26),
               (x + 44, y + h - 26)], fill=(255, 240, 170))
    d.polygon([(x + w - 34, y + 20), (x + w - 14, y + 20),
               (x + w - 44, y + h - 30), (x + w - 62, y + h - 30)],
              fill=(255, 240, 170))
    # stretcher with a blue blanket, legs, and a headlamp glow
    rect(d, x + w // 2 - 34, y + h - 22, x + w // 2 + 34, y + h - 14,
         fill=WHITE)
    rect(d, x + w // 2 - 34, y + h - 22, x + w // 2 + 6, y + h - 14,
         fill=(40, 110, 190))
    rect(d, x + w // 2 - 28, y + h - 14, x + w // 2 - 24, y + h - 8,
         fill=INK)
    rect(d, x + w // 2 + 24, y + h - 14, x + w // 2 + 28, y + h - 8,
         fill=INK)
    # rubble detail on the mounds
    for rx, ry in [(x + 12, y + h - 12), (x + 40, y + h - 8),
                   (x + w - 44, y + h - 10), (x + w - 16, y + h - 14)]:
        rect(d, rx, ry, rx + 10, ry + 4, fill=(52, 48, 54))
    person(d, x + 16, y + h - 34, (232, 110, 40), h=16)
    person(d, x + w - 20, y + h - 34, (232, 110, 40), h=16)
    scene_label(d, x + 6, y + 4, "14 HOURS", INK, size=12, bg=(255, 240, 170))


def sc_awacs(d, x, y, w, h):
    rect(d, x, y, x + w, y + h, fill=PALESKY)
    for cx, cy, r in [(30, 12, 12), (w - 40, 10, 10), (w // 2 + 30, 22, 9),
                      (w - 78, 30, 7), (58, 26, 7)]:
        d.ellipse([x + cx - r, y + cy - r // 2, x + cx + r, y + cy + r // 2],
                  fill=WHITE)
    # distant small plane, top-right
    d.ellipse([x + w - 58, y + 6, x + w - 38, y + 12], fill=(210, 216, 222))
    d.polygon([(x + w - 44, y + 7), (x + w - 36, y + 4),
               (x + w - 36, y + 10)], fill=(210, 216, 222))
    # fuselage + radar dome + tail
    d.ellipse([x + w // 2 - 12, y + 12, x + w // 2 + 12, y + 30],
              fill=LIGHTGREY)
    d.rounded_rectangle([x + 8, y + 26, x + w - 8, y + 44], radius=8,
                        fill=WHITE, outline=GREY, width=1)
    for wx in range(x + 22, x + w - 22, 16):
        rect(d, wx, y + 31, wx + 8, y + 38, fill=(30, 70, 130))
    d.polygon([(x + w - 16, y + 26), (x + w - 2, y + 10),
               (x + w - 2, y + 26)], fill=LIGHTGREY)
    # green ground strip, two ground crew, red windsock
    rect(d, x, y + h - 10, x + w, y + h, fill=(110, 170, 90))
    person(d, x + 30, y + h - 26, (40, 70, 140), h=12)
    person(d, x + w - 34, y + h - 26, (40, 70, 140), h=12)
    d.line([(x + w - 60, y + h - 10), (x + w - 60, y + h - 26)],
           fill=INK, width=2)
    d.polygon([(x + w - 60, y + h - 26), (x + w - 44, y + h - 23),
               (x + w - 60, y + h - 20)], fill=RED)
    scene_label(d, x + 6, y + 4, "AWACS", INK, size=12)


def sc_temple(d, x, y, w, h):
    rect(d, x, y, x + w, y + h, fill=PALESKY)
    # three mountains, snow-capped, for depth
    d.polygon([(x, y + h - 22), (x + w // 3, y + 12),
               (x + 2 * w // 3, y + h - 22)], fill=(150, 150, 155))
    d.polygon([(x + w // 3, y + 12), (x + w // 3 + 10, y + 22),
               (x + w // 3 - 10, y + 22)], fill=WHITE)
    d.polygon([(x + w // 2, y + h - 22), (x + w - 10, y + 20),
               (x + w, y + h - 22)], fill=(120, 120, 128))
    d.polygon([(x + w - 10, y + 20), (x + w - 2, y + 28),
               (x + w - 18, y + 28)], fill=WHITE)
    d.polygon([(x + w // 4, y + h - 22), (x + w // 2, y + 26),
               (x + 3 * w // 4, y + h - 22)], fill=(135, 135, 142))
    # red temple with white columns
    rect(d, x + 26, y + h - 34, x + w - 26, y + h - 14, fill=(172, 40, 40))
    for cx in range(x + 34, x + w - 30, 18):
        rect(d, cx, y + h - 32, cx + 5, y + h - 16, fill=WHITE)
    d.polygon([(x + 20, y + h - 34), (x + w // 2, y + h - 46),
               (x + w - 20, y + h - 34)], fill=(140, 28, 28))
    d.line([(x + w // 2, y + h - 46), (x + w // 2, y + h - 56)],
           fill=INK, width=2)
    d.polygon([(x + w // 2, y + h - 56), (x + w // 2 + 12, y + h - 53),
               (x + w // 2, y + h - 50)], fill=ORANGE)
    person(d, x + 18, y + h - 16, (240, 240, 240), h=12)
    person(d, x + w - 22, y + h - 16, (30, 60, 120), h=12)
    _fnt = F(SANSB, 12)
    _tw = int(text_w(d, "\u20b915,000 CR", _fnt))
    rect(d, x + w - 100 - _tw - 6, y + 2, x + w - 98, y + 18, fill=WHITE)
    draw_text(d, (x + w - 100, y + 4), "\u20b915,000 CR", _fnt, INK,
              anchor="ra")


def sc_refinery(d, x, y, w, h):
    rect(d, x, y, x + w, y + h, fill=(14, 18, 34))
    stars(d, x, y, x + w, y + h - 16, 10, seed=31)
    rect(d, x + 12, y + 18, x + 30, y + h - 6, fill=(70, 74, 84))
    rect(d, x + 44, y + 10, x + 62, y + h - 6, fill=(70, 74, 84))
    rect(d, x + w - 62, y + 22, x + w - 44, y + h - 6, fill=(70, 74, 84))
    rect(d, x + w - 30, y + 14, x + w - 12, y + h - 6, fill=(70, 74, 84))
    # flame + glow over the second tower
    d.ellipse([x + 58, y + 6, x + 84, y + 26], fill=(255, 170, 60))
    d.polygon([(x + 64, y + 20), (x + 71, y + 6), (x + 78, y + 20)],
              fill=(255, 110, 30))
    d.line([(x + 8, y + h - 8), (x + w - 8, y + h - 8)], fill=(52, 60, 74),
           width=3)
    scene_label(d, x + 6, y + 4, "RABIGH", WHITE, size=11)


def sc_quake(d, x, y, w, h):
    rect(d, x, y, x + w, y + h, fill=(16, 42, 66))
    d.polygon([(x, y + h - 26), (x + w // 3, y + 8),
               (x + 2 * w // 3, y + h - 26)], fill=(30, 90, 70))
    d.polygon([(x + w // 2, y + h - 26), (x + w - 8, y + 14),
               (x + w, y + h - 26)], fill=(24, 78, 60))
    # yellow seismograph zigzag
    pts = [(x + 4, y + 22)]
    for i in range(1, 9):
        pts.append((x + 4 + i * (w - 8) // 8,
                    y + 22 + (14 if i % 2 else -6)))
    d.line(pts, fill=(255, 214, 60), width=2)
    # white wave lines + a clean down arrow (deep)
    for yy in (y + h - 20, y + h - 12, y + h - 5):
        pts = [(x + 6, yy)]
        for i in range(1, 7):
            pts.append((x + 6 + i * (w - 52) // 6,
                        yy + (3 if i % 2 else -3)))
        d.line(pts, fill=WHITE, width=2)
    ax = x + w - 24
    d.line([(ax, y + h - 26), (ax, y + h - 8)], fill=WHITE, width=3)
    d.polygon([(ax - 6, y + h - 12), (ax + 6, y + h - 12),
               (ax, y + h - 4)], fill=WHITE)
    draw_text(d, (x + w - 6, y + 4), "601 KM", F(SANSB, 12), WHITE,
              anchor="ra")


def sc_trophy(d, x, y, w, h):
    rect(d, x, y, x + w, y + h, fill=(52, 110, 180))
    # stadium arc + green pitch
    d.pieslice([x - 30, y - 40, x + w + 30, y + h - 6], 0, 180,
               fill=(240, 240, 235))
    rect(d, x, y + h - 18, x + w, y + h, fill=(60, 150, 80))
    d.line([(x + 10, y + h - 18), (x + w - 10, y + h - 18)],
           fill=WHITE, width=2)
    # gold trophy
    tx, ty = x + w // 2 - 8, y + 8
    d.ellipse([tx, ty, tx + 16, ty + 18], fill=GOLD)
    rect(d, tx + 6, ty + 18, tx + 10, ty + 26, fill=GOLD)
    rect(d, tx - 2, ty + 26, tx + 18, ty + 30, fill=GOLD)
    d.arc([tx - 8, ty + 2, tx + 2, ty + 14], 90, 270, fill=GOLD, width=3)
    d.arc([tx + 14, ty + 2, tx + 24, ty + 14], 270, 90, fill=GOLD, width=3)
    person(d, x + 18, y + h - 26, (200, 40, 40), h=14, arm_up=True)
    person(d, x + w - 22, y + h - 26, (40, 40, 180), h=14)
    # crowd dots along the stadium arc + a match ball
    import random as _rnd
    _r = _rnd.Random(5)
    for _ in range(16):
        cx = x + _r.randint(12, w - 12)
        cy = y + _r.randint(4, h - 26)
        d.ellipse([cx, cy, cx + 3, cy + 3],
                  fill=_r.choice([(255, 220, 90), (255, 255, 255),
                                  (255, 140, 90), (140, 200, 255)]))
    d.ellipse([x + w // 2 - 4, y + h - 12, x + w // 2 + 2, y + h - 6],
              fill=WHITE)
    scene_label(d, x + 6, y + h - 16, "104 MATCHES", WHITE, size=11,
                bg=(30, 90, 50))


def sc_capitol(d, x, y, w, h):
    rect(d, x, y, x + w, y + h, fill=(206, 216, 226))
    # white capitol: dome + base
    d.pieslice([x + w // 2 - 22, y + 6, x + w // 2 + 22, y + 34], 180, 360,
               fill=WHITE)
    rect(d, x + w // 2 - 26, y + 20, x + w // 2 + 26, y + h - 18,
         fill=WHITE)
    for cx in range(x + w // 2 - 22, x + w // 2 + 20, 9):
        rect(d, cx, y + 26, cx + 4, y + h - 20, fill=(180, 186, 192))
    # blue and red bars (house floor)
    rect(d, x + 8, y + h - 16, x + w // 2 - 4, y + h - 10, fill=(30, 70, 150))
    rect(d, x + w // 2 + 4, y + h - 16, x + w - 8, y + h - 10,
         fill=(180, 40, 40))
    person(d, x + 16, y + h - 30, (40, 40, 40), h=14)
    person(d, x + w - 20, y + h - 30, (40, 40, 40), h=14)
    scene_label(d, x + 6, y + 4, "258 SEATS", INK, size=12)


def sc_mountains(d, x, y, w, h):
    rect(d, x, y, x + w, y + h, fill=(196, 210, 222))
    d.polygon([(x, y + h - 18), (x + w // 3, y + 8),
               (x + 2 * w // 3, y + h - 18)], fill=(120, 130, 145))
    d.polygon([(x + w // 3, y + 8), (x + w // 3 + 12, y + 18),
               (x + w // 3 - 12, y + 18)], fill=WHITE)
    d.polygon([(x + w // 2, y + h - 18), (x + w - 6, y + 14),
               (x + w, y + h - 18)], fill=(96, 106, 122))
    rect(d, x, y + h - 18, x + w, y + h, fill=(140, 165, 110))
    # two flags on poles + two figures + a brown crate
    for fx, col in [(x + int(w * 0.25), ORANGE),
                    (x + int(w * 0.45), (240, 240, 240))]:
        d.line([(fx, y + 10), (fx, y + 30)], fill=INK, width=2)
        d.polygon([(fx, y + 10), (fx + 14, y + 14), (fx, y + 18)], fill=col)
    person(d, x + w // 3 - 8, y + h - 34, (30, 90, 50), h=14)
    person(d, x + 2 * w // 3 + 2, y + h - 34, (120, 60, 40), h=14)
    rect(d, x + w // 2 - 8, y + h - 28, x + w // 2 + 8, y + h - 18,
         fill=(122, 84, 52))
    scene_label(d, x + 6, y + h - 16, "10-DAY TALKS", INK, size=11,
                bg=WHITE)


def sc_taiex(d, x, y, w, h):
    rect(d, x, y, x + w, y + h, fill=NAVY)
    stars(d, x, y, x + w, y + h, 8, seed=41)
    # yellow building bars on the right
    for i, bh in enumerate([18, 26, 14, 22]):
        bx = x + w - 52 + i * 12
        building(d, bx, y + h - bh - 4, 10, bh, fill=(120, 110, 40),
                 lit=False)
    pts = [(x + 6, y + h - 14), (x + w * 0.3, y + h - 26),
           (x + w * 0.5, y + h - 20), (x + w * 0.72, y + h - 38),
           (x + w - 8, y + 14)]
    d.line(pts, fill=BRIGHTGREEN, width=3, joint="curve")
    d.polygon([(x + w - 14, y + 10), (x + w - 4, y + 14),
               (x + w - 14, y + 20)], fill=BRIGHTGREEN)
    scene_label(d, x + 6, y + 6, "+2.16%", BRIGHTGREEN, size=13)


def sc_hospital(d, x, y, w, h):
    rect(d, x, y, x + w, y + h, fill=PALESKY)
    rect(d, x + 10, y + 14, x + w - 40, y + h - 12, fill=WHITE,
         outline=GREY, width=1)
    rect(d, x + 10, y + 14, x + w - 40, y + 22, fill=(30, 90, 170))
    for wy in range(y + 28, y + h - 16, 10):
        for wx in range(x + 16, x + w - 46, 14):
            rect(d, wx, wy, wx + 8, wy + 6, fill=(120, 190, 220))
    rect(d, x, y + h - 12, x + w, y + h, fill=(110, 170, 90))
    # pink cell under a magnifier, held by a doctor
    d.ellipse([x + w - 40, y + 24, x + w - 22, y + 42], fill=(232, 130, 170))
    d.ellipse([x + w - 46, y + 20, x + w - 16, y + 46], outline=INK, width=2)
    d.line([(x + w - 20, y + 42), (x + w - 12, y + 50)], fill=INK, width=2)
    person(d, x + w - 22, y + h - 28, WHITE, h=16)
    person(d, x + 18, y + h - 28, WHITE, h=16)
    scene_label(d, x + 6, y + 4, "AI TRIAL", INK, size=12)


def sc_tennis(d, x, y, w, h):
    rect(d, x, y, x + w, y + h, fill=(64, 140, 88))
    d.line([(x + 6, y + h // 2), (x + w - 6, y + h // 2)], fill=WHITE,
           width=2)
    d.line([(x + w // 2, y + 6), (x + w // 2, y + h - 6)], fill=WHITE,
           width=1)
    # net across the middle
    d.line([(x + 6, y + h // 2 - 8), (x + w - 6, y + h // 2 - 8)],
           fill=INK, width=2)
    # gold trophy + celebrating player + ball boy with a ball
    tx, ty = x + 14, y + 6
    d.ellipse([tx, ty, tx + 14, ty + 14], fill=GOLD)
    rect(d, tx + 5, ty + 14, tx + 9, ty + 20, fill=GOLD)
    rect(d, tx - 1, ty + 20, tx + 15, ty + 23, fill=GOLD)
    person(d, x + w // 2 + 6, y + h - 30, WHITE, h=16, arm_up=True)
    person(d, x + w - 24, y + h - 30, (40, 40, 40), h=14)
    d.ellipse([x + w - 40, y + h - 12, x + w - 34, y + h - 6],
              fill=(200, 220, 60))
    scene_label(d, x + 6, y + h - 14, "ATP FINALS", WHITE, size=11,
                bg=(30, 90, 50))


def sc_flood(d, x, y, w, h):
    rect(d, x, y, x + w, y + h, fill=(150, 170, 185))
    # stilt houses
    for hx in [x + 8, x + w // 2 - 14, x + w - 52]:
        rect(d, hx, y + 12, hx + 44, y + 30, fill=(150, 100, 60))
        d.polygon([(hx - 4, y + 12), (hx + 22, y + 2), (hx + 48, y + 12)],
                  fill=(110, 70, 40))
        d.line([(hx + 8, y + 30), (hx + 8, y + 40)], fill=INK, width=2)
        d.line([(hx + 36, y + 30), (hx + 36, y + 40)], fill=INK, width=2)
    # water with wave lines + a boat
    rect(d, x, y + h - 22, x + w, y + h, fill=(50, 110, 170))
    for wy in (y + h - 18, y + h - 10):
        for wx in range(x + 6, x + w - 6, 22):
            d.arc([wx, wy - 3, wx + 14, wy + 3], 180, 360, fill=WHITE,
                  width=2)
    d.polygon([(x + w // 2 - 16, y + h - 14), (x + w // 2 + 16, y + h - 14),
               (x + w // 2 + 10, y + h - 6), (x + w // 2 - 10, y + h - 6)],
              fill=(122, 84, 52))
    person(d, x + w // 2 - 2, y + h - 28, (200, 60, 60), h=12)
    person(d, x + w // 2 + 10, y + h - 28, (60, 60, 200), h=12)
    scene_label(d, x + 6, y + 4, "1,582", INK, size=12, bg=WHITE)


def sc_ebola(d, x, y, w, h):
    rect(d, x, y, x + w, y + h, fill=(214, 200, 170))
    rect(d, x + 8, y + 16, x + w - 8, y + h - 14, fill=WHITE,
         outline=GREY, width=1)
    rect(d, x + 8, y + 16, x + w - 8, y + 22, fill=(40, 120, 90))
    for wx in range(x + 14, x + w - 14, 16):
        rect(d, wx, y + 28, wx + 9, y + 35, fill=(120, 190, 220))
    # yellow warning triangle (left of the chip zone)
    tx, ty = x + w - 104, y + 6
    d.polygon([(tx, ty + 16), (tx + 10, ty), (tx + 20, ty + 16)],
              fill=(255, 210, 40), outline=INK)
    d.text((tx + 8, ty + 5), "!", font=F(SANSB, 12), fill=INK, anchor="ma")
    # sand mound + three figures
    d.polygon([(x + w // 2 - 24, y + h - 14), (x + w // 2, y + h - 28),
               (x + w // 2 + 24, y + h - 14)], fill=(196, 168, 120))
    person(d, x + 16, y + h - 28, (40, 70, 150), h=14)
    person(d, x + w // 2 - 2, y + h - 28, (40, 120, 70), h=14)
    person(d, x + w - 20, y + h - 28, (150, 40, 40), h=14)
    scene_label(d, x + 6, y + 4, "11,762 CASES", INK, size=11, bg=WHITE)


def sc_kospi(d, x, y, w, h):
    rect(d, x, y, x + w, y + h, fill=(20, 20, 28))
    for i, bh in enumerate([16, 24, 12, 20]):
        bx = x + 10 + i * 12
        rect(d, bx, y + h - bh - 6, bx + 9, y + h - 6,
             fill=(200, 170, 60))
    # red falling line, starting clear of the label at top-left
    pts = [(x + 62, y + 16), (x + w * 0.45, y + 22),
           (x + w * 0.68, y + h - 26), (x + w - 8, y + h - 10)]
    d.line(pts, fill=(230, 60, 50), width=3, joint="curve")
    person(d, x + w - 22, y + h - 30, (200, 200, 200), h=14)
    scene_label(d, x + 6, y + 6, "\u22123.31%", WHITE, size=13)


def sc_airport(d, x, y, w, h):
    rect(d, x, y, x + w, y + h, fill=PALESKY)
    # clouds, kept clear of the CANCELLED sign and the tower
    for cx, cy, r in [(w // 2 + 22, 12, 9), (w - 92, 26, 8),
                      (30, 34, 7)]:
        d.ellipse([x + cx - r, y + cy - r // 2, x + cx + r, y + cy + r // 2],
                  fill=WHITE)
    # control tower: shaft + cab with a lit window
    tx = x + w - 34
    rect(d, tx, y + 12, tx + 8, y + h - 22, fill=(120, 128, 138))
    rect(d, tx - 4, y + 6, tx + 12, y + 16, fill=(70, 80, 92))
    rect(d, tx - 2, y + 8, tx + 10, y + 14, fill=(140, 200, 230))
    # terminal block with lit windows
    rect(d, x + 8, y + h - 34, x + w - 44, y + h - 12, fill=(96, 108, 124))
    rect(d, x + 8, y + h - 34, x + w - 44, y + h - 28, fill=(70, 82, 100))
    for wx in range(x + 14, x + w - 50, 14):
        rect(d, wx, y + h - 26, wx + 7, y + h - 18, fill=(255, 214, 110))
    # jet bridge from the terminal up to a parked plane
    d.line([(x + w - 44, y + h - 24), (x + w - 44, y + h - 40)],
           fill=(200, 200, 200), width=3)
    d.ellipse([x + w - 42, y + h - 46, x + w - 6, y + h - 36],
              fill=WHITE)
    d.polygon([(x + w - 12, y + h - 44), (x + w - 2, y + h - 50),
               (x + w - 2, y + h - 40)], fill=WHITE)
    # runway with centre dashes
    rect(d, x, y + h - 12, x + w, y + h, fill=(90, 90, 92))
    for wx in range(x + 8, x + w - 8, 24):
        rect(d, wx, y + h - 7, wx + 12, y + h - 5, fill=WHITE)
    # CANCELLED sign, red outline, top-left
    fnt = F(SANSB, 11)
    tw = int(text_w(d, "CANCELLED", fnt))
    sx = x + 8
    rect(d, sx, y + 4, sx + tw + 12, y + 19, fill=WHITE, outline=RED,
         width=2)
    draw_text(d, (sx + 6, y + 6), "CANCELLED", fnt, RED)


# -------------------------------------------------------------- cards -----
LEADS = [
    {
        "num": "1", "kind": "LEAD", "tag": "MON", "chip": "ON RECORD",
        "scene": sc_chart_up, "ticker":
            "NVDA +31.5% \u00b7 TSLA +11.5% \u00b7 META +6.6% \u00b7 "
            "GOOGL +6.3% \u00b7 AMZN +3.5%",
        "kicker": "NEW YORK \u00b7 MARKETS \u00b7 MON",
        "headline": "Nvidia brings Huang back \u2014 shares soar 31%",
        "body": "Board votes unanimously, 11 days after resignation; "
                "NVDA +31.5%, TSLA +11.5%, +$950bn. (Reuters)",
    },
    {
        "num": "2", "kind": "LEAD", "tag": "SUN", "chip": "REPORTED",
        "scene": sc_ship, "ticker": None,
        "kicker": "BENGHAZI \u00b7 LIBYA \u00b7 SUN",
        "headline": "Russian warship sunk by sea drones in Libyan port",
        "body": "Capsized, bow up; 10 hurt, 4 drones downed \u2014 "
                "Sparta II towed out. Suspected Ukrainian drones. "
                "(AP, Reuters)",
    },
    {
        "num": "3", "kind": "LEAD", "tag": "SUN", "chip": "REPORTED",
        "scene": sc_conference, "ticker": None,
        "kicker": "ANTALYA \u00b7 CLIMATE \u00b7 SUN",
        "headline": "COP31 collapses \u2014 no deal on fossil fuels",
        "body": "Longest COP ever, 2 days over; $120bn goal lost; "
                "EU + 130 nations said no. (BBC, Reuters)",
    },
]

MEDIUMS = [
    # row A
    {"num": "18", "kind": "HERO", "tag": "SUN", "chip": "REPORTED",
     "scene": sc_rescue,
     "kicker": "DYMER \u00b7 UKRAINE \u00b7 SUN",
     "headline": "Boy, 7, pulled alive after 14 hours",
     "body": "11 dead, none missing. Vyshneve: 3 killed, 15 hurt. "
             "(BBC, AFP)"},
    {"num": "4", "kind": "", "tag": "MON", "chip": "ON RECORD",
     "scene": sc_awacs,
     "kicker": "NATO \u00b7 POLAND \u00b7 MON",
     "headline": "NATO sends AWACS to Poland",
     "body": "SACEUR authorises jet; Article 4 not invoked. (NATO)"},
    {"num": "5", "kind": "", "tag": "MON", "chip": "ON RECORD",
     "scene": sc_temple,
     "kicker": "NEW DELHI \u00b7 NEPAL \u00b7 MON",
     "headline": "Modi gives Nepal \u20b915,000 crore",
     "body": "NPR 5,600 cr grant + 18,400 cr credit; rail flagged off. "
             "(PIB)"},
    {"num": "6", "kind": "", "tag": "SUN", "chip": "CLAIM",
     "scene": sc_refinery,
     "kicker": "RABIGH \u00b7 SAUDI \u00b7 SUN",
     "headline": "Houthis claim refinery hit",
     "body": "Rabigh targeted. Saudis silent; coalition: missile down. "
             "(Reuters)"},
    {"num": "7", "kind": "", "tag": "MON", "chip": "ON RECORD",
     "scene": sc_quake,
     "kicker": "VANUATU \u00b7 PACIFIC \u00b7 MON",
     "headline": "Deep quake shakes Vanuatu",
     "body": "M6.5 at 601 km, no tsunami. (USGS)"},
    # row B
    {"num": "8", "kind": "", "tag": "MON", "chip": "ON RECORD",
     "scene": sc_trophy,
     "kicker": "ZURICH \u00b7 SPORT \u00b7 MON",
     "headline": "UK to host 2035 Women's World Cup",
     "body": "48 teams, 104 matches. (BBC)"},
    {"num": "9", "kind": "", "tag": "SUN", "chip": "REPORTED",
     "scene": sc_capitol,
     "kicker": "WASHINGTON \u00b7 POLITICS \u00b7 SUN",
     "headline": "Democrats' biggest House majority",
     "body": "Largest since 1992. (BBC)"},
    {"num": "10", "kind": "", "tag": "MON", "chip": "REPORTED",
     "scene": sc_mountains,
     "kicker": "ARUNACHAL \u00b7 INDIA-CHINA \u00b7 MON",
     "headline": "India, China open border talks",
     "body": "10-day talks on LAC. (Hindu)"},
    {"num": "11", "kind": "", "tag": "MON", "chip": "ON RECORD",
     "scene": sc_taiex,
     "kicker": "TAIPEI \u00b7 MARKETS \u00b7 MON",
     "headline": "Taiex rebounds 2.16% after rout",
     "body": "Close 36,811.89 (TVBS)"},
    {"num": "12", "kind": "", "tag": "MON", "chip": "REPORTED",
     "scene": sc_hospital,
     "kicker": "LONDON \u00b7 HEALTH \u00b7 MON",
     "headline": "NHS launches biggest AI trial",
     "body": "AI spots cancer earlier. (BBC)"},
    # row C
    {"num": "13", "kind": "", "tag": "SUN", "chip": "ON RECORD",
     "scene": sc_tennis,
     "kicker": "TURIN \u00b7 SPORT \u00b7 SUN",
     "headline": "Alcaraz wins ATP Finals in Turin",
     "body": "M\u00e1rquez 8th title too. (BBC)"},
    {"num": "14", "kind": "", "tag": "MON", "chip": "REPORTED",
     "scene": sc_flood,
     "kicker": "SELANGOR \u00b7 MALAYSIA \u00b7 MON",
     "headline": "Selangor floods displace 1,582",
     "body": "1,582 at 06:00, falling. (ADINet)"},
    {"num": "15", "kind": "", "tag": "MON", "chip": "REPORTED",
     "scene": sc_ebola,
     "kicker": "BUNIA \u00b7 DR CONGO \u00b7 MON",
     "headline": "Ebola teams trapped as fighting rages",
     "body": "Doubled in 3 months. (UN News)"},
    {"num": "16", "kind": "", "tag": "MON", "chip": "ON RECORD",
     "scene": sc_kospi,
     "kicker": "SEOUL \u00b7 MARKETS \u00b7 MON",
     "headline": "Kospi plunges 5.8% intraday",
     "body": "Close \u22123.31% at 4,708. (KRX)"},
    {"num": "17", "kind": "", "tag": "MON", "chip": "ON RECORD",
     "scene": sc_airport,
     "kicker": "BRUSSELS \u00b7 STRIKE \u00b7 MON",
     "headline": "Belgium grounds all flights",
     "body": "404 of 429 cancelled 07:00\u201321:00."},
]


def draw_lead(d, x, y, w, card):
    """One lead card, 232 tall: band, scene, ticker, kicker, headline, body."""
    header_band(d, x, y, w,
                card["num"] + " \u00b7 " + card["kind"], card["tag"])
    sy = y + 22
    scene_h = 96 if card["ticker"] else 110
    card["scene"](d, x, sy, w, scene_h)
    chip(d, x + w - 8 - int(text_w(d, card["chip"], F(SANSB, 10))) - 12,
         sy + 6, card["chip"])
    ty = sy + scene_h
    if card["ticker"]:
        rect(d, x, ty, x + w, ty + 14, fill=NAVY)
        tsize = fit_size(SANSB, card["ticker"], w - 12, 10)
        draw_text(d, (x + 6, ty + 2), card["ticker"], F(SANSB, tsize),
                  BRIGHTGREEN)
        ty += 14
    draw_text(d, (x + 2, ty + 4), card["kicker"], F(SANSB, 11), RED)
    hy = ty + 18
    hsize = 24
    lines = wrap(d, card["headline"], F(SERIFB, hsize), w - 4)
    while len(lines) > 2 and hsize > 18:
        hsize -= 1
        lines = wrap(d, card["headline"], F(SERIFB, hsize), w - 4)
    hlh = hsize + 2
    for i, ln in enumerate(lines[:2]):
        draw_text(d, (x + 2, hy + i * hlh), ln, F(SERIFB, hsize), INK)
    by = hy + len(lines[:2]) * hlh + 1
    for i, ln in enumerate(wrap(d, card["body"], F(SERIF, 11), w - 4)[:2]):
        draw_text(d, (x + 2, by + i * 13), ln, F(SERIF, 11), INK)


def draw_medium(d, x, y, w, card):
    """One medium card, 136 tall: band, scene, kicker, headline, body."""
    left = card["num"] + (" \u00b7 " + card["kind"] if card["kind"] else "")
    header_band(d, x, y, w, left, card["tag"], h=18, size=11)
    sy = y + 18
    card["scene"](d, x, sy, w, 52)
    chip(d, x + w - 8 - int(text_w(d, card["chip"], F(SANSB, 10))) - 12,
         sy + 5, card["chip"])
    draw_text(d, (x + 2, sy + 54), card["kicker"], F(SANSB, 10), RED)
    hy = sy + 66
    lines = wrap(d, card["headline"], F(SERIFB, 14), w - 4)
    for i, ln in enumerate(lines[:2]):
        draw_text(d, (x + 2, hy + i * 15), ln, F(SERIFB, 14), INK)
    by = hy + len(lines[:2]) * 15 + 2
    for i, ln in enumerate(wrap(d, card["body"], F(SERIF, 10), w - 4)[:2]):
        draw_text(d, (x + 2, by + i * 11), ln, F(SERIF, 10), INK)


def draw_leads_row(d):
    y0 = 226
    w = 328
    for i, card in enumerate(LEADS):
        x = MX + i * (w + 6)
        draw_lead(d, x, y0, w, card)
        rect(d, x, y0, x + w, y0 + 232, outline=INK, width=1)


def draw_medium_rows(d):
    w = 195
    gap = 5
    for r in range(3):
        y0 = 460 + r * 138
        for c in range(5):
            x = MX + c * (w + gap)
            draw_medium(d, x, y0, w, MEDIUMS[r * 5 + c])
            rect(d, x, y0, x + w, y0 + 138, outline=INK, width=1)


# ------------------------------------------------- map, briefs, footer -----
# Dotted world map: land cells as (row, col0, col1) on a 76 x 11 grid.
LAND = [
    (0, 3, 19), (0, 52, 72),
    (1, 2, 21), (1, 26, 29), (1, 41, 47), (1, 50, 74),
    (2, 1, 20), (2, 40, 48), (2, 48, 75),
    (3, 2, 18), (3, 18, 21), (3, 42, 52), (3, 54, 58), (3, 58, 73),
    (4, 3, 16), (4, 19, 22), (4, 41, 54), (4, 60, 70), (4, 70, 73),
    (5, 20, 26), (5, 42, 53), (5, 62, 68), (5, 69, 72), (5, 72, 75),
    (6, 21, 27), (6, 44, 52), (6, 66, 74),
    (7, 22, 26), (7, 46, 50), (7, 68, 73),
    (8, 23, 25),
    (9, 24, 24),
]

# pin number -> (grid col, grid row, dx, dy, label, label x, label y,
# label anchor). (dx, dy) spread the drawn pin off its grid anchor so
# neighbouring pins stay readable; labels sit in clear space with a thin
# leader line from the pin. Positions are approximate by design.
PINS = [
    (1, 9, 3, -4, -5, None, 0, 0, None),
    (2, 47, 4, 5, 7, "Benghazi", 306, 914, "la"),
    (3, 53, 3, 2, -5, "Antalya", 338, 901, "la"),
    (4, 46, 2, 3, -6, None, 0, 0, None),
    (5, 62, 4, -3, 3, None, 0, 0, None),
    (6, 53, 5, 8, 10, None, 0, 0, None),
    (7, 73, 7, 3, 0, None, 0, 0, None),
    (8, 43, 2, -3, -8, None, 0, 0, None),
    (9, 10, 4, 2, 3, None, 0, 0, None),
    (10, 68, 4, -10, -3, None, 0, 0, None),
    (11, 73, 4, 3, -3, "Taipei", 428, 938, "ma"),
    (12, 38, 2, -12, -6, "London", 220, 896, "ra"),
    (13, 44, 3, 3, 3, None, 0, 0, None),
    (14, 69, 6, -2, 5, None, 0, 0, None),
    (15, 48, 6, 9, 9, None, 0, 0, None),
    (16, 72, 2, -3, -6, "Seoul", 428, 895, "ra"),
    (17, 41, 2, -8, 6, "Brussels", 248, 924, "ma"),
    (18, 50, 1, 4, -7, "Dymer", 314, 881, "ma"),
]

BRIEFS = [
    ["19 India-NZ 1st Test drawn (AP, MON)",
     "20 Sindarov gets White, G1 (FIDE, SUN)",
     "21 Taiwan bans short-selling (CNA, MON)",
     "22 Anthropic \u22121.4% $87.64 (FOOL, MON)",
     "23 Bulgari funeral in Rome (ANSA, MON)",
     "24 Trump warns Iran (FOX, SUN)",
     "25 Nigeria debt payoff 2027 (ARISE, MON)",
     "26 Liverpool beat 10-man Utd (BBC, SUN)"],
    ["27 Thitikul wins 3rd LPGA (AP, SUN)",
     "28 Visegr\u00e1d loan talks (REUTERS, MON)",
     "29 Trump hush bid revived (AP, MON)",
     "30 Monza 3\u20130 Fiorentina (LIVESCORE, MON)",
     "31 Levante draw 1\u20131 with Elche (SKY, MON)",
     "32 Lilly buys LoQus23 $725m (LAW360, MON)",
     "33 Iowa blast goes ahead Wed (WSJ, MON)"],
    ["34 Commanders 22\u201320 Bengals (AP, MON)",
     "35 Indonesia fire kills 24 (REUTERS, MON)",
     "36 White House rejects TrumpCare (AP, MON)",
     "37 90+ sign COP31 pledge (REUTERS, MON)",
     "38 Brent \u22123.5% to $89.37 (REUTERS, MON)",
     "39 Brentford rout Everton 4\u20130 (SKY, MON)",
     "40 Centrica: bills may rise 26% (BBC, SUN)"],
]


def draw_map(d):
    x0, y0, x1, y1 = MX, 890, 460, 950
    draw_text(d, (x0, 876), "WHERE IT HAPPENED \u2014 PINS 1\u201318",
              F(SANSB, 12), INK)
    rect(d, x0, y0, x1, y1, fill=MAPBG, outline=INK, width=1)
    cw, ch = (x1 - x0) / 76.0, 52.0 / 11.0
    for row, c0, c1 in LAND:
        for c in range(c0, c1 + 1):
            px = x0 + c * cw + cw / 2
            py = y0 + 4 + row * ch + ch / 2
            d.ellipse([px - 1.6, py - 1.6, px + 1.6, py + 1.6], fill=MAPDOT)
    fnt = F(SANSB, 9)
    for num, col, row, dx, dy, label, lx, ly, anchor in PINS:
        px = x0 + col * cw + cw / 2 + dx
        py = y0 + 4 + row * ch + ch / 2 + dy
        if label:
            # thin leader from the pin to its label, drawn under the pin
            d.line([(px, py), (lx, ly + 4)], fill=GREY, width=1)
        d.ellipse([px - 6, py - 6, px + 6, py + 6], fill=DARKRED,
                  outline=WHITE, width=1)
        d.text((px, py - 5), str(num), font=F(SANSB, 8), fill=WHITE,
               anchor="ma")
        if label:
            if anchor == "ra":
                draw_text(d, (lx, ly), label, fnt, INK, anchor="ra")
            elif anchor == "ma":
                draw_text(d, (lx, ly), label, fnt, INK, anchor="ma")
            else:
                draw_text(d, (lx, ly), label, fnt, INK)
    draw_text(d, (x0 + 4, y1 - 10),
              "RED NUMBERS MARK STORIES 1\u201318 \u00b7 POSITIONS APPROXIMATE",
              F(SANSB, 8), INK)


def draw_briefs(d):
    x0 = 468
    draw_text(d, (x0, 876), "ALSO ON \u2014 22 BRIEFS", F(SANSB, 12), INK)
    fnt = F(SANS, 7.5)
    for ci, col in enumerate(BRIEFS):
        cx = x0 + ci * 180
        for i, line in enumerate(col):
            draw_text(d, (cx, 888 + i * 8), line, fnt, INK)


def draw_datecheck(d):
    y0, y1 = 956, 1000
    rect(d, MX, y0, RX, y1, outline=DARKRED, width=2)
    title = "DATE CHECK \u2014 DATES AUDITED \u00b7 "
    body = ("This page covers Monday 23 November 2026. Sunday events are "
            "flagged SUN. Nvidia's 12 Nov resignation is NOT the story "
            "\u2014 its Monday return is Lead 1. Excluded: COP31 'nears "
            "deal' (false), Kryvyi Rih (20 Nov), Kerch Bridge (16\u201317 "
            "Nov), Kospi Tue rebound (+7.2%), Hormuz + Gaza (Sat 21 Nov), "
            "Vancouver 2\u20130 RSL (Sun 22 Nov), Sinaloa kingpin "
            "(Fri 20 Nov), EU\u2013Indonesia deal (Sat 21 Nov), Kenya\u2013DRC "
            "pact (Sun 22 Nov), Santos 0\u20132 Gr\u00eamio (Tue 24 Nov).")
    tf, bf = F(SANSB, 11), F(SERIF, 11)
    # wrap the body with the title occupying the start of the first line
    first_w = RX - MX - 16 - text_w(d, title, tf)
    first_line = wrap(d, body, bf, first_w)[0]
    rest = body[len(first_line) + 1:]
    lines = [first_line] + wrap(d, rest, bf, RX - MX - 16)
    draw_text(d, (MX + 8, y0 + 4), title, tf, DARKRED)
    draw_text(d, (MX + 8 + text_w(d, title, tf), y0 + 4), lines[0], bf, INK)
    for i, ln in enumerate(lines[1:3]):
        draw_text(d, (MX + 8, y0 + 4 + (i + 1) * 13), ln, bf, INK)


def draw_footer(d):
    centered(d, 512, 1002,
             "Sources: Reuters, BBC, AP, AFP, Guardian, USGS, FIFA, "
             "MENAFN, PIB \u00b7 SUN = happened Sunday \u00b7 MON = Monday "
             "23 November 2026",
             F(SANS, 10), INK)
    centered(d, 512, 1013,
             "HOW SURE: ON RECORD = official data \u00b7 REPORTED = "
             "reported by the press \u00b7 CLAIM = single-source claim",
             F(SANS, 10), INK)


def main():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    draw_top(d)
    draw_number_strip(d)
    draw_region_strip(d)
    draw_leads_row(d)
    draw_medium_rows(d)
    draw_map(d)
    draw_briefs(d)
    draw_datecheck(d)
    draw_footer(d)
    img.save("entry.png")
    print("wrote entry.png", img.size)


if __name__ == "__main__":
    main()
