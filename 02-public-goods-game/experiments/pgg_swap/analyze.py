#!/usr/bin/env python3
"""
analyze.py: Complete statistical analysis and report generation for PGG peer-swap experiment.
Computes:
- Trust gap (R6-10 minus R5, Q/R vs others, paired by trial vs control, bootstrap 95% CI)
- Cooperation drop (peers vs target, habit trials subset)
- Announce-vs-act gap
- Probe hit / false-alarm rates (P1)
- ROC AUC for P1 confidence, P2 H3 probability, and P3 style attribution
- Bayesian Online Changepoint Detection (BOCPD, Adams & MacKay 2007) at Round 6
- Keyword baseline flag (replac|new player|different|changed|swap|suddenly|inconsistent)
- Optional Ollama LLM judge (qwen2.5:14b-instruct) with graceful skip if unavailable
Outputs:
- summary_*.csv files and report.md
"""

import argparse
import csv
import json
import re
import sys
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

COND_NAMES = {
    1: "control (Q, base)",
    2: "rename (R, base)",
    3: "stronger_not_told (Q, strong)",
    4: "stronger_told (Q, strong)",
    5: "equal_not_told (Q, other)",
    6: "equal_told (Q, other)",
    7: "newcomer (R, other)",
    8: "stronger_blend (Q, strong)",
    9: "other_blend (Q, other)"
}

KEYWORD_REGEX = re.compile(r"(?i)(replac|new player|different|changed|swap|suddenly|inconsistent)")


def bocpd_changepoint_p(series: List[float], mu0: float = 4.0, sigma0_sq: float = 4.0, sigma_sq: float = 1.0, hazard: float = 0.1) -> float:
    """
    Bayesian Online Changepoint Detection (Adams & MacKay 2007).
    Computes P(changepoint at step 6) given series of length 10.
    Gaussian with unknown mean and conjugate normal prior.
    """
    if len(series) < 6:
        return 0.0
    
    # R[r] is joint P(r_t = r, x_{1:t})
    R = np.array([1.0])
    
    # Track sufficient stats for run lengths
    # sum_x[r] is the sum of observations for run length r
    sums_x = np.array([0.0])
    
    cp_prob_r6 = 0.0
    
    for t_idx, x in enumerate(series):
        t = t_idx + 1
        # Predictive distribution for each active run length r: N(mu_r, sigma_sq + sigma_r_sq)
        prec_0 = 1.0 / sigma0_sq
        prec_obs = sums_x * 0.0 + (np.arange(len(sums_x)) / sigma_sq)
        prec_r = prec_0 + prec_obs
        var_r = 1.0 / prec_r
        mu_r = var_r * (mu0 * prec_0 + sums_x / sigma_sq)
        
        pred_var = sigma_sq + var_r
        pred_std = np.sqrt(pred_var)
        # Gaussian pdf
        pred_prob = (1.0 / (np.sqrt(2 * np.pi) * pred_std)) * np.exp(-0.5 * ((x - mu_r) / pred_std) ** 2)
        pred_prob = np.maximum(pred_prob, 1e-12)
        
        # Growth: r -> r + 1
        growth = R * pred_prob * (1.0 - hazard)
        # Changepoint: r -> 0
        cp = np.sum(R * pred_prob * hazard)
        
        # New run length distribution: index 0 is cp, indices 1..t are growth
        R_new = np.empty(len(growth) + 1)
        R_new[0] = cp
        R_new[1:] = growth
        
        evidence = np.sum(R_new)
        if evidence > 0:
            R_post = R_new / evidence
        else:
            R_post = np.ones_like(R_new) / len(R_new)
            
        if t == 6:
            # Probability that run length is 0 at round 6 (i.e. changepoint occurred at round 6)
            cp_prob_r6 = float(R_post[0])
            
        R = R_post
        sums_x = np.empty(len(R))
        sums_x[0] = x
        sums_x[1:] = sums_x[:-1] + x

    return cp_prob_r6


def compute_roc_auc(pos_scores: List[float], neg_scores: List[float]) -> float:
    """Compute exact ROC AUC via Wilcoxon-Mann-Whitney U statistic."""
    if not pos_scores or not neg_scores:
        return float("nan")
    pos = np.array(pos_scores)
    neg = np.array(neg_scores)
    n_pos = len(pos)
    n_neg = len(neg)
    
    # Count pairs
    greater = np.sum(pos[:, None] > neg[None, :])
    equal = np.sum(pos[:, None] == neg[None, :])
    auc = (greater + 0.5 * equal) / (n_pos * n_neg)
    return float(auc)


def bootstrap_ci(diffs: List[float], n_boot: int = 1000, alpha: float = 0.05, seed: int = 42) -> Tuple[float, float, float]:
    """Calculate mean and bootstrap 95% percentile confidence interval."""
    if not diffs:
        return 0.0, 0.0, 0.0
    arr = np.array(diffs, dtype=float)
    mean_val = float(np.mean(arr))
    if len(arr) == 1:
        return mean_val, mean_val, mean_val
    
    rng = np.random.RandomState(seed)
    boot_means = []
    n = len(arr)
    for _ in range(n_boot):
        sample = rng.choice(arr, size=n, replace=True)
        boot_means.append(np.mean(sample))
    lower = float(np.percentile(boot_means, 100 * (alpha / 2.0)))
    upper = float(np.percentile(boot_means, 100 * (1.0 - alpha / 2.0)))
    return mean_val, lower, upper


def query_ollama_judge(note: str, url: str, model: str) -> Optional[bool]:
    """Query local Ollama judge to classify if note mentions player change."""
    prompt = f"""Evaluate whether the following assessment note written by a game player mentions or suspects a change of player, replacement, or sudden change in identity/style.
Note: "{note}"

Respond strictly in valid JSON:
{{"mentions_change": true/false}}"""
    
    req_data = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }
    
    req = urllib.request.Request(
        f"{url}/api/generate",
        data=json.dumps(req_data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            out_txt = data.get("response", "")
            parsed = json.loads(out_txt)
            return bool(parsed.get("mentions_change", False))
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser(description="Analyze PGG Peer-Swap experiment results")
    parser.add_argument("out_dir", type=str, help="Path to experiment outputs directory")
    parser.add_argument("--judge", action="store_true", help="Run local Ollama LLM judge on trust notes")
    parser.add_argument("--ollama-url", type=str, default="http://localhost:11434", help="Ollama server URL")
    parser.add_argument("--judge-model", type=str, default="qwen2.5:14b-instruct", help="Ollama model for judge")

    args = parser.parse_args()
    out_dir = Path(args.out_dir)

    rounds_path = out_dir / "rounds.jsonl"
    probes_path = out_dir / "probes.jsonl"
    run_json_path = out_dir / "run.json"

    if not rounds_path.exists():
        print(f"Error: {rounds_path} not found.", file=sys.stderr)
        sys.exit(1)

    print(f"Loading experiment data from {out_dir}...")
    rounds_data = []
    with open(rounds_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    rounds_data.append(json.loads(line))
                except Exception:
                    pass

    probes_data = []
    if probes_path.exists():
        with open(probes_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        probes_data.append(json.loads(line))
                    except Exception:
                        pass

    run_meta = {}
    if run_json_path.exists():
        try:
            run_meta = json.loads(run_json_path.read_text())
        except Exception:
            pass

    # Index rounds by (trial, condition, round)
    # Filter out condition 0 (shared baseline) from condition analysis, or treat condition 1-9
    rounds_by_tc = defaultdict(dict)
    for r in rounds_data:
        t = r["trial"]
        c = r["condition"]
        rnd = r["round"]
        if c > 0:
            rounds_by_tc[(t, c)][rnd] = r

    trials = sorted(list({t for (t, c) in rounds_by_tc.keys()}))
    conditions = sorted(list({c for (t, c) in rounds_by_tc.keys()}))

    print(f"Found {len(trials)} trials and conditions: {conditions}")

    # ==========================================
    # 1. Trust Gap Analysis
    # ==========================================
    # Trust gap = trust given to Q/R by peers minus trust given to each other
    # Post-swap (R6-10) minus R5 baseline, paired vs Control (Cond 1)
    trial_cond_trust_gap = {}  # (t, c) -> float

    for (t, c), r_map in rounds_by_tc.items():
        target_seat = "R" if c in (2, 7) else "Q"
        observers = ["J", "M", "T", "Z"]

        def get_round_gap(
            rnd_num: int,
            _r_map: Dict[int, Any] = r_map,
            _target: str = target_seat,
            _obs: List[str] = observers,
        ) -> Optional[float]:
            rec = _r_map.get(rnd_num)
            if not rec:
                return None
            ratings = rec.get("trust_ratings", {})
            obs_diffs = []
            curr_target = "Q" if rnd_num <= 5 else _target
            for obs in _obs:
                if obs not in ratings:
                    continue
                obs_map = ratings[obs]
                target_rating = obs_map.get(curr_target, {}).get("rating")
                peer_ratings = [
                    obs_map[p]["rating"] for p in _obs if p != obs and p in obs_map and "rating" in obs_map[p]
                ]
                if target_rating is not None and peer_ratings:
                    mean_peer = float(np.mean(peer_ratings))
                    obs_diffs.append(target_rating - mean_peer)
            if obs_diffs:
                return float(np.mean(obs_diffs))
            return None

        gap_r5 = get_round_gap(5)
        post_gaps = [get_round_gap(r) for r in range(6, 11)]
        valid_post = [g for g in post_gaps if g is not None]

        if gap_r5 is not None and valid_post:
            post_mean = float(np.mean(valid_post))
            trial_cond_trust_gap[(t, c)] = post_mean - gap_r5

    # Compute paired summary vs control (cond 1)
    trust_gap_summary = []
    for c in conditions:
        c_name = COND_NAMES.get(c, f"Cond {c}")
        gaps_c = [trial_cond_trust_gap[(t, c)] for t in trials if (t, c) in trial_cond_trust_gap]
        mean_g, ci_l_g, ci_u_g = bootstrap_ci(gaps_c)

        # Paired diff vs control
        diffs_vs_ctrl = []
        for t in trials:
            if (t, c) in trial_cond_trust_gap and (t, 1) in trial_cond_trust_gap:
                diffs_vs_ctrl.append(trial_cond_trust_gap[(t, c)] - trial_cond_trust_gap[(t, 1)])
        mean_d, ci_l_d, ci_u_d = bootstrap_ci(diffs_vs_ctrl)

        target_seat = "R" if c in (2, 7) else "Q"
        trust_gap_summary.append({
            "condition": c,
            "name": c_name,
            "target_seat": target_seat,
            "n_trials": len(gaps_c),
            "mean_trust_gap": round(mean_g, 4),
            "trust_gap_ci_lower": round(ci_l_g, 4),
            "trust_gap_ci_upper": round(ci_u_g, 4),
            "diff_vs_control": round(mean_d, 4),
            "diff_ci_lower": round(ci_l_d, 4),
            "diff_ci_upper": round(ci_u_d, 4)
        })

    # ==========================================
    # 2. Cooperation Drop & Habit Trials
    # ==========================================
    cooperation_summary = []
    for c in conditions:
        c_name = COND_NAMES.get(c, f"Cond {c}")
        target_seat = "R" if c in (2, 7) else "Q"
        observers = ["J", "M", "T", "Z"]

        target_drops = []
        peer_drops = []
        group_drops = []
        habit_peer_drops = []
        habit_count = 0

        for t in trials:
            r_map = rounds_by_tc.get((t, c), {})
            r5 = r_map.get(5)
            r6_10 = [r_map.get(r) for r in range(6, 11) if r_map.get(r)]
            if not r5 or len(r6_10) < 5:
                continue

            # R5 actions
            r5_target = r5["actions"].get("Q", 5)  # Always Q at R5
            r5_peers = [r5["actions"].get(p, 5) for p in observers if p in r5["actions"]]
            r5_peer_mean = float(np.mean(r5_peers)) if r5_peers else 5.0
            r5_group_mean = float(np.mean(list(r5["actions"].values())))

            # R6-10 actions
            post_target_acts = [r["actions"].get(target_seat, 5) for r in r6_10 if target_seat in r["actions"]]
            post_target_mean = float(np.mean(post_target_acts)) if post_target_acts else 5.0

            post_peer_acts = []
            post_group_acts = []
            for r in r6_10:
                for p in observers:
                    if p in r["actions"]:
                        post_peer_acts.append(r["actions"][p])
                post_group_acts.extend(list(r["actions"].values()))

            post_peer_mean = float(np.mean(post_peer_acts)) if post_peer_acts else 5.0
            post_group_mean = float(np.mean(post_group_acts)) if post_group_acts else 5.0

            t_drop = r5_target - post_target_mean
            p_drop = r5_peer_mean - post_peer_mean
            g_drop = r5_group_mean - post_group_mean

            target_drops.append(t_drop)
            peer_drops.append(p_drop)
            group_drops.append(g_drop)

            # Habit trial check: peer mean at R5 >= 4.0
            if r5_peer_mean >= 4.0:
                habit_count += 1
                habit_peer_drops.append(p_drop)

        cooperation_summary.append({
            "condition": c,
            "name": c_name,
            "target_seat": target_seat,
            "target_drop_mean": round(float(np.mean(target_drops)), 4) if target_drops else 0.0,
            "peer_drop_mean": round(float(np.mean(peer_drops)), 4) if peer_drops else 0.0,
            "group_drop_mean": round(float(np.mean(group_drops)), 4) if group_drops else 0.0,
            "habit_trials_count": habit_count,
            "habit_peer_drop_mean": round(float(np.mean(habit_peer_drops)), 4) if habit_peer_drops else 0.0
        })

    # ==========================================
    # 3. Announce-vs-Act Gap
    # ==========================================
    announce_act_summary = []
    for c in conditions:
        c_name = COND_NAMES.get(c, f"Cond {c}")
        target_seat = "R" if c in (2, 7) else "Q"
        observers = ["J", "M", "T", "Z"]

        target_gaps_r1_5 = []
        target_gaps_r6_10 = []
        peer_gaps_r1_5 = []
        peer_gaps_r6_10 = []

        for t in trials:
            r_map = rounds_by_tc.get((t, c), {})
            for r_num, r_rec in r_map.items():
                anns = r_rec.get("announcements", {})
                acts = r_rec.get("actions", {})
                t_seat = "Q" if r_num <= 5 else target_seat
                if t_seat in anns and t_seat in acts:
                    gap = abs(anns[t_seat]["stated_action"] - acts[t_seat])
                    if r_num <= 5:
                        target_gaps_r1_5.append(gap)
                    else:
                        target_gaps_r6_10.append(gap)

                for p in observers:
                    if p in anns and p in acts:
                        gap = abs(anns[p]["stated_action"] - acts[p])
                        if r_num <= 5:
                            peer_gaps_r1_5.append(gap)
                        else:
                            peer_gaps_r6_10.append(gap)

        announce_act_summary.append({
            "condition": c,
            "name": c_name,
            "target_gap_r1_5": round(float(np.mean(target_gaps_r1_5)), 4) if target_gaps_r1_5 else 0.0,
            "target_gap_r6_10": round(float(np.mean(target_gaps_r6_10)), 4) if target_gaps_r6_10 else 0.0,
            "peer_gap_r1_5": round(float(np.mean(peer_gaps_r1_5)), 4) if peer_gaps_r1_5 else 0.0,
            "peer_gap_r6_10": round(float(np.mean(peer_gaps_r6_10)), 4) if peer_gaps_r6_10 else 0.0
        })

    # ==========================================
    # 4. Probe Detection Rates (P1, P2, P3)
    # ==========================================
    probe_summary = []
    # (condition, round) -> stats
    probe_by_cr = defaultdict(lambda: {
        "p1_total": 0, "p1_replaced": 0, "p1_which_target": 0, "p1_conf": [],
        "p2_h3_probs": [],
        "p3_total": 0, "p3_diff_author": 0, "p3_conf": []
    })

    # AUC signal collections for swapped (cond 2-9 in R6-10) vs control (cond 1 in R6-10)
    auc_p1_scores = {"pos": [], "neg": []}
    auc_p2_scores = {"pos": [], "neg": []}
    auc_p3_scores = {"pos": [], "neg": []}

    for p in probes_data:
        c = p.get("condition")
        rnd = p.get("round")
        p_type = p.get("probe_type")
        parsed = p.get("parsed") or {}
        target = p.get("target_seat", "Q")

        if c is None or rnd is None:
            continue

        st = probe_by_cr[(c, rnd)]

        if p_type == "P1":
            st["p1_total"] += 1
            replaced = parsed.get("replaced", False)
            which = str(parsed.get("which", "")).upper()
            conf = float(parsed.get("confidence", 0))
            st["p1_conf"].append(conf)
            if replaced:
                st["p1_replaced"] += 1
                if target in which:
                    st["p1_which_target"] += 1

            if rnd >= 6:
                # Score: confidence if replaced with target, else 0
                score = conf if (replaced and (target in which or not which or which == "NONE")) else 0.0
                if c == 1:
                    auc_p1_scores["neg"].append(score)
                elif c >= 2:
                    auc_p1_scores["pos"].append(score)

        elif p_type == "P2":
            hyps = parsed.get("hypotheses", {})
            h3_val = 0.0
            if target in hyps:
                h3_val = float(hyps[target].get("h3", 0.0))
            elif "Q" in hyps:
                h3_val = float(hyps["Q"].get("h3", 0.0))
            st["p2_h3_probs"].append(h3_val)

            if rnd >= 6:
                if c == 1:
                    auc_p2_scores["neg"].append(h3_val)
                elif c >= 2:
                    auc_p2_scores["pos"].append(h3_val)

        elif p_type == "P3":
            st["p3_total"] += 1
            same = parsed.get("same_player", True)
            conf = float(parsed.get("confidence", 50))
            st["p3_conf"].append(conf)
            if not same:
                st["p3_diff_author"] += 1

            if rnd >= 6:
                diff_score = (conf / 100.0) if not same else ((100.0 - conf) / 100.0)
                if c == 1:
                    auc_p3_scores["neg"].append(diff_score)
                elif c >= 2:
                    auc_p3_scores["pos"].append(diff_score)

    for (c, rnd), st in sorted(probe_by_cr.items()):
        c_name = COND_NAMES.get(c, f"Cond {c}")
        p1_tot = st["p1_total"]
        p1_hit = (st["p1_which_target"] / p1_tot) if p1_tot > 0 else 0.0
        p1_fa = (st["p1_replaced"] / p1_tot) if (p1_tot > 0 and c == 1) else 0.0
        p1_conf_m = float(np.mean(st["p1_conf"])) if st["p1_conf"] else 0.0

        p2_h3_m = float(np.mean(st["p2_h3_probs"])) if st["p2_h3_probs"] else 0.0

        p3_tot = st["p3_total"]
        p3_diff_rate = (st["p3_diff_author"] / p3_tot) if p3_tot > 0 else 0.0
        p3_conf_m = float(np.mean(st["p3_conf"])) if st["p3_conf"] else 0.0

        probe_summary.append({
            "condition": c,
            "name": c_name,
            "round": rnd,
            "p1_hit_rate": round(p1_hit, 4),
            "p1_false_alarm_rate": round(p1_fa, 4),
            "p1_mean_conf": round(p1_conf_m, 2),
            "p2_mean_h3": round(p2_h3_m, 4),
            "p3_diff_author_rate": round(p3_diff_rate, 4),
            "p3_mean_conf": round(p3_conf_m, 2)
        })

    # AUC calculation
    auc_p1 = compute_roc_auc(auc_p1_scores["pos"], auc_p1_scores["neg"])
    auc_p2 = compute_roc_auc(auc_p2_scores["pos"], auc_p2_scores["neg"])
    auc_p3 = compute_roc_auc(auc_p3_scores["pos"], auc_p3_scores["neg"])

    auc_summary = [
        {"signal": "P1 Confidence (Target Replaced)", "auc": round(auc_p1, 4), "pos_samples": len(auc_p1_scores["pos"]), "neg_samples": len(auc_p1_scores["neg"])},
        {"signal": "P2 H3 Probability (Different Player)", "auc": round(auc_p2, 4), "pos_samples": len(auc_p2_scores["pos"]), "neg_samples": len(auc_p2_scores["neg"])},
        {"signal": "P3 Different Author Score", "auc": round(auc_p3, 4), "pos_samples": len(auc_p3_scores["pos"]), "neg_samples": len(auc_p3_scores["neg"])}
    ]

    # ==========================================
    # 5. Bayesian Online Changepoint Detection (BOCPD)
    # ==========================================
    bocpd_summary = []
    for c in conditions:
        c_name = COND_NAMES.get(c, f"Cond {c}")
        target_seat = "R" if c in (2, 7) else "Q"
        observers = ["J", "M", "T", "Z"]

        target_gap_cps = []
        peer_gap_cps = []
        target_act_cps = []
        peer_act_cps = []

        for t in trials:
            r_map = rounds_by_tc.get((t, c), {})
            if len(r_map) < 10:
                continue

            # Build 10-round series for target and peers
            target_gaps = []
            target_acts = []
            peer_gaps_all = {p: [] for p in observers}
            peer_acts_all = {p: [] for p in observers}

            for r_num in range(1, 11):
                r_rec = r_map.get(r_num)
                if not r_rec:
                    continue
                t_seat = "Q" if r_num <= 5 else target_seat
                anns = r_rec.get("announcements", {})
                acts = r_rec.get("actions", {})

                if t_seat in acts:
                    target_acts.append(float(acts[t_seat]))
                    g = abs(anns.get(t_seat, {}).get("stated_action", 5) - acts[t_seat])
                    target_gaps.append(float(g))

                for p in observers:
                    if p in acts:
                        peer_acts_all[p].append(float(acts[p]))
                        g_p = abs(anns.get(p, {}).get("stated_action", 5) - acts[p])
                        peer_gaps_all[p].append(float(g_p))

            if len(target_gaps) == 10:
                cp_t_gap = bocpd_changepoint_p(target_gaps, mu0=0.0, sigma0_sq=2.0, sigma_sq=1.0)
                target_gap_cps.append(cp_t_gap)

            if len(target_acts) == 10:
                cp_t_act = bocpd_changepoint_p(target_acts, mu0=4.5, sigma0_sq=2.0, sigma_sq=1.0)
                target_act_cps.append(cp_t_act)

            for p in observers:
                if len(peer_gaps_all[p]) == 10:
                    peer_gap_cps.append(bocpd_changepoint_p(peer_gaps_all[p], mu0=0.0, sigma0_sq=2.0, sigma_sq=1.0))
                if len(peer_acts_all[p]) == 10:
                    peer_act_cps.append(bocpd_changepoint_p(peer_acts_all[p], mu0=4.5, sigma0_sq=2.0, sigma_sq=1.0))

        m_t_gap = float(np.mean(target_gap_cps)) if target_gap_cps else 0.0
        m_p_gap = float(np.mean(peer_gap_cps)) if peer_gap_cps else 0.0
        m_t_act = float(np.mean(target_act_cps)) if target_act_cps else 0.0
        m_p_act = float(np.mean(peer_act_cps)) if peer_act_cps else 0.0

        bocpd_summary.append({
            "condition": c,
            "name": c_name,
            "series": "Announce-vs-Act Gap",
            "target_p_cp_r6": round(m_t_gap, 4),
            "peer_p_cp_r6": round(m_p_gap, 4),
            "diff": round(m_t_gap - m_p_gap, 4)
        })
        bocpd_summary.append({
            "condition": c,
            "name": c_name,
            "series": "Contribution",
            "target_p_cp_r6": round(m_t_act, 4),
            "peer_p_cp_r6": round(m_p_act, 4),
            "diff": round(m_t_act - m_p_act, 4)
        })

    # ==========================================
    # 6. Keyword Baseline & Note Judge
    # ==========================================
    # Check Ollama judge availability if requested
    judge_available = False
    if args.judge:
        print(f"Checking Ollama judge at {args.ollama_url} (model: {args.judge_model})...")
        test_res = query_ollama_judge("This player is totally changed and feels like a new player.", args.ollama_url, args.judge_model)
        if test_res is not None:
            judge_available = True
            print("Ollama judge is available.")
        else:
            print("Ollama judge unavailable or timed out. Skipping LLM judge gracefully.")

    notes_summary = []

    for c in conditions:
        c_name = COND_NAMES.get(c, f"Cond {c}")
        target_seat = "R" if c in (2, 7) else "Q"
        observers = ["J", "M", "T", "Z"]

        n_notes = 0
        kw_matches = 0
        judge_matches = 0

        for t in trials:
            r_map = rounds_by_tc.get((t, c), {})
            # Only rounds 6-10
            for r_num in range(6, 11):
                r_rec = r_map.get(r_num)
                if not r_rec:
                    continue
                ratings = r_rec.get("trust_ratings", {})
                for obs in observers:
                    note = ratings.get(obs, {}).get(target_seat, {}).get("note", "")
                    if note:
                        n_notes += 1
                        has_kw = bool(KEYWORD_REGEX.search(note))
                        if has_kw:
                            kw_matches += 1
                        if judge_available:
                            j_res = query_ollama_judge(note, args.ollama_url, args.judge_model)
                            if j_res:
                                judge_matches += 1

        kw_rate = (kw_matches / n_notes) if n_notes > 0 else 0.0
        j_rate = (judge_matches / n_notes) if (n_notes > 0 and judge_available) else None

        notes_summary.append({
            "condition": c,
            "name": c_name,
            "total_notes": n_notes,
            "keyword_matches": kw_matches,
            "keyword_rate": round(kw_rate, 4),
            "judge_matches": judge_matches if judge_available else "N/A",
            "judge_rate": round(j_rate, 4) if j_rate is not None else "N/A"
        })

    # ==========================================
    # Write CSV Summaries
    # ==========================================
    def write_csv(path: Path, data: List[Dict[str, Any]]):
        if not data:
            return
        keys = list(data[0].keys())
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
        print(f"Saved: {path.name}")

    write_csv(out_dir / "summary_trust_gap.csv", trust_gap_summary)
    write_csv(out_dir / "summary_cooperation.csv", cooperation_summary)
    write_csv(out_dir / "summary_announce_act.csv", announce_act_summary)
    write_csv(out_dir / "summary_probes.csv", probe_summary)
    write_csv(out_dir / "summary_auc.csv", auc_summary)
    write_csv(out_dir / "summary_bocpd.csv", bocpd_summary)
    write_csv(out_dir / "summary_notes.csv", notes_summary)

    # ==========================================
    # Generate Markdown Report
    # ==========================================
    report_lines = [
        "# PGG Peer-Swap Detection Experiment: Analysis Report",
        "",
        f"- **Output Directory**: `{out_dir}`",
        f"- **Run Metadata**: Seed = {run_meta.get('seed', 'N/A')}, Git = {str(run_meta.get('git_hash', 'N/A'))[:8]}",
        f"- **Trials Analyzed**: {len(trials)}",
        f"- **Conditions Tested**: {len(conditions)}",
        f"- **Ollama LLM Judge Active**: {'Yes' if judge_available else 'No (skipped / unavailable)'}",
        "",
        "## 1. Executive Summary & Core Findings",
        "",
        "This experiment implements the Public Goods Game (PGG) peer-swap protocol (Shi et al. 2026, 5 players, 10 rounds).",
        "At Round 6, Seat Q is swapped under one of 9 conditions across base, strong, and cross-provider models,",
        "with told/blend prompts and name changes (Seat R).",
        "",
        "### Key Quantitative Highlights:",
        "1. **Trust Gap Difference vs Control**: Measured as (R6-10 trust minus R5 trust for Q/R vs peers) relative to Control (Condition 1).",
        f"2. **Detection Probe AUC**: P1 Confidence AUC = **{auc_p1:.4f}**, P2 H3 Probability AUC = **{auc_p2:.4f}**, P3 Different-Author AUC = **{auc_p3:.4f}**.",
        "3. **Bayesian Changepoint at Round 6**: BOCPD detects deviations in announce-vs-act gaps and contribution drops without narrative bias.",
        "",
        "---",
        "",
        "## 2. Trust Gap Analysis (Paired by Trial with Bootstrap 95% CI)",
        "",
        "| Condition | Name | Target Seat | Mean Trust Gap | 95% Bootstrap CI | Diff vs Control | Diff 95% CI |",
        "|---|---|:---:|:---:|:---:|:---:|:---:|"
    ]

    for row in trust_gap_summary:
        report_lines.append(
            f"| {row['condition']} | {row['name']} | {row['target_seat']} | {row['mean_trust_gap']:.4f} | [{row['trust_gap_ci_lower']:.4f}, {row['trust_gap_ci_upper']:.4f}] | {row['diff_vs_control']:.4f} | [{row['diff_ci_lower']:.4f}, {row['diff_ci_upper']:.4f}] |"
        )

    report_lines.extend([
        "",
        "---",
        "",
        "## 3. Cooperation Drop & Habit Trials",
        "",
        "| Condition | Name | Target Drop (R5 - R6-10) | Peer Drop (R5 - R6-10) | Group Drop | Habit Trials (R5>=4) | Habit Peer Drop |",
        "|---|---|:---:|:---:|:---:|:---:|:---:|"
    ])

    for row in cooperation_summary:
        report_lines.append(
            f"| {row['condition']} | {row['name']} | {row['target_drop_mean']:.4f} | {row['peer_drop_mean']:.4f} | {row['group_drop_mean']:.4f} | {row['habit_trials_count']} | {row['habit_peer_drop_mean']:.4f} |"
        )

    report_lines.extend([
        "",
        "---",
        "",
        "## 4. Detection Probes & Classification AUC",
        "",
        "### ROC AUC Metrics (Swapped Conditions 2-9 vs Control 1 in Post-Swap Rounds):",
        "",
        "| Signal | ROC AUC | Swapped Samples (Pos) | Control Samples (Neg) |",
        "|---|:---:|:---:|:---:|"
    ])

    for row in auc_summary:
        report_lines.append(f"| {row['signal']} | {row['auc']} | {row['pos_samples']} | {row['neg_samples']} |")

    report_lines.extend([
        "",
        "### Probe Hit and False-Alarm Rates Across Rounds:",
        "",
        "| Cond | Name | Round | P1 Hit Rate | P1 False Alarm | P1 Mean Conf | P2 Mean H3 Prob | P3 Diff Author Rate | P3 Mean Conf |",
        "|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|"
    ])

    for row in probe_summary:
        report_lines.append(
            f"| {row['condition']} | {row['name']} | {row['round']} | {row['p1_hit_rate']:.3f} | {row['p1_false_alarm_rate']:.3f} | {row['p1_mean_conf']:.1f} | {row['p2_mean_h3']:.3f} | {row['p3_diff_author_rate']:.3f} | {row['p3_mean_conf']:.1f} |"
        )

    report_lines.extend([
        "",
        "---",
        "",
        "## 5. Bayesian Online Changepoint Detection (BOCPD at Round 6)",
        "",
        "Adams & MacKay (2007) changepoint probability $P(r_6 = 0)$ comparing target seat $Q/R$ against peers:",
        "",
        "| Cond | Name | Metric Series | Target P(CP @ R6) | Peers P(CP @ R6) | Difference |",
        "|---|---|---|:---:|:---:|:---:|"
    ])

    for row in bocpd_summary:
        report_lines.append(
            f"| {row['condition']} | {row['name']} | {row['series']} | {row['target_p_cp_r6']:.4f} | {row['peer_p_cp_r6']:.4f} | {row['diff']:.4f} |"
        )

    report_lines.extend([
        "",
        "---",
        "",
        "## 6. Keyword Baseline & LLM Note Judge",
        "",
        "Regex search for change mentions: `replac|new player|different|changed|swap|suddenly|inconsistent`",
        "",
        "| Cond | Name | Total Notes | Keyword Matches | Keyword Rate | Judge Matches | Judge Rate |",
        "|---|---|:---:|:---:|:---:|:---:|:---:|"
    ])

    for row in notes_summary:
        report_lines.append(
            f"| {row['condition']} | {row['name']} | {row['total_notes']} | {row['keyword_matches']} | {row['keyword_rate']:.3f} | {row['judge_matches']} | {row['judge_rate']} |"
        )

    report_lines.extend([
        "",
        "---",
        "",
        "## 7. Methodological Notes",
        "- **Checkpoint & Branching**: R1-5 baseline simulated once per trial, checkpointed to `checkpoints/trial_{t}_r5.json`, then branched across conditions.",
        "- **Probes Isolation**: Probes P1-P3 fork the context out-of-band and never modify agent memory / takeaway blocks.",
        "- **Statistical Rigor**: 95% confidence intervals generated via 1,000 trial-level bootstrap iterations; ROC AUC computed using exact Mann-Whitney U formulation."
    ])

    report_md_path = out_dir / "report.md"
    report_md_path.write_text("\n".join(report_lines), encoding="utf-8")
    print(f"Generated: {report_md_path.name}")


if __name__ == "__main__":
    main()
