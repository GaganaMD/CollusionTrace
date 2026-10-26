"""Tests for the experiment variants: public history, warning, probe v2, run folders."""
import contextlib
import io
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path

import experiment  # noqa: F401  (puts the harness on sys.path)
from experiment import analyze, cli_common, run_branch, run_trunk, state
from experiment.clients import Clients
from experiment.config import (MODEL_SETS, PROBE2_MOST_LIKELY, VARIANTS, WARNING_TEXT, RoundPlan,
                               run_config, variant_of)
from experiment.engine import public_history, run_branches
from experiment.fake_client import FakeClient
from experiment.probe import allowed_which, build_probe_prompt, forced_options, parse_probe
from experiment.roster import empty_memory
from experiment.state import BranchState

B = MODEL_SETS["option_b"]
PLAN = RoundPlan(5, 10)


def play(branches, fake, variant):
    with contextlib.redirect_stdout(io.StringIO()):
        run_branches(branches, PLAN, B, Clients(fake, fake), save=lambda b: None, variant=variant)


def new_trunk(variant, trial_id=0):
    return BranchState(key=f"trunk.t{trial_id}", trial_id=trial_id, condition=None, model_set="x",
                       config=run_config(B, PLAN, variant), memory=empty_memory())


def system_prompts(fake, prefix):
    return [r["messages"][0]["content"] for r in fake.requests if r["custom_id"].startswith(prefix)]


class TestConfig(unittest.TestCase):
    def test_variant_round_trip(self):
        self.assertEqual(variant_of(run_config(B, PLAN)), VARIANTS["baseline"])
        self.assertNotIn("variant", run_config(B, PLAN))            # baseline config unchanged
        cfg = run_config(B, PLAN, VARIANTS["history_warned"])
        self.assertEqual(variant_of(cfg), VARIANTS["history_warned"])
        self.assertEqual(cfg["warning_text"], WARNING_TEXT)

    def test_run_folder(self):
        self.assertEqual(experiment.config.run_name("option_b", "baseline"), "option_b")
        self.assertEqual(experiment.config.run_name("option_b", "history"), "option_b__history")


class TestHistoryAndWarning(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fake = FakeClient()
        cls.trunk = new_trunk(VARIANTS["history_warned"])
        play([cls.trunk], cls.fake, VARIANTS["history_warned"])
        cls.branch = cls.trunk.branch_from("newcomer")
        play([cls.branch], cls.fake, VARIANTS["history_warned"])

    def test_round_one_has_no_history(self):
        for p in system_prompts(self.fake, "r0.trunk.t0."):
            self.assertNotIn("PUBLIC RECORD", p)
            self.assertIn(WARNING_TEXT, p)

    def test_history_lists_every_earlier_round(self):
        prompt = system_prompts(self.fake, "r7.newcomer.t0.s1.J")[0]
        self.assertEqual(re.findall(r"^Round (\d+):", prompt, re.M), [str(i) for i in range(1, 8)])
        self.assertIn("Agent Q announced", prompt)    # the old seat's messages, under its old name
        self.assertIn("Agent R announced", prompt)    # and the newcomer's, under its new name
        self.assertIn(WARNING_TEXT, prompt)

    def test_every_stage_and_probe_gets_it(self):
        round_8 = [r for r in self.fake.requests if r["custom_id"].startswith("r7.newcomer.t0.")]
        for stage in ("s1", "s2", "s3", "refl", "probe"):
            prompts = [r["messages"][0]["content"] for r in round_8 if f".{stage}." in r["custom_id"]]
            self.assertTrue(prompts, stage)
            self.assertTrue(all("PUBLIC RECORD" in p for p in prompts), stage)

    def test_history_matches_saved_rounds(self):
        text = public_history(self.branch.rounds[:3])
        first = self.branch.rounds[0]
        self.assertIn(first["agents"]["J"]["stage2"]["message"], text)
        self.assertIn("Final choices: J CHEAP", text)


class TestBaselineUntouched(unittest.TestCase):
    def test_no_history_or_warning(self):
        fake = FakeClient()
        trunk = new_trunk(VARIANTS["baseline"])
        play([trunk], fake, VARIANTS["baseline"])
        for r in fake.requests:
            self.assertNotIn("PUBLIC RECORD", r["messages"][0]["content"])
            self.assertNotIn(WARNING_TEXT, r["messages"][0]["content"])
            self.assertNotIn(PROBE2_MOST_LIKELY, r["messages"][-1]["content"])


class TestProbeV2(unittest.TestCase):
    names = ["J", "M", "Q", "T", "Z"]

    def test_wording(self):
        trial = {"agents": {n: {"stage2": {"stated_action": "CHEAP", "message": "hi"}} for n in self.names},
                 "outcomes": {"choices": {n: "CHEAP" for n in self.names}}}
        allowed = allowed_which(self.names, None)
        _, user, schema = build_probe_prompt("J", self.names, {}, trial, 5, allowed,
                                             ask_same=False, supports_structured=False, version=2)
        questions = user.split("Final actions:")[1]
        self.assertNotRegex(questions, r"\bAI\b")
        self.assertIn("swapped out for a different player", questions)
        self.assertIn('"most_likely" must be one of: M, Q, T, Z', user)
        self.assertEqual(schema["schema"]["properties"]["most_likely"]["enum"], ["M", "Q", "T", "Z"])

    def test_parse(self):
        allowed, forced = allowed_which(self.names, None), forced_options(self.names, "J")
        reply = {"content": '{"swapped": "yes", "which": "Q", "confidence": 70, "most_likely": "Agent Q"}'}
        self.assertEqual(parse_probe(reply, allowed, False, 2, forced),
                         {"replaced": "yes", "which": "Q", "confidence": 70, "most_likely": "Q"})
        for bad in ('"none"', '"J"', '"X"'):   # 'none', yourself, or an unknown letter
            body = '{"swapped": "no", "which": "none", "confidence": 70, "most_likely": %s}' % bad
            reply = {"content": body}
            self.assertIsNone(parse_probe(reply, allowed, False, 2, forced), bad)


class TestReviewFixes(unittest.TestCase):
    names = ["J", "M", "Q", "T", "Z"]

    def test_refused_forced_choice_keeps_the_rest(self):
        allowed, forced = allowed_which(self.names, None), forced_options(self.names, "J")
        reply = {"content": '{"swapped": "no", "which": "none", "confidence": 90, "most_likely": "none"}'}
        self.assertIsNone(parse_probe(reply, allowed, False, 2, forced))           # re-asked first
        kept = parse_probe(reply, allowed, False, 2, forced, allow_refusal=True)   # then kept
        self.assertEqual(kept, {"replaced": "no", "which": "none", "confidence": 90,
                                "most_likely": None, "forced_refused": True})

    def test_refusal_through_the_engine(self):
        fake = FakeClient(probe={"replaced": "no", "swapped": "no", "which": "none", "confidence": 90,
                                 "most_likely": "none"})
        trunk = new_trunk(VARIANTS["probe2"])
        play([trunk], fake, VARIANTS["probe2"])
        self.assertEqual(trunk.status, "complete")
        self.assertTrue(all(p["forced_refused"] and p["most_likely"] is None and p["parse_ok"]
                            for p in trunk.probes))
        self.assertEqual(len([r for r in trunk.reasks if ".probe." in r["request"]]), 4 * 3)

    def test_told_text_in_warned_variants(self):
        self.assertIn("have not been told", experiment.config.told_text())
        self.assertNotIn("have not been told", experiment.config.told_text(warned=True))
        self.assertNotIn("have not been told",
                         run_config(B, PLAN, VARIANTS["history_warned"])["told_text"])

    def test_sign_test(self):
        self.assertAlmostEqual(analyze.sign_test(5, 0), 0.0625)
        self.assertEqual(analyze.sign_test(2, 2), 1.0)
        self.assertIsNone(analyze.sign_test(0, 0))

    def test_ceiling_newcomer_model(self):
        from experiment import ceiling_test
        self.assertEqual(ceiling_test.newcomer_model("equal", B), B.equal)
        self.assertEqual(ceiling_test.newcomer_model("stronger_told", B), B.stronger)
        self.assertIsNone(ceiling_test.newcomer_model("rename", B))


class TestForcedChoiceMetric(unittest.TestCase):
    def test_metric(self):
        names = lambda seat: ["J", "M", seat, "T", "Z"]   # noqa: E731
        rounds = []
        for r in range(10):
            agents = {n: {"stage2": {"stated_action": "CHEAP"}, "stage3": {"choice": "CHEAP"},
                          "commitment_breaking": False, "promise_deception": False,
                          "reflection": {"takeaways": {t: {"score": 4, "assessment": "x"}
                                                       for t in names("Q") if t != n}}}
                      for n in names("Q")}
            rounds.append({"seat": "Q", "round_id": r, "agents": agents})
        probes = [{"round_id": 5, "agent": a, "parse_ok": True, "replaced": "no", "which": "none",
                   "confidence": 50, "most_likely": pick} for a, pick in zip("JMTZ", "QQTQ")]
        probes.append({"round_id": 4, "agent": "J", "parse_ok": True, "replaced": "no", "which": "none",
                       "confidence": 50, "most_likely": "M"})
        b = BranchState(key="equal.t0", trial_id=0, condition="equal", model_set="x", config={},
                        memory={}, rounds=rounds, probes=probes, status="complete")
        m = analyze.branch_metrics(b, PLAN, {})
        self.assertEqual(m["forced_choice"], 0.75)
        self.assertEqual(m["forced_choice_before_swap"], 0.0)
        self.assertEqual((m["forced_hits"], m["forced_n"]), (3.0, 4.0))
        self.assertAlmostEqual(analyze.binomial_tail(3, 4, 0.25), 13 / 256)


class TestVariantPipeline(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.old = (state._runs_root, cli_common.FAKE_RUNS_DIR)
        state.set_runs_root(Path(self.tmp))
        cli_common.FAKE_RUNS_DIR = Path(self.tmp)

    def tearDown(self):
        state.set_runs_root(self.old[0])
        cli_common.FAKE_RUNS_DIR = self.old[1]
        shutil.rmtree(self.tmp)

    def test_history_run_goes_to_its_own_folder(self):
        args = ["--model-set", "option_b", "--fake", "--variant", "history"]
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(run_trunk.main(args), 0)
            self.assertEqual(run_branch.main(args + ["--conditions", "control", "equal"]), 0)
            self.assertEqual(analyze.main(args), 0)
        root = Path(self.tmp) / "option_b__history"
        cfg = json.loads((root / "trunk" / "run_config.json").read_text())
        self.assertEqual(cfg["variant"]["name"], "history")
        self.assertFalse((Path(self.tmp) / "option_b").exists())
        self.assertIn("Forced choice", (root / "report.md").read_text())
        merged = json.loads((root / "conditions" / "equal.json").read_text())
        self.assertEqual(merged["metadata"]["variant"], "history")


if __name__ == "__main__":
    unittest.main()
