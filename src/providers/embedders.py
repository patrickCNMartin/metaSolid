# -----------------------------------------------------------------------------#
# IMPORT LIBS
# -----------------------------------------------------------------------------#
from typing import List, Union
import numpy as np
import requests


# -----------------------------------------------------------------------------#
# FUNCTIONS
# -----------------------------------------------------------------------------#
def build_embedder(
    provider: str = "ollama",
    model_name: str = "nomic-embed-text",
    api_key: str = None,
    endpoint: str = None,
):
    # 1. Establish the network configuration for embeddings
    match provider.lower():
        case "ollama":
            url = endpoint or "http://localhost:11434/v1/embeddings"
            headers = {
                "Authorization": "Bearer local-sovereign",
                "Content-Type": "application/json",
            }
        case "llama-cpp" | "vllm":
            url = endpoint or "http://localhost:8080/v1/embeddings"
            headers = {"Content-Type": "application/json"}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
        case "opem-llm":
            url = endpoint or "https://openllm.scilifelab.se/api/embeddings"
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
        case "openai":
            url = endpoint or "https://api.openai.com/v1/embeddings"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
        case _:
            raise ValueError(f"Unsupported embedding profile: {provider}")

    # NOTE: the purpose of doing this is for maximum sovereignty.
    # I don't want to rely on any vendor sdk if I can avoid doing so.
    # The goal is to have universal open source approach
    def embed(text_input: Union[str, List[str]]) -> np.ndarray:
        """
        Takes a single string or a list of text chunks and
        returns their vector embeddings.
        """
        # Prepare prompt
        payload = {"model": model_name, "input": text_input}

        # Pull embeddings
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            response_data = response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to embed text: {e}")

        # Clean results and convert to NumPy array
        try:
            results = response_data["data"]
            raw_embeddings = [item["embedding"] for item in results]
            return np.array(raw_embeddings, dtype=np.float32)
        except (KeyError, IndexError, TypeError) as e:
            # Halt execution with a descriptive exception
            raise RuntimeError(
                f"Failed to parse embedding payload: {e}. Raw response: {response_data}"
            )

    return embed
