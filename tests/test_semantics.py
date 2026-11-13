import numpy as np

from metasolid.semantics import add_field_context, semantic_clusters, semantic_stripping


def test_add_field_context_one_sentence_per_field(records):
    fields, contexts = add_field_context(records)
    assert len(fields) == len(contexts) == sum(len(r) for r in records)
    assert contexts[0] == (
        'The context of field "id" is: '
        "Unique number that identifies the service request in the booking system."
    )


def test_semantic_stripping_drops_fields_close_to_an_excluded_term(records):
    def embed(texts):
        return np.array([[1.0, 0.0] if "API" in t else [0.0, 1.0] for t in texts])

    stripped = semantic_stripping(embed, records, ["API"], exclusion_threshold=0.9)
    kept = {k for r in stripped for k in r}
    api_fields = {
        k for r in records for k, (_, meaning) in r.items() if "API" in meaning
    }
    assert api_fields and not kept & api_fields
    assert kept == {k for r in records for k in r} - api_fields


def test_semantic_clusters_groups_identical_vectors():
    clusters, distances = semantic_clusters(
        np.array([[1.0, 0.0], [1.0, 0.0], [0.0, 1.0]]), threshold=0.1
    )
    a, b, c = clusters.labels_
    assert a == b != c
    assert distances.shape == (3, 3)
