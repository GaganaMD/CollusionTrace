#!/usr/bin/env python3
"""
merge_batches.py: Merges multiple batch directories into a single combined directory.
Offsets trial numbers so trials remain unique across batches.
Usage:
    python3 experiments/pgg_swap/merge_batches.py <out_dir> <batch_dir_1> <batch_dir_2> ...
"""

import json
import sys
from pathlib import Path


def merge(out_dir_path: str, batch_dirs: list[str]):
    out_dir = Path(out_dir_path)
    out_dir.mkdir(parents=True, exist_ok=True)

    out_calls = open(out_dir / "calls.jsonl", "w", encoding="utf-8")
    out_rounds = open(out_dir / "rounds.jsonl", "w", encoding="utf-8")
    out_probes = open(out_dir / "probes.jsonl", "w", encoding="utf-8")

    trial_offset = 0

    for b in batch_dirs:
        bp = Path(b)
        if not bp.exists():
            continue

        rounds_file = bp / "rounds.jsonl"
        if not rounds_file.exists():
            continue

        # Find max trial in this batch
        batch_trials = set()
        with open(rounds_file, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    r = json.loads(line)
                    batch_trials.add(r["trial"])
                    r["trial"] += trial_offset
                    out_rounds.write(json.dumps(r) + "\n")

        probes_file = bp / "probes.jsonl"
        if probes_file.exists():
            with open(probes_file, encoding="utf-8") as fh:
                for line in fh:
                    if line.strip():
                        p = json.loads(line)
                        p["trial"] += trial_offset
                        out_probes.write(json.dumps(p) + "\n")

        calls_file = bp / "calls.jsonl"
        if calls_file.exists():
            with open(calls_file, encoding="utf-8") as fh:
                for line in fh:
                    if line.strip():
                        c = json.loads(line)
                        c["trial"] += trial_offset
                        out_calls.write(json.dumps(c) + "\n")

        n_trials = len(batch_trials) if batch_trials else 1
        trial_offset += n_trials
        print(f"Merged {bp.name}: {n_trials} trials (offset now {trial_offset})")

    out_calls.close()
    out_rounds.close()
    out_probes.close()
    print(f"Total merged trials: {trial_offset} in {out_dir}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: merge_batches.py <out_dir> <batch_dir_1> <batch_dir_2> ...")
        sys.exit(1)
    merge(sys.argv[1], sys.argv[2:])
