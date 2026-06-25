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
def get_semantic_embeddings(prompts: list, model_name: str = "nomic-embed-text")-> np.array:
    response = ollama.embed(
        model=model_name,
        input=prompts
    )
    return np.array(response['embeddings'], dtype=np.float32)

def add_field_context(metadata:str) -> list:
    context_fields = [[k,f'The metadata field "{k}" means {v[1]}'] for d in metadata for k,v in d.items()]
    return context_fields




def semantic_clusters(embeddings, threshold: float = 0.1)-> tuple:
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
                       exclusion_threshold: float = 0.7, 
                       model_name: str = "nomic-embed-text")->dict:
    # Get keys that are not semantically relevant
    
    context_fields = add_field_context(metadata)
    context = [context[1] for context in context_fields]
    metadata_semantics = get_semantic_embeddings(context, model_name=model_name)
    exclusion_semantics = get_semantic_embeddings(exclude_subject, model_name=model_name)
    
    distance = cosine_similarity(exclusion_semantics, metadata_semantics)  # (n_subjects, n_keys)
    
    # Keep keys where NO exclusion subject exceeds the threshold
    keep_mask = ~(distance >= exclusion_threshold).any(axis=0)
    keep_fields = [f[0] for f in context_fields]
    keep_fields = np.array(keep_fields)[keep_mask]

    stripped_metadata = [
        {k: v for k, v in d.items() if k in set(keep_fields)}
        for d in metadata
    ]
    return stripped_metadata