# metaSolid/__init__.py
from .semantics import (build_semantic_array,semantic_clusters)
# Expose everything to the outside world
__all__ = ["build_semantic_array",
           "semantic_clusters"]