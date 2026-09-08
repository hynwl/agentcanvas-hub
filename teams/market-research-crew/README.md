# Market Research Report

Three independent research tracks, synthesized by an analyst into one report.

|  |  |
| --- | --- |
| Author | AgentCanvas |
| License | CC0-1.0 |
| API keys | `OPENAI_API_KEY`, `SERPER_API_KEY` |
| Models | `openai/gpt-4o-mini` |
| Graph | 13 nodes · 23 edges |

## What it does

Three researchers work independent angles — demand, competitors, trends — and an analyst synthesizes them. The three research tasks are deliberately **not** chained to each other: they only meet in the synthesis task, so one researcher's framing does not contaminate the others.

## Agents

| Agent | Role |
| --- | --- |
| Demand Researcher | Demand & customer researcher |
| Competitor Researcher | Competitor researcher |
| Trend Researcher | Trend & regulation researcher |
| Market Analyst | Market analyst |

## Tasks

1. **Research Demand** — expects Three segments, each with motivation, pain point and a source URL.
2. **Research Competitors** — expects A Markdown table of five competitors. Columns: name / price / strengths / weaknesses / source.
3. **Research Trends** — expects Five trends, each with a one-line rationale, a source URL, and whether it is a risk.
4. **Synthesize Report** — expects A Markdown report: summary (5 lines) → market size & demand → competitive landscape → trends & risks → three entry reco…

## Run it

1. Open [AgentCanvas](https://github.com/hynwl/agentcanvas) (hosted or self-hosted).
2. **Templates → Hub → Fork** on this team.
3. Add `OPENAI_API_KEY` and `SERPER_API_KEY` under **API keys** — they stay in your browser.
4. Press **Run**.
