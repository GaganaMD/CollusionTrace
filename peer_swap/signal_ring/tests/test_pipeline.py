"""Command-line pipeline end to end, offline: trunk -> selection -> branches -> judge ->
ceiling -> analysis -> transcripts, in a temporary runs folder."""
import io
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

from signal_ring import analyze, ceiling, judge, run_branch, run_trunk, transcripts
from signal_ring import state as S
from signal_ring.config import RoundPlan
from signal_ring.run_trunk import selection_result
from signal_ring.state import GameState


def quiet(fn, *args):
    with redirect_stdout(io.StringIO()):
        return fn(*args)


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.patch = mock.patch("signal_ring.cli.FAKE_RUNS_DIR", self.tmp)
        self.patch.start()

    def tearDown(self):
        self.patch.stop()
        S.set_runs_root(S.RUNS_DIR)
        shutil.rmtree(self.tmp)

    def test_full_offline_pipeline(self):
        common = ["--fake", "--tag", "t"]
        self.assertEqual(quiet(run_trunk.main, common + ["--trials", "3", "--keep", "2"]), 0)
        run = "haiku__naive__t"
        self.assertEqual(S.kept_trials(run), [0, 1])
        self.assertEqual(quiet(run_branch.main, common), 0)
        for c in ("sham", "warm", "infiltrator", "cold"):
            for t in (0, 1):
                self.assertEqual(S.load_state(S.branch_path(run, c, t)).status, "complete")
        # Rerunning skips finished work.
        self.assertEqual(quiet(run_branch.main, common), 0)
        self.assertEqual(quiet(judge.main, common), 0)
        self.assertEqual(quiet(ceiling.main, common), 0)
        self.assertEqual(quiet(transcripts.main, common), 0)
        self.assertEqual(quiet(analyze.main, common), 0)
        report = (self.tmp / run / "report.md").read_text()
        self.assertIn("Paired contrasts vs sham", report)
        self.assertIn("Ceiling test", report)
        rows = {(r["condition"], r["trial"]): r for r in
                [analyze.game_metrics(g, RoundPlan(), analyze.load_labels(run))
                 for c in ("sham", "warm") for g in S.load_branches(run, c, [0, 1])]}
        self.assertEqual(rows[("sham", 0)]["susp_window_delta"], 0)
        self.assertGreater(rows[("warm", 0)]["susp_window_delta"], 0)
        self.assertTrue((self.tmp / run / "transcripts" / "readable" / "warm" / "trial_0.md").exists())

    def test_calibration_and_dry_run(self):
        self.assertEqual(quiet(run_trunk.main, ["--fake", "--tag", "c", "--calibrate", "--trials", "2"]), 0)
        summary = S.load_json(self.tmp / "haiku__naive__c" / "calib" / "summary.json")
        self.assertEqual(summary["games_complete"], 2)
        out = io.StringIO()
        with redirect_stdout(out):
            run_trunk.main(["--fake", "--tag", "d", "--trials", "4", "--dry-run"])
        self.assertIn("total", out.getvalue())
        self.assertFalse((self.tmp / "haiku__naive__d" / "trunk").exists())   # nothing played

    def test_design_change_needs_new_tag(self):
        quiet(run_trunk.main, ["--fake", "--tag", "x", "--trials", "1", "--keep", "1"])
        with self.assertRaises(S.ConfigMismatch):
            quiet(run_trunk.main, ["--fake", "--tag", "x", "--trials", "1", "--monitor-window", "3"])


class SelectionTests(unittest.TestCase):
    def game(self, successes, marks=False, status="complete"):
        rounds = []
        for r in (7, 8, 9):
            rounds.append({"round": r, "phase": "play", "outcome": {"ring_success": r - 7 < successes},
                           "reflections": {"J": {"exclude": ["Q"] if marks and r == 8 else []}}})
        return GameState(key="trunk.t0", trial_id=0, condition=None, config={}, rounds=rounds, status=status)

    def test_rule(self):
        plan = RoundPlan()
        self.assertTrue(selection_result(self.game(2), plan)["passed"])
        self.assertFalse(selection_result(self.game(1), plan)["passed"])
        self.assertFalse(selection_result(self.game(3, marks=True), plan)["passed"])
        self.assertFalse(selection_result(self.game(3, status="failed"), plan)["passed"])


if __name__ == "__main__":
    unittest.main()
