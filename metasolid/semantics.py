"""Field context sentences, clustering and exclusion over their embeddings."""

from typing import Callable

import numpy as np
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import cdist, pdist, squareform


def add_field_context(metadata: list[dict]) -> tuple[list, list]:
    """Field names, and one sentence per field of records {field: [value, meaning]}."""
    if not metadata:
        return [], []
    fields, contexts = zip(
        *(
            (k, f'The context of field "{k}" is: {v[1]}')
            for d in metadata
            for k, v in d.items()
        )
    )
    return list(fields), list(contexts)


def semantic_clusters(embeddings, threshold: float = 0.1) -> tuple:
    """Average-linkage clusters cut at a cosine *distance* of `threshold`.

    Returns (label per field, linkage matrix, square distance matrix).
    """
    distances = np.clip(pdist(embeddings, "cosine"), 0, 2)
    tree = linkage(distances, "average")
    return fcluster(tree, threshold, "distance"), tree, squareform(distances)


def semantic_stripping(
    embed_func: Callable,
    metadata: list[dict],
    exclude_subject: list,
    exclusion_threshold: float = 0.7,
) -> list[dict]:
    """Drop each field whose context is `exclusion_threshold` similar to any term."""
    if not exclude_subject:
        return metadata
    fields, context = add_field_context(metadata)
    similarity = 1 - cdist(embed_func(exclude_subject), embed_func(context), "cosine")
    keep = set(np.array(fields)[~(similarity >= exclusion_threshold).any(axis=0)])
    return [{k: v for k, v in d.items() if k in keep} for d in metadata]
