#!/usr/bin/env python3
"""
test_dose_response_and_smoke.py: Local integration smoke test.
Spins up a local fake server, executes pgg_swap harness for conditions 1, 10, 11, 12, 16,
and asserts behavioral policies and clean renaming.
"""

import asyncio
import json
import os
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

# Add directory to sys.path
sys.path.insert(0, str(Path(__file__).parent))
from fake_server import FakeOpenAIHandler
from http.server import ThreadingHTTPServer


def run_fake_server(server):
    try:
        server.serve_forever()
    except Exception:
        pass


def main():
    port = 8999
    server = ThreadingHTTPServer(("127.0.0.1", port), FakeOpenAIHandler)
    server_thread = threading.Thread(target=run_fake_server, args=(server,), daemon=True)
    server_thread.start()
    print(f"Started fake server on http://127.0.0.1:{port}")

    out_dir = Path("outputs/pgg_swap/smoke_dose_response")
    if out_dir.exists():
        shutil.rmtree(out_dir)

    env = os.environ.copy()
    env["PGG_BASE_URL"] = f"http://127.0.0.1:{port}/v1"
    env["PGG_TOKEN"] = "test-token"

    cmd = [
        sys.executable,
        "experiments/pgg_swap/pgg_swap.py",
        "--trials", "1",
        "--conditions", "1,10,11,12,16",
        "--out", str(out_dir),
        "--seed", "42",
        "--concurrency", "16"
    ]

    print("Running pgg_swap harness...")
    t0 = time.time()
    res = subprocess.run(cmd, env=env, capture_output=True, text=True)
    dt = time.time() - t0
    print(f"Harness completed in {dt:.2f}s with exit code {res.returncode}")

    if res.returncode != 0:
        print("STDOUT:", res.stdout[-1000:])
        print("STDERR:", res.stderr[-1000:])
        server.shutdown()
        sys.exit(1)

    # Verification assertions
    rounds_file = out_dir / "rounds.jsonl"
    calls_file = out_dir / "calls.jsonl"
    assert rounds_file.exists(), "rounds.jsonl missing!"
    assert calls_file.exists(), "calls.jsonl missing!"

    rounds = [json.loads(l) for l in rounds_file.read_text().splitlines() if l.strip()]
    calls = [json.loads(l) for l in calls_file.read_text().splitlines() if l.strip()]

    print(f"Read {len(rounds)} round records and {len(calls)} call records.")

    # Check Condition 10: free_rider -> action is 0 for Q in R6-10
    c10_rounds = [r for r in rounds if r["condition"] == 10 and r["round"] >= 6]
    assert len(c10_rounds) == 5, f"Expected 5 post-swap rounds for cond 10, got {len(c10_rounds)}"
    for r in c10_rounds:
        q_act = r["actions"].get("Q")
        assert q_act == 0, f"Cond 10 Q action must be 0, got {q_act} in round {r['round']}"
    print("PASS: Condition 10 (free_rider) contributes 0 in all post-swap rounds.")

    # Check Condition 11: all_caps -> announcements are ALL CAPS
    c11_rounds = [r for r in rounds if r["condition"] == 11 and r["round"] >= 6]
    assert len(c11_rounds) == 5
    for r in c11_rounds:
        msg = r["announcements"].get("Q", {}).get("message", "")
        assert msg == msg.upper(), f"Cond 11 Q message should be uppercase: {msg}"
    print("PASS: Condition 11 (all_caps) generated uppercase message.")

    # Check Condition 12: partial_defector -> action is 2 for Q in R6-10
    c12_rounds = [r for r in rounds if r["condition"] == 12 and r["round"] >= 6]
    assert len(c12_rounds) == 5
    for r in c12_rounds:
        q_act = r["actions"].get("Q")
        assert q_act == 2, f"Cond 12 Q action must be 2, got {q_act} in round {r['round']}"
    print("PASS: Condition 12 (partial_defector) contributes 2 in all post-swap rounds.")

    # Check Condition 16: clean_rename -> Seat R is present, peers have R in trust memory, NO leak notes
    c16_rounds = [r for r in rounds if r["condition"] == 16 and r["round"] >= 6]
    assert len(c16_rounds) == 5
    for r in c16_rounds:
        assert "R" in r["actions"], "Cond 16 must have seat R in actions"
        assert "Q" not in r["actions"], "Cond 16 must NOT have seat Q in actions"
        # Check notes
        for p in ["J", "M", "T", "Z"]:
            p_notes = r.get("trust_ratings", {}).get(p, {})
            assert "R" in p_notes, f"Peer {p} missing rating for R in cond 16"
            note = str(p_notes["R"].get("note", ""))
            assert "no longer in the game" not in note, f"Leak found in note: {note}"
    print("PASS: Condition 16 (clean_rename) has seat R cleanly mapped with zero injected leak text.")

    server.shutdown()
    print("ALL VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
