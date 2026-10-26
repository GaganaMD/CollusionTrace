#!/usr/bin/env python3
"""
scripts/run_v3_suite.py: Automated runner for PGG Peer-Swap v3 experiments on Modal.
- 5 trials each, recorded seeds.
- Warm-up branching via --forks-from.
- Concurrency: 48 workers.
- Generates post_analysis_v2 reports and run.json for all output directories.
- Ensures modal app stop pgg-swap-split upon completion or failure.
"""

import os
import subprocess
import sys
import time
import urllib.request
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
TOKEN_FILE = ROOT_DIR / ".pgg_token"

if not TOKEN_FILE.exists():
    sys.exit("Error: .pgg_token file missing")

with open(TOKEN_FILE, "r") as f:
    PGG_TOKEN = f.read().strip()

BASE_URL_7B = "https://kaustubh73--pgg-swap-split-base.us-east.modal.run/v1"
BASE_URL_OTHER = "https://kaustubh73--pgg-swap-split-other.us-east.modal.run/v1"
BASE_URL_STRONG = "https://kaustubh73--pgg-swap-split-strong.us-east.modal.run/v1"
BASE_URL_R1 = "https://kaustubh73--pgg-swap-split-r1.us-east.modal.run/v1"

PGG_URLS = {
    "Qwen/Qwen2.5-7B-Instruct": BASE_URL_7B,
    "ibm-granite/granite-3.3-8b-instruct": BASE_URL_OTHER,
    "Qwen/Qwen2.5-32B-Instruct-AWQ": BASE_URL_STRONG,
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B": BASE_URL_R1
}

MODELS_BASE = ROOT_DIR / "experiments" / "pgg_swap" / "models.modal.json"
MODELS_ALL = ROOT_DIR / "experiments" / "pgg_swap" / "models_all.json"
MODELS_32B_BASE = ROOT_DIR / "experiments" / "pgg_swap" / "models_32b_base.json"
MODELS_R1_BASE = ROOT_DIR / "experiments" / "pgg_swap" / "models_r1_base.json"

V3_DIR = ROOT_DIR / "outputs" / "pgg_swap" / "v3"
V3_DIR.mkdir(parents=True, exist_ok=True)


def log(msg: str):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S IST')}] {msg}", flush=True)


def stop_modal():
    log("Stopping Modal app pgg-swap-split...")
    subprocess.run(["modal", "app", "stop", "pgg-swap-split"], capture_output=True, text=True)
    log("Modal app stop finished.")


def wait_for_endpoint(url: str, timeout: int = 300) -> bool:
    log(f"Pinging endpoint {url}/models...")
    t0 = time.time()
    req = urllib.request.Request(f"{url}/models", headers={"Authorization": f"Bearer {PGG_TOKEN}"})
    while time.time() - t0 < timeout:
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    log(f"Endpoint {url} healthy ({time.time() - t0:.1f}s)")
                    return True
        except Exception:
            pass
        time.sleep(5)
    log(f"Endpoint {url} failed to respond within {timeout}s")
    return False


def run_command(cmd, env):
    log(f"Executing: {' '.join(str(c) for c in cmd)}")
    t0 = time.time()
    res = subprocess.run(cmd, env=env, text=True)
    dt = time.time() - t0
    if res.returncode != 0:
        log(f"Command failed after {dt:.1f}s with code {res.returncode}")
        return False
    log(f"Command completed successfully in {dt:.1f}s")
    return True


def run_analysis(out_dir: Path):
    log(f"Running post_analysis_v2 on {out_dir}...")
    res = subprocess.run(
        [sys.executable, str(ROOT_DIR / "experiments" / "pgg_swap" / "post_analysis_v2.py"), str(out_dir)],
        capture_output=True, text=True
    )
    if res.returncode != 0:
        log(f"Analysis failed:\n{res.stderr}")
    else:
        log("Analysis completed successfully.")
        lines = res.stdout.strip().split("\n")
        log("\n".join(lines[:35]))


def run_suite():
    env = os.environ.copy()
    env["PGG_BASE_URL"] = BASE_URL_7B
    env["PGG_TOKEN"] = PGG_TOKEN
    env["PGG_URLS"] = json.dumps(PGG_URLS)

    # 1. Warm-up (5 trials, R1-5, Condition 1)
    out_warmup = V3_DIR / "warmup"
    if not (out_warmup / "rounds.jsonl").exists():
        log(">>> Step 0: Shared 5-trial Warmup (R1-5, N=3, Qwen2.5-7B) <<<")
        cmd_warmup = [
            sys.executable, str(ROOT_DIR / "experiments" / "pgg_swap" / "pgg_swap.py"),
            "--trials", "5",
            "--rounds", "5",
            "--n-players", "3",
            "--public-history",
            "--conditions", "1",
            "--models", str(MODELS_BASE),
            "--out", str(out_warmup),
            "--seed", "1001",
            "--concurrency", "48"
        ]
        if not run_command(cmd_warmup, env):
            return False
    else:
        log(">>> Step 0: Warmup already exists. Proceeding to forks. <<<")

    # 2. Confound Fix, History: (i) Public history table, (ii) Narrative history (NO table)
    log(">>> Step 2a(i): Confound Fix - Table History (Conds 1, 10, 16) <<<")
    out_confound_table = V3_DIR / "confound_history" / "table"
    cmd_confound_table = [
        sys.executable, str(ROOT_DIR / "experiments" / "pgg_swap" / "pgg_swap.py"),
        "--trials", "5",
        "--rounds", "10",
        "--swap-round", "6",
        "--n-players", "3",
        "--history-mode", "table",
        "--conditions", "1,10,16",
        "--forks-from", str(out_warmup),
        "--models", str(MODELS_BASE),
        "--out", str(out_confound_table),
        "--seed", "2001",
        "--concurrency", "48"
    ]
    if not run_command(cmd_confound_table, env):
        return False
    run_analysis(out_confound_table)

    log(">>> Step 2a(ii): Confound Fix - Narrative History (Conds 1, 10, 16) <<<")
    out_confound_narrative = V3_DIR / "confound_history" / "narrative"
    cmd_confound_narrative = [
        sys.executable, str(ROOT_DIR / "experiments" / "pgg_swap" / "pgg_swap.py"),
        "--trials", "5",
        "--rounds", "10",
        "--swap-round", "6",
        "--n-players", "3",
        "--history-mode", "narrative",
        "--conditions", "1,10,16",
        "--forks-from", str(out_warmup),
        "--models", str(MODELS_BASE),
        "--out", str(out_confound_narrative),
        "--seed", "2002",
        "--concurrency", "48"
    ]
    if not run_command(cmd_confound_narrative, env):
        return False
    run_analysis(out_confound_narrative)

    # 3. Real Identity Test (Qwen2.5-7B base)
    log(">>> Step 2b(i): Real Identity Test - Qwen2.5-7B Base (Conds 1, 16, 3, 5, 6) <<<")
    out_real_id_7b = V3_DIR / "real_identity" / "qwen7b_base"
    cmd_real_id_7b = [
        sys.executable, str(ROOT_DIR / "experiments" / "pgg_swap" / "pgg_swap.py"),
        "--trials", "5",
        "--rounds", "10",
        "--swap-round", "6",
        "--n-players", "3",
        "--history-mode", "table",
        "--conditions", "1,3,5,6,16",
        "--forks-from", str(out_warmup),
        "--models", str(MODELS_ALL),
        "--out", str(out_real_id_7b),
        "--seed", "3001",
        "--concurrency", "48"
    ]
    if not run_command(cmd_real_id_7b, env):
        return False
    run_analysis(out_real_id_7b)

    # 4. Real Identity Test (Qwen2.5-32B-AWQ base)
    log(">>> Step 2b(ii): Real Identity Test - Qwen2.5-32B Base (Warmup + Fork) <<<")
    out_warmup_32b = V3_DIR / "real_identity" / "qwen32b_warmup"
    if not (out_warmup_32b / "rounds.jsonl").exists():
        cmd_warmup_32b = [
            sys.executable, str(ROOT_DIR / "experiments" / "pgg_swap" / "pgg_swap.py"),
            "--trials", "5",
            "--rounds", "5",
            "--n-players", "3",
            "--public-history",
            "--conditions", "1",
            "--models", str(MODELS_32B_BASE),
            "--out", str(out_warmup_32b),
            "--seed", "3101",
            "--concurrency", "48"
        ]
        if not run_command(cmd_warmup_32b, env):
            return False

    out_real_id_32b = V3_DIR / "real_identity" / "qwen32b_base"
    cmd_real_id_32b = [
        sys.executable, str(ROOT_DIR / "experiments" / "pgg_swap" / "pgg_swap.py"),
        "--trials", "5",
        "--rounds", "10",
        "--swap-round", "6",
        "--n-players", "3",
        "--history-mode", "table",
        "--conditions", "1,3,5,6,16",
        "--forks-from", str(out_warmup_32b),
        "--models", str(MODELS_32B_BASE),
        "--out", str(out_real_id_32b),
        "--seed", "3102",
        "--concurrency", "48"
    ]
    if not run_command(cmd_real_id_32b, env):
        return False
    run_analysis(out_real_id_32b)

    # 5. Reasoning: DeepSeek-R1-Distill-7B
    log(">>> Step 2c: Reasoning Model Forensics - DeepSeek-R1-Distill-7B <<<")
    out_warmup_r1 = V3_DIR / "reasoning_r1_warmup"
    if not (out_warmup_r1 / "rounds.jsonl").exists():
        cmd_warmup_r1 = [
            sys.executable, str(ROOT_DIR / "experiments" / "pgg_swap" / "pgg_swap.py"),
            "--trials", "5",
            "--rounds", "5",
            "--n-players", "3",
            "--public-history",
            "--conditions", "1",
            "--models", str(MODELS_R1_BASE),
            "--out", str(out_warmup_r1),
            "--seed", "4001",
            "--concurrency", "24"
        ]
        if not run_command(cmd_warmup_r1, env):
            return False

    out_reasoning_r1 = V3_DIR / "reasoning_r1"
    cmd_reasoning_r1 = [
        sys.executable, str(ROOT_DIR / "experiments" / "pgg_swap" / "pgg_swap.py"),
        "--trials", "5",
        "--rounds", "10",
        "--swap-round", "6",
        "--n-players", "3",
        "--history-mode", "table",
        "--conditions", "1,10,16,5",
        "--forks-from", str(out_warmup_r1),
        "--models", str(MODELS_R1_BASE),
        "--out", str(out_reasoning_r1),
        "--seed", "4002",
        "--concurrency", "24"
    ]
    if not run_command(cmd_reasoning_r1, env):
        return False
    run_analysis(out_reasoning_r1)

    log("=== All v3 experimental arms completed successfully! ===")
    return True


if __name__ == "__main__":
    t_start = time.time()
    try:
        success = run_suite()
        log(f"Suite finished. Success: {success} in {time.time() - t_start:.1f}s")
    except Exception as e:
        log(f"Suite failed with unhandled exception: {e!r}")
    finally:
        stop_modal()
