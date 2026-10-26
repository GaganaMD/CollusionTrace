# Newcomer screen: `haiku__naive__pilot`, warm swap, rounds 10-13

| Newcomer | Code correct | Re-asks | Stopped games | Suspicion of Q (probe) | Marks on Q | Q words/msg | Haiku says 'different author' | AUROC vs sham |
|---|---|---|---|---|---|---|---|---|
| anthropic/claude-haiku-5.5 (sham) | 31/32 (0.97) | – | 0 | 8.1 | 0 | 34.6 | 0.12 | – |
| openai/gpt-4o-mini (run's warm branches) | 16/25 (0.64) | 23 | 2 | 15.4 | 9 | 28.3 | 1.00 | 0.93 |
| openai/gpt-6-luna | 32/32 (1.00) | 0 | 0 | 9.2 | 2 | 25.0 | 0.69 | 0.78 |
| qwen/qwen3.8-flash | 31/32 (0.97) | 1 | 0 | 8.3 | 1 | 35.0 | 0.44 | 0.73 |
| google/gemini-3.8-flash | 32/32 (1.00) | 3 | 0 | 8.3 | 0 | 35.2 | 0.62 | 0.78 |
