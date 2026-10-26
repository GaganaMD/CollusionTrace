"""Offline end-to-end tests: engine, failure handling, CLIs, selection and analysis."""
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

import experiment  # noqa: F401  (puts the harness on sys.path)
from experiment import analyze, run_branch, run_trunk, state
from experiment.clients import Clients, SpendCapReached
from experiment.config import (CONDITIONS, MAX_REASKS, MODEL_SETS, PROBE_INTRO, RoundPlan, run_config)
from experiment.engine import run_branches
from experiment.fake_client import FakeClient
from experiment.roster import empty_memory
from experiment.state import BranchState

PLAN = RoundPlan(5, 10)
B = MODEL_SETS["option_b"]
CONFIG = run_config(B, PLAN)


def quiet(fn, *args, **kwargs):
    """Run fn with stdout silenced (the harness prints a line per batch)."""
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


def new_trunk(trial_id: int) -> BranchState:
    return BranchState(key=f"trunk.t{trial_id}", trial_id=trial_id, condition=None, model_set=B.name,
                       config=CONFIG, memory=empty_memory())


def play(branches, fake):
    quiet(run_branches, branches, PLAN, B, Clients(fake, fake), save=lambda b: None)


class TestEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fake = FakeClient(policy={B.stronger: {"choice": "EXPENSIVE"}})
        cls.trunk = new_trunk(0)
        play([cls.trunk], cls.fake)
        cls.branches = {c: cls.trunk.branch_from(c) for c in CONDITIONS}
        play(list(cls.branches.values()), cls.fake)

    def test_all_complete(self):
        self.assertEqual(self.trunk.status, "complete")
        self.assertEqual(len(self.trunk.rounds), PLAN.swap)
        for b in self.branches.values():
            self.assertEqual((b.status, len(b.rounds)), ("complete", PLAN.total_rounds), b.key)
            self.assertEqual([t["round_id"] for t in b.rounds], list(range(PLAN.total_rounds)))

    def test_request_ids_unique_in_every_batch(self):
        for batch in self.fake.batches:
            self.assertEqual(len(batch), len(set(batch)))

    def test_branches_share_the_trunk(self):
        for b in self.branches.values():
            self.assertEqual(b.rounds[:PLAN.swap], self.trunk.rounds)

    def test_seat_model_and_behavior(self):
        b = self.branches["stronger"]
        last = b.rounds[-1]
        self.assertEqual(last["seat_models"]["Q"], B.stronger)
        self.assertEqual(last["outcomes"]["choices"]["Q"], "EXPENSIVE")
        self.assertEqual(last["outcomes"]["choices"]["J"], "CHEAP")

    def test_told_sentence_only_seat_after_swap(self):
        told = [r for r in self.fake.requests if "taking over seat" in r["messages"][0]["content"]]
        per_branch_round = 3 + 4  # plan, announce, choice + 4 reflections
        self.assertEqual(len(told), 2 * (PLAN.total_rounds - PLAN.swap) * per_branch_round)
        for r in told:
            parts = r["custom_id"].split(".")
            rnd, branch, who = parts[0], parts[1], parts[-1]
            self.assertIn(branch, ("stronger_told", "equal_told"))
            self.assertGreaterEqual(int(rnd[1:]), PLAN.swap)
            self.assertTrue(who.split(">")[0] == "Q")

    def test_rename(self):
        b = self.branches["newcomer"]
        self.assertEqual(b.rounds[-1]["announcement_order"], ["J", "M", "R", "T", "Z"])
        self.assertEqual(b.rounds[-1]["seat"], "R")
        self.assertIn("Q (no longer in the game)", b.memory["J"])
        self.assertIn("R", b.memory["J"])
        self.assertEqual(b.rounds[PLAN.swap - 1]["seat"], "Q")
        prefix = f"r{PLAN.swap}.newcomer.t0.s1.J"
        plan_prompt = next(r for r in self.fake.requests if r["custom_id"].startswith(prefix))
        self.assertIn("Agent Q (no longer in the game) (trust 4/5)", plan_prompt["messages"][0]["content"])

    def test_probes(self):
        b = self.branches["rename"]
        rounds = sorted({p["round_id"] for p in b.probes})
        self.assertEqual(rounds, PLAN.probe_rounds)
        for p in b.probes:
            self.assertNotEqual(p["agent"], "R" if p["round_id"] >= PLAN.swap else "Q")   # seat never asked
            self.assertEqual("same_as_q" in p, p["round_id"] >= PLAN.swap)
        self.assertNotIn("same_as_q", self.branches["equal"].probes[-1])

    def test_probe_never_in_memory(self):
        for b in self.branches.values():
            self.assertNotIn(PROBE_INTRO, json.dumps(b.memory))
            self.assertNotIn("replaced", json.dumps(b.memory))

    def test_no_harness_judge(self):
        for agent in self.branches["control"].rounds[-1]["agents"].values():
            self.assertNotIn("judge", agent)


class TestFailures(unittest.TestCase):
    def test_reask_recovers(self):
        fake = FakeClient(fail={".s3.Q": 2})
        trunk = new_trunk(1)
        play([trunk], fake)
        self.assertEqual(trunk.status, "complete")
        self.assertEqual(len(trunk.reasks), 2)

    def test_persistent_failure_stops_only_that_branch(self):
        fake = FakeClient()
        trunk = new_trunk(2)
        play([trunk], fake)
        bad, good = trunk.branch_from("equal"), trunk.branch_from("control")
        fake.fail = {"r6.equal.t2.s2.Q": MAX_REASKS + 1}
        play([bad, good], fake)
        self.assertEqual(bad.status, "failed")
        self.assertEqual(bad.failure["stage"], "announce")
        self.assertEqual(bad.failure["round_id"], 6)
        self.assertEqual(len(bad.rounds), 6)          # rounds before the failure are kept
        self.assertEqual(good.status, "complete")

    def test_invalid_action_is_unparsed(self):
        fake = FakeClient(policy={B.base: {"choice": "MAYBE"}})
        trunk = new_trunk(3)
        play([trunk], fake)
        self.assertEqual(trunk.status, "failed")
        self.assertEqual(trunk.failure["stage"], "choice")

    def test_openai_cap(self):
        fake = FakeClient()
        with self.assertRaises(SpendCapReached):
            quiet(run_branches, [new_trunk(4)], PLAN, B, Clients(fake, fake, max_openai_calls=10),
                  save=lambda b: None)
        self.assertEqual(fake.batches, [])   # stopped before sending anything


class TestCommandLine(unittest.TestCase):
    """Full trunk -> selection -> branches -> merge -> analysis, offline, in a temp folder."""

    def test_end_to_end(self):
        from experiment import cli_common
        with tempfile.TemporaryDirectory() as tmp:
            old_root, old_fake = state._runs_root, cli_common.FAKE_RUNS_DIR
            try:
                fake_root = Path(tmp)
                state.set_runs_root(fake_root)
                cli_common.FAKE_RUNS_DIR = fake_root
                self.assertEqual(quiet(run_trunk.main, ["--model-set", "option_b", "--fake"]), 0)
                sel = json.loads(state.selection_path("option_b").read_text())
                self.assertEqual(sel["kept"], [0, 1, 2, 3, 4])
                self.assertEqual(quiet(run_branch.main, ["--model-set", "option_b", "--fake"]), 0)
                merged = json.loads(state.condition_path("option_b", "newcomer").read_text())
                self.assertEqual(merged["metadata"]["swap"]["new_name"], "R")
                self.assertEqual(merged["metadata"]["harness_judge"], "not run")
                self.assertEqual(len(merged["rounds"]), PLAN.total_rounds)
                self.assertEqual(len(merged["rounds"][0]["trials"]), 5)
                self.assertEqual(quiet(analyze.main, ["--model-set", "option_b", "--fake"]), 0)
                self.assertTrue((state.run_dir("option_b") / "report.md").exists())
                # rerunning skips everything that is complete
                self.assertEqual(quiet(run_branch.main, ["--model-set", "option_b", "--fake"]), 0)
            finally:
                state.set_runs_root(old_root)
                cli_common.FAKE_RUNS_DIR = old_fake

    def test_selection_rule(self):
        st = new_trunk(5)
        st.status = "complete"
        st.rounds = [{"outcomes": {"choices": dict(zip("JMQTZ", choices))}} for choices in
                     [["CHEAP"] * 5] * 3 + [["CHEAP"] * 4 + ["EXPENSIVE"], ["CHEAP"] * 3 + ["EXPENSIVE"] * 2]]
        res = run_trunk.selection_result(st, PLAN)
        self.assertEqual(res["cheap"], {"R4": 4, "R5": 3})
        self.assertFalse(res["passes"])


class TestAnalysis(unittest.TestCase):
    def trial(self, seat, to_seat, among, seat_action="CHEAP", round_id=0):
        names = ["J", "M", seat, "T", "Z"]
        agents = {}
        for n in names:
            notes = {t: {"score": (to_seat if t == seat else among), "assessment": "x"}
                     for t in names if t != n}
            agents[n] = {"stage2": {"stated_action": "CHEAP"},
                         "stage3": {"choice": seat_action if n == seat else "CHEAP"},
                         "commitment_breaking": n == seat and seat_action != "CHEAP",
                         "promise_deception": False, "reflection": {"takeaways": notes}}
        return {"seat": seat, "round_id": round_id, "agents": agents}

    def test_trust_gap(self):
        self.assertEqual(analyze.trust_gap(self.trial("Q", 2, 4)), -2.0)

    def test_branch_metrics_and_contrast(self):
        b = new_trunk(0)
        b.condition = "stronger"
        b.rounds = [self.trial("Q", 4, 4, round_id=r) for r in range(5)] + \
                   [self.trial("Q", 3, 4, round_id=5), self.trial("Q", 2, 4, "EXPENSIVE", round_id=6)] + \
                   [self.trial("Q", 2, 4, round_id=r) for r in range(7, 10)]
        m = analyze.branch_metrics(b, PLAN, judge={})
        self.assertAlmostEqual(m["trust_gap"], (-1 - 2 - 2 - 2 - 2) / 5)
        self.assertAlmostEqual(m["trust_gap_pre_deviation"], -1.0)   # only R6, before the R7 defection
        self.assertEqual(m["matched_rounds"], 4.0)
        self.assertAlmostEqual(m["seat_cheap"], 0.8)
        per_trial = {0: {"stronger": {"x": 1.0}, "control": {"x": 0.25}},
                     1: {"stronger": {"x": None}, "control": {"x": 0.0}}}
        self.assertEqual(analyze.contrast_values(per_trial, {"stronger": 1, "control": -1}, "x"), {0: 0.75})
        s = analyze.summarize([1.0, -1.0, 2.0])
        self.assertEqual((s["n"], s["positive"], s["negative"]), (3, 2, 1))


if __name__ == "__main__":
    unittest.main()
