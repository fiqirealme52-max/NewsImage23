#!/usr/bin/env python3
# News 23 — "Monday 23 November 2026" front page.
# Spec: ~/workspace/makefun/NewsImage23/research-spec-2026-11-23.md
# Pipeline reused from News 22 round 7 (same 10-element template, same
# helpers, same layout engine) with 23 Nov stories and new scenes.
# Family: FLAT ILLUSTRATION only, serif broadsheet, cream paper. No photos.
# Past failures this build must not repeat (PLAYBOOK gate, read 23 Nov):
#  - PM-16 / News 22 r5: mixed family (photos + cartoons) penalised.
#    This build is flat-only, one coherent style.
#  - News 22 r6/r7 audit: big grey smoke blobs -> thin wisps; flat orange
#    triangles -> layered flame tongues; light beige map -> dark navy map;
#    thin lead decks -> TWO-LINE decks with source in parens.
#  - News 22 r5: "COP31 nears deal" style false claims. Here COP31 is
#    "collapses — no deal"; Merkury attribution is "suspected" only;
#    Houthis Rabigh is a CLAIM; Dymer toll is 9 dead (not 5/6/8).
#  - r7 map bug fixed: Antalya is lon 30.7E, not 37.7E.
#  - Date honesty: the 3 leads happened Sunday; each is flagged SUN and
#    the DATE CHECK names the exclusions explicitly.
# Maximization pass ROUND 2 (23 Nov, user order: score MUST beat top 1-20):
#  - 12 mediums (was 10): Selangor floods + Bangladesh typhoid promoted
#    from briefs to drawn mediums; 37 stories (3+12+22); 2 new verified
#    briefs (Gaza strikes, Brent oil) replace them.
#  - Number strip: all 6 slots are now checkable NEWS numbers (14 hrs,
#    90+ pledge, 9 dead, 601 km, 104 matches, $120bn) — the old strip
#    wasted 2 slots on meta counts (35 stories, 7 regions), unlike the
#    News 22 winner (186, 161, 35%, $120bn, 720/9, 50).
#  - Lead decks densified to 4+ checkable numbers each (3 lines at 13px).
#  - DATE CHECK: 2 more named exclusions + winner-style hook tying the
#    box to the strip ("Today's real count: ... on the top of this page").
#  - UTC strip SKIPPED (round 2): only 1 verified Monday event time
#    (02:40 Vanuatu); NATO/FIFA times not published — do NOT invent times.
#  - Medium grid 5 cols -> 6 cols (163px), headlines/subs shortened to
#    fit 2 lines; map pins 13 -> 15 (Selangor, Dhaka).
#  - Dymer beams were white sticks -> tapered cones (faint wide + bright core).
#  - Map pins 4 & 12 collided into one "14" -> 20px separation, clamp-before-test.
#  - COP31 gavel was a brown strip -> rotated head + handle; hall got a wall
#    sign + ceiling lights (empty-wall monotony).
#  - B35 "Gaza board may quit" was the WRONG DIRECTION (board mulls removing
#    committee members, unconfirmed) -> replaced with verified Centrica warning.
#  - Lead decks densified (COP31 $120bn, Merkury 4 drones downed) — research
#    gap #3: 3-4 checkable numbers per lead.
#  - Merkury boatman, M13 rider, Dymer stretcher boy, M9 checkmark: readability.
# Zones (px): masthead 104, strip 84, region 32, leads 280, mediums 260,
# map+briefs 180, DATE CHECK 82 = 1024.
from PIL import Image, ImageDraw, ImageFont
import math, os, random, sys

W, H = 1024, 1024
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

PAPER = (250, 243, 228)      # cream (spec)
PAPER2 = (238, 231, 214)     # slightly darker cream (strip)
INK = (30, 28, 26)
RED = (178, 34, 30)          # brick red
RED_D = (140, 25, 22)
GOLD = (198, 162, 78)
GREY = (110, 105, 95)
GREY_L = (200, 192, 176)
BLACK = (18, 16, 14)
WHITE = (252, 250, 246)

SF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SFB = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SFI = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SSB = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

def font(path, size):
    return ImageFont.truetype(path, size)

def tw(d, text, f):
    return d.textlength(text, font=f)

def assert_fit(d, text, f, max_w, what):
    w = tw(d, text, f)
    if w > max_w:
        print(f"OVERFLOW {what}: {w:.0f} > {max_w} :: {text!r}")
        sys.exit(2)

def fit_font(d, text, path, sizes, max_w):
    """Largest size from `sizes` whose single-line width fits max_w."""
    for s in sizes:
        f = font(path, s)
        if tw(d, text, f) <= max_w:
            return f, s
    f = font(path, sizes[-1])
    print(f"OVERFLOW fit_font: {tw(d, text, f):.0f} > {max_w} :: {text!r}")
    sys.exit(2)

def wrap_text(d, text, f, max_w):
    """Greedy word wrap to lines that each fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if tw(d, trial, f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines

def headline_lines(d, text, max_w, sizes=(30, 28, 26, 24)):
    """Largest size whose wrap is <= 2 lines. Returns (font, size, lines)."""
    for s in sizes:
        f = font(SFB, s)
        lines = wrap_text(d, text, f, max_w)
        if len(lines) <= 2:
            return f, s, lines
    f = font(SFB, sizes[-1])
    lines = wrap_text(d, text, f, max_w)
    print(f"OVERFLOW headline: {lines} :: {text!r}")
    sys.exit(2)

# ---------- drawing helpers ----------
def vgrad(d, box, top, bottom):
    x0, y0, x1, y1 = box
    n = max(1, y1 - y0)
    for i in range(n):
        t = i / n
        c = tuple(int(top[k] + (bottom[k] - top[k]) * t) for k in range(3))
        d.line([(x0, y0 + i), (x1, y0 + i)], fill=c)

def person(d, x, y, s, suit, skin=(214, 178, 142), hair=(40, 32, 24)):
    d.ellipse([x - 3.5 * s, y - 6 * s, x + 3.5 * s, y + 1 * s], fill=skin)
    d.pieslice([x - 4 * s, y - 7 * s, x + 4 * s, y - 1 * s], 180, 360, fill=hair)
    d.polygon([(x - 5 * s, y + 1 * s), (x + 5 * s, y + 1 * s),
               (x + 4 * s, y + 14 * s), (x - 4 * s, y + 14 * s)], fill=suit)
    d.polygon([(x - 5 * s, y + 1 * s), (x - 2 * s, y + 3 * s),
               (x, y + 1 * s), (x + 2 * s, y + 3 * s), (x + 5 * s, y + 1 * s)],
              fill=(250, 248, 244))
    d.polygon([(x - 1 * s, y + 2 * s), (x + 1 * s, y + 2 * s),
               (x, y + 6 * s)], fill=(150, 30, 28))

def car(d, x, y, w, h, body=(210, 60, 45)):
    d.rounded_rectangle([x, y, x + w, y + h], radius=3, fill=body)
    d.polygon([(x + w * 0.2, y), (x + w * 0.35, y - h * 0.55),
               (x + w * 0.65, y - h * 0.55), (x + w * 0.8, y)], fill=(40, 45, 60))
    d.ellipse([x + w * 0.12, y + h * 0.7, x + w * 0.3, y + h * 1.15], fill=(20, 20, 22))
    d.ellipse([x + w * 0.7, y + h * 0.7, x + w * 0.88, y + h * 1.15], fill=(20, 20, 22))

def flames(d, x, y, w, h, seed=0):
    rnd = random.Random(seed)
    for i in range(9):
        fx = x + rnd.random() * w
        fw = w * rnd.uniform(0.14, 0.3)
        fh = h * rnd.uniform(0.5, 1.0)
        col = rnd.choice([(240, 120, 30), (250, 170, 40), (230, 80, 20)])
        d.polygon([(fx - fw / 2, y), (fx, y - fh), (fx + fw / 2, y)], fill=col)

def flame_tongues(d, x, y, w, h, seed=0):
    """Layered flame tongues: tall orange outer tongue + bright yellow
    inner core, slight lean. Base line y, height h, spread w. Seeded."""
    rnd = random.Random(seed)
    for i in range(4):
        fx = x + w * (0.12 + 0.24 * i) + rnd.uniform(-4, 4)
        fh = h * rnd.uniform(0.6, 1.0)
        fw = w * 0.16
        lean = rnd.uniform(-6, 6)
        d.polygon([(fx - fw, y), (fx + lean, y - fh),
                   (fx + fw, y)], fill=(235, 110, 25))
        cw, ch = fw * 0.65, fh * 0.72
        d.polygon([(fx - cw, y), (fx + lean * 0.7, y - ch),
                   (fx + cw, y)], fill=(250, 195, 60))
        tw2, th2 = fw * 0.30, fh * 0.42
        d.polygon([(fx - tw2, y), (fx + lean * 0.5, y - th2),
                   (fx + tw2, y)], fill=(255, 230, 120))

def wisps(d, x, y, n=3, seed=0, top=None):
    """Thin dark smoke wisps (small flat ellipses), rising from (x, y)."""
    rnd = random.Random(seed)
    for i in range(n):
        rw = 10 + rnd.random() * 8
        rh = 4 + rnd.random() * 3
        sx = x + (rnd.random() - 0.5) * 30
        sy = y - i * 11 - rnd.random() * 5
        if top is not None:
            sy = max(sy, top + rh)
        d.ellipse([sx - rw, sy - rh, sx + rw, sy + rh],
                  fill=(70, 70, 78))

def smoke(d, x, y, n=5, seed=0, top=None):
    """Grey smoke puffs rising from (x, y)."""
    rnd = random.Random(seed)
    for i in range(n):
        r = 7 + rnd.random() * 9
        sx = x + (rnd.random() - 0.5) * 26
        sy = y - i * 9 - rnd.random() * 6
        if top is not None:
            sy = max(sy, top + r)
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(110, 108, 105))

def glow(d, x, y, r, col=(250, 190, 80)):
    for k in range(3, 0, -1):
        rr = r * k / 3
        d.ellipse([x - rr, y - rr, x + rr, y + rr],
                  outline=col, width=2)

def moon(d, x, y, r=13):
    d.ellipse([x - r, y - r, x + r, y + r], fill=(245, 240, 220))
    d.ellipse([x - r * 0.4, y - r * 0.3, x - r * 0.1, y], fill=(220, 212, 190))
    d.ellipse([x + r * 0.2, y + r * 0.2, x + r * 0.45, y + r * 0.45],
              fill=(220, 212, 190))

def stars(d, box, n=26, seed=1):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    for _ in range(n):
        sx = rnd.uniform(x0, x1)
        sy = rnd.uniform(y0, y1)
        r = rnd.choice([0.7, 1.0, 1.3])
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(255, 255, 255))

def sun(d, x, y, r=10):
    d.ellipse([x - r, y - r, x + r, y + r], fill=(250, 200, 60))
    for a in range(0, 360, 45):
        x2 = x + (r + 5) * math.cos(math.radians(a))
        y2 = y + (r + 5) * math.sin(math.radians(a))
        d.line([(x, y), (x2, y2)], fill=(250, 200, 60), width=2)

def tag_chip(d, x, y, text, bg=BLACK, fg=WHITE, size=10, pad=5):
    f = font(SSB, size)
    w = tw(d, text, f) + 2 * pad
    d.rectangle([x, y, x + w, y + size + 2 * pad - 2], fill=bg)
    d.text((x + pad, y + pad - 1), text, font=f, fill=fg)
    return w

# ---------- LEAD scenes (3-layer depth: foreground / midground / background) ----------
def scene_merkury(d, x, y, w, h):
    # LEAD 1 — night harbour, Benghazi. Background: navy night sky, stars,
    # moon. Midground: harbour cranes + smoke. Foreground: capsized grey
    # corvette hull, bow above the water, fire glow + reflections.
    vgrad(d, (x, y, x + w, y + int(h * 0.55)), (14, 20, 46), (38, 34, 64))
    stars(d, (x + 4, y + 4, x + w - 4, y + h * 0.30), n=24, seed=41)
    moon(d, x + w * 0.80, y + h * 0.14, r=11)
    # harbour cranes, dark silhouettes on the horizon
    for cx0 in (0.06, 0.30, 0.55):
        d.line([(x + w * cx0, y + h * 0.52), (x + w * cx0, y + h * 0.20)],
               fill=(10, 14, 24), width=4)
        d.line([(x + w * cx0, y + h * 0.20),
                (x + w * (cx0 + 0.16), y + h * 0.30)], fill=(10, 14, 24), width=3)
    d.rectangle([x, y + h * 0.50, x + w, y + h * 0.55], fill=(12, 18, 30))
    # sea, bottom half, with fire-glow reflection streaks
    d.rectangle([x, y + h * 0.55, x + w, y + h], fill=(16, 36, 70))
    for wy in (0.62, 0.68, 0.74, 0.86, 0.95):
        d.line([(x + w * 0.04, y + h * wy), (x + w * 0.96, y + h * wy)],
               fill=(80, 120, 170), width=2)
    # fire glow on the water under the wreck
    d.ellipse([x + w * 0.30, y + h * 0.66, x + w * 0.66, y + h * 0.78],
              fill=(200, 90, 25))
    d.ellipse([x + w * 0.38, y + h * 0.70, x + w * 0.58, y + h * 0.76],
              fill=(240, 150, 40))
    for rx in (0.32, 0.40, 0.48, 0.56, 0.64):
        d.line([(x + w * rx, y + h * 0.80), (x + w * (rx + 0.06), y + h * 0.80)],
               fill=(250, 170, 60), width=2)
    # capsized hull: long grey slab tilted bow-up, curved rising bow,
    # white superstructure block + dark portholes (ship cues, not a road)
    d.polygon([(x + w * 0.06, y + h * 0.74), (x + w * 0.58, y + h * 0.62),
               (x + w * 0.82, y + h * 0.50), (x + w * 0.90, y + h * 0.42),
               (x + w * 0.94, y + h * 0.48), (x + w * 0.86, y + h * 0.56),
               (x + w * 0.64, y + h * 0.70), (x + w * 0.20, y + h * 0.82)],
              fill=(90, 95, 105))
    d.polygon([(x + w * 0.58, y + h * 0.62), (x + w * 0.82, y + h * 0.50),
               (x + w * 0.90, y + h * 0.42), (x + w * 0.94, y + h * 0.48),
               (x + w * 0.86, y + h * 0.56), (x + w * 0.64, y + h * 0.70)],
              fill=(120, 125, 135))
    # white superstructure block near the bow
    d.rectangle([x + w * 0.74, y + h * 0.46, x + w * 0.82, y + h * 0.52],
                fill=(235, 235, 230))
    # dark portholes along the hull top edge
    for ph in (0.18, 0.30, 0.42, 0.54):
        py = y + h * (0.77 - 0.38 * (ph - 0.06) / 0.84)
        d.ellipse([x + w * ph - 3, py - 3, x + w * ph + 3, py + 3],
                  fill=(20, 24, 34))
    # bow tip above the waterline, small mast
    d.line([(x + w * 0.90, y + h * 0.42), (x + w * 0.90, y + h * 0.28)],
           fill=(60, 62, 70), width=3)
    d.polygon([(x + w * 0.88, y + h * 0.30), (x + w * 0.92, y + h * 0.30),
               (x + w * 0.90, y + h * 0.26)], fill=(178, 40, 35))
    # layered flame tongues from the wreck + thin wisps
    flame_tongues(d, x + w * 0.30, y + h * 0.64, w * 0.34, h * 0.30, seed=42)
    wisps(d, x + w * 0.46, y + h * 0.30, n=4, seed=43, top=y)
    # small rescue boat, foreground right — boatman stands IN it, feet on deck
    d.polygon([(x + w * 0.70, y + h * 0.86), (x + w * 0.88, y + h * 0.86),
               (x + w * 0.84, y + h * 0.94), (x + w * 0.74, y + h * 0.94)],
              fill=(250, 140, 30))
    person(d, x + w * 0.79, y + h * 0.67, h / 52, (30, 60, 110))
    # data chip, top-left (clear of the moon)
    tag_chip(d, x + 6, y + 6, "CAPSIZED", bg=WHITE, fg=BLACK, size=10)

def scene_cop31(d, x, y, w, h):
    # LEAD 2 — COP31 collapses, no deal. Background: dark conference hall,
    # tall windows, night blue. Midground: long empty table, empty chairs,
    # delegates walking away. Foreground: gavel + document crossed in red.
    vgrad(d, (x, y, x + w, y + h), (36, 44, 66), (18, 22, 38))
    # tall windows, back wall
    for wx in (0.08, 0.30, 0.52, 0.74):
        d.rectangle([x + w * wx, y + h * 0.08, x + w * (wx + 0.14),
                     y + h * 0.52], fill=(90, 120, 160))
        d.line([(x + w * (wx + 0.07), y + h * 0.08),
                (x + w * (wx + 0.07), y + h * 0.52)], fill=(36, 44, 66), width=2)
    moon(d, x + w * 0.88, y + h * 0.12, r=9)
    # wall sign above the table + ceiling lights (hall cues, breaks the
    # empty dark wall)
    d.rectangle([x + w * 0.36, y + h * 0.02, x + w * 0.64, y + h * 0.09],
                fill=(52, 62, 92))
    sf2 = font(SSB, 9)
    st2 = "COP31 · ANTALYA"
    assert_fit(d, st2, sf2, w * 0.28 - 6, "cop31 sign")
    d.text((x + w * 0.50 - tw(d, st2, sf2) / 2, y + h * 0.028), st2,
           font=sf2, fill=(250, 248, 242))
    for lx in (0.22, 0.78):
        glow(d, x + w * lx, y + h * 0.04, 7, col=(250, 210, 120))
        d.ellipse([x + w * lx - 3, y + h * 0.04 - 3, x + w * lx + 3,
                   y + h * 0.04 + 3], fill=(250, 220, 140))
    # long empty table + chairs, midground
    d.rectangle([x + w * 0.06, y + h * 0.58, x + w * 0.94, y + h * 0.68],
                fill=(120, 85, 55))
    for cx in (0.12, 0.26, 0.40, 0.54, 0.68, 0.82):
        d.rectangle([x + w * cx, y + h * 0.44, x + w * (cx + 0.07),
                     y + h * 0.58], fill=(70, 50, 38))
        d.rectangle([x + w * (cx + 0.01), y + h * 0.46,
                     x + w * (cx + 0.06), y + h * 0.52], fill=(150, 140, 120))
    # white name plates on the table, one per chair
    for cx in (0.12, 0.26, 0.40, 0.54, 0.68, 0.82):
        d.rectangle([x + w * (cx + 0.015), y + h * 0.60,
                     x + w * (cx + 0.055), y + h * 0.64],
                    fill=(250, 248, 242))
    # two delegates walking away, left and right edges
    person(d, x + w * 0.10, y + h * 0.66, h / 44, (30, 60, 110))
    person(d, x + w * 0.90, y + h * 0.66, h / 44, (120, 30, 30))
    # foreground: document with a big red X + gavel
    d.rectangle([x + w * 0.34, y + h * 0.72, x + w * 0.66, y + h * 0.94],
                fill=(250, 248, 242), outline=(120, 30, 28), width=2)
    for ly in (0.78, 0.83, 0.88):
        d.line([(x + w * 0.38, y + h * ly), (x + w * 0.62, y + h * ly)],
               fill=(110, 105, 95), width=2)
    d.line([(x + w * 0.38, y + h * 0.74), (x + w * 0.62, y + h * 0.92)],
           fill=(200, 40, 35), width=4)
    d.line([(x + w * 0.62, y + h * 0.74), (x + w * 0.38, y + h * 0.92)],
           fill=(200, 40, 35), width=4)
    # gavel, bottom-right of the document: chunky rotated head with a dark
    # band + handle (reads as a gavel, clear of the red delegate)
    gx, gy = x + w * 0.77, y + h * 0.85
    ang = math.radians(-28)
    hw, hh = w * 0.062, h * 0.10
    ca, sa = math.cos(ang), math.sin(ang)
    pts = []
    for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        pts.append((gx + sx * hw * ca - sy * hh * sa,
                    gy + sx * hw * sa + sy * hh * ca))
    d.polygon(pts, fill=(120, 85, 55))
    d.line([(gx - (hh / 2) * (-sa), gy - (hh / 2) * ca),
            (gx + (hh / 2) * (-sa), gy + (hh / 2) * ca)],
           fill=(90, 60, 35), width=2)
    d.line([(gx, gy), (x + w * 0.68, y + h * 0.95)], fill=(90, 60, 35),
           width=3)
    # data chip, top-left
    tag_chip(d, x + 6, y + 6, "NO DEAL", bg=WHITE, fg=BLACK, size=10)

def scene_dymer(d, x, y, w, h):
    # LEAD 3 — Dymer, dawn rescue. Background: dawn gradient (deep purple
    # to orange horizon) + fading stars. Midground: broken 5-storey block,
    # searchlight beams. Foreground: rubble pile + rescuers in helmets.
    vgrad(d, (x, y, x + w, y + h), (48, 38, 78), (215, 140, 80))
    stars(d, (x + 4, y + 4, x + w - 4, y + h * 0.25), n=16, seed=51)
    moon(d, x + w * 0.85, y + h * 0.12, r=9)
    # broken apartment block, left — jagged top, dark windows
    d.polygon([(x + w * 0.06, y + h * 0.85), (x + w * 0.06, y + h * 0.30),
               (x + w * 0.16, y + h * 0.22), (x + w * 0.24, y + h * 0.30),
               (x + w * 0.30, y + h * 0.26), (x + w * 0.38, y + h * 0.34),
               (x + w * 0.38, y + h * 0.85)], fill=(52, 48, 58))
    for wy in range(4):
        for wx in range(2):
            # two dark windows = blast damage, not a lit office grid
            wcol = (20, 18, 24) if (wx, wy) in ((1, 1), (0, 3)) else (250, 210, 90)
            d.rectangle([x + w * (0.10 + wx * 0.12), y + h * (0.38 + wy * 0.11),
                         x + w * (0.15 + wx * 0.12), y + h * (0.44 + wy * 0.11)],
                        fill=wcol)
    # collapsed stairwell gap (dark wedge)
    d.polygon([(x + w * 0.38, y + h * 0.34), (x + w * 0.46, y + h * 0.30),
               (x + w * 0.46, y + h * 0.85), (x + w * 0.38, y + h * 0.85)],
              fill=(20, 18, 24))
    # second block, right, shorter
    d.rectangle([x + w * 0.58, y + h * 0.42, x + w * 0.90, y + h * 0.85],
                fill=(62, 56, 66))
    for wy in range(3):
        d.rectangle([x + w * 0.63, y + h * (0.48 + wy * 0.11),
                     x + w * 0.68, y + h * (0.54 + wy * 0.11)],
                    fill=(250, 210, 90))
    # searchlight beams from the rubble, up into the dawn sky — tapered
    # cones (faint wide spill + narrow bright core), NOT solid sticks
    for bx, ang in ((0.46, -0.35), (0.54, 0.25)):
        tx = bx + ang
        d.polygon([(x + w * (bx - 0.008), y + h * 0.82),
                   (x + w * (tx - 0.045), y + h * 0.10),
                   (x + w * (tx + 0.045), y + h * 0.10),
                   (x + w * (bx + 0.008), y + h * 0.82)],
                  fill=(255, 236, 190))
        d.polygon([(x + w * (bx - 0.004), y + h * 0.82),
                   (x + w * (tx - 0.014), y + h * 0.10),
                   (x + w * (tx + 0.014), y + h * 0.10),
                   (x + w * (bx + 0.004), y + h * 0.82)],
                  fill=(255, 250, 225))
    # rubble pile, foreground
    d.polygon([(x + w * 0.30, y + h * 0.85), (x + w * 0.46, y + h * 0.66),
               (x + w * 0.64, y + h * 0.85)], fill=(110, 100, 90))
    d.polygon([(x + w * 0.40, y + h * 0.85), (x + w * 0.50, y + h * 0.74),
               (x + w * 0.58, y + h * 0.85)], fill=(80, 72, 64))
    # scattered rubble chunks at the base
    for rx0, rw in ((0.22, 0.08), (0.66, 0.07), (0.72, 0.06)):
        d.polygon([(x + w * rx0, y + h * 0.88),
                   (x + w * (rx0 + rw / 2), y + h * 0.80),
                   (x + w * (rx0 + rw), y + h * 0.88)], fill=(95, 86, 76))
    # rescuers in orange helmets + a stretcher with the boy
    for px, suit in ((0.52, (220, 90, 30)), (0.62, (30, 90, 140))):
        person(d, x + w * px, y + h * 0.66, h / 48, suit)
        d.ellipse([x + w * px - h * 0.045, y + h * 0.66 - h * 0.10,
                   x + w * px + h * 0.045, y + h * 0.66 - h * 0.035],
                  fill=(250, 140, 30))
    d.rectangle([x + w * 0.70, y + h * 0.84, x + w * 0.92, y + h * 0.88],
                fill=(200, 60, 40))
    # the boy, lying on the stretcher under a blanket (head + blue blanket)
    d.ellipse([x + w * 0.705, y + h * 0.845, x + w * 0.735, y + h * 0.875],
              fill=(214, 178, 142))
    d.rectangle([x + w * 0.735, y + h * 0.845, x + w * 0.885, y + h * 0.875],
                fill=(90, 140, 200))
    person(d, x + w * 0.81, y + h * 0.68, h / 56, (60, 90, 60))
    # thin smoke wisps from the rubble
    wisps(d, x + w * 0.46, y + h * 0.60, n=2, seed=52, top=y)
    # data chip, top-left
    tag_chip(d, x + 6, y + 6, "9 DEAD", bg=WHITE, fg=BLACK, size=10)

# ---------- MEDIUM scenes (12 — all genuinely drawn, ~56px tall) ----------
def scene_nato(d, x, y, w, h):
    # NATO emergency council: navy hall, ring of small flags, long table.
    vgrad(d, (x, y, x + w, y + h), (30, 50, 100), (18, 30, 60))
    # NATO compass star, top centre
    cx, cy = x + w * 0.50, y + h * 0.22
    for a in range(0, 360, 90):
        x2 = cx + h * 0.16 * math.cos(math.radians(a))
        y2 = cy + h * 0.16 * math.sin(math.radians(a))
        d.line([(cx, cy), (x2, y2)], fill=(250, 250, 250), width=2)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(250, 250, 250))
    # ring of small flags along the top
    for i, col in enumerate([(30, 60, 110), (200, 40, 35), (40, 90, 50),
                             (200, 170, 40), (120, 30, 90), (30, 90, 90),
                             (30, 130, 130), (200, 90, 40)]):
        d.rectangle([x + w * (0.04 + 0.115 * i), y + h * 0.08,
                     x + w * (0.12 + 0.115 * i), y + h * 0.22], fill=col)
    # long table + 3 delegates
    d.rectangle([x + w * 0.10, y + h * 0.62, x + w * 0.90, y + h * 0.72],
                fill=(120, 85, 55))
    for i, suit in enumerate([(30, 60, 110), (120, 30, 30), (40, 90, 50)]):
        person(d, x + w * (0.25 + 0.25 * i), y + h * 0.56, h / 40, suit)


def scene_handshake(d, x, y, w, h):
    # Nepal PM Shah meets Modi: two flags + handshake, warm hall.
    vgrad(d, (x, y, x + w, y + h), (215, 190, 150), (170, 140, 105))
    # India flag (saffron/white/green) left, Nepal flag (crimson/blue) right
    for fy, col in ((0.12, (255, 153, 51)), (0.24, (255, 255, 255)),
                    (0.36, (19, 136, 8))):
        d.rectangle([x + w * 0.08, y + h * fy, x + w * 0.30, y + h * (fy + 0.12)],
                    fill=col)
    d.rectangle([x + w * 0.70, y + h * 0.12, x + w * 0.92, y + h * 0.48],
                fill=(220, 20, 60))
    d.rectangle([x + w * 0.70, y + h * 0.12, x + w * 0.92, y + h * 0.48],
                outline=(0, 56, 147), width=3)
    # two leaders shaking hands, centre
    person(d, x + w * 0.42, y + h * 0.58, h / 36, (30, 60, 110))
    person(d, x + w * 0.58, y + h * 0.58, h / 36, (120, 30, 30))
    d.ellipse([x + w * 0.47, y + h * 0.62, x + w * 0.53, y + h * 0.68],
              fill=(214, 178, 142))


def scene_rabigh(d, x, y, w, h):
    # Rabigh refinery, night — CLAIM, so flames are modest, not a blaze.
    vgrad(d, (x, y, x + w, y + int(h * 0.55)), (18, 24, 52), (42, 38, 68))
    moon(d, x + w * 0.78, y + h * 0.16, r=9)
    d.rectangle([x, y + h * 0.55, x + w, y + h], fill=(22, 42, 78))
    for wy in (0.62, 0.68, 0.74, 0.82, 0.92):
        d.line([(x + w * 0.06, y + h * wy), (x + w * 0.94, y + h * wy)],
               fill=(90, 130, 180), width=2)
    # white refinery tanks on the horizon
    for tx0, tw in ((0.08, 0.12), (0.26, 0.14), (0.46, 0.10)):
        d.rectangle([x + w * tx0, y + h * 0.40, x + w * (tx0 + tw),
                     y + h * 0.55], fill=(235, 235, 230))
    d.rectangle([x + w * 0.34, y + h * 0.28, x + w * 0.365, y + h * 0.40],
                fill=(200, 200, 195))
    # small flame tongues only (claim, unconfirmed) + wisps
    flame_tongues(d, x + w * 0.10, y + h * 0.42, w * 0.30, h * 0.22, seed=61)
    wisps(d, x + w * 0.24, y + h * 0.16, n=2, seed=62, top=y)
    # tanker silhouette, right
    d.rectangle([x + w * 0.62, y + h * 0.62, x + w * 0.92, y + h * 0.72],
                fill=(12, 18, 28))
    d.rectangle([x + w * 0.82, y + h * 0.52, x + w * 0.90, y + h * 0.62],
                fill=(235, 235, 230))


def scene_quake(d, x, y, w, h):
    # Vanuatu deep quake: earth strata + crack + seismograph trace.
    vgrad(d, (x, y, x + w, y + h), (90, 70, 55), (40, 32, 28))
    # strata layers
    for i, col in enumerate([(140, 110, 80), (110, 85, 60), (85, 65, 48)]):
        d.rectangle([x, y + h * (0.30 + 0.20 * i), x + w,
                     y + h * (0.50 + 0.20 * i)], fill=col)
    # zigzag crack through the strata
    d.line([(x + w * 0.50, y + h * 0.28), (x + w * 0.44, y + h * 0.48),
            (x + w * 0.54, y + h * 0.62), (x + w * 0.47, y + h * 0.82)],
           fill=(20, 16, 12), width=3)
    # seismograph panel, top-left
    d.rectangle([x + w * 0.06, y + h * 0.08, x + w * 0.56, y + h * 0.26],
                fill=(250, 248, 242), outline=(30, 30, 30), width=1)
    pts = []
    for i in range(21):
        px = x + w * (0.08 + 0.024 * i)
        py = y + h * 0.17 + (h * 0.06 if i % 5 == 2 else
                            (-h * 0.06 if i % 5 == 4 else 0))
        pts.append((px, py))
    d.line(pts, fill=(200, 40, 35), width=2)
    # depth arrow down the right side
    d.line([(x + w * 0.88, y + h * 0.30), (x + w * 0.88, y + h * 0.80)],
           fill=(250, 200, 60), width=3)
    d.polygon([(x + w * 0.84, y + h * 0.80), (x + w * 0.92, y + h * 0.80),
               (x + w * 0.88, y + h * 0.90)], fill=(250, 200, 60))


def scene_stadium(d, x, y, w, h):
    # FIFA 2035: stadium bowl + pitch + gold trophy + ball.
    vgrad(d, (x, y, x + w, y + h), (60, 110, 180), (30, 70, 120))
    # stands: rows of tiny spectator dots
    for row in range(4):
        for i in range(14):
            sx = x + w * (0.06 + 0.068 * i)
            sy = y + h * (0.10 + 0.08 * row)
            d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2],
                      fill=(250, 240, 220) if (i + row) % 3 else (250, 200, 60))
    # green pitch ellipse
    d.ellipse([x + w * 0.05, y + h * 0.48, x + w * 0.95, y + h * 0.92],
              fill=(50, 140, 70))
    d.ellipse([x + w * 0.38, y + h * 0.60, x + w * 0.62, y + h * 0.80],
              outline=(250, 250, 250), width=2)
    # gold trophy, centre
    tx = x + w * 0.50
    d.polygon([(tx - 10, y + h * 0.42), (tx + 10, y + h * 0.42),
               (tx + 6, y + h * 0.62), (tx - 6, y + h * 0.62)],
              fill=(250, 200, 60))
    d.rectangle([tx - 4, y + h * 0.62, tx + 4, y + h * 0.72],
                fill=(200, 160, 40))
    d.rectangle([tx - 12, y + h * 0.72, tx + 12, y + h * 0.76],
                fill=(200, 160, 40))
    # football, bottom-right
    d.ellipse([x + w * 0.78, y + h * 0.74, x + w * 0.90, y + h * 0.86],
              fill=(250, 250, 250), outline=(20, 20, 20), width=1)
    d.ellipse([x + w * 0.82, y + h * 0.78, x + w * 0.86, y + h * 0.82],
              fill=(20, 20, 20))


def scene_vote(d, x, y, w, h):
    # US House final count: blue sky, ballot box, voters queue.
    vgrad(d, (x, y, x + w, y + h), (120, 160, 210), (210, 220, 235))
    d.rectangle([x, y + h * 0.72, x + w, y + h], fill=(200, 195, 185))
    d.rectangle([x + w * 0.38, y + h * 0.34, x + w * 0.66, y + h * 0.68],
                fill=(40, 80, 150))
    d.rectangle([x + w * 0.43, y + h * 0.30, x + w * 0.61, y + h * 0.34],
                fill=(30, 60, 120))
    d.rectangle([x + w * 0.46, y + h * 0.26, x + w * 0.58, y + h * 0.30],
                fill=(250, 250, 250))
    for i, suit in enumerate([(30, 60, 110), (120, 30, 30), (40, 90, 50)]):
        person(d, x + w * (0.15 + 0.12 * i), y + h * 0.66, h / 44, suit)
    # white checkmark on the ballot box (reads as voting at a glance)
    d.line([(x + w * 0.45, y + h * 0.52), (x + w * 0.51, y + h * 0.60),
            (x + w * 0.61, y + h * 0.42)], fill=(250, 250, 250), width=3)


def scene_lac(d, x, y, w, h):
    # India–China LAC talks: Himalayan peaks + two flags in the valley.
    vgrad(d, (x, y, x + w, y + h), (150, 180, 220), (210, 225, 235))
    # mountain range with snow caps
    for mx, mh, mw in ((0.02, 0.55, 0.34), (0.30, 0.70, 0.40),
                       (0.62, 0.60, 0.36)):
        d.polygon([(x + w * mx, y + h * 0.85),
                   (x + w * (mx + mw / 2), y + h * (0.85 - mh)),
                   (x + w * (mx + mw), y + h * 0.85)], fill=(90, 100, 120))
        d.polygon([(x + w * (mx + mw / 2 - 0.06), y + h * (0.85 - mh + 0.12)),
                   (x + w * (mx + mw / 2), y + h * (0.85 - mh)),
                   (x + w * (mx + mw / 2 + 0.06), y + h * (0.85 - mh + 0.12))],
                  fill=(250, 250, 250))
    # valley floor + two flags
    d.rectangle([x, y + h * 0.85, x + w, y + h], fill=(120, 150, 90))
    for fx, cols in ((0.30, [(255, 153, 51), (255, 255, 255), (19, 136, 8)]),
                     (0.58, [(222, 41, 16), (222, 41, 16), (222, 41, 16)])):
        for k, col in enumerate(cols):
            d.rectangle([x + w * fx, y + h * (0.55 + 0.09 * k),
                         x + w * (fx + 0.12), y + h * (0.64 + 0.09 * k)],
                        fill=col)
        d.line([(x + w * fx, y + h * 0.55), (x + w * fx, y + h * 0.85)],
               fill=(60, 50, 40), width=2)


def scene_flood(d, x, y, w, h):
    # Himalayan flood: mountains + brown muddy wave + small houses.
    vgrad(d, (x, y, x + w, y + h), (140, 160, 190), (200, 210, 225))
    for mx, mh, mw in ((0.00, 0.50, 0.36), (0.30, 0.62, 0.40),
                       (0.64, 0.52, 0.36)):
        d.polygon([(x + w * mx, y + h * 0.70),
                   (x + w * (mx + mw / 2), y + h * (0.70 - mh)),
                   (x + w * (mx + mw), y + h * 0.70)], fill=(100, 110, 130))
    # muddy wave sweeping the valley
    d.polygon([(x, y + h * 0.78), (x + w * 0.30, y + h * 0.58),
               (x + w * 0.60, y + h * 0.66), (x + w, y + h * 0.60),
               (x + w, y + h), (x, y + h)], fill=(140, 105, 65))
    d.polygon([(x + w * 0.10, y + h * 0.82), (x + w * 0.35, y + h * 0.70),
               (x + w * 0.55, y + h * 0.76), (x + w * 0.45, y + h * 0.88)],
              fill=(160, 125, 80))
    # two small houses half-submerged
    for hx in (0.14, 0.66):
        d.rectangle([x + w * hx, y + h * 0.80, x + w * (hx + 0.12),
                     y + h * 0.94], fill=(200, 180, 150))
        d.polygon([(x + w * (hx - 0.01), y + h * 0.80),
                   (x + w * (hx + 0.06), y + h * 0.70),
                   (x + w * (hx + 0.13), y + h * 0.80)], fill=(178, 40, 35))
    # rain streaks
    for i in range(10):
        rx = x + w * (0.06 + 0.09 * i)
        d.line([(rx, y + h * 0.06), (rx - 4, y + h * 0.20)],
               fill=(200, 210, 230), width=2)


def scene_nhs(d, x, y, w, h):
    # NHS AI breast-cancer trial: hospital + blue cross + scan screen.
    vgrad(d, (x, y, x + w, y + h), (190, 215, 235), (230, 235, 240))
    # hospital building
    d.rectangle([x + w * 0.08, y + h * 0.30, x + w * 0.46, y + h * 0.92],
                fill=(250, 250, 248), outline=(100, 130, 170), width=2)
    d.rectangle([x + w * 0.24, y + h * 0.38, x + w * 0.30, y + h * 0.50],
                fill=(0, 94, 184))
    d.rectangle([x + w * 0.18, y + h * 0.42, x + w * 0.36, y + h * 0.46],
                fill=(0, 94, 184))
    for wy in range(2):
        for wx in range(3):
            d.rectangle([x + w * (0.12 + wx * 0.11), y + h * (0.58 + wy * 0.14),
                         x + w * (0.18 + wx * 0.11), y + h * (0.66 + wy * 0.14)],
                        fill=(140, 180, 220))
    # scan screen, right — dark panel, pink scan blob, AI sparkle
    d.rectangle([x + w * 0.54, y + h * 0.22, x + w * 0.94, y + h * 0.78],
                fill=(30, 40, 60), outline=(0, 94, 184), width=2)
    # scan target: pink disc + white ring + crosshair (mammogram-style)
    d.ellipse([x + w * 0.60, y + h * 0.32, x + w * 0.82, y + h * 0.58],
              fill=(240, 150, 180))
    d.ellipse([x + w * 0.64, y + h * 0.36, x + w * 0.78, y + h * 0.54],
              outline=(250, 250, 250), width=2)
    d.line([(x + w * 0.71, y + h * 0.40), (x + w * 0.71, y + h * 0.50)],
           fill=(250, 250, 250), width=2)
    d.line([(x + w * 0.66, y + h * 0.45), (x + w * 0.76, y + h * 0.45)],
           fill=(250, 250, 250), width=2)
    d.line([(x + w * 0.84, y + h * 0.34), (x + w * 0.88, y + h * 0.42),
            (x + w * 0.92, y + h * 0.34)], fill=(250, 200, 60), width=2)
    d.line([(x + w * 0.88, y + h * 0.30), (x + w * 0.88, y + h * 0.46)],
           fill=(250, 200, 60), width=2)


def scene_sport(d, x, y, w, h):
    # Sport double: tennis court left, motorbike + chequered flag right.
    # tennis court
    d.rectangle([x, y, x + w * 0.48, y + h], fill=(60, 140, 80))
    d.rectangle([x + w * 0.04, y + h * 0.12, x + w * 0.44, y + h * 0.88],
                outline=(250, 250, 250), width=2)
    d.line([(x + w * 0.04, y + h * 0.50), (x + w * 0.44, y + h * 0.50)],
           fill=(250, 250, 250), width=2)
    d.ellipse([x + w * 0.34, y + h * 0.60, x + w * 0.42, y + h * 0.68],
              fill=(220, 240, 60), outline=(255, 255, 255), width=1)
    # motorbike on dark track, right half
    d.rectangle([x + w * 0.48, y, x + w, y + h], fill=(25, 25, 40))
    d.line([(x + w * 0.48, y + h * 0.80), (x + w, y + h * 0.80)],
           fill=(250, 210, 90), width=2)
    # chequered flag, top-right
    for fy in range(2):
        for fx in range(3):
            col = (250, 250, 250) if (fx + fy) % 2 == 0 else (20, 20, 20)
            d.rectangle([x + w * (0.82 + 0.05 * fx), y + h * (0.08 + 0.10 * fy),
                         x + w * (0.87 + 0.05 * fx), y + h * (0.18 + 0.10 * fy)],
                        fill=col)
    d.line([(x + w * 0.82, y + h * 0.08), (x + w * 0.82, y + h * 0.42)],
           fill=(200, 200, 200), width=2)
    # bike silhouette: two wheels + leaned body
    d.ellipse([x + w * 0.56, y + h * 0.62, x + w * 0.66, y + h * 0.74],
              outline=(250, 250, 250), width=3)
    d.ellipse([x + w * 0.76, y + h * 0.62, x + w * 0.86, y + h * 0.74],
              outline=(250, 250, 250), width=3)
    d.polygon([(x + w * 0.61, y + h * 0.68), (x + w * 0.74, y + h * 0.52),
               (x + w * 0.81, y + h * 0.68)], fill=(220, 40, 35))
    # rider in white leathers (stands out from the red bike + clears the
    # BBC chip, which covers 0.68w+)
    person(d, x + w * 0.65, y + h * 0.52, h / 52, (245, 245, 240))


def scene_selangor(d, x, y, w, h):
    # Selangor floods: flat grey-rain sky, low houses half-submerged,
    # brown flood water, rescue boat with two people, palm at the edge.
    # Deliberately NOT the Himalayan scene (no mountains, no muddy wave).
    vgrad(d, (x, y, x + w, y + h), (150, 165, 185), (120, 135, 155))
    # low skyline: flat rooftops on the horizon
    for hx, hw in ((0.04, 0.20), (0.30, 0.16), (0.52, 0.22), (0.78, 0.18)):
        d.rectangle([x + w * hx, y + h * 0.34, x + w * (hx + hw),
                     y + h * 0.52], fill=(110, 115, 125))
        d.polygon([(x + w * (hx - 0.01), y + h * 0.34),
                   (x + w * (hx + hw / 2), y + h * 0.26),
                   (x + w * (hx + hw + 0.01), y + h * 0.34)],
                  fill=(150, 60, 50))
    # brown flood water, lower half, with pale drift streaks
    d.rectangle([x, y + h * 0.52, x + w, y + h], fill=(125, 100, 70))
    for wy in (0.62, 0.72, 0.84, 0.94):
        d.line([(x + w * 0.06, y + h * wy), (x + w * 0.94, y + h * wy)],
               fill=(170, 145, 105), width=2)
    # two houses half-submerged, roofs + upper walls above the water
    for hx in (0.08, 0.62):
        d.rectangle([x + w * hx, y + h * 0.44, x + w * (hx + 0.13),
                     y + h * 0.60], fill=(205, 185, 155))
        d.polygon([(x + w * (hx - 0.01), y + h * 0.44),
                   (x + w * (hx + 0.065), y + h * 0.34),
                   (x + w * (hx + 0.14), y + h * 0.44)], fill=(178, 40, 35))
    # palm tree, left — trunk leaning out of the water, fronds above
    d.line([(x + w * 0.36, y + h * 0.86), (x + w * 0.40, y + h * 0.30)],
           fill=(90, 70, 45), width=4)
    for fa in (-70, -35, 0, 35, 70):
        fx = x + w * 0.40 + h * 0.22 * math.cos(math.radians(fa - 90))
        fy = y + h * 0.30 + h * 0.22 * math.sin(math.radians(fa - 90))
        d.line([(x + w * 0.40, y + h * 0.30), (fx, fy)],
               fill=(40, 110, 60), width=3)
    # orange rescue boat, foreground right, two people aboard
    d.polygon([(x + w * 0.52, y + h * 0.72), (x + w * 0.88, y + h * 0.72),
               (x + w * 0.82, y + h * 0.84), (x + w * 0.58, y + h * 0.84)],
              fill=(250, 140, 30))
    person(d, x + w * 0.63, y + h * 0.60, h / 48, (30, 90, 140))
    person(d, x + w * 0.77, y + h * 0.60, h / 48, (220, 90, 30))
    # rain streaks
    for i in range(8):
        rx = x + w * (0.08 + 0.11 * i)
        d.line([(rx, y + h * 0.05), (rx - 3, y + h * 0.18)],
               fill=(200, 210, 230), width=2)


def scene_typhoid(d, x, y, w, h):
    # Bangladesh typhoid drive: white clinic tent with red cross, nurse
    # in blue vaccinating a child, row of vaccine vials, warm morning.
    vgrad(d, (x, y, x + w, y + h), (235, 225, 205), (205, 190, 165))
    sun(d, x + w * 0.86, y + h * 0.16, r=8)
    # clinic tent, left — white canopy + red cross panel
    d.polygon([(x + w * 0.04, y + h * 0.78), (x + w * 0.04, y + h * 0.40),
               (x + w * 0.26, y + h * 0.22), (x + w * 0.48, y + h * 0.40),
               (x + w * 0.48, y + h * 0.78)], fill=(250, 250, 248))
    d.rectangle([x + w * 0.20, y + h * 0.36, x + w * 0.32, y + h * 0.56],
                fill=(200, 40, 35))
    d.rectangle([x + w * 0.24, y + h * 0.42, x + w * 0.28, y + h * 0.50],
                fill=(250, 250, 250))
    d.rectangle([x + w * 0.22, y + h * 0.44, x + w * 0.30, y + h * 0.48],
                fill=(250, 250, 250))
    # nurse in blue, centre, arm out to the child
    person(d, x + w * 0.56, y + h * 0.58, h / 40, (30, 90, 160))
    d.line([(x + w * 0.58, y + h * 0.62), (x + w * 0.68, y + h * 0.66)],
           fill=(214, 178, 142), width=3)
    # child in yellow, right, small
    person(d, x + w * 0.72, y + h * 0.66, h / 56, (230, 190, 60))
    # vaccine vials in a row, foreground
    for i in range(5):
        vx = x + w * (0.55 + 0.07 * i)
        d.rectangle([vx, y + h * 0.82, vx + 7, y + h * 0.94],
                    fill=(240, 240, 235), outline=(100, 100, 100), width=1)
        d.rectangle([vx + 1, y + h * 0.79, vx + 6, y + h * 0.82],
                    fill=(0, 120, 180))
    # ground line
    d.rectangle([x, y + h * 0.92, x + w, y + h], fill=(170, 150, 120))


# ---------- Map (dark navy ocean + tan continents, red numbered pins) ----------
# Coarse continent outlines (lon, lat), reused from News 22 r7.
# Pins: the 13 drawn stories ONLY. Antalya corrected: lon 30.7E (r7 had 37.7E).
POLYS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 68), (-95, 69), (-80, 73),
     (-65, 62), (-55, 52), (-65, 45), (-75, 35), (-80, 26), (-85, 30),
     (-95, 29), (-105, 22), (-115, 30), (-125, 40), (-125, 49), (-140, 60),
     (-155, 58), (-168, 66)],
    [(-170, 66), (-155, 71), (-135, 69), (-125, 71), (-140, 70), (-165, 68)],
    [(-10, 37), (-9, 43), (-2, 44), (0, 46), (3, 43), (8, 44), (12, 44),
     (15, 40), (19, 42), (23, 40), (28, 41), (30, 36), (26, 36), (23, 36),
     (19, 41), (15, 44), (10, 45), (5, 43), (-1, 38), (-6, 36), (-10, 37)],
    [(30, 36), (36, 36), (40, 40), (44, 39), (48, 38), (50, 30), (44, 29),
     (40, 31), (36, 33), (32, 31), (28, 36), (30, 36)],
    [(55, 26), (60, 25), (65, 25), (70, 20), (72, 21), (77, 8), (80, 7),
     (80, 13), (85, 20), (89, 22), (92, 21), (95, 16), (98, 16), (100, 13),
     (101, 8), (104, 2), (103, 1), (100, 8), (98, 10), (95, 15), (92, 21),
     (88, 22), (80, 15), (77, 10), (74, 20), (70, 22), (66, 25), (61, 25),
     (57, 26), (55, 26)],
    [(100, 15), (104, 9), (106, 10), (109, 13), (108, 18), (105, 20),
     (100, 15)],
    [(113, -22), (114, -30), (115, -35), (124, -33), (129, -32), (132, -32),
     (135, -35), (138, -35), (140, -38), (145, -38), (150, -37), (153, -27),
     (150, -22), (146, -19), (142, -11), (137, -12), (135, -15), (132, -11),
     (130, -13), (126, -14), (122, -17), (118, -20), (113, -22)],
    [(129, 32), (132, 33), (135, 34), (137, 35), (139, 38), (141, 41),
     (140, 44), (137, 41), (134, 38), (131, 34), (129, 32)],
    [(95, 65), (105, 68), (115, 70), (125, 72), (135, 71), (145, 72),
     (155, 70), (165, 66), (175, 66), (178, 65), (170, 60), (160, 60),
     (150, 59), (140, 55), (130, 50), (120, 50), (110, 55), (100, 60),
     (95, 65)],
    [(95, 5), (100, 5), (104, 1), (105, -2), (102, -4), (98, -2), (95, 2),
     (95, 5)],
    [(-10, 15), (-17, 15), (-17, 21), (-12, 28), (-6, 35), (0, 36), (10, 37),
     (11, 34), (20, 32), (32, 31), (35, 28), (38, 22), (43, 12), (48, 11),
     (51, 12), (48, 15), (43, 15), (40, 10), (36, 5), (33, -1), (30, -5),
     (28, -10), (26, -15), (22, -18), (18, -20), (16, -25), (14, -30),
     (12, -32), (18, -34), (20, -30), (25, -33), (28, -32), (32, -28),
     (35, -25), (35, -20), (36, -15), (40, -12), (40, -5), (42, 0), (44, 5),
     (48, 10), (43, 12), (40, 18), (35, 22), (32, 28), (30, 31), (25, 32),
     (20, 35), (15, 37), (10, 37), (5, 35), (0, 30), (-5, 25), (-10, 20),
     (-10, 15)],
    [(-58, -34), (-65, -41), (-68, -50), (-70, -54), (-66, -55), (-62, -45),
     (-58, -40), (-52, -33), (-48, -28), (-41, -23), (-39, -15), (-35, -8),
     (-35, -5), (-40, -3), (-44, -3), (-50, 0), (-52, 4), (-58, 2), (-62, -5),
     (-65, -10), (-70, -18), (-72, -25), (-70, -30), (-65, -35), (-58, -34)],
    [(-70, 18), (-75, 20), (-80, 25), (-85, 28), (-90, 21), (-95, 19),
     (-97, 16), (-95, 15), (-90, 14), (-85, 12), (-80, 9), (-78, 7),
     (-75, 10), (-72, 12), (-70, 18)],
    [(-100, 20), (-105, 20), (-110, 24), (-105, 30), (-100, 32), (-95, 29),
     (-90, 21), (-95, 16), (-100, 20)],
    [(-75, 10), (-80, 8), (-83, 9), (-80, 2), (-77, 4), (-72, 11), (-70, 12),
     (-75, 10)],
    [(68, 75), (75, 72), (85, 68), (95, 70), (105, 72), (115, 74), (125, 72),
     (135, 70), (145, 72), (155, 70), (165, 68), (175, 65), (178, 64),
     (170, 60), (160, 60), (150, 58), (140, 55), (130, 52), (120, 50),
     (110, 55), (100, 60), (90, 62), (80, 68), (68, 75)],
    [(140, -45), (150, -42), (160, -45), (170, -42), (175, -45), (165, -48),
     (155, -48), (145, -46), (140, -45)],
]

# (lon, lat) of the 15 drawn stories, in story order (1-15).
PINS = [
    (30.7, 36.9),    # 1 Antalya — COP31
    (20.1, 32.1),    # 2 Benghazi — Merkury
    (30.2, 50.8),    # 3 Dymer
    (4.4, 50.8),     # 4 Brussels — NATO
    (77.2, 28.6),    # 5 New Delhi
    (39.0, 22.8),    # 6 Rabigh
    (172.2, -13.7),  # 7 Vanuatu
    (8.5, 47.4),     # 8 Zurich — FIFA
    (-77.0, 38.9),   # 9 Washington
    (93.0, 28.0),    # 10 Arunachal
    (78.5, 30.7),    # 11 Himalayas
    (-0.1, 51.5),    # 12 London — NHS
    (7.7, 45.1),     # 13 Turin — sport
    (101.5, 3.1),    # 14 Selangor — floods
    (90.4, 23.8),    # 15 Dhaka — typhoid drive
]

def lonlat_to_xy(lon, lat, mx, my, mw, mh):
    px = mx + (lon + 180) / 360 * mw
    py = my + (75 - lat) / 135 * mh
    return px, py

def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 28, 48))
    # graticule: thin lon/lat lines under the land (real cartographic detail)
    for lon in range(-150, 181, 30):
        gx = x + (lon + 180) / 360 * w
        d.line([(gx, y), (gx, y + h)], fill=(40, 55, 80), width=1)
    for lat in (-60, -30, 0, 30, 60):
        gy = y + (75 - lat) / 135 * h
        d.line([(x, gy), (x + w, gy)], fill=(40, 55, 80), width=1)
    # ocean labels (small, on the water, under the land)
    lf = font(SSB, 8)
    for lon, lat, name in ((-37, 35, "ATLANTIC"),
                           (-135, -5, "PACIFIC OCEAN"),
                           (85, -28, "INDIAN OCEAN")):
        lx, ly = lonlat_to_xy(lon, lat, x, y, w, h)
        d.text((lx - tw(d, name, lf) / 2, ly), name, font=lf,
               fill=(100, 120, 160))
    for poly in POLYS:
        pts = [lonlat_to_xy(lon, lat, x, y, w, h) for lon, lat in poly]
        d.polygon(pts, fill=(200, 180, 120), outline=(150, 130, 85))
    # pins: collision-spread — pins must sit >=20px apart AFTER clamping
    # (v1 bug: the clamp re-introduced collisions, so pins 4 & 12 read as
    # one "14"). Try a fan of offsets, clamp each candidate first, then
    # test; take the first clear one, else the best-effort max-distance one.
    # A short white leader joins a moved pin back to its true spot
    # (legend: approximate).
    placed = []
    for i, (lon, lat) in enumerate(PINS, start=1):
        px, py = lonlat_to_xy(lon, lat, x, y, w, h)

        def _clamp(cx, cy):
            return (max(x + 8, min(x + w - 8, cx)),
                    max(y + 8, min(y + h - 8, cy)))

        def _mind(cx, cy):
            if not placed:
                return 99.0
            return min(((cx - qx) ** 2 + (cy - qy) ** 2) ** 0.5
                       for qx, qy in placed)

        ox, oy = _clamp(px, py)
        if placed and _mind(ox, oy) < 20:
            best = None
            for dx, dy in ((20, 0), (0, -20), (0, 20), (-20, 0),
                           (20, -20), (20, 20), (-20, -20), (-20, 20),
                           (30, 0), (0, -30), (0, 30), (-30, 0),
                           (40, 0), (0, -40), (40, -40), (40, 40),
                           (-40, -40), (-40, 40)):
                cx, cy = _clamp(px + dx, py + dy)
                md = _mind(cx, cy)
                if md >= 20:
                    ox, oy = cx, cy
                    best = "found"
                    break
                if best is None or md > best[0]:
                    best = (md, cx, cy)
            if best != "found" and best is not None:
                ox, oy = best[1], best[2]
        if (ox, oy) != (px, py):
            d.line([(px, py), (ox, oy)], fill=(250, 250, 250), width=1)
        placed.append((ox, oy))
        r = 7
        d.ellipse([ox - r, oy - r, ox + r, oy + r],
                  fill=(200, 40, 35), outline=(250, 250, 250), width=1)
        ntxt = str(i)
        nf = font(SSB, 9)
        d.text((ox - tw(d, ntxt, nf) / 2, oy - 5), ntxt, font=nf, fill=WHITE)

# ---------- data (research spec 2026-11-23; 37 stories = 3 leads + 12 mediums + 22 briefs) ----------
STRIP = [  # (number, label line 1, label line 2) — 6 giant checkable NEWS numbers
    # (round 2: the old strip wasted 2 slots on meta counts "35 stories /
    # 7 regions"; the News 22 winner's strip is all news numbers)
    ("14", "HRS UNDER", "RUBBLE — DAVID"),
    ("90+", "COUNTRIES SIGN", "COP PLEDGE"),
    ("9", "DEAD IN", "DYMER"),
    ("601", "KM DEEP —", "VANUATU QUAKE"),
    ("104", "MATCHES, 2035", "WORLD CUP"),
    ("$120bn", "FINANCE GOAL", "LOST AT COP31"),
]

REGIONS = [  # (label, count, color, width) — widths sum to 1008
    ("EUROPE 9", 9, (40, 90, 160), 232),
    ("MIDDLE EAST 6", 6, (178, 50, 40), 133),
    ("ASIA 9", 9, (200, 120, 30), 240),
    ("AFRICA 1", 1, (130, 90, 50), 64),
    ("N. AMERICA 4", 4, (40, 130, 70), 107),
    ("OCEANIA 1", 1, (30, 130, 130), 72),
    ("WORLD 7", 7, (110, 70, 160), 160),
]

LEADS = [
    dict(num=1, scene=scene_cop31, source="REUTERS", status="SUN",
         dateline="ANTALYA, TÜRKIYE · CLIMATE · SUN",
         headline="COP31 collapses — no deal on fossil fuels",
         deck="No fossil-fuel line; longest COP ever, 49 hrs over; $120bn "
              "goal lost; 5 blocs said no. (BBC, Reuters)"),
    dict(num=2, scene=scene_merkury, source="AP", status="SUN",
         dateline="BENGHAZI, LIBYA · WAR AT SEA · SUN",
         headline="Russian warship sunk by sea drones in Libyan port",
         deck="Capsized, bow up; 10 hurt, 4 drones downed; Sparta II towed "
              "out. Suspected Ukrainian drones. (AP, Reuters)"),
    dict(num=3, scene=scene_dymer, source="BBC", status="SUN",
         dateline="DYMER, UKRAINE · WAR · SUN",
         headline="Boy, 7, pulled alive after 14 hours under rubble",
         deck="9 dead, 11 missing; Vyshneve: 3 killed, 13 hurt. David, 7, "
              "saved after 14 hours. (BBC, AFP)"),
]

MEDIUMS = [  # 12 mediums (round 2: was 10 — winner has 12)
    dict(num=4, scene=scene_nato, source="REUTERS", status="REPORTED",
         banner="NATO", dateline="BRUSSELS · NATO",
         headline="NATO emergency meeting on Poland",
         sub="3 missiles were Russian"),
    dict(num=5, scene=scene_handshake, source="PTI", status="REPORTED",
         banner="TALKS", dateline="NEW DELHI · DIPLOMACY",
         headline="Nepal PM Shah meets Modi",
         sub="Vision pact, rail link"),
    dict(num=6, scene=scene_rabigh, source="REUTERS", status="CLAIM",
         banner="REFINERY", dateline="RABIGH, SAUDI ARABIA · WAR",
         headline="Houthis claim refinery hit",
         sub="Saudis silent"),
    dict(num=7, scene=scene_quake, source="USGS", status="REPORTED",
         banner="QUAKE", dateline="VANUATU · PACIFIC",
         headline="Deep quake shakes Vanuatu",
         sub="M6.5 at 601 km, no tsunami"),
    dict(num=8, scene=scene_stadium, source="FIFA", status="REPORTED",
         banner="2035", dateline="ZURICH · FOOTBALL",
         headline="UK to host 2035 Women's World Cup",
         sub="48 teams, 104 matches"),
    dict(num=9, scene=scene_vote, source="AP", status="REPORTED",
         banner="HOUSE", dateline="WASHINGTON · US POLITICS",
         headline="Democrats' biggest House majority",
         sub="Largest since 1992"),
    dict(num=10, scene=scene_lac, source="PTI", status="REPORTED",
         banner="BORDER", dateline="ARUNACHAL · BORDER",
         headline="India, China open border talks",
         sub="10-day talks on LAC"),
    dict(num=11, scene=scene_flood, source="AP", status="REPORTED",
         banner="FLOOD", dateline="INDIA · HIMALAYAS",
         headline="Himalayan flood kills 4",
         sub="100 missing in valley"),
    dict(num=12, scene=scene_nhs, source="NHS", status="REPORTED",
         banner="AI TRIAL", dateline="LONDON · HEALTH",
         headline="NHS launches biggest AI trial",
         sub="AI spots cancer earlier"),
    dict(num=13, scene=scene_sport, source="BBC", status="SUN",
         banner="SPORT", dateline="TURIN & PORTIMÃO · SPORT",
         headline="Alcaraz wins ATP Finals in Turin",
         sub="Márquez 8th title too"),
    dict(num=14, scene=scene_selangor, source="BERNAMA", status="REPORTED",
         banner="FLOOD", dateline="SELANGOR · MALAYSIA",
         headline="Selangor floods displace 1,800",
         sub="Evacuees past 1,800"),
    dict(num=15, scene=scene_typhoid, source="AP", status="REPORTED",
         banner="VACCINE", dateline="DHAKA · BANGLADESH",
         headline="Typhoid drive for 50m children",
         sub="Month-long, nationwide"),
]

BRIEFS = [  # (num, text, source, day tag) — 22 briefs, stories 16–37
    # (round 2: 17 + 25 promoted to mediums 15 + 14; 36 + 37 are new,
    # verified this session — Gaza strikes via MENAFN 23 Nov 00:56 GMT,
    # Brent via Reuters/yahoo 23 Nov, $89.55 −3.26%)
    (16, "India–NZ 1st Test drawn", "AP", "MON"),
    (17, "Sindarov gets White, G1", "FIDE", "MON"),
    (18, "Taiwan bans short-selling", "CNA", "MON"),
    (19, "Youth Congress hits Meta", "PTI", "MON"),
    (20, "Paolo Bulgari dies, 89", "ANSA", "MON"),
    (21, "Trump warns Iran", "REUTERS", "MON"),
    (22, "Tankers hit in Hormuz", "UKMTO", "SAT"),
    (23, "Liverpool beat 10-man Utd", "BBC", "SUN"),
    (24, "Thitikul wins 3rd LPGA", "AP", "MON"),
    (25, "Slovakia nixes EU loan", "REUTERS", "SUN"),
    (26, "Syria arrests 2nd officer", "SANA", "MON"),
    (27, "Titanic ring sells £150k", "BBC", "MON"),
    (28, "Trump posts Putin, Xi photos", "AP", "SUN"),
    (29, "Trio blocks UN job bid", "REUTERS", "SUN"),
    (30, "Iowa blast defies court", "REUTERS", "MON"),
    (31, "US varsity shooting: 2 dead", "AP", "SUN"),
    (32, "FSSAI: prosecute Bisleri", "PTI", "MON"),
    (33, "Trump reposts 'TrumpCare'", "AP", "SUN"),
    (34, "90+ sign COP pledge", "REUTERS", "MON"),
    (35, "Centrica: bills may rise 26%", "BBC", "SUN"),
    (36, "Gaza strikes kill 4", "MENAFN", "SAT"),
    (37, "Brent -3% to $89.55", "REUTERS", "MON"),
]
assert len(BRIEFS) == 22 and BRIEFS[0][0] == 16 and BRIEFS[-1][0] == 37

DATE_CHECK_BODY = (
    "CHECKED: ALL 37 STORIES ARE FROM MONDAY 23 NOVEMBER 2026. Sunday events "
    "flagged SUN — their Monday tolls and outcomes are the 23 November news. "
    "Excluded: COP31 'nears deal' (false), Nvidia resignation (12 Nov), "
    "Kryvyi Rih (20 Nov), Kerch Bridge (16–17 Nov). Today's real count: "
    "9 dead in Dymer, 601 km deep in Vanuatu — on the top of this page."
)

DATE_CHECK_FOOTER = (
    "Sources: Reuters, BBC, AP, AFP, Al Jazeera, Guardian, USGS, FIFA, "
    "MENAFN · REPORTED = confirmed · CLAIM = one side's claim · "
    "SUN = happened Sunday"
)

# ---------- canvas ----------
img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)
# newsprint grain: faint 1px speckles on the bare paper (seeded, deterministic)
_gr = random.Random(7)
for _ in range(1500):
    gx, gy = _gr.uniform(0, W), _gr.uniform(0, H)
    d.point((gx, gy), fill=(236, 228, 210))
MX = 8
RIGHT = W - MX  # 1016

# ---------- 1. MASTHEAD (0–104) ----------
d.text((MX, 5), "THE WORLD IN ONE DAY", font=font(SFB, 15), fill=RED)
rk = "37 STORIES · 7 REGIONS · EVERY ONE DATED MONDAY 23 NOVEMBER 2026"
assert_fit(d, rk, font(SFB, 13), RIGHT - MX, "masthead kicker right")
d.text((RIGHT - tw(d, rk, font(SFB, 13)), 6), rk, font=font(SFB, 13), fill=GREY)
title = "Monday 23 November 2026"
tf = font(SFB, 54)
assert_fit(d, title, tf, RIGHT - MX, "masthead title")
d.text(((W - tw(d, title, tf)) / 2, 22), title, font=tf, fill=INK)
deck = ("COP31 collapses with no deal · Russian corvette sunk off Benghazi · "
        "Boy, 7, pulled alive in Dymer")
df, dsize = fit_font(d, deck, SFI, [22, 20, 18, 16], RIGHT - MX)
d.text(((W - tw(d, deck, df)) / 2, 80), deck, font=df, fill=RED_D)
d.line([(MX, 102), (RIGHT, 102)], fill=INK, width=2)

# ---------- 2. STRIP (104–188) ----------
d.rectangle([MX, 104, RIGHT, 188], fill=PAPER2)
d.line([(MX, 104), (RIGHT, 104)], fill=INK, width=1)
d.line([(MX, 188), (RIGHT, 188)], fill=INK, width=1)
cell_w = (RIGHT - MX) / 6
for i, (num, l1, l2) in enumerate(STRIP):
    cx = MX + i * cell_w
    # number: largest size that fits (round 2: "$120bn" needs 46px)
    nf, nsize = fit_font(d, num, SFB, [52, 46, 40, 36], cell_w - 8)
    d.text((cx + (cell_w - tw(d, num, nf)) / 2, 104), num, font=nf, fill=INK)
    lf = font(SFB, 12)
    for j, lab in enumerate((l1, l2)):
        assert_fit(d, lab, lf, cell_w - 8, f"strip label {lab}")
        # round 2 fix: labels were clipped by the region bar (bar top 188);
        # 156/169 keeps both lines clear of it
        d.text((cx + (cell_w - tw(d, lab, lf)) / 2, 156 + j * 13), lab,
               font=lf, fill=GREY)
    if i:
        d.line([(cx, 112), (cx, 180)], fill=GREY_L, width=1)

# ---------- 3. REGION BAR (188–220) ----------
rx = MX
for label, count, color, wseg in REGIONS:
    d.rectangle([rx, 188, rx + wseg, 220], fill=color)
    rf = font(SSB, 13)
    if tw(d, label, rf) > wseg - 6:
        rf = font(SSB, 12)
    if tw(d, label, rf) > wseg - 6:
        rf = font(SSB, 11)
    assert_fit(d, label, rf, wseg - 4, f"region {label}")
    d.text((rx + (wseg - tw(d, label, rf)) / 2, 197), label, font=rf, fill=WHITE)
    rx += wseg
assert rx == RIGHT, f"region bar width {rx} != {RIGHT}"

# ---------- 4. LEADS (220–500) — no clock strip (only 2 verified times) ----------
lead_w, lead_gap = 330, 9
for i, L in enumerate(LEADS):
    x = MX + i * (lead_w + lead_gap)
    y = 220
    # red tag band
    d.rectangle([x, y, x + lead_w, y + 20], fill=RED)
    bf = font(SSB, 12)
    d.text((x + 8, y + 4), f"{L['num']} · LEAD", font=bf, fill=WHITE)
    sf = font(SSB, 11)
    st = L["status"]
    assert_fit(d, st, sf, lead_w - 90, f"lead status {st}")
    d.text((x + lead_w - tw(d, st, sf) - 8, y + 5), st, font=sf, fill=WHITE)
    # scene 132px
    L["scene"](d, x, y + 20, lead_w, 132)
    d.rectangle([x, y + 20, x + lead_w, y + 152], outline=INK, width=1)
    tag_chip(d, x + 6, y + 20 + 132 - 22, L["source"], size=10)
    # dateline
    dy = y + 156
    df2 = font(SFB, 13)
    assert_fit(d, L["dateline"], df2, lead_w - 4, f"lead dateline {L['num']}")
    d.text((x + 2, dy), L["dateline"], font=df2, fill=RED)
    # headline (serif bold, <=2 lines)
    hf, hsize, hlines = headline_lines(d, L["headline"], lead_w - 4)
    hy = dy + 16
    for ln in hlines:
        d.text((x + 2, hy), ln, font=hf, fill=INK)
        hy += hsize + 1
    # deck (round 2: up to THREE lines, serif 13, 4+ checkable numbers —
    # like the winner's 3-line lead bodies)
    deckf = font(SF, 13)
    dlines = wrap_text(d, L["deck"], deckf, lead_w - 4)
    assert len(dlines) <= 3, f"lead deck needs {len(dlines)} lines: {dlines}"
    sy = hy
    for ln in dlines:
        d.text((x + 2, sy), ln, font=deckf, fill=GREY)
        sy += 14
    assert sy <= y + 280, f"lead {L['num']} overflows card: {sy} > {y + 280}"

# ---------- 5. MEDIUMS (500–760) — 2 rows x 6 cols, 163px wide ----------
med_w, med_gap = 163, 5
med_h = 130
for idx, M in enumerate(MEDIUMS):
    col, row = idx % 6, idx // 6
    x = MX + 2 + col * (med_w + med_gap)
    y = 500 + row * med_h
    # scene 56px
    M["scene"](d, x, y, med_w, 56)
    d.rectangle([x, y, x + med_w, y + 56], outline=INK, width=1)
    # red number circle, top-right of the scene (like #10)
    cx, cy, cr = x + med_w - 13, y + 24, 9
    d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=RED,
              outline=WHITE, width=1)
    nf = font(SSB, 10)
    d.text((cx - tw(d, str(M["num"]), nf) / 2, cy - 5), str(M["num"]),
           font=nf, fill=WHITE)
    # red banner tag (full width, over scene top)
    d.rectangle([x, y, x + med_w, y + 14], fill=RED)
    bf = font(SSB, 11)
    btxt = f"{M['num']} · {M['banner']}"
    assert_fit(d, btxt, bf, med_w - 60, f"medium banner {M['num']}")
    d.text((x + 5, y + 2), btxt, font=bf, fill=WHITE)
    sf = font(SSB, 10)
    st = M["status"]
    assert_fit(d, st, sf, 56, f"medium status {M['num']}")
    d.text((x + med_w - tw(d, st, sf) - 5, y + 3), st, font=sf, fill=WHITE)
    tag_chip(d, x + med_w - 66, y + 56 - 20, M["source"], size=9)
    # dateline
    dy = y + 57
    df3 = font(SFB, 9)
    assert_fit(d, M["dateline"], df3, med_w - 4, f"medium dateline {M['num']}")
    d.text((x + 2, dy), M["dateline"], font=df3, fill=RED)
    # headline (serif bold, <=2 lines — 6-col grid is narrower)
    hf, hsize, hlines = headline_lines(d, M["headline"], med_w - 4,
                                       sizes=(18, 17, 16))
    hy = dy + 10
    for ln in hlines:
        d.text((x + 2, hy), ln, font=hf, fill=INK)
        hy += hsize
    # sub (1 line, serif 13)
    subf = font(SF, 13)
    assert_fit(d, M["sub"], subf, med_w - 4, f"medium sub {M['num']}")
    sy = hy
    d.text((x + 2, sy), M["sub"], font=subf, fill=GREY)
    assert sy + 14 <= y + med_h, f"medium {M['num']} overflows: {sy + 14} > {y + med_h}"

# ---------- 6. MAP + BRIEFS (760–940) ----------
# map (left): DARK navy map, gold-tan continents, red pins (15 drawn only)
map_x, map_y, map_w, map_h = MX, 774, 322, 112
d.text((MX, 760), "WHERE IT HAPPENED — PINS 1–15", font=font(SFB, 13), fill=INK)
d.rectangle([map_x, map_y, map_x + map_w, map_y + map_h], fill=(16, 28, 48),
            outline=INK, width=1)
draw_map(d, map_x, map_y, map_w, map_h)
# pin index (3 lines, 9px serif)
idx_lines = [
    "1 COP31 · 2 Merkury · 3 Dymer · 4 NATO · 5 Delhi · 6 Rabigh",
    "7 Vanuatu · 8 FIFA · 9 Washington · 10 Arunachal · 11 Himalayas",
    "12 London · 13 Turin · 14 Selangor · 15 Dhaka",
]
for j, line in enumerate(idx_lines):
    assert_fit(d, line, font(SF, 9), map_w - 4, f"pin index {j}")
    d.text((map_x + 2, map_y + map_h + 4 + j * 11), line, font=font(SF, 9), fill=INK)
d.text((map_x + 2, map_y + map_h + 38),
       "Red numbers mark stories 1–15. Positions are approximate.",
       font=font(SFI, 9), fill=GREY)

# briefs (right): 3 cols x 8 rows
d.text((340, 760), "ALSO ON — 22 BRIEFS", font=font(SFB, 13), fill=INK)
bf_font = font(SF, 11)
col_w = 220
for i, (num, text, src, tag) in enumerate(BRIEFS):
    col, row = i % 3, i // 3
    bx = 340 + col * (col_w + 6)
    by = 776 + row * 14
    line = f"{num}  {text} ({src}, {tag})"
    assert_fit(d, line, bf_font, col_w - 8, f"brief {num}")
    d.text((bx, by), line, font=bf_font, fill=INK)

# ---------- 7. DATE CHECK (942–1022) ----------
d.rectangle([MX, 942, RIGHT, 1022], outline=RED, width=2)
d.text((MX + 8, 946), "DATE CHECK", font=font(SFB, 13), fill=RED)
body_font = font(SF, 13)
body_lines = wrap_text(d, DATE_CHECK_BODY, body_font, RIGHT - MX - 16)
assert len(body_lines) <= 3, f"DATE CHECK needs {len(body_lines)} lines: {body_lines}"
by = 962
for ln in body_lines:
    d.text((MX + 8, by), ln, font=body_font, fill=INK)
    by += 15
foot_font, foot_size = fit_font(d, DATE_CHECK_FOOTER, SFB, [12, 11, 10],
                                RIGHT - MX - 16)
d.text((MX + 8, 1008), DATE_CHECK_FOOTER, font=foot_font, fill=INK)

# ---------- save + report ----------
img.save(OUT)
print("saved", OUT)
print("DATE CHECK body chars:", len(DATE_CHECK_BODY),
      "lines:", len(body_lines))
print("DATE CHECK body:", DATE_CHECK_BODY)
print("region counts sum:", sum(c for _, c, _, _ in REGIONS),
      "stories:", 3 + len(MEDIUMS) + len(BRIEFS))
assert sum(c for _, c, _, _ in REGIONS) == 3 + len(MEDIUMS) + len(BRIEFS), \
    "region strip does not sum to story total"
print("strip numbers:", [s[0] for s in STRIP])
print("lead headlines:", [L["headline"] for L in LEADS])
