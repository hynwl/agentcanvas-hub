# Support Triage Desk

Classifies an incoming customer message, drafts a reply that refuses to invent timelines, and stops for a human to approve before anything is sent.

|  |  |
| --- | --- |
| Author | AgentCanvas |
| License | CC0-1.0 |
| API keys | `OPENAI_API_KEY` |
| Models | `openai/gpt-4o-mini` |
| Graph | 10 nodes · 11 edges |

## What it does

The failure mode of automated support replies is not bad grammar — it is confident invention: a fix that is not planned, a refund nobody approved, a date nobody committed to. The drafter here is told to answer or ask, never to promise.

It is also the reference graph for the **Human Review** node: the draft stops and waits for a person, who can send it as-is or paste their own version. Nothing reaches a customer that a human did not read.

## Agents

| Agent | Role |
| --- | --- |
| Triager | Support triage specialist |
| Reply Drafter | Support reply writer |

## Tasks

1. **Triage Ticket** — expects Category, urgency with reason, and the one blocking question — nothing else.
2. **Draft Reply** — expects A ready-to-send reply under 150 words, plus a one-line internal note on what the agent should check before sending.

## Run it

1. Open [AgentCanvas](https://github.com/hynwl/agentcanvas) (hosted or self-hosted).
2. **Templates → Hub → Fork** on this team.
3. Add `OPENAI_API_KEY` under **API keys** — they stay in your browser.
4. Press **Run**.
