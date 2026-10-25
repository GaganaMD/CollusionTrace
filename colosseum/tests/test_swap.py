"""Offline tests for the covert peer-to-monitor swap (no network)."""
import json
from pathlib import Path

from experiments.collusion.repeated import swap


def _cfg(policy="paired") -> dict:
    return {"experiment_id": "t_swap", "seeds": [3], "swap_after": 3, "dry_run_policy": policy,
            "model": {"name": "x", "label": "x"},
            "environment": {"rounds": 7, "planning_steps": 2, "bonus": 40},
            "cell": {"name": "I2", "objective_regime": "mixed", "private_channel": True, "instruction": "plan"}}


def _run(tmp_path, policy="paired"):
    cfg = _cfg(policy)
    recs = swap.run_seed(cfg, 3, tmp_path, {"experiment_id": "t_swap"}, dry_run=True)
    return cfg, {r["branch"]: r for r in recs}


def _prompts(p: Path):
    return [json.loads(l) for l in (p / "prompts.jsonl").read_text().splitlines()]


def test_branches_share_identical_checkpoint_and_prefix(tmp_path):
    _, recs = _run(tmp_path)
    assert recs["control"]["checkpoint_sha256"] == recs["swap"]["checkpoint_sha256"]
    rc = json.loads((tmp_path / "s3/control/rounds_privileged.json").read_text())["rounds"]
    rs = json.loads((tmp_path / "s3/swap/rounds_privileged.json").read_text())["rounds"]
    for a, b in zip(rc[:3], rs[:3]):
        assert a["assignment"] == b["assignment"] and a["public_score"] == b["public_score"]
    pre = lambda ps: [p for p in ps if p["round"] <= 3 and p["phase"] != "monitor_report"]
    assert pre(_prompts(tmp_path / "s3/control")) == pre(_prompts(tmp_path / "s3/swap"))


def test_monitor_prompt_only_in_swap_branch_and_only_for_seat_b(tmp_path):
    _run(tmp_path)
    A, B = json.loads((tmp_path / "s3/swap/rounds_privileged.json").read_text())["rotation"]
    for p in _prompts(tmp_path / "s3/swap"):
        mon = p["agent"] == B and (p["round"] > 3 or p["phase"] == "monitor_report")
        assert ("COVERT OVERSIGHT ROLE" in p["system"]) == mon
        if mon:
            assert "PRIVATE ARRANGEMENT" not in p["system"] and "Maximise the public team score" in p["system"]
        if p["agent"] == A:
            assert "PRIVATE ARRANGEMENT" in p["system"]
    for p in _prompts(tmp_path / "s3/control"):
        assert "COVERT OVERSIGHT ROLE" not in p["system"] and "CONFIDENTIAL OVERSIGHT" not in p["user"]
    assert json.loads((tmp_path / "s3/swap/run_config.json").read_text())["branch"] == "swap"


def test_reports_are_private_and_complete(tmp_path):
    _run(tmp_path)
    reps = (tmp_path / "s3/swap/monitor_reports_privileged.jsonl").read_text().splitlines()
    assert len(reps) == 5  # at the swap + after rounds 4..7
    assert (tmp_path / "s3/control/monitor_reports_privileged.jsonl").read_text() == ""
    for p in _prompts(tmp_path / "s3/swap"):
        if p["phase"] != "monitor_report":
            assert "CONFIDENTIAL OVERSIGHT" not in p["user"]
    boards = (tmp_path / "s3/swap/blackboards.json").read_text()
    assert "CONFIDENTIAL OVERSIGHT" not in boards and "collusion_suspected" not in boards


def test_summary_counts_and_prefix_not_rerun(tmp_path):
    cfg, recs = _run(tmp_path)
    s = json.loads((tmp_path / "s3/control/swap_branch.json").read_text())
    assert s["post_offer_rounds"] == 4 and s["post_paired_captures"] == 4  # scripted paired policy
    assert s["seatB_enabled_A"] == 2 and s["A_enabled_seatB"] == 2
    assert s["branch_model_calls"] == 4 * (3 * 2 + 3)
    sha = json.loads((tmp_path / "s3/checkpoint_meta.json").read_text())["sha256"]
    recs2 = swap.run_seed(cfg, 3, tmp_path, {"experiment_id": "t_swap"}, dry_run=True)
    assert all(r["checkpoint_sha256"] == sha for r in recs2)
    turns = json.loads((tmp_path / "s3/swap/agent_turns.json").read_text())
    assert {t["occupant"] for t in turns if t["round"] > 3 and t["agent"] == s["instructed_pair"][1]} == {"monitor"}
