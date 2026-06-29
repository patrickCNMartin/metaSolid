# -----------------------------------------------------------------------------#
# IMPORT LIBS
# -----------------------------------------------------------------------------#
from typing import Callable

import numpy as np


# -----------------------------------------------------------------------------#
# FUNCTIONS
# -----------------------------------------------------------------------------#
def harmonize_fields(
    generator_func: Callable, cluster, fields, field_only: bool = True
):
    cluster_labels = cluster.labels_
    fields = np.array(fields)
    harmonized_fields = {}
    for cl in set(cluster_labels):
        local_fields = fields[cluster_labels == cl]
        field_prompt = prepare_harmonization_prompt(local_fields, field_only)
        harmonized_field = generator_func(field_prompt)
        print(f"Harmonized Field Label: {harmonized_field}")
        harmonized_fields.update(harmonized_field)
    return harmonized_fields


def prepare_harmonization_prompt(fields, field_only: bool = True):
    textified = " ".join(fields)
    prompt = (
        f"Consider the following metadata fields and their context: "
        f"{textified} "
        f"Provide a single metadata field. "
        f"The term should cover all metadata fields provided above. "
        f"Use ONLY english terms. "
    )
    if field_only:
        prompt = f"{prompt} Return ONLY the harmonized term. "
    else:
        prompt = (
            f"{prompt} "
            f"Respond ONLY with a JSON object containing "
            f"a key mapping a single string. "
            f"The key is the new harmonized field label. "
            f"The value is a short (MAX 50 words) explination of "
            f"the new harmonized field label. "
        )
    return prompt
