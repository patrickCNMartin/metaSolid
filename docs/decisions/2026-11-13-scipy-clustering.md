---
date: 2026-11-13
title: Clustering and cosine similarity move from scikit-learn to scipy
decided_by: [human:patrickCNMartin, claude-code/claude-opus-5-5]
---

**Decided:** `semantic_clusters` uses scipy's `linkage(..., "average")` and
`fcluster(..., "distance")` and returns the labels, the linkage matrix and the square distance
matrix. Cosine similarity is `1 - cdist(..., "cosine")`. The dendrogram draws the linkage matrix
directly. scikit-learn, joblib and threadpoolctl leave the dependencies.
**Why:** scipy was already a dependency and does the same clustering; one fewer package. At nixpkgs
3ec6363 scikit-learn had no cached aarch64-linux build, which blocked the arm64 image. Measured on
the fixtures with nomic-embed-text: identical partitions to scikit-learn at thresholds 0.1, 0.2,
0.3 and 0.4 (59, 25, 7 and 1 clusters).
**Cost:** `fcluster` keeps a merge at exactly the threshold, where scikit-learn split it; equal
floats there are not expected.
