---
name: SYS-FAULT
about: Report a failure in the grievance core
title: "[FAULT] "
labels: ""
assignees: ""

---

> <samp><kbd>CORE: ONLINE</kbd> // <b>CORE OVERRIDE</b> // <b>LEDGER:</b> <span style="color: #FF0000;">DO NOT TOUCH ON FAITH</span></samp>

**Which organ failed**

<kbd>bot.py</kbd> (intake) · <kbd>backend.py</kbd> (routing/ledger) · <kbd>app.py</kbd> (console) · <kbd>main.py</kbd> (supervisor)

**Reproduction sequence**

1. …
2. …
3. Failure: …

**Environment**

- <kbd>TELEGRAM_BOT_TOKEN</kbd> / <kbd>DATABASE_URL</kbd> / <kbd>GEMINI_API_KEY</kbd>: set or unset?
- Python <kbd>3.11.x</kbd>, OS:
- Supervisor heartbeat: did <kbd>main.py</kbd> revive it before you could even look?

**Ledger evidence**

Relevant log lines or ticket state. The ledger is the truth; your opinion of it is not.

```diff
- A FAULT REPORT WITHOUT LEDGER EVIDENCE IS A RUMOR. RUMORS ARE CLOSED AUTOMATICALLY.
```
