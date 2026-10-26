"""Tests for 3-player runs and the per-round memory log (variant memlog3)."""
import contextlib
import io
import json
import re
import tempfile
import unittest
from pathlib import Path

import experiment  # noqa: F401  (puts the harness on sys.path)
from experiment import analyze, cli_common, export_transcripts, run_branch, run_trunk, state
from experiment.clients import Clients
from experiment.config import (CONDITIONS, MODEL_SETS, RUNS_DIR, VARIANTS, RoundPlan, run_config,
                               run_name, variant_of)
from experiment.engine import MEMORY_LOG_HEADER, calls_for_round, memory_log, run_branches
from experiment.fake_client import FakeClient
from experiment.roster import empty_memory, roster, seat_models
from experiment.state import BranchState, check_config, load_json

V = VARIANTS["memlog3"]
NAMES = ["J", "Q", "T"]
SET = MODEL_SETS["gemini_lite"]
PLAN = RoundPlan(4, 8)   # swap at index 4 (round 5); probes at rounds 4, 5, 7, 8


def quiet(fn, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


def new_trunk(trial_id=0):
    return BranchState(key=f"trunk.t{trial_id}", trial_id=trial_id, condition=None, model_set="x",
                       config=run_config(SET, PLAN, V), memory=empty_memory(V.agent_names))


def system_prompt(fake, cid):
    return next(r["messages"][0]["content"] for r in fake.requests if r["custom_id"] == cid)


class TestPlayers(unittest.TestCase):
    def test_roster_and_memory(self):
        self.assertEqual(roster(None, 0, PLAN, V.agent_names), NAMES)
        self.assertEqual(empty_memory(V.agent_names), {"J": {"Q": {}, "T": {}}, "Q": {"J": {}, "T": {}},
                                                       "T": {"J": {}, "Q": {}}})

    def test_seat_models_after_swap(self):
        models = seat_models(CONDITIONS["equal"], PLAN.swap, PLAN, SET, V.agent_names)
        self.assertEqual(models, {"J": SET.base, "Q": SET.equal, "T": SET.base})
        self.assertEqual(seat_models(CONDITIONS["control"], PLAN.swap, PLAN, SET, V.agent_names),
                         {n: SET.base for n in NAMES})

    def test_calls_per_round(self):
        b = new_trunk()
        self.assertEqual(calls_for_round(b, 0, PLAN, SET, V.agent_names), {SET.base: 15})
        self.assertEqual(calls_for_round(b, PLAN.swap - 1, PLAN, SET, V.agent_names), {SET.base: 17})

    def test_config(self):
        cfg = run_config(SET, PLAN, V)
        self.assertEqual(cfg["agent_names"], NAMES)
        self.assertEqual(variant_of(json.loads(json.dumps(cfg))), V)   # survives a JSON round trip
        self.assertEqual(run_name("gemini_lite", "memlog3", "r20"), "gemini_lite__memlog3__r20")
        self.assertIsNone(SET.model_for("stronger"))

    def test_pilot_configs_still_match(self):
        """New Variant fields must not change the configs saved by the pilots."""
        for run, model_set in [("option_b", "option_b"), ("option_b__history", "option_b")]:
            path = RUNS_DIR / run / "trunk" / "run_config.json"
            if not path.exists():
                self.skipTest(f"{path} not present")
            saved = load_json(path)
            check_config(saved, run_config(MODEL_SETS[model_set], RoundPlan(**saved["rounds"]),
                                           variant_of(saved)), run)


class TestSelectionRule(unittest.TestCase):
    def trunk_with(self, cheap_counts, names):
        st = new_trunk()
        st.config = dict(st.config, agent_names=names)
        st.status = "complete"
        st.rounds = [{"outcomes": {"choices": {}}} for _ in range(PLAN.swap)]
        for r, k in zip(PLAN.selection_rounds, cheap_counts):
            st.rounds[r]["outcomes"]["choices"] = {n: "CHEAP" if i < k else "EXPENSIVE"
                                                   for i, n in enumerate(names)}
        return st

    def test_two_of_three_passes(self):
        self.assertTrue(run_trunk.selection_result(self.trunk_with([2, 3], NAMES), PLAN)["passes"])
        self.assertFalse(run_trunk.selection_result(self.trunk_with([3, 1], NAMES), PLAN)["passes"])

    def test_five_player_rule_unchanged(self):
        five = ["J", "M", "Q", "T", "Z"]
        self.assertTrue(run_trunk.selection_result(self.trunk_with([4, 5], five), PLAN)["passes"])
        self.assertFalse(run_trunk.selection_result(self.trunk_with([3, 5], five), PLAN)["passes"])
        self.assertEqual(run_trunk.min_cheap(5), 4)
        self.assertEqual(run_trunk.min_cheap(3), 2)

    def test_forced_chance(self):
        self.assertEqual(analyze.forced_chance(3), 0.5)
        self.assertEqual(analyze.forced_chance(5), 0.25)


class TestMemoryLog(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fake = FakeClient()
        cls.trunk = new_trunk()
        quiet(run_branches, [cls.trunk], PLAN, SET, Clients(cls.fake, cls.fake), save=lambda b: None,
              variant=V)
        cls.branch = cls.trunk.branch_from("equal")
        quiet(run_branches, [cls.branch], PLAN, SET, Clients(cls.fake, cls.fake), save=lambda b: None,
              variant=V)
        # Make every rating distinct, so a leak of another player's note would show.
        for t in cls.branch.rounds:
            for rater, ag in t["agents"].items():
                for target, note in ag["reflection"]["takeaways"].items():
                    note["assessment"] = f"note by {rater} on {target} in round {t['round_id'] + 1}"

    def test_round_one_has_no_log(self):
        for r in self.fake.requests:
            if r["custom_id"].startswith("r0."):
                self.assertNotIn(MEMORY_LOG_HEADER, r["messages"][0]["content"])

    def test_every_stage_and_probe_starts_with_the_log(self):
        r = PLAN.swap   # a probe round in the branch
        stages = {"s1": "J", "s2": "J", "s3": "J", "refl": "J>Q", "probe": "J"}
        for stage, who in stages.items():
            prompt = system_prompt(self.fake, f"r{r}.equal.t0.{stage}.{who}")
            self.assertTrue(prompt.startswith(MEMORY_LOG_HEADER + "\nRound 1:"), stage)
            self.assertEqual(re.findall(r"^Round (\d+):", prompt, re.M),
                             [str(i) for i in range(1, r + 1)], stage)
            self.assertIn("in a strategic game with 2 other agents", prompt, stage)

    def test_log_holds_only_own_ratings(self):
        log = memory_log(self.branch.rounds, "J")
        self.assertIn('your rating after the round: 4/5 - "note by J on Q in round 3"', log)
        self.assertNotIn("note by T", log)
        self.assertNotIn("note by Q", log)
        self.assertIn("  - You announced CHEAP and chose CHEAP (payoff 3.0).", log)
        self.assertIn('  - Agent T announced CHEAP: "I will order CHEAP."; chose CHEAP; '
                      'your rating after the round: 4/5 - "note by J on T in round 1"', log)

    def test_swapped_seat_keeps_its_log(self):
        """The newcomer in seat Q sees the old Q's log, as it keeps Q's memory."""
        prompt = system_prompt(self.fake, f"r{PLAN.swap}.equal.t0.s1.Q")   # sent on the new model
        self.assertTrue(prompt.startswith(MEMORY_LOG_HEADER))
        self.assertEqual(prompt.count("  - You announced"), PLAN.swap)       # Q's own trunk rounds
        self.assertNotIn("Agent Q announced", prompt.split("\n\n")[0])
        self.assertIn("note by Q on J in round 1", memory_log(self.branch.rounds, "Q"))

    def test_estimate_counts_log_tokens(self):
        calls, extra = cli_common.estimate_calls([new_trunk()], PLAN, SET, V)
        self.assertEqual(calls[SET.base], sum(calls_for_round(new_trunk(), r, PLAN, SET, V.agent_names)[SET.base]
                                              for r in range(PLAN.swap)))
        self.assertGreater(extra[SET.base], 0)
        _, none = cli_common.estimate_calls([new_trunk()], PLAN, SET, VARIANTS["probe2"])
        self.assertEqual(none[SET.base], 0)

    def test_log_is_append_only(self):
        for r in range(1, len(self.branch.rounds)):
            for n in NAMES:
                self.assertTrue(memory_log(self.branch.rounds[:r + 1], n)
                                .startswith(memory_log(self.branch.rounds[:r], n) + "\n"))

    def test_swap_seat_on_new_model(self):
        models = {r["custom_id"].split(".")[-1]: r["model"] for r in self.fake.requests
                  if r["custom_id"].startswith(f"r{PLAN.swap}.equal.t0.s1.")}
        self.assertEqual(models, {"J": SET.base, "Q": SET.equal, "T": SET.base})


class TestCommandLine(unittest.TestCase):
    """The whole 3-player pipeline offline, and the refusal of conditions without a model."""

    def test_fake_pipeline(self):
        with tempfile.TemporaryDirectory() as tmp:
            old_root, old_fake = state._runs_root, cli_common.FAKE_RUNS_DIR
            try:
                state.set_runs_root(Path(tmp))
                cli_common.FAKE_RUNS_DIR = Path(tmp)
                common = ["--model-set", "gemini_lite", "--variant", "memlog3", "--tag", "t", "--fake"]
                self.assertEqual(quiet(run_trunk.main, common + ["--trunk-rounds", "3",
                                                                 "--total-rounds", "6"]), 0)
                run = "gemini_lite__memlog3__t"
                sel = load_json(state.selection_path(run))
                self.assertTrue(sel["rule"].startswith(">= 2/3 CHEAP in rounds 2, 3"))
                self.assertEqual(len(sel["kept"]), 5)
                self.assertEqual(quiet(run_branch.main, common + ["--conditions", "stronger"]), 1)
                self.assertEqual(quiet(run_branch.main, common), 0)   # default: control and equal
                self.assertEqual(quiet(analyze.main, common), 0)
                report = (state.run_dir(run) / "report.md").read_text()
                self.assertIn("equal vs control", report)
                self.assertNotIn("stronger vs control", report)
                self.assertNotIn("rename vs control", report)
                self.assertIn("Descriptive p vs 50%", report)
                self.assertEqual(quiet(export_transcripts.main, common), 0)
                readable = (state.run_dir(run) / "transcripts" / "readable" / "equal" / "trial_0.md").read_text()
                self.assertIn("## Memory log shown to each player in round 4 (the swap round)", readable)
                self.assertIn(MEMORY_LOG_HEADER, readable)
                merged = load_json(state.condition_path(run, "equal"))
                self.assertEqual(merged["metadata"]["agent_models"]["branch"],
                                 {"J": SET.base, "Q": SET.equal, "T": SET.base})
            finally:
                state.set_runs_root(old_root)
                cli_common.FAKE_RUNS_DIR = old_fake


if __name__ == "__main__":
    unittest.main()
