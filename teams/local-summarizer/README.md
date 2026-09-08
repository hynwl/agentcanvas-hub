# Local-only Summarizer

Uses only a local Ollama model. No API key, no cost.

|  |  |
| --- | --- |
| Author | AgentCanvas |
| License | CC0-1.0 |
| API keys | none — runs locally |
| Models | `ollama/llama3` |
| Graph | 6 nodes · 5 edges |

## What it does

A summarizer that never sends your text anywhere. Point the LLM node at whatever model your Ollama has pulled and it runs offline, for free — the honest starting point for anything you would not paste into a hosted API.

## Agents

| Agent | Role |
| --- | --- |
| Summarizer | Document summarization specialist |

## Tasks

1. **Summarize** — expects Five lines of summary plus three suggested actions.

## Run it

1. Open [AgentCanvas](https://github.com/hynwl/agentcanvas) (hosted or self-hosted).
2. **Templates → Hub → Fork** on this team.
3. No API keys needed. Point the LLM node at a model your Ollama has pulled.
4. Press **Run**.
