import json
from pathlib import Path

import pytest
import yaml
from conftest import FIXTURES

from metasolid.__main__ import join_context, parse_args, read_records

ARGS = ["--metadata", "m.json", "--context", "c.json", "--output", "out"]


def test_parse_args_requires_metadata_context_and_output():
    with pytest.raises(SystemExit):
        parse_args(["--metadata", "m.json", "--output", "out"])


def test_parse_args_ok():
    args = parse_args(ARGS)
    assert args.metadata == Path("m.json")
    assert args.context == Path("c.json")
    assert args.render_report is False
    assert parse_args(ARGS + ["--render_report"]).render_report is True


def test_read_records_json_and_yaml_agree(tmp_path, service_requests):
    as_yaml = tmp_path / "requests.yaml"
    as_yaml.write_text(yaml.safe_dump(service_requests))
    from_json = read_records(FIXTURES / "service_requests.json")
    assert from_json == read_records(as_yaml) == service_requests


@pytest.mark.parametrize(
    "name, content, message",
    [
        ("r.csv", "a,b", "expected a .json"),
        ("r.json", '{"a": 1}', "expected a list of records"),
        ("r.json", '[{"a": {"b": 1}}]', "nested fields: \\['a'\\]"),
    ],
)
def test_read_records_refuses(tmp_path, name, content, message):
    path = tmp_path / name
    path.write_text(content)
    with pytest.raises(ValueError, match=message):
        read_records(path)


def test_join_context_pairs_value_and_meaning(records, service_requests):
    first = records[0]
    assert first["owner.email"] == [
        service_requests[0]["owner.email"],
        "Email address of the person who submitted the request.",
    ]
    assert [r.keys() for r in records] == [r.keys() for r in service_requests]


def test_join_context_refuses_a_field_without_meaning(service_requests, field_context):
    field_context = json.loads(json.dumps(field_context))
    del field_context[1]["status"]
    with pytest.raises(
        ValueError, match="record 1: fields without a meaning \\['status'\\]"
    ):
        join_context(service_requests, field_context)


def test_join_context_refuses_a_length_mismatch(service_requests, field_context):
    with pytest.raises(ValueError, match="5 records but 4"):
        join_context(service_requests, field_context[:4])
