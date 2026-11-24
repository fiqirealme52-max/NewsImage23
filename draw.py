# draw.py — News 23 round 4 revision (news-image-20261123)
# Fresh build, 24 Nov 2026. 40 stories: 3 leads + 15 mediums + 22 briefs.
# R4 fixes the 6 hard fails + 7 soft fails of the R3 audit. All numbers below were
# verified to live sources by the builder on 24 Nov 2026 before drawing:
#   NVDA close +31.48% at $165.05 (+~$950bn, best day since 2003); TSLA +11.46%,
#   META +6.55%, GOOGL +6.34%, AMZN +3.47%, AAPL +1.90%, MSFT +1.65%;
#   Nasdaq +6.51%, S&P +4.73%, Dow +3.01% (Finnhub/Motley Fool) /
#   Belgium: 404 of 429 flights cancelled (Brussels Airport) /
#   Dymer 11 dead, 2 missing; Vyshneve 3 killed, 15 hurt (BBC/AFP, Mayor Dikov) /
#   Taiex close 36,811.89 +2.16%, TSMC +1.5% (TVBS) / Ebola: WHO warning Mon 23 Nov,
#   cases doubled in 3 months (UN News) / Nepal INR 15,000 cr = NPR 24,000 cr (PIB) /
#   Selangor 1,582 evacuees 06:00 Mon (ADINet) / COP31: 2 days over, $120bn goal lost,
#   EU + ~130 nations refused a text with no fossil-fuel mention (magnabureau/BBC) /
#   FIFA congress Mon 23 Nov: 2031 + 2035 Women's World Cups, 48 teams, 104 matches /
#   Indonesia factory fire: 24 dead (Reuters) / Nigeria power-debt payoff by 2027 (ARISE) /
#   Anthropic close $87.64, -1.43% (Finnhub) / Brent -3.5% to $89.37 (Reuters).
# Full verification log: ~/workspace/makefun/News23/r4-verification-log-2026-11-24.md
# PIL programmatic flat illustration, one style, serif broadsheet, cream paper.
# Deterministic: no randomness.
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
CREAM = (250, 243, 228)
PAPER = (247, 238, 219)
INK = (26, 26, 26)
SOFT = (74, 66, 58)
RED = (179, 39, 30)
RED_DK = (140, 28, 22)
NAVY = (18, 38, 62)
NAVY_DK = (7, 18, 36)
GOLD = (198, 154, 52)
GREEN = (46, 139, 87)
TEAL = (14, 124, 123)
ORANGE = (214, 122, 42)
BLUE = (44, 90, 160)
PURPLE = (123, 94, 167)
GREEN2 = (31, 122, 109)
SKY = (176, 208, 224)

DJ = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
DJB = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
NTI = "/usr/share/fonts/truetype/noto/NotoSerif-Italic.ttf"
NTB = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
DS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
DSB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def F(p, s):
    return ImageFont.truetype(p, s)

def wrap(text, font, maxw):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if font.getlength(t) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def draw_lines(d, lines, x, y, font, fill, lh, align="left", maxw=None):
    for ln in lines:
        xx = x
        if align == "center" and maxw is not None:
            xx = x + (maxw - font.getlength(ln)) / 2
        d.text((xx, y), ln, font=font, fill=fill)
        y += lh
    return y

def vgrad(d, box, c1, c2):
    x0, y0, x1, y1 = box
    h = max(1, y1 - y0)
    for i in range(h):
        t = i / h
        c = tuple(int(c1[k] + (c2[k] - c1[k]) * t) for k in range(3))
        d.line([(x0, y0 + i), (x1, y0 + i)], fill=c)

def hgrad(d, box, c1, c2):
    x0, y0, x1, y1 = box
    w = max(1, x1 - x0)
    for i in range(w):
        t = i / w
        c = tuple(int(c1[k] + (c2[k] - c1[k]) * t) for k in range(3))
        d.line([(x0 + i, y0), (x0 + i, y1)], fill=c)

def person(d, x, y, s, shirt, skin=(216, 178, 140), pants=(38, 44, 58), arm="down"):
    # flat person, head + torso + legs, s = height in px
    hr = s * 0.11
    d.ellipse([x - hr, y, x + hr, y + 2 * hr], fill=skin)
    d.ellipse([x - hr, y, x + hr, y + hr * 0.9], fill=(52, 40, 32))  # hair cap
    ty = y + 2 * hr
    d.rounded_rectangle([x - s * 0.16, ty, x + s * 0.16, ty + s * 0.42],
                        radius=s * 0.05, fill=shirt)
    ly = ty + s * 0.42
    d.rectangle([x - s * 0.14, ly, x - s * 0.02, ly + s * 0.36], fill=pants)
    d.rectangle([x + s * 0.02, ly, x + s * 0.14, ly + s * 0.36], fill=pants)
    if arm == "up":
        d.line([(x + s * 0.15, ty + s * 0.08), (x + s * 0.30, ty - s * 0.12)],
               fill=shirt, width=max(2, int(s * 0.05)))
        d.line([(x - s * 0.15, ty + s * 0.08), (x - s * 0.28, ty - s * 0.10)],
               fill=shirt, width=max(2, int(s * 0.05)))
    elif arm == "one":
        d.line([(x + s * 0.15, ty + s * 0.08), (x + s * 0.30, ty - s * 0.10)],
               fill=shirt, width=max(2, int(s * 0.05)))

def building(d, x, y, w, h, color, lit=(255, 214, 130), rows=4, cols=4):
    d.rectangle([x, y, x + w, y + h], fill=color)
    cw, ch = w / cols, h / rows
    for r in range(rows):
        for c in range(cols):
            if (r * cols + c) % 3 != 0:
                d.rectangle([x + c * cw + cw * 0.22, y + r * ch + ch * 0.22,
                             x + (c + 1) * cw - cw * 0.22, y + (r + 1) * ch - ch * 0.22],
                            fill=lit)

def stars(d, box, n, seed=7):
    x0, y0, x1, y1 = box
    for i in range(n):
        px = x0 + ((i * 137 + seed * 31) % (x1 - x0 - 4)) + 2
        py = y0 + ((i * 89 + seed * 17) % (y1 - y0 - 4)) + 2
        r = 1 if i % 3 else 1.6
        d.ellipse([px - r, py - r, px + r, py + r], fill=(255, 250, 220))

def chart(d, pts, color, width=3):
    d.line(pts, fill=color, width=width, joint="curve")

def moon(d, x, y, r):
    d.ellipse([x - r, y - r, x + r, y + r], fill=(240, 232, 200))
    d.ellipse([x - r * 0.45, y - r * 0.25, x - r * 0.05, y + r * 0.15], fill=(214, 202, 168))
    d.ellipse([x + r * 0.15, y + r * 0.3, x + r * 0.5, y + r * 0.6], fill=(214, 202, 168))

img = Image.new("RGB", (W, H), CREAM)
d = ImageDraw.Draw(img, "RGBA")

# ---------- header ----------
f_kick = F(DSB, 15)
f_mast = F(DJB, 48)
f_sub = F(NTI, 17)
d.text((8, 6), "THE WORLD IN ONE DAY", font=f_kick, fill=RED)
r = "40 STORIES · 6 REGIONS · MONDAY 23 NOVEMBER 2026 · WIRES TO 06:49 UTC"
d.text((W - 8 - F(DSB, 11).getlength(r), 9), r, font=F(DSB, 11), fill=SOFT)
d.line([(8, 24), (W - 8, 24)], fill=(190, 175, 150), width=1)
d.text(((W - F(DJB, 48).getlength("Monday 23 November 2026")) / 2, 27),
       "Monday 23 November 2026", font=f_mast, fill=INK)
d.line([(8, 80), (W - 8, 80)], fill=INK, width=2)
sub = "Nvidia brings Huang back as shares soar 31%  ·  Russian warship sunk off Benghazi  ·  COP31 collapses with no deal"
d.text(((W - F(NTI, 17).getlength(sub)) / 2, 84), sub, font=f_sub, fill=RED)

# ---------- timeline strip: HOUR BY HOUR, UTC (all times verified live, 24 Nov 2026) ----------
# 05:23 Dymer 11th body (infokava live, 07:23 Kyiv = 05:23 UTC) /
# 05:30 Taiex +2.16% close (TWSE session ends 13:30 Taipei = 05:30 UTC) /
# 06:30 Kospi -3.31% close (KRX session ends 15:30 Seoul = 06:30 UTC) /
# 08:38 COP31 pledge 90+ (metropunch published 2026-11-23T08:38:21Z) /
# 14:30 Nasdaq opens (NYSE/Nasdaq 09:30 ET = 14:30 UTC) /
# 19:45 Monza kicks off (Serie A, 19:45 UTC) /
# 20:00 Brentford kicks off (Premier League, 20:00 UTC) /
# 21:00 NVDA +31.5% close (NYSE close 16:00 ET = 21:00 UTC; +31.48% R4 F1)
tl = [("05:23", "Dymer 11th body"), ("05:30", "Taiex +2.16%"),
      ("06:30", "Kospi \u22123.31%"), ("08:38", "COP31 pledge 90+"),
      ("14:30", "Nasdaq opens"), ("19:45", "Monza kicks off"),
      ("20:00", "Brentford kicks off"), ("21:00", "NVDA +31.5% close")]
d.rectangle([8, 104, W - 8, 122], fill=(245, 238, 220), outline=(200, 185, 160))
_tl_lab = "HOUR BY HOUR, UTC"
d.text((14, 109), _tl_lab, font=F(DSB, 9), fill=RED)
_fb8 = F(DSB, 8)
_fr8 = F(DJ, 8)
_tl_w = [(_fb8.getlength(t + " ") + _fr8.getlength(e)) for t, e in tl]
_tx = 14 + F(DSB, 9).getlength(_tl_lab) + 12
_tl_gap = (W - 16 - _tx - sum(_tl_w)) / (len(tl) - 1)
for (t, e), _w in zip(tl, _tl_w):
    d.text((_tx, 109), t, font=_fb8, fill=RED)
    d.text((_tx + _fb8.getlength(t + " "), 109), e, font=_fr8, fill=INK)
    _tx += _w + _tl_gap

# ---------- number strip ----------
nums = [("40", "STORIES"), ("6", "REGIONS"), ("+31%", "NVIDIA, MON"),
        ("404", "FLIGHTS CANCELLED"), ("+2.16%", "TAIEX, MON"),
        ("104", "MATCHES, 2035 WORLD CUP")]
y0, y1 = 126, 170
d.rectangle([8, y0, W - 8, y1], outline=(190, 175, 150), width=1)
cw = (W - 16) / 6
for i, (n, lab) in enumerate(nums):
    x = 8 + i * cw
    fn = F(DJB, 30)
    d.text((x + (cw - fn.getlength(n)) / 2, y0 + 2), n, font=fn, fill=INK)
    fl = F(DSB, 9)
    d.text((x + (cw - fl.getlength(lab)) / 2, y0 + 33), lab, font=fl, fill=SOFT)
    if i:
        d.line([(x, y0 + 4), (x, y1 - 4)], fill=(205, 190, 165), width=1)

# ---------- region strip (6 real regions, sums to 40) ----------
regs = [("EUROPE 17", BLUE), ("ASIA 7", ORANGE), ("N. AMERICA 9", TEAL),
        ("MIDDLE EAST 2", RED), ("OCEANIA 2", PURPLE), ("AFRICA 3", GREEN2)]
y0, y1 = 174, 196
x = 8
for lab, col in regs:
    w = (W - 16) / 6
    d.rectangle([x, y0, x + w - 2, y1], fill=col)
    f = F(DSB, 13)
    d.text((x + (w - 2 - f.getlength(lab)) / 2, y0 + 4), lab, font=f, fill=(255, 255, 255))
    x += w

# ---------- scene painters (each: background + midground + foreground, >=3 elements) ----------
def sc_nvidia(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (16, 30, 58), (34, 62, 96))
    stars(d, (x, y, x + w, y + h * 0.4), 14, 3)
    d.rectangle([x, y, x + w, y + 16], fill=(10, 20, 40))
    d.text((x + 5, y + 2), "NVDA  +31.5%", font=F(DSB, 11), fill=(120, 220, 140))
    _nas = "NASDAQ +6.5%"
    d.text((x + w - 78 - F(DSB, 10).getlength(_nas), y + 2), _nas, font=F(DSB, 10),
           fill=(200, 210, 225))
    for gy in range(1, 4):
        gy2 = y + 18 + gy * (h - 40) / 4
        d.line([(x + 4, gy2), (x + w - 4, gy2)], fill=(70, 95, 130), width=1)
    pts = [(x + 6, y + h - 26), (x + w * 0.25, y + h - 40), (x + w * 0.45, y + h - 62),
           (x + w * 0.62, y + h - 52), (x + w * 0.8, y + h - 88), (x + w - 40, y + h - 92)]
    chart(d, pts, (80, 220, 130), 4)
    d.polygon([(x + w - 40, y + h - 92), (x + w - 54, y + h - 90), (x + w - 42, y + h - 78)],
              fill=(80, 220, 130))
    # clean ticker tape strip at the very bottom: figures stand ABOVE it, never on the text
    d.rectangle([x, y + h - 16, x + w, y + h], fill=(12, 24, 44))
    d.line([(x, y + h - 16), (x + w, y + h - 16)], fill=(90, 120, 160), width=1)
    d.text((x + 5, y + h - 14), "NVDA +31.5%  TSLA +11.5%  META +6.6%  GOOGL +6.3%  AMZN +3.5%",
           font=F(DSB, 8), fill=(120, 220, 140))
    # skyline sits above the tape strip, bottom edge on the tape line
    for bx, bw, bh in [(0.60, 0.07, 20), (0.68, 0.05, 30), (0.75, 0.08, 22)]:
        d.rectangle([x + w * bx, y + h - 16 - bh, x + w * (bx + bw), y + h - 16],
                    fill=(24, 40, 64))
        for wy in range(2):
            d.rectangle([x + w * bx + 3, y + h - 16 - bh + 4 + wy * 10,
                         x + w * bx + 7, y + h - 16 - bh + 8 + wy * 10], fill=(255, 214, 130))
    # traders stand on the tape line, feet at y+h-16, clear of the tape text below it
    person(d, x + w * 0.18, y + h - 52, 36, (90, 60, 50), arm="one")
    person(d, x + w * 0.86, y + h - 52, 36, (50, 80, 60), arm="up")
    # figure from behind, leather jacket, facing the board
    cx = x + w * 0.5
    person(d, cx, y + h - 54, 38, (30, 30, 34), skin=(170, 140, 110))
    d.ellipse([cx - 5, y + h - 52, cx + 5, y + h - 44], fill=(52, 40, 32))

def sc_merkury(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (10, 22, 44), (28, 52, 86))
    moon(d, x + w * 0.70, y + 20, 9)
    stars(d, (x, y, x + w, y + h * 0.5), 12, 5)
    # fire glow behind the hull, low on the water
    d.ellipse([x + w * 0.32, y + h * 0.55, x + w * 0.68, y + h * 0.85], fill=(230, 120, 40))
    d.ellipse([x + w * 0.38, y + h * 0.60, x + w * 0.62, y + h * 0.82], fill=(250, 180, 70))
    # capsized hull, bow above water, superstructure block
    d.polygon([(x + w * 0.22, y + h * 0.66), (x + w * 0.50, y + h * 0.38),
               (x + w * 0.60, y + h * 0.66), (x + w * 0.36, y + h * 0.74)], fill=(24, 28, 38))
    d.rectangle([x + w * 0.42, y + h * 0.50, x + w * 0.52, y + h * 0.66], fill=(70, 78, 92))
    # flame on the hull
    d.polygon([(x + w * 0.46, y + h * 0.52), (x + w * 0.50, y + h * 0.40),
               (x + w * 0.54, y + h * 0.52)], fill=(255, 200, 60))
    # smoke columns rising from the hull, bases touching the hull edge
    for sx, sb, sh in [(0.33, 0.55, 20), (0.47, 0.44, 26), (0.57, 0.58, 18)]:
        d.ellipse([x + w * sx, y + h * sb - sh, x + w * sx + 14, y + h * sb],
                  fill=(120, 118, 112))
    # second smoke layer, higher and lighter
    for sx, sb, sh in [(0.36, 0.50, 22), (0.50, 0.40, 24)]:
        d.ellipse([x + w * sx, y + h * sb - sh, x + w * sx + 12, y + h * sb],
                  fill=(150, 148, 142))
    # sea: dark band + wave lines + small drone boat
    d.rectangle([x, y + h * 0.72, x + w, y + h], fill=(14, 32, 58))
    for wy in (0.78, 0.86, 0.94):
        d.line([(x + 6, y + h * wy), (x + w - 6, y + h * wy)], fill=(70, 110, 150), width=1)
    d.polygon([(x + w * 0.72, y + h * 0.80), (x + w * 0.82, y + h * 0.80),
               (x + w * 0.78, y + h * 0.86)], fill=(60, 66, 78))
    # fire reflection streaks on the water, under the glow
    for rx, rw, ry in [(0.36, 0.26, 0.78), (0.40, 0.18, 0.84), (0.44, 0.12, 0.90)]:
        d.line([(x + w * rx, y + h * ry), (x + w * (rx + rw), y + h * ry)],
               fill=(230, 130, 50), width=2)

def sc_cop31(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (88, 66, 48), (150, 118, 76))
    # hall windows
    for i in range(4):
        wx = x + 6 + i * (w - 12) / 4
        d.rectangle([wx, y + 6, wx + (w - 12) / 4 - 6, y + h * 0.42], fill=(232, 200, 140))
        d.line([(wx + (w - 12) / 8 - 3, y + 6), (wx + (w - 12) / 8 - 3, y + h * 0.42)],
               fill=(120, 92, 60), width=2)
    d.rectangle([x, y + h * 0.44, x + w, y + h * 0.52], fill=(70, 50, 36))
    # clock "2 DAYS OVER"
    d.ellipse([x + w * 0.43, y + 2, x + w * 0.57, y + 26], fill=(245, 240, 225),
              outline=INK, width=2)
    d.line([(x + w * 0.5, y + 14), (x + w * 0.5, y + 6)], fill=INK, width=2)
    d.line([(x + w * 0.5, y + 14), (x + w * 0.55, y + 17)], fill=INK, width=2)
    d.text((x + w * 0.5 - F(DSB, 9).getlength("2 DAYS OVER") / 2, y + 28),
           "2 DAYS OVER", font=F(DSB, 9), fill=RED_DK)
    # table + gavel + red-X document
    d.rectangle([x + w * 0.08, y + h * 0.56, x + w * 0.92, y + h * 0.68], fill=(96, 62, 40))
    d.rectangle([x + w * 0.30, y + h * 0.56, x + w * 0.48, y + h * 0.65], fill=(245, 240, 225))
    d.line([(x + w * 0.33, y + h * 0.58), (x + w * 0.45, y + h * 0.63)], fill=RED, width=2)
    d.line([(x + w * 0.45, y + h * 0.58), (x + w * 0.33, y + h * 0.63)], fill=RED, width=2)
    # gavel: head + diagonal handle + sound block
    d.rectangle([x + w * 0.60, y + h * 0.56, x + w * 0.70, y + h * 0.61], fill=(160, 120, 70))
    d.line([(x + w * 0.68, y + h * 0.60), (x + w * 0.78, y + h * 0.68)], fill=(120, 85, 50),
           width=3)
    d.rectangle([x + w * 0.76, y + h * 0.66, x + w * 0.84, y + h * 0.69], fill=(160, 120, 70))
    # delegates walking out, foreground
    person(d, x + w * 0.18, y + h * 0.62, 34, (60, 70, 90))
    person(d, x + w * 0.42, y + h * 0.62, 36, (120, 60, 50), arm="one")
    person(d, x + w * 0.68, y + h * 0.62, 34, (50, 90, 60))
    person(d, x + w * 0.86, y + h * 0.62, 30, (90, 80, 110))
    d.rectangle([x, y + h - 8, x + w, y + h], fill=(60, 44, 32))

def sc_awacs(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (120, 170, 205), (205, 225, 235))
    for cx, cy, cr in [(0.15, 0.25, 14), (0.55, 0.15, 18), (0.85, 0.35, 12), (0.35, 0.55, 10)]:
        d.ellipse([x + w * cx - cr, y + h * cy - cr * 0.55, x + w * cx + cr, y + h * cy + cr * 0.55],
                  fill=(255, 255, 255))
    # second, lower cloud layer for depth (drawn before the plane)
    for cx, cy, cr in [(0.25, 0.65, 8), (0.65, 0.70, 9), (0.90, 0.60, 7)]:
        d.ellipse([x + w * cx - cr, y + h * cy - cr * 0.55, x + w * cx + cr, y + h * cy + cr * 0.55],
                  fill=(235, 240, 245))
    # AWACS plane side view: fuselage, nose, tail fin, wing, radar dome
    px, py, s = x + w * 0.10, y + h * 0.42, w * 0.72
    d.polygon([(px + s * 0.96, py + s * 0.10), (px + s * 1.08, py + s * 0.02),
               (px + s * 1.04, py + s * 0.16)], fill=(210, 214, 218))
    d.ellipse([px, py + s * 0.02, px + s, py + s * 0.18], fill=(240, 240, 238))
    d.line([(px + s * 0.05, py + s * 0.15), (px + s * 0.92, py + s * 0.15)],
           fill=(150, 158, 165), width=2)
    d.rectangle([px + s * 0.86, py + s * 0.04, px + s * 0.93, py + s * 0.09],
                fill=(30, 60, 110))
    d.polygon([(px + s * 0.02, py + s * 0.08), (px + s * 0.10, py - s * 0.14),
               (px + s * 0.16, py + s * 0.08)], fill=(215, 219, 224))
    # wing + stabiliser drawn after the land block (below), so they stay visible
    d.line([(px + s * 0.30, py - s * 0.06), (px + s * 0.30, py + s * 0.02)], fill=(160, 165, 170),
           width=2)
    d.ellipse([px + s * 0.22, py - s * 0.16, px + s * 0.44, py + s * 0.02],
              fill=(200, 205, 210), outline=(150, 155, 160))
    for wx in (0.30, 0.45, 0.60, 0.75):
        d.rectangle([px + s * wx, py + s * 0.08, px + s * (wx + 0.05), py + s * 0.13],
                    fill=(40, 80, 140))
    # land below with Poland pin
    d.rectangle([x, y + h * 0.78, x + w, y + h], fill=(120, 160, 110))
    d.polygon([(x + w * 0.20, y + h * 0.78), (x + w * 0.45, y + h * 0.72), (x + w * 0.70, y + h * 0.78),
               (x + w * 0.62, y + h), (x + w * 0.30, y + h)], fill=(150, 185, 130))
    # main wing + tail stabiliser over the land: swept, clearly a plane not a blimp
    d.polygon([(px + s * 0.42, py + s * 0.16), (px + s * 0.80, py + s * 0.30),
               (px + s * 0.64, py + s * 0.16)], fill=(205, 210, 215))
    d.polygon([(px + s * 0.03, py + s * 0.14), (px + s * 0.14, py + s * 0.27),
               (px + s * 0.09, py + s * 0.14)], fill=(205, 210, 215))
    d.ellipse([x + w * 0.44, y + h * 0.80, x + w * 0.50, y + h * 0.86], fill=RED)
    d.line([(x + w * 0.47, y + h * 0.83), (x + w * 0.47, y + h * 0.70)], fill=RED, width=2)
    # ground crew on the land, clear of the tail fin and the nose
    person(d, x + w * 0.32, y + h * 0.78, 14, (30, 60, 110))
    person(d, x + w * 0.58, y + h * 0.78, 14, (30, 60, 110))
    d.text((x + 8, y + 2), "AWACS", font=F(DSB, 11), fill=NAVY)

def sc_nepal(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (200, 220, 235), (240, 232, 210))
    d.polygon([(x, y + h * 0.5), (x + w * 0.25, y + h * 0.18), (x + w * 0.5, y + h * 0.5)],
              fill=(120, 140, 165))
    d.polygon([(x + w * 0.45, y + h * 0.5), (x + w * 0.72, y + h * 0.12), (x + w, y + h * 0.5)],
              fill=(140, 158, 180))
    d.polygon([(x + w * 0.18, y + h * 0.28), (x + w * 0.25, y + h * 0.18), (x + w * 0.32, y + h * 0.28)],
              fill=(255, 255, 255))
    d.polygon([(x + w * 0.65, y + h * 0.24), (x + w * 0.72, y + h * 0.12), (x + w * 0.79, y + h * 0.24)],
              fill=(255, 255, 255))
    # train
    d.rectangle([x + w * 0.06, y + h * 0.62, x + w * 0.94, y + h * 0.78], fill=(180, 60, 40))
    d.rectangle([x + w * 0.06, y + h * 0.62, x + w * 0.30, y + h * 0.78], fill=(40, 60, 110))
    for i in range(5):
        wx = x + w * (0.34 + i * 0.12)
        d.rectangle([wx, y + h * 0.66, wx + w * 0.07, y + h * 0.74], fill=(255, 240, 200))
    d.rectangle([x, y + h * 0.80, x + w, y + h * 0.84], fill=(60, 60, 60))
    # two figures shaking hands in front of the train, standing on the ground
    person(d, x + w * 0.34, y + h * 0.47, 34, (240, 240, 240), arm="one")
    person(d, x + w * 0.60, y + h * 0.47, 34, (30, 50, 90), arm="one")
    _np = "\u20b915,000 CR"
    _nf = F(DSB, 10)
    d.text((x + (w - _nf.getlength(_np)) / 2, y + 2), _np, font=_nf, fill=INK)
    d.rectangle([x + w * 0.10, y + h * 0.06, x + w * 0.22, y + h * 0.13], fill=(255, 153, 51))
    d.rectangle([x + w * 0.10, y + h * 0.13, x + w * 0.22, y + h * 0.20], fill=(255, 255, 255))
    d.rectangle([x + w * 0.80, y + h * 0.28, x + w * 0.92, y + h * 0.42], fill=(220, 20, 60))

def sc_houthis(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (12, 16, 34), (50, 44, 70))
    stars(d, (x, y, x + w, y + h * 0.45), 12, 9)
    # refinery towers, lighter so they read against the night sky
    for tx, tw, th in [(0.10, 0.14, 0.55), (0.30, 0.12, 0.42), (0.52, 0.16, 0.62), (0.74, 0.12, 0.48)]:
        d.rectangle([x + w * tx, y + h - th * h - h * 0.18, x + w * (tx + tw), y + h * 0.82],
                    fill=(105, 108, 122))
        d.rectangle([x + w * tx - 2, y + h - th * h - h * 0.18 - 6, x + w * (tx + tw) + 2,
                     y + h - th * h - h * 0.18], fill=(130, 132, 146))
    # flame on the hit tower: small teardrop + glow
    fx, fy = x + w * 0.58, y + h * 0.16
    d.ellipse([fx - 10, fy - 2, fx + 10, fy + 18], fill=(250, 140, 40))
    d.polygon([(fx - 6, fy + 14), (fx, fy - 4), (fx + 6, fy + 14)], fill=(250, 170, 50))
    d.polygon([(fx - 3, fy + 14), (fx, fy + 4), (fx + 3, fy + 14)], fill=(255, 225, 100))
    # missile arc + smoke
    pts = [(x + w * 0.06, y + h * 0.30), (x + w * 0.30, y + h * 0.16),
           (x + w * 0.52, y + h * 0.14)]
    chart(d, pts, (240, 240, 240), 3)
    d.ellipse([x + w * 0.52, y + h * 0.11, x + w * 0.57, y + h * 0.17], fill=(255, 205, 60))
    d.rectangle([x, y + h * 0.82, x + w, y + h], fill=(30, 28, 36))
    d.text((x + 8, y + 2), "RABIGH", font=F(DSB, 10), fill=(255, 255, 255))

def sc_vanuatu(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (30, 90, 120), (16, 50, 80))
    # island silhouette
    d.polygon([(x, y + h * 0.55), (x + w * 0.30, y + h * 0.30), (x + w * 0.55, y + h * 0.55)],
              fill=(20, 60, 55))
    d.polygon([(x + w * 0.55, y + h * 0.55), (x + w * 0.80, y + h * 0.38), (x + w, y + h * 0.55)],
              fill=(16, 52, 48))
    # seismograph zigzag
    pts = [(x + 6, y + h * 0.22)]
    for i in range(1, 10):
        px = x + 6 + i * (w - 12) / 9
        py = y + h * (0.22 + (0.10 if i % 2 else -0.10) * (1 if i not in (4, 5) else 2.2))
        pts.append((px, py))
    chart(d, pts, (255, 220, 90), 2)
    # waves + depth arrow
    for wy in (0.62, 0.74, 0.86):
        for k in range(4):
            wx = x + w * (0.05 + k * 0.25)
            d.arc([wx, y + h * wy - 4, wx + w * 0.18, y + h * wy + 8], 180, 360,
                  fill=(150, 200, 220), width=2)
    d.line([(x + w * 0.86, y + h * 0.58), (x + w * 0.86, y + h * 0.90)], fill=(255, 255, 255), width=2)
    d.polygon([(x + w * 0.86 - 5, y + h * 0.86), (x + w * 0.86 + 5, y + h * 0.86),
               (x + w * 0.86, y + h * 0.94)], fill=(255, 255, 255))
    # "601 KM" on a dark tag so the seismograph line passes behind it, not through it
    _v7 = "601 KM"
    _f7 = F(DSB, 9)
    _w7 = _f7.getlength(_v7)
    d.rectangle([x + w * 0.34 - 3, y, x + w * 0.34 + _w7 + 3, y + 12], fill=(16, 50, 80))
    d.text((x + w * 0.34, y + 2), _v7, font=_f7, fill=(255, 255, 255))

def sc_fifa(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (30, 90, 140), (90, 150, 190))
    # stadium arc
    d.pieslice([x + w * 0.02, y - h * 0.55, x + w * 0.98, y + h * 0.75], 0, 180,
               fill=(245, 245, 240))
    d.pieslice([x + w * 0.10, y - h * 0.40, x + w * 0.90, y + h * 0.60], 0, 180,
               fill=(60, 120, 60))
    for i in range(7):
        lx = x + w * (0.12 + i * 0.125)
        d.line([(lx, y + h * 0.02), (lx, y + h * 0.10)], fill=(255, 240, 160), width=2)
    # gold trophy
    tx, ty = x + w * 0.5, y + h * 0.42
    d.polygon([(tx - 16, ty - 12), (tx - 8, ty + 10), (tx + 8, ty + 10), (tx + 16, ty - 12)],
              fill=GOLD)
    d.arc([tx - 22, ty - 12, tx - 8, ty + 2], 90, 270, fill=GOLD, width=3)
    d.arc([tx + 8, ty - 12, tx + 22, ty + 2], -90, 90, fill=GOLD, width=3)
    d.rectangle([tx - 3, ty + 10, tx + 3, ty + 18], fill=GOLD)
    d.rectangle([tx - 10, ty + 18, tx + 10, ty + 22], fill=GOLD)
    # ball + pitch
    d.ellipse([x + w * 0.14, y + h * 0.66, x + w * 0.24, y + h * 0.76], fill=(255, 255, 255))
    d.polygon([(x + w * 0.17, y + h * 0.69), (x + w * 0.21, y + h * 0.69),
               (x + w * 0.19, y + h * 0.73)], fill=INK)
    d.rectangle([x, y + h * 0.78, x + w, y + h], fill=(46, 120, 60))
    d.line([(x + w * 0.5, y + h * 0.78), (x + w * 0.5, y + h)], fill=(255, 255, 255), width=2)
    # crowd heads on the stands (left/centre only — the chip owns the top-right)
    for _i in range(7):
        _hx = x + w * (0.12 + _i * 0.08)
        d.ellipse([_hx - 2.5, y + h * 0.05 - 2.5, _hx + 2.5, y + h * 0.05 + 2.5],
                  fill=((216, 178, 140) if _i % 2 else (90, 60, 50)))
    # second player, right side of the pitch
    person(d, x + w * 0.80, y + h * 0.60, 14, (200, 40, 40), arm="one")
    # confetti over the stands
    for _cx, _cy, _cc in [(0.20, 0.18, (255, 200, 60)), (0.35, 0.12, (220, 60, 60)),
                          (0.50, 0.22, (60, 120, 220)), (0.62, 0.15, (255, 255, 255)),
                          (0.28, 0.30, (60, 200, 120)), (0.58, 0.32, (255, 200, 60)),
                          (0.75, 0.35, (220, 60, 60)), (0.42, 0.08, (255, 255, 255))]:
        d.rectangle([x + w * _cx, y + h * _cy, x + w * _cx + 3, y + h * _cy + 3], fill=_cc)
    d.text((x + 6, y + h - 12), "104 MATCHES", font=F(DSB, 10), fill=(255, 255, 255))

def sc_house(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (180, 200, 225), (235, 235, 230))
    # capitol dome
    d.rectangle([x + w * 0.30, y + h * 0.42, x + w * 0.70, y + h * 0.52], fill=(220, 220, 215))
    d.pieslice([x + w * 0.36, y + h * 0.10, x + w * 0.64, y + h * 0.46], 180, 360,
               fill=(235, 235, 230))
    d.rectangle([x + w * 0.48, y + h * 0.06, x + w * 0.52, y + h * 0.14], fill=(200, 200, 195))
    d.rectangle([x + w * 0.14, y + h * 0.52, x + w * 0.86, y + h * 0.58], fill=(210, 210, 205))
    for i in range(5):
        d.rectangle([x + w * (0.20 + i * 0.13), y + h * 0.58, x + w * (0.26 + i * 0.13),
                     y + h * 0.72], fill=(200, 200, 195))
    # bars: blue majority vs red
    d.rectangle([x + w * 0.12, y + h * 0.76, x + w * 0.62, y + h * 0.84], fill=BLUE)
    d.rectangle([x + w * 0.12, y + h * 0.86, x + w * 0.42, y + h * 0.94], fill=RED)
    # ballot box
    d.rectangle([x + w * 0.78, y + h * 0.72, x + w * 0.94, y + h * 0.92], fill=(120, 90, 60))
    d.rectangle([x + w * 0.80, y + h * 0.66, x + w * 0.92, y + h * 0.72], fill=(90, 66, 44))
    d.rectangle([x + w * 0.82, y + h * 0.60, x + w * 0.90, y + h * 0.68], fill=(255, 255, 255))
    d.text((x + 8, y + 2), "258 SEATS", font=F(DSB, 10), fill=INK)
    # two flags flanking the dome, poles down to the steps
    for _fx, _fc in [(0.10, BLUE), (0.88, RED)]:
        d.line([(x + w * _fx, y + h * 0.55), (x + w * _fx, y + h * 0.34)], fill=INK, width=2)
        d.rectangle([x + w * _fx, y + h * 0.34, x + w * (_fx + 0.08), y + h * 0.40], fill=_fc)
    # two figures on the steps, in the gaps between columns
    person(d, x + w * 0.295, y + h * 0.29, 22, (60, 70, 90), arm="one")
    person(d, x + w * 0.685, y + h * 0.29, 22, (90, 60, 50), arm="one")

def sc_lac(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (170, 200, 225), (235, 228, 200))
    d.polygon([(x, y + h * 0.62), (x + w * 0.28, y + h * 0.22), (x + w * 0.55, y + h * 0.62)],
              fill=(110, 130, 155))
    d.polygon([(x + w * 0.45, y + h * 0.62), (x + w * 0.74, y + h * 0.16), (x + w, y + h * 0.62)],
              fill=(130, 148, 170))
    d.polygon([(x + w * 0.21, y + h * 0.33), (x + w * 0.28, y + h * 0.22), (x + w * 0.35, y + h * 0.33)],
              fill=(255, 255, 255))
    d.polygon([(x + w * 0.67, y + h * 0.28), (x + w * 0.74, y + h * 0.16), (x + w * 0.81, y + h * 0.28)],
              fill=(255, 255, 255))
    # border post + fence
    d.rectangle([x + w * 0.46, y + h * 0.55, x + w * 0.54, y + h * 0.80], fill=(140, 110, 70))
    d.line([(x, y + h * 0.62), (x + w * 0.46, y + h * 0.62)], fill=(90, 90, 90), width=2)
    d.line([(x + w * 0.54, y + h * 0.62), (x + w, y + h * 0.62)], fill=(90, 90, 90), width=2)
    # two flags
    d.rectangle([x + w * 0.08, y + h * 0.14, x + w * 0.24, y + h * 0.26], fill=(255, 153, 51))
    d.rectangle([x + w * 0.08, y + h * 0.26, x + w * 0.24, y + h * 0.38], fill=(255, 255, 255))
    d.rectangle([x + w * 0.78, y + h * 0.36, x + w * 0.90, y + h * 0.48], fill=(222, 41, 16))
    # two soldiers shaking hands at the post
    person(d, x + w * 0.34, y + h * 0.38, 30, (60, 90, 60), arm="one")
    person(d, x + w * 0.64, y + h * 0.38, 30, (90, 60, 50), arm="one")
    d.rectangle([x, y + h * 0.82, x + w, y + h], fill=(150, 170, 120))
    _t10 = "10-DAY TALKS"
    _f10 = F(DSB, 9)
    _tw10 = _f10.getlength(_t10)
    # centre in the space left of the word chip (chip starts at x+w-65)
    d.text((x + 8 + (w - 73 - _tw10) / 2, y + 2), _t10, font=_f10, fill=INK)

def sc_taiex(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (16, 34, 58), (38, 68, 96))
    stars(d, (x, y, x + w, y + h * 0.4), 8, 11)
    # Taipei 101: tapered tower, narrow at the top, right side (shifted left of the chip)
    tx = x + w * 0.62
    for i in range(5):
        ww = 14 + i * 3
        d.rectangle([tx - ww / 2, y + h * (0.18 + i * 0.11), tx + ww / 2,
                     y + h * (0.29 + i * 0.11)], fill=(52, 62, 80))
    d.line([(tx, y + h * 0.18), (tx, y + h * 0.06)], fill=(150, 165, 185), width=2)
    d.ellipse([tx - 3, y + h * 0.04, tx + 3, y + h * 0.10], fill=(255, 214, 130))
    for wy in (0.30, 0.42, 0.54, 0.66):
        d.rectangle([tx - 5, y + h * wy, tx + 5, y + h * wy + 3], fill=(255, 214, 130))
    # rising green chart with arrowhead
    pts = [(x + 6, y + h * 0.72), (x + w * 0.25, y + h * 0.62), (x + w * 0.42, y + h * 0.66),
           (x + w * 0.58, y + h * 0.44), (x + w * 0.68, y + h * 0.34)]
    chart(d, pts, (80, 220, 130), 3)
    d.polygon([(x + w * 0.68, y + h * 0.34), (x + w * 0.68 - 10, y + h * 0.34 + 4),
               (x + w * 0.68 - 2, y + h * 0.34 + 12)], fill=(80, 220, 130))
    d.text((x + 5, y + 4), "+2.16%", font=F(DSB, 10), fill=(120, 220, 140))
    d.rectangle([x, y + h * 0.86, x + w, y + h], fill=(12, 24, 44))

def sc_nhs(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (190, 215, 230), (245, 242, 235))
    # hospital
    d.rectangle([x + w * 0.08, y + h * 0.30, x + w * 0.55, y + h * 0.78], fill=(240, 240, 238))
    d.rectangle([x + w * 0.08, y + h * 0.30, x + w * 0.55, y + h * 0.38], fill=(0, 90, 160))
    # hospital cross, moved right so the AI TRIAL label clears it
    d.rectangle([x + w * 0.42, y + h * 0.16, x + w * 0.48, y + h * 0.32], fill=(255, 255, 255))
    d.rectangle([x + w * 0.39, y + h * 0.21, x + w * 0.51, y + h * 0.27], fill=(255, 255, 255))
    for r in range(2):
        for c in range(3):
            d.rectangle([x + w * (0.13 + c * 0.13), y + h * (0.44 + r * 0.14),
                         x + w * (0.20 + c * 0.13), y + h * (0.52 + r * 0.14)], fill=(140, 190, 220))
    # screen with scan: light screen, dark lung oval, pink highlight, crosshair
    # (shifted down 0.04h so the word chip clears the oval)
    d.rectangle([x + w * 0.60, y + h * 0.26, x + w * 0.94, y + h * 0.66], fill=(225, 232, 236))
    d.ellipse([x + w * 0.68, y + h * 0.32, x + w * 0.86, y + h * 0.60], fill=(52, 62, 74))
    d.ellipse([x + w * 0.73, y + h * 0.40, x + w * 0.81, y + h * 0.52], fill=(225, 110, 150))
    d.line([(x + w * 0.77, y + h * 0.34), (x + w * 0.77, y + h * 0.58)], fill=(200, 210, 215),
           width=1)
    d.line([(x + w * 0.70, y + h * 0.46), (x + w * 0.84, y + h * 0.46)], fill=(200, 210, 215),
           width=1)
    person(d, x + w * 0.72, y + h * 0.36, 32, (255, 255, 255), arm="one")
    d.rectangle([x, y + h * 0.82, x + w, y + h], fill=(150, 185, 140))
    d.text((x + 8, y + 2), "AI TRIAL", font=F(DSB, 10), fill=INK)
    # second doctor at the screen, and a door on the hospital block
    person(d, x + w * 0.88, y + h * 0.40, 28, (255, 255, 255), arm="one")
    d.rectangle([x + w * 0.47, y + h * 0.62, x + w * 0.53, y + h * 0.78], fill=(60, 60, 60))
    d.ellipse([x + w * 0.515, y + h * 0.70, x + w * 0.525, y + h * 0.71], fill=(255, 214, 130))

def sc_sport(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (60, 110, 170), (200, 220, 235))
    # tennis court
    d.rectangle([x + w * 0.04, y + h * 0.34, x + w * 0.56, y + h * 0.86], fill=(60, 140, 90))
    d.rectangle([x + w * 0.10, y + h * 0.40, x + w * 0.50, y + h * 0.80], fill=(90, 170, 110))
    d.line([(x + w * 0.30, y + h * 0.40), (x + w * 0.30, y + h * 0.80)], fill=(255, 255, 255), width=2)
    d.line([(x + w * 0.10, y + h * 0.60), (x + w * 0.50, y + h * 0.60)], fill=(255, 255, 255), width=2)
    # net
    d.line([(x + w * 0.04, y + h * 0.55), (x + w * 0.56, y + h * 0.55)], fill=(40, 40, 40), width=2)
    # trophy
    tx, ty = x + w * 0.30, y + h * 0.14
    d.polygon([(tx - 10, ty), (tx - 6, ty + 12), (tx + 6, ty + 12), (tx + 10, ty)], fill=GOLD)
    d.rectangle([tx - 2, ty + 12, tx + 2, ty + 16], fill=GOLD)
    d.rectangle([tx - 7, ty + 16, tx + 7, ty + 19], fill=GOLD)
    # motorcycle: two small wheels + thin red frame
    mx, my = x + w * 0.70, y + h * 0.66
    d.ellipse([mx - 11, my - 3, mx - 3, my + 5], fill=INK)
    d.ellipse([mx + 7, my - 3, mx + 15, my + 5], fill=INK)
    d.line([(mx - 7, my + 1), (mx + 11, my + 1)], fill=(200, 40, 40), width=3)
    d.line([(mx - 7, my + 1), (mx - 2, my - 9)], fill=(200, 40, 40), width=2)
    d.line([(mx + 11, my + 1), (mx + 6, my - 9)], fill=(200, 40, 40), width=2)
    # player figure (moved left of the chip zone)
    person(d, x + w * 0.60, y + h * 0.24, 34, (255, 255, 255), arm="up")
    d.rectangle([x, y + h * 0.88, x + w, y + h], fill=(40, 100, 70))
    d.text((x + 6, y + h - 13), "ATP FINALS", font=F(DSB, 9), fill=(255, 255, 255))

def sc_selangor(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (140, 160, 180), (190, 200, 205))
    # rain lines
    for i in range(10):
        rx = x + ((i * 37) % int(w - 6)) + 3
        d.line([(rx, y + 4), (rx - 4, y + 16)], fill=(220, 230, 240), width=1)
    # houses on stilts (third house lowered 0.16h so its roof clears the word chip)
    for hx, hw, dy in [(0.08, 0.26, 0.0), (0.42, 0.26, 0.0), (0.74, 0.20, 0.16)]:
        d.rectangle([x + w * hx, y + h * (0.30 + dy), x + w * (hx + hw), y + h * (0.52 + dy)], fill=(190, 120, 70))
        d.polygon([(x + w * (hx - 0.02), y + h * (0.30 + dy)), (x + w * (hx + hw / 2), y + h * (0.18 + dy)),
                   (x + w * (hx + hw + 0.02), y + h * (0.30 + dy))], fill=(120, 60, 40))
        d.line([(x + w * (hx + 0.04), y + h * (0.52 + dy)), (x + w * (hx + 0.04), y + h * (0.66 + dy))],
               fill=(90, 70, 50), width=2)
        d.line([(x + w * (hx + hw - 0.04), y + h * (0.52 + dy)), (x + w * (hx + hw - 0.04), y + h * (0.66 + dy))],
               fill=(90, 70, 50), width=2)
    # flood water + boat with family
    d.rectangle([x, y + h * 0.62, x + w, y + h], fill=(70, 110, 140))
    d.polygon([(x + w * 0.28, y + h * 0.72), (x + w * 0.72, y + h * 0.72), (x + w * 0.66, y + h * 0.82),
               (x + w * 0.34, y + h * 0.82)], fill=(140, 90, 50))
    person(d, x + w * 0.42, y + h * 0.46, 26, (60, 120, 180))
    person(d, x + w * 0.58, y + h * 0.46, 22, (200, 80, 80))
    d.line([(x + w * 0.50, y + h * 0.56), (x + w * 0.50, y + h * 0.72)], fill=(90, 70, 50), width=2)
    for wy in (0.88, 0.94):
        d.line([(x + 6, y + h * wy), (x + w - 6, y + h * wy)], fill=(150, 190, 210), width=1)
    d.text((x + 6, y + 2), "1,582", font=F(DSB, 10), fill=INK)

def sc_ebola(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (200, 222, 232), (245, 240, 225))
    # clinic block with cross (cross lowered so the case-count label clears it)
    d.rectangle([x + w * 0.06, y + h * 0.30, x + w * 0.44, y + h * 0.74], fill=(250, 250, 248))
    d.rectangle([x + w * 0.06, y + h * 0.30, x + w * 0.44, y + h * 0.38], fill=(0, 120, 120))
    d.rectangle([x + w * 0.22, y + h * 0.24, x + w * 0.28, y + h * 0.40], fill=(255, 255, 255))
    d.rectangle([x + w * 0.19, y + h * 0.29, x + w * 0.31, y + h * 0.35], fill=(255, 255, 255))
    for c in range(3):
        d.rectangle([x + w * (0.10 + c * 0.11), y + h * 0.44, x + w * (0.17 + c * 0.11),
                     y + h * 0.54], fill=(140, 190, 210))
    # warning triangle, shrunk so the third responder clears it
    cx, cy = x + w * 0.70, y + h * 0.42
    d.polygon([(cx, cy - 14), (cx + 14, cy + 10), (cx - 14, cy + 10)], fill=(250, 200, 40),
              outline=INK)
    d.text((cx - 2, cy - 6), "!", font=F(DSB, 12), fill=INK)
    # relief tent behind the responders
    d.polygon([(x + w * 0.48, y + h * 0.78), (x + w * 0.58, y + h * 0.58),
               (x + w * 0.68, y + h * 0.78)], fill=(200, 180, 140))
    d.line([(x + w * 0.58, y + h * 0.58), (x + w * 0.58, y + h * 0.78)], fill=(150, 130, 100),
           width=1)
    # three responders at the clinic door
    person(d, x + w * 0.56, y + h * 0.52, 24, (40, 90, 160), arm="one")
    person(d, x + w * 0.80, y + h * 0.52, 24, (40, 90, 160), arm="one")
    person(d, x + w * 0.88, y + h * 0.52, 24, (40, 90, 160), arm="one")
    d.rectangle([x, y + h * 0.84, x + w, y + h], fill=(170, 200, 160))
    # case count: freshest verified figure, UN News (released 20 Nov): 11,762 cases
    d.text((x + 8, y + 2), "11,762 CASES", font=F(DSB, 9), fill=INK)

def sc_kospi(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (40, 50, 70), (90, 70, 80))
    # Seoul tower: lighter shaft with lit windows, ringed deck, antenna — clearly a tower
    # (shifted left so the word chip clears the deck)
    d.rectangle([x + w * 0.55, y + h * 0.18, x + w * 0.61, y + h * 0.62], fill=(52, 58, 74))
    d.ellipse([x + w * 0.51, y + h * 0.10, x + w * 0.65, y + h * 0.24], fill=(52, 58, 74),
              outline=(150, 165, 185))
    d.line([(x + w * 0.58, y + h * 0.10), (x + w * 0.58, y + h * 0.02)], fill=(150, 165, 185), width=1)
    for wy in (0.30, 0.42, 0.54):
        d.rectangle([x + w * 0.565, y + h * wy, x + w * 0.595, y + h * wy + 3], fill=(255, 214, 130))
    d.rectangle([x + w * 0.06, y + h * 0.52, x + w * 0.30, y + h * 0.66], fill=(44, 48, 62))
    d.rectangle([x + w * 0.34, y + h * 0.44, x + w * 0.52, y + h * 0.66], fill=(38, 42, 56))
    building(d, x + w * 0.06, y + h * 0.52, w * 0.24, h * 0.14, (44, 48, 62), rows=2, cols=3)
    # falling red chart
    pts = [(x + 6, y + h * 0.18), (x + w * 0.25, y + h * 0.30), (x + w * 0.45, y + h * 0.28),
           (x + w * 0.65, y + h * 0.55), (x + w * 0.85, y + h * 0.72), (x + w - 6, y + h * 0.78)]
    chart(d, pts, (240, 70, 60), 4)
    d.polygon([(x + w - 6, y + h * 0.78), (x + w - 20, y + h * 0.74), (x + w - 8, y + h * 0.90)],
              fill=(240, 70, 60))
    # intraday path: plunge to the -5.8% low, then recovery to the -3.31% close
    _op = [(x + 6, y + h * 0.20), (x + w * 0.30, y + h * 0.45), (x + w * 0.55, y + h * 0.82),
           (x + w * 0.75, y + h * 0.70), (x + w - 6, y + h * 0.62)]
    chart(d, _op, (230, 140, 40), 2)
    # close label with a dark backing so it reads over both chart lines
    _k16 = "\u22123.31%"
    _f16 = F(DSB, 10)
    _kw = _f16.getlength(_k16)
    d.rectangle([x + 5, y + h * 0.30 - 2, x + 5 + _kw + 7, y + h * 0.30 + 12], fill=(24, 28, 40))
    d.text((x + 8, y + h * 0.30), _k16, font=_f16, fill=(255, 255, 255))
    # trader watching the board, right side
    person(d, x + w * 0.88, y + h * 0.44, 22, (90, 60, 50), arm="one")
    d.rectangle([x, y + h * 0.86, x + w, y + h], fill=(24, 28, 40))

def sc_belgium(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (150, 180, 205), (215, 225, 235))
    # departure board, all cancelled
    d.rectangle([x + w * 0.06, y + h * 0.06, x + w * 0.94, y + h * 0.42], fill=(20, 26, 36))
    # one clean CANCELLED stamp, drawn once, centred on the board
    _ct, _cf = "CANCELLED", F(DSB, 12)
    _cw = _cf.getlength(_ct)
    _cx = x + w * 0.32 - _cw / 2
    _cy = y + h * 0.24 - 6
    d.rectangle([_cx - 6, _cy - 3, _cx + _cw + 6, _cy + 13], outline=(255, 90, 70), width=2)
    d.text((_cx, _cy), _ct, font=_cf, fill=(255, 90, 70))
    # control tower
    d.rectangle([x + w * 0.08, y + h * 0.50, x + w * 0.14, y + h * 0.86], fill=(90, 100, 115))
    d.rectangle([x + w * 0.05, y + h * 0.42, x + w * 0.17, y + h * 0.52], fill=(70, 80, 95))
    # parked planes
    for px in (0.30, 0.58, 0.84):
        bx, by = x + w * px, y + h * 0.66
        d.ellipse([bx - 16, by - 6, bx + 16, by + 6], fill=(230, 230, 228))
        d.polygon([(bx + 14, by), (bx + 24, by - 8), (bx + 22, by + 2)], fill=(200, 205, 210))
        d.polygon([(bx - 2, by + 4), (bx + 6, by + 14), (bx - 2, by + 4)], fill=(200, 205, 210))
        d.rectangle([bx - 10, by - 2, bx + 2, by + 2], fill=(30, 70, 140))
    d.rectangle([x, y + h * 0.86, x + w, y + h], fill=(120, 125, 130))
    d.line([(x, y + h * 0.86), (x + w, y + h * 0.86)], fill=(255, 255, 255), width=2)

def sc_dymer(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (120, 125, 150), (205, 175, 140))
    # dawn sun + broken skyline (sun moved left of the chip zone)
    d.ellipse([x + w * 0.48, y + h * 0.06, x + w * 0.64, y + h * 0.22], fill=(255, 215, 140))
    d.polygon([(x, y + h * 0.48), (x + w * 0.14, y + h * 0.48), (x + w * 0.18, y + h * 0.34),
               (x + w * 0.30, y + h * 0.48)], fill=(95, 85, 78))
    d.polygon([(x + w * 0.55, y + h * 0.48), (x + w * 0.66, y + h * 0.30), (x + w * 0.80, y + h * 0.48)],
              fill=(85, 76, 70))
    # searchlight beams, narrow
    d.polygon([(x + w * 0.32, y + h * 0.95), (x + w * 0.14, y + h * 0.22), (x + w * 0.20, y + h * 0.22)],
              fill=(255, 242, 190))
    d.polygon([(x + w * 0.64, y + h * 0.95), (x + w * 0.78, y + h * 0.18), (x + w * 0.84, y + h * 0.20)],
              fill=(255, 242, 190))
    # rubble mound, lighter
    d.polygon([(x, y + h), (x, y + h * 0.78), (x + w * 0.22, y + h * 0.60), (x + w * 0.48, y + h * 0.68),
               (x + w * 0.72, y + h * 0.58), (x + w, y + h * 0.76), (x + w, y + h)], fill=(140, 124, 106))
    d.polygon([(x + w * 0.30, y + h * 0.72), (x + w * 0.44, y + h * 0.62), (x + w * 0.52, y + h * 0.74)],
              fill=(118, 102, 86))
    d.polygon([(x + w * 0.58, y + h * 0.70), (x + w * 0.70, y + h * 0.60), (x + w * 0.78, y + h * 0.72)],
              fill=(112, 98, 82))
    # extra broken slabs in the foreground rubble
    d.polygon([(x + w * 0.02, y + h * 0.86), (x + w * 0.15, y + h * 0.80), (x + w * 0.17, y + h * 0.92),
               (x + w * 0.04, y + h * 0.96)], fill=(118, 102, 86))
    d.polygon([(x + w * 0.86, y + h * 0.84), (x + w * 0.98, y + h * 0.80), (x + w * 0.98, y + h * 0.94),
               (x + w * 0.88, y + h * 0.96)], fill=(112, 98, 82))
    for dx, dy in [(0.45, 0.66), (0.52, 0.68), (0.60, 0.65)]:
        d.rectangle([x + w * dx, y + h * dy, x + w * dx + 6, y + h * dy + 4], fill=(100, 86, 72))
    # rescuers close to the stretcher + boy wrapped in a blue blanket
    person(d, x + w * 0.22, y + h * 0.52, 32, (230, 120, 40), arm="one")
    person(d, x + w * 0.76, y + h * 0.52, 32, (230, 120, 40), arm="one")
    d.rectangle([x + w * 0.28, y + h * 0.73, x + w * 0.72, y + h * 0.81], fill=(240, 240, 235))
    d.ellipse([x + w * 0.30, y + h * 0.69, x + w * 0.37, y + h * 0.76], fill=(216, 178, 140))
    d.rectangle([x + w * 0.36, y + h * 0.71, x + w * 0.70, y + h * 0.79], fill=(40, 90, 160))
    d.text((x + 8, y + 2), "14 HOURS", font=F(DSB, 10), fill=INK)

# ---------- card renderers ----------
def word_chip(d, sx, sy, sw, word):
    # 64x15 white word chip at the top-right corner inside a scene
    cx0 = sx + sw - 65
    cy0 = sy + 1
    col = RED if word == "CLAIM" else ((31, 122, 80) if word == "ON RECORD" else INK)
    d.rounded_rectangle([cx0, cy0, cx0 + 64, cy0 + 15], radius=3, fill=(255, 255, 255),
                        outline=(190, 175, 150))
    f = F(DSB, 8)
    tw = f.getlength(word)
    d.text((cx0 + (64 - tw) / 2, cy0 + 4), word, font=f, fill=col)

def lead_card(d, x, y, w, h, num, tag, scene, loc, head, body, chip="REPORTED"):
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255), outline=(200, 185, 160))
    d.rectangle([x, y, x + w, y + 16], fill=RED)
    d.text((x + 6, y + 2), "%d · LEAD" % num, font=F(DSB, 10), fill=(255, 255, 255))
    _tw = F(DSB, 10).getlength(tag)
    d.text((x + w - 6 - _tw, y + 2), tag, font=F(DSB, 10), fill=(255, 255, 255))
    sy = y + 16
    scene(d, x + 1, sy, w - 2, 96)
    word_chip(d, x + 1, sy, w - 2, chip)
    ty = sy + 96
    d.text((x + 6, ty + 2), loc, font=F(DSB, 9), fill=RED)
    fh = F(DJB, 18)
    hl = wrap(head, fh, w - 12)
    draw_lines(d, hl[:2], x + 6, ty + 13, fh, INK, 20)
    fb = F(DJ, 11)
    bl = wrap(body, fb, w - 12)
    draw_lines(d, bl[:2], x + 6, ty + 13 + len(hl[:2]) * 20 + 2, fb, SOFT, 14)

def med_card(d, x, y, w, h, num, tag, scene, loc, head, body, hero=False, blines=1, sh=52,
             chip="REPORTED"):
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255), outline=(200, 185, 160))
    d.rectangle([x, y, x + w, y + 14], fill=RED)
    d.text((x + 5, y + 2), "%d · HERO" % num if hero else "%d" % num, font=F(DSB, 10),
           fill=(255, 255, 255))
    _tw = F(DSB, 9).getlength(tag)
    d.text((x + w - 5 - _tw, y + 2), tag, font=F(DSB, 9), fill=(255, 255, 255))
    sy = y + 14
    scene(d, x + 1, sy, w - 2, sh)
    word_chip(d, x + 1, sy, w - 2, chip)
    ty = sy + sh
    d.text((x + 5, ty + 1), loc, font=F(DSB, 8), fill=RED)
    fh = F(DJB, 15) if hero else F(DJB, 13)
    lh = 16 if hero else 14
    hl = wrap(head, fh, w - 10)
    draw_lines(d, hl[:2], x + 5, ty + 10, fh, INK, lh)
    fb = F(DJ, 10)
    bl = wrap(body, fb, w - 10)
    draw_lines(d, bl[:blines], x + 5, ty + 10 + len(hl[:2]) * lh + 1, fb, SOFT, 12)

# ---------- pictured stories ----------
LEADS = [
    (1, "MON", sc_nvidia, "NEW YORK · MARKETS · MON",
     "Nvidia brings Huang back — shares soar 31%",
     "Board votes unanimously, 11 days after resignation; NVDA +31.5%, TSLA +11.5%, +$950bn. (Reuters)"),
    (2, "SUN", sc_merkury, "BENGHAZI · LIBYA · SUN",
     "Russian warship sunk by sea drones in Libyan port",
     "Capsized, bow up; 10 hurt, 4 drones downed — Sparta II towed out. Suspected Ukrainian drones. (AP, Reuters)"),
    (3, "SUN", sc_cop31, "ANTALYA · CLIMATE · SUN",
     "COP31 collapses — no deal on fossil fuels",
     "Longest COP ever, 2 days over; $120bn goal lost; EU + 130 nations said no. (BBC, Reuters)"),
]
MEDS = [
    (18, "SUN", sc_dymer, "DYMER · UKRAINE · SUN", True,
     "Boy, 7, pulled alive after 14 hours under rubble",
     "11 dead, 2 missing; Vyshneve: 3 killed, 15 hurt. (BBC, AFP)"),
    (4, "MON", sc_awacs, "NATO · POLAND · MON", False,
     "NATO sends AWACS to Poland",
     "SACEUR authorises jet; Article 4 not invoked. (NATO)"),
    (5, "MON", sc_nepal, "NEW DELHI · NEPAL · MON", False,
     "Modi gives Nepal ₹15,000 crore",
     "NPR 5,600 cr grant + 18,400 cr credit; rail flagged off. (PIB)"),
    (6, "SUN", sc_houthis, "RABIGH · SAUDI · SUN", False,
     "Houthis claim refinery hit",
     "Rabigh targeted, Saudis silent; coalition: missile down. (Reuters)"),
    (7, "MON", sc_vanuatu, "VANUATU · PACIFIC · MON", False,
     "Deep quake shakes Vanuatu",
     "M6.5 at 601 km, no tsunami. (USGS)"),
    (8, "MON", sc_fifa, "ZURICH · SPORT · MON", False,
     "UK to host 2035 Women's World Cup",
     "48 teams, 104 matches. (BBC)"),
    (9, "SUN", sc_house, "WASHINGTON · POLITICS · SUN", False,
     "Democrats' biggest House majority",
     "Largest since 1992. (BBC)"),
    (10, "MON", sc_lac, "ARUNACHAL · INDIA-CHINA · MON", False,
     "India, China open border talks",
     "10-day talks on LAC. (Hindu)"),
    (11, "MON", sc_taiex, "TAIPEI · MARKETS · MON", False,
     "Taiex rebounds 2.16% after rout",
     "Close 36,811.89 (TVBS)"),
    (12, "MON", sc_nhs, "LONDON · HEALTH · MON", False,
     "NHS launches biggest AI trial",
     "AI spots cancer earlier. (BBC)"),
    (13, "SUN", sc_sport, "TURIN · SPORT · SUN", False,
     "Alcaraz wins ATP Finals in Turin",
     "Márquez 8th title too. (BBC)"),
    (14, "MON", sc_selangor, "SELANGOR · MALAYSIA · MON", False,
     "Selangor floods displace 1,582",
     "1,582 at 06:00, falling. (ADINet)"),
    (15, "MON", sc_ebola, "BUNIA · DR CONGO · MON", False,
     "Ebola teams trapped as fighting rages",
     "Doubled in 3 months. (UN News)"),
    (16, "MON", sc_kospi, "SEOUL · MARKETS · MON", False,
     "Kospi plunges 5.8% intraday",
     "Close −3.31% at 4,708. (KRX)"),
    (17, "MON", sc_belgium, "BRUSSELS · STRIKE · MON", False,
     "Belgium grounds all flights",
     "All flights 07:00–21:00 cancelled."),
]

# ---------- leads row ----------
# verification status per story: ON RECORD = official source, REPORTED = press-reported,
# CLAIM = single-source claim (M6: only the Houthis claim the hit)
CHIP = {1: "REPORTED", 2: "REPORTED", 3: "REPORTED", 4: "ON RECORD",
        5: "ON RECORD", 6: "CLAIM", 7: "ON RECORD", 8: "ON RECORD",
        9: "REPORTED", 10: "REPORTED", 11: "ON RECORD", 12: "REPORTED",
        13: "ON RECORD", 14: "REPORTED", 15: "REPORTED", 16: "ON RECORD",
        17: "ON RECORD", 18: "REPORTED"}
lw = (W - 16 - 14) / 3
for i, (num, tag, scene, loc, head, body) in enumerate(LEADS):
    lead_card(d, 8 + i * (lw + 7), 200, lw, 196, num, tag, scene, loc, head, body,
              chip=CHIP[num])

# ---------- medium rows: A (hero row, 147px) / B / C (116px) ----------
mw = (W - 16 - 24) / 5
rows = [(400, 158, MEDS[0:5], 76, 2), (562, 118, MEDS[5:10], 52, 1), (684, 118, MEDS[10:15], 52, 1)]
for ry, rh, items, sh, bl in rows:
    for j, (num, tag, scene, loc, hero, head, body) in enumerate(items):
        med_card(d, 8 + j * (mw + 6), ry, mw, rh, num, tag, scene, loc, head, body,
                 hero=hero, blines=bl, sh=sh, chip=CHIP[num])

# ---------- map + ALSO ON ----------
d.text((8, 806), "WHERE IT HAPPENED — PINS 1–18", font=F(DSB, 11), fill=INK)
d.text((428, 806), "ALSO ON — 22 BRIEFS", font=F(DSB, 11), fill=INK)
mx0, my0, mx1, my1 = 8, 820, 418, 936
d.rectangle([mx0, my0, mx1, my1], fill=(232, 240, 244), outline=(200, 185, 160))
CONTINENTS = [
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-80, 73), (-70, 62), (-55, 52),
     (-60, 45), (-75, 35), (-80, 26), (-90, 21), (-97, 16), (-105, 20), (-115, 30),
     (-125, 40), (-125, 49), (-140, 60), (-165, 60)],
    [(-80, 10), (-60, 5), (-50, 0), (-35, -8), (-40, -20), (-48, -28), (-58, -35),
     (-65, -41), (-70, -52), (-73, -40), (-70, -20), (-80, -5)],
    [(-10, 36), (0, 39), (10, 44), (20, 40), (28, 36), (30, 42), (24, 45), (18, 46),
     (12, 50), (5, 53), (-2, 51), (-5, 48), (-10, 43), (-10, 37)],
    [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (32, 31), (35, 28), (43, 12),
     (51, 10), (48, 0), (40, -10), (35, -20), (32, -28), (20, -35), (15, -27), (12, -18),
     (9, -1), (9, 4), (-8, 5), (-15, 12)],
    [(30, 42), (40, 45), (50, 47), (60, 50), (70, 55), (80, 60), (100, 65), (120, 70),
     (140, 72), (160, 70), (178, 65), (170, 60), (162, 55), (155, 50), (142, 45), (135, 40),
     (127, 35), (120, 30), (110, 20), (105, 10), (100, 8), (95, 15), (90, 22), (85, 20),
     (78, 10), (75, 8), (70, 20), (62, 25), (55, 25), (48, 28), (40, 30), (35, 36), (30, 40)],
    [(113, -22), (114, -30), (120, -34), (130, -32), (140, -38), (150, -37), (153, -27),
     (150, -20), (142, -11), (135, -12), (130, -13), (122, -17), (114, -22)],
    [(-5, 50), (-3, 53), (-2, 55), (-4, 58), (-6, 56), (-5, 50)],
    [(130, 31), (133, 34), (137, 35), (140, 38), (142, 42), (140, 44), (137, 41), (134, 36), (131, 33)],
    [(95, 5), (100, 0), (105, -5), (115, -8), (125, -9), (131, -3), (137, -2), (141, -4),
     (147, -8), (150, -10), (146, -18), (142, -17), (136, -15), (132, -11), (128, -8),
     (120, -10), (113, -22), (105, -15), (100, -5)],
]
def proj(lon, lat):
    px = mx0 + (lon + 170) / 350 * (mx1 - mx0)
    py = my0 + (83 - lat) / 141 * (my1 - my0)
    return px, py
# dotted map: steel-blue dots inside the continent polygons, on a light ground
_CONT = [[proj(lon, lat) for lon, lat in poly] for poly in CONTINENTS]
def _inside(px, py, poly):
    ins = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
            ins = not ins
        j = i
    return ins
for _gy in range(my0 + 3, my1 - 2, 4):
    for _gx in range(mx0 + 3, mx1 - 2, 4):
        if any(_inside(_gx, _gy, _p) for _p in _CONT):
            d.ellipse([_gx - 1, _gy - 1, _gx + 1, _gy + 1], fill=(90, 130, 160))
PINS = [
    (1, -74, 40.7, -10, -4, None, None), (2, 20.1, 32.1, 4, 2, "Benghazi", (-28, 14)),
    (3, 30.7, 36.9, 9, 12, "Antalya", (8, -18)), (4, 21, 52.2, -2, -20, None, None),
    (5, 77.2, 28.6, -8, 4, None, None), (6, 39, 22.8, 12, 12, None, None),
    (7, 172.2, -13.7, 0, 0, None, None), (8, 8.5, 47.4, -11, -22, None, None),
    (9, -77, 38.9, -2, 8, None, None), (10, 94, 28, 8, -2, None, None),
    (11, 121.6, 25.0, -14, 10, "Taipei", (10, -6)), (12, -0.1, 51.5, -32, -17, "London", (-48, -2)),
    (13, 7.7, 45.1, -14, 20, None, None), (14, 101.5, 3.1, -6, 8, None, None),
    (15, 30.2, 1.6, 0, 0, None, None), (16, 127, 37.5, 0, 0, "Seoul", (13, -4)),
    (17, 4.4, 50.8, -21, 1, "Brussels", (-58, -2)), (18, 30.3, 50.8, 14, -11, "Dymer", (14, -14)),
]
for n, lon, lat, dx, dy, lab, loff in PINS:
    tx, ty = proj(lon, lat)
    px, py = tx + dx, ty + dy
    if dx or dy:
        d.line([(tx, ty), (px, py)], fill=(70, 100, 130), width=1)
        d.ellipse([tx - 1.5, ty - 1.5, tx + 1.5, ty + 1.5], fill=(70, 100, 130))
    d.ellipse([px - 6, py - 6, px + 6, py + 6], fill=RED, outline=(255, 255, 255))
    fn = F(DSB, 8)
    s = str(n)
    d.text((px - fn.getlength(s) / 2, py - 5.5), s, font=fn, fill=(255, 255, 255))
    if lab:
        d.text((px + loff[0], py + loff[1]), lab, font=F(DSB, 8), fill=INK,
               stroke_width=1, stroke_fill=(255, 255, 255))
d.text((mx0 + 6, my1 - 13), "RED NUMBERS MARK STORIES 1–18 · POSITIONS APPROXIMATE",
       font=F(DSB, 8), fill=(60, 70, 80))

BRIEFS = [
    "19 India-NZ 1st Test drawn (AP, MON)",
    "20 Sindarov gets White, G1 (FIDE, SUN)",
    "21 Taiwan bans short-selling (CNA, MON)",
    "22 Anthropic −1.4%, $87.64 (FOOL, MON)",
    "23 Bulgari funeral in Rome (ANSA, MON)",
    "24 Trump warns Iran (FOX, SUN)",
    "25 Nigeria debt payoff 2027 (ARISE, MON)",
    "26 Liverpool beat 10-man Utd (BBC, SUN)",
    "27 Thitikul wins 3rd LPGA (AP, SUN)",
    "28 Visegrád loan talks (REUTERS, MON)",
    "29 Trump hush bid revived (AP, MON)",
    "30 Monza 3-0 Fiorentina (LIVESCORE, MON)",
    "31 Levante draw 1-1 with Elche (SKY, MON)",
    "32 Lilly buys LoQus23 $725m (LAW360,MON)",
    "33 Iowa blast goes ahead Wed (WSJ, MON)",
    "34 Commanders 22-20 Bengals (AP, MON)",
    "35 Indonesia fire kills 24 (REUTERS, MON)",
    "36 White House rejects TrumpCare (AP, MON)",
    "37 90+ sign COP31 pledge (REUTERS, MON)",
    "38 Brent −3.5% to $89.37 (REUTERS, MON)",
    "39 Brentford rout Everton 4-0 (SKY, MON)",
    "40 Centrica: bills may rise 26% (BBC, SUN)",
]
cols = [BRIEFS[0:8], BRIEFS[8:15], BRIEFS[15:22]]
fb = F(DJ, 8)
for ci, col in enumerate(cols):
    cx = 428 + ci * 196
    cy = 824
    for b in col:
        lines = wrap(b, fb, 190)
        for ln in lines:
            d.text((cx, cy), ln, font=fb, fill=INK)
            cy += 10
        cy += 1.5

# ---------- DATE CHECK ----------
d.rectangle([8, 938, W - 8, 988], outline=RED, width=2)
dc = ("DATE CHECK — DATES AUDITED · This page covers Monday 23 November 2026. "
      "Sunday events are flagged SUN. "
      "Nvidia's 12 Nov resignation is NOT the story — its Monday return is Lead 1. "
      "Excluded: COP31 'nears deal' (false), Kryvyi Rih (20 Nov), Kerch Bridge "
      "(16–17 Nov), Kospi Tue rebound (+7.2%), Hormuz + Gaza (Sat 21 Nov), "
      "Vancouver 2–0 RSL (Sun 22 Nov), Sinaloa kingpin (Fri 20 Nov), EU–Indonesia "
      "deal (Sat 21 Nov), Kenya–DRC pact (Sun 22 Nov), Santos 0–2 Grêmio (Tue 24 Nov).")
fdc = F(DJ, 11)
dcl = wrap(dc, fdc, W - 32)
draw_lines(d, dcl, 14, 943, fdc, INK, 15)

# ---------- footer ----------
foot = ("Sources: Reuters, BBC, AP, AFP, Guardian, USGS, FIFA, MENAFN, PIB  ·  "
        "SUN = happened Sunday  ·  MON = Monday 23 November 2026")
ff = F(DS, 9)
d.text(((W - ff.getlength(foot)) / 2, 992), foot, font=ff, fill=SOFT)
how = "HOW SURE: ON RECORD = official data  ·  REPORTED = reported by the press  ·  CLAIM = single-source claim"
d.text(((W - ff.getlength(how)) / 2, 1006), how, font=ff, fill=SOFT)

img.save("entry.png", optimize=True)
import os, hashlib
sz = os.path.getsize("entry.png")
md = hashlib.md5(open("entry.png", "rb").read()).hexdigest()
print("entry.png", img.size, sz, "bytes, md5", md)
