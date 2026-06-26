#-----------------------------------------------------------------------------#
# IMPORT LIBS
#-----------------------------------------------------------------------------#
import json
import requests
from typing import Callable, Union
#-----------------------------------------------------------------------------#
# FUNCTIONS
#-----------------------------------------------------------------------------#
def build_generator(
    provider: str = "ollama", 
    model_name: str = "qwen:v1.0",
    api_key: str = None,
    endpoint: str = None
) -> Callable[[str, bool], Union[str, dict]]:
    
    match provider.lower():
        case "ollama":
            # Native local Ollama architecture
            url = endpoint or "http://localhost:11434/v1/chat/completions"
            headers = {"Authorization": "Bearer local", "Content-Type": "application/json"}
        case "llama-cpp" | "vllm":
            # Self-hosted embedded servers on local metal or isolated clusters
            url = endpoint or "http://localhost:8080/v1/chat/completions"
            headers = {"Content-Type": "application/json"}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
        case "openai":
            # Strictly fallback commercial layer
            # assume that this is the default url
            url = endpoint or "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        case _:
            raise ValueError(f"Unsupported profile: {provider}")
    
    # NOTE: the purpose of doing this is for maximum sovereignty. I don't want to rely on any
    # vendor sdk if I can avoid doing so. The goal is to have universal open source approach
    def generate(prompt: str, return_json: bool = True) -> Union[str, dict]:
        # Prepare prompt
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }
        
        # Make sure that response comes as json
        if return_json:
            payload["response_format"] = {"type": "json_object"}

        # Now we send the request to the LLM
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            response_data = response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to generate text: {e}")

        # Pull data from response
        try:
            raw_contents = response_data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            raise RuntimeError("Malformed response during text generation: {response_data}")

        # If we need a json and not just text we format and return as dict instead of text
        if return_json:
            try:
                return json.loads(raw_contents)
            except (json.JSONDecodeError, TypeError):
                raise RuntimeError("Cannot build json from contents: {raw_contents}")
                
        return raw_contents

    return generate