<div align="center">

# ▓ JANSEVA // DPI CORE ▓

</div>

<p align="center">
  <sub><samp><kbd><b>CORE</b></kbd> · TELEGRAM → GEMINI → LEDGER &nbsp;·&nbsp; <b>THREAT:</b> <span style="color: #FF0000;">CIVIC DECAY — DENIED</span></samp></sub>
</p>

---

A civic-grievance system with a taste for order. Citizens file complaints over Telegram; Gemini 2.5 Flash reads the mess and assigns a real statutory office — PWD division, GHMC circle, cyber cell — plus a nodal officer to answer for it. Every intake becomes a ticket row. Every ticket is auditable from a Streamlit console that decides who you are before it shows you anything.

## 01 // INGESTION

<kbd>bot.py</kbd> accepts text, photo, video, animation, voice, audio, document. One chat, one evidence buffer. Reply with a GPS pin and the session closes: a <kbd>GRV-MMDDHHMMSS</kbd> ticket departs the intake with category, severity, summary, office, and officer attached. Come back later and <kbd>STATUS GRV-MMDDHHMMSS</kbd> will tell you exactly how it's going. Complaints are not a democracy; they're a pipeline.

## 02 // LEDGER

<kbd>janseva_tickets</kbd> on PostgreSQL. The schema migrates itself — accountability columns (budget allocated, contractor, materials used) are injected at boot, so old rows never block new ones. Status begins at <samp>1. Pending Review</samp>. Moving it is not the intake's job; the console's executive and field commands handle that.

## 03 // CONSOLE

Role-gated, not decorative. <span style="color: #FF0000;"><b>Every row keeps the full dossier</b></span> — claimant chat, evidence media, GPS, AI verdict, office, officer, budget allocated vs. spent, contractor, materials, resolution media, timestamps. Nothing gets summarized away.

| ROLE | SURFACES |
|:--|:--|
| <kbd>🌐 PUBLIC</kbd> | Social Audit Ledger · Jurisdictional Map |
| <kbd>🏛️ EXECUTIVE</kbd> | Executive Sanctions · Social Audit Ledger |
| <kbd>👷 FIELD</kbd> | Field Execution (Material Budget) · Social Audit Ledger |

## 04 // DEPLOYMENT

Four environment variables. Nothing hardcoded, nothing to hunt for.

| ENV VAR | PURPOSE |
|:--|:--|
| <kbd>TELEGRAM_BOT_TOKEN</kbd> | Intake channel credential |
| <kbd>DATABASE_URL</kbd> | PostgreSQL ledger connection |
| <kbd>GEMINI_API_KEY</kbd> | Routing engine credential |
| <kbd>PORT</kbd> | Streamlit console port (default `8501`) |

```bash
git clone https://github.com/mohdziauddin2006-cloud/janseva-ai.git
cd janseva-ai
export TELEGRAM_BOT_TOKEN=... DATABASE_URL=... GEMINI_API_KEY=...
pip install -r requirements.txt
python main.py
```

<kbd>main.py</kbd> is the supervisor: it spawns both halves and revives anything that dies, checking every 10 seconds. <kbd>./start.sh</kbd> is the PaaS cut — bot in the background, Streamlit on <kbd>$PORT</kbd>, runtime pinned to Python 3.11.9. Loadout: Streamlit · pyTelegramBotAPI · google-genai · psycopg2-binary · pandas · requests · plotly.

---

<div align="center">

<sub><samp>▓ <span style="color: #FF0000;">THE TICKET NEVER FORGIVES A DEAD PMC.</span> ▓</samp></sub>

<sub><samp>Documentation themed under the <b>Evil Ultron</b> standard. Application logic untouched, as it should be.</samp></sub>

</div>
