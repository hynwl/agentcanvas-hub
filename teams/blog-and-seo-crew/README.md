# Blog & SEO Crew

Trend research, then writing, then an SEO pass — run in sequence.

|  |  |
| --- | --- |
| Author | AgentCanvas |
| License | CC0-1.0 |
| API keys | `OPENAI_API_KEY`, `SERPER_API_KEY` |
| Models | `openai/gpt-4o-mini` |
| Graph | 12 nodes · 17 edges |

## What it does

Research, draft, optimize — the pipeline most content teams run informally, drawn explicitly so you can see where the handoffs are. The SEO agent gets a scraper so it can look at what currently ranks instead of guessing.

## Agents

| Agent | Role |
| --- | --- |
| Trend Researcher | Senior Content Trend Researcher |
| Content Writer | Senior Blog Content Writer |
| SEO Specialist | Technical SEO Specialist |

## Tasks

1. **Research Trends** — expects A ranked list of three topics, each with a one-line rationale and a source URL.
2. **Write Blog Post** — expects A finished Markdown post with a title and subheadings.
3. **SEO Optimize** — expects The final, SEO-optimized Markdown post.

## Run it

1. Open [AgentCanvas](https://github.com/hynwl/agentcanvas) (hosted or self-hosted).
2. **Templates → Hub → Fork** on this team.
3. Add `OPENAI_API_KEY` and `SERPER_API_KEY` under **API keys** — they stay in your browser.
4. Press **Run**.
