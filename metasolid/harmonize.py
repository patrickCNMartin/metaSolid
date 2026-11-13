"""Name each cluster of fields with an LLM, and map records onto a target's fields."""

import re
from typing import Callable

import numpy as np
from scipy.spatial.distance import cdist

from metasolid.semantics import add_field_context


def harmonize_fields(
    generator_func: Callable, labels, fields, field_only: bool = True
) -> dict:
    """One harmonized label per cluster, merged into one dict."""
    fields = np.array(fields)
    harmonized_fields = {}
    for cl in np.unique(labels):
        prompt = prepare_harmonization_prompt(fields[labels == cl], field_only)
        harmonized_field = generator_func(prompt)
        print(f"Harmonized Field Label: {harmonized_field}")
        harmonized_fields.update(harmonized_field)
    return harmonized_fields


def prepare_harmonization_prompt(fields, field_only: bool = True) -> str:
    prompt = (
        f"Consider the following metadata fields and their context: "
        f"{' '.join(fields)} "
        f"Provide a single metadata field. "
        f"The term should cover all metadata fields provided above. "
        f"Use ONLY english terms. "
    )
    if field_only:
        return f"{prompt} Return ONLY the harmonized term. "
    return (
        f"{prompt} "
        f"Respond ONLY with a JSON object containing "
        f"a key mapping a single string. "
        f"The key is the new harmonized field label. "
        f"The value is a short (MAX 50 words) explanation of "
        f"the new harmonized field label. "
    )


def harmonize_to_target(
    embed_func: Callable, metadata: dict, target: dict, semantic_threshold: float = 0.8
):
    """Map each field onto its closest target field at cosine *similarity* >= threshold.

    Returns (harmonized, unmatched_metadata, unmatched_target).
    """
    fields, context = add_field_context([metadata])
    target_fields, target_context = add_field_context([target])

    similarity = 1 - cdist(embed_func(target_context), embed_func(context), "cosine")
    best_target_idx = similarity.argmax(axis=0)
    best_score = similarity[best_target_idx, range(len(fields))]
    matched = best_score >= semantic_threshold

    harmonized = {}
    for field, t_idx, is_match in zip(fields, best_target_idx, matched):
        if is_match:
            harmonized.setdefault(target_fields[t_idx], []).append(metadata[field])

    unmatched_metadata = {f: metadata[f] for f, m in zip(fields, matched) if not m}
    unmatched_target = {t: target[t] for t in target_fields if t not in harmonized}
    return harmonized, unmatched_metadata, unmatched_target


def create_hierarchy(
    generator_func: Callable, metadata: dict, max_depth: int = 2
) -> str:
    """A YAML hierarchy of the fields, written by the LLM, with code fences stripped."""
    prompt = (
        f"Read this json structured text. Create an appropriate hierarchy. "
        f"The hierarchy should represent metadata fields and "
        f"sub-categories within those fields. "
        f"Return the meta data field as a YAML structured document. "
        f"Field should be the YAML titles. "
        f"The description can be the field value. "
        f"The YAML hierarchy should not exceed a depth of {max_depth}. "
        f"{metadata}"
    )
    response = generator_func(prompt, return_json=False)
    # Strip fence lines only; a field or description may itself contain "yaml".
    response = re.sub(
        r"^\s*```[ \t]*[A-Za-z0-9_+-]*[ \t]*$", "", response, flags=re.MULTILINE
    )
    return response.strip()
