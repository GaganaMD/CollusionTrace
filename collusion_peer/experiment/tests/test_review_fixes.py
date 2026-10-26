"""Tests for the fixes from Gogo's code review: run-level config, kept trials, R notes,
probe baseline, failure history, hand-check safety and small parsing details."""
import contextlib
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import experiment  # noqa: F401  (puts the harness on sys.path)
from experiment import analyze, cli_common, judge_notes, run_branch, run_trunk, state
from experiment.config import MODEL_SETS, RoundPlan
from experiment.probe import allowed_which, parse_probe

B = MODEL_SETS["option_b"]


def run(main, *args):
    """Call a CLI main() with output silenced; return its exit code."""
    with contextlib.redirect_stdout(io.StringIO()):
        return main(["--model-set", "option_b", "--fake", *args])


class FakeRunsTestCase(unittest.TestCase):
    """Each test gets an empty runs folder."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.old = (state._runs_root, cli_common.FAKE_RUNS_DIR)
        state.set_runs_root(Path(self.tmp))
        cli_common.FAKE_RUNS_DIR = Path(self.tmp)

    def tearDown(self):
        state.set_runs_root(self.old[0])
        cli_common.FAKE_RUNS_DIR = self.old[1]
        shutil.rmtree(self.tmp)


class TestRunLevelConfig(FakeRunsTestCase):
    def test_settings_fixed_by_first_run(self):
        self.assertEqual(run(run_trunk.main, "--trunk-rounds", "4", "--total-rounds", "8"), 0)
        saved = json.loads(state.run_config_path("option_b").read_text())
        self.assertEqual(saved["rounds"], {"trunk_rounds": 4, "total_rounds": 8})
        # --extend without flags reuses the saved settings ...
        self.assertEqual(run(run_trunk.main, "--extend"), 0)
        extended = state.load_state(state.trunk_path("option_b", 9))
        self.assertEqual(len(extended.rounds), 4)
        sel = json.loads(state.selection_path("option_b").read_text())
        self.assertEqual(set(sel["trials"]["9"]["cheap"]), {"R3", "R4"})   # selection uses the saved plan
        # ... and conflicting flags are refused.
        self.assertEqual(run(run_trunk.main, "--total-rounds", "10"), 1)

    def test_branch_refuses_trial_not_kept(self):
        run(run_trunk.main)
        self.assertEqual(run(run_branch.main, "--trials", "7"), 1)   # kept are 0-4


class TestKeptTrialsOnly(FakeRunsTestCase):
    def test_partial_run_does_not_shrink_merged_file(self):
        run(run_trunk.main)
        run(run_branch.main, "--conditions", "control")
        run(run_branch.main, "--trials", "0", "--conditions", "control")
        merged = json.loads(state.condition_path("option_b", "control").read_text())
        self.assertEqual(merged["metadata"]["trial_ids"], [0, 1, 2, 3, 4])

    def test_analysis_ignores_stray_files(self):
        run(run_trunk.main)
        run(run_branch.main, "--conditions", "control")
        src = state.branch_path("option_b", "control", 0)
        stray = state.branch_path("option_b", "control", 6)
        data = json.loads(src.read_text())
        data.update(trial_id=6, key="control.t6")
        stray.write_text(json.dumps(data))
        per_trial, _, _, ignored = analyze.collect("option_b")
        self.assertEqual(sorted(per_trial), [0, 1, 2, 3, 4])
        self.assertEqual(ignored, [str(stray)])
        self.assertEqual(len({n["trial_id"] for n in judge_notes.collect_notes("option_b")}), 5)


class TestFailureHistory(FakeRunsTestCase):
    def test_rerun_failed_keeps_history(self):
        run(run_trunk.main)
        path = state.branch_path("option_b", "equal", 0)
        trunk = state.load_state(state.trunk_path("option_b", 0))
        failed = trunk.branch_from("equal")
        failed.status, failed.failure = "failed", {"round_id": 5, "stage": "choice"}
        state.save_state(path, failed)
        run(run_branch.main, "--trials", "0", "--conditions", "equal")
        self.assertEqual(state.load_state(path).status, "failed")          # kept without the flag
        run(run_branch.main, "--trials", "0", "--conditions", "equal", "--rerun-failed")
        rerun = state.load_state(path)
        self.assertEqual(rerun.status, "complete")
        self.assertEqual(rerun.history[0]["failure"]["stage"], "choice")


class TestHandCheck(FakeRunsTestCase):
    def test_no_overwrite_and_no_duplicates(self):
        run(run_trunk.main)
        run(run_branch.main)
        run(judge_notes.main)
        run(judge_notes.main, "--hand-check")
        sheet = state.run_dir("option_b") / "hand_check.csv"
        key = json.loads((state.run_dir("option_b") / "hand_check_key.json").read_text())
        hashes = [k["note_sha256"] for k in key]
        self.assertEqual(len(hashes), len(set(hashes)))
        sheet.write_text(sheet.read_text().replace(",,,", ",yes,no,no", 1))
        before = sheet.read_text()
        run(judge_notes.main, "--hand-check")
        self.assertEqual(sheet.read_text(), before)                         # human labels kept

    def test_kappa(self):
        self.assertAlmostEqual(judge_notes.cohen_kappa([(True, True), (False, False)]), 1.0)
        self.assertIsNone(judge_notes.cohen_kappa([(True, True), (True, True)]))


class TestAnalysisSplits(unittest.TestCase):
    PLAN = RoundPlan(5, 10)

    def branch(self, condition, seat_after):
        names = lambda seat: ["J", "M", seat, "T", "Z"]   # noqa: E731
        rounds = []
        for r in range(10):
            seat = "Q" if r < 5 else seat_after
            agents = {n: {"stage2": {"stated_action": "CHEAP"}, "stage3": {"choice": "CHEAP"},
                          "commitment_breaking": False, "promise_deception": False,
                          "reflection": {"takeaways": {t: {"score": 4, "assessment": "x"}
                                                       for t in names(seat) if t != n}}}
                      for n in names(seat)}
            rounds.append({"seat": seat, "round_id": r, "agents": agents})
        probes = [{"round_id": 4, "agent": "J", "parse_ok": True, "replaced": "yes", "which": "Q",
                   "confidence": 90},
                  {"round_id": 4, "agent": "M", "parse_ok": True, "replaced": "no", "which": "none",
                   "confidence": 50}]
        return state.BranchState(key=f"{condition}.t0", trial_id=0, condition=condition, model_set="option_b",
                                 config={}, memory={}, rounds=rounds, probes=probes, status="complete")

    def test_r_notes_and_probe_baseline(self):
        judge = {(0, "rename", 7, "J"): {"labels": {"identity": True, "style": False, "behavior": False}},
                 (0, "rename", 4, "J"): {"labels": {"identity": False, "style": False, "behavior": False}}}
        m = analyze.branch_metrics(self.branch("rename", "R"), self.PLAN, judge)
        self.assertIsNone(m["change_detected"])          # notes about R are not detection
        self.assertEqual(m["change_about_R"], 1.0)
        self.assertEqual(m["change_detected_before_swap"], 0.0)
        self.assertEqual(m["detection_before_swap"], 0.5)  # round-5 false alarms
        self.assertEqual(m["detection@R5"], 0.5)
        self.assertEqual(m["change@R8"], 1.0)

        m2 = analyze.branch_metrics(self.branch("equal", "Q"), self.PLAN,
                                    {(0, "equal", 6, "J"): {"labels": {"identity": False, "style": True,
                                                                       "behavior": True}}})
        self.assertEqual(m2["change_detected"], 1.0)
        self.assertIsNone(m2["change_about_R"])


class TestParsingDetails(unittest.TestCase):
    def test_confidence_with_percent(self):
        allowed = allowed_which(["J", "M", "Q", "T", "Z"], None)
        reply = {"content": '{"replaced": "no", "which": "none", "confidence": "80%"}'}
        p = parse_probe(reply, allowed, ask_same=False)
        self.assertEqual(p["confidence"], 80)


if __name__ == "__main__":
    unittest.main()
