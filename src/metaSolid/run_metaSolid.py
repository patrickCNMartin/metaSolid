#-----------------------------------------------------------------------------#
# IMPORT LIBS
#-----------------------------------------------------------------------------#
import json
import os
import argparse
import matplotlib.pyplot as plt
from metaSolid.semantics import (build_semantic_array,semantic_clusters,semantic_stripping)
from metaSolid.visualize import (plot_dendrogram_and_heatmap,plot_word_cloud_umap)

#-----------------------------------------------------------------------------#
# CONFIG
#-----------------------------------------------------------------------------#
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
GEN_MODEL = os.getenv("GEN_MODEL", "qwen:v0.0.1")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
SEMANTIC_THRESHOLD = float(os.getenv("SEMANTIC_THRESHOLD", 0.2))

#-----------------------------------------------------------------------------#
# UTIL FUNCTIONS
#-----------------------------------------------------------------------------#
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

#-----------------------------------------------------------------------------#
# HARMONIZE META DATA LABELS
#-----------------------------------------------------------------------------#

if __name__ == "__main__":
    args = parse_args()
    # Get provider specific generator function
    # This generator function is essentially what wraps the LLM api into a single
    # Function call. It gets a prompt and bool (return json on true).
    # This function is then parse to what ever subfunction needs a generator.
    print(f'Using:{LLM_PROVIDER} with {EMBED_MODEL}')

    # Load meta data - atm I'm assuming that it is a list of dicts
    with open(f'{args.metadata}') as f:
        metadata = json.load(f)
    
    unique_fields,embeddings = build_semantic_array(metadata = metadata)
    print(f'Unique Fields: {unique_fields}')
    clusters, distance_matrix = semantic_clusters(embeddings=embeddings)
    strip = semantic_stripping(unique_fields,['API','url'],0.6)
    import pdb;pdb.set_trace()
    fig, ax = plt.subplots(figsize=(20, 20))
    plot_dendrogram_and_heatmap(unique_fields, clusters, distance_matrix,fig=fig)
    ax.tick_params(axis='x', labelsize=8)
    plt.savefig(f"{args.output}/semantic_clusters.png",dpi=300, bbox_inches='tight')
    #plt.show()

    fig, ax = plt.subplots(figsize=(12, 6))
    plot_word_cloud_umap(unique_fields, embeddings, ax=ax)
    ax.tick_params(axis='x', labelsize=8)
    plt.tight_layout()
    plt.savefig(f"{args.output}/semantic_word_cloud.png",dpi=300, bbox_inches='tight')
    #plt.show()