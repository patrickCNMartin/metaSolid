---
date: 2026-11-13
title: The .gitignore is a short denylist; detect-secrets guards credentials
decided_by: [human:patrickCNMartin, claude-code/claude-opus-5-5]
---

**Decided:** The `.gitignore` excludes secrets (`.env` files, with `env/.env.example` let back in),
`data/`, `iLab/`, `.claude/`, Python and environment caches, notebooks and OS files, and nothing
else. The key-file patterns, `*_token*`, `*_secret*`, `CLAUDE.md` and the scratch `src/explore/`
rule are gone.
**Why:** detect-secrets reads file contents, which is the right guard for a leaked credential.
`*_token*` and `*_secret*` silently ignored source files such as `count_tokens.py`.
**Cost:** Data written outside `data/` and `iLab/` is committable: read `git status` before
committing.
