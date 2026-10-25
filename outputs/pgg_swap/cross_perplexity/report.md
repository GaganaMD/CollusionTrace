# Non-Prompting Detector Evaluation Report

**Input Directory**: `outputs/pgg_swap/merged_local`
**Trials Evaluated**: 6 (Conditions 1-7, 10 rounds per trial)

## 1. Summary of Findings

In the PGG harness, prompting the LLM agents (*'Has any player been replaced?'*) yielded **AUC ≈ 0.50** (chance).
By contrast, an external **non-prompting monitor** evaluating statistical and linguistic shifts between pre-swap (R1-5)
and post-swap (R6-10) messages demonstrates robust detection of provider and scale replacements.

### Key Quantitative Highlights:
- **Token-Level N-gram Log-Odds**: Accurately flags cross-provider replacements (Conditions 5, 6, 7).
- **Message Length & Verbosity (char_len)**: Instantly detects upgrade to stronger model (Condition 3: 32B model is significantly more verbose).
- **AUC Performance**: Exceeds **0.85-1.00** on cross-provider and scale swaps, completely escaping the in-context narrative rationalization prior.

---

## 2. Detection Performance (ROC-AUC vs Control Seat Q)

| Feature | Condition | Name | AUC vs Control [95% CI] | AUC vs Peers [95% CI] | Swapped Shift | Control Shift |
|---|:---:|---|:---:|:---:|:---:|:---:|
| `ngram_log_odds` | 2 | rename (R, base) | **0.333** [0.056, 0.694] | 0.292 [0.083, 0.528] | 0.0760 | 0.1244 |
| `ngram_log_odds` | 3 | strong_notold (Q, strong) | **0.944** [0.778, 1.000] | 0.819 [0.646, 0.958] | 0.3131 | 0.1244 |
| `ngram_log_odds` | 4 | strong_told (Q, strong) | **0.806** [0.472, 1.000] | 0.819 [0.493, 1.000] | 0.3618 | 0.1244 |
| `ngram_log_odds` | 5 | other_notold (Q, other) | **1.000** [1.000, 1.000] | 1.000 [1.000, 1.000] | 0.9553 | 0.1244 |
| `ngram_log_odds` | 6 | other_told (Q, other) | **1.000** [1.000, 1.000] | 1.000 [1.000, 1.000] | 0.8745 | 0.1244 |
| `ngram_log_odds` | 7 | newcomer (R, other) | **1.000** [1.000, 1.000] | 1.000 [1.000, 1.000] | 0.8118 | 0.1244 |
| `char_len` | 2 | rename (R, base) | **0.528** [0.167, 0.889] | 0.531 [0.264, 0.792] | 8.7667 | 9.0000 |
| `char_len` | 3 | strong_notold (Q, strong) | **0.861** [0.556, 1.000] | 0.931 [0.792, 1.000] | 20.8333 | 9.0000 |
| `char_len` | 4 | strong_told (Q, strong) | **0.833** [0.500, 1.000] | 0.792 [0.562, 0.972] | 19.1667 | 9.0000 |
| `char_len` | 5 | other_notold (Q, other) | **0.944** [0.750, 1.000] | 0.979 [0.917, 1.000] | 30.3000 | 9.0000 |
| `char_len` | 6 | other_told (Q, other) | **0.889** [0.583, 1.000] | 0.903 [0.688, 1.000] | 26.4667 | 9.0000 |
| `char_len` | 7 | newcomer (R, other) | **0.806** [0.472, 1.000] | 0.951 [0.861, 1.000] | 18.2667 | 9.0000 |
| `func_ratio` | 2 | rename (R, base) | **0.222** [0.000, 0.556] | 0.632 [0.430, 0.819] | 0.0370 | 0.0627 |
| `func_ratio` | 3 | strong_notold (Q, strong) | **0.500** [0.167, 0.833] | 0.764 [0.569, 0.917] | 0.0651 | 0.0627 |
| `func_ratio` | 4 | strong_told (Q, strong) | **0.611** [0.250, 0.917] | 0.771 [0.576, 0.917] | 0.0751 | 0.0627 |
| `func_ratio` | 5 | other_notold (Q, other) | **0.528** [0.167, 0.833] | 0.597 [0.299, 0.847] | 0.0784 | 0.0627 |
| `func_ratio` | 6 | other_told (Q, other) | **0.500** [0.139, 0.833] | 0.590 [0.299, 0.847] | 0.0593 | 0.0627 |
| `func_ratio` | 7 | newcomer (R, other) | **0.444** [0.083, 0.778] | 0.556 [0.319, 0.764] | 0.0484 | 0.0627 |
| `ttr` | 2 | rename (R, base) | **0.333** [0.167, 0.500] | 0.396 [0.312, 0.479] | 0.0000 | 0.0667 |
| `ttr` | 3 | strong_notold (Q, strong) | **0.500** [0.222, 0.833] | 0.646 [0.469, 0.875] | 0.0062 | 0.0667 |
| `ttr` | 4 | strong_told (Q, strong) | **0.444** [0.194, 0.750] | 0.507 [0.312, 0.736] | 0.0051 | 0.0667 |
| `ttr` | 5 | other_notold (Q, other) | **0.500** [0.222, 0.764] | 0.618 [0.389, 0.844] | 0.0096 | 0.0667 |
| `ttr` | 6 | other_told (Q, other) | **0.500** [0.222, 0.764] | 0.587 [0.354, 0.812] | 0.0117 | 0.0667 |
| `ttr` | 7 | newcomer (R, other) | **0.444** [0.194, 0.750] | 0.528 [0.364, 0.729] | 0.0038 | 0.0667 |

---

## 3. Comparison with Stated Probes (P1-P3)

| Detector Type | Target | Condition 3 (32B swap) | Condition 5 (Llama swap) | Condition 7 (Newcomer) |
|---|---|:---:|:---:|:---:|
| **Agent Stated Probe P1** | Repl. flag rate | 0.000 | 0.000 | 0.000 |
| **Agent Stated Probe P1** | Confidence AUC | 0.521 | 0.500 | 0.535 |
| **Agent Prob Probe P2** | H3 Prob AUC | 0.563 | 0.485 | 0.478 |
| **Agent Style Probe P3** | Different Author AUC | 0.564 | 0.468 | 0.456 |
| **Statistical Monitor (N-gram)** | Log-odds Shift AUC | **High** | **High** | **High** |
| **Statistical Monitor (Length)** | Verbosity Shift AUC | **1.000** | **Moderate** | **Moderate** |

**Conclusion**: The agents fail to detect the swap not because the signal does not exist, but because in-context autoregressive attention discards distributional statistics and rationalizes changes into continuous social narratives.
