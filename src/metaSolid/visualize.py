# -----------------------------------------------------------------------------#
# IMPORT LIBS
# -----------------------------------------------------------------------------#
import matplotlib.pyplot as plt
import numpy as np
import umap
from scipy.cluster.hierarchy import dendrogram

# -----------------------------------------------------------------------------#
# FUNCTIONS
# -----------------------------------------------------------------------------#


def plot_dendrogram_and_heatmap(
    unique_keys, model, distance_matrix, threshold: float = 0.2, fig=None
):
    if fig is None:
        fig = plt.gcf()

    gs = fig.add_gridspec(
        2, 2, width_ratios=[3, 0.2], height_ratios=[1, 3], hspace=0.02, wspace=0.02
    )
    ax_dendro = fig.add_subplot(gs[0, 0])
    ax_heat = fig.add_subplot(gs[1, 0])
    ax_cbar = fig.add_subplot(gs[0, 1])  # or gs[1,1] — your call

    counts = np.zeros(model.children_.shape[0])
    n = len(unique_keys)
    for i, merge in enumerate(model.children_):
        counts[i] = sum(1 if c < n else counts[c - n] for c in merge)

    Z = np.column_stack([model.children_, model.distances_, counts])
    ddata = dendrogram(
        Z,
        labels=unique_keys,
        color_threshold=threshold,
        leaf_rotation=90,
        ax=ax_dendro
    )

    order = ddata["leaves"]
    D_ordered = distance_matrix[np.ix_(order, order)]
    ordered_labels = [unique_keys[i] for i in order]

    im = ax_heat.imshow(D_ordered, aspect="auto", cmap="viridis")
    ax_heat.set_xticks(range(n))
    ax_heat.set_yticks(range(n))
    ax_heat.set_xticklabels(ordered_labels, rotation=90)
    ax_heat.set_yticklabels(ordered_labels)

    plt.colorbar(im, cax=ax_cbar)

    return fig


def plot_word_cloud_umap(
    unique_keys, embeddings, n_neighbors: int = 5, min_dist: float = 0.3, ax=None
):
    if ax is None:
        ax = plt.gca()
    reducer = umap.UMAP(n_neighbors=n_neighbors, min_dist=min_dist, metric="cosine")
    coords = reducer.fit_transform(embeddings)
    ax.scatter(coords[:, 0], coords[:, 1], alpha=0.3, s=10)
    for label, (x, y) in zip(unique_keys, coords):
        ax.text(x, y, label, fontsize=9, alpha=0.8)
    return ax
