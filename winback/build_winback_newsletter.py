"""Baut die beiden Winback-Newsletter (Okt. 2026) im hellen Design-System:
  anrufer    -> Kündigung, weil Anrufer nicht mit Petra sprechen wollten (Petra Live: still dabei)
  heizsaison -> Kündigung wegen kein Bedarf / zu wenig Anrufe, nur SHK-Betriebe
Erzeugt je eine Mailjet-Datei (GitHub-Bild-URLs) und eine Vorschau mit eingebetteten Bildern."""
import base64, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = "https://raw.githubusercontent.com/jesko-maker/hallopetra-referral/main/"
F = "font-family:Arial,Helvetica,sans-serif;"
CAL = "https://calendly.com/jesko-hallopetra/30-minute-meeting"

head = open(os.path.join(ROOT, "newsletter-wartung-mailjet.html")).read()
head = head[:head.index("<body")]


def chip(icon, top, bottom, bg, border, col):
    return (f'<td class="chip" width="30%" align="center" valign="middle" style="background:{bg};border:1px solid {border};'
            f'border-radius:12px;padding:12px 8px;{F}font-size:13px;line-height:18px;color:#47546c;" bgcolor="{bg}">'
            f'<span style="font-size:20px;line-height:24px;">{icon}</span><br><strong style="color:{col};">{top}</strong><br>{bottom}</td>')


ARROW = f'<td width="5%" align="center" valign="middle" style="{F}font-size:18px;color:#8b96ad;">&#8594;</td>'


def check(bold, rest):
    return (f'<tr><td width="28" valign="top" style="padding:2px 10px 12px 0;{F}font-size:16px;line-height:22px;color:#12b981;font-weight:800;">&#10003;</td>'
            f'<td valign="top" style="padding:0 0 12px;"><p class="p"><strong style="color:#0f1a3c;">{bold}</strong> {rest}</p></td></tr>')


def box(text, color="blue"):
    bg, edge = ("#eef2fd", "#2b45d4") if color == "blue" else ("#eafaf1", "#12b981")
    return (f'<table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="border-radius:12px;margin-bottom:20px;" bgcolor="{bg}">'
            f'<tr><td style="padding:14px 16px;border-radius:12px;border-left:3px solid {edge};background:{bg};" bgcolor="{bg}">'
            f'<p style="{F}font-size:14px;line-height:21px;color:#47546c;margin:0;">{text}</p></td></tr></table>')


def button(label, href=CAL):
    return (f'<table role="presentation" cellspacing="0" cellpadding="0" border="0"><tr><td style="border-radius:12px;background:#2b45d4;" bgcolor="#2b45d4">'
            f'<a href="{href}" class="button" style="display:inline-block;background:#2b45d4;color:#ffffff;{F}font-size:15px;line-height:18px;font-weight:800;'
            f'padding:15px 24px;border-radius:12px;text-decoration:none;">{label}</a></td></tr></table>')


def card(inner):
    return f'''          <tr>
            <td class="mob-pad" style="background:#eef1fb;padding:0 16px 16px;" bgcolor="#eef1fb">
              <table role="presentation" class="card" width="100%" cellspacing="0" cellpadding="0" border="0" style="border-radius:22px;" bgcolor="#ffffff">
                <tr>
                  <td class="px28" style="background:#ffffff;padding-top:26px;padding-bottom:26px;border-radius:22px;" bgcolor="#ffffff">
{inner}
                  </td>
                </tr>
              </table>
            </td>
          </tr>
'''


def page(title, preheader, pill, h1a, h1b, sub, img, img_w, img_h, img_alt, cards):
    return head.replace(re.search(r"<title>.*?</title>", head).group(0), f"<title>{title}</title>") + f'''<body style="margin:0;padding:0;background:#eef1fb;" bgcolor="#eef1fb">
  <div class="preheader">{preheader}&nbsp;&#847;&nbsp;&#847;&nbsp;&#847;&nbsp;&#847;&nbsp;&#847;&nbsp;&#847;&nbsp;&#847;&nbsp;&#847;</div>

  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" bgcolor="#eef1fb">
    <tr>
      <td align="center" style="padding:12px 18px 0;{F}font-size:12px;color:#8b96ad;">
        Diese E-Mail im Browser nicht korrekt dargestellt?&nbsp;<a href="[[PERMALINK]]" style="color:#2b45d4;text-decoration:underline;">Hier öffnen.</a>
      </td>
    </tr>
  </table>

  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" bgcolor="#eef1fb">
    <tr>
      <td align="center" class="mob-pad" style="padding:26px 16px;">
        <table role="presentation" class="container" cellspacing="0" cellpadding="0" border="0" width="680" style="max-width:680px;background:#eef1fb;border-radius:28px;" bgcolor="#eef1fb">

          <!-- ═══════════════ HERO ═══════════════ -->
          <tr>
            <td class="hero-bg" style="background:#e6ecfc;border-radius:28px 28px 0 0;padding:26px 0 0 30px;" bgcolor="#e6ecfc">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                <tr>
                  <td class="stack hero-text" valign="top" style="padding:0 10px 28px 0;">
                    <table role="presentation" cellspacing="0" cellpadding="0" border="0">
                      <tr>
                        <td valign="middle" style="padding-right:10px;"><img src="{RAW}petra-face-nobg.png" width="36" height="36" alt="HalloPetra" style="width:36px;height:36px;border-radius:50%;display:block;background:#d7def8;"></td>
                        <td valign="middle" style="{F}font-size:19px;font-weight:800;color:#0f1a3c;">HalloPetra</td>
                      </tr>
                    </table>
                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="margin-top:18px;margin-bottom:14px;">
                      <tr>
                        <td style="background:#eafaf1;border:1px solid #bfe8d3;border-radius:22px;padding:5px 13px;{F}font-size:11px;font-weight:800;color:#0f9d63;letter-spacing:1.4px;text-transform:uppercase;" bgcolor="#eafaf1">{pill}</td>
                      </tr>
                    </table>
                    <p class="h1" style="{F}font-size:34px;line-height:41px;font-weight:800;color:#0f1a3c;margin:0 0 12px;">{h1a}<br><span style="display:inline-block;background:#d5ddfb;color:#26357e;border-radius:12px;padding:1px 12px;">{h1b}</span></p>
                    <p style="{F}font-size:15px;line-height:23px;color:#47546c;margin:0;">{sub}</p>
                  </td>
                  <td class="hero-img hide-mob" valign="bottom" align="right" width="{img_w}" style="width:{img_w}px;padding:0 20px 0 0;font-size:0;line-height:0;">
                    <img src="{RAW}{img}" width="{img_w}" height="{img_h}" alt="{img_alt}" style="width:{img_w}px;max-width:100%;height:auto;display:block;margin-left:auto;">
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <tr><td style="background:#eef1fb;height:16px;line-height:16px;font-size:0;" bgcolor="#eef1fb">&nbsp;</td></tr>

{"".join(card(c) for c in cards)}
          <!-- ═══════════════ FOOTER BAR ═══════════════ -->
          <tr>
            <td class="mob-pad" style="background:#eef1fb;padding:0 16px 18px;" bgcolor="#eef1fb">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="border-radius:16px;" bgcolor="#0f1a3c">
                <tr>
                  <td align="center" style="padding:20px 22px;{F}font-size:16px;line-height:23px;color:#ffffff;border-radius:16px;background:#0f1a3c;" bgcolor="#0f1a3c">
                    &#128172;&nbsp; <strong>Lieber erst schreiben?</strong> Antworte einfach auf diese Mail, ich lese jede Antwort persönlich.
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- ═══════════════ LEGAL ═══════════════ -->
          <tr>
            <td align="center" style="background:#eef1fb;padding:6px 20px 28px;{F}font-size:12px;line-height:20px;color:#8b96ad;border-radius:0 0 28px 28px;" bgcolor="#eef1fb">
              <p style="margin:0 0 8px;{F}font-size:13px;font-weight:700;color:#6c788f;">HalloPetra</p>
              <p style="margin:0 0 10px;">
                <a href="https://www.instagram.com/hallopetra.de/" style="color:#8b96ad;text-decoration:underline;">Instagram</a>&nbsp; &middot; &nbsp;<a href="https://www.linkedin.com/company/hallopetra/" style="color:#8b96ad;text-decoration:underline;">LinkedIn</a>
              </p>
              <p style="margin:0 0 10px;color:#8b96ad;">HalloPetra &middot; Monbijouplatz 2, 10178 Berlin, Deutschland</p>
              <p style="margin:0;">Diese E-Mail wurde an dich gesendet, weil du Kunde bei HalloPetra warst.<br>
              <a href="[[UNSUB_LINK_DE_DE]]" style="color:#8b96ad;text-decoration:underline;">Abmelden</a></p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
'''


SIGN = (f'<p class="p" style="margin-top:18px;">Viele Grüße<br><strong style="color:#0f1a3c;">Jesko</strong><br>'
        f'<span style="font-size:13px;color:#6c788f;">Mitgründer, HalloPetra</span></p>')

# ─────────────── 1: Anrufer haben aufgelegt ───────────────
anrufer = page(
    title="Deine Kunden sprechen wieder mit dir. Petra schreibt mit.",
    preheader="Petra muss nicht mehr ans Telefon. Sie hört still mit und erledigt den Papierkram.",
    pill="Neu &middot; Petra hört nur zu",
    h1a="Du telefonierst,", h1b="Petra schreibt mit",
    sub="Du hattest Petra gekündigt, weil deine Anrufer lieber mit einem Menschen sprechen wollten. Das haben wir von mehreren Betrieben gehört und Petra deshalb etwas Neues beigebracht.",
    img="petra-headset-hero.png", img_w=190, img_h=173, img_alt="Petra mit Headset am Laptop",
    cards=[
        f'''                    <p class="eyebrow" style="color:#2b45d4;">Das ist neu</p>
                    <p class="h2">Petra ist still im Gespräch dabei</p>
                    <p class="p" style="margin-bottom:16px;">Deine Kunden sprechen wie gewohnt mit dir oder deinem Team. Petra hört im Hintergrund mit, schreibt das Gespräch mit und gibt das Anliegen danach an die richtige Person weiter. Den Papierkram nach dem Anruf sparst du dir.</p>
                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin:0 0 18px;">
                      <tr>
                        {chip("&#128222;", "Kunde ruft an", "deine bekannte Nummer", "#f5f7fd", "#e3e7f0", "#0f1a3c")}
                        {ARROW}
                        {chip("&#128587;", "Du nimmst ab", "ganz normal", "#eef2fd", "#d5ddfb", "#2b45d4")}
                        {ARROW}
                        {chip("&#128221;", "Petra schreibt mit", "und gibt's weiter", "#eafaf1", "#bfe8d3", "#0f9d63")}
                      </tr>
                    </table>
                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                      {check("Kein Anrufer spricht mit einer KI.", "Der Mensch bleibt am Telefon, so wie es deine Kunden wollen.")}
                      {check("Jedes Gespräch sauber notiert.", "Im Dashboard und per E-Mail, ohne Mitschreiben nebenbei.")}
                      {check("Das Anliegen landet bei der richtigen Person.", "Petra gibt es weiter, du musst niemandem mehr Zettel hinlegen.")}
                    </table>
                    <p style="{F}font-size:13px;line-height:20px;color:#6c788f;margin:6px 0 0;">Dafür brauchst du zwei Nummern: die bekannte Kundennummer und eine interne. Das richten wir gemeinsam ein.</p>''',
        f'''                    <p class="eyebrow" style="color:#0f9d63;">Schnell wieder dabei</p>
                    <p class="h2">Dein alter Account ist vermutlich noch da</p>
                    <p class="p" style="margin-bottom:20px;">Deine Einstellungen sind wahrscheinlich noch hinterlegt. In einem kurzen Termin schauen wir gemeinsam drauf, stellen auf das stille Mithören um und du kannst direkt loslegen.</p>
                    {button("Kurzen Termin buchen &#8594;")}
                    {SIGN}''',
    ])

# ─────────────── 2: Heizsaison (SHK, kein Bedarf) ───────────────
heizsaison = page(
    title="Die Heizsaison geht los. Sollen wir wieder ran?",
    preheader="Bei allen SHK-Betrieben klingelt es gerade öfter. Dein alter Account ist vermutlich noch da.",
    pill="Heizsaison 2026",
    h1a="Bei dir klingelt's", h1b="bald wieder öfter",
    sub="Die Heizsaison geht los, und in jedem SHK-Betrieb, den wir betreuen, läuft gerade die Bude ein. Deshalb melden wir uns proaktiv: Können wir dich in dieser stressigen Zeit wieder unterstützen?",
    img="petra-daumen-hero.png", img_w=170, img_h=205, img_alt="Petra am Telefon mit Daumen hoch",
    cards=[
        f'''                    <p class="eyebrow" style="color:#2b45d4;">Warum gerade jetzt</p>
                    <p class="h2">Im Winter sieht die Lage anders aus</p>
                    <p class="p" style="margin-bottom:16px;">Als du gekündigt hast, war zu wenig los, als dass sich Petra gelohnt hätte. Jetzt kommen die Störungsmeldungen, die Wartungen und die Notfälle am Abend. Genau dann nimmt Petra die Anrufe an, während du auf der Baustelle bist.</p>
                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                      {check("Heizung ausgefallen?", "Petra nimmt die Störung auf, fragt die wichtigen Infos ab und gibt sie sofort an dich weiter.")}
                      {check("Notdienst am Abend und Wochenende.", "Petra stellt echte Notfälle zu deinem Bereitschaftsdienst durch.")}
                      {check("Kein Anruf geht verloren,", "auch wenn alle Leitungen belegt sind.")}
                    </table>''',
        f'''                    <p class="eyebrow" style="color:#0f9d63;">Schnell wieder dabei</p>
                    <p class="h2">Dein alter Account ist vermutlich noch da</p>
                    <p class="p" style="margin-bottom:16px;">Deine Einstellungen sind wahrscheinlich noch hinterlegt. Damit kannst du ganz unkompliziert wieder einsteigen und musst Petra nicht neu einrichten.</p>
                    {box('<strong style="color:#0f1a3c;">Auch nur für den Winter.</strong> Es gibt keinen Jahresvertrag, Petra ist monatlich kündbar. Du kannst sie also genau für die Heizsaison wieder dazuholen.', "green")}
                    {button("Wieder einsteigen: Termin buchen &#8594;")}
                    {SIGN}''',
    ])


def emb(m):
    fn = os.path.join(ROOT, m.group(1))
    mt = "image/jpeg" if fn.endswith(".jpg") else "image/png"
    return f'src="data:{mt};base64,' + base64.b64encode(open(fn, "rb").read()).decode() + '"'


for name, html in [("anrufer", anrufer), ("heizsaison", heizsaison)]:
    assert "—" not in html and "–" not in html.split("<body")[1], name
    open(os.path.join(ROOT, f"newsletter-winback-{name}-mailjet.html"), "w").write(html)
    open(os.path.join(ROOT, f"newsletter-winback-{name}-preview-local.html"), "w").write(
        re.sub(r'src="https://raw.githubusercontent.com/jesko-maker/hallopetra-referral/main/([^"]+)"', emb, html))
    print("ok", name)
