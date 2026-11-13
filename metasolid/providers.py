"""Embedding and generation over plain HTTP to OpenAI-compatible routes; no SDK."""

import json

import numpy as np
import requests

BASE_URLS = {
    "ollama": "http://localhost:11434/v1",
    "llama-cpp": "http://localhost:8080/v1",
    "vllm": "http://localhost:8080/v1",
    "open-llm": "https://openllm.scilifelab.se/api",
    "openai": "https://api.openai.com/v1",
}


def connection(provider: str, route: str, api_key: str | None, endpoint: str | None):
    """URL and headers for one route of a provider; `endpoint` overrides the URL."""
    base = BASE_URLS.get(provider.lower())
    if base is None:
        raise ValueError(
            f"Unsupported provider {provider!r}; "
            f"expected one of: {', '.join(BASE_URLS)}"
        )
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    return endpoint or f"{base}/{route}", headers


def build_embedder(
    provider: str,
    model_name: str,
    api_key: str | None = None,
    endpoint: str | None = None,
):
    """A function that embeds a string or a list of strings into a float32 array."""
    url, headers = connection(provider, "embeddings", api_key, endpoint)

    def embed(text_input: str | list[str]) -> np.ndarray:
        payload = {"model": model_name, "input": text_input}
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to embed text at {url}: {e}") from e
        try:
            vectors = [item["embedding"] for item in data["data"]]
        except (KeyError, IndexError, TypeError) as e:
            raise RuntimeError(
                f"Failed to parse embedding payload: {e}. Raw response: {data}"
            ) from e
        return np.array(vectors, dtype=np.float32)

    return embed


def build_generator(
    provider: str,
    model_name: str,
    api_key: str | None = None,
    endpoint: str | None = None,
):
    """A function that sends one prompt and returns the reply, as JSON by default."""
    url, headers = connection(provider, "chat/completions", api_key, endpoint)

    def generate(prompt: str, return_json: bool = True) -> str | dict:
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        }
        if return_json:
            payload["response_format"] = {"type": "json_object"}
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to generate text at {url}: {e}") from e
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as e:
            raise RuntimeError(
                f"Malformed response during text generation: {data}"
            ) from e
        if not return_json:
            return content
        try:
            return json.loads(content)
        except (json.JSONDecodeError, TypeError) as e:
            raise RuntimeError(f"Cannot build json from contents: {content}") from e

    return generate
