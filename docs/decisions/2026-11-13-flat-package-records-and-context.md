---
date: 2026-11-13
title: One flat metasolid package that reads records and their field meanings as two files
decided_by: [human:patrickCNMartin, claude-code/claude-opus-5-5]
---

**Decided:** `src/` with six packages becomes one package, `metasolid/`, run as
`python -m metasolid --metadata FILE --context FILE --output DIR`. `--metadata` is a list of flat
records; `--context` holds the meaning of each field, one `{field: meaning}` per record in the same
order; both are `.json` or `.yaml`. They are joined once, at the edge, into the
`{field: [value, meaning]}` shape the rest of the code already took. All config is read in
`__main__` and passed down. Embedders and generators share one provider table in `providers.py`.
The test fixtures are written by hand from scratch: five made-up service requests with differing,
partly shared field names, and their meanings; every email and URL is on `example.org`, which a
test enforces.
**Why:** The meaning is what gets embedded, and a real metadata file has none, so it comes in as its
own file now and from generation later. Joining at the edge left every downstream function as it
was. The earlier synthetic output carried real request data, so no part of it became a fixture.
**Cost:** A record and its context must list exactly the same fields, or the run refuses. Field
values are passed through but never embedded.
