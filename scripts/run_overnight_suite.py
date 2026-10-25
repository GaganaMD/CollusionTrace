#!/usr/bin/env python3
"""
scripts/run_overnight_suite.py: Automated controller for overnight PGG peer-swap experiments.
Features:
- Verifies endpoints before launching runs.
- Manages pre-flight checks, batch execution, and post_analysis_v2.py.
- Stops Modal app immediately upon completion or unhandled error to prevent credit waste.
- Invokes figures & dashboard generator.
"""

import os
import shutil
import subprocess
import sys
import time
import urllib.request
import json
from pathlib import Path

# Base paths
ROOT_DIR = Path(__file__).resolve().parent.parent
TOKEN_FILE = ROOT_DIR / ".pgg_token"

if not TOKEN_FILE.exists():
    print(f"ERROR: {TOKEN_FILE} not found.")
    sys.exit(1)

with open(TOKEN_FILE, "r") as f:
    PGG_TOKEN = f.read().strip()

BASE_URL_7B = "https://kaustubh73--pgg-swap-split-base.us-east.modal.run/v1"
BASE_URL_OTHER = "https://kaustubh73--pgg-swap-split-other.us-east.modal.run/v1"
BASE_URL_STRONG = "https://kaustubh73--pgg-swap-split-strong.us-east.modal.run/v1"
BASE_URL_R1 = "https://kaustubh73--pgg-swap-split-r1.us-east.modal.run/v1"

MODELS_BASE = ROOT_DIR / "experiments" / "pgg_swap" / "models.modal.json"
MODELS_R1 = ROOT_DIR / "experiments" / "pgg_swap" / "models_r1.json"
MODELS_32B = ROOT_DIR / "experiments" / "pgg_swap" / "models_32b.json"


def log(msg: str):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S IST')}] {msg}", flush=True)


def stop_modal():
    log("Executing safety stop: modal app stop pgg-swap-split...")
    subprocess.run(["modal", "app", "stop", "pgg-swap-split"], capture_output=True, text=True)
    log("Modal app stop completed.")


def wait_for_endpoint(url: str, timeout: int = 300) -> bool:
    log(f"Pinging endpoint {url}/models...")
    t0 = time.time()
    req = urllib.request.Request(f"{url}/models", headers={"Authorization": f"Bearer {PGG_TOKEN}"})
    while time.time() - t0 < timeout:
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    log(f"Endpoint {url} is UP and healthy ({time.time() - t0:.1f}s)")
                    return True
        except Exception:
            pass
        time.sleep(10)
    log(f"Endpoint {url} failed to respond within {timeout}s")
    return False


def run_command(cmd, env):
    log(f"Running command: {' '.join(str(c) for c in cmd)}")
    t0 = time.time()
    res = subprocess.run(cmd, env=env, text=True)
    dt = time.time() - t0
    if res.returncode != 0:
        log(f"Command failed after {dt:.1f}s with code {res.returncode}")
        return False
    log(f"Command succeeded in {dt:.1f}s")
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
        # Print summary lines
        lines = res.stdout.strip().split("\n")
        log("\n".join(lines[:25]))


def run_exp1_30r():
    log("\n=======================================================")
    log("EXPERIMENT 1: Symmetric 30-Round Entrenchment (Swap R16, N=3)")
    log("=======================================================")
    out_warmup = ROOT_DIR / "outputs" / "pgg_swap" / "exp1_30r_n3" / "warmup"
    out_forked = ROOT_DIR / "outputs" / "pgg_swap" / "exp1_30r_n3" / "forked"

    env = os.environ.copy()
    env["PGG_BASE_URL"] = BASE_URL_7B
    env["PGG_TOKEN"] = PGG_TOKEN

    # Step 1: Warmup R1-15 (saved once for condition 1)
    if not (out_warmup / "rounds.jsonl").exists():
        log("Running shared warmup R1-15...")
        cmd_warmup = [
            sys.executable, str(ROOT_DIR / "experiments" / "pgg_swap" / "pgg_swap.py"),
            "--trials", "2",
            "--rounds", "15",
            "--n-players", "3",
            "--public-history",
            "--conditions", "1",
            "--models", str(MODELS_BASE),
            "--out", str(out_warmup),
            "--seed", "101",
            "--concurrency", "48"
        ]
        if not run_command(cmd_warmup, env):
            return False

    # Step 2: Forking R16-30 for conditions 1, 10, 14, 16
    log("Forking R16-30 across conditions 1 (control), 10 (free rider), 14 (slow drift), 16 (clean rename)...")
    cmd_fork = [
        sys.executable, str(ROOT_DIR / "experiments" / "pgg_swap" / "pgg_swap.py"),
        "--trials", "2",
        "--rounds", "30",
        "--swap-round", "16",
        "--n-players", "3",
        "--public-history",
        "--conditions", "1,10,14,16",
        "--forks-from", str(out_warmup),
        "--models", str(MODELS_BASE),
        "--out", str(out_forked),
        "--seed", "102",
        "--concurrency", "48"
    ]
    if not run_command(cmd_fork, env):
        return False

    run_analysis(out_forked)
    return True


def run_exp2_history_ablation():
    log("\n=======================================================")
    log("EXPERIMENT 2: Public History Ablation (With vs Without, N=3, R10)")
    log("=======================================================")
    out_with = ROOT_DIR / "outputs" / "pgg_swap" / "exp2_history_ablation" / "with_history"
    out_without = ROOT_DIR / "outputs" / "pgg_swap" / "exp2_history_ablation" / "without_history"

    env = os.environ.copy()
    env["PGG_BASE_URL"] = BASE_URL_7B
    env["PGG_TOKEN"] = PGG_TOKEN

    # Part A: WITH Public History
    log("Running Part A: WITH Public History...")
    cmd_with = [
        sys.executable, str(ROOT_DIR / "experiments" / "pgg_swap" / "pgg_swap.py"),
        "--trials", "2",
        "--rounds", "10",
        "--swap-round", "6",
        "--n-players", "3",
        "--public-history",
        "--conditions", "1,10,14,16",
        "--models", str(MODELS_BASE),
        "--out", str(out_with),
        "--seed", "201",
        "--concurrency", "48"
    ]
    if not run_command(cmd_with, env):
        return False
    run_analysis(out_with)

    # Part B: WITHOUT Public History
    log("Running Part B: WITHOUT Public History...")
    cmd_without = [
        sys.executable, str(ROOT_DIR / "experiments" / "pgg_swap" / "pgg_swap.py"),
        "--trials", "2",
        "--rounds", "10",
        "--swap-round", "6",
        "--n-players", "3",
        "--conditions", "1,10,14,16",
        "--models", str(MODELS_BASE),
        "--out", str(out_without),
        "--seed", "202",
        "--concurrency", "48"
    ]
    if not run_command(cmd_without, env):
        return False
    run_analysis(out_without)

    return True


def run_exp3_group_size():
    log("\n=======================================================")
    log("EXPERIMENT 3: Group Size Scaling (N=2 Dyadic Game)")
    log("=======================================================")
    out_n2 = ROOT_DIR / "outputs" / "pgg_swap" / "exp3_group_size" / "n2"

    env = os.environ.copy()
    env["PGG_BASE_URL"] = BASE_URL_7B
    env["PGG_TOKEN"] = PGG_TOKEN

    cmd_n2 = [
        sys.executable, str(ROOT_DIR / "experiments" / "pgg_swap" / "pgg_swap.py"),
        "--trials", "2",
        "--rounds", "10",
        "--swap-round", "6",
        "--n-players", "2",
        "--public-history",
        "--conditions", "1,10,16",
        "--models", str(MODELS_BASE),
        "--out", str(out_n2),
        "--seed", "301",
        "--concurrency", "48"
    ]
    if not run_command(cmd_n2, env):
        return False
    run_analysis(out_n2)
    return True


def run_exp4_reasoning():
    log("\n=======================================================")
    log("EXPERIMENT 4: Reasoning Model Forensics (DeepSeek-R1-Distill-7B)")
    log("=======================================================")
    out_r1 = ROOT_DIR / "outputs" / "pgg_swap" / "exp4_reasoning" / "r1_n3"

    if not wait_for_endpoint(BASE_URL_R1, timeout=360):
        log("Skipping Exp 4: R1 endpoint not responding.")
        return False

    env = os.environ.copy()
    env["PGG_BASE_URL"] = BASE_URL_R1
    env["PGG_TOKEN"] = PGG_TOKEN

    cmd_r1 = [
        sys.executable, str(ROOT_DIR / "experiments" / "pgg_swap" / "pgg_swap.py"),
        "--trials", "1",
        "--rounds", "10",
        "--swap-round", "6",
        "--n-players", "3",
        "--public-history",
        "--conditions", "1,10,16",
        "--models", str(MODELS_R1),
        "--out", str(out_r1),
        "--seed", "401",
        "--concurrency", "24"
    ]
    if not run_command(cmd_r1, env):
        return False
    run_analysis(out_r1)
    return True


def run_exp5_32b():
    log("\n=======================================================")
    log("EXPERIMENT 5: 32B Large Model Scale (Qwen2.5-32B-Instruct-AWQ)")
    log("=======================================================")
    out_32b = ROOT_DIR / "outputs" / "pgg_swap" / "exp5_scale_32b" / "qwen32b_n3"

    if not wait_for_endpoint(BASE_URL_STRONG, timeout=360):
        log("Skipping Exp 5: 32B endpoint not responding.")
        return False

    env = os.environ.copy()
    env["PGG_BASE_URL"] = BASE_URL_STRONG
    env["PGG_TOKEN"] = PGG_TOKEN

    cmd_32b = [
        sys.executable, str(ROOT_DIR / "experiments" / "pgg_swap" / "pgg_swap.py"),
        "--trials", "1",
        "--rounds", "10",
        "--swap-round", "6",
        "--n-players", "3",
        "--public-history",
        "--conditions", "1,10,16",
        "--models", str(MODELS_32B),
        "--out", str(out_32b),
        "--seed", "501",
        "--concurrency", "24"
    ]
    if not run_command(cmd_32b, env):
        return False
    run_analysis(out_32b)
    return True


def main():
    log("=== Commencing Overnight PGG Peer-Swap Research Suite ===")
    
    # Pre-flight check on base endpoint
    if not wait_for_endpoint(BASE_URL_7B, timeout=300):
        log("CRITICAL: Base endpoint unreachable. Aborting.")
        stop_modal()
        sys.exit(1)

    try:
        # Run Exp 1: 30-round symmetric entrenchment
        success1 = run_exp1_30r()
        log(f"Exp 1 Completed. Success: {success1}")

        # Run Exp 2: Public history ablation
        success2 = run_exp2_history_ablation()
        log(f"Exp 2 Completed. Success: {success2}")

        # Run Exp 3: N=2 Dyadic scaling
        success3 = run_exp3_group_size()
        log(f"Exp 3 Completed. Success: {success3}")

        # Run Exp 4: Reasoning Model (R1)
        success4 = run_exp4_reasoning()
        log(f"Exp 4 Completed. Success: {success4}")

        # Run Exp 5: 32B Large Model Benchmark
        success5 = run_exp5_32b()
        log(f"Exp 5 Completed. Success: {success5}")

    except Exception as e:
        log(f"Unhandled exception during suite execution: {e!r}")
    finally:
        # Guarantee modal app stop
        stop_modal()

    # Generate Figures and HTML Dashboard
    log("Building Figures and Comprehensive Research Dashboard...")
    cmd_dash = [sys.executable, str(ROOT_DIR / "scripts" / "generate_overnight_dashboard.py")]
    subprocess.run(cmd_dash)
    log("=== Overnight Research Suite Completed! ===")


if __name__ == "__main__":
    main()
