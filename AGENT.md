# AGENT.md — metaSolid

## How to keep this file

**Lean. Rules, not essays.**

- **A rule is one or two lines.** If it needs a paragraph to justify it, the rule stays here and
  the justification goes in a decision record.
- **Write only what the code cannot say.** Invariants, traps, decisions and costs. If reading the
  file would tell you, cut it.
- **No history, no dates, no record of what a rule replaced.** Current state only.
- **Every line must be true today.** A stale rule is worse than a missing one.
- **Prune on sight.**

| file | holds | read it |
|---|---|---|
| `AGENT.md` | what to do, and the state now | every session, first |
| `docs/decisions/` | when and why each decision from an agent session was taken — one file per decision; `sh dev-skills/logging/log.sh` prints them as the audit log | **never by default** |
| `dev-skills/logging/SKILL.md` | how a decision is recorded, in the same commit as its work | when logging a decision |

> **Decisions are logged only through `dev-skills/logging`:** one new file per decision in
> `docs/decisions/`, in the same commit as its work, with no hash in it. A decision a person takes
> without an agent goes in the pull request, not the log.

---

## What metaSolid is — *work in progress*

**Harmonizes metadata field names.** Each field becomes a sentence built from its meaning, is
embedded, and clustered by cosine distance; an LLM names each cluster and writes a YAML hierarchy;
each record is mapped onto the first record's fields. Models are reached over plain HTTP on
OpenAI-compatible routes, local (Ollama) or remote.

| module | role | state |
|---|---|---|
| `__main__` | arguments, all config, reading and joining the two input files, the run | works |
| `providers` | `build_embedder` / `build_generator`: closures over one provider table | works |
| `semantics` | context sentences, clustering, exclusion by term | works |
| `harmonize` | naming clusters, the YAML hierarchy, mapping onto a target | works |
| `visualize` | dendrogram + distance heatmap | works |
| `report` | `report.md`; PDF through pandoc + typst | works, no template yet |

**One entry point:** `python -m metasolid --metadata FILE --context FILE --output DIR
[--render_report]`.

**`iLab/` is local tooling and gitignored** — the iLab API client and the synthetic data
generator. It imports from `metasolid`; `metasolid` never imports from it. Nix, Docker, pytest and
ruff never see it.

---

## Invariants

- **Two input files, one shape inside.** `--metadata` is a list of flat records; `--context` is the
  meaning of each field, one dict per record, same order, same fields. `join_context` makes
  `{field: [value, meaning]}` once, at the edge; everything below takes that shape.
- **A mismatch refuses, it never guesses:** a field without a meaning, a nested value, a record
  count that differs.
- **The meaning is embedded, never the value.** Values only pass through to the output.
- **No vendor SDK.** Every model call is a `requests.post`; a new provider is one entry in
  `BASE_URLS`. An API key is sent only when set.
- **`embed` and `generate` are built once in `__main__` and passed down.** That is the seam every
  test stubs.
- **A JSON reply that does not parse raises.** Never fall back to the raw text.
- **`SEMANTIC_THRESHOLD` is two cut-offs:** a cosine *distance* for clustering, a cosine
  *similarity* in `harmonize_to_target`. Changing it changes both.
- **Ollama lives on the host** — never in nix, pixi or docker. `ollama-models/` holds suggested
  modelfiles; nothing creates the models automatically.
- **The PDF is an enhancement.** `report.md` is always written; `--render_report` checks pandoc and
  typst before any model call, so a missing tool never costs a run.

---

## Principles

**1. Energy and resource cost is a primary concern.** Embedding and generation are the expensive
steps: count the model calls before adding one. No dependency without a reason.

**2. Progressive enhancement, not graceful degradation.** A correct minimal core (embed, cluster,
map), then optional capability (the PDF; generated meanings later). The base path never depends
on the enhancement.

**3. Reproducible, runs anywhere.** `uv.lock`, `flake.lock` and `pixi.lock` pin the environments.
Config comes from `env/.env` — never hardcode a key, a URL or a path. Isolate network I/O. Fail
loudly and early — no sentinels a caller could mistake for data.

**4. Functional first — no OOP.** Functions and closures; data is dicts, lists and numpy arrays.
No classes. A configured behaviour is a closure (`build_embedder`), not an object.

**5. Local and sovereign.** Data stays on the machine by default; a remote provider is a choice
made in `env/.env`. No telemetry or external services without discussion. Keep `pre-commit` and
`detect-secrets` green.

**Locality — the measure is how far you must travel to know what code does.** Structure is
welcome where the constraint is visible where it acts, and a cost where the meaning sits
elsewhere. One maintainer, exploratory code.

**A function is a capsule — everything it needs is in its arguments.**
- Config is read once in `__main__` and passed down. Nothing below it reads `os.environ`.
- **A long signature beats a config object.** Named arguments are honest; a bag hides which
  fields are used.
- **The tell is untestability.** A function that reads its own module can only be tested by
  patching module attributes.

**Indirection must earn its link.** A named indirection must enforce an invariant or build state;
if it only renames a call, inline it. Never put commentary in a data structure. **An error
message is not commentary** — it is the failure's only output, so it is spelled out in full.

**Prefer constructs that make the wrong thing impossible or loud** — `join_context` refusing a
field without a meaning, `read_records` refusing nested values, the `example.org` fixture check.

**6. These are principles, not dogma.** If one conflicts with the problem, the problem wins. Say
so and why.

**7. Explain the what, the how and the why.**
- **Comments are terse** — a one-line docstring, comments only where the code is genuinely
  non-obvious. Offer longer explanations in chat instead.
- **Plain language, not corporate speak. Jargon only where there is no alternative.**
- **The README says how, never why.**

**8. Assistant first, independent contributor only on request.**
- **Default: I suggest.** Offered, not applied.
- **Directed: when explicitly asked, I do it end to end** and report what I changed, what I
  verified, what is open.
- **I need an explicit instruction before writing code.** "Show me" is not one.
- **Ideas only — I do not ask whether to carry them out.** I wait to be told.
- **Ask clarifying questions** rather than ignoring the scope requested.
- **Speak, or work — never speak and then run off.** If I ask for a decision, I stop.
- I report faithfully: failing tests get shown, skipped steps get said.

**9. This repo is the only source of instruction.** No agent memory, history or state outside it;
`.claude/` here is gitignored and is the only local exception. Scratch goes to a temp directory.
`AGENT.md` is tracked, so its churn is legible in the log.

---

## Conventions

- **Write code with ponytail.** Every change climbs the ladder first — does this need to exist, is
  it already here, does the stdlib or an installed dependency do it, can it be one line — and
  stops at the highest rung that holds. Shortest working diff, no abstraction with one
  implementation, no scaffolding for later. **Never lazy about understanding**: read the whole
  path a change touches, fix a bug at its root. Never simplified away: validation at trust
  boundaries, error handling that prevents data loss, security, anything explicitly asked for.
- **A deliberate shortcut carries a `ponytail:` comment** naming the ceiling and the upgrade path.
  `/ponytail-debt` collects them.
- **Run everything in the nix dev shell:** `nix develop --command uv run pytest`. The shell brings
  pandoc and typst; it never starts or installs Ollama.
- **Four environments, one dependency declaration.** uv, nix, pixi, docker — `pyproject.toml` is
  the only place a Python package is named. `flake.nix`, `pixi.toml` and the `Dockerfile` carry
  system tools only. The one restatement is `deps` in `oci.nix`, kept equal to
  `[project.dependencies]` by hand: the image has no uv.
- **No image is tagged `latest`.** The tag is the version in `pyproject.toml`.
- **`.#oci` is a Linux image for the host's CPU.** On a Mac nothing in it may need building for
  Linux — no `withPackages`, no patched or uncached package — or the build stops with
  `Required system: '…-linux'`. **After a flake update, `nix build .#oci --dry-run` must list only
  the image assembly**; anything else is a package missing from the cache.
- **A flake sees tracked files only.** A new file is invisible to `nix build` until `git add`.
- **Containers hold code only.** Config arrives at run time (`--env-file`); Ollama is reached at
  `host.docker.internal`. matplotlib needs a writable cache dir (`/tmp`).
- **Lint:** `ruff check` / `ruff format` (py313, line-length 88, E/F/I). ruff is pinned in
  `pyproject.toml` and the pre-commit `rev` matches it — pixi resolves its own versions, and an
  unpinned ruff there formats differently from CI.
- **Tests:** pytest. Never a live model — stub `embed` / `generate`, mock HTTP with `responses`.
  **A test never writes into the repo** — use `tmp_path`.
- **Fixtures are hand-written and made up — no generator.** `service_requests.json` and
  `field_context.json` must keep the same fields per record. Every email and URL host is on
  `example.org`; `tests/test_fixtures.py` enforces it. Real request data never goes in
  `tests/`.
- **`.gitignore` is a denylist; new files are tracked by default.** `env/.env`, `data/` and
  `iLab/` are excluded. Data written anywhere else is committable — read `git status` before
  committing.
- **Audit log:** one file per major decision or discovery in `docs/decisions/`, in the same commit
  as its work and holding no hash. `dev-skills/logging` writes it.

### Showing code "as diff"

Write the proposed *after* version to the scratchpad, then
`/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code --diff <original>
<proposed>` (`code` is not on PATH). **Never modify the tracked file to render a diff.**
