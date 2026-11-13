import shutil

import matplotlib.pyplot as plt
import pytest

from metasolid import report
from metasolid.report import check_pdf_tools, render_pdf, write_report


def test_write_report_links_the_plots_and_lists_the_fields(tmp_path):
    md = write_report(tmp_path, ["a.png"], {"sample_type": "What the samples are."})
    text = md.read_text()
    assert md == tmp_path / "report.md"
    assert "![](a.png){width=100%}" in text
    assert "- **sample_type**: What the samples are." in text


def test_check_pdf_tools_names_what_is_missing(monkeypatch):
    monkeypatch.setattr(report.shutil, "which", lambda tool: None)
    with pytest.raises(RuntimeError, match="needs pandoc and typst"):
        check_pdf_tools()


@pytest.mark.skipif(
    not all(shutil.which(t) for t in report.PDF_TOOLS), reason="needs pandoc and typst"
)
def test_render_pdf_with_a_plot(tmp_path):
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    fig.savefig(tmp_path / "plot.png")
    plt.close(fig)
    md = write_report(tmp_path, ["plot.png"], {"temperature": "Stored at 4 °C, ± 1 µL"})
    render_pdf(md, tmp_path / "report.pdf")
    assert (tmp_path / "report.pdf").read_bytes().startswith(b"%PDF")
