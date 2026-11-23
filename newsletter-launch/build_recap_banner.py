"""Banner Recap-Mail: echtes App-Screenshot auf den Greenscreen im ChatGPT-Bild (Petra hält Handy in die Kamera)."""
import os, sys
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
shot_name = sys.argv[1] if len(sys.argv) > 1 else "app-eingang-screen.jpg"
im = Image.open(os.path.join(HERE, "petra-handy-gruen-raw.png")).convert("RGB")
a = np.array(im).astype(np.float32)
r, g, b = a[..., 0], a[..., 1], a[..., 2]
green = np.clip((g - np.maximum(r, b) - 30) / 70, 0, 1)
hard = green > 0.5
ys, xs = np.where(hard)
x0, x1, y0, y1 = xs.min() - 3, xs.max() + 3, ys.min() - 3, ys.max() + 3
# Maske: weich, leicht geweitet, damit kein grüner Saum bleibt
mask = Image.fromarray((green * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(0.8))
W, H = x1 - x0, y1 - y0
s = Image.open(os.path.join(ROOT, shot_name)).convert("RGB")
sc = max(W / s.width, H / s.height)
s = s.resize((round(s.width * sc), round(s.height * sc)), Image.LANCZOS)
cx = (s.width - W) // 2
cy = int((s.height - H) * 0.35)
s = s.crop((cx, cy, cx + W, cy + H))
layer = im.copy(); layer.paste(s, (x0, y0))
out = Image.composite(layer, im, mask)
# restlichen Grünstich an den Kanten entfärben
o = np.array(out).astype(np.float32)
spill = (o[..., 1] > np.maximum(o[..., 0], o[..., 2]) + 25)
o[..., 1] = np.where(spill, np.maximum(o[..., 0], o[..., 2]) + 5, o[..., 1])
out = Image.fromarray(np.clip(o, 0, 255).astype(np.uint8))
out = out.resize((1240, round(1240 * out.height / out.width)), Image.LANCZOS)
out.save(os.path.join(ROOT, "recap-banner.jpg"), quality=88, optimize=True, progressive=True)
print("ok", out.size, os.path.getsize(os.path.join(ROOT, "recap-banner.jpg")))
