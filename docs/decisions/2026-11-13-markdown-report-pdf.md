---
date: 2026-11-13
title: The report is markdown beside the plots, rendered to PDF by pandoc and typst on request
decided_by: [human:patrickCNMartin, claude-code/claude-opus-5-5]
---

**Decided:** Every run writes `report.md` (the plots, then the harmonized fields). `--render_report`
also renders `report.pdf` with `pandoc --pdf-engine=typst`, and checks both tools are on PATH
before any model call. The python-pptx slide builder is gone.
**Why:** One markdown source, and pandoc is the renderer. typst over LaTeX: one small binary in
nixpkgs and conda-forge, no TeX install, and µ, °C and ± render with its bundled fonts, where
pdflatex stops on them.
**Cost:** The report template, when it comes, is a pandoc typst template. Pandoc and typst are
system tools: the uv-only setup installs them by hand.
