#-----------------------------------------------------------------------------#
# IMPORT LIBS
#-----------------------------------------------------------------------------#
import random
from typing import Callable
#-----------------------------------------------------------------------------#
# FUCNTIONS
#-----------------------------------------------------------------------------#
def generate_label(generator_func:Callable[[str, bool], str | dict],
                   label:str,
                   n:int = 1,
                   context_promt : str = 'Biological Laboratory Services') -> dict:
    base_promt_set = [f'Provide {n} synonyms for the word "{label}".',
                  f'Change the spelling of "{label}".',
                  f'Provide {n} labels which have semantic relationship with the word "{label}".']
    label_style = random.choice(base_promt_set)
    base_promt = (f'Consider this context: {context_promt}'
                f'{label_style}'
                f'Respond ONLY with a JSON object containing a key "label" mapping a single string.'
                f'Only use english terms.')
    field_label = generator_func(base_promt, return_json = True)
    print(f'Label Conversion: {label} => {field_label["label"]}')
    return field_label["label"]

def augment_context(generator_func:Callable[[str,bool],str | dict],label:dict) -> dict:
    augmentation_prompt = (f'Provide a short explination for what {list(label.keys())[0]} means.'
                           f'Keep it to a maximum of 50 words.'
                           f'Consider that these terms are found in the context of biological lab services.'
                           f'Potential values assigned to this field can look like: {list(label.values())[0]}'
                           f'DO NOT return {list(label.values())[0]} in your response.'
                           f'Respond ONLY with a JSON object containing a key "label" mapping a single string.'
                           f'Only use english terms.')
    context_augmentation = generator_func(augmentation_prompt, return_json = True)
    print(f'Augmented Context: {context_augmentation['label']}')
    return context_augmentation

def ablate_metadata(metadata:dict, ablation_frac:float = 0.2) -> dict:
    n_fields = len(metadata) - (len(metadata)  * ablation_frac)
    keys = random.sample(list(metadata.keys()),int(n_fields))
    ablated_matadata = {k:v for k,v in metadata.items() if k in keys}
    return ablated_matadata

# Remember that this is only to create synthetic data so we can
# reduce flexibility since we are only using iLAB
def flatten_dict(metadata, parent_key='', sep='.') -> dict:
    flat_dict = {}
    for k, v in metadata.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            flat_dict.update(flatten_dict(v, new_key, sep=sep))
        else:
            flat_dict[new_key] = v
    return flat_dict

