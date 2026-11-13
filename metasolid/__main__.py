"""metaSolid: harmonize metadata field names. All config is read here."""

import argparse
import json
import os
from pathlib import Path

import matplotlib.pyplot as plt
import yaml
from dotenv import load_dotenv

from metasolid.harmonize import create_hierarchy, harmonize_fields, harmonize_to_target
from metasolid.providers import build_embedder, build_generator
from metasolid.report import check_pdf_tools, render_pdf, write_report
from metasolid.semantics import add_field_context, semantic_clusters, semantic_stripping
from metasolid.visualize import plot_dendrogram_and_heatmap


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="python -m metasolid",
        description="Harmonize metadata field names.",
        epilog="example: python -m metasolid --metadata requests.json "
        "--context context.json --output out/ --render_report",
    )
    parser.add_argument(
        "--metadata", required=True, type=Path, help="Flat records, .json or .yaml."
    )
    parser.add_argument(
        "--context",
        required=True,
        type=Path,
        help="The meaning of each field, one {field: meaning} per record, same order.",
    )
    parser.add_argument("--output", required=True, type=Path, help="Output directory.")
    parser.add_argument(
        "--render_report",
        action="store_true",
        help="Also render report.md to report.pdf (needs pandoc and typst).",
    )
    return parser.parse_args(argv)


def read_records(path: Path) -> list[dict]:
    """A list of flat records from .json, .yaml or .yml."""
    with open(path, encoding="utf-8") as f:
        match path.suffix.lower():
            case ".json":
                data = json.load(f)
            case ".yaml" | ".yml":
                data = yaml.safe_load(f)
            case _:
                raise ValueError(f"{path}: expected a .json, .yaml or .yml file")
    if not isinstance(data, list) or not all(isinstance(r, dict) for r in data):
        raise ValueError(f"{path}: expected a list of records")
    nested = sorted({k for r in data for k, v in r.items() if isinstance(v, dict)})
    if nested:
        raise ValueError(f"{path}: records must be flat; nested fields: {nested}")
    return data


def join_context(records: list[dict], contexts: list[dict]) -> list[dict]:
    """Pair each value with its field's meaning: {field: [value, meaning]}."""
    if len(records) != len(contexts):
        raise ValueError(f"{len(records)} records but {len(contexts)} context entries")
    for i, (record, context) in enumerate(zip(records, contexts)):
        if record.keys() != context.keys():
            raise ValueError(
                f"record {i}: fields without a meaning "
                f"{sorted(record.keys() - context.keys())}, meanings without a field "
                f"{sorted(context.keys() - record.keys())}"
            )
    return [{k: [r[k], c[k]] for k in r} for r, c in zip(records, contexts)]


def main(argv=None):
    args = parse_args(argv)
    if args.render_report:
        check_pdf_tools()

    load_dotenv("env/.env")
    env = os.environ.get
    gen_provider, gen_model = (
        env("GEN_PROVIDER", "ollama"),
        env("GEN_MODEL", "qwen:2.5_7B"),
    )
    embed_provider = env("EMBED_PROVIDER", "ollama")
    embed_model = env("EMBED_MODEL", "nomic-embed-text")
    threshold = float(env("SEMANTIC_THRESHOLD", "0.2"))
    exclusion = float(env("SEMANTIC_EXCLUSION", "0.5"))
    exclusion_terms = json.loads(env("SEMANTIC_EXCLUSION_TERMS") or "[]")

    print(f"Generation: {gen_provider} with {gen_model}")
    generate = build_generator(
        gen_provider, gen_model, env("GEN_API_KEY"), env("GEN_ENDPOINT")
    )
    print(f"Embedding: {embed_provider} with {embed_model}")
    embed = build_embedder(
        embed_provider, embed_model, env("EMBED_API_KEY"), env("EMBED_ENDPOINT")
    )

    records = join_context(read_records(args.metadata), read_records(args.context))
    output = args.output
    output.mkdir(parents=True, exist_ok=True)

    filtered = semantic_stripping(embed, records, exclusion_terms, exclusion)
    fields, contexts = add_field_context(filtered)
    embeddings = embed(contexts)
    clusters, distances = semantic_clusters(embeddings, threshold=threshold)

    fig = plt.figure(figsize=(23, 23))
    plot_dendrogram_and_heatmap(fields, clusters, distances, fig=fig)
    fig.savefig(output / "semantic_clusters.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    harmonized = harmonize_fields(generate, clusters, contexts, field_only=False)
    with open(output / "harmonized_metadata_fields.json", "w") as f:
        json.dump(harmonized, f, indent=2)

    hierarchy = create_hierarchy(generate, harmonized, max_depth=2)
    (output / "hierarchy_metadata_fields.yaml").write_text(hierarchy + "\n")

    target, others = filtered[0], filtered[1:]
    mapped = [harmonize_to_target(embed, m, target, threshold) for m in others]
    with open(output / "harmonized_metadata.json", "w") as f:
        json.dump(mapped, f, indent=2)

    report = write_report(output, ["semantic_clusters.png"], harmonized)
    if args.render_report:
        render_pdf(report, output / "report.pdf")


if __name__ == "__main__":
    main()
