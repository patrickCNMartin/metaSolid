import sys
from pathlib import Path

# Ensure `src` is on sys.path so imports work when running pytest from project root
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from metaSolid.harmonize import create_hiarchy


def _generator(response):
    """Build a stub generator_func that always returns `response`."""

    def generate(prompt, return_json=True):
        return response

    return generate


def test_create_hiarchy_strips_code_fence():
    raw = "```yaml\nsample_type:\n  description: a sample\n```"
    out = create_hiarchy(_generator(raw), {})
    assert out == "sample_type:\n  description: a sample"


def test_create_hiarchy_preserves_literal_yaml_in_content():
    """Regression: cleanup used to be `re.sub("yaml", "", response)`, which
    corrupted any field or description legitimately containing "yaml"."""
    raw = "```yaml\nconfig_format:\n  description: yaml or json config\n```"
    out = create_hiarchy(_generator(raw), {})
    assert "yaml or json config" in out
    assert "```" not in out


def test_create_hiarchy_handles_unfenced_response():
    raw = "sample_type:\n  description: a sample"
    assert create_hiarchy(_generator(raw), {}) == raw
