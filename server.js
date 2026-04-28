const express = require('express');
const path = require('path');
const fetch = require('node-fetch');

const app = express();
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

app.post('/api/referral', async (req, res) => {
  const {
    referrer_name, referrer_email, referrer_company,
    lead_name, lead_company, lead_email, lead_phone
  } = req.body;

  if (!referrer_name || !referrer_email || !lead_name || !lead_email || !lead_company) {
    return res.status(400).json({ error: 'Pflichtfelder fehlen' });
  }

  const API_KEY    = process.env.MAILJET_API_KEY;
  const API_SECRET = process.env.MAILJET_API_SECRET;
  const DEMO_LINK  = process.env.DEMO_LINK || 'https://hallopetra.de';
  const FROM_EMAIL = process.env.FROM_EMAIL || 'info@hallopetra.de';
  const NOTIFY_MAIL = process.env.NOTIFY_EMAIL || 'jesko@hallopetra.de';

  const auth = Buffer.from(`${API_KEY}:${API_SECRET}`).toString('base64');

  const leadHtml = `
<!DOCTYPE html><html lang="de"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  body{margin:0;padding:0;background:#f0f4f8;font-family:Inter,Arial,Helvetica,sans-serif;}
  .wrap{max-width:600px;margin:32px auto;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 1px 16px rgba(0,0,0,0.06);}
  .hero{background:#2d4f7c;padding:36px 40px 32px;}
  .hero img{width:72px;height:72px;border-radius:50%;border:3px solid rgba(255,255,255,0.4);}
  .hero h1{color:#fff;font-size:22px;font-weight:700;margin:16px 0 6px;}
  .hero p{color:rgba(255,255,255,0.8);font-size:14px;margin:0;}
  .body{padding:36px 40px;}
  .label{text-align:center;color:#2d4f7c;font-size:11px;letter-spacing:3px;text-transform:uppercase;font-weight:600;margin-bottom:8px;}
  h2{text-align:center;color:#1b1b1b;font-size:22px;font-weight:700;margin:0 0 4px;}
  .divider{width:60px;height:3px;background:#2d4f7c;margin:12px auto 24px;}
  p{color:#4a4a4a;font-size:15px;line-height:26px;text-align:center;margin:0 0 14px;}
  .cta{display:block;background:#2d4f7c;color:#fff;font-size:15px;font-weight:600;text-decoration:none;padding:16px 32px;border-radius:8px;text-align:center;margin:28px auto 0;max-width:280px;}
  .footer{background:#2d4f7c;padding:32px 40px;text-align:center;}
  .footer p{color:rgba(255,255,255,0.7);font-size:13px;margin:0;}
</style></head><body>
<div class="wrap">
  <div class="hero">
    <img src="https://framerusercontent.com/images/wD5sulqIEBeqaadHq8mrgRoqziI.png" alt="Petra">
    <h1>HalloPetra</h1>
    <p>Die KI-Bürokraft für Handwerksbetriebe</p>
  </div>
  <div class="body">
    <p class="label">Empfehlung</p>
    <h2>${referrer_name} hat euch bei HalloPetra empfohlen.</h2>
    <div class="divider"></div>
    <p>Hallo ${lead_name},</p>
    <p>${referrer_name} ${referrer_company ? 'von ' + referrer_company : ''} denkt, dass HalloPetra euren Betrieb unterstützen kann. Petra nimmt Anrufe an, vereinbart Termine und hält den Laden am Laufen, während ihr auf der Baustelle seid.</p>
    <p>In einer kurzen Demo zeigen wir euch, was Petra konkret für <strong>${lead_company}</strong> tun kann. Kein Aufwand, kein Verkaufsgespräch.</p>
    <a href="${DEMO_LINK}" class="cta">Demo vereinbaren →</a>
  </div>
  <div class="footer">
    <p>Fragen? Antwortet einfach auf diese Mail.</p>
  </div>
</div>
</body></html>`;

  const referrerHtml = `
<!DOCTYPE html><html lang="de"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  body{margin:0;padding:0;background:#f0f4f8;font-family:Inter,Arial,Helvetica,sans-serif;}
  .wrap{max-width:600px;margin:32px auto;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 1px 16px rgba(0,0,0,0.06);}
  .hero{background:#2d4f7c;padding:36px 40px 32px;}
  .hero img{width:72px;height:72px;border-radius:50%;border:3px solid rgba(255,255,255,0.4);}
  .hero h1{color:#fff;font-size:22px;font-weight:700;margin:16px 0 6px;}
  .hero p{color:rgba(255,255,255,0.8);font-size:14px;margin:0;}
  .body{padding:36px 40px;}
  .label{text-align:center;color:#2d4f7c;font-size:11px;letter-spacing:3px;text-transform:uppercase;font-weight:600;margin-bottom:8px;}
  h2{text-align:center;color:#1b1b1b;font-size:22px;font-weight:700;margin:0 0 4px;}
  .divider{width:60px;height:3px;background:#2d4f7c;margin:12px auto 24px;}
  p{color:#4a4a4a;font-size:15px;line-height:26px;text-align:center;margin:0 0 14px;}
  .highlight{background:#eff4ff;border-radius:12px;padding:20px 24px;margin:20px 0;}
  .highlight p{margin:0;color:#2d4f7c;font-weight:600;font-size:15px;}
  .footer{background:#2d4f7c;padding:32px 40px;text-align:center;}
  .footer p{color:rgba(255,255,255,0.7);font-size:13px;margin:0;}
</style></head><body>
<div class="wrap">
  <div class="hero">
    <img src="https://framerusercontent.com/images/wD5sulqIEBeqaadHq8mrgRoqziI.png" alt="Petra">
    <h1>HalloPetra</h1>
    <p>Die KI-Bürokraft für Handwerksbetriebe</p>
  </div>
  <div class="body">
    <p class="label">Danke für deine Empfehlung</p>
    <h2>Empfehlung eingegangen.</h2>
    <div class="divider"></div>
    <p>Hallo ${referrer_name},</p>
    <p>wir haben ${lead_name} von ${lead_company} gerade eine E-Mail mit einem Link zur Demo geschickt. Wenn der Betrieb Kunde wird, steht dir das WhatsApp-Feature kostenlos zur Verfügung.</p>
    <div class="highlight">
      <p>Für jede Empfehlung, die Kunde wird: WhatsApp-Feature kostenlos.</p>
    </div>
    <p>Danke, dass du HalloPetra weiterempfiehlst.</p>
  </div>
  <div class="footer">
    <p>Fragen? Antwortet einfach auf diese Mail.</p>
  </div>
</div>
</body></html>`;

  const notifyText = `
Neue Empfehlung eingegangen:

Empfohlen von: ${referrer_name} (${referrer_company || '–'}) – ${referrer_email}
Lead: ${lead_name} – ${lead_company} – ${lead_email}${lead_phone ? ' – Tel: ' + lead_phone : ''}

Demo-Link wurde an ${lead_email} gesendet.
  `.trim();

  try {
    const response = await fetch('https://api.mailjet.com/v3.1/send', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Basic ${auth}`
      },
      body: JSON.stringify({
        Messages: [
          {
            From: { Email: FROM_EMAIL, Name: 'HalloPetra' },
            To: [{ Email: lead_email, Name: lead_name }],
            Subject: `${referrer_name} hat euch bei HalloPetra empfohlen`,
            HTMLPart: leadHtml
          },
          {
            From: { Email: FROM_EMAIL, Name: 'HalloPetra' },
            To: [{ Email: referrer_email, Name: referrer_name }],
            Subject: 'Deine Empfehlung ist eingegangen',
            HTMLPart: referrerHtml
          },
          {
            From: { Email: FROM_EMAIL, Name: 'HalloPetra' },
            To: [{ Email: NOTIFY_MAIL, Name: 'HalloPetra Team' }],
            Subject: `Neue Empfehlung: ${lead_name} – ${lead_company}`,
            TextPart: notifyText
          }
        ]
      })
    });

    const data = await response.json();
    if (!response.ok) {
      console.error('Mailjet error:', data);
      return res.status(500).json({ error: 'E-Mail konnte nicht gesendet werden' });
    }

    res.json({ success: true });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Serverfehler' });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server läuft auf Port ${PORT}`));
