# Résumé Tailor

Reads a job posting and your résumé, puts the matching experience first in the employer's own words, then drills you on the gaps it could not paper over.

|  |  |
| --- | --- |
| Author | AgentCanvas |
| License | CC0-1.0 |
| API keys | `OPENAI_API_KEY` |
| Models | `openai/gpt-4o-mini` |
| Graph | 11 nodes · 15 edges |

## What it does

Tailoring a résumé is mostly reordering, not rewriting — but doing it by hand for every posting is tedious enough that people skip it and send the same file everywhere.

The editor here is explicitly forbidden from inventing experience: it reorders, rewords and cuts, and reports what it changed. The third agent then does the part people avoid — naming the requirements you do **not** meet and preparing an honest answer, because the interviewer will find them anyway.

## Agents

| Agent | Role |
| --- | --- |
| Posting Analyst | Job posting analyst |
| Résumé Editor | Résumé editor |
| Gap Coach | Interview preparation coach |

## Tasks

1. **Analyze Posting** — expects Three lists — Must have, Nice to have, Keywords — with nothing invented.
2. **Tailor Résumé** — expects A rewritten résumé in markdown, plus a short list of what you moved, reworded or cut and why.
3. **Prepare for Gaps** — expects A Q&A list, one entry per gap, ordered by how likely the question is.

## Run it

1. Open [AgentCanvas](https://github.com/hynwl/agentcanvas) (hosted or self-hosted).
2. **Templates → Hub → Fork** on this team.
3. Add `OPENAI_API_KEY` under **API keys** — they stay in your browser.
4. Press **Run**.
