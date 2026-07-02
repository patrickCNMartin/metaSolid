# -----------------------------------------------------------------------------#
# IMPORT LIBS
# -----------------------------------------------------------------------------#
import re
from typing import Callable

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from .semantics import add_field_context, get_semantic_embeddings


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


def harmonize_to_target(
    embed_func: Callable, metadata: dict, target: dict, semantic_threshold: float = 0.8
):
    fields, context = add_field_context([metadata])
    target_fields, target_context = add_field_context([target])

    metadata_semantics = get_semantic_embeddings(embed_func, context)
    target_semantics = get_semantic_embeddings(embed_func, target_context)

    similarity = cosine_similarity(target_semantics, metadata_semantics)

    best_target_idx = similarity.argmax(axis=0)
    best_score = similarity[best_target_idx, range(len(fields))]
    matched = best_score >= semantic_threshold

    harmonized = {}
    for field, t_idx, is_match in zip(fields, best_target_idx, matched):
        if not is_match:
            continue
        t_key = target_fields[t_idx]
        harmonized.setdefault(t_key, []).append(metadata[field])

    unmatched_metadata = {f: metadata[f] for f, m in zip(fields, matched) if not m}
    unmatched_target = {t: target[t] for t in target_fields if t not in harmonized}

    return harmonized, unmatched_metadata, unmatched_target


def create_hiarchy(generator_func: Callable, metadata: dict, max_depth: int = 2):
    prompt = (
        f"Read this json structured text. Create an appropriate hiarchy. "
        f"The hiarchy should represent metadata fields and "
        f"sub-categories within those fields. "
        f"Return the meta data field as a YAML structured document. "
        f"Field should be the YAML titles."
        f"The description can be the field value. "
        f"The YAML hiarchy should not exceed a dept of {max_depth}"
        f"{metadata}"
    )
    response = generator_func(prompt, return_json=False)
    response = re.sub("```", "", response)
    response = re.sub("yaml", "", response)
    return response
