import json
from pathlib import Path

import numpy as np
import pytest

from metasolid.__main__ import join_context

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def service_requests():
    return json.loads((FIXTURES / "service_requests.json").read_text())


@pytest.fixture
def field_context():
    return json.loads((FIXTURES / "field_context.json").read_text())


@pytest.fixture
def records(service_requests, field_context):
    return join_context(service_requests, field_context)


@pytest.fixture
def one_hot_embed():
    """Stub embedder: each distinct text gets its own axis, the same on every call."""
    index = {}

    def embed(texts):
        texts = [texts] if isinstance(texts, str) else texts
        for t in texts:
            index.setdefault(t, len(index))
        vectors = np.zeros((len(texts), 256))
        for row, t in enumerate(texts):
            vectors[row, index[t]] = 1.0
        return vectors

    return embed
