from metasolid.harmonize import create_hierarchy, harmonize_to_target


def _generator(response):
    """Stub generator that always returns `response`."""

    def generate(prompt, return_json=True):
        return response

    return generate


def test_create_hierarchy_strips_code_fence():
    raw = "```yaml\nsample_type:\n  description: a sample\n```"
    assert (
        create_hierarchy(_generator(raw), {}) == "sample_type:\n  description: a sample"
    )


def test_create_hierarchy_preserves_literal_yaml_in_content():
    raw = "```yaml\nconfig_format:\n  description: yaml or json config\n```"
    out = create_hierarchy(_generator(raw), {})
    assert "yaml or json config" in out
    assert "```" not in out


def test_create_hierarchy_handles_unfenced_response():
    raw = "sample_type:\n  description: a sample"
    assert create_hierarchy(_generator(raw), {}) == raw


def test_harmonize_to_target_maps_a_record_onto_itself(records, one_hot_embed):
    record = records[0]
    harmonized, unmatched, unmatched_target = harmonize_to_target(
        one_hot_embed, record, record, semantic_threshold=0.99
    )
    assert harmonized == {k: [v] for k, v in record.items()}
    assert unmatched == unmatched_target == {}


def test_harmonize_to_target_below_threshold_matches_nothing(records, one_hot_embed):
    harmonized, unmatched, unmatched_target = harmonize_to_target(
        one_hot_embed, records[1], records[0], semantic_threshold=0.5
    )
    assert harmonized == {}
    assert unmatched == records[1]
    assert unmatched_target == records[0]
