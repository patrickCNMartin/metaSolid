#-----------------------------------------------------------------------------#
# IMPORT LIBS
#-----------------------------------------------------------------------------#
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram
import umap
import numpy as np

#-----------------------------------------------------------------------------#
# FUNCTIONS
#-----------------------------------------------------------------------------#

def plot_dendrogram_from_clustering(unique_keys, model, threshold: float = 0.2, ax = None):
    if ax is None:
        ax = plt.gca()

    counts = np.zeros(model.children_.shape[0])
    n_samples = len(unique_keys)
    for i, merge in enumerate(model.children_):
        counts[i] = sum(1 if c < n_samples else counts[c - n_samples] for c in merge)

    Z = np.column_stack([model.children_, model.distances_, counts])

    dendrogram(Z, labels=unique_keys, color_threshold=threshold, leaf_rotation=90, ax=ax)
    return ax


def plot_word_cloud_umap(unique_keys, embeddings, n_neighbors: int = 5, min_dist: float = 0.3, ax=None):
    if ax is None:
        ax = plt.gca()
    reducer = umap.UMAP(n_neighbors=n_neighbors, min_dist=min_dist, metric='cosine')
    coords = reducer.fit_transform(embeddings)
    ax.scatter(coords[:, 0], coords[:, 1], alpha=0.3, s=10)
    for label, (x, y) in zip(unique_keys, coords):
        ax.text(x, y, label, fontsize=9, alpha=0.8)
    return ax