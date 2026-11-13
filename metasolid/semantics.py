"""Field context sentences, clustering and exclusion over their embeddings."""

from typing import Callable

import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity


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
    """Average-linkage clusters cut at a cosine *distance* of `threshold`."""
    similarity_matrix = cosine_similarity(embeddings)
    distance_matrix = np.clip(1 - similarity_matrix, 0, 2)
    clusters = AgglomerativeClustering(
        metric="precomputed",
        linkage="average",
        distance_threshold=threshold,
        n_clusters=None,
        compute_distances=True,
    ).fit(distance_matrix)
    return clusters, distance_matrix


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
    similarity = cosine_similarity(embed_func(exclude_subject), embed_func(context))
    keep = set(np.array(fields)[~(similarity >= exclusion_threshold).any(axis=0)])
    return [{k: v for k, v in d.items() if k in keep} for d in metadata]
