"""A markdown report beside the plots, and its PDF through pandoc and typst."""

import shutil
import subprocess
from pathlib import Path

PDF_TOOLS = ("pandoc", "typst")


def write_report(output: Path, plots: list[str], harmonized: dict) -> Path:
    """report.md in `output`: each plot, then the harmonized fields."""
    lines = ["# metaSolid report", ""]
    for plot in plots:
        lines += [f"![]({plot}){{width=100%}}", ""]
    lines += ["## Harmonized fields", ""]
    lines += [f"- **{field}**: {meaning}" for field, meaning in harmonized.items()]
    path = output / "report.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def check_pdf_tools() -> None:
    """Raise if pandoc or typst is missing, so a run fails before any model call."""
    missing = [tool for tool in PDF_TOOLS if shutil.which(tool) is None]
    if missing:
        raise RuntimeError(
            f"--render_report needs {' and '.join(missing)} on PATH; "
            f"see Setup in the README."
        )


def render_pdf(markdown: Path, pdf: Path) -> None:
    """Markdown to PDF; pandoc runs beside the markdown so its image paths resolve."""
    subprocess.run(
        ["pandoc", markdown.name, "--pdf-engine=typst", "-o", str(pdf.resolve())],
        cwd=markdown.parent,
        check=True,
    )
