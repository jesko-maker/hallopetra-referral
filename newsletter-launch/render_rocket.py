"""Fotorealistische Launch-Grafik: 3D-Rakete (SDF-Raymarching in torch), Sternenhimmel,
gesprungene Lupe, die den Hintergrund verzerrt. Aufruf: python3 render_rocket.py out.png"""
import math, sys, random
import numpy as np
import torch
import torch.nn.functional as Fn
from PIL import Image, ImageDraw, ImageFont, ImageFilter

torch.manual_seed(3); random.seed(3); np.random.seed(3)
OUT = sys.argv[1]
W, H = 1240, 700           # Ausgabe
SS = 2                     # Supersampling
W2, H2 = W * SS, H * SS
UNIT = 45 * SS             # Pixel pro Welteinheit (Kernradius = 1)
dev = "cpu"
BG = np.array([5, 8, 26]) / 255.0

# ---------------- Geometrie ----------------
LC = (W2 / 2, 352 * SS)            # Lupenmitte = Bildmitte
LR = 228 * SS
TILT = math.radians(27)            # Neigung nach rechts
PITCH = math.radians(-33)          # Spitze kommt auf den Betrachter zu
CAMD = 22.0                        # Kameraabstand zur Glasebene (Perspektive)
BZ = 2.8                           # Raketenfuß liegt hinter dem Glas (z>0)
BASE_PX = (LC[0] - 30 * SS, LC[1] + 95 * SS)


def px2world(x, y, z=0.0):
    k = (z + CAMD) / CAMD
    return (x - W2 / 2) / UNIT * k, -(y - H2 / 2) / UNIT * k


def world2px(p):
    k = CAMD / (p[2] + CAMD)
    return (W2 / 2 + p[0] * k * UNIT, H2 / 2 - p[1] * k * UNIT)


BW = px2world(*BASE_PX, BZ)
B = torch.tensor([BW[0], BW[1], BZ])
ca, sa, cp, sp = math.cos(TILT), math.sin(TILT), math.cos(PITCH), math.sin(PITCH)
Rz = torch.tensor([[ca, sa, 0], [-sa, ca, 0], [0, 0, 1.0]])          # Rz(-tilt)
Rx = torch.tensor([[1, 0, 0], [0, cp, -sp], [0, sp, cp]])            # Rx(pitch)
R = Rz @ Rx                       # lokal -> Welt
RT = R.T                          # Welt -> lokal


def to_local(p):
    return (p - B) @ RT.T


def to_world_dir(v):
    return v @ R.T


def ogive(y, y0, L, r0, k=0.62):
    t = ((y - y0) / L).clamp(0, 1)
    return r0 * (1 - t * t).clamp(min=0) ** k


def sdf(q):
    x, y, z = q[..., 0], q[..., 1], q[..., 2]
    # Hauptstufe + Nutzlastverkleidung
    rho = torch.sqrt(x * x + z * z)
    rc = torch.where(y < 6.85, torch.ones_like(y), torch.full_like(y, 1.07))
    rc = torch.where(y > 7.25, ogive(y, 7.25, 3.25, 1.07), rc)
    d_core = torch.maximum((rho - rc) * 0.72, torch.maximum(-y - 0.0, y - 10.5))
    # Booster
    ds = []
    for bx in (-1.56, 1.56):
        rb_ = torch.sqrt((x - bx) ** 2 + z * z)
        rb = torch.where(y > 4.7, ogive(y, 4.7, 1.35, 0.47, 0.58), torch.full_like(y, 0.47))
        ds.append(torch.maximum((rb_ - rb) * 0.72, torch.maximum(-y - 0.3, y - 6.05)))
    d_boost = torch.minimum(ds[0], ds[1])
    # Düsen (Haupttriebwerk + Booster)
    t = ((-y) / 1.05).clamp(0, 1)
    rn = 0.30 + 0.26 * t ** 1.4
    d_noz = torch.maximum((rho - rn) * 0.7, torch.maximum(y - 0.02, -y - 1.05))
    for bx in (-1.56, 1.56):
        rb_ = torch.sqrt((x - bx) ** 2 + z * z)
        tb = ((-y - 0.3) / 0.45).clamp(0, 1)
        rbn = 0.22 + 0.15 * tb
        d_noz = torch.minimum(d_noz, torch.maximum((rb_ - rbn) * 0.7, torch.maximum(y + 0.28, -y - 0.75)))
    # Streben zwischen Kern und Boostern
    for yy in (0.55, 4.35):
        for bx in (-1.28, 1.28):
            dxs = torch.stack([(x - bx).abs() - 0.22, (y - yy).abs() - 0.06, z.abs() - 0.07], -1)
            d_noz = torch.minimum(d_noz, dxs.clamp(min=0).norm(dim=-1) + dxs.max(-1).values.clamp(max=0))
    d = torch.minimum(torch.minimum(d_core, d_boost), d_noz)
    mat = torch.where(d == d_core, 0, torch.where(d == d_boost, 1, 2))
    return d, mat


def sdf_d(q):
    return sdf(q)[0]


# ---------------- Raymarching (orthografisch) ----------------
ys, xs = torch.meshgrid(torch.arange(H2, dtype=torch.float32) + 0.5, torch.arange(W2, dtype=torch.float32) + 0.5, indexing="ij")
wx = (xs - W2 / 2) / UNIT
wy = -(ys - H2 / 2) / UNIT
ro = torch.tensor([0, 0, -CAMD]).expand(H2 * W2, 3)
rd = Fn.normalize(torch.stack([wx, wy, torch.full_like(wx, CAMD)], -1).reshape(-1, 3), dim=-1)
tt = torch.zeros(ro.shape[0])
hit = torch.zeros(ro.shape[0], dtype=torch.bool)
active = torch.ones(ro.shape[0], dtype=torch.bool)
# Bounding: nur Pixel nahe der Rakete marschieren
cx_b, cy_b = world2px((to_world_dir(torch.tensor([0, 4.5, 0.0])) + B).tolist())
near = ((xs.reshape(-1) - cx_b) ** 2 + (ys.reshape(-1) - cy_b) ** 2) < (7.5 * UNIT) ** 2
active &= near
for i in range(160):
    idx = active.nonzero().squeeze(1)
    if idx.numel() == 0:
        break
    p = ro[idx] + rd[idx] * tt[idx, None]
    d = sdf_d(to_local(p))
    tt[idx] += d
    h = d < 0.0015
    hit[idx[h]] = True
    done = h | (tt[idx] > 70)
    active[idx[done]] = False
print("march ok", int(hit.sum()))

hidx = hit.nonzero().squeeze(1)
P = ro[hidx] + rd[hidx] * tt[hidx, None]
Q = to_local(P)
_, MAT = sdf(Q)
e = 0.002
k1 = torch.tensor([1, -1, -1.0]); k2 = torch.tensor([-1, -1, 1.0]); k3 = torch.tensor([-1, 1, -1.0]); k4 = torch.tensor([1, 1, 1.0])
Nl = (k1 * sdf_d(Q + k1 * e)[:, None] + k2 * sdf_d(Q + k2 * e)[:, None] + k3 * sdf_d(Q + k3 * e)[:, None] + k4 * sdf_d(Q + k4 * e)[:, None])
Nl = Fn.normalize(Nl, dim=-1)
N = to_world_dir(Nl)
V = -rd[hidx]

# ---------------- Material / Textur ----------------
qx, qy, qz = Q[:, 0], Q[:, 1], Q[:, 2]
alb = torch.ones(len(hidx), 3) * torch.tensor([0.93, 0.93, 0.92])
rough = torch.full((len(hidx),), 1.0)


def band(y, y0, w):
    return ((y - y0).abs() < w).float()


core = MAT == 0
boost = MAT == 1
noz = MAT == 2
seam = torch.zeros_like(qy)
for ysm in (1.6, 3.2, 4.8, 6.85, 7.25):
    seam = torch.maximum(seam, band(qy, ysm, 0.022) * core.float())
for ysm in (1.25, 2.5, 3.75, 4.7):
    seam = torch.maximum(seam, band(qy, ysm, 0.02) * boost.float())
alb = alb * (1 - 0.45 * seam[:, None])
# HalloPetra-Blau: Band unter der Verkleidung + Booster-Spitzen
blue = torch.tensor([0.10, 0.17, 0.78])
bmask = (core & (qy > 6.2) & (qy < 6.7)) | (boost & (qy > 5.2))
alb[bmask] = blue
# Düsen: dunkles Metall
alb[noz] = torch.tensor([0.16, 0.16, 0.18])
# leichte Rußspuren unten
soot = ((0.9 - qy).clamp(0, 0.9) / 0.9) * (core | boost).float()
alb = alb * (1 - 0.25 * soot[:, None]) + torch.tensor([0.05, 0.03, 0.0]) * soot[:, None]

# Wortmarke „hallopetra“ entlang der Achse (zylindrische UV)
FONT_R = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_B = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
TW, TH = 1200, 220
timg = Image.new("L", (TW, TH), 0)
td = ImageDraw.Draw(timg)
f1 = ImageFont.truetype(FONT_R, 190); f2 = ImageFont.truetype(FONT_B, 190)
w1 = td.textlength("hallo", font=f1); w2 = td.textlength("petra", font=f2)
x0 = (TW - w1 - w2) / 2
td.text((x0, TH / 2), "hallo", font=f1, fill=255, anchor="lm")
td.text((x0 + w1, TH / 2), "petra", font=f2, fill=255, anchor="lm")
tex = torch.tensor(np.array(timg.filter(ImageFilter.GaussianBlur(1.0))), dtype=torch.float32) / 255
theta = torch.atan2(qx, -qz)
u = theta * 1.0
Y0, Y1, U0 = 0.55, 3.85, 0.34
tx = ((qy - Y0) / (Y1 - Y0) * TW).long().clamp(0, TW - 1)
ty = ((u + U0) / (2 * U0) * TH).long().clamp(0, TH - 1)
inside = core & (qy > Y0) & (qy < Y1) & (u.abs() < U0)
a = torch.where(inside, tex[ty, tx], torch.zeros_like(qy))
navy = torch.tensor([0.06, 0.09, 0.30])
alb = alb * (1 - a[:, None]) + navy * a[:, None]

# ---------------- Licht ----------------
L1 = Fn.normalize(torch.tensor([-0.62, 0.50, -0.60]), dim=0)    # Sonne oben links vorn
L2 = Fn.normalize(torch.tensor([0.80, -0.35, -0.45]), dim=0)    # blaues Fülllicht
c1 = torch.tensor([1.0, 0.96, 0.90]) * 1.55
c2 = torch.tensor([0.25, 0.38, 1.0]) * 0.32


def soft_shadow(p, l, kk=10.0):
    res = torch.ones(p.shape[0])
    t = torch.full((p.shape[0],), 0.04)
    for _ in range(56):
        h = sdf_d(to_local(p + l * t[:, None]))
        res = torch.minimum(res, (kk * h / t).clamp(0, 1))
        t = t + h.clamp(0.02, 0.4)
    return res.clamp(0, 1) ** 1.5


Pn = P + N * 0.01
sh = soft_shadow(Pn, L1)
ao = torch.ones(len(hidx))
for i in range(1, 6):
    hh = 0.06 * i
    ao -= (hh - sdf_d(to_local(P + N * hh))).clamp(min=0) * (0.5 ** i) * 4
ao = ao.clamp(0.25, 1)

ndl1 = (N @ L1).clamp(min=0)
ndl2 = (N @ L2).clamp(min=0)
Hh = Fn.normalize(L1 + V, dim=-1)
spec_pow = torch.where(noz, torch.tensor(30.0), torch.tensor(70.0))
spec = (N * Hh).sum(-1).clamp(min=0) ** spec_pow * torch.where(noz, torch.tensor(0.6), torch.tensor(0.32))
fres = (1 - (N * V).sum(-1).clamp(0, 1)) ** 4
# Glut des Triebwerks von unten (lokal unterhalb der Düse)
plume_pos = to_world_dir(torch.tensor([0, -2.0, 0.0])) + B
Lp = plume_pos - P
dist = Lp.norm(dim=-1)
Lp = Lp / dist[:, None]
glow = ((N * Lp).sum(-1).clamp(min=0) * 3.2 / (1 + dist * dist * 0.55))[:, None] * torch.tensor([1.0, 0.55, 0.22])
amb = (0.05 + 0.05 * N[:, 1:2].clamp(min=0)) * torch.tensor([0.55, 0.65, 1.0])

col = alb * (c1 * (ndl1 * sh)[:, None] + c2 * ndl2[:, None] + amb + glow) * ao[:, None]
col = col + (spec * sh)[:, None] * c1 + fres[:, None] * torch.tensor([0.30, 0.42, 0.95]) * 0.55
rocket_rgb = torch.zeros(H2 * W2, 3)
rocket_rgb[hidx] = col
rocket_a = torch.zeros(H2 * W2)
rocket_a[hidx] = 1.0
front_a = torch.zeros(H2 * W2)
front_a[hidx] = (P[:, 2] < 0).float()
front_a = front_a.reshape(H2, W2)
rocket_rgb = rocket_rgb.reshape(H2, W2, 3)
rocket_a = rocket_a.reshape(H2, W2)
print("shade ok")

# ---------------- Rauschen ----------------
def fbm(h, w, octaves=6, base=6, persist=0.55, seed=0):
    g = torch.Generator().manual_seed(seed)
    out = torch.zeros(h, w); amp = 1.0; tot = 0
    for o in range(octaves):
        gh, gw = base * 2 ** o, int(base * 2 ** o * w / h)
        n = torch.rand(1, 1, gh + 3, gw + 3, generator=g)
        n = Fn.interpolate(n, size=(h + 0, w + 0), mode="bicubic", align_corners=False)[0, 0]
        out += n * amp; tot += amp; amp *= persist
    return out / tot


# ---------------- Hintergrund: Sternenhimmel ----------------
sky = torch.tensor(BG, dtype=torch.float32).view(1, 1, 3).expand(H2, W2, 3).clone()
neb = fbm(H2 // 4, W2 // 4, 6, 3, 0.6, 11)
neb = Fn.interpolate(neb[None, None], size=(H2, W2), mode="bilinear")[0, 0]
# sanftes Milchstraßenband diagonal
bandm = torch.exp(-((ys - (H2 * 0.95 - xs * 0.55)) / (H2 * 0.32)) ** 2)
sky += (neb - 0.45).clamp(min=0)[..., None] * bandm[..., None] * torch.tensor([0.10, 0.12, 0.32]) * 1.4
sky += (0.06 * torch.exp(-(((xs - W2 * 0.75) / (W2 * 0.4)) ** 2 + ((ys - H2 * 0.2) / (H2 * 0.5)) ** 2)))[..., None] * torch.tensor([0.25, 0.35, 1.0])
stars = torch.zeros(H2, W2)
n_st = 1400
sxs = torch.randint(0, W2, (n_st,)); sys_ = torch.randint(0, H2, (n_st,))
br = torch.rand(n_st) ** 6 * 2.2 + 0.08
stars[sys_, sxs] = br
stars = Fn.conv2d(stars[None, None], torch.tensor([[[[0.05, 0.2, 0.05], [0.2, 1, 0.2], [0.05, 0.2, 0.05]]]]), padding=1)[0, 0]
tint = torch.where(torch.rand(H2, W2) > 0.5, torch.tensor(1.0), torch.tensor(0.85))
sky += stars[..., None] * torch.stack([tint, torch.ones_like(tint) * 0.95, torch.ones_like(tint)], -1)

# ---------------- Abgasstrahl + Rauch ----------------
axis_s = torch.tensor([sa, ca])                 # Bildrichtung „nach oben entlang Rakete“ (x, -y)
down = None


def proj(local):
    w = to_world_dir(torch.tensor(local, dtype=torch.float32)) + B
    return world2px(w.tolist())


_a, _b = proj([0, -1.0, 0]), proj([0, -5.0, 0])
_v = torch.tensor([_b[0] - _a[0], _b[1] - _a[1]]); _v = _v / _v.norm()


nozzles = [proj([0, -1.05, 0]), proj([-1.56, -0.75, 0]), proj([1.56, -0.75, 0])]
down = _v
perp = torch.tensor([-_v[1], _v[0]])
fire = torch.zeros(H2, W2, 3)
for k, (nx, ny) in enumerate(nozzles):
    dx, dy = xs - nx, ys - ny
    s = (dx * down[0] + dy * down[1]) / UNIT
    d = (dx * perp[0] + dy * perp[1]) / UNIT
    rad0 = 0.42 if k == 0 else 0.30
    wdt = rad0 * (1 + 0.25 * s.clamp(min=0))
    core_j = torch.exp(-(d / (wdt * 0.55)) ** 2) * torch.exp(-(s.clamp(min=0) / (2.6 if k == 0 else 2.0)) ** 1.6) * (s > -0.05).float()
    fire += core_j[..., None] * torch.tensor([3.2, 2.6, 1.7])
    outer = torch.exp(-(d / (wdt * 1.1)) ** 2) * torch.exp(-(s.clamp(min=0) / 3.6) ** 1.3) * (s > -0.05).float()
    fire += outer[..., None] * torch.tensor([1.6, 0.75, 0.22])

# Rauchsäule
nx, ny = nozzles[0]
dx, dy = xs - nx, ys - ny
s = (dx * down[0] + dy * down[1]) / UNIT
d = (dx * perp[0] + dy * perp[1]) / UNIT
noise = fbm(H2 // 2, W2 // 2, 6, 5, 0.58, 5)
noise = Fn.interpolate(noise[None, None], size=(H2, W2), mode="bilinear")[0, 0]
noise2 = Fn.interpolate(fbm(H2 // 2, W2 // 2, 5, 9, 0.5, 9)[None, None], size=(H2, W2), mode="bilinear")[0, 0]
wid = 1.0 + 0.75 * s.clamp(min=0)
dd = (d + (noise2 - 0.5) * 2.2) / wid
dens = torch.exp(-dd ** 2 * 1.3) * ((s - 0.8) / 1.4).clamp(0, 1) * (0.55 + 1.8 * (noise - 0.40)).clamp(0, 1.4)
dens = dens.clamp(0, 1)
# Beleuchtung des Rauchs: Sonnenseite heller, unten warm von der Glut
lit = 0.62 + 0.38 * torch.tanh(-d / wid * 1.8)
warm = torch.exp(-(s.clamp(min=0) - 1.5).clamp(min=0) / 2.2)
smoke_col = (torch.tensor([1.25, 1.27, 1.38]) * lit[..., None] * (0.45 + 0.9 * noise[..., None])
             + torch.tensor([1.0, 0.55, 0.2]) * (warm * 1.1)[..., None])
smoke_a = (dens * 1.25).clamp(0, 0.97)

scene_bg = sky * (1 - smoke_a[..., None]) + smoke_col * smoke_a[..., None]
scene_bg = scene_bg + fire

# ---------------- Lupe: Verzerrung des Hintergrunds ----------------
lx, ly = LC
rr = torch.sqrt((xs - lx) ** 2 + (ys - ly) ** 2) / LR
inside_l = rr < 1
m = 0.70 + 0.25 * rr ** 2          # Mitte stark vergrößert, Rand fast normal (Lupeneffekt)
srcx = lx + (xs - lx) * m
srcy = ly + (ys - ly) * m
# leichte chromatische Aberration am Rand
grid_r = torch.stack([(srcx * (1 + 0.004 * rr ** 2) - lx * 0.004 * rr ** 2) / W2 * 2 - 1, srcy / H2 * 2 - 1], -1)
grid = torch.stack([srcx / W2 * 2 - 1, srcy / H2 * 2 - 1], -1)
behind = scene_bg * (1 - (rocket_a - front_a)[..., None]) + rocket_rgb * (rocket_a - front_a)[..., None]
img_t = behind.permute(2, 0, 1)[None]
mag = Fn.grid_sample(img_t, grid[None], mode="bilinear", align_corners=False)[0].permute(1, 2, 0)
mag_r = Fn.grid_sample(img_t, grid_r[None], mode="bilinear", align_corners=False)[0].permute(1, 2, 0)
mag[..., 0] = mag_r[..., 0]
mag = mag * 1.06 + torch.tensor([0.02, 0.035, 0.10])        # Glas leicht bläulich
ringv = torch.exp(-((1 - rr) / 0.06) ** 2)                     # Lichtbrechung am Glasrand
mag = mag + ringv[..., None] * torch.tensor([0.10, 0.16, 0.40])
mag = mag + (torch.exp(-((rr - 0.9) / 0.05) ** 2) * 0.05)[..., None]
comp_pre = mag

# Bruchloch in der Lupe (wo die Rakete austritt): in Richtung Raketenachse am Rand
hx, hy = proj([0, 5.2, 0])          # dort durchstößt die Rakete die Glasebene
exit_ang = math.atan2(hy - ly, hx - lx)
hole_pts = []
for kk in range(26):
    ang = 2 * math.pi * kk / 26
    r_ = (1.0 if kk % 2 == 0 else 0.74) * random.uniform(0.85, 1.15) * 118 * SS
    hole_pts.append((hx + r_ * math.cos(ang) * 1.05, hy + r_ * math.sin(ang) * 0.85))
hole_img = Image.new("L", (W2, H2), 0)
ImageDraw.Draw(hole_img).polygon(hole_pts, fill=255)
hole = torch.tensor(np.array(hole_img), dtype=torch.float32) / 255
glass = inside_l.float() * (1 - hole)
comp = behind * (1 - glass[..., None]) + comp_pre * glass[..., None]

# Rakete einsetzen; hinter dem Glas leicht getönt
comp = comp * (1 - front_a[..., None]) + rocket_rgb * front_a[..., None]

# Glasreflex oben links (nur auf Glas)
refl = torch.exp(-(((xs - (lx - LR * 0.35)) / (LR * 0.55)) ** 2 + ((ys - (ly - LR * 0.45)) / (LR * 0.28)) ** 2))
comp = comp + (refl * glass * 0.16)[..., None]

# ---------------- Bloom ----------------
lum = comp.clamp(min=0)
bright = (lum - 0.85).clamp(min=0)
bt = bright.permute(2, 0, 1)[None]
bloom = torch.zeros_like(bt)
for k_, wgt in ((9, 0.5), (31, 0.5), (91, 0.6), (181, 0.5)):
    b = Fn.avg_pool2d(bt, k_, stride=1, padding=k_ // 2, count_include_pad=False)
    b = Fn.avg_pool2d(b, k_, stride=1, padding=k_ // 2, count_include_pad=False)
    bloom += b * wgt
comp = comp + bloom[0].permute(1, 2, 0)

# Tonemapping (ACES-Näherung) + Gamma
x = comp.clamp(min=0) * 1.05
x = (x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14)
x = x.clamp(0, 1) ** (1 / 1.0)
base_img = Image.fromarray((x.numpy() * 255).astype(np.uint8))

# ---------------- Vektor-Overlay: Risse, Fassung, Splitter ----------------
ov = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
od = ImageDraw.Draw(ov)
# Risse von der Bruchstelle über das Glas
for kk in range(16):
    ang = 2 * math.pi * kk / 16 + random.uniform(-0.2, 0.2)
    x0_, y0_ = hx + 105 * SS * math.cos(ang), hy + 85 * SS * math.sin(ang)
    pts = [(x0_, y0_)]
    Lr = random.uniform(110, 300) * SS
    for st in range(1, 6):
        aa = ang + random.uniform(-0.3, 0.3)
        r_ = Lr * st / 5
        pts.append((x0_ + r_ * math.cos(aa), y0_ + r_ * math.sin(aa)))
    od.line(pts, fill=(255, 255, 255, random.randint(70, 150)), width=random.choice([2, 3, 4]), joint="curve")
crack = ov
# auf Glas beschränken
gm = Image.fromarray((glass.numpy() * 255).astype(np.uint8))
ca_ = crack.getchannel("A")
crack.putalpha(Image.fromarray(np.minimum(np.array(ca_), np.array(gm))))
# Bruchkante
edge = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
ImageDraw.Draw(edge).line(hole_pts + [hole_pts[0]], fill=(225, 235, 255, 200), width=3 * SS, joint="curve")
lens_mask = Image.new("L", (W2, H2), 0)
ImageDraw.Draw(lens_mask).ellipse((lx - LR, ly - LR, lx + LR, ly + LR), fill=255)
ra = np.array(Image.fromarray((front_a.numpy() * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5)))
em = np.minimum(np.array(edge.getchannel("A")), np.array(lens_mask))
em = (em * (1 - ra / 255.0)).astype(np.uint8)
edge.putalpha(Image.fromarray(em))

# Fassung: Metallring mit Lücke an der Austrittsstelle
rim = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
rdr = ImageDraw.Draw(rim)
gap_c = math.degrees(exit_ang)
_dist = math.hypot(hx - lx, hy - ly) / LR
_gap = 22 if _dist > 0.55 else 0
a0, a1 = gap_c + _gap, gap_c + 360 - _gap
for wdt, colr in ((14 * SS, (40, 50, 80, 255)), (10 * SS, (170, 180, 205, 255)), (4 * SS, (240, 244, 255, 255))):
    rdr.arc((lx - LR, ly - LR, lx + LR, ly + LR), a0, a1, fill=colr, width=wdt)
# Glanzlicht oben links auf der Fassung
gl = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
ImageDraw.Draw(gl).arc((lx - LR + 3 * SS, ly - LR + 3 * SS, lx + LR - 3 * SS, ly + LR - 3 * SS), 190, 250, fill=(255, 255, 255, 255), width=4 * SS)
gl = gl.filter(ImageFilter.GaussianBlur(2 * SS))
# Griff der Lupe (unten links, angedeutet)
hg = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
hd = ImageDraw.Draw(hg)
ang = math.radians(135)
p0 = (lx + (LR + 6 * SS) * math.cos(ang), ly + (LR + 6 * SS) * math.sin(ang))
p1 = (lx + (LR + 210 * SS) * math.cos(ang), ly + (LR + 210 * SS) * math.sin(ang))
hd.line([p0, p1], fill=(22, 28, 52, 255), width=34 * SS)
hd.line([(p0[0] - 6 * SS, p0[1] - 6 * SS), (p1[0] - 6 * SS, p1[1] - 6 * SS)], fill=(90, 100, 135, 255), width=6 * SS)
# weggesprengte Fassungsstücke
pieces = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
pdw = ImageDraw.Draw(pieces)
for off, span, shift in ((-24, 12, (-40, -70)), (14, 10, (55, -60)), (-8, 7, (10, -120))):
    c_ = gap_c + off
    sx, sy = shift[0] * SS, shift[1] * SS
    pdw.arc((lx - LR + sx, ly - LR + sy, lx + LR + sx, ly + LR + sy), c_ - span / 2, c_ + span / 2, fill=(225, 232, 250, 255), width=8 * SS)


def shard_layer(n, blur, size_rng, dist_rng, alpha_rng):
    L_ = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
    d_ = ImageDraw.Draw(L_)
    for _ in range(n):
        ang_ = exit_ang + random.uniform(-1.2, 1.2)
        dist_ = random.uniform(*dist_rng) * SS
        cx_ = hx + dist_ * math.cos(ang_); cy_ = hy + dist_ * math.sin(ang_)
        sz = random.uniform(*size_rng) * SS
        kq = random.randint(3, 4); rot = random.uniform(0, 2 * math.pi)
        pts = []
        for j in range(kq):
            aj = rot + 2 * math.pi * j / kq + random.uniform(-0.5, 0.5)
            rj = sz * random.uniform(0.5, 1.0)
            pts.append((cx_ + rj * math.cos(aj), cy_ + rj * math.sin(aj) * random.uniform(0.4, 1)))
        a_ = random.randint(*alpha_rng)
        d_.polygon(pts, fill=(150, 175, 255, a_ // 4), outline=(235, 242, 255, a_), width=max(2, int(sz / 12)))
        d_.line([pts[0], pts[1]], fill=(255, 255, 255, min(255, a_ + 40)), width=max(2, int(sz / 9)))
    return L_.filter(ImageFilter.GaussianBlur(blur)) if blur else L_


sh_back = shard_layer(26, 1.5 * SS, (5, 13), (120, 560), (90, 170))
sh_front = shard_layer(9, 3.5 * SS, (16, 30), (90, 420), (140, 220))
sh_mid = shard_layer(16, 0, (7, 18), (80, 380), (170, 240))

img = base_img.convert("RGBA")
for layer in (crack, edge, rim, gl, sh_back, sh_mid, sh_front):
    img = Image.alpha_composite(img, layer)

# Rakete muss vor Fassung/Splittern liegen, wo sie außerhalb des Glases ist: Raketenpixel erneut drüberlegen,
# aber nur außerhalb der Lupenscheibe (dort ist sie „ausgebrochen“)
rk_only = base_img.convert("RGBA")
out_mask = np.maximum(front_a.numpy(), rocket_a.numpy() * (1 - glass.numpy())).clip(0, 1)
rk_only.putalpha(Image.fromarray((out_mask * 255).astype(np.uint8)))
img = Image.alpha_composite(img, rk_only)
img = Image.alpha_composite(img, sh_front)

# Vignette an den Rändern auf Kartenfarbe
img = img.convert("RGB").resize((W, H), Image.LANCZOS)
arr = np.array(img).astype(np.float32) / 255
yy, xx = np.mgrid[0:H, 0:W]
vig = np.clip(1 - (((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.70)) ** 2) ** 2 * 0.28, 0.0, 1)
arr = arr * vig[..., None] + BG * (1 - vig[..., None])
Image.fromarray((arr.clip(0, 1) * 255).astype(np.uint8)).save(OUT, quality=95)
print("ok", OUT)
