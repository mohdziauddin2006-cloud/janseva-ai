# ▓ CONTRIBUTING // JANSEVA // DPI CORE ▓

> <samp><kbd>CORE: ONLINE</kbd> // <b>LEDGER: SACRED</b> // <kbd>THREAT:</kbd> <span style="color: #FF0000;">HOT-PATCHES TO PRODUCTION</span></samp>

Civic infrastructure doesn't get hot-patched. It gets verified, then deployed.

## 01 // THE ONE LAW

```diff
- UNCHECKED CODE ALWAYS FAILS IN A LOUDER ROOM THAN YOURS. VERIFY IT LOCALLY OR SUFFER THE REVIEW.
```

The acceptance test: run <kbd>python main.py</kbd> with all four env vars staged, drive one ticket from Telegram intake through to the console, and confirm the ledger row landed intact before you open a PR.

## 02 // NON-NEGOTIABLES

- **<kbd>Additive migrations only</kbd>** — the self-migrating ledger injects columns; it never drops or renames. A migration that breaks existing tickets is a war crime in this codebase.
- **<kbd>Keys are env vars</kbd>** — nothing hardcoded, ever. Every credential enters through `TELEGRAM_BOT_TOKEN`, `DATABASE_URL`, `GEMINI_API_KEY`, or `PORT`.
- **<kbd>AI verdicts are advisory</kbd>** — Gemini classifies and routes; humans resolve. Patches that let the model close a ticket unilaterally will be denied.
- **<kbd>Failures revive</kbd>** — anything you add must survive `main.py`'s 10-second revival loop, not fight it.

## 03 // FILING

- **<kbd>SYS-FAULT</kbd>** — which bot died, at which env var, with what evidence.
- **<kbd>UPGRADE DIRECTIVE</kbd>** — which surface gains power: intake, routing, ledger, or console.
