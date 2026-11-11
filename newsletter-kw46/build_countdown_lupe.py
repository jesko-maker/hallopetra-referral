from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
import sys
OUT = sys.argv[1]
W, H = 1240, 420
BLUE = (43, 69, 212)
FB = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FR = "/System/Library/Fonts/Supplemental/Arial.ttf"
CX, CY, R = 620, 210, 176
NUMS = ["5", "4", "3", "2", "1", "0"]
GAPX = 210
xs = [CX + (i - 3) * GAPX for i in range(len(NUMS))]

def dial(scale=1.0, alpha=70, bold_center=False):
    """Zahlenreihe + Skala, um (CX,CY) skaliert."""
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    f = ImageFont.truetype(FB, int(150 * scale))
    for n, x in zip(NUMS, xs):
        x2 = CX + (x - CX) * scale
        a = 255 if (bold_center and n == "2") else alpha
        d.text((x2, CY - 8 * scale), n, font=f, fill=(255, 255, 255, a), anchor="mm")
    # feine Skala unter den Zahlen
    for i in range(-60, 61):
        x = CX + i * (GAPX / 10) * scale
        if 0 <= x <= W:
            big = i % 10 == 0
            h = (22 if big else 10) * scale
            y0 = CY + 110 * scale
            d.line([(x, y0), (x, y0 + h)], fill=(255, 255, 255, 110 if big else 55), width=max(1, int(2 * scale)))
    return L

bg = Image.new("RGBA", (W, H), BLUE + (255,))
# Hintergrund: Zahlenreihe, leicht weich, zum Rand hin ausblendend
base = dial(1.0, 60).filter(ImageFilter.GaussianBlur(1.2))
fade = Image.new("L", (W, H), 0)
fd = ImageDraw.Draw(fade)
for x in range(W):
    v = int(255 * max(0.0, 1 - (abs(x - CX) / (W / 2)) ** 1.6))
    fd.line([(x, 0), (x, H)], fill=v)
base.putalpha(ImageChops.multiply(base.getchannel("A"), fade))
img = Image.alpha_composite(bg, base)

# Schatten der Lupe
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(sh).ellipse((CX - R, CY - R + 18, CX + R, CY + R + 18), fill=(10, 20, 90, 120))
img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(26)))

# Inhalt in der Lupe: eigene Ebene, Nachbarn 3 und 1 ragen an den Rand
inner_bg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ig = ImageDraw.Draw(inner_bg)
for y in range(H):  # leichter Verlauf, oben heller
    t = max(0, min(1, (y - (CY - R)) / (2 * R)))
    c = tuple(int(a + (b2 - a) * t) for a, b2 in zip((78, 102, 232), (48, 74, 214)))
    ig.line([(0, y), (W, y)], fill=c + (255,))
mag = inner_bg
dd = ImageDraw.Draw(mag)
fbig = ImageFont.truetype(FB, 200)
dd.text((CX, CY - 24), "2", font=fbig, fill=(255, 255, 255, 255), anchor="mm")
for n, dx in (("3", -170), ("1", 170)):
    dd.text((CX + dx, CY - 24), n, font=fbig, fill=(255, 255, 255, 120), anchor="mm")
for i in range(-20, 21):
    x = CX + i * 32
    big = i % 5 == 0
    dd.line([(x, CY + 128), (x, CY + 128 + (26 if big else 12))], fill=(255, 255, 255, 140 if big else 70), width=3)
dd.text((CX, CY + 96), "WOCHEN", font=ImageFont.truetype(FB, 28), fill=(255, 255, 255, 240), anchor="mm")
blurred = mag.filter(ImageFilter.GaussianBlur(10))
# Maske: Mitte scharf -> Rand weich
m = Image.new("L", (W, H), 0)
md = ImageDraw.Draw(m)
for r in range(R, 0, -1):
    t = r / R
    v = 0 if t < 0.66 else int(255 * min(1, ((t - 0.66) / 0.34) ** 1.2))
    md.ellipse((CX - r, CY - r, CX + r, CY + r), fill=v)
lens = Image.composite(blurred, mag, m)
circle = Image.new("L", (W, H), 0)
ImageDraw.Draw(circle).ellipse((CX - R, CY - R, CX + R, CY + R), fill=255)
circle = circle.filter(ImageFilter.GaussianBlur(0.8))
img.paste(lens, (0, 0), circle)

# Glanz: oben links heller Schimmer, unten rechts zarter Schatten
gl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(gl)
gd.ellipse((CX - R + 22, CY - R + 14, CX + R - 70, CY - 10), fill=(255, 255, 255, 34))
gl = gl.filter(ImageFilter.GaussianBlur(22))
gl.putalpha(ImageChops.multiply(gl.getchannel("A"), circle))
img = Image.alpha_composite(img, gl)
# Rand: feiner heller Ring + innerer dunkler Ring
rim = Image.new("RGBA", (W, H), (0, 0, 0, 0))
rd = ImageDraw.Draw(rim)
rd.ellipse((CX - R, CY - R, CX + R, CY + R), outline=(255, 255, 255, 150), width=3)
rd.ellipse((CX - R + 5, CY - R + 5, CX + R - 5, CY + R - 5), outline=(20, 35, 140, 60), width=4)
img = Image.alpha_composite(img, rim.filter(ImageFilter.GaussianBlur(0.6)))
# Lichtkante oben
hl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(hl).arc((CX - R + 3, CY - R + 3, CX + R - 3, CY + R - 3), 200, 300, fill=(255, 255, 255, 200), width=3)
img = Image.alpha_composite(img, hl.filter(ImageFilter.GaussianBlur(1.2)))

img.convert("RGB").save(OUT, optimize=True)
print("ok", OUT)
