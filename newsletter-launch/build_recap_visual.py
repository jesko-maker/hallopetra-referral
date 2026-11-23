"""Recap-Grafik App-Woche: Petra verzaubert vorne, echte App-Store-Stimmen (Kuhlmann GmbH) + Zahl als Karten dahinter.
Ausgabe: recap-petra-stimmen.jpg (1240x820, im Mail als 620px)."""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
W, H = 1240, 820
FB = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FR = "/System/Library/Fonts/Supplemental/Arial.ttf"
FBL = "/System/Library/Fonts/Supplemental/Arial Black.ttf"


def font(p, s):
    return ImageFont.truetype(p, s)


# Hintergrund: Blau-Verlauf mit Lichtkegel in der Mitte
y, x = np.mgrid[0:H, 0:W].astype(np.float32)
top, bot = np.array([43, 69, 212], np.float32), np.array([15, 26, 60], np.float32)
t = (y / H)[..., None]
bg = top * (1 - t) + bot * t
d = np.sqrt(((x - W / 2) / (W * 0.42)) ** 2 + ((y - H * 0.58) / (H * 0.55)) ** 2)
glow = np.clip(1 - d, 0, 1)[..., None] ** 2
bg = bg + glow * np.array([70, 90, 160], np.float32)
img = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).convert("RGBA")

# kleine Funkelpunkte
rng = np.random.default_rng(7)
dr = ImageDraw.Draw(img)
for _ in range(70):
    px, py = rng.integers(0, W), rng.integers(0, H)
    r = rng.choice([1, 1, 1.5, 2])
    a = int(rng.integers(60, 170))
    dr.ellipse([px - r, py - r, px + r, py + r], fill=(255, 255, 255, a))


def wrap(draw, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=f) <= maxw:
            cur = test
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def review_card(text, w, stars=True, src="Kuhlmann GmbH · App Store", fs=30):
    pad = 30
    tmp = Image.new("RGBA", (10, 10))
    dt = ImageDraw.Draw(tmp)
    f = font(FB, fs)
    lines = wrap(dt, text, f, w - 2 * pad)
    lh = int(fs * 1.28)
    h = pad + (44 if stars else 0) + lh * len(lines) + 16 + 26 + pad
    card = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dc = ImageDraw.Draw(card)
    dc.rounded_rectangle([0, 0, w - 1, h - 1], radius=26, fill=(255, 255, 255, 255))
    yy = pad
    if stars:
        dc.text((pad, yy - 4), "★★★★★", font=font("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", 32), fill=(255, 181, 0))
        yy += 44
    for ln in lines:
        dc.text((pad, yy), ln, font=f, fill=(15, 26, 60))
        yy += lh
    yy += 16
    dc.text((pad, yy), src, font=font(FR, 22), fill=(108, 120, 143))
    return card


def place(card, cx, cy, angle):
    c = card.rotate(angle, resample=Image.BICUBIC, expand=True)
    sh = Image.new("RGBA", c.size, (0, 0, 0, 0))
    sh.paste((5, 10, 40, 110), mask=c.split()[3])
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    x0, y0 = int(cx - c.width / 2), int(cy - c.height / 2)
    img.alpha_composite(sh, (x0 + 6, y0 + 16))
    img.alpha_composite(c, (x0, y0))


import sys
# Quelle des Zitats: mit Firmennamen nur nach Zustimmung von Kuhlmann (Entwurf 23.11.), sonst neutral
QUOTE_SRC = "Kuhlmann GmbH · App Store" if "--kuhlmann" in sys.argv else "Bewertung im App Store"


def stat_card(big, line1, line2, w=330, bg=(255, 255, 255, 255), fg=(15, 26, 60), sub=(108, 120, 143), star=False):
    c = Image.new("RGBA", (w, 210), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([0, 0, w - 1, 209], radius=26, fill=bg)
    d.text((30, 20), big, font=font(FBL, 80), fill=fg)
    if star:
        bw = d.textlength(big, font=font(FBL, 80))
        d.text((30 + bw + 10, 36), "★", font=font("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", 60), fill=(255, 181, 0))
    d.text((32, 122), line1, font=font(FB, 26), fill=sub)
    d.text((32, 156), line2, font=font(FB, 26), fill=sub)
    return c


# Karten hinter Petra: ein Zitat (wörtlich, Bewertung vom 17.11.) + echte Zahlen
place(stat_card("50+", "Betriebe direkt in", "der App gewechselt", w=340), 215, 300, 5)

# Petra vorne, unten mittig
p = Image.open(os.path.join(HERE, "petra-verzaubert-raw.png")).convert("RGBA")
p = p.crop(p.getbbox())
ph = 760
p = p.resize((int(p.width * ph / p.height), ph), Image.LANCZOS)
# weicher Schatten/Leuchten hinter Petra
halo = Image.new("RGBA", p.size, (0, 0, 0, 0))
halo.paste((120, 160, 255, 120), mask=p.split()[3])
halo = halo.filter(ImageFilter.GaussianBlur(30))
px0 = (W - p.width) // 2
img.alpha_composite(halo, (px0, H - ph))
img.alpha_composite(p, (px0, H - ph))

# Zahl-Karte rechts
num = Image.new("RGBA", (360, 230), (0, 0, 0, 0))
dn = ImageDraw.Draw(num)
dn.rounded_rectangle([0, 0, 359, 229], radius=26, fill=(18, 185, 129, 255))
dn.text((30, 22), "200+", font=font(FBL, 92), fill=(255, 255, 255))
dn.text((32, 136), "Betriebe sind schon", font=font(FB, 27), fill=(255, 255, 255))
dn.text((32, 172), "auf Petra 2.0", font=font(FB, 27), fill=(255, 255, 255))
place(num, 1030, 420, -4)

img.convert("RGB").save(os.path.join(ROOT, "recap-petra-stimmen.jpg"), quality=88, optimize=True, progressive=True)
print("ok", os.path.getsize(os.path.join(ROOT, "recap-petra-stimmen.jpg")))
