---
date: 2026-11-13
title: Decisions are logged one file each through dev-skills/logging
decided_by: [human:patrickCNMartin, claude-code/claude-opus-5-5]
---

**Decided:** Agent-session decisions go in `docs/decisions/`, one file per decision, committed with
their work. `dev-skills/logging/` holds the skill and `log.sh`, copied from Iris. `log.sh` is
unchanged so the repos stay in step; the skill drops the frozen `docs/audit_log.md`, which this
repo never had.
**Why:** Same scheme as Hermetica and Iris: a new file per decision never conflicts on merge, and
no stored hash breaks on a rebase.
**Cost:** None.
