"""Kunden-Newsletter App-Recap (nach dem Launch 19.11.2026): Zahlen + echte App-Store-Stimme, Store-Links.
Zahlen aus #sales-notifications 12.-23.11.: 216 Umstiege + 19 Neukäufe Petra 2.0, 52 davon Quelle „Mobile App“.
Bewertung: App Store, Kuhlmann GmbH, 17.11.2026, 5 Sterne (wörtlich). Versand über Resend."""

import base64, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

_src = open(os.path.join(HERE, "build_newsletter_launch.py")).read()
__file__ = os.path.join(HERE, "build_newsletter_launch.py")
exec(_src[:_src.index('\nIOS = ')])
_store = _src[_src.index("def store_btn("):_src.index("\nrocket = ")]
exec(_store)
_feat = _src[_src.index("def feat("):_src.index("\ndef shot(")]
exec(_feat)

IOS = "https://apps.apple.com/de/app/hallopetra/id6829791182"
IOS_REVIEW = IOS + "?action=write-review"
AND = "https://play.google.com/store/apps/details?id=de.hallopetra.app"
SWITCH = "https://app.hallopetra.de/dashboard/account?tab=subscription&amp;pool=switch"

html = page(
    title="Die HalloPetra-App kommt an",
    preheader="Über 200 Betriebe sind schon auf Petra 2.0, und die ersten Bewertungen sind da.",
    pill="Eine Woche App &middot; HalloPetra",
    h1a="Die App", h1b="kommt an.",
    sub="Vor ein paar Tagen ist die HalloPetra-App gestartet. Seitdem ist eine Menge passiert. Hier ist ein kurzer Blick auf die ersten Tage.",
    img="recap-hero-klein.jpg", img_w=230, img_h=202, img_alt="Petra hält die HalloPetra-App in die Kamera",
    cards=[])

html = html.replace("#e6ecfc", "#d3defe").replace("background:#d5ddfb;", "background:#ffffff;")
BANNER = f'''          <tr>
            <td style="background:#d3defe;padding:0;font-size:0;line-height:0;" bgcolor="#d3defe">
              <img src="{RAW}recap-banner.jpg" width="680" height="453" alt="Petra hält die HalloPetra-App in die Kamera: der Eingang mit Anrufen, Mails und Chats" style="width:100%;max-width:680px;height:auto;display:block;color:#0f1a3c;font-size:18px;font-weight:bold;background-color:#d3defe;">
            </td>
          </tr>
'''
_sp = '          <tr><td style="background:#eef1fb;height:16px;line-height:16px;font-size:0;" bgcolor="#eef1fb">&nbsp;</td></tr>'
assert _sp in html

visual = f'''<table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin:0 0 24px;">
                      <tr>
                        <td align="center" bgcolor="#1d2f8a" style="border-radius:18px;font-size:0;line-height:0;">
                          <img src="{RAW}recap-petra-stimmen.jpg" width="620" height="410" alt="Petra staunt über die App. Dahinter: eine Bewertung aus dem App Store, 4,3 Sterne, 50+ Betriebe direkt in der App gewechselt, 200+ Betriebe auf Petra 2.0" style="width:100%;max-width:620px;height:auto;display:block;border-radius:18px;color:#ffffff;font-size:22px;font-weight:bold;background-color:#1d2f8a;">
                        </td>
                      </tr>
                    </table>'''

stats = (f'<table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin:0 0 24px;"><tr>'
         f'{stat("200+", "Betriebe auf Petra 2.0", False)}{stat("50+", "direkt in der App gewechselt")}{stat("4,3&nbsp;&#9733;", "im App Store")}'
         f'</tr></table>')

quote = f'''<table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin:0;border-radius:18px;" bgcolor="#f3f5fc">
                      <tr><td style="padding:22px 22px 20px;background:#f3f5fc;border-radius:18px;" bgcolor="#f3f5fc">
                        <p style="{F}font-size:18px;line-height:22px;color:#FFB500;margin:0 0 10px;letter-spacing:2px;">&#9733;&#9733;&#9733;&#9733;&#9733;</p>
                        <p style="{F}font-size:17px;line-height:26px;color:#0f1a3c;margin:0 0 12px;font-weight:700;">&#8222;Potenzial ohne Ende. Wirklich eine perfekte Ergänzung zur ohnehin genialen Petra. Besonders muss ich das Team loben, welches schnell reagiert und verbessert, in einem super Tempo. Das hat richtig Potenzial und hat unseren Alltag verbessert.&#8220;</p>
                        <p style="{F}font-size:13px;line-height:18px;color:#6c788f;margin:0;">Kuhlmann GmbH &middot; Bewertung im App Store</p>
                      </td></tr>
                    </table>'''

cards = [
    card(f'''                    <p style="{F}font-size:12px;font-weight:800;letter-spacing:1.8px;text-transform:uppercase;color:#8b96ad;margin:0 0 10px;text-align:center;">Die ersten Tage</p>
                    <p class="h2" style="margin:0 0 20px;text-align:center;font-size:28px;line-height:34px;">Da ist richtig was los.</p>
                    {visual}
                    <p class="p" style="margin:0;">Seit dem Start sind über 200 Betriebe auf Petra 2.0 umgestiegen, über 50 davon direkt in der App. Und im App Store sind die ersten Bewertungen eingegangen.</p>
'''),
    card(f'''                    <p style="{F}font-size:13px;font-weight:800;letter-spacing:1.8px;text-transform:uppercase;color:#c9d2fa;margin:0 0 10px;text-align:center;">Noch nicht dabei?</p>
                    <p class="h2" style="margin:0 0 10px;text-align:center;color:#ffffff;font-size:28px;line-height:34px;">Hol dir Petra aufs Handy.</p>
                    <p style="{F}font-size:15px;line-height:23px;color:#ffffff;margin:0 0 22px;text-align:center;">Lade dir die App aus dem Store und melde dich mit deiner HalloPetra-E-Mail an. Du bekommst einen Code per Mail, und schon ist Petra auf deinem Handy.</p>
                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0"><tr>
                      {store_btn(IOS, "Laden im", "App Store", "icon-apple.png")}{store_btn(AND, "Jetzt bei", "Google Play", "icon-googleplay.png")}
                    </tr></table>
                    <p style="{F}font-size:13px;line-height:20px;color:#c9d2fa;margin:12px 0 0;text-align:center;border-top:1px solid #222a4f;padding-top:16px;"><strong style="color:#ffffff;">Gut zu wissen:</strong> Die App gehört zu Petra 2.0. Du bist noch nicht umgestiegen? Dann wechselst du <a href="{SWITCH}" style="color:#ffffff;font-weight:700;text-decoration:none;border-bottom:1px solid #ffffff;">in deinem Konto</a>, oder du antwortest auf diese Mail und Leonard meldet sich bei dir.</p>''', bg="#05081a", shadow="box-shadow:0 18px 40px rgba(5,8,26,0.35);"),
    card(f'''                    <p style="{F}font-size:12px;font-weight:800;letter-spacing:1.8px;text-transform:uppercase;color:#8b96ad;margin:0 0 10px;text-align:center;">Du nutzt die App schon?</p>
                    <p class="h2" style="margin:0 0 10px;text-align:center;font-size:24px;line-height:30px;">Dann sag uns, wie sie dir gefällt.</p>
                    <p style="{F}font-size:15px;line-height:23px;color:#6c788f;margin:0 0 10px;text-align:center;">Eine kurze Bewertung im Store hilft anderen Betrieben bei der Entscheidung. Und wenn dir etwas fehlt, antworte einfach auf diese Mail. Wir lesen jede Antwort.</p>
                    <p style="{F}font-size:15px;line-height:22px;margin:0;text-align:center;"><a href="{IOS_REVIEW}" style="color:#2b45d4;font-weight:800;text-decoration:none;">Im App Store bewerten</a>&nbsp;&nbsp;&middot;&nbsp;&nbsp;<a href="{AND}" style="color:#2b45d4;font-weight:800;text-decoration:none;">Bei Google Play bewerten</a></p>'''),
]

html = html.replace("          <!-- ═══════════════ FOOTER BAR ═══════════════ -->",
                    "".join(cards) + f'''          <tr><td class="mob-pad px28" style="background:#eef1fb;padding:4px 46px 18px;" bgcolor="#eef1fb">{SIGN}</td></tr>
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


open(os.path.join(ROOT, "newsletter-recap-resend.html"), "w").write(html)
open(os.path.join(ROOT, "newsletter-recap-preview-local.html"), "w").write(
    re.sub(r'src="https://raw.githubusercontent.com/jesko-maker/hallopetra-referral/main/([^"]+)"', emb, html))
print("ok recap")
