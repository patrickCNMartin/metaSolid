 # metaSolid

**Meta Data Consolidation - IDS - METASOLID**

**Summary**: A small toolkit to harmonize and cluster metadata field names using semantic embeddings and hierarchical clustering. It is provider-agnostic and can use local or remote embedding/generation services (e.g., Ollama, OpenLLM, OpenAI).

**Status**: Early-stage, experimental research code.


**Features**
- **Semantic key context**: convert metadata keys to short context sentences for embedding (`add_field_context`).
- **Embedding-agnostic**: accepts any embedding function that returns numpy vectors (`get_semantic_embeddings`).
- **Clustering & visualization**: hierarchical clustering of keys and visual outputs (dendrogram + heatmap, UMAP word-cloud).
- **Exclusion/stripping**: filter out keys that are semantically related to supplied exclusion terms.

**Requirements**
- Python >= 3.13 (see `pyproject.toml`).
- Install dependencies from `pyproject.toml` or create a virtual environment.

**Install (recommended)**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
# optional dev extras
pip install -e .[dev]
```

**Quickstart**
1. Prepare a JSON metadata file (a list of dicts). Example dataset files are located in the `data/` directory.
2. (Optional) Create an `env/.env` file to set provider configuration (see Configuration below).
3. (Optional) If you are using `ollama` locally, run `ollama serve & disown` first.
4. Run the CLI runner to produce visualization outputs:

```bash
python src/metaSolid/run_metaSolid.py --metadata data/fuzzy_ablated_requests.json --output data/
```

Outputs written to the `--output` directory include:
- `semantic_clusters.png` — dendrogram and heatmap of clustered keys.
- `semantic_word_cloud.png` — UMAP-based scatter with labels.

**Configuration / Environment variables**
The runner loads environment variables from `env/.env` by default. Common variables:
- **GEN_PROVIDER**: generation provider (default: `ollama`)
- **GEN_MODEL**: generation model name (default set in code)
- **GEN_ENDPOINT / GEN_API_KEY**: optional endpoint and key for generation APIs
- **EMBED_PROVIDER**: embedding provider (default: `ollama`)
- **EMBED_MODEL / EMBED_ENDPOINT / EMBED_API_KEY**: embedding settings
- **SEMANTIC_THRESHOLD**: threshold used for clustering/stripping
- **EXCLUSION_TERMS**: JSON-list of terms to exclude (example: `["api","url"]`)


**Supported provider keys**
The project implements lightweight HTTP-based wrapper functions so you can switch providers without vendor SDKs. Supported keys (used by `build_embedder` and `build_generator`) include:
- `ollama`
- `llama-cpp` / `vllm`
- `open-llm` (self-hosted OpenLLM endpoints)
- `openai`

Check the provider code for exact behavior and headers: [src/providers/embedders.py](src/providers/embedders.py#L1) and [src/providers/generators.py](src/providers/generators.py#L1).



**Development**
- Recommended tools: `ruff`, `pre-commit`, and Jupyter for exploratory runs (see `[project.optional-dependencies]` in `pyproject.toml`).


**Nix / Reproducible environment**
- This repository includes Nix flakes (`flake.nix`, `flake.lock`) to provide a reproducible development shell and build environment.
- Enter the development shell with:

```bash
nix develop
```

- Inside the Nix shell you can run the same commands listed in this README, for example:

```bash
python src/metaSolid/run_metaSolid.py --metadata data/fuzzy_ablated_requests.json --output data/
```

- Notes for macOS: ensure you have a recent Nix installation with flakes enabled. If flakes are unavailable, use your preferred Python virtual environment instead.





