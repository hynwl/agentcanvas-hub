# Meeting Notes to Action Items

Paste a transcript; get decisions, open questions and an owner-and-date action table. Runs entirely on your own Ollama — nothing leaves the machine.

|  |  |
| --- | --- |
| Author | AgentCanvas |
| License | CC0-1.0 |
| API keys | none — runs locally |
| Models | `ollama/llama3` |
| Graph | 8 nodes · 10 edges |

## What it does

Most meeting summarizers give you a paragraph nobody reads. This one splits what was **decided** from what was merely **raised**, then forces every decision into an owner-and-date row — the two moves that turn a transcript into something you can chase next week.

It runs on your own Ollama, so transcripts of internal meetings never leave the machine. That is the point: the meetings most worth summarizing are usually the ones you cannot paste into a hosted model.

## Agents

| Agent | Role |
| --- | --- |
| Scribe | Meeting scribe |
| Action Tracker | Action item tracker |

## Tasks

1. **Extract Decisions** — expects Three markdown sections — Decisions, Open questions, Dropped — each a bullet list with a short supporting quote.
2. **Write Action Items** — expects A markdown table (Action \| Owner \| Due) followed by a one-line blockers note.

## Run it

1. Open [AgentCanvas](https://github.com/hynwl/agentcanvas) (hosted or self-hosted).
2. **Templates → Hub → Fork** on this team.
3. No API keys needed. Point the LLM node at a model your Ollama has pulled.
4. Press **Run**.
