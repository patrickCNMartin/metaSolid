#-----------------------------------------------------------------------------#
# IMPORT LIBS
#-----------------------------------------------------------------------------#
import json
import ollama
from typing import Callable
from .ollama_api import ollama_generator
#-----------------------------------------------------------------------------#
# FUNCTIONS
#-----------------------------------------------------------------------------#


# Setting default 
def build_generator(provider:str = "ollama", model_name:str="qwen:v1.0"):
    match provider.lower():
        case "ollama":
            return ollama_generator(model_name=model_name)
        case _:
            raise ValueError("Unsuported Provider")