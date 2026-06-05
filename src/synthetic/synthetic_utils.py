#-----------------------------------------------------------------------------#
# IMPORT LIBS
#-----------------------------------------------------------------------------#
import random
from typing import Callable
#-----------------------------------------------------------------------------#
# FUCNTIONS
#-----------------------------------------------------------------------------#
def generate_label(generator_func:Callable[[str, bool], str | dict], label:str,n:int = 5) -> dict:
    base_promt = (f'Provide {n} synonyms for the word "{label}".'
                  f'Respond ONLY with a JSON object containing a key "label" mapping to a list of strings.')
    response = generator_func(base_promt, return_json = True)
    return response


def ablate_metadata(metadata:dict, ablation_frac:float = 0.2) -> dict:
    n_fields = len(metadata) - (len(metadata)  * ablation_frac)
    keys = random.sample(metadata.keys(),n_fields)
    ablated_matadata = {k:v for k,v in metadata.items if k in keys}
    return ablated_matadata


def get_labels_from_json(metadata, parent_key='', sep='.') -> dict:
    items = {}
    for k, v in metadata.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(get_labels_from_json(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items

