# YouTube Script Pipeline

Outline, script, then hook optimization — all in one run.

|  |  |
| --- | --- |
| Author | AgentCanvas |
| License | CC0-1.0 |
| API keys | `OPENAI_API_KEY` |
| Models | `openai/gpt-4o-mini` |
| Graph | 11 nodes · 16 edges |

## What it does

Plan, script, then rework the opening. The hook specialist exists as a separate agent for a reason: the same model that just wrote eight minutes of script is the worst judge of whether its first fifteen seconds earn them.

## Agents

| Agent | Role |
| --- | --- |
| Content Planner | YouTube content planner |
| Scriptwriter | Video scriptwriter |
| Hook Specialist | Hook & retention specialist |

## Tasks

1. **Plan Video** — expects Target viewer / one-line promise / 5–7 sections (each with purpose and rough length) / three candidate titles.
2. **Write Script** — expects A script per section, each with one [on-screen] direction line. 1,200–1,800 words total.
3. **Optimize Hook** — expects Three candidate hooks with rationale, plus the full final script with the hook swapped in.

## Run it

1. Open [AgentCanvas](https://github.com/hynwl/agentcanvas) (hosted or self-hosted).
2. **Templates → Hub → Fork** on this team.
3. Add `OPENAI_API_KEY` under **API keys** — they stay in your browser.
4. Press **Run**.
