# Competitor Price Watch

Reads competitors' own pricing pages, records what it saw and where, then compares only the things that are actually comparable.

|  |  |
| --- | --- |
| Author | AgentCanvas |
| License | CC0-1.0 |
| API keys | `OPENAI_API_KEY`, `SERPER_API_KEY` |
| Models | `openai/gpt-4o-mini` |
| Graph | 11 nodes · 12 edges |

## What it does

Pricing research goes stale the moment it is written, and secondhand summaries are stale before that. This crew opens the vendors' own pricing pages and records a URL and a date next to every figure, marking anything it could not confirm rather than estimating.

The analyst is instructed to refuse comparisons that do not hold — different seat definitions, bundled services, usage caps — because a tidy table that quietly compares unlike things is worse than no table.

## Agents

| Agent | Role |
| --- | --- |
| Pricing Scout | Pricing researcher |
| Positioning Analyst | Competitive analyst |

## Tasks

1. **Collect Prices** — expects One block per competitor: price, period, included, gated, source URL, date — with unconfirmed figures marked.
2. **Compare and Position** — expects A markdown comparison table, a short list of non-comparable items, and 2–3 deciding differences.

## Run it

1. Open [AgentCanvas](https://github.com/hynwl/agentcanvas) (hosted or self-hosted).
2. **Templates → Hub → Fork** on this team.
3. Add `OPENAI_API_KEY` and `SERPER_API_KEY` under **API keys** — they stay in your browser.
4. Press **Run**.
