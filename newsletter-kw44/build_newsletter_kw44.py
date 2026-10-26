"""Kunden-Newsletter KW 44/2026 (Themen aus #newsletter-topic):
  Hero      -> Einfacher Modus: alle Anruf-Einstellungen auf einer Seite
  Karte 2   -> Konnektoren: Petra arbeitet im Chat mit deinen Werkzeugen
  Karte 3   -> Apple Kalender (Beta)
  FOTW      -> Persönliche Ansage vor Petra
Versand über Resend: erzeugt die Resend-Datei (GitHub-Bild-URLs, Resend-Abmeldelink)
und eine Vorschau mit eingebetteten Bildern."""

import base64, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# Helfer (chip, check, box, button, card, page) aus dem Winback-Generator übernehmen
src = open(os.path.join(ROOT, "winback", "build_winback_newsletter.py")).read()
exec(src[:src.index("\nSIGN = ")].replace(
    'os.path.dirname(os.path.dirname(os.path.abspath(__file__)))', repr(ROOT)))

APP = "https://app.hallopetra.de/dashboard"

SIGN = (f'<p class="p" style="margin-top:18px;">Viele Grüße<br>'
        f'<strong style="color:#0f1a3c;">Jesko &amp; Hendric</strong><br>'
        f'<span style="font-size:13px;color:#6c788f;">HalloPetra</span></p>')


def fotw(title, text, where, after):
    return f'''          <!-- ═══════════════ FEATURE OF THE WEEK ═══════════════ -->
          <tr>
            <td class="mob-pad" style="background:#eef1fb;padding:0 16px 16px;" bgcolor="#eef1fb">
              <table role="presentation" class="fotw" width="100%" cellspacing="0" cellpadding="0" border="0" style="border-radius:22px;" bgcolor="#FFE7A1">
                <tr>
                  <td class="px28" style="background:#FFE7A1;padding-top:24px;padding-bottom:24px;border-radius:22px;" bgcolor="#FFE7A1">
                    <table role="presentation" cellspacing="0" cellpadding="0" border="0"><tr><td style="background:#0f1a3c;border-radius:20px;padding:5px 12px;{F}font-size:11px;font-weight:800;color:#FFD45C;letter-spacing:1.4px;text-transform:uppercase;" bgcolor="#0f1a3c">&#9733;&nbsp; Feature of the Week</td></tr></table>
                    <p class="h2" style="margin:12px 0 8px;">{title}</p>
                    <p class="p" style="margin-bottom:14px;">{text}</p>
                    <table role="presentation" cellspacing="0" cellpadding="0" border="0"><tr>
                      <td valign="middle" style="padding-right:10px;{F}font-size:18px;line-height:20px;">&#127897;&#65039;</td>
                      <td valign="middle" style="{F}font-size:13px;line-height:20px;color:#47546c;"><strong style="color:#0f1a3c;">{where}</strong> &middot; {after}</td>
                    </tr></table>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
'''


html = page(
    title="Petras Anruf-Einstellungen passen jetzt auf eine Seite",
    preheader="Der einfache Modus, Petra mit deinen Werkzeugen und Apple Kalender. Plus: Feature of the Week.",
    pill="Neu &middot; Einfacher Modus",
    h1a="Alle Anruf-Einstellungen", h1b="auf einer Seite",
    sub="Wer wird durchgestellt, wann gibt es Termine, was passiert im Notdienst? Das stellst du jetzt an einem Ort ein, Schritt für Schritt mit dem Einrichtungs-Assistenten.",
    img="petra-multitask-hero.png", img_w=190, img_h=190, img_alt="Petra mit Telefon, Laptop und Zollstock",
    cards=[
        f'''                    <p class="eyebrow" style="color:#2b45d4;">Einfacher Modus</p>
                    <p class="h2">Petra einrichten, ohne Abläufe zu bauen</p>
                    <p class="p" style="margin-bottom:16px;">Bisher hast du Petras Verhalten über einzelne Abläufe eingestellt. Im einfachen Modus beantwortest du ein paar Fragen, und alles Wichtige steht danach übersichtlich auf einer Seite. Einschalten kannst du ihn als Admin selbst, am Ende des Assistenten.</p>
                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin:0 0 18px;">
                      <tr>
                        {chip("&#128172;", "Assistent starten", "Frage für Frage", "#f5f7fd", "#e3e7f0", "#0f1a3c")}
                        {ARROW}
                        {chip("&#128203;", "Eine Seite", "alles auf einen Blick", "#eef2fd", "#d5ddfb", "#2b45d4")}
                        {ARROW}
                        {chip("&#9989;", "Petra legt los", "mit deinen Regeln", "#eafaf1", "#bfe8d3", "#0f9d63")}
                      </tr>
                    </table>
                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                      {check("Durchstellen, Termine, Rückruf, Notdienst.", "Jeder Bereich ist eine Zeile, die du an- und ausschaltest.")}
                      {check("Bei unklarem Anliegen.", "Passt kein Ablauf, nimmt Petra Name, Nummer und Anliegen auf und sagt einen Rückruf zu.")}
                      {check("Mitarbeiter direkt anlegen.", "Fehlt jemand in der Auswahl, legst du ihn gleich dort an.")}
                    </table>
                    <p style="margin:6px 0 0;"></p>
                    {button("Zum Einrichtungs-Assistenten &#8594;", APP + "/flows/einrichten")}''',
        f'''                    <p class="eyebrow" style="color:#0f9d63;">Neu im Petra-Chat</p>
                    <p class="h2">Petra arbeitet mit deinen Werkzeugen</p>
                    <p class="p" style="margin-bottom:16px;">Über Konnektoren verbindest du Petra mit Programmen, die du sowieso nutzt. Petra greift dann direkt im Chat darauf zu, für dein ganzes Team oder nur für dich.</p>
                    {box("<strong style='color:#0f1a3c;'>Zur Auswahl stehen 15 Werkzeuge,</strong> zum Beispiel Zapier, Make, n8n, Calendly, Pipedrive, Notion und Stripe. Wer einen eigenen MCP-Server hat, bindet auch den an.", "green")}
                    <p style="{F}font-size:13px;line-height:20px;color:#6c788f;margin:0;"><strong style="color:#47546c;">So geht's:</strong> <a href="{APP}/settings/integrations/konnektoren" style="color:#2b45d4;text-decoration:underline;">Einstellungen &#8594; Integrationen &#8594; Konnektoren</a> &#8594; „Konnektor hinzufügen“.</p>''',
        f'''                    <p class="eyebrow" style="color:#2b45d4;">Kalender &middot; Beta</p>
                    <p class="h2">Apple Kalender verbinden</p>
                    <p class="p" style="margin-bottom:12px;">Du planst mit dem iPhone und iCloud? Dann kann Petra jetzt auch in deinem Apple Kalender nachsehen, wann du Zeit hast, und Termine eintragen. Die Funktion ist noch in der Beta. Sag uns gern, wie es bei dir läuft.</p>
                    <p style="{F}font-size:13px;line-height:20px;color:#6c788f;margin:0;"><strong style="color:#47546c;">So geht's:</strong> <a href="{APP}/settings/calendar" style="color:#2b45d4;text-decoration:underline;">Einstellungen &#8594; Kalender</a> &#8594; Apple iCloud wählen.</p>
                    {SIGN}''',
    ])

# Feature of the Week vor die Fußleiste
html = html.replace("          <!-- ═══════════════ FOOTER BAR ═══════════════ -->",
                    fotw("Deine eigene Ansage vor Petra",
                         "Nimm eine kurze Ansage mit deiner Stimme auf, bis zu 30 Sekunden. Sie läuft bei jedem Anruf, bevor Petra begrüßt. So hören deine Kunden zuerst dich.",
                         "Anruf-Einstellungen",
                         "Aufnahme direkt im Dashboard oder Datei hochladen.")
                    + "          <!-- ═══════════════ FOOTER BAR ═══════════════ -->", 1)

# Fußleiste und Rechtliches für Bestandskunden und Resend
html = html.replace("<strong>Lieber erst schreiben?</strong> Antworte einfach auf diese Mail, ich lese jede Antwort persönlich.",
                    "<strong>Fragen?</strong> Antworte einfach auf diese Mail, wir lesen jede Antwort persönlich.")
html = html.replace("weil du Kunde bei HalloPetra warst.", "weil du Kunde bei HalloPetra bist.")
html = html.replace("[[UNSUB_LINK_DE_DE]]", "{{{RESEND_UNSUBSCRIBE_URL}}}")
html = re.sub(r'\s*<table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" bgcolor="#eef1fb">\s*<tr>\s*<td align="center" style="padding:12px 18px 0;.*?</table>',
              "", html, count=1, flags=re.S)
assert "[[" not in html, "Mailjet-Platzhalter übrig"
assert "—" not in html and "–" not in html.split("<body")[1], "Gedankenstrich"


def emb(m):
    fn = os.path.join(ROOT, m.group(1))
    mt = "image/jpeg" if fn.endswith(".jpg") else "image/png"
    return f'src="data:{mt};base64,' + base64.b64encode(open(fn, "rb").read()).decode() + '"'


open(os.path.join(ROOT, "newsletter-kw44-resend.html"), "w").write(html)
open(os.path.join(ROOT, "newsletter-kw44-preview-local.html"), "w").write(
    re.sub(r'src="https://raw.githubusercontent.com/jesko-maker/hallopetra-referral/main/([^"]+)"', emb, html))
print("ok kw44")
