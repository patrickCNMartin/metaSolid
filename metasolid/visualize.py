"""Dendrogram + distance heatmap of the fields."""

import matplotlib.pyplot as plt
import numpy as np
from scipy.cluster.hierarchy import dendrogram


def plot_dendrogram_and_heatmap(
    unique_keys, tree, distance_matrix, threshold: float = 0.2, fig=None
):
    if fig is None:
        fig = plt.gcf()

    gs = fig.add_gridspec(
        2, 2, width_ratios=[3, 0.2], height_ratios=[1, 3], hspace=0.02, wspace=0.02
    )
    ax_dendro = fig.add_subplot(gs[0, 0])
    ax_heat = fig.add_subplot(gs[1, 0])
    ax_cbar = fig.add_subplot(gs[0, 1])

    ddata = dendrogram(
        tree,
        labels=unique_keys,
        color_threshold=threshold,
        leaf_rotation=90,
        ax=ax_dendro,
    )

    order = ddata["leaves"]
    D_ordered = distance_matrix[np.ix_(order, order)]
    ordered_labels = [unique_keys[i] for i in order]

    im = ax_heat.imshow(D_ordered, aspect="auto", cmap="viridis")
    ax_heat.set_xticks(range(len(order)), ordered_labels, rotation=90)
    ax_heat.set_yticks(range(len(order)), ordered_labels)

    plt.colorbar(im, cax=ax_cbar)

    return fig
