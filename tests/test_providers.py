import numpy as np
import pytest
import responses

from metasolid.providers import (
    BASE_URLS,
    build_embedder,
    build_generator,
    connection,
)

# Inert placeholder: requests go to `responses`, never to a real service.
DUMMY_API_KEY = "dummy"  # pragma: allowlist secret
OLLAMA_EMBED = "http://localhost:11434/v1/embeddings"
OLLAMA_CHAT = "http://localhost:11434/v1/chat/completions"


@pytest.mark.parametrize("provider", list(BASE_URLS))
def test_every_provider_builds(provider):
    assert callable(build_embedder(provider, "m", DUMMY_API_KEY))
    assert callable(build_generator(provider, "m", DUMMY_API_KEY))


def test_connection_default_url_and_override():
    assert connection("OPEN-LLM", "embeddings", None, None) == (
        "https://openllm.scilifelab.se/api/embeddings",
        {},
    )
    url, headers = connection("ollama", "embeddings", DUMMY_API_KEY, "http://x/e")
    assert url == "http://x/e"
    assert headers == {"Authorization": f"Bearer {DUMMY_API_KEY}"}


def test_connection_rejects_unknown_provider():
    with pytest.raises(ValueError, match="Unsupported provider 'opem-llm'"):
        connection("opem-llm", "embeddings", None, None)


@responses.activate
def test_embed_returns_float32_rows():
    responses.post(
        OLLAMA_EMBED, json={"data": [{"embedding": [1, 2]}, {"embedding": [3, 4]}]}
    )
    vectors = build_embedder("ollama", "m")(["a", "b"])
    assert vectors.dtype == np.float32
    assert vectors.tolist() == [[1, 2], [3, 4]]


@responses.activate
def test_embed_raises_on_a_malformed_payload():
    responses.post(OLLAMA_EMBED, json={"unexpected": []})
    with pytest.raises(RuntimeError, match="Failed to parse embedding payload"):
        build_embedder("ollama", "m")(["a"])


def _chat(content):
    return {"choices": [{"message": {"content": content}}]}


@responses.activate
def test_generate_parses_json_and_returns_text():
    generate = build_generator("ollama", "m")
    responses.post(OLLAMA_CHAT, json=_chat('{"label": "x"}'))
    assert generate("p") == {"label": "x"}
    responses.post(OLLAMA_CHAT, json=_chat("plain text"))
    assert generate("p", return_json=False) == "plain text"


@responses.activate
def test_generate_raises_when_json_was_asked_and_text_came_back():
    responses.post(OLLAMA_CHAT, json=_chat("not json"))
    with pytest.raises(RuntimeError, match="Cannot build json"):
        build_generator("ollama", "m")("p")
