#-----------------------------------------------------------------------------#
# IMPORT LIBS
#-----------------------------------------------------------------------------#
import os
import argparse
import json
from providers.generators import build_generator
from synthetic.synthetic_utils import (generate_label, ablate_metadata,flatten_dict,augment_context)
#-----------------------------------------------------------------------------#
# CONFIG
#-----------------------------------------------------------------------------#
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
GEN_MODEL = os.getenv("MODEL", "qwen:v0.0.1")
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
        "--output",
        required=True,
        type=str,
        help="Location where synthetic data should be saved.",
    )
    return parser.parse_args() 
#-----------------------------------------------------------------------------#
# GENERATE SYNTHETIC ILAB META DATA
#-----------------------------------------------------------------------------#
if __name__ == "__main__":
    args = parse_args()
    # Get provider specific generator function
    # This generator function is essentially what wraps the LLM api into a single
    # Function call. It gets a prompt and bool (return json on true).
    # This function is then parse to what ever subfunction needs a generator.
    print(f'Using:{LLM_PROVIDER} with {GEN_MODEL}')
    generator_func = build_generator(provider = LLM_PROVIDER, model_name = GEN_MODEL)
    # Loading previously computed fuzzy request just in case.
    if os.path.exists(f'{args.output}/fuzzy_service_request.json'):
        with open(f'{args.output}/fuzzy_service_request.json') as f:
            fuzzy_requests = json.load(f)
    else :
        with open(args.metadata) as f:
            metadata = json.load(f)

        # First we flatten the request before parsing it to the generator functions.
        requests = [flatten_dict(md) for md in metadata]
        requests = requests[:5] # only take 5 requests for development purposes
        context_augmentation = [
            {k:augment_context(generator_func,{k:v})['label'] for k,v in req.items()}
            for req in requests
        ]
        with open(f'{args.output}/context_augmentation.json', 'w') as f:
            json.dump(context_augmentation,f)

        fuzzy_requests = [
            {generate_label(generator_func, k, 1,ck): [v,cv] for (k,v),(ck,cv) in zip(req.items(),cont.items())}
            for req,cont in zip(requests,context_augmentation)
        ]
        with open(f'{args.output}/fuzzy_service_request.json', 'w') as f:
            json.dump(fuzzy_requests,f)
    
    
    
    ablated_requests = [ablate_metadata(fr, 0.1) for fr in fuzzy_requests]
    
    with open(f'{args.output}/fuzzy_ablated_requests.json', 'w') as f:
        json.dump(ablated_requests, f)