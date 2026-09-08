# agentcanvas-hub

A public, no-login registry of published [AgentCanvas](https://github.com/hynwl/agentcanvas)
agent teams — visual CrewAI crews anyone can browse, fork, and run.

There is no account system here. Publishing a team means opening a pull
request; the PR itself *is* the submission form, and review is the
moderation. Anyone can then load a listed team into AgentCanvas and run it
with their own API keys.

## Layout

```text
agentcanvas-hub/
├── teams/
│   └── <slug>/
│       ├── team.acanvas.json   # the exported .acanvas.json document
│       ├── README.md           # what it does, one screenshot's worth of context
│       └── preview.png         # card thumbnail (16:9, ≤200KB)
├── scripts/
│   └── build_index.py          # regenerates index.json from teams/*
└── index.json                  # generated — do not hand-edit, see below
```

`<slug>` is the directory name shown in URLs and the app's Hub browser — pick
something short and kebab-case, e.g. `market-research-crew`.

## `index.json`

`index.json` at the repo root is a generated file: a flat, deterministic
listing of every team under `teams/`, built by `scripts/build_index.py`. It
exists so the AgentCanvas app (and anything else) can fetch one small file
instead of walking the whole tree. **Never edit it by hand** — regenerate it
instead:

```sh
python3 scripts/build_index.py
```

`--check` exits non-zero if the committed `index.json` doesn't match what the
script would produce right now (used by CI to catch a PR that forgot to
regenerate it after touching `teams/`).

Each `teams/<slug>/team.acanvas.json` must be a valid AgentCanvas document —
see `CanvasDoc` in the main repo's
[`frontend/src/types/canvas.ts`](https://github.com/hynwl/agentcanvas/blob/main/frontend/src/types/canvas.ts).
The fields that end up in `index.json` are `id`, `name`, `description`,
`tags`, `author`, `license`, `revision`, `forked_from`, `created_at`,
`updated_at`, and `meta.{requires_keys,difficulty}`. The document's own
`meta.thumbnail` (a `data:` URI) is ignored in favor of the sibling
`preview.png` file — keeps `index.json` small regardless of how many teams
are listed.

## Licensing

The tooling in this repo (`scripts/`, this README, CI config) is MIT
licensed — see `LICENSE`.

Each **team's own content** carries whatever license its author chose at
publish time, recorded in `team.acanvas.json`'s `license` field. That choice
is independent of both this repo's license and of AgentCanvas's own
AGPL-3.0 — publishing a team here doesn't relicense it.

## Submitting a team

A step-by-step submission guide is coming in a follow-up change (M5-T8). For
now, the shape above is the contract: a `teams/<slug>/` directory with the
three files listed, and a regenerated `index.json`.

Every PR touching `teams/` is checked automatically by
[`.github/workflows/validate.yml`](.github/workflows/validate.yml), which
runs `scripts/validate_submission.py` against each changed team:

1. **Schema** — the document matches the `.acanvas.json` shape (required
   fields, known node types, edges pointing at real node ids).
2. **Publish scan** — no leaked API keys. (Other findings — a private
   hostname, a local file path, an email address — are posted as CI
   warnings for the human reviewer to judge; they don't block the PR. See
   R9: PR review *is* the moderation here.)
3. **Dry-run compile** — the graph would actually compile into a Crew (has
   exactly one Crew node, every Task has an Agent, no cyclic task
   dependencies, no empty required fields). This never calls an LLM and
   needs no API key.

These checks are a stdlib-only Python port of the main AgentCanvas repo's own
validators, kept here rather than imported across repos — this repo takes
anonymous fork PRs, and giving that CI context any credential for the
(private) main repo would be a real risk. `python3 scripts/validate_submission.py <slug>`
runs the same checks locally before you open a PR.
