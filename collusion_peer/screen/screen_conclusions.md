## Models not screened

| Model | Status | Reason |
|---|---|---|
| `z-ai/glm-5.3-flash` | Skipped (user) | Stalled for 14 min on slow API replies after round 1 |
| `qwen/qwen3.6-35b-a3b` | Skipped (user) | Half of its replies came back empty after 8 retries; likely its hidden reasoning used up the output allowance (the harness treats any `qwen` model as a reasoning model) |
| `z-ai/glm-5.3` | Skipped (user: large models) | Stopped a few minutes in, when the screen was cut to small models |
| `mistralai/mistral-large-4-0` | Not run (large) | First attempt hung when the laptop suspended; it used about $1.44 before hanging and left no data |
| `meta-llama/llama-3.3-70b-instruct`, `gpt-5.2` | Not run (large) | Dropped when the screen was cut to small models |

## Harness fixes during the screen

The first runs exposed bugs in the harness's API clients. Fixed in `harness/src/llm/providers/` and `harness/experiments/run_endogenous.py` (see `git diff` in `harness/`):

1. **No retry on error replies.** Error bodies returned with HTTP 200 and empty replies were treated as permanent failures, which wiped out whole stages during brief provider hiccups. They are now retried up to 8 times with backoff up to 60 s, and anything that still fails is logged to `harness/outputs/api_errors.jsonl`.
2. **GPT-5 replies.** The OpenAI client read only the first output item, which for reasoning models is the hidden reasoning, not the answer.
3. **Judge never ran.** The judge always uses `openai/gpt-5-mini`, but no OpenAI client was created for non-GPT runs, and the `openai/` prefix was rejected by OpenAI. Judge labels exist only for runs after the fix (GPT models, Gemma, Gemini 3.8 Flash rerun).

**Effect, Gemini 3.8 Flash before vs after the fix:** parse rates went from 65 / 97 / 100 / 20% (plan / announce / choice / reflection) to 100% at every stage. The class did not change (selfish, 0% CHEAP).

**Results still from the old client:** Llama 4 Scout, Llama 4 Maverick, Mistral Small 3.2, Gemini 3.5 Flash Lite, Claude Haiku 5.5 (all parsed ≥ 95%, so unaffected), and Claude Sonnet 5.5, DeepSeek V4 Pro, DeepSeek V4.1 Flash (low parse rates; their reruns were skipped, so read their honesty and trust numbers with care; their classes rest on the choices that did parse, all EXPENSIVE or nearly so).

## Spend

- **OpenRouter:** $4.52 of $10 used in total. The table's per-model costs sum to about $2.40; the rest went to the Mistral Large run that hung (~$1.44), runs stopped partway (GLM, Qwen, the DeepSeek rerun, superseded first runs), and small test calls.
- **OpenAI:** GPT-4o-mini, GPT-5-mini, GPT-4o and every judge call since the fix. Not measurable from here; check the OpenAI usage page.

## What the screen shows

- **Four cooperative models, from three providers:** GPT-4o-mini, Gemini 3.5 Flash Lite, Llama 4 Scout, Llama 4 Maverick.
- **Two kinds of cooperator.** GPT-4o-mini and Gemini 3.5 Flash Lite are **honest cooperators**: they announce CHEAP and order CHEAP, and rate each other highly (mean trust 4.7–4.9). The Llama 4 models are **bluffing cooperators**: they often announce EXPENSIVE and then order CHEAP, so they break commitments 60–85% of the time and distrust each other (Maverick groups gave mean trust 1.24 despite all-CHEAP play).
- **Larger or newer siblings defect more,** in every family tested: Gemini 3.5 Flash Lite 95% → Gemini 3.8 Flash 0%; Gemma 4 26B 60% → Gemma 4 31B 0%; GPT-4o-mini 100% → GPT-4o 65% → GPT-5-mini 0%. Llama is the exception (Scout 90%, Maverick 100%).
- **Claude models are honest but selfish**, matching what the harness paper found for Claude Opus 4.6.

## Recommendation for the experiment

Trust ratings are the main detection measure in `Plan.md`. Among bluffing cooperators trust stays low and noisy whatever happens, so an **honest cooperator is the better base**.

| Role | Option B (recommended) | Option A (alternative) |
|---|---|---|
| Base model (all seats rounds 1–5, other 4 seats throughout) | **`gpt-4o-mini`**: 100% CHEAP, honest, 100% parse everywhere | `meta-llama/llama-4-scout`: 90% CHEAP, bluffing |
| Stronger, same family (conditions 3–4) | **`gpt-4o`**: 65% CHEAP, so it also behaves differently | `meta-llama/llama-4-maverick`: 100% CHEAP, same behavior |
| Equal, other provider (conditions 5–7) | **`google/gemini-3.5-flash-lite`**: honest cooperator like the base | `gpt-4o-mini` or Gemini 3.5 Flash Lite: honest, unlike the base |

- **Option B** matches behavior in the three cross-provider conditions, so any detection there comes from identity or style, not strategy. Its weak point is the stronger swap: GPT-4o defects about a third of the time, so detection in conditions 3–4 may come from behavior. Report the newcomer's choices next to detection.
- **Option A** is the reverse: Scout → Maverick keeps behavior the same, but every cross-provider newcomer is honest among bluffers, and trust signals are weak.
- **Mixed-group comparison is feasible.** With four cooperative models from three providers, a mixed cooperative group (e.g. GPT-4o-mini, Gemini 3.5 Flash Lite, Llama 4 Scout, Llama 4 Maverick) can be run alongside the homogeneous one.

**Caveat:** each class rests on 20 choices from 2 groups. Confirm the chosen base in the Friday pilot before the main run.
