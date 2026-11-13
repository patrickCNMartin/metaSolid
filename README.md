# metaSolid

Harmonizes metadata field names: the meaning of each field is embedded, similar fields are
clustered, and an LLM names each cluster. Experimental.

## Setup

Every setup needs [Ollama](https://ollama.com) running on the host:

```sh
brew install ollama
ollama serve & disown
```

Then one of:

| environment | enter it | brings |
|---|---|---|
| nix | `nix develop` | Python, uv, pandoc, typst, and the dev tools in `.venv` |
| pixi | `pixi shell -e dev` (`pixi shell` for the runtime only) | Python, pandoc, typst, the dev tools |
| uv | `uv sync --extra dev` | the Python packages; for `--render_report` also `brew install pandoc typst` |
| docker | see [Docker](#docker) | the runtime, pandoc and typst |

For Jupyter, in the nix shell or with uv: `uv run --extra notebook jupyter lab`.

## Creating the models

```sh
ollama pull nomic-embed-text

ollama pull qwen2.5:7b
ollama create qwen:2.5_7B -f ollama-models/qwen2.5_7B.modelfile

ollama pull gemma4:12b
ollama create gemma:4_12B -f ollama-models/gemma4_12B.modelfile

ollama ls
```

Put the created name in `GEN_MODEL`. To change a model's settings, edit its modelfile and run
`ollama create` again.

## Configuration

```sh
cp env/.env.example env/.env
```

| variable | sets | default |
|---|---|---|
| `EMBED_PROVIDER`, `GEN_PROVIDER` | `ollama`, `llama-cpp`, `vllm`, `open-llm` or `openai` | `ollama` |
| `EMBED_MODEL` | the embedding model | `nomic-embed-text` |
| `GEN_MODEL` | the generation model | `qwen:2.5_7B` |
| `EMBED_ENDPOINT`, `GEN_ENDPOINT` | the full URL of the route; empty uses the provider's default | |
| `EMBED_API_KEY`, `GEN_API_KEY` | sent as `Authorization: Bearer`, only when set | |
| `SEMANTIC_THRESHOLD` | the clustering cut-off (cosine distance), and the cut-off for matching onto the target (cosine similarity) | `0.2` |
| `SEMANTIC_EXCLUSION` | how similar to an exclusion term a field must be to be dropped | `0.5` |
| `SEMANTIC_EXCLUSION_TERMS` | JSON list of terms; fields close to one are dropped | `[]` |

## Use

Two input files, each `.json`, `.yaml` or `.yml`:

- `--metadata`: a list of records, one flat dict per record.
- `--context`: the meaning of each field, one dict per record, in the same order and with the same
  fields.

```json
[{"owner.email": "ada@example.org", "state": "new"}]
```
```json
[{"owner.email": "Email of the person who submitted the request.", "state": "Stage of the request."}]
```

```sh
python -m metasolid --metadata requests.json --context context.json --output out/
python -m metasolid --metadata requests.yaml --context context.yaml --output out/ --render_report
```

Run it as `nix develop --command uv run python -m metasolid …`, `uv run python -m metasolid …` or
`pixi run harmonize …`. To try it, use the fixtures:

```sh
python -m metasolid --metadata tests/fixtures/service_requests.json \
  --context tests/fixtures/field_context.json --output out/
```

| output | holds |
|---|---|
| `semantic_clusters.png` | dendrogram and distance heatmap of the fields |
| `harmonized_metadata_fields.json` | one harmonized label per cluster, with its explanation |
| `hierarchy_metadata_fields.yaml` | the harmonized labels as a YAML hierarchy |
| `harmonized_metadata.json` | every record after the first, mapped onto the first record's fields |
| `report.md` | the plots and the harmonized labels |
| `report.pdf` | with `--render_report` |

## Docker

Build with Docker, or with nix:

```sh
VERSION=$(python3 -c "import tomllib;print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])")
docker build --build-arg VERSION=$VERSION -t metasolid:$VERSION .
```
```sh
nix build .#oci && docker load < result
```

Both are tagged with the version in `pyproject.toml`. In `env/.env`, point `EMBED_ENDPOINT` and
`GEN_ENDPOINT` at `host.docker.internal` instead of `localhost`, then:

```sh
docker run --rm --user "$(id -u):$(id -g)" --env-file env/.env -v "$PWD/data:/app/data" \
  metasolid:0.1.0 --metadata data/requests.json --context data/context.json \
  --output data/out --render_report
```

## Tests and lint

```sh
nix develop --command uv run pytest
nix develop --command uv run ruff check .
nix develop --command uv run ruff format --check .
```

Or `pixi run -e dev test` and `pixi run -e dev lint`. The PDF test is skipped without pandoc and
typst.

## Contributing

- Coding agents read [AGENT.md](AGENT.md) first.
- Write code with [ponytail](https://github.com/dietrichgebert/ponytail): the shortest working
  change, functions rather than classes.
- Install the pre-push hooks (ruff, detect-secrets): `pre-commit install --hook-type pre-push`.
- Fixtures in `tests/fixtures/` are made up; every email and URL stays on `example.org`.
- Decisions taken with a coding agent are logged by the agent with
  [dev-skills/logging](dev-skills/logging/SKILL.md), one file per decision in `docs/decisions/`.
  Read them with `sh dev-skills/logging/log.sh`. Decisions you take yourself go in the pull
  request description.
