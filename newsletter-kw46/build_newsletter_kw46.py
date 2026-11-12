"""Kunden-Newsletter KW 46/2026 (Themen aus #newsletter-topic):
  Hero      -> Petra kommt aufs Handy: Countdown + Warteliste (Tally Kp5x4K)
  Karte 2   -> Neuer Ratgeber + neue Anruf-Einstellungen (Video "Anrufe einrichten")
  Karte 3   -> Petra im Chat: kennt deinen Betrieb, TAIFUN, Chat Petra mit ChatGPT/Claude/Gemini
  FOTW      -> Erinnerung im Kalender je Terminvorlage
Versand über Resend."""

import base64, datetime, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

src = open(os.path.join(ROOT, "winback", "build_winback_newsletter.py")).read()
exec(src[:src.index("\nSIGN = ")].replace(
    'os.path.dirname(os.path.dirname(os.path.abspath(__file__)))', repr(ROOT)))

APP = "https://app.hallopetra.de/dashboard"
WAIT = "https://tally.so/r/Kp5x4K?email={{{EMAIL}}}&amp;vorname={{{FIRST_NAME}}}&amp;nachname={{{LAST_NAME}}}"  # Resend-Platzhalter, Tally-Hidden-Fields
RG = "https://www.hallopetra.de/ratgeber"

SIGN = (f'<p class="p" style="margin-top:18px;">Viele Grüße<br>'
        f'<strong style="color:#0f1a3c;">Jesko</strong></p>')

SHADOW = "box-shadow:0 1px 2px rgba(15,26,60,0.04),0 12px 32px rgba(15,26,60,0.06);"


def card(inner, bar=None, bg="#ffffff", shadow=SHADOW):
    """Karte mit Schatten und optionalem Farbbalken oben (Farbcode je Thema)."""
    top = (f'<tr><td height="6" style="height:6px;background:{bar};border-radius:22px 22px 0 0;font-size:0;line-height:0;" bgcolor="{bar}">&nbsp;</td></tr>'
           if bar else "")
    rad = "0 0 22px 22px" if bar else "22px"
    return f'''          <tr>
            <td class="mob-pad" style="background:#eef1fb;padding:0 16px 18px;" bgcolor="#eef1fb">
              <table role="presentation" class="card" width="100%" cellspacing="0" cellpadding="0" border="0" style="border-radius:22px;{shadow}" bgcolor="{bg}">
                {top}<tr>
                  <td class="px28" style="background:{bg};padding-top:30px;padding-bottom:32px;border-radius:{rad};" bgcolor="{bg}">
{inner}
                  </td>
                </tr>
              </table>
            </td>
          </tr>
'''


def head_row(num, eyebrow, ecol="#2b45d4"):
    return (f'<table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-bottom:14px;"><tr>'
            f'<td valign="bottom" style="{F}font-size:13px;font-weight:800;letter-spacing:1.8px;color:{ecol};white-space:nowrap;padding-right:12px;">{num + "&nbsp;&nbsp;" if num else ""}<span style="color:#8b96ad;font-weight:700;text-transform:uppercase;">{eyebrow}</span></td>'
            f'<td width="100%" valign="middle" style="border-bottom:1px solid #e3e7f0;font-size:0;line-height:0;">&nbsp;</td>'
            f'</tr></table>')


def note(label, text):
    return (f'<table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin:0 0 20px;"><tr>'
            f'<td style="border-top:1px solid #e3e7f0;border-bottom:1px solid #e3e7f0;padding:14px 0;">'
            f'<p style="{F}font-size:14px;line-height:21px;color:#47546c;margin:0;"><strong style="color:#0f1a3c;">{label}</strong> {text}</p></td></tr></table>')


def mark(t):
    return f'<span style="background:#FFE7A1;color:#0f1a3c;font-weight:700;padding:0 4px;border-radius:4px;">{t}</span>'


def stat(num, label, border=True):
    bl = "border-left:1px solid #e3e7f0;" if border else ""
    return (f'<td width="33%" align="left" valign="top" style="{bl}padding:2px 0 2px {"18px" if border else "0"};">'
            f'<p style="{F}font-size:30px;line-height:34px;font-weight:800;color:#0f1a3c;margin:0;letter-spacing:-0.5px;">{num}</p>'
            f'<p style="{F}font-size:12px;line-height:16px;color:#6c788f;margin:4px 0 0;text-transform:uppercase;letter-spacing:1.2px;">{label}</p></td>')


GAP = '<td width="2%" style="font-size:0;line-height:0;">&nbsp;</td>'

# 14-Tage-Leiste: schmale Segmente, heute grün
days = "".join(
    f'<td width="7%" style="height:4px;line-height:4px;font-size:0;background:{"#12b981" if i == 0 else "#5a6fe0"};" bgcolor="{"#12b981" if i == 0 else "#5a6fe0"}">&nbsp;</td>'
    + ('<td style="width:4px;font-size:0;line-height:0;">&nbsp;</td>' if i < 13 else "")
    for i in range(14))

countdown = f'''<table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin:6px 0 4px;">
                      <tr>
                        <td align="center" bgcolor="#2b45d4" style="font-size:0;line-height:0;">
                          <img src="{RAW}countdown-lupe.png" width="620" height="210" alt="Noch 10 Tage bis zur HalloPetra-App" style="width:100%;max-width:620px;height:auto;display:block;color:#ffffff;font-size:28px;font-weight:bold;background-color:#2b45d4;">
                        </td>
                      </tr>
                    </table>
                    <p style="{F}font-size:16px;line-height:24px;color:#ffffff;text-align:center;margin:0 0 4px;font-weight:700;">bis Petra auf deinem Handy ist</p>
                    <p style="{F}font-size:11px;line-height:18px;letter-spacing:1.6px;text-transform:uppercase;color:#c9d2fa;text-align:center;margin:0 0 26px;">iPhone &amp; Android</p>'''

white_button = (f'<table role="presentation" cellspacing="0" cellpadding="0" border="0" align="center" style="margin:0 auto;"><tr><td style="border-radius:12px;background:#ffffff;" bgcolor="#ffffff">'
                f'<a href="{WAIT}" style="display:inline-block;background:#ffffff;color:#2b45d4;{F}font-size:16px;line-height:18px;font-weight:800;'
                f'padding:16px 26px;border-radius:12px;text-decoration:none;">Auf die Warteliste &#8594;</a></td></tr></table>')

video = f'''<table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin:0 0 18px;">
                      <tr>
                        <td bgcolor="#e6ecfc" style="border-radius:16px;font-size:0;line-height:0;box-shadow:0 8px 22px rgba(43,69,212,0.18);">
                          <a href="{RG}/anrufe-einrichten" style="text-decoration:none;"><img src="{RAW}ratgeber-anrufe-thumb.jpg" width="620" height="349" alt="Film ansehen: Anrufe einrichten (1:29)" style="width:100%;max-width:620px;height:auto;display:block;border-radius:16px;color:#0f1a3c;font-size:16px;font-weight:bold;background-color:#e6ecfc;"></a>
                        </td>
                      </tr>
                    </table>'''

stats = (f'<table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin:4px 0 22px;"><tr>'
         f'{stat("53", "Anleitungen", False)}{stat("26", "Filme")}{stat("12", "Themen")}'
         f'</tr></table>')

chat = f'''<table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin:0 0 20px;border-radius:18px;" bgcolor="#f3f5fc">
                      <tr><td style="padding:20px 18px;background:#f3f5fc;border-radius:18px;" bgcolor="#f3f5fc">
                        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0"><tr><td align="right" style="padding:0 0 10px 50px;">
                          <table role="presentation" cellspacing="0" cellpadding="0" border="0"><tr><td style="background:#0f1a3c;border-radius:16px 16px 4px 16px;padding:10px 14px;{F}font-size:14px;line-height:20px;color:#ffffff;" bgcolor="#0f1a3c">Was haben wir Familie Weber zuletzt angeboten?</td></tr></table>
                        </td></tr></table>
                        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0"><tr>
                          <td width="34" valign="bottom" style="padding-right:8px;"><img src="{RAW}petra-face-nobg.png" width="28" height="28" alt="Petra" style="width:28px;height:28px;border-radius:50%;display:block;background:#d7def8;"></td>
                          <td style="padding-right:30px;">
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0"><tr><td style="background:#ffffff;box-shadow:0 2px 8px rgba(15,26,60,0.06);border-radius:16px 16px 16px 4px;padding:10px 14px;{F}font-size:14px;line-height:20px;color:#47546c;" bgcolor="#ffffff">Laut TAIFUN den Tausch der Gastherme, Angebot vom 3. November. Soll ich dir die Positionen zeigen?</td></tr></table>
                          </td>
                        </tr></table>
                      </td></tr>
                    </table>'''


def fotw(title, text, where, after):
    return f'''          <!-- ═══════════════ FEATURE OF THE WEEK ═══════════════ -->
          <tr>
            <td class="mob-pad" style="background:#eef1fb;padding:0 16px 16px;" bgcolor="#eef1fb">
              <table role="presentation" class="fotw" width="100%" cellspacing="0" cellpadding="0" border="0" style="border-radius:22px;box-shadow:0 12px 30px rgba(176,120,0,0.12);" bgcolor="#FFE7A1">
                <tr>
                  <td class="px28" style="background:#FFE7A1;padding-top:24px;padding-bottom:24px;border-radius:22px;" bgcolor="#FFE7A1">
                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0"><tr><td valign="top"><table role="presentation" cellspacing="0" cellpadding="0" border="0"><tr><td style="background:#0f1a3c;border-radius:20px;padding:5px 12px;{F}font-size:11px;font-weight:800;color:#FFD45C;letter-spacing:1.4px;text-transform:uppercase;" bgcolor="#0f1a3c">&#9733;&nbsp; Feature of the Week</td></tr></table></td><td align="right" valign="top" style="{F}font-size:40px;line-height:28px;color:#F2C94C;padding-left:10px;" class="hide-mob">&#9733;</td></tr></table>
                    <p class="h2" style="margin:14px 0 8px;">{title}</p>
                    <p class="p" style="margin-bottom:14px;">{text}</p>
                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="border-radius:12px;" bgcolor="#F7D774"><tr>
                      <td style="background:#F7D774;border-radius:12px;padding:12px 16px;{F}font-size:13px;line-height:20px;color:#5b4a12;" bgcolor="#F7D774"><strong style="color:#0f1a3c;">So geht's:</strong> {where} &middot; {after}</td>
                    </tr></table>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
'''


html = page(
    title="Petra kommt aufs Handy",
    preheader="In 10 Tagen startet die HalloPetra-App. Ein erster Blick auf das, was sie für dich tut.",
    pill="Bald &middot; Die HalloPetra-App",
    h1a="Petra kommt", h1b="aufs Handy",
    sub="Bald hast du Petra als App in der Hosentasche, auf der Baustelle genauso wie im Büro. Wer jetzt auf der Warteliste steht, ist als Erstes dabei.",
    img="petra-handy-hero.png", img_w=190, img_h=190, img_alt="Petra mit dem Handy am Ohr",
    cards=[])

cards = [
    card(f'''                    <p style="{F}font-size:13px;font-weight:800;letter-spacing:1.8px;text-transform:uppercase;color:#c9d2fa;margin:0 0 4px;text-align:center;">Countdown</p>
                    {countdown}
                    <p style="{F}font-size:15px;line-height:23px;color:#ffffff;margin:0 0 22px;text-align:center;">Trag dich jetzt auf die Warteliste ein, dann meldet sich unser Kollege Leonard persönlich bei dir. Wenn du magst, bestellst du die App dort gleich vor und hast sie zum Start sofort auf dem Handy.</p>
                    {white_button}
                    <p style="{F}font-size:13px;line-height:20px;color:#c9d2fa;margin:12px 0 0;text-align:center;">Ein Klick genügt, deine Daten sind schon eingetragen.</p>
                    <p style="{F}font-size:13px;line-height:20px;color:#c9d2fa;margin:18px 0 0;text-align:center;border-top:1px solid #4a61dc;padding-top:16px;"><strong style="color:#ffffff;">Gut zu wissen:</strong> Die App gehört zu Petra 2.0. Vorbestellen heißt also, dass du auf Petra 2.0 umsteigst. Das bespricht Leonard mit dir, oder du wechselst gleich selbst <a href="https://app.hallopetra.de/dashboard/account?tab=subscription&amp;pool=switch" style="color:#ffffff;font-weight:700;text-decoration:none;border-bottom:1px solid #ffffff;">in deinem Konto</a>.</p>''', bg="#2b45d4", shadow="box-shadow:0 18px 40px rgba(43,69,212,0.28);"),
]


def teaser(title, text, last=False):
    pad = "0" if last else "0 0 22px"
    return (f'<p style="{F}font-size:19px;line-height:25px;font-weight:800;color:#0f1a3c;margin:0 0 4px;text-align:center;">{title}</p>'
            f'<p style="{F}font-size:15px;line-height:23px;color:#6c788f;margin:{pad};text-align:center;">{text}</p>')


cards.append(card(f'''                    <p style="{F}font-size:12px;font-weight:800;letter-spacing:1.8px;text-transform:uppercase;color:#8b96ad;margin:0 0 10px;text-align:center;">Ein erster Blick</p>
                    <p class="h2" style="margin:0 0 18px;text-align:center;font-size:28px;line-height:34px;">Sag's einfach Petra.</p>
                    <p style="{F}font-size:16px;line-height:26px;color:#47546c;margin:0 0 14px;">Du sitzt im Auto, die Hände am Lenkrad, und dir fällt ein: Der Termin morgen früh muss auf Donnerstag. Mit der App sagst du es einfach Petra, so wie du es einer Kollegin im Büro sagen würdest.</p>
                    <p style="{F}font-size:16px;line-height:26px;color:#47546c;margin:0 0 26px;">Sie verschiebt den Termin, legt dir eine Aufgabe an oder bereitet eine Nachricht an den Kunden vor. Ohne Tippen, über die Freisprechanlage im Auto genauso wie auf der Baustelle.</p>
                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0"><tr><td style="border-top:1px solid #e3e7f0;padding-top:20px;">
                    <p style="{F}font-size:15px;line-height:22px;color:#0f1a3c;margin:0 0 6px;text-align:center;font-weight:700;">Und das ist erst der Anfang.</p>
                    <p style="{F}font-size:15px;line-height:22px;color:#6c788f;margin:0 0 10px;text-align:center;">Was die App noch alles kann, zeigen wir dir in den nächsten Tagen.</p>
                    <p style="{F}font-size:15px;line-height:22px;margin:0;text-align:center;"><a href="{WAIT}" style="color:#2b45d4;font-weight:800;text-decoration:none;">Jetzt auf die Warteliste&nbsp;&#8594;</a></p>
                    </td></tr></table>'''))

html = html.replace("          <!-- ═══════════════ FOOTER BAR ═══════════════ -->",
                    "".join(cards) + "          <!-- ═══════════════ FOOTER BAR ═══════════════ -->", 1)


def banner(bg, border, label, lcol, text, link, linktext, thumb=None):
    img = (f'<td width="112" valign="middle" style="padding-right:14px;" class="hide-mob"><a href="{link}"><img src="{RAW}{thumb}" width="112" height="63" alt="Film ansehen" style="width:112px;height:63px;display:block;border-radius:8px;"></a></td>'
           if thumb else "")
    return f'''          <tr>
            <td class="mob-pad" style="background:#eef1fb;padding:0 16px 12px;" bgcolor="#eef1fb">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="border-radius:16px;" bgcolor="{bg}">
                <tr>
                  <td style="background:{bg};padding:14px 18px;border-radius:16px;border:1px solid {border};" bgcolor="{bg}">
                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0"><tr>{img}
                      <td valign="middle"><p style="{F}font-size:11px;font-weight:800;letter-spacing:1.4px;text-transform:uppercase;color:{lcol};margin:0 0 4px;">{label}</p>
                      <p style="{F}font-size:14px;line-height:21px;color:#47546c;margin:0;">{text} <a href="{link}" style="color:#0f1a3c;font-weight:700;text-decoration:none;border-bottom:1px solid #0f1a3c;">{linktext}</a>&nbsp;&#8594;</p></td>
                    </tr></table>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
'''


html = html.replace("          <!-- ═══════════════ FOOTER BAR ═══════════════ -->",
                    ""
                    + banner("#f7f8fd", "#dfe4f2", "Neu &middot; Ratgeber", "#2b45d4",
                             "<strong style=\"color:#0f1a3c;\">Zu jeder Funktion eine Anleitung,</strong> meist mit kurzem Film. Zum Einstieg: die neuen Anruf-Einstellungen in 90 Sekunden.",
                             f"{RG}/anrufe-einrichten", "Film ansehen", thumb="ratgeber-anrufe-thumb.jpg")
                    + "          <!-- ═══════════════ FOOTER BAR ═══════════════ -->", 1)

html = html.replace("          <!-- ═══════════════ FOOTER BAR ═══════════════ -->",
                    f'''          <tr><td class="mob-pad px28" style="background:#eef1fb;padding:4px 46px 18px;" bgcolor="#eef1fb">{SIGN}</td></tr>
''' + "          <!-- ═══════════════ FOOTER BAR ═══════════════ -->", 1)
html = html.replace("<strong>Lieber erst schreiben?</strong> Antworte einfach auf diese Mail, ich lese jede Antwort persönlich.",
                    "<strong>Fragen?</strong> Antworte einfach auf diese Mail, wir lesen jede Antwort persönlich.")
html = html.replace("&#128172;&nbsp; <strong>Fragen?</strong>", "<strong>Fragen?</strong>")
html = html.replace("weil du Kunde bei HalloPetra warst.", "weil du Kunde bei HalloPetra bist.")
html = html.replace("[[UNSUB_LINK_DE_DE]]", "{{{RESEND_UNSUBSCRIBE_URL}}}")
html = re.sub(r'\s*<table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" bgcolor="#eef1fb">\s*<tr>\s*<td align="center" style="padding:12px 18px 0;.*?</table>',
              "", html, count=1, flags=re.S)
assert "[[" not in html, "Mailjet-Platzhalter übrig"
body = html.split("<body")[1]
assert "—" not in body and "–" not in body, "Gedankenstrich"


def emb(m):
    fn = os.path.join(ROOT, m.group(1))
    mt = "image/jpeg" if fn.endswith(".jpg") else "image/png"
    return f'src="data:{mt};base64,' + base64.b64encode(open(fn, "rb").read()).decode() + '"'


open(os.path.join(ROOT, "newsletter-kw46-resend.html"), "w").write(html)
open(os.path.join(ROOT, "newsletter-kw46-preview-local.html"), "w").write(
    re.sub(r'src="https://raw.githubusercontent.com/jesko-maker/hallopetra-referral/main/([^"]+)"', emb, html))
print("ok kw46")
