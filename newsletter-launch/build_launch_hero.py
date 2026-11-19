"""Launch-Grafik: Die Countdown-Lupe reißt auf, eine Rakete steigt heraus.
SVG -> PNG über Chrome headless. Aufruf: python3 build_launch_hero.py out.png"""
import math, random, subprocess, sys, os, tempfile

OUT = sys.argv[1]
W, H = 1240, 700
CX, LY, R = 620, 480, 168          # Lupe
random.seed(7)

def f(v): return f"{v:.1f}"

# ---------- Hintergrund: Sterne + verblasste Skala ----------
stars = []
for _ in range(140):
    x, y = random.uniform(0, W), random.uniform(0, H * 0.75)
    r = random.choice([0.8, 0.8, 1.0, 1.2, 1.6])
    o = random.uniform(0.15, 0.55) * (1 - y / H)
    stars.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{r}" fill="#fff" opacity="{o:.2f}"/>')

ticks = []
for i in range(-60, 61):
    x = CX + i * 25
    big = i % 10 == 0
    ticks.append(f'<line x1="{x}" y1="{LY+190}" x2="{x}" y2="{LY+190+(22 if big else 10)}" stroke="#fff" stroke-opacity="{0.35 if big else 0.18}" stroke-width="2"/>')

# ---------- Riss-Loch in der Lupe ----------
HX, HY = CX, LY - R + 22           # Bruchstelle oben an der Fassung
pts = []
n = 22
for k in range(n):
    a = 2 * math.pi * k / n
    rr = (92 if k % 2 == 0 else 70) * random.uniform(0.9, 1.12)
    pts.append((HX + rr * math.cos(a), HY - 10 + rr * 0.55 * math.sin(a)))
hole = " ".join(f"{f(x)},{f(y)}" for x, y in pts)

cracks = []
for k in range(14):
    a = 2 * math.pi * k / 14 + random.uniform(-0.15, 0.15)
    x, y = HX + 85 * math.cos(a), HY + 45 * math.sin(a)
    d = f"M{f(x)},{f(y)}"
    L = random.uniform(70, 150)
    steps = 4
    for s in range(1, steps + 1):
        aa = a + random.uniform(-0.25, 0.25)
        rr = 85 + L * s / steps
        d += f" L{f(HX + rr*math.cos(aa))},{f(HY + rr*0.85*math.sin(aa))}"
    cracks.append(f'<path d="{d}" fill="none" stroke="#fff" stroke-opacity="{random.uniform(0.35,0.7):.2f}" stroke-width="{random.choice([1.2,1.6,2.2])}" stroke-linejoin="round"/>')
# Ringförmige Querrisse
for k in range(6):
    a0 = random.uniform(0, 2*math.pi); a1 = a0 + random.uniform(0.3, 0.7)
    rr = random.uniform(85, 130)
    cracks.append(f'<path d="M{f(HX+rr*math.cos(a0))},{f(HY+rr*0.85*math.sin(a0))} Q{f(HX+(rr+8)*math.cos((a0+a1)/2))},{f(HY+(rr+8)*0.85*math.sin((a0+a1)/2))} {f(HX+rr*math.cos(a1))},{f(HY+rr*0.85*math.sin(a1))}" fill="none" stroke="#fff" stroke-opacity="0.35" stroke-width="1.2"/>')

# ---------- Glassplitter ----------
def shard(cx, cy, size, rot, blur, op):
    k = random.randint(3, 4)
    ps = []
    for j in range(k):
        a = 2*math.pi*j/k + random.uniform(-0.5, 0.5)
        rr = size * random.uniform(0.55, 1.0)
        ps.append((rr*math.cos(a), rr*math.sin(a)*random.uniform(0.4, 1.0)))
    p = " ".join(f"{f(x)},{f(y)}" for x, y in ps)
    flt = f' filter="url(#b{blur})"' if blur else ""
    return (f'<g transform="translate({f(cx)},{f(cy)}) rotate({f(rot)})" opacity="{op:.2f}"{flt}>'
            f'<polygon points="{p}" fill="url(#glass)" stroke="#fff" stroke-opacity="0.95" stroke-width="1.6" stroke-linejoin="round"/>'
            f'<polyline points="{f(ps[0][0]*0.6)},{f(ps[0][1]*0.6)} {f(ps[1][0]*0.6)},{f(ps[1][1]*0.6)}" stroke="#fff" stroke-opacity="0.8" stroke-width="1.2" fill="none"/></g>')

shards_back, shards_front = [], []
for _ in range(30):
    a = random.uniform(math.radians(190), math.radians(350))    # nach oben/seitlich
    dist = random.uniform(90, 470)
    x, y = HX + dist*math.cos(a)*1.25, HY + dist*math.sin(a)*0.95
    if abs(x - CX) < 80 and y < HY + 20:      # nicht in die Rakete
        x += 110 if x >= CX else -110
    size = random.uniform(7, 26) * (1.25 if dist > 300 else 1)
    blur = 0 if size < 18 else random.choice([0, 1, 2])
    (shards_front if blur == 2 or size > 20 else shards_back).append(
        shard(x, y, size, random.uniform(0, 360), blur, random.uniform(0.6, 0.95)))

# Randstücke der Fassung, die weggesprengt werden
rim_pieces = []
for a0, a1, dx, dy, rot in [(-122, -104, -34, -56, -18), (-78, -62, 30, -60, 16), (-140, -126, -44, -22, -8), (-56, -44, 40, -26, 10)]:
    a0r, a1r = math.radians(a0), math.radians(a1)
    d = (f"M{f(CX+R*math.cos(a0r))},{f(LY+R*math.sin(a0r))} "
         f"A{R},{R} 0 0 1 {f(CX+R*math.cos(a1r))},{f(LY+R*math.sin(a1r))}")
    mx, my = CX+R*math.cos((a0r+a1r)/2), LY+R*math.sin((a0r+a1r)/2)
    rim_pieces.append(f'<g transform="translate({dx},{dy}) rotate({rot} {f(mx)} {f(my)})"><path d="{d}" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" opacity="0.9"/></g>')
# Fassung mit Lücke oben
ga0, ga1 = math.radians(-44), math.radians(220)
rim_d = (f"M{f(CX+R*math.cos(ga0))},{f(LY+R*math.sin(ga0))} "
         f"A{R},{R} 0 1 1 {f(CX+R*math.cos(ga1))},{f(LY+R*math.sin(ga1))}")

# ---------- Rauch ----------
smoke = []
for _ in range(36):
    side = random.choice([-1, 1])
    t = random.random()
    x = CX + side * t * random.uniform(20, 170)
    y = LY + 100 + random.uniform(-30, 70)
    r = 30 + random.uniform(0, 30)
    o = random.uniform(0.25, 0.55)
    smoke.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="url(#puff)" opacity="{o:.2f}"/>')
plume = []
for k in range(16):           # Rauchsäule direkt unter dem Triebwerk
    y = HY - 20 + k * 8
    plume.append(f'<circle cx="{f(HX + random.uniform(-14,14))}" cy="{f(y)}" r="{f(40 + k*4)}" fill="url(#puff)" opacity="0.55"/>')

# ---------- Rakete (lokale Koordinaten: Spitze bei 0, Länge 340) ----------
RL = 340
rocket = f'''
<g transform="translate({CX},{LY + 6 - 356})">
  <!-- Flamme -->
  <g filter="url(#b3)">
    <ellipse cx="0" cy="{RL+80}" rx="36" ry="90" fill="url(#flameOuter)"/>
  </g>
  <g filter="url(#b1)">
    <ellipse cx="0" cy="{RL+52}" rx="17" ry="46" fill="url(#flameCore)"/>
  </g>
  <!-- Flossen hinten -->
  <path d="M-48,232 C-78,262 -96,300 -100,350 L-96,360 C-80,338 -64,330 -46,326 Z" fill="url(#fin)"/>
  <path d="M48,232 C78,262 96,300 100,350 L96,360 C80,338 64,330 46,326 Z" fill="url(#finR)"/>
  <!-- Düse -->
  <path d="M-30,326 L30,326 L40,356 L-40,356 Z" fill="url(#nozzle)"/>
  <ellipse cx="0" cy="356" rx="40" ry="6" fill="#ffd9a0" opacity="0.9"/>
  <!-- Rumpf -->
  <path d="M0,0 C34,24 58,86 58,150 L58,288 C58,306 54,318 48,330 L-48,330 C-54,318 -58,306 -58,288 L-58,150 C-58,86 -34,24 0,0 Z" fill="url(#body)"/>
  <path d="M0,0 C34,24 58,86 58,150 L58,288 C58,306 54,318 48,330 L-48,330 C-54,318 -58,306 -58,288 L-58,150 C-58,86 -34,24 0,0 Z" fill="url(#bodyV)"/>
  <!-- Spitze in Markenblau -->
  <path d="M0,0 C24,17 40,46 48,78 C30,72 -30,72 -48,78 C-40,46 -24,17 0,0 Z" fill="url(#nose)"/>
  <!-- Bauchband -->
  <path d="M-58,262 C-20,270 20,270 58,262 L58,278 C20,286 -20,286 -58,278 Z" fill="url(#band)"/>
  <!-- Fenster -->
  <circle cx="0" cy="165" r="31" fill="url(#ringG)"/>
  <circle cx="0" cy="165" r="24" fill="url(#window)"/>
  <ellipse cx="-8" cy="155" rx="10" ry="6" fill="#fff" opacity="0.75" transform="rotate(-30 -8 155)"/>
  <circle cx="9" cy="176" r="3" fill="#fff" opacity="0.35"/>
  <!-- Glanzstreifen -->
  <path d="M-30,96 C-34,140 -34,240 -32,320" stroke="#fff" stroke-width="7" stroke-linecap="round" opacity="0.85" filter="url(#b1)" fill="none"/>
</g>'''

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <radialGradient id="bg" cx="50%" cy="72%" r="75%">
    <stop offset="0" stop-color="#4a64ea"/><stop offset="0.55" stop-color="#2b45d4"/><stop offset="1" stop-color="#1d32a8"/>
  </radialGradient>
  <radialGradient id="lensFill" cx="45%" cy="30%" r="80%">
    <stop offset="0" stop-color="#6d86f2"/><stop offset="1" stop-color="#3550d8"/>
  </radialGradient>
  <radialGradient id="holeGlow" cx="50%" cy="50%" r="50%">
    <stop offset="0" stop-color="#fffdf5"/><stop offset="0.45" stop-color="#ffe7a8"/><stop offset="0.8" stop-color="#ffb35c"/><stop offset="1" stop-color="#ff8a3d"/>
  </radialGradient>
  <radialGradient id="burst" cx="50%" cy="50%" r="50%">
    <stop offset="0" stop-color="#fff6d8" stop-opacity="0.95"/><stop offset="0.35" stop-color="#ffd27a" stop-opacity="0.45"/><stop offset="1" stop-color="#ffb35c" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="puff" cx="45%" cy="40%" r="55%">
    <stop offset="0" stop-color="#ffffff"/><stop offset="0.6" stop-color="#eef1fb"/><stop offset="1" stop-color="#dfe5f8" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="glass" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#ffffff" stop-opacity="0.75"/><stop offset="0.5" stop-color="#b9c7ff" stop-opacity="0.35"/><stop offset="1" stop-color="#7f95f5" stop-opacity="0.55"/>
  </linearGradient>
  <linearGradient id="body" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#9aa8d6"/><stop offset="0.14" stop-color="#d9dff2"/><stop offset="0.36" stop-color="#ffffff"/>
    <stop offset="0.6" stop-color="#f3f5fc"/><stop offset="0.86" stop-color="#bcc6e6"/><stop offset="1" stop-color="#7e8cc4"/>
  </linearGradient>
  <linearGradient id="bodyV" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="0.85" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#ffcf8a" stop-opacity="0.55"/>
  </linearGradient>
  <linearGradient id="nose" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#1c2f9c"/><stop offset="0.35" stop-color="#4d68f0"/><stop offset="0.55" stop-color="#3653e0"/><stop offset="1" stop-color="#16257e"/>
  </linearGradient>
  <linearGradient id="band" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#1c2f9c"/><stop offset="0.35" stop-color="#4d68f0"/><stop offset="0.6" stop-color="#3653e0"/><stop offset="1" stop-color="#16257e"/>
  </linearGradient>
  <linearGradient id="fin" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#3a56e6"/><stop offset="1" stop-color="#14217a"/>
  </linearGradient>
  <linearGradient id="finR" x1="1" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#2a43c8"/><stop offset="1" stop-color="#0f1a60"/>
  </linearGradient>
  <linearGradient id="finC" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#2a43c8"/><stop offset="0.5" stop-color="#5a74f4"/><stop offset="1" stop-color="#1a2a90"/>
  </linearGradient>
  <linearGradient id="nozzle" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#3b4256"/><stop offset="0.4" stop-color="#9aa3b8"/><stop offset="1" stop-color="#2a3044"/>
  </linearGradient>
  <linearGradient id="ringG" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#ffffff"/><stop offset="0.5" stop-color="#b8c2e0"/><stop offset="1" stop-color="#7b88b8"/>
  </linearGradient>
  <radialGradient id="window" cx="35%" cy="30%" r="80%">
    <stop offset="0" stop-color="#7f9cff"/><stop offset="0.5" stop-color="#2440c8"/><stop offset="1" stop-color="#0b1450"/>
  </radialGradient>
  <linearGradient id="flameOuter" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fff4d6"/><stop offset="0.35" stop-color="#ffc56b"/><stop offset="0.75" stop-color="#ff8a3d" stop-opacity="0.6"/><stop offset="1" stop-color="#ff6a2a" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="flameCore" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#ffffff"/><stop offset="0.6" stop-color="#fff1c4"/><stop offset="1" stop-color="#ffd27a" stop-opacity="0"/>
  </linearGradient>
  <radialGradient id="rocketGlow" cx="50%" cy="50%" r="50%">
    <stop offset="0" stop-color="#ffffff" stop-opacity="0.35"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="fadeBottom" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#2b45d4" stop-opacity="0"/><stop offset="1" stop-color="#2b45d4" stop-opacity="0.9"/>
  </linearGradient>
  <filter id="b1" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2"/></filter>
  <filter id="b2" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3.5"/></filter>
  <filter id="b3" x="-80%" y="-50%" width="260%" height="200%"><feGaussianBlur stdDeviation="9"/></filter>
  <filter id="soft" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="14"/></filter>
  <filter id="smokeF" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="7"/></filter>
  <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="22"/></filter>
</defs>
<rect width="{W}" height="{H}" fill="url(#bg)"/>
<g>{"".join(stars)}</g>
<g>{"".join(ticks)}</g>
<clipPath id="lensClip"><circle cx="{CX}" cy="{LY}" r="{R}"/></clipPath>
<mask id="edgeMask"><rect width="{W}" height="{H}" fill="#fff"/><rect x="{CX-60}" y="0" width="120" height="{LY}" fill="#000"/></mask>
<mask id="glassMask"><circle cx="{CX}" cy="{LY}" r="{R}" fill="#fff"/><polygon points="{hole}" fill="#000"/></mask>
<!-- Schatten + Glow hinter Lupe und Rakete -->
<ellipse cx="{CX}" cy="{LY+26}" rx="{R}" ry="{R}" fill="#0a1460" opacity="0.45" filter="url(#shadow)"/>
<ellipse cx="{CX}" cy="{LY-250}" rx="190" ry="260" fill="url(#rocketGlow)"/>
<circle cx="{HX}" cy="{HY}" r="230" fill="url(#burst)" opacity="0.8"/>
<!-- Lupen-Innenraum -->
<g clip-path="url(#lensClip)">
  <circle cx="{CX}" cy="{LY}" r="{R}" fill="url(#lensFill)"/>
  <ellipse cx="{CX}" cy="{LY+90}" rx="170" ry="130" fill="url(#burst)"/>
  <ellipse cx="{CX}" cy="{LY+60}" rx="70" ry="90" fill="url(#burst)"/>
  <g filter="url(#smokeF)">{"".join(smoke)}</g>
</g>
<!-- Rakete -->
{rocket}
<!-- Glas vor dem unteren Teil der Rakete -->
<g mask="url(#glassMask)">
  <circle cx="{CX}" cy="{LY}" r="{R}" fill="#5f79ee" opacity="0.30"/>
  <ellipse cx="{CX-40}" cy="{LY-40}" rx="{R-40}" ry="70" fill="#fff" opacity="0.16" filter="url(#soft)" transform="rotate(-20 {CX-40} {LY-40})"/>
  <g>{"".join(cracks)}</g>
</g>
<polygon points="{hole}" fill="none" stroke="#fff" stroke-width="2.2" stroke-linejoin="round" opacity="0.95" clip-path="url(#lensClip)" mask="url(#edgeMask)"/>
<!-- Fassung -->
<path d="{rim_d}" fill="none" stroke="#fff" stroke-width="6" stroke-linecap="round"/>
<circle cx="{CX}" cy="{LY}" r="{R-8}" fill="none" stroke="#14227a" stroke-opacity="0.22" stroke-width="4" mask="url(#glassMask)"/>
<path d="{rim_d}" fill="none" stroke="#fff" stroke-width="14" stroke-opacity="0.18" filter="url(#b2)"/>
<path d="M{f(CX+R*math.cos(math.radians(150)))},{f(LY+R*math.sin(math.radians(150)))} A{R},{R} 0 0 1 {f(CX+R*math.cos(math.radians(212)))},{f(LY+R*math.sin(math.radians(212)))}" fill="none" stroke="#fff" stroke-width="3" opacity="0.9" filter="url(#b1)"/>
{"".join(rim_pieces)}
<g>{"".join(shards_back)}</g>
<g>{"".join(shards_front)}</g>
</svg>'''

tmp = tempfile.mkdtemp()
html = os.path.join(tmp, "hero.html")
with open(html, "w") as fh:
    fh.write(f'<!doctype html><html><head><style>html,body{{margin:0;background:#2b45d4}}</style></head><body>{svg}</body></html>')
open(OUT.rsplit(".", 1)[0] + ".svg", "w").write(svg)
chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
subprocess.run([chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                f"--window-size={W},{H}", f"--screenshot={os.path.abspath(OUT)}", f"file://{html}"],
               check=True, capture_output=True)
print("ok", OUT)
