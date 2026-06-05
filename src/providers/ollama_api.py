#-----------------------------------------------------------------------------#
# IMPORT LIBS
#-----------------------------------------------------------------------------#
import json
import ollama
from typing import Callable
model_name = "qwen:v1.0"
#-----------------------------------------------------------------------------#
# FUNCTIONS
#-----------------------------------------------------------------------------#


def ollama_generator(model_name:str) -> Callable[[str,bool],str|dict]:
    def generate(prompt:str, return_json:bool = True) -> str|dict:
        format_type = 'json' if return_json else ''
        response = ollama.chat(
            model=model_name,
            messages=[{'role': 'user', 'content': prompt}],
            format=format_type,
            stream=False
        )
        raw_contents = response['message']['content']
        if return_json:
            return json.loads(raw_contents)
        else:
            return raw_contents
    return generate
