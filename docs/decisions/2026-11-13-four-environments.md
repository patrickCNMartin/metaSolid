---
date: 2026-11-13
title: Four environments from one dependency declaration; Ollama stays on the host
decided_by: [human:patrickCNMartin, claude-code/claude-opus-5-5]
---

**Decided:** uv, nix, pixi and docker, with `pyproject.toml` the only place a Python package is
named. `flake.nix` is a dev shell (Python, uv, git, pandoc, typst) that syncs `.venv` with uv, and
calls `oci.nix` for `.#oci`, whose Python packages come from nixpkgs. The `Dockerfile` builds a uv
venv in one stage and copies only it, with pandoc from Debian and typst from the official image.
`pixi.toml` takes Python, git, pandoc and typst from conda-forge. Images are tagged with the
`pyproject.toml` version. ruff is pinned in `pyproject.toml` to the pre-commit `rev`.
**Discovered:** pandoc 3.7 (nixpkgs) and 3.1 (Debian) hand typst an empty font list unless
`mainfont` is set, and typst 0.15 refuses it; `render_pdf` now names typst's bundled Libertinus
Serif. pixi resolved ruff 0.17 while `uv.lock` held 0.15, and 0.17 also checks Markdown, so lint
differed between environments until ruff was pinned.
At nixpkgs 3ec6363 scikit-learn had no cached aarch64-linux build, so `.#oci` on a Mac needed a
Linux builder; the lock moved to d4f25a3 (2026-11-11), where it is cached.
**Why:** Ollama through nix is not workable now, and the flake used to install, start, pull and
kill it on every shell. The image builds from nixpkgs so a Mac needs no Linux builder. typst is
pinned to 0.15.1 everywhere: the version nixpkgs and conda-forge carry.
**Cost:** `oci.nix` restates the dependency list by hand. pandoc and typst add about 265 MB to the
Docker image. The Jupyter kernel registration is gone: `uv run jupyter lab` uses the venv.
