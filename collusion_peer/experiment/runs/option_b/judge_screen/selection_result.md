# Selection result

Rule: `SELECTION_RULE.md` (amended). Decision set = the 5 `stronger` items vs the 15 same-writer items, both orders.

| Judge | Unparsed | Order agreement | Decision-set AUC (n diff / n same) | Larger own-model-free set AUC (info) | Eligible |
|---|---|---|---|---|---|
| `google/gemini-3.5-flash-lite` | 0% | 82% | 0.53 (10 / 30) | 0.53 (10 / 30) | no |
| `meta-llama/llama-4-maverick` | 0% | 100% | 0.55 (10 / 30) | 0.63 (30 / 30) | no |
| `gpt-4o` | 0% | 100% | 0.55 (10 / 30) | 0.85 (20 / 30) | info only |

**No candidate is eligible.** Keep Option B's players and rely on the history variants alone; report that no cooperative detector was found.
