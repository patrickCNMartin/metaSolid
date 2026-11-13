"""The fixtures are made up: 5 requests, a meaning for every field, example.org only."""

import re

from conftest import FIXTURES

EMAIL = re.compile(r"[\w.+-]+@([\w-]+(?:\.[\w-]+)+)")
URL_HOST = re.compile(r"https?://([^/\s\"']+)")


def test_five_requests_and_a_meaning_for_every_field(service_requests, field_context):
    assert len(service_requests) == len(field_context) == 5
    for request, context in zip(service_requests, field_context):
        assert request.keys() == context.keys()


def test_field_names_differ_between_requests_and_some_are_shared(service_requests):
    names = [frozenset(r) for r in service_requests]
    assert len(set(names)) == 5
    assert any(a & b for i, a in enumerate(names) for b in names[i + 1 :])


def test_only_example_org_addresses():
    text = "".join(p.read_text() for p in sorted(FIXTURES.glob("*")))
    emails = EMAIL.findall(text)
    assert emails, "no email found: the check below would pass on nothing"
    assert set(emails) == {"example.org"}
    assert all(h.endswith("example.org") for h in URL_HOST.findall(text))
