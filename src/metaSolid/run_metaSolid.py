#-----------------------------------------------------------------------------#
# IMPORT LIBS
#-----------------------------------------------------------------------------#
import json
import os
import argparse
import matplotlib.pyplot as plt
from metaSolid.semantics import (get_semantic_embeddings,semantic_clusters,semantic_stripping,add_field_context)
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
    

    #import pdb;pdb.set_trace()
    filtered_metadata = semantic_stripping(metadata,['API','url','HTTP','git'],0.6)
    # adding context to key for semantic embeddings and pull associated key
    # I think this could be improved. The aim was to make it a bit more flexible
    # but I end up going back and forth with stuff - wasted compute
    context_fields = add_field_context(filtered_metadata)
    context = [context[1] for context in context_fields]
    fields = [field[0] for field in context_fields]
    embeddings = get_semantic_embeddings(prompts = context)
    clusters, distance_matrix = semantic_clusters(embeddings=embeddings)
    
    #import pdb;pdb.set_trace()
    fig, ax = plt.subplots(figsize=(23, 23))
    plot_dendrogram_and_heatmap(fields, clusters, distance_matrix,fig=fig)
    ax.tick_params(axis='x', labelsize=8)
    plt.savefig(f"{args.output}/semantic_clusters.png",dpi=300, bbox_inches='tight')
    #plt.show()

    fig, ax = plt.subplots(figsize=(12, 6))
    plot_word_cloud_umap(fields, embeddings, ax=ax)
    ax.tick_params(axis='x', labelsize=8)
    plt.tight_layout()
    plt.savefig(f"{args.output}/semantic_word_cloud.png",dpi=300, bbox_inches='tight')
    #plt.show()