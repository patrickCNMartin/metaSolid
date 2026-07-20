import sys
from pathlib import Path

import pytest

# Ensure `src` is on sys.path so imports work when running pytest from project root
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from providers.embedders import build_embedder


@pytest.mark.parametrize(
    "provider", ["ollama", "llama-cpp", "vllm", "open-llm", "openai"]
)
def test_build_embedder_supported_providers(provider):
    """Every documented provider key must build without raising."""
    assert callable(build_embedder(provider=provider, api_key="dummy"))


def test_build_embedder_open_llm_default_endpoint():
    """Regression: the key was previously misspelled `opem-llm`, making the
    self-hosted OpenLLM embedding backend unreachable."""
    assert callable(build_embedder(provider="open-llm", api_key="dummy"))


def test_build_embedder_provider_is_case_insensitive():
    assert callable(build_embedder(provider="OPEN-LLM", api_key="dummy"))


def test_build_embedder_rejects_unknown_provider():
    with pytest.raises(ValueError, match="Unsupported embedding profile"):
        build_embedder(provider="opem-llm", api_key="dummy")
