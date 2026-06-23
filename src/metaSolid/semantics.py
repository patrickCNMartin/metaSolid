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


def build_semantic_array(metadata: list, model_name:str = "nomic-embed-text"):
    unique_keys = list({k for d in metadata for k in d.keys()})
    embeddings = get_semantic_embeddings(unique_keys, model_name = model_name)
    return unique_keys, embeddings


def semantic_clusters(embeddings, threshold: float = 0.1):
    similarity_matrix = cosine_similarity(embeddings)
    distance_matrix = np.clip(1 - similarity_matrix, 0, 2)
    clusters = AgglomerativeClustering(
        metric='precomputed',
        linkage='average',
        distance_threshold=threshold,
        n_clusters=None,
        compute_distances=True
    ).fit(distance_matrix)
    return clusters, distance_matrix

def semantic_stripping(metadata: list, exclude_subject: list, 
                       exclusion_threshold: float = 0.1, 
                       model_name: str = "nomic-embed-text"):
    unique_keys = np.array(metadata)
    
    metadata_semantics = get_semantic_embeddings(unique_keys.tolist(), model_name=model_name)
    exclusion_semantics = get_semantic_embeddings(exclude_subject, model_name=model_name)
    
    distance = cosine_similarity(exclusion_semantics, metadata_semantics)  # (n_subjects, n_keys)
    
    # Keep keys where NO exclusion subject exceeds the threshold
    keep_mask = ~(distance >= exclusion_threshold).any(axis=0)
    
    return unique_keys[keep_mask]