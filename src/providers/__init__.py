# providers/__init__.py
from .ollama_api import ollama_generator
# Expose everything to the outside world
__all__ = ["ollama_generator"]