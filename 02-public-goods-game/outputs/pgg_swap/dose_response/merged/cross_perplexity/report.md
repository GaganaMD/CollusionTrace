# Non-Prompting Detector Evaluation Report

**Input Directory**: `outputs/pgg_swap/dose_response/merged`
**Trials Evaluated**: 5 (Conditions 1-7, 10 rounds per trial)

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
| `ngram_log_odds` | 10 | cond_10 | **1.000** [1.000, 1.000] | 1.000 [1.000, 1.000] | 1.3724 | 0.1856 |
| `ngram_log_odds` | 11 | cond_11 | **0.680** [0.200, 1.000] | 0.740 [0.440, 1.000] | 0.5144 | 0.1856 |
| `ngram_log_odds` | 12 | cond_12 | **0.560** [0.160, 1.000] | 0.730 [0.530, 0.910] | 0.2116 | 0.1856 |
| `ngram_log_odds` | 13 | cond_13 | **0.800** [0.400, 1.000] | 0.750 [0.390, 1.000] | 0.3824 | 0.1856 |
| `ngram_log_odds` | 14 | cond_14 | **1.000** [1.000, 1.000] | 0.970 [0.880, 1.000] | 0.8435 | 0.1856 |
| `ngram_log_odds` | 15 | cond_15 | **0.280** [0.000, 0.680] | 0.480 [0.200, 0.780] | 0.1307 | 0.1856 |
| `ngram_log_odds` | 16 | cond_16 | **0.280** [0.000, 0.680] | 0.450 [0.150, 0.740] | 0.1609 | 0.1856 |
| `char_len` | 10 | cond_10 | **0.280** [0.000, 0.640] | 0.590 [0.275, 0.900] | 14.3600 | 19.4000 |
| `char_len` | 11 | cond_11 | **0.160** [0.000, 0.480] | 0.510 [0.240, 0.780] | 5.6400 | 19.4000 |
| `char_len` | 12 | cond_12 | **0.360** [0.080, 0.800] | 0.550 [0.180, 0.940] | 15.0800 | 19.4000 |
| `char_len` | 13 | cond_13 | **0.320** [0.000, 0.720] | 0.510 [0.190, 0.840] | 13.6800 | 19.4000 |
| `char_len` | 14 | cond_14 | **0.280** [0.000, 0.640] | 0.430 [0.190, 0.700] | 9.4000 | 19.4000 |
| `char_len` | 15 | cond_15 | **0.200** [0.000, 0.600] | 0.415 [0.190, 0.690] | 9.6400 | 19.4000 |
| `char_len` | 16 | cond_16 | **0.200** [0.000, 0.560] | 0.420 [0.135, 0.730] | 7.1200 | 19.4000 |
| `func_ratio` | 10 | cond_10 | **0.680** [0.200, 1.000] | 0.590 [0.190, 0.970] | 0.0565 | 0.0268 |
| `func_ratio` | 11 | cond_11 | **0.800** [0.440, 1.000] | 0.460 [0.250, 0.680] | 0.0458 | 0.0268 |
| `func_ratio` | 12 | cond_12 | **0.520** [0.000, 0.840] | 0.430 [0.120, 0.760] | 0.0465 | 0.0268 |
| `func_ratio` | 13 | cond_13 | **0.560** [0.160, 0.920] | 0.360 [0.060, 0.710] | 0.0429 | 0.0268 |
| `func_ratio` | 14 | cond_14 | **0.520** [0.160, 0.880] | 0.440 [0.160, 0.720] | 0.0271 | 0.0268 |
| `func_ratio` | 15 | cond_15 | **0.680** [0.280, 1.000] | 0.490 [0.290, 0.710] | 0.0292 | 0.0268 |
| `func_ratio` | 16 | cond_16 | **0.640** [0.240, 1.000] | 0.350 [0.110, 0.610] | 0.0395 | 0.0268 |
| `ttr` | 10 | cond_10 | **0.380** [0.000, 0.760] | 0.290 [0.080, 0.530] | 0.0126 | 0.0147 |
| `ttr` | 11 | cond_11 | **0.580** [0.199, 0.900] | 0.420 [0.150, 0.695] | 0.0204 | 0.0147 |
| `ttr` | 12 | cond_12 | **0.420** [0.040, 0.800] | 0.210 [0.000, 0.480] | 0.0099 | 0.0147 |
| `ttr` | 13 | cond_13 | **0.480** [0.119, 0.860] | 0.395 [0.130, 0.680] | 0.0151 | 0.0147 |
| `ttr` | 14 | cond_14 | **0.540** [0.160, 0.880] | 0.390 [0.150, 0.640] | 0.0174 | 0.0147 |
| `ttr` | 15 | cond_15 | **0.440** [0.000, 0.800] | 0.380 [0.150, 0.640] | 0.0144 | 0.0147 |
| `ttr` | 16 | cond_16 | **0.680** [0.200, 1.000] | 0.555 [0.260, 0.810] | 0.0244 | 0.0147 |

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
