# metaSolid/__init__.py
from .harmonize import harmonize_fields
from .semantics import add_field_context, get_semantic_embeddings, semantic_clusters

# Expose everything to the outside world
__all__ = [
    "get_semantic_embeddings",
    "add_field_context",
    "semantic_clusters",
    "harmonize_fields",
]
