import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

# Ensure `src` is on sys.path so imports work when running pytest from project root
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pptx import Presentation

from reporting.build_ppt import convert_md_to_ppt

SAMPLE_MD = """# First Slide

## A sub-heading

- a bullet
- another bullet with **bold** text

A plain paragraph.

# Second Slide

1. a numbered item
- a nested bullet
"""


@pytest.fixture
def rendered_deck(tmp_path):
    """Render SAMPLE_MD to a real .pptx on disk and return the path."""
    md_path = tmp_path / "report.md"
    md_path.write_text(SAMPLE_MD, encoding="utf-8")
    out_path = tmp_path / "report.pptx"

    convert_md_to_ppt(str(md_path), str(out_path))
    return out_path


def test_render_produces_a_nonempty_file(rendered_deck):
    assert rendered_deck.exists()
    assert rendered_deck.stat().st_size > 0


def test_render_produces_a_valid_openable_pptx(rendered_deck):
    """A .pptx is an OOXML zip; reopening it proves it is well-formed rather
    than merely present."""
    assert zipfile.is_zipfile(rendered_deck)

    prs = Presentation(str(rendered_deck))
    # 1 generated title slide + 1 per H1 in SAMPLE_MD
    assert len(prs.slides) == 3


def test_rendered_deck_contains_the_source_text(rendered_deck):
    prs = Presentation(str(rendered_deck))
    text = " ".join(
        shape.text_frame.text
        for slide in prs.slides
        for shape in slide.shapes
        if shape.has_text_frame
    )

    assert "First Slide" in text
    assert "Second Slide" in text
    assert "a bullet" in text


def test_render_shells_out_to_nothing(tmp_path, monkeypatch):
    """Regression guard for the pandoc removal: python-pptx writes the .pptx
    natively, so rendering must not invoke any external binary. Fails loudly if
    someone reintroduces a pandoc/libreoffice subprocess call."""

    def _fail(*args, **kwargs):
        raise AssertionError(f"unexpected subprocess call: {args!r}")

    for name in ("run", "call", "check_call", "check_output", "Popen"):
        monkeypatch.setattr(subprocess, name, _fail)

    md_path = tmp_path / "report.md"
    md_path.write_text(SAMPLE_MD, encoding="utf-8")
    out_path = tmp_path / "report.pptx"

    convert_md_to_ppt(str(md_path), str(out_path))
    assert out_path.exists()
