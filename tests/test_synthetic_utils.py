import sys
from pathlib import Path

# Ensure `src` is on sys.path so imports work when running pytest from project root
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from synthetic.synthetic_utils import (
    ablate_metadata,
    augment_context,
    flatten_dict,
    generate_label,
    update_context,
)


def test_flatten_dict_simple():
    nested = {"a": {"b": 1}, "c": 2}
    flat = flatten_dict(nested)
    assert flat == {"a.b": 1, "c": 2}


def test_ablate_metadata_length():
    meta = {"f1": 1, "f2": 2, "f3": 3, "f4": 4, "f5": 5}
    # ablation_frac=0.2 should keep 4 fields (5 - 1)
    ablated = ablate_metadata(meta, ablation_frac=0.2)
    assert len(ablated) == 4


def test_generate_label_and_augment_update_context_monkeypatched(monkeypatch):
    # Provide deterministic mocks for generator_func

    def mock_gen_label(prompt, return_json=True):
        assert return_json is True
        return {"label": "synonym_label"}

    def mock_gen_augment(prompt, return_json=True):
        assert return_json is True
        return {"label": "short explanation"}

    def mock_gen_update(prompt, return_json=False):
        # update_context calls with return_json=False
        assert return_json is False
        return "new context string"

    # Test generate_label
    res_label = generate_label(mock_gen_label, "test_label", n=1, context_promt="ctx")
    assert isinstance(res_label, str)
    assert res_label == "synonym_label"

    # Test augment_context
    res_aug = augment_context(mock_gen_augment, {"k": ["v1", "v2"]})
    assert isinstance(res_aug, dict)
    assert res_aug["label"] == "short explanation"

    # Test update_context
    res_update = update_context(mock_gen_update, "key", "value")
    assert isinstance(res_update, str)
    assert res_update == "new context string"
