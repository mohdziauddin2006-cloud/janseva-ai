---
name: UPGRADE DIRECTIVE
about: Propose an enhancement to the core
title: "[DIRECTIVE] "
labels: ""
assignees: ""

---

> <samp><kbd>UPGRADE CHANNEL</kbd> // <b>NEW SURFACES COME WITH MAINTENANCE COSTS</b></samp>

**The directive**

Which surface gains power — <kbd>INTAKE</kbd> · <kbd>ROUTING</kbd> · <kbd>LEDGER</kbd> · <kbd>CONSOLE</kbd> — and why the current one is insufficient. One paragraph.

**Ledger impact**

Does this touch <kbd>janseva_tickets</kbd>? If yes: additive only (ALTER TABLE ADD COLUMN), fully documented, and reversible for old rows. Anything else gets redesigned or not built.

**Revival check**

Will your feature survive <kbd>main.py</kbd>'s 10-second crash-revival loop without becoming a crash source?

```diff
- A FEATURE THAT WRITES TO THE LEDGER WITHOUT AUDIT TRAIL IS REJECTED ON SIGHT.
```
