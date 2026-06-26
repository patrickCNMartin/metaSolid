# -----------------------------------------------------------------------------#
# IMPORT LIBS
# -----------------------------------------------------------------------------#
from typing import Callable

import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity


# -----------------------------------------------------------------------------#
# FUNCTIONS
# -----------------------------------------------------------------------------#
def get_semantic_embeddings(embed_func: Callable, prompts: list) -> np.ndarray:
    # using this function for naming clarity
    return embed_func(prompts)


def add_field_context(metadata: list) -> tuple[list, list]:
    if not metadata:
        return [], []

    fields, contexts = zip(
        *(
            (k, f'The metadata field "{k}" means {v[1]}')
            for d in metadata
            for k, v in d.items()
        )
    )

    return list(fields), list(contexts)


def semantic_clusters(embeddings, threshold: float = 0.1) -> tuple:
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
    metadata: list,
    exclude_subject: list,
    exclusion_threshold: float = 0.7,
) -> dict:
    # Return meta data if no exclusion terms provided
    if not exclude_subject:
        return metadata
    # Get keys that are not semantically relevant
    fields, context = add_field_context(metadata)

    metadata_semantics = get_semantic_embeddings(embed_func, context)
    exclusion_semantics = get_semantic_embeddings(embed_func, exclude_subject)

    distance = cosine_similarity(
        exclusion_semantics, metadata_semantics
    )  # (n_subjects, n_keys)

    # Keep keys where NO exclusion subject exceeds the threshold
    keep_mask = ~(distance >= exclusion_threshold).any(axis=0)
    fields = np.array(fields)[keep_mask]

    stripped_metadata = [
        {k: v for k, v in d.items() if k in set(fields)} for d in metadata
    ]
    return stripped_metadata
