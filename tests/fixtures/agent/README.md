# Agent provider fixtures (D-69)

Recorded HTTP responses replayed by `tests/test_llm_provider.py`; no test opens a socket.

| File | What it is | Source |
|---|---|---|
| `groq_429_rate_limit.json` | Groq 429, per-minute (TPM) limit | Groq's documented `rate_limit_exceeded` error body; organisation id replaced |
| `groq_429_daily.json` | Groq 429, per-day (TPD) limit | as above, the tokens-per-day variant |
| `bedrock_reply_reasoning.json` | Bedrock OpenAI-compatible chat completion whose content opens with `<reasoning>...</reasoning>` | the reply shape observed by the operator's manual call of 13 Oct 2026 (HTTP 200, OpenAI format, `usage` block); the text is a hand-written instance of that shape, because the endpoint answered 400 "Operation not allowed" when this fixture was made |

`body` is what `resp.json()` returns and, serialised, what `resp.text` returns.
