# metaSolid/__init__.py
from .semantics import (get_semantic_embeddings,add_field_context,semantic_clusters)
# Expose everything to the outside world
__all__ = ["get_semantic_embeddings",
           "add_field_context",
           "semantic_clusters"]