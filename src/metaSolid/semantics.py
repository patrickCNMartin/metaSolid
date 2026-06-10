#-----------------------------------------------------------------------------#
# IMPORT LIBS
#-----------------------------------------------------------------------------#
import ollama
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import AgglomerativeClustering
#-----------------------------------------------------------------------------#
# FUNCTIONS
#-----------------------------------------------------------------------------#
def get_semantic_embeddings(prompts: list, model_name: str = "nomic-embed-text"):
    response = ollama.embed(
        model=model_name,
        input=prompts
    )
    return np.array(response['embeddings'], dtype=np.float32)


def build_semantic_array(metadata: list):
    unique_keys = list({k for d in metadata for k in d.keys()})
    embeddings = get_semantic_embeddings(unique_keys)
    return unique_keys, embeddings


def semantic_clusters(embeddings, threshold: float = 0.1):
    similarity_matrix = cosine_similarity(embeddings)
    clusters = AgglomerativeClustering(
        metric='precomputed',
        linkage='average',
        distance_threshold=threshold,
        n_clusters=None,
        compute_distances=True  # <-- add this
    ).fit(1 - similarity_matrix)
    return clusters