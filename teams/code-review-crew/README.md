# Code Review Crew

Three reviewers — correctness, tests, readability — working under a manager LLM instead of a fixed order. Paste a unified diff and get findings ranked by what actually breaks.

|  |  |
| --- | --- |
| Author | AgentCanvas |
| License | CC0-1.0 |
| API keys | `OPENAI_API_KEY` |
| Models | `openai/gpt-4o-mini` |
| Graph | 11 nodes · 14 edges |

## What it does

Three reviewers with genuinely different jobs: one hunts for the input that breaks the change, one asks whether the tests would fail if it were wrong, one reads it as a stranger would in six months.

This is also the reference graph for a **hierarchical** crew. Instead of a fixed task order, a manager LLM (the second LLM node, wired into the Crew's `manager llm` port) decides who works on what — which is why the tasks here are not chained with context edges.

## Agents

| Agent | Role |
| --- | --- |
| Correctness Reviewer | Correctness reviewer |
| Test Reviewer | Test reviewer |
| Clarity Reviewer | Readability reviewer |

## Tasks

1. **Review Correctness** — expects A severity-ordered list of findings, each with location, trigger and consequence — or an explicit "no correctness issue…
2. **Review Tests** — expects A list of uncovered behaviours and weak assertions, each with the test that should exist.
3. **Review Clarity** — expects A short list of readability problems, each with the rewrite you would suggest.

## Run it

1. Open [AgentCanvas](https://github.com/hynwl/agentcanvas) (hosted or self-hosted).
2. **Templates → Hub → Fork** on this team.
3. Add `OPENAI_API_KEY` under **API keys** — they stay in your browser.
4. Press **Run**.
