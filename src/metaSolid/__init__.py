# metaSolid/__init__.py
from .harmonize import create_hiarchy, harmonize_fields
from .semantics import add_field_context, get_semantic_embeddings, semantic_clusters
from .visualize import plot_dendrogram_and_heatmap, plot_word_cloud_umap

# Expose everything to the outside world
__all__ = [
    "get_semantic_embeddings",
    "add_field_context",
    "semantic_clusters",
    "harmonize_fields",
    "create_hiarchy",
    "plot_word_cloud_umap",
    "plot_dendrogram_and_heatmap",
]
