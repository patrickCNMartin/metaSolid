# -----------------------------------------------------------------------------#
# IMPORT LIBS
# -----------------------------------------------------------------------------#
import argparse
import json
import yaml
import os
from pathlib import Path

import matplotlib.pyplot as plt
from dotenv import load_dotenv

from metaSolid.harmonize import (harmonize_fields,create_hiarchy)
from metaSolid.semantics import (
    add_field_context,
    get_semantic_embeddings,
    semantic_clusters,
    semantic_stripping,
)
from metaSolid.visualize import plot_dendrogram_and_heatmap, plot_word_cloud_umap
from providers.embedders import build_embedder
from providers.generators import build_generator

# -----------------------------------------------------------------------------#
# CONFIG
# -----------------------------------------------------------------------------#
# should probably clean this....
dotenv_path = (Path(__file__).resolve().parent / "../../env/.env").resolve()
load_dotenv(dotenv_path=dotenv_path)

GEN_PROVIDER = os.getenv("GEN_PROVIDER", "ollama")
GEN_MODEL = os.getenv("GEN_MODEL", "qwen:v0.0.1")
GEN_ENDPOINT = os.getenv("GEN_ENDPOINT", "http://localhost:11434/v1/chat/completions")
GEN_API_KEY = os.getenv("GEN_API_KEY", None)

EMBED_PROVIDER = os.getenv("EMBED_PROVIDER", "ollama")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
EMBED_ENDPOINT = os.getenv("EMBED_ENDPOINT", "http://localhost:11434/v1/embeddings")
EMBED_API_KEY = os.getenv("EMBED_API_KEY", None)

SEMANTIC_THRESHOLD = float(os.getenv("SEMANTIC_THRESHOLD", 0.2))
SEMANTIC_EXCLUSION = float(os.getenv("SEMANTIC_EXCLUSION", 0.5))

et = os.getenv("SEMANTIC_EXCLUSION_TERMS")
EXCLUSION_TERMS = json.loads(et) if et else []


# -----------------------------------------------------------------------------#
# UTIL FUNCTIONS
# -----------------------------------------------------------------------------#
def parse_args():
    parser = argparse.ArgumentParser(
        description="METASOLID: Harmonize Meta data Labels",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  python metaSolid.py --metadata data/fuzzy_ablated_requests --output data/
        """,
    )
    parser.add_argument(
        "--metadata",
        required=True,
        type=str,
        help="Location where meta data is stored.",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=str,
        help="Location where synthetic data should be saved.",
    )
    return parser.parse_args()


# -----------------------------------------------------------------------------#
# HARMONIZE META DATA LABELS
# -----------------------------------------------------------------------------#

if __name__ == "__main__":
    args = parse_args()
    # Get provider specific generator function
    # This generator function is essentially what wraps the LLM api into a single
    # Function call. It gets a prompt and bool (return json on true).
    # This function is then parse to what ever subfunction needs a generator.
    print(f"Using:{GEN_PROVIDER} with {GEN_MODEL}")
    generator_func = build_generator(
        provider=GEN_PROVIDER,
        model_name=GEN_MODEL,
        api_key=GEN_API_KEY,
        endpoint=GEN_ENDPOINT,
    )
    print(f"Using:{EMBED_PROVIDER} with {EMBED_MODEL}")
    embedder_func = build_embedder(
        provider=EMBED_PROVIDER,
        model_name=EMBED_MODEL,
        api_key=EMBED_API_KEY,
        endpoint=EMBED_ENDPOINT,
    )

    # Load meta data - atm I'm assuming that it is a list of dicts
    with open(f"{args.metadata}") as f:
        metadata = json.load(f)

    # first we filter the mete data base on the exclusion terms
    # For the most part we don't care about API specific terms
    filtered_metadata = semantic_stripping(
        embedder_func,
        metadata=metadata,
        exclude_subject=EXCLUSION_TERMS,
        exclusion_threshold=SEMANTIC_EXCLUSION,
    )
    fields, context_fields = add_field_context(filtered_metadata)
    embeddings = get_semantic_embeddings(embedder_func, prompts=context_fields)
    clusters, distance_matrix = semantic_clusters(
        embeddings=embeddings, threshold=SEMANTIC_THRESHOLD
    )

    # Plot semantic clusters
    fig, ax = plt.subplots(figsize=(23, 23))
    plot_dendrogram_and_heatmap(fields, clusters, distance_matrix, fig=fig)
    ax.tick_params(axis="x", labelsize=8)
    plt.savefig(f"{args.output}/semantic_clusters.png", dpi=300, bbox_inches="tight")

    fig, ax = plt.subplots(figsize=(12, 6))
    plot_word_cloud_umap(fields, embeddings, ax=ax)
    ax.tick_params(axis="x", labelsize=8)
    plt.tight_layout()
    plt.savefig(f"{args.output}/semantic_word_cloud.png", dpi=300, bbox_inches="tight")

    # Harmonize meta data labels
    harmonized_fields = harmonize_fields(
        generator_func, clusters, context_fields, field_only=False
    )
    with open(f"{args.output}/harmonzied_metadata_fields.json", "w") as f:
        json.dump(harmonized_fields, f)
    
    # Create YAML hiarchy file
    hiarchy_file = create_hiarchy(
        generator_func, harmonized_fields, max_depth = 2
    )
    with open(f"{args.output}/hiarchy_metadata_fields.yaml", "w") as f:
        f.write(hiarchy_file)
