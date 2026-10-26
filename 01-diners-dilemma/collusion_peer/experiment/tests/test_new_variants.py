"""Tests for the round-1 warning, the cold swap, the detection bonus and the shuffled forced choice."""
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

import experiment  # noqa: F401  (puts the harness on sys.path)
from experiment import analyze, cli_common, export_transcripts, run_branch, run_trunk, state
from experiment.clients import Clients
from experiment.config import (CONDITIONS, MODEL_SETS, PINNED_WARNING, RUNS_DIR, VARIANTS, WARNING_TEXT,
                               RoundPlan, bonus_text, run_config, variant_of)
from experiment.engine import MEMORY_LOG_HEADER, memory_log, run_branches
from experiment.fake_client import FakeClient
from experiment.roster import empty_memory
from experiment.state import BranchState, check_config, load_json

SET = MODEL_SETS["llama_maverick"]   # base without structured output; GPT-4o-mini newcomer with it
PLAN = RoundPlan(4, 8)               # swap at index 4 (round 5); probes at rounds 4, 5, 7, 8
WARN, BONUS, MEMLOG = VARIANTS["memlog3_warn1"], VARIANTS["memlog3_warn1_bonus"], VARIANTS["memlog3"]
RULE = bonus_text(10.0, accuse_from=2)


def quiet(fn, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


def play(variant, condition, fake):
    trunk = BranchState(key="trunk.t0", trial_id=0, condition=None, model_set="x",
                        config=run_config(SET, PLAN, variant), memory=empty_memory(variant.agent_names))
    quiet(run_branches, [trunk], PLAN, SET, Clients(fake, fake), save=lambda b: None, variant=variant)
    branch = trunk.branch_from(condition)
    quiet(run_branches, [branch], PLAN, SET, Clients(fake, fake), save=lambda b: None, variant=variant)
    return branch


def requests(fake, prefix):
    return [r for r in fake.requests if r["custom_id"].startswith(prefix)]


def system(r):
    return r["messages"][0]["content"]


def user(r):
    return r["messages"][-1]["content"]


class TestConfig(unittest.TestCase):
    def test_round_trip(self):
        for v in (WARN, BONUS):
            self.assertEqual(variant_of(json.loads(json.dumps(run_config(SET, PLAN, v)))), v)
        self.assertEqual(run_config(SET, PLAN, BONUS)["bonus_text"], RULE)
        self.assertNotIn("bonus_text", run_config(SET, PLAN, WARN))

    def test_saved_configs_still_match(self):
        """The cold swap reuses the stage-1 trunks, so their config must not change."""
        runs = [("option_b", "option_b"), ("option_b__history", "option_b"),
                ("llama_maverick__memlog3__r20", "llama_maverick")]
        for run, model_set in runs:
            path = RUNS_DIR / run / "trunk" / "run_config.json"
            if not path.exists():
                continue
            saved = load_json(path)
            check_config(saved, run_config(MODEL_SETS[model_set], RoundPlan(**saved["rounds"]),
                                           variant_of(saved)), run)

    def test_cold_condition(self):
        self.assertTrue(CONDITIONS["cold"].cold and CONDITIONS["cold"].swapped)
        self.assertFalse(CONDITIONS["control"].swapped)


class TestWarningFirstRound(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fake = FakeClient()
        cls.branch = play(BONUS, "equal", cls.fake)

    def test_warning_and_rule_only_in_round_one_stages(self):
        for r in self.fake.requests:
            if ".refl." in r["custom_id"]:
                continue
            first = r["custom_id"].startswith("r0.")
            # after round 1 the warning survives only as the pinned line at the top of the log
            expected = 1 if first else 0
            self.assertEqual(system(r).count(WARNING_TEXT) - system(r).count(PINNED_WARNING), expected,
                             r["custom_id"])
            self.assertEqual(RULE in system(r), first, r["custom_id"])

    def test_warning_pinned_in_log(self):
        for r in self.fake.requests:
            if r["custom_id"].startswith("r0."):
                self.assertNotIn(PINNED_WARNING, system(r))
            else:
                self.assertTrue(system(r).startswith(f"{MEMORY_LOG_HEADER}\n{PINNED_WARNING}\nRound 1:"),
                                r["custom_id"])

    def test_question_from_round_two(self):
        self.assertIn("from round 2 on, after each round you may accuse", RULE)
        for r in (x for x in self.fake.requests if ".refl." in x["custom_id"]):
            asked = not r["custom_id"].startswith("r0.")
            self.assertEqual("Accusation: do you accuse" in user(r), asked, r["custom_id"])
            self.assertEqual(RULE in user(r), asked, r["custom_id"])
        self.assertEqual(self.branch.rounds[0]["agents"]["J"]["reflection"]["accusations"], {})
        self.assertEqual(set(self.branch.rounds[1]["agents"]["J"]["reflection"]["accusations"]), {"Q", "T"})


class TestAccusation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fake = FakeClient(accuse={"J>Q": 5})       # J accuses Q after round 6 (index 5)
        cls.branch = play(BONUS, "equal", cls.fake)
        cls.control_fake = FakeClient(accuse={"J>Q": 5})
        cls.control = play(BONUS, "control", cls.control_fake)

    def test_question_and_schema(self):
        base = requests(self.fake, "r5.equal.t0.refl.J>Q")[0]          # Llama: JSON in the prompt
        self.assertIn("Accusation: do you accuse Agent Q", user(base))
        self.assertIn('"accuse": "yes" or "no"}', user(base))
        self.assertLess(user(base).index("Accusation:"), user(base).index("IMPORTANT: Respond"))
        newcomer = requests(self.fake, "r5.equal.t0.refl.Q>J")[0]       # GPT-4o-mini: strict schema
        schema = newcomer["response_format"]["json_schema"]["schema"]
        self.assertIn("accuse", schema["required"])

    def test_accusation_is_final(self):
        accusations = [t["agents"]["J"]["reflection"]["accusations"] for t in self.branch.rounds]
        self.assertEqual(accusations[5], {"Q": "yes", "T": "no"})
        self.assertEqual(accusations[6], {"T": "no"})                   # not asked about Q again
        later = user(requests(self.fake, "r6.equal.t0.refl.J>Q")[0])
        self.assertIn("You accused Agent Q of having been swapped in round 6", later)
        self.assertNotIn("Accusation: do you accuse", later)
        self.assertIn("; you accused them of having been swapped", memory_log(self.branch.rounds, "J"))
        self.assertNotIn("accused", memory_log(self.branch.rounds, "T"))
        self.assertTrue(all("accuse" not in note for t in self.branch.rounds
                            for a in t["agents"].values() for note in a["reflection"]["takeaways"].values()))

    def test_metrics(self):
        m = analyze.accusation_metrics(self.branch, PLAN)
        self.assertEqual(m, {"accused_seat": 0.5, "false_accusations": 0.0, "first_accusation_round": 6.0,
                             "seat_accusations": 0.0})
        c = analyze.accusation_metrics(self.control, PLAN)       # Q was never swapped: a false accusation
        self.assertEqual(c["accused_seat"], 0.0)
        self.assertEqual(c["false_accusations"], 1.0)

    def test_seat_accusations_kept_apart(self):
        fake = FakeClient(accuse={"Q>J": 5, "J>Q": 5})   # the seat accuses J; J accuses the seat
        m = analyze.accusation_metrics(play(BONUS, "equal", fake), PLAN)
        self.assertEqual((m["accused_seat"], m["false_accusations"], m["seat_accusations"]), (0.5, 0.0, 1.0))

    def test_no_accusation_metrics_without_bonus(self):
        branch = play(WARN, "equal", FakeClient())
        self.assertEqual(analyze.accusation_metrics(branch, PLAN), {})


class TestShuffledForcedChoice(unittest.TestCase):
    def test_order_varies_and_is_reproducible(self):
        fake = FakeClient()
        play(WARN, "equal", fake)
        orders = set()
        for r in (x for x in fake.requests if ".probe." in x["custom_id"]):
            enum = None
            text = user(r)
            marker = '"most_likely" must be one of: '
            if marker in text:   # Llama players: options listed in the prompt
                enum = text.split(marker)[1].split(".")[0]
            orders.add((r["custom_id"].split(".")[-1], enum))
        self.assertIn(("J", "Q, T"), orders)
        self.assertIn(("J", "T, Q"), orders)
        again = FakeClient()
        play(WARN, "equal", again)
        self.assertEqual([user(r) for r in fake.requests if ".probe." in r["custom_id"]],
                         [user(r) for r in again.requests if ".probe." in r["custom_id"]])

    def test_stage_one_order_unchanged(self):
        fake = FakeClient()
        play(MEMLOG, "equal", fake)
        for r in (x for x in fake.requests if ".probe.J" in x["custom_id"]):
            self.assertIn('"most_likely" must be one of: Q, T.', user(r))


class TestColdSwap(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fake = FakeClient()
        cls.branch = play(MEMLOG, "cold", cls.fake)

    def test_newcomer_starts_without_memory(self):
        first = system(requests(self.fake, f"r{PLAN.swap}.cold.t0.s1.Q")[0])
        self.assertNotIn(MEMORY_LOG_HEADER, first)
        self.assertNotIn("Based on your previous interactions", first)
        refl = user(requests(self.fake, f"r{PLAN.swap}.cold.t0.refl.Q>J")[0])
        self.assertIn("Agent J ← FOCUS: (no prior assessment)", refl)

    def test_cold_newcomer_gets_no_pinned_warning(self):
        fake = FakeClient()
        play(WARN, "cold", fake)
        later = system(requests(fake, f"r{PLAN.swap + 2}.cold.t0.s1.Q")[0])
        self.assertTrue(later.startswith(MEMORY_LOG_HEADER + f"\nRound {PLAN.swap + 1}:"))
        self.assertNotIn(WARNING_TEXT, later)
        j = system(requests(fake, f"r{PLAN.swap + 2}.cold.t0.s1.J")[0])
        self.assertTrue(j.startswith(f"{MEMORY_LOG_HEADER}\n{PINNED_WARNING}\nRound 1:"))

    def test_newcomer_log_starts_at_swap(self):
        later = system(requests(self.fake, f"r{PLAN.swap + 2}.cold.t0.s1.Q")[0])
        self.assertTrue(later.startswith(MEMORY_LOG_HEADER + f"\nRound {PLAN.swap + 1}:"))
        self.assertNotIn("Round 1:", later)

    def test_cold_newcomer_ignores_old_accusations(self):
        """Under a bonus variant, the old Q's accusations must not reach a cold newcomer."""
        fake = FakeClient(accuse={"Q>J": 1})          # the old Q accuses J in round 2
        branch = play(BONUS, "cold", fake)
        swap_refl = user(requests(fake, f"r{PLAN.swap}.cold.t0.refl.Q>J")[0])
        self.assertIn("Accusation: do you accuse Agent J", swap_refl)
        self.assertNotIn("You accused Agent J", swap_refl)
        self.assertEqual(branch.rounds[1]["agents"]["Q"]["reflection"]["accusations"]["J"], "yes")

    def test_others_keep_full_log(self):
        j = system(requests(self.fake, f"r{PLAN.swap}.cold.t0.s1.J")[0])
        self.assertTrue(j.startswith(MEMORY_LOG_HEADER + "\nRound 1:"))
        self.assertEqual(self.branch.rounds[PLAN.swap]["seat_models"]["Q"], SET.equal)


class TestCommandLine(unittest.TestCase):
    def test_fake_pipelines(self):
        with tempfile.TemporaryDirectory() as tmp:
            old_root, old_fake = state._runs_root, cli_common.FAKE_RUNS_DIR
            try:
                state.set_runs_root(Path(tmp))
                cli_common.FAKE_RUNS_DIR = Path(tmp)
                rounds = ["--trunk-rounds", "3", "--total-rounds", "6"]
                bonus = ["--model-set", "llama_maverick", "--variant", "memlog3_warn1_bonus", "--tag", "t",
                         "--fake"]
                self.assertEqual(quiet(run_trunk.main, bonus + rounds), 0)
                self.assertEqual(quiet(run_branch.main, bonus), 0)
                self.assertEqual(quiet(analyze.main, bonus), 0)
                self.assertEqual(quiet(export_transcripts.main, bonus), 0)
                report = (state.run_dir("llama_maverick__memlog3_warn1_bonus__t") / "report.md").read_text()
                self.assertIn("accused_seat", report)
                cold = ["--model-set", "llama_maverick", "--variant", "memlog3", "--tag", "t", "--fake"]
                self.assertEqual(quiet(run_trunk.main, cold + rounds), 0)
                self.assertEqual(quiet(run_branch.main, cold), 0)                      # control, equal
                self.assertEqual(quiet(run_branch.main, cold + ["--conditions", "cold"]), 0)
                self.assertEqual(quiet(analyze.main, cold), 0)
                report = (state.run_dir("llama_maverick__memlog3__t") / "report.md").read_text()
                self.assertIn("cold vs control", report)
                self.assertNotIn("accused_seat", report)
            finally:
                state.set_runs_root(old_root)
                cli_common.FAKE_RUNS_DIR = old_fake


if __name__ == "__main__":
    unittest.main()
