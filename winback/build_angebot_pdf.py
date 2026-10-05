# Baut das Winback-Angebot als A4-PDF (Vorlage: Angebot Auler + Haubrich), Variante Oktober oder November.
# Aufruf: python3 build_angebot_pdf.py kunde.json   (ohne Argument: Musterkunde für die Vorschau)
import json, pathlib, subprocess, sys, html, datetime

ROOT = pathlib.Path(__file__).resolve().parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

ANSPRECHPARTNER = dict(
    name="Jesko Will",
    rolle="Mitgründer, Ihr persönlicher Ansprechpartner",
    mobil="+49 MOBILNUMMER",
    mail="jesko@hallopetra.de",
)

VARIANTEN = {
    "oktober": dict(
        ziel="Petra arbeitet ab sofort wieder für Sie. Bis zum 30. November zahlen Sie nichts, die erste Zahlung fällt am 1. Dezember 2026 an.",
        fahrplan=[
            ("Heute", "Zusage", "Eine kurze Mail oder ein Anruf genügt."),
            ("Diese Woche", "Neueinrichtung", "Wir gehen Petras Einstellungen gemeinsam durch, damit sie vom ersten Anruf an so arbeitet, wie Sie es brauchen."),
            ("Bis 30. November", "Kostenlos", "Petra nimmt Ihre Anrufe an. Sie zahlen in dieser Zeit nichts."),
            ("1. Dezember", "Erste Zahlung", "Ihr regulärer Tarif beginnt."),
        ],
        fahrplan_hinweis="So sehen Sie im November selbst, wie Petra heute arbeitet, bevor der erste Euro fließt.",
        konditionen=[
            ("Start", "sofort nach Ihrer Zusage"),
            ("Kosten bis 30. November", "0,00 €"),
            ("Erste Zahlung", "1. Dezember 2026"),
            ("Rücktrittsrecht", "bis zum 30. November jederzeit kostenlos"),
        ],
        gueltig_bis="31.10.2026",
        gueltig_lang="31. Oktober 2026",
    ),
    "november": dict(
        ziel="Petra arbeitet ab sofort wieder für Sie. Erste Zahlung am 1. Dezember 2026, dazu drei Monate Geld-zurück-Garantie.",
        fahrplan=[
            ("Heute", "Zusage", "Eine kurze Mail oder ein Anruf genügt."),
            ("Diese Woche", "Neueinrichtung", "Wir gehen Petras Einstellungen gemeinsam durch, damit sie vom ersten Anruf an so arbeitet, wie Sie es brauchen."),
            ("1. Dezember", "Erste Zahlung", "Ihr regulärer Tarif beginnt. Der November bleibt kostenlos."),
            ("Bis 28. Februar", "Garantie", "Überzeugt Petra Sie nicht, erhalten Sie die Zahlungen für Dezember, Januar und Februar zurück."),
        ],
        fahrplan_hinweis="Eine kurze Mail genügt, um die Garantie in Anspruch zu nehmen. Ohne Begründung.",
        konditionen=[
            ("Start", "sofort nach Ihrer Zusage"),
            ("Kosten im November", "0,00 €"),
            ("Erste Zahlung", "1. Dezember 2026"),
            ("Geld-zurück-Garantie", "Dezember, Januar und Februar"),
        ],
        gueltig_bis="30.11.2026",
        gueltig_lang="30. November 2026",
    ),
}

MUSTER = dict(
    variante="oktober",
    angebotsnr="WB-2026-1005-MH",
    datum="05.10.2026",
    firma="Mustermann Haustechnik GmbH",
    firma_zeile2="",
    anrede="Herr Mustermann",
    ansprechpartner_kunde="Herrn Peter Mustermann",
    ort="12345 Musterstadt",
    logo="muster-logo.svg",
    paket="Betriebe",
    preis="",
    damals="Petra hat Namen und Adressen zu oft falsch verstanden, Ihre Kunden mussten sich wiederholen.",
    heute="Wir haben Petra Ihre Mitarbeiternamen, Straßen und Orte beigebracht, bevor sie wieder ans Telefon geht. Die ersten Gespräche schauen wir uns gemeinsam an.",
)

e = html.escape


def rows(items, cls="kv"):
    return "".join(f'<tr><td class="k">{e(k)}</td><td class="v">{e(v)}</td></tr>' for k, v in items)


def build(d):
    v = VARIANTEN[d["variante"]]
    a = ANSPRECHPARTNER
    preis = f'{e(d["preis"])} / Monat' if d.get("preis") else '<span style="font-family:Inter,Arial;font-weight:400;font-size:10.5pt;">Ihr bisheriger Tarif</span>'
    fahrplan = "".join(
        f'<tr><td class="k">{e(w)}</td><td class="tag">{e(t)}</td><td class="v l">{e(x)}</td></tr>' for w, t, x in v["fahrplan"]
    )
    logo = f'<img class="kundenlogo" src="{e(d["logo"])}" alt="{e(d["firma"])}">' if d.get("logo") else ""
    adresse = "<br>".join(e(x) for x in [d["firma"], d.get("firma_zeile2", ""), d["ansprechpartner_kunde"], d["ort"]] if x)
    footer = lambda n: f'''<div class="footer"><div>HalloPetra GmbH | Monbijouplatz 2, 10178 Berlin | Geschäftsführer: Jonas Südfels &amp; Hendric Martens<br>HRB 267962 B | Amtsgericht Berlin (Charlottenburg) | USt-IdNr.: DE370556341 | info@hallopetra.de | www.hallopetra.de</div><div>Seite {n}</div></div>'''

    return f'''<!doctype html>
<html lang="de"><head><meta charset="utf-8">
<title>Willkommen zurück · {e(d["firma"])}</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Plus+Jakarta+Sans:wght@600;700;800&display=block" rel="stylesheet">
<style>
  @page {{ size: A4; margin: 0; }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; font-family: Inter, Arial, sans-serif; color: #1d2433; font-size: 10.5pt; line-height: 1.55; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
  .page {{ width: 210mm; height: 297mm; padding: 14mm 20mm 0; position: relative; overflow: hidden; page-break-after: always; }}
  .page:last-child {{ page-break-after: auto; }}
  h1, h2, .brand, .ziel b, .preis {{ font-family: "Plus Jakarta Sans", Arial, sans-serif; }}
  .head {{ display: flex; justify-content: space-between; align-items: center; height: 16mm; }}
  .brand {{ display: flex; align-items: center; gap: 9px; font-size: 22pt; font-weight: 600; color: #0f1a3c; letter-spacing: -.3px; }}
  .brand img {{ width: 34px; height: 34px; border-radius: 50%; background: #e6ecfc; }}
  .kundenlogo {{ max-height: 15mm; max-width: 62mm; object-fit: contain; }}
  .meta {{ display: flex; justify-content: space-between; margin-top: 7mm; }}
  .adresse {{ font-size: 10.5pt; line-height: 1.6; }}
  .metatab {{ width: 76mm; border-collapse: collapse; font-size: 10pt; }}
  .metatab td {{ padding: 3px 0; border-bottom: 1px solid #eef0f4; }}
  .metatab td:first-child {{ color: #6c788f; font-size: 9pt; }}
  .metatab td:last-child {{ text-align: right; }}
  .eyebrow {{ margin-top: 8mm; font-size: 8.5pt; letter-spacing: .4px; text-transform: uppercase; color: #0f9d63; font-weight: 600; }}
  .eyebrow span {{ color: #2b45d4; }}
  h1 {{ font-size: 24pt; line-height: 1.15; margin: 2mm 0 5mm; font-weight: 700; color: #0f1a3c; letter-spacing: -.5px; }}
  p {{ margin: 0 0 3mm; }}
  .ziel {{ background: #eef2fd; border-left: 4px solid #2b45d4; border-radius: 0 6px 6px 0; padding: 5mm 6mm; margin: 5mm 0 6mm; }}
  .ziel .lbl {{ font-size: 8.5pt; color: #2b45d4; text-transform: uppercase; letter-spacing: .4px; margin-bottom: 1.5mm; }}
  .ziel b {{ font-size: 12.5pt; line-height: 1.4; font-weight: 700; color: #0f1a3c; display: block; }}
  h2 {{ font-size: 13.5pt; margin: 0 0 3mm; font-weight: 700; color: #0f1a3c; }}
  table.kv {{ width: 100%; border-collapse: collapse; }}
  table.kv td {{ padding: 3mm 0; border-bottom: 1px solid #e9edf5; vertical-align: top; }}
  table.kv tr:last-child td {{ border-bottom: 0; }}
  table.kv td.k {{ width: 52mm; color: #1d2433; }}
  table.kv td.v {{ text-align: right; }}
  table.kv td.v.l {{ text-align: left; }}
  table.kv td.tag {{ width: 30mm; color: #2b45d4; font-weight: 500; }}
  table.kv.vergleich td.k {{ color: #6c788f; width: 46mm; }}
  table.kv.vergleich td.v {{ text-align: left; }}
  table.kv.vergleich tr.neu td.k {{ color: #0f9d63; font-weight: 500; }}
  .kontakt {{ display: flex; gap: 6mm; align-items: center; background: #f6f8fd; border: 1px solid #e3e8f5; border-radius: 10px; padding: 6mm; margin-top: 7mm; }}
  .avatar {{ width: 17mm; height: 17mm; border-radius: 50%; background: #2b45d4; color: #fff; display: flex; align-items: center; justify-content: center; font-family: "Plus Jakarta Sans", Arial, sans-serif; font-weight: 700; font-size: 15pt; flex: none; }}
  .kontakt .lbl {{ font-size: 8.5pt; color: #2b45d4; text-transform: uppercase; letter-spacing: .4px; }}
  .kontakt .name {{ font-family: "Plus Jakarta Sans", Arial, sans-serif; font-size: 13pt; font-weight: 700; color: #0f1a3c; margin: .5mm 0 1.5mm; }}
  .kontakt .daten {{ display: flex; gap: 8mm; font-size: 10pt; }}
  .kontakt .daten span {{ color: #6c788f; margin-right: 2mm; }}
  .kontakt .note {{ font-size: 9pt; color: #6c788f; margin-top: 1.5mm; }}
  .hinweis {{ font-size: 8.5pt; color: #6c788f; margin-top: 2.5mm; }}
  .konditionen-kopf {{ display: flex; justify-content: space-between; align-items: flex-start; padding-bottom: 3mm; border-bottom: 1.2px solid #0f1a3c; }}
  .konditionen-kopf small {{ display: block; color: #6c788f; font-size: 9pt; }}
  .preis {{ font-size: 13pt; font-weight: 700; color: #0f1a3c; }}
  .section {{ margin-bottom: 9mm; }}
  .sign {{ margin-top: 8mm; }}
  .sign b {{ font-family: "Plus Jakarta Sans", Arial, sans-serif; color: #0f1a3c; }}
  .footer {{ position: absolute; left: 20mm; right: 20mm; bottom: 8mm; border-top: 1px solid #e9edf5; padding-top: 2.5mm; display: flex; justify-content: space-between; font-size: 7.5pt; color: #6c788f; line-height: 1.5; }}
</style></head><body>

<div class="page">
  <div class="head">
    <div class="brand"><img src="../petra-face-sm.png" alt="">HalloPetra</div>
    {logo}
  </div>
  <div class="meta">
    <div class="adresse">{adresse}</div>
    <table class="metatab">
      <tr><td>Angebot</td><td>{e(d["angebotsnr"])}</td></tr>
      <tr><td>Datum</td><td>{e(d["datum"])}</td></tr>
      <tr><td>Gültig bis</td><td>{v["gueltig_bis"]}</td></tr>
      <tr><td>Ansprechpartner</td><td>{a["name"]}</td></tr>
    </table>
  </div>

  <div class="eyebrow">Willkommen zurück <span>| Rückkehrangebot</span></div>
  <h1>Schön, dass Petra wieder<br>bei Ihnen anfängt</h1>
  <p>Guten Tag {e(d["anrede"])},</p>
  <p>vielen Dank für das offene Gespräch. Es freut uns sehr, dass Sie Petra noch einmal eine Chance geben. Wir haben ehrlich darüber gesprochen, was damals nicht gepasst hat, und genau dort setzen wir an.</p>

  <div class="ziel">
    <div class="lbl">Ihr Rückkehrangebot</div>
    <b>{e(v["ziel"])}</b>
  </div>

  <div class="section">
    <h2>Was sich seitdem geändert hat</h2>
    <table class="kv vergleich">
      <tr><td class="k">Ihr Punkt von damals</td><td class="v">{e(d["damals"])}</td></tr>
      <tr class="neu"><td class="k">Was wir geändert haben</td><td class="v">{e(d["heute"])}</td></tr>
    </table>
  </div>

  <div class="kontakt">
    <div class="avatar">JW</div>
    <div>
      <div class="lbl">Ihr persönlicher Ansprechpartner</div>
      <div class="name">{a["name"]}</div>
      <div class="daten"><div><span>Mobil</span>{a["mobil"]}</div><div><span>E-Mail</span>{a["mail"]}</div></div>
      <div class="note">Sie erreichen mich direkt. Wenn etwas hakt, rufen Sie einfach an, ich kümmere mich persönlich darum.</div>
    </div>
  </div>
  {footer(1)}
</div>

<div class="page">
  <div class="section" style="margin-top:4mm;">
    <h2>So läuft Ihre Rückkehr</h2>
    <table class="kv">{fahrplan}</table>
    <div class="hinweis">{e(v["fahrplan_hinweis"])}</div>
  </div>

  <div class="section">
    <h2>Konditionen</h2>
    <div class="konditionen-kopf">
      <div>HalloPetra {e(d["paket"])}<small>Ihr Paket</small></div>
      <div class="preis">{preis}</div>
    </div>
    <table class="kv">{rows(v["konditionen"])}</table>
    <div class="hinweis">Alle Preise zzgl. gesetzlicher USt.</div>
  </div>

  <div class="section">
    <h2>Zusage</h2>
    <p>Wenn Sie zurückkommen möchten, reicht eine kurze Bestätigung per E-Mail an {a["mail"]} oder ein Anruf unter {a["mobil"]}. Eine Unterschrift ist nicht nötig. Danach melde ich mich bei Ihnen und wir richten Petra gemeinsam ein. Das Angebot gilt bis zum {v["gueltig_lang"]}.</p>
    <div class="sign">
      <p>Wir freuen uns, wieder für Sie da zu sein.</p>
      <p><b>{a["name"]}</b><br><span style="color:#6c788f;font-size:9.5pt;">Mitgründer, HalloPetra</span></p>
    </div>
  </div>
  {footer(2)}
</div>
</body></html>'''


def render(d):
    out_html = ROOT / f'angebot-{d["angebotsnr"]}.html'
    out_pdf = ROOT / f'Angebot {d["firma"]} - Willkommen zurück.pdf'
    out_html.write_text(build(d), encoding="utf-8")
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=8000",
                    "--allow-file-access-from-files", f"--print-to-pdf={out_pdf}", out_html.as_uri()],
                   check=True, capture_output=True)
    return out_pdf


if __name__ == "__main__":
    data = json.loads(pathlib.Path(sys.argv[1]).read_text()) if len(sys.argv) > 1 else MUSTER
    if len(sys.argv) > 2:
        data["variante"] = sys.argv[2]
    print(render(data))
