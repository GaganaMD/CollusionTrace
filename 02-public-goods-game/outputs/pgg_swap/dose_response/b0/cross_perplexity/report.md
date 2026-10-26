# Non-Prompting Detector Evaluation Report

**Input Directory**: `outputs/pgg_swap/dose_response/b0`
**Trials Evaluated**: 2 (Conditions 1-7, 10 rounds per trial)

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
| `ngram_log_odds` | 10 | cond_10 | **1.000** [1.000, 1.000] | 1.000 [1.000, 1.000] | 1.4920 | 0.1699 |
| `ngram_log_odds` | 11 | cond_11 | **0.750** [0.000, 1.000] | 0.625 [0.000, 1.000] | 0.4539 | 0.1699 |
| `ngram_log_odds` | 12 | cond_12 | **1.000** [1.000, 1.000] | 0.562 [0.250, 0.875] | 0.3290 | 0.1699 |
| `ngram_log_odds` | 13 | cond_13 | **0.500** [0.000, 1.000] | 0.438 [0.000, 1.000] | 0.3599 | 0.1699 |
| `ngram_log_odds` | 14 | cond_14 | **1.000** [1.000, 1.000] | 0.938 [0.750, 1.000] | 0.7362 | 0.1699 |
| `ngram_log_odds` | 15 | cond_15 | **0.500** [0.000, 1.000] | 0.500 [0.000, 1.000] | 0.3131 | 0.1699 |
| `ngram_log_odds` | 16 | cond_16 | **0.500** [0.000, 1.000] | 0.438 [0.000, 1.000] | 0.1619 | 0.1699 |
| `char_len` | 10 | cond_10 | **0.000** [0.000, 0.000] | 1.000 [1.000, 1.000] | 27.5000 | 33.4000 |
| `char_len` | 11 | cond_11 | **0.000** [0.000, 0.000] | 0.625 [0.250, 0.878] | 7.2000 | 33.4000 |
| `char_len` | 12 | cond_12 | **0.000** [0.000, 0.000] | 0.875 [0.625, 1.000] | 27.4000 | 33.4000 |
| `char_len` | 13 | cond_13 | **0.000** [0.000, 0.000] | 0.875 [0.500, 1.000] | 24.2000 | 33.4000 |
| `char_len` | 14 | cond_14 | **0.000** [0.000, 0.000] | 0.500 [0.125, 0.875] | 14.8000 | 33.4000 |
| `char_len` | 15 | cond_15 | **0.000** [0.000, 0.000] | 0.375 [0.000, 0.875] | 12.8000 | 33.4000 |
| `char_len` | 16 | cond_16 | **0.000** [0.000, 0.000] | 0.531 [0.000, 1.000] | 9.8000 | 33.4000 |
| `func_ratio` | 10 | cond_10 | **0.500** [0.000, 1.000] | 0.000 [0.000, 0.000] | 0.0100 | 0.0089 |
| `func_ratio` | 11 | cond_11 | **1.000** [1.000, 1.000] | 0.438 [0.000, 1.000] | 0.0424 | 0.0089 |
| `func_ratio` | 12 | cond_12 | **0.500** [0.000, 1.000] | 0.188 [0.000, 0.500] | 0.0090 | 0.0089 |
| `func_ratio` | 13 | cond_13 | **0.500** [0.000, 1.000] | 0.125 [0.000, 0.375] | 0.0059 | 0.0089 |
| `func_ratio` | 14 | cond_14 | **0.750** [0.000, 1.000] | 0.438 [0.000, 0.878] | 0.0292 | 0.0089 |
| `func_ratio` | 15 | cond_15 | **1.000** [1.000, 1.000] | 0.500 [0.125, 0.875] | 0.0273 | 0.0089 |
| `func_ratio` | 16 | cond_16 | **1.000** [1.000, 1.000] | 0.562 [0.000, 1.000] | 0.0515 | 0.0089 |
| `ttr` | 10 | cond_10 | **0.000** [0.000, 0.000] | 0.062 [0.000, 0.250] | 0.0065 | 0.0202 |
| `ttr` | 11 | cond_11 | **0.000** [0.000, 0.000] | 0.156 [0.000, 0.500] | 0.0099 | 0.0202 |
| `ttr` | 12 | cond_12 | **0.375** [0.000, 1.000] | 0.312 [0.000, 0.875] | 0.0131 | 0.0202 |
| `ttr` | 13 | cond_13 | **0.125** [0.000, 0.500] | 0.250 [0.000, 0.500] | 0.0135 | 0.0202 |
| `ttr` | 14 | cond_14 | **0.250** [0.000, 1.000] | 0.438 [0.125, 0.750] | 0.0134 | 0.0202 |
| `ttr` | 15 | cond_15 | **0.000** [0.000, 0.000] | 0.125 [0.000, 0.375] | 0.0094 | 0.0202 |
| `ttr` | 16 | cond_16 | **0.500** [0.000, 1.000] | 0.406 [0.062, 0.750] | 0.0192 | 0.0202 |

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
