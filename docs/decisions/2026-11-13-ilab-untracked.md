---
date: 2026-11-13
title: iLab and synthetic data generation leave metaSolid for an untracked iLab/ folder
decided_by: [human:patrickCNMartin, claude-code/claude-opus-5-5]
---

**Decided:** The iLab API client, its markdown writer, its date helpers and the synthetic data
generator move to `iLab/`, which is gitignored. `build_ppt.py` and the unused `Ok`/`Err` classes are
deleted. `iLab/` imports from metaSolid (`providers`, and the report renderer); metaSolid never
imports from `iLab/`. The iLab variables move from `env/.env.example` to `iLab/env.example`.
**Why:** metaSolid harmonizes field names; fetching iLab requests and building core-meeting slides is
a separate tool. The old synthetic output carried real request values (names, emails, phone, iLab
URLs), so it moved to `iLab/` with the generator rather than becoming a fixture.
**Cost:** Nothing in `iLab/` is reviewed, tested in CI or backed up by git from here on.
