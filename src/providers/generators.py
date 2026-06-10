#-----------------------------------------------------------------------------#
# IMPORT LIBS
#-----------------------------------------------------------------------------#
from .ollama_api import ollama_generator
#-----------------------------------------------------------------------------#
# FUNCTIONS
#-----------------------------------------------------------------------------#


# Setting default base on what I use for now but will clean it up later
def build_generator(provider:str = "ollama", model_name:str="qwen:v1.0"):
    match provider.lower():
        case "ollama":
            return ollama_generator(model_name=model_name)
        case _:
            raise ValueError("Unsuported Provider")