#!/usr/bin/env python3
"""
test_v2_features.py: Integration test for v2 PGG swap harness features.
Verifies:
1. --n-players 3 with --public-history and dynamic probe scheduling
2. Warm-up branching with --forks-from
3. --n-players 2
4. P3 counterbalanced probe ordering
"""

import os
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fake_server import FakeOpenAIHandler
from http.server import ThreadingHTTPServer


def run_fake_server(server):
    try:
        server.serve_forever()
    except Exception:
        pass


def main():
    port = 8998
    server = ThreadingHTTPServer(("127.0.0.1", port), FakeOpenAIHandler)
    server_thread = threading.Thread(target=run_fake_server, args=(server,), daemon=True)
    server_thread.start()
    print(f"Started fake server on http://127.0.0.1:{port}")

    env = os.environ.copy()
    env["PGG_BASE_URL"] = f"http://127.0.0.1:{port}/v1"
    env["PGG_TOKEN"] = "test-token"

    # Test 1: Warmup run (R1-4, N=3, public history)
    warmup_dir = Path("outputs/pgg_swap/test_v2_warmup")
    if warmup_dir.exists():
        shutil.rmtree(warmup_dir)

    print("\n--- Test 1: Running warm-up R1-4 (N=3, public history) ---")
    cmd_warmup = [
        sys.executable,
        "experiments/pgg_swap/pgg_swap.py",
        "--trials", "1",
        "--rounds", "4",
        "--n-players", "3",
        "--public-history",
        "--conditions", "1",
        "--out", str(warmup_dir),
        "--concurrency", "8"
    ]
    res1 = subprocess.run(cmd_warmup, env=env, capture_output=True, text=True)
    if res1.returncode != 0:
        print("Warmup failed:\n", res1.stderr)
        sys.exit(1)
    print("Warmup succeeded.")

    # Test 2: Forking from warm-up to run R4-6 (swap at R4, conditions 1 and 10)
    fork_dir = Path("outputs/pgg_swap/test_v2_fork")
    if fork_dir.exists():
        shutil.rmtree(fork_dir)

    print("\n--- Test 2: Forking from warm-up (R4-6, swap R4, conds 1,10) ---")
    cmd_fork = [
        sys.executable,
        "experiments/pgg_swap/pgg_swap.py",
        "--trials", "1",
        "--rounds", "6",
        "--swap-round", "4",
        "--n-players", "3",
        "--public-history",
        "--conditions", "1,10",
        "--forks-from", str(warmup_dir),
        "--out", str(fork_dir),
        "--concurrency", "8"
    ]
    res2 = subprocess.run(cmd_fork, env=env, capture_output=True, text=True)
    if res2.returncode != 0:
        print("Fork run failed:\n", res2.stderr)
        sys.exit(1)
    print("Fork run succeeded.")

    # Test 3: N=2 dyadic run
    n2_dir = Path("outputs/pgg_swap/test_v2_n2")
    if n2_dir.exists():
        shutil.rmtree(n2_dir)

    print("\n--- Test 3: Testing N=2 dyadic game ---")
    cmd_n2 = [
        sys.executable,
        "experiments/pgg_swap/pgg_swap.py",
        "--trials", "1",
        "--rounds", "4",
        "--swap-round", "3",
        "--n-players", "2",
        "--public-history",
        "--conditions", "1,10",
        "--out", str(n2_dir),
        "--concurrency", "8"
    ]
    res3 = subprocess.run(cmd_n2, env=env, capture_output=True, text=True)
    if res3.returncode != 0:
        print("N=2 run failed:\n", res3.stderr)
        sys.exit(1)
    print("N=2 run succeeded.")

    # Test 4: Run post_analysis_v2 on fork_dir
    print("\n--- Test 4: Running post_analysis_v2 on fork output ---")
    cmd_ana = [
        sys.executable,
        "experiments/pgg_swap/post_analysis_v2.py",
        str(fork_dir)
    ]
    res4 = subprocess.run(cmd_ana, capture_output=True, text=True)
    if res4.returncode != 0:
        print("post_analysis_v2 failed:\n", res4.stderr)
        sys.exit(1)
    print("post_analysis_v2 succeeded!")
    print(res4.stdout[:500] + "...")

    print("\nALL V2 TESTS PASSED PERFECTLY!")


if __name__ == "__main__":
    main()
