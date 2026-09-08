# Submitting a team

There is no account here. **A pull request is the submission form**, and review
is the moderation. You need a GitHub account to open the PR — nothing else, and
no AgentCanvas account ever.

A submission is one directory:

```text
teams/<slug>/
├── team.acanvas.json   # the team itself
├── README.md           # what it does, and why anyone should run it
└── preview.png         # 16:9 card image
```

`<slug>` is the folder name, shown in URLs and in the app's Hub browser. Use
lowercase letters, digits and dashes: `market-research-crew`.

## The easy path — let AgentCanvas build the bundle

1. Open your team in [AgentCanvas](https://github.com/hynwl/agentcanvas) and
   press **Publish** in the header.
2. Step 1 shows everything that would become public — API keys are always
   removed, and anything else it flags (an internal hostname, a path with your
   username in it, an email address) you can mask with one click. Pick who it
   is published by and under what license.
3. Confirm. You get `<slug>.acanvas.json`, and step 2 hands you the
   `preview.png` download and a filled-in `README.md` draft, plus the exact
   commands to move all three into place.

Then continue from [Open the pull request](#open-the-pull-request) below.

## The manual path

Any valid `.acanvas.json` works — export one from AgentCanvas
(**Backup → Export**) and add the two extra files yourself:

- **`preview.png`** — a 16:9 image of the canvas. Keep it small (the Publish
  flow produces roughly 30–80KB at 400×225); a full screenshot is fine too.
- **`README.md`** — see any existing team for the shape. What the team does,
  which agents are in it, what it needs to run, and — the part no generator can
  write — *why it exists*.

## Open the pull request

```sh
# in your fork of this repo
mkdir -p teams/<slug>
# put team.acanvas.json, README.md and preview.png in there

python3 scripts/build_index.py                     # regenerate index.json
python3 scripts/validate_submission.py <slug>      # the same checks CI runs

git add teams/<slug> index.json
git commit -m "add <slug>"
git push
```

Then open a PR against `main`. Both scripts are stdlib-only Python 3 — no
`pip install`, no Node, no API key.

## What CI checks

[`.github/workflows/validate.yml`](.github/workflows/validate.yml) runs on every
PR that touches `teams/`:

1. **`index.json` is up to date** — `build_index.py --check`. Forgetting to
   regenerate it is the single most common mistake; run the command above.
2. **Schema** — required fields, known node types, edges that point at real
   node ids.
3. **Publish scan** — leaked API keys **fail the PR**. Softer findings (an
   internal hostname, a local path, an email address) are posted as warnings
   for the reviewer to judge, not as failures.
4. **Dry-run compile** — the graph would actually build a Crew: exactly one
   Crew node, every Task has an Agent, no cyclic task dependencies, no empty
   required fields. Never calls an LLM, so it needs no keys.

Every step runs even when an earlier one fails, so one CI run shows you
everything at once.

## What gets merged

The bar is low but not zero:

- **It runs.** Someone with the listed keys should be able to fork it and press
  Run. If it needs a paid key, say which in the README.
- **It is yours to publish.** Don't submit someone else's prompts as your own.
- **No secrets, no personal data** — not yours, not anyone else's. This is a
  public repo; anything merged here is public forever.
- **Nothing built to harm.** Teams whose stated purpose is phishing, spam,
  harassment or mass-produced deception get closed. Judgment call, made by a
  human reviewer.

## Licensing

Your team's own license is your choice, recorded in `team.acanvas.json`'s
`license` field (the Publish flow asks). It is independent of this repo's MIT
tooling license and of AgentCanvas's AGPL-3.0 — publishing here does not
relicense your work. If you leave it unset, people will see "not specified",
which most readers treat as "ask first".

## Updating or removing a team

Open another PR. Bump `revision` in `team.acanvas.json` when the graph changes
meaningfully — the app shows it, and forks record which revision they came
from. To take a team down, delete its directory and regenerate `index.json`;
say in the PR that it is your team.
