#-----------------------------------------------------------------------------#
# IMPORT LIBS
#-----------------------------------------------------------------------------#
import os
import argparse
from providers.generators import build_generator
from synthetic.synthetic_utils import generate_label
#-----------------------------------------------------------------------------#
# CONFIG
#-----------------------------------------------------------------------------#
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen:v1.0")
#-----------------------------------------------------------------------------#
# UTIL FUNCTIONS
#-----------------------------------------------------------------------------#
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
        "--metadata",
        required=True,
        type=str,
        help="Location where meta data is stored.",
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
    print(f'Using:LLM_PROVIDER')
    print(MODEL_NAME)
    generator_func = build_generator(provider = LLM_PROVIDER, model_name = MODEL_NAME)

    # Testing some silly label stuff
    new_labs = generate_label(generator_func,"silly",10)
    print(new_labs)