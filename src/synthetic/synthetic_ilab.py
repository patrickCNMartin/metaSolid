#-----------------------------------------------------------------------------#
# IMPORT LIBS
#-----------------------------------------------------------------------------#
import os
import argparse
from typing import Callable
from providers.generators import build_generator
#-----------------------------------------------------------------------------#
# CONFIG
#-----------------------------------------------------------------------------#
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen:v1.0")
#-----------------------------------------------------------------------------#
# UTIL FUNCTIONS
#-----------------------------------------------------------------------------#
def generate_label(generator_func:Callable[[str, bool], str | dict], label:str,n:int = 5) -> dict:
    base_promt = f'Provide {n} synonyms for the word "{label}". Respond ONLY with a JSON object containing a key "label" mapping to a list of strings.'
    response = generator_func(base_promt, return_json = True)
    return response

def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate Synthetic iLAB data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  python synthetic_ilab.py --out data/synthetic
        """,
    )
    parser.add_argument(
        "--out",
        required=True,
        type=str,
        help="Location where synthetic data should be saved.",
    )
#-----------------------------------------------------------------------------#
# GENERATE SYNTHETIC ILAB META DATA
#-----------------------------------------------------------------------------#
if __name__ == "__main__":
    args = parse_args()
    
    # Get provider specific generator function
    print(LLM_PROVIDER)
    print(MODEL_NAME)
    generator_func = build_generator(provider = LLM_PROVIDER, model_name = MODEL_NAME)

    # Testing some silly label stuff
    new_labs = generate_label(generator_func,"silly",10)
    print(new_labs)