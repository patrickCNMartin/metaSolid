#-----------------------------------------------------------------------------#
# IMPORT LIBS
#-----------------------------------------------------------------------------#
import json
import ollama
from sklearn.cluster import AgglomerativeClustering
#-----------------------------------------------------------------------------#
# FUNCTIONS
#-----------------------------------------------------------------------------#
def get_semantic_embeddings(prompt:str, model_name:str = "nomic-embed-text"):
    response = ollama.embeddings(
            model=model_name,
            prompt = prompt,
            stream=False
        )
    return response['embedding'] # Will this always return a 768 vector regardless of prompt size?


def semantic_clusters(embeddings, cluster_type:str = "hclust"):
    return 0