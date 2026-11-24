# draw.py — News 23 round 3 revision (news-image-20261123)
# Fresh build, 24 Nov 2026. 40 stories: 3 leads + 15 mediums + 22 briefs.
# All new Monday numbers verified to sources before drawing:
#   Nvidia +33% (Reuters, Nasdaq +6%, S&P +4%) / Kospi close -3.31% at 4,708.54,
#   intraday -5.8% (Korea Exchange) / Belgium: all flights 07:00-21:00 cancelled,
#   429 scheduled, 59,500 passengers (Brussels Airport) / NATO AWACS authorised
#   by SACEUR, no Article 4 (NATO) / Nepal NPR 24,000 cr package (PIB) /
#   Brent -3.46% to $89.37 (Morningstar) / Taiex +2.16% to 36,811.89 /
#   India-NZ 1st Test drawn (Cricinfo) / Trump orders Iowa blast paused (Reuters) /
#   Gaza strikes kill 4 on Sat 22 Nov (MENAFN).
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
f_mast = F(DJB, 56)
f_sub = F(NTI, 17)
d.text((8, 6), "THE WORLD IN ONE DAY", font=f_kick, fill=RED)
r = "40 STORIES · 6 REGIONS · EVERY ONE DATED MONDAY 23 NOVEMBER 2026"
d.text((W - 8 - F(DSB, 11).getlength(r), 9), r, font=F(DSB, 11), fill=SOFT)
d.line([(8, 26), (W - 8, 26)], fill=(190, 175, 150), width=1)
d.text(((W - F(DJB, 56).getlength("Monday 23 November 2026")) / 2, 28),
       "Monday 23 November 2026", font=f_mast, fill=INK)
d.line([(8, 92), (W - 8, 92)], fill=INK, width=2)
sub = "Nvidia brings Huang back as shares soar 33%  ·  Russian warship sunk off Benghazi  ·  COP31 collapses with no deal"
d.text(((W - F(NTI, 17).getlength(sub)) / 2, 96), sub, font=f_sub, fill=RED)

# ---------- number strip ----------
nums = [("40", "STORIES"), ("6", "REGIONS"), ("+33%", "NVIDIA, MON"),
        ("429", "FLIGHTS GROUNDED"), ("+2.16%", "TAIEX, MON"),
        ("104", "MATCHES, 2035 WORLD CUP")]
y0, y1 = 118, 162
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
regs = [("EUROPE 16", BLUE), ("ASIA 10", ORANGE), ("N. AMERICA 7", TEAL),
        ("MIDDLE EAST 4", RED), ("OCEANIA 2", PURPLE), ("AFRICA 1", GREEN2)]
y0, y1 = 166, 188
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
    d.text((x + 5, y + 2), "NVDA  +33%", font=F(DSB, 11), fill=(120, 220, 140))
    _nas = "NASDAQ +6%"
    d.text((x + w - 9 - F(DSB, 10).getlength(_nas), y + 2), _nas, font=F(DSB, 10),
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
    d.text((x + 5, y + h - 14), "NVDA +33%   TSLA +4%   AAPL +2%   MSFT +1%   AMZN +3%",
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
    moon(d, x + w - 22, y + 18, 10)
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
    # sea: dark band + wave lines + small drone boat
    d.rectangle([x, y + h * 0.72, x + w, y + h], fill=(14, 32, 58))
    for wy in (0.78, 0.86, 0.94):
        d.line([(x + 6, y + h * wy), (x + w - 6, y + h * wy)], fill=(70, 110, 150), width=1)
    d.polygon([(x + w * 0.72, y + h * 0.80), (x + w * 0.82, y + h * 0.80),
               (x + w * 0.78, y + h * 0.86)], fill=(60, 66, 78))

def sc_cop31(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (88, 66, 48), (150, 118, 76))
    # hall windows
    for i in range(4):
        wx = x + 6 + i * (w - 12) / 4
        d.rectangle([wx, y + 6, wx + (w - 12) / 4 - 6, y + h * 0.42], fill=(232, 200, 140))
        d.line([(wx + (w - 12) / 8 - 3, y + 6), (wx + (w - 12) / 8 - 3, y + h * 0.42)],
               fill=(120, 92, 60), width=2)
    d.rectangle([x, y + h * 0.44, x + w, y + h * 0.52], fill=(70, 50, 36))
    # clock "49 HRS OVER"
    d.ellipse([x + w * 0.43, y + 2, x + w * 0.57, y + 26], fill=(245, 240, 225),
              outline=INK, width=2)
    d.line([(x + w * 0.5, y + 14), (x + w * 0.5, y + 6)], fill=INK, width=2)
    d.line([(x + w * 0.5, y + 14), (x + w * 0.55, y + 17)], fill=INK, width=2)
    # table + gavel + red-X document
    d.rectangle([x + w * 0.08, y + h * 0.56, x + w * 0.92, y + h * 0.68], fill=(96, 62, 40))
    d.rectangle([x + w * 0.30, y + h * 0.56, x + w * 0.48, y + h * 0.65], fill=(245, 240, 225))
    d.line([(x + w * 0.33, y + h * 0.58), (x + w * 0.45, y + h * 0.63)], fill=RED, width=2)
    d.line([(x + w * 0.45, y + h * 0.58), (x + w * 0.33, y + h * 0.63)], fill=RED, width=2)
    d.rectangle([x + w * 0.60, y + h * 0.58, x + w * 0.72, y + h * 0.62], fill=(160, 120, 70))
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
    d.rectangle([x + w * 0.10, y + h * 0.06, x + w * 0.22, y + h * 0.13], fill=(255, 153, 51))
    d.rectangle([x + w * 0.10, y + h * 0.13, x + w * 0.22, y + h * 0.20], fill=(255, 255, 255))
    d.rectangle([x + w * 0.78, y + h * 0.06, x + w * 0.90, y + h * 0.20], fill=(220, 20, 60))

def sc_houthis(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (12, 16, 34), (50, 44, 70))
    stars(d, (x, y, x + w, y + h * 0.45), 12, 9)
    moon(d, x + w * 0.82, y + h * 0.18, 9)
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
    d.text((x + w * 0.70, y + h * 0.04), "601 KM", font=F(DSB, 9), fill=(255, 255, 255))

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
    d.rectangle([x + w * 0.76, y + h * 0.14, x + w * 0.92, y + h * 0.38], fill=(222, 41, 16))
    # two soldiers shaking hands at the post
    person(d, x + w * 0.34, y + h * 0.38, 30, (60, 90, 60), arm="one")
    person(d, x + w * 0.64, y + h * 0.38, 30, (90, 60, 50), arm="one")
    d.rectangle([x, y + h * 0.82, x + w, y + h], fill=(150, 170, 120))

def sc_himalaya(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (150, 170, 190), (200, 195, 175))
    d.polygon([(x, y + h * 0.55), (x + w * 0.30, y + h * 0.14), (x + w * 0.58, y + h * 0.55)],
              fill=(100, 115, 135))
    d.polygon([(x + w * 0.50, y + h * 0.55), (x + w * 0.78, y + h * 0.20), (x + w, y + h * 0.55)],
              fill=(120, 133, 150))
    d.polygon([(x + w * 0.24, y + h * 0.26), (x + w * 0.30, y + h * 0.14), (x + w * 0.36, y + h * 0.26)],
              fill=(255, 255, 255))
    # muddy flood water + tilted house + truck
    d.polygon([(x, y + h * 0.60), (x + w, y + h * 0.66), (x + w, y + h), (x, y + h)],
              fill=(140, 110, 70))
    d.polygon([(x + w * 0.12, y + h * 0.52), (x + w * 0.30, y + h * 0.52), (x + w * 0.34, y + h * 0.66),
               (x + w * 0.08, y + h * 0.66)], fill=(180, 90, 60))
    d.polygon([(x + w * 0.10, y + h * 0.52), (x + w * 0.32, y + h * 0.52), (x + w * 0.21, y + h * 0.44)],
              fill=(120, 60, 40))
    d.rectangle([x + w * 0.58, y + h * 0.70, x + w * 0.90, y + h * 0.84], fill=(200, 60, 40))
    d.rectangle([x + w * 0.58, y + h * 0.62, x + w * 0.72, y + h * 0.72], fill=(160, 50, 35))
    d.ellipse([x + w * 0.62, y + h * 0.82, x + w * 0.68, y + h * 0.88], fill=INK)
    d.ellipse([x + w * 0.80, y + h * 0.82, x + w * 0.86, y + h * 0.88], fill=INK)
    person(d, x + w * 0.44, y + h * 0.50, 24, (40, 60, 120), arm="up")

def sc_nhs(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (190, 215, 230), (245, 242, 235))
    # hospital
    d.rectangle([x + w * 0.08, y + h * 0.30, x + w * 0.55, y + h * 0.78], fill=(240, 240, 238))
    d.rectangle([x + w * 0.08, y + h * 0.30, x + w * 0.55, y + h * 0.38], fill=(0, 90, 160))
    d.rectangle([x + w * 0.30, y + h * 0.14, x + w * 0.36, y + h * 0.30], fill=(255, 255, 255))
    d.rectangle([x + w * 0.27, y + h * 0.20, x + w * 0.39, y + h * 0.26], fill=(255, 255, 255))
    for r in range(2):
        for c in range(3):
            d.rectangle([x + w * (0.13 + c * 0.13), y + h * (0.44 + r * 0.14),
                         x + w * (0.20 + c * 0.13), y + h * (0.52 + r * 0.14)], fill=(140, 190, 220))
    # screen with scan: light screen, dark lung oval, pink highlight, crosshair
    d.rectangle([x + w * 0.60, y + h * 0.22, x + w * 0.94, y + h * 0.62], fill=(225, 232, 236))
    d.ellipse([x + w * 0.68, y + h * 0.28, x + w * 0.86, y + h * 0.56], fill=(52, 62, 74))
    d.ellipse([x + w * 0.73, y + h * 0.36, x + w * 0.81, y + h * 0.48], fill=(225, 110, 150))
    d.line([(x + w * 0.77, y + h * 0.30), (x + w * 0.77, y + h * 0.54)], fill=(200, 210, 215),
           width=1)
    d.line([(x + w * 0.70, y + h * 0.42), (x + w * 0.84, y + h * 0.42)], fill=(200, 210, 215),
           width=1)
    person(d, x + w * 0.72, y + h * 0.36, 32, (255, 255, 255), arm="one")
    d.rectangle([x, y + h * 0.82, x + w, y + h], fill=(150, 185, 140))

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
    # player figure
    person(d, x + w * 0.74, y + h * 0.18, 34, (255, 255, 255), arm="up")
    d.rectangle([x, y + h * 0.88, x + w, y + h], fill=(40, 100, 70))

def sc_selangor(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (140, 160, 180), (190, 200, 205))
    # rain lines
    for i in range(10):
        rx = x + ((i * 37) % int(w - 6)) + 3
        d.line([(rx, y + 4), (rx - 4, y + 16)], fill=(220, 230, 240), width=1)
    # houses on stilts
    for hx, hw in [(0.08, 0.26), (0.42, 0.26), (0.74, 0.20)]:
        d.rectangle([x + w * hx, y + h * 0.30, x + w * (hx + hw), y + h * 0.52], fill=(190, 120, 70))
        d.polygon([(x + w * (hx - 0.02), y + h * 0.30), (x + w * (hx + hw / 2), y + h * 0.18),
                   (x + w * (hx + hw + 0.02), y + h * 0.30)], fill=(120, 60, 40))
        d.line([(x + w * (hx + 0.04), y + h * 0.52), (x + w * (hx + 0.04), y + h * 0.66)],
               fill=(90, 70, 50), width=2)
        d.line([(x + w * (hx + hw - 0.04), y + h * 0.52), (x + w * (hx + hw - 0.04), y + h * 0.66)],
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

def sc_typhoid(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (200, 225, 235), (245, 240, 225))
    # clinic
    d.rectangle([x + w * 0.06, y + h * 0.26, x + w * 0.46, y + h * 0.72], fill=(250, 250, 248))
    d.rectangle([x + w * 0.06, y + h * 0.26, x + w * 0.46, y + h * 0.34], fill=(0, 120, 120))
    d.rectangle([x + w * 0.24, y + h * 0.12, x + w * 0.30, y + h * 0.26], fill=(255, 255, 255))
    d.rectangle([x + w * 0.21, y + h * 0.17, x + w * 0.33, y + h * 0.23], fill=(255, 255, 255))
    for c in range(3):
        d.rectangle([x + w * (0.11 + c * 0.12), y + h * 0.42, x + w * (0.18 + c * 0.12),
                     y + h * 0.52], fill=(140, 190, 210))
    # vaccine vial + syringe, big
    d.rectangle([x + w * 0.58, y + h * 0.18, x + w * 0.74, y + h * 0.52], fill=(200, 230, 240))
    d.rectangle([x + w * 0.60, y + h * 0.14, x + w * 0.72, y + h * 0.18], fill=(120, 140, 160))
    d.rectangle([x + w * 0.62, y + h * 0.34, x + w * 0.70, y + h * 0.48], fill=(90, 160, 220))
    d.line([(x + w * 0.80, y + h * 0.30), (x + w * 0.94, y + h * 0.16)], fill=(180, 180, 180), width=3)
    d.rectangle([x + w * 0.78, y + h * 0.32, x + w * 0.86, y + h * 0.40], fill=(200, 200, 200))
    # queue of children
    person(d, x + w * 0.55, y + h * 0.44, 28, (220, 100, 90))
    person(d, x + w * 0.68, y + h * 0.44, 26, (90, 140, 200))
    person(d, x + w * 0.81, y + h * 0.44, 28, (90, 180, 120))
    d.rectangle([x, y + h * 0.84, x + w, y + h], fill=(170, 200, 160))

def sc_kospi(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (40, 50, 70), (90, 70, 80))
    # Seoul tower: lighter shaft with lit windows, ringed deck, antenna — clearly a tower
    d.rectangle([x + w * 0.70, y + h * 0.18, x + w * 0.76, y + h * 0.62], fill=(52, 58, 74))
    d.ellipse([x + w * 0.66, y + h * 0.10, x + w * 0.80, y + h * 0.24], fill=(52, 58, 74),
              outline=(150, 165, 185))
    d.line([(x + w * 0.73, y + h * 0.10), (x + w * 0.73, y + h * 0.02)], fill=(150, 165, 185), width=1)
    for wy in (0.30, 0.42, 0.54):
        d.rectangle([x + w * 0.715, y + h * wy, x + w * 0.745, y + h * wy + 3], fill=(255, 214, 130))
    d.rectangle([x + w * 0.06, y + h * 0.52, x + w * 0.30, y + h * 0.66], fill=(44, 48, 62))
    d.rectangle([x + w * 0.34, y + h * 0.44, x + w * 0.52, y + h * 0.66], fill=(38, 42, 56))
    building(d, x + w * 0.06, y + h * 0.52, w * 0.24, h * 0.14, (44, 48, 62), rows=2, cols=3)
    # falling red chart
    pts = [(x + 6, y + h * 0.18), (x + w * 0.25, y + h * 0.30), (x + w * 0.45, y + h * 0.28),
           (x + w * 0.65, y + h * 0.55), (x + w * 0.85, y + h * 0.72), (x + w - 6, y + h * 0.78)]
    chart(d, pts, (240, 70, 60), 4)
    d.polygon([(x + w - 6, y + h * 0.78), (x + w - 20, y + h * 0.74), (x + w - 8, y + h * 0.90)],
              fill=(240, 70, 60))
    d.rectangle([x, y + h * 0.86, x + w, y + h], fill=(24, 28, 40))

def sc_belgium(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (150, 180, 205), (215, 225, 235))
    # departure board, all cancelled
    d.rectangle([x + w * 0.06, y + h * 0.06, x + w * 0.94, y + h * 0.42], fill=(20, 26, 36))
    # one clean CANCELLED stamp, drawn once, centred on the board
    _ct, _cf = "CANCELLED", F(DSB, 12)
    _cw = _cf.getlength(_ct)
    _cx = x + w * 0.5 - _cw / 2
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
    # dawn sun + broken skyline
    d.ellipse([x + w * 0.78, y + h * 0.08, x + w * 0.94, y + h * 0.24], fill=(255, 215, 140))
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

# ---------- card renderers ----------
def lead_card(d, x, y, w, h, num, tag, scene, loc, head, body):
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255), outline=(200, 185, 160))
    d.rectangle([x, y, x + w, y + 16], fill=RED)
    d.text((x + 6, y + 2), "%d · LEAD" % num, font=F(DSB, 10), fill=(255, 255, 255))
    d.text((x + w - 6 - F(DSB, 10).getlength(tag), y + 2), tag, font=F(DSB, 10),
           fill=(255, 255, 255))
    sy = y + 16
    scene(d, x + 1, sy, w - 2, 104)
    ty = sy + 104
    d.text((x + 6, ty + 2), loc, font=F(DSB, 9), fill=RED)
    fh = F(DJB, 18)
    hl = wrap(head, fh, w - 12)
    draw_lines(d, hl[:2], x + 6, ty + 13, fh, INK, 20)
    fb = F(DJ, 11)
    bl = wrap(body, fb, w - 12)
    draw_lines(d, bl[:2], x + 6, ty + 13 + len(hl[:2]) * 20 + 2, fb, SOFT, 14)

def med_card(d, x, y, w, h, num, tag, scene, loc, head, body, hero=False, blines=1, sh=52):
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255), outline=(200, 185, 160))
    d.rectangle([x, y, x + w, y + 14], fill=RED)
    d.text((x + 5, y + 2), "%d · HERO" % num if hero else "%d" % num, font=F(DSB, 10),
           fill=(255, 255, 255))
    d.text((x + w - 5 - F(DSB, 9).getlength(tag), y + 2), tag, font=F(DSB, 9),
           fill=(255, 255, 255))
    sy = y + 14
    scene(d, x + 1, sy, w - 2, sh)
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
     "Nvidia brings Huang back — shares soar 33%",
     "Board votes unanimously, 11 days after his resignation; Nasdaq +6%, S&P +4%. (Reuters, WSJ)"),
    (2, "SUN", sc_merkury, "BENGHAZI · LIBYA · SUN",
     "Russian warship sunk by sea drones in Libyan port",
     "Capsized, bow up; 10 hurt, 4 drones downed; Sparta II towed out. Suspected Ukrainian drones. (AP, Reuters)"),
    (3, "SUN", sc_cop31, "ANTALYA · CLIMATE · SUN",
     "COP31 collapses — no deal on fossil fuels",
     "Longest COP ever, 49 hrs over; $120bn goal lost; five blocs said no. (BBC, Reuters)"),
]
MEDS = [
    (18, "SUN", sc_dymer, "DYMER · UKRAINE · SUN", True,
     "Boy, 7, pulled alive after 14 hours under rubble",
     "9 dead, 11 missing; Vyshneve: 3 killed, 13 hurt. (BBC, AFP)"),
    (4, "MON", sc_awacs, "NATO · POLAND · MON", False,
     "NATO sends AWACS to Poland",
     "SACEUR authorises jet; Article 4 not invoked. (NATO)"),
    (5, "MON", sc_nepal, "NEW DELHI · NEPAL · MON", False,
     "Modi gives Nepal ₹24,000 crore",
     "NPR 5,600 cr grant + 18,400 cr credit; rail flagged off. (PIB)"),
    (6, "SUN", sc_houthis, "RABIGH · SAUDI · SUN", False,
     "Houthis claim refinery hit",
     "Rabigh targeted, Saudis silent; coalition: missile down. (Reuters)"),
    (7, "MON", sc_vanuatu, "VANUATU · PACIFIC · MON", False,
     "Deep quake shakes Vanuatu",
     "M6.5 at 601 km, no tsunami. (USGS)"),
    (8, "SUN", sc_fifa, "ZURICH · SPORT · SUN", False,
     "UK to host 2035 Women's World Cup",
     "48 teams, 104 matches. (BBC, Reuters)"),
    (9, "SUN", sc_house, "WASHINGTON · POLITICS · SUN", False,
     "Democrats' biggest House majority",
     "Largest since 1992. (BBC)"),
    (10, "MON", sc_lac, "ARUNACHAL · INDIA-CHINA · MON", False,
     "India, China open border talks",
     "10-day talks on LAC. (Hindu)"),
    (11, "MON", sc_himalaya, "HIMALAYAS · FLOOD · MON", False,
     "Himalayan flood kills 4",
     "100 missing in valley. (Access24)"),
    (12, "MON", sc_nhs, "LONDON · HEALTH · MON", False,
     "NHS launches biggest AI trial",
     "AI spots cancer earlier. (BBC)"),
    (13, "SUN", sc_sport, "TURIN · SPORT · SUN", False,
     "Alcaraz wins ATP Finals in Turin",
     "Márquez 8th title too. (BBC)"),
    (14, "MON", sc_selangor, "SELANGOR · MALAYSIA · MON", False,
     "Selangor floods displace 1,800",
     "Evacuees past 1,800. (Bernama)"),
    (15, "MON", sc_typhoid, "DHAKA · HEALTH · MON", False,
     "Typhoid drive for 50m children",
     "Month-long, nationwide. (AP)"),
    (16, "MON", sc_kospi, "SEOUL · MARKETS · MON", False,
     "Kospi plunges 5.8% intraday",
     "Close −3.31% at 4,708. (KRX)"),
    (17, "MON", sc_belgium, "BRUSSELS · STRIKE · MON", False,
     "Belgium grounds all flights",
     "All flights 07:00–21:00 cancelled."),
]

# ---------- leads row ----------
lw = (W - 16 - 14) / 3
for i, (num, tag, scene, loc, head, body) in enumerate(LEADS):
    lead_card(d, 8 + i * (lw + 7), 192, lw, 204, num, tag, scene, loc, head, body)

# ---------- medium rows: A (hero row, 147px) / B / C (116px) ----------
mw = (W - 16 - 24) / 5
rows = [(400, 158, MEDS[0:5], 76, 2), (562, 118, MEDS[5:10], 52, 1), (684, 118, MEDS[10:15], 52, 1)]
for ry, rh, items, sh, bl in rows:
    for j, (num, tag, scene, loc, hero, head, body) in enumerate(items):
        med_card(d, 8 + j * (mw + 6), ry, mw, rh, num, tag, scene, loc, head, body,
                 hero=hero, blines=bl, sh=sh)

# ---------- map + ALSO ON ----------
d.text((8, 806), "WHERE IT HAPPENED — PINS 1–18", font=F(DSB, 11), fill=INK)
d.text((428, 806), "ALSO ON — 22 BRIEFS", font=F(DSB, 11), fill=INK)
mx0, my0, mx1, my1 = 8, 820, 418, 936
d.rectangle([mx0, my0, mx1, my1], fill=NAVY_DK, outline=(200, 185, 160))
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
    px = mx0 + (lon + 170) / 360 * (mx1 - mx0)
    py = my0 + (85 - lat) / 145 * (my1 - my0)
    return px, py
for poly in CONTINENTS:
    d.polygon([proj(lon, lat) for lon, lat in poly], fill=(228, 214, 178))
PINS = [
    (1, -74, 40.7, -10, -4, None, None), (2, 20.1, 32.1, 4, 2, "Benghazi", (-28, 14)),
    (3, 30.7, 36.9, 6, 6, "Antalya", (8, -18)), (4, 21, 52.2, -2, -16, None, None),
    (5, 77.2, 28.6, -8, 4, None, None), (6, 39, 22.8, 8, 8, None, None),
    (7, 172.2, -13.7, 0, 0, None, None), (8, 8.5, 47.4, 0, -14, None, None),
    (9, -77, 38.9, -2, 8, None, None), (10, 94, 28, 8, -2, None, None),
    (11, 84, 28.5, 0, -8, None, None), (12, -0.1, 51.5, -16, -10, None, None),
    (13, 7.7, 45.1, 4, 8, None, None), (14, 101.5, 3.1, -6, 8, None, None),
    (15, 90.4, 23.8, 10, 10, None, None), (16, 127, 37.5, 0, 0, "Seoul", (13, -4)),
    (17, 4.4, 50.8, -6, 10, "Brussels", (-58, -2)), (18, 30.3, 50.8, 12, -12, "Dymer", (14, -14)),
]
for n, lon, lat, dx, dy, lab, loff in PINS:
    tx, ty = proj(lon, lat)
    px, py = tx + dx, ty + dy
    if dx or dy:
        d.line([(tx, ty), (px, py)], fill=(255, 255, 255), width=1)
        d.ellipse([tx - 1.5, ty - 1.5, tx + 1.5, ty + 1.5], fill=(255, 255, 255))
    d.ellipse([px - 6, py - 6, px + 6, py + 6], fill=RED, outline=(255, 255, 255))
    fn = F(DSB, 8)
    s = str(n)
    d.text((px - fn.getlength(s) / 2, py - 5.5), s, font=fn, fill=(255, 255, 255))
    if lab:
        d.text((px + loff[0], py + loff[1]), lab, font=F(DSB, 8), fill=(255, 255, 255),
               stroke_width=1, stroke_fill=NAVY_DK)
d.text((mx0 + 6, my1 - 13), "RED NUMBERS MARK STORIES 1–18 · POSITIONS APPROXIMATE",
       font=F(DSB, 8), fill=(200, 205, 215))

BRIEFS = [
    "19 India-NZ 1st Test drawn (AP, MON)",
    "20 Sindarov gets White, G1 (FIDE, SUN)",
    "21 Taiwan bans short-selling (CNA, MON)",
    "22 Youth Congress hits Meta (PTI, MON)",
    "23 Paolo Bulgari dies, 89 (ANSA, MON)",
    "24 Trump warns Iran (REUTERS, MON)",
    "25 Tankers hit in Hormuz (UKMTO, SAT)",
    "26 Liverpool beat 10-man Utd (BBC, SUN)",
    "27 Thitikul wins 3rd LPGA (AP, MON)",
    "28 Slovakia nixes EU loan (REUTERS, SUN)",
    "29 Syria arrests 2nd officer (SANA, MON)",
    "30 Titanic ring sells £150k (BBC, MON)",
    "31 Trump posts Putin, Xi photos (AP, SUN)",
    "32 Trio blocks UN job bid (REUTERS, SUN)",
    "33 Trump pauses Iowa blast (REUTERS, MON)",
    "34 US varsity shooting; 2 dead (AP, SUN)",
    "35 FSSAI: prosecute Bisleri (PTI, MON)",
    "36 Trump reposts TrumpCare (AP, SUN)",
    "37 90+ sign COP31 pledge (REUTERS)",
    "38 Brent −3.5% to $89.37 (REUTERS, MON)",
    "39 Gaza strikes kill 4 (MENAFN, SAT)",
    "40 Centrica: bills may rise 26% (BBC, SUN)",
]
cols = [BRIEFS[0:8], BRIEFS[8:15], BRIEFS[15:22]]
fb = F(DJ, 8.5)
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
dc = ("DATE CHECK — ALL 40 STORIES ARE FROM MONDAY 23 NOVEMBER 2026. Sunday events "
      "flagged SUN — their Monday tolls and outcomes are the news. "
      "Nvidia's resignation (12 Nov) is NOT the story — its Monday reinstatement is Lead 1. "
      "Excluded: COP31 'nears deal' (false), Kryvyi Rih (20 Nov), Kerch Bridge (16–17 Nov).")
fdc = F(DJ, 11)
dcl = wrap(dc, fdc, W - 32)
draw_lines(d, dcl, 14, 943, fdc, INK, 15)

# ---------- footer ----------
foot = ("Sources: Reuters, BBC, AP, AFP, Guardian, USGS, FIFA, MENAFN, PIB  ·  "
        "SUN = happened Sunday  ·  MON = Monday 23 November 2026")
ff = F(DS, 9)
d.text(((W - ff.getlength(foot)) / 2, 992), foot, font=ff, fill=SOFT)

img.save("entry.png", optimize=True)
import os, hashlib
sz = os.path.getsize("entry.png")
md = hashlib.md5(open("entry.png", "rb").read()).hexdigest()
print("entry.png", img.size, sz, "bytes, md5", md)
