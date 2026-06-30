import sys
from pathlib import Path

import pytest

# Ensure `src` is on sys.path so imports work when running pytest from project root
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from metaSolid import run_metaSolid as run_meta
from synthetic import synthetic_ilab as synth_ilab


def test_run_meta_parse_args_missing(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["run_meta"])
    with pytest.raises(SystemExit):
        run_meta.parse_args()


def test_run_meta_parse_args_ok(monkeypatch):
    monkeypatch.setattr(
        sys, "argv", ["run_meta", "--metadata",
                      "meta.json", "--output", "outdir"]
    )
    ns = run_meta.parse_args()
    assert ns.metadata == "meta.json"
    assert ns.output == "outdir"


def test_synth_ilab_parse_args_missing(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["synth_ilab"])
    with pytest.raises(SystemExit):
        synth_ilab.parse_args()


def test_synth_ilab_parse_args_ok(monkeypatch):
    monkeypatch.setattr(
        sys, "argv", ["synth_ilab", "--metadata",
                      "meta.json", "--output", "outdir"]
    )
    ns = synth_ilab.parse_args()
    assert ns.metadata == "meta.json"
    assert ns.output == "outdir"
