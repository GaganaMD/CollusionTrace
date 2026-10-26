"""Tests for the ceiling test (blinding, items, scoring) on an offline run."""
import contextlib
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import experiment  # noqa: F401  (puts the harness on sys.path)
from experiment import ceiling_test, cli_common, run_branch, run_trunk, state
from experiment.clients import transcript_file


def run(main, *args):
    """Call a CLI main() with output silenced; return its exit code."""
    with contextlib.redirect_stdout(io.StringIO()):
        return main(["--model-set", "option_b", "--fake", *args])


class TestPieces(unittest.TestCase):
    def test_blind(self):
        text = "This is Agent R, and R agrees with Agent J. Quick note: Q left."
        self.assertEqual(ceiling_test.blind(text, ["Q", "R"]),
                         "This is [PLAYER], and [PLAYER] agrees with Agent J. Quick note: [PLAYER] left.")

    def test_parse_and_scores(self):
        self.assertEqual(ceiling_test.parse_answer({"content": '{"same_author": "No", "confidence": "80%"}'}),
                         {"same_author": "no", "confidence": 80})
        self.assertIsNone(ceiling_test.parse_answer({"content": '{"same_author": "maybe", "confidence": 5}'}))
        self.assertAlmostEqual(ceiling_test.different_score({"same_author": "no", "confidence": 100}), 1.0)
        self.assertAlmostEqual(ceiling_test.different_score({"same_author": "yes", "confidence": 100}), 0.0)
        self.assertEqual(ceiling_test.auc([0.9, 0.8], [0.1, 0.8]), 0.875)

    def test_headline_and_order_check(self):
        def row(cond, order, same, answer, conf):
            return {"condition": cond, "trial_id": 0, "order": order, "same_writer": same,
                    "content_cue": False, "answer": {"same_author": answer, "confidence": conf}}
        rows = [row("equal", "AB", False, "no", 80), row("equal", "BA", False, "unsure", 50),
                row("control", "AB", True, "yes", 70), row("control", "BA", True, "yes", 70)]
        m = ceiling_test.headline(rows)
        self.assertEqual((m["hit"], m["false_alarm"], m["accuracy"], m["auc"]), (0.5, 0.0, 0.75, 1.0))
        self.assertEqual(ceiling_test.order_agreement(rows), 0.5)

    def test_content_cue(self):
        self.assertTrue(ceiling_test.CONTENT_CUE.search("Hello fellow agents, I'm [PLAYER] taking over."))
        self.assertIsNone(ceiling_test.CONTENT_CUE.search("I'm fully on board with ordering CHEAP."))

    def test_transcript_routing(self):
        self.assertEqual(transcript_file(Path("/x"), "ceiling.equal.t3.AB.j0"),
                         Path("/x/ceiling/items.jsonl"))


class TestOffline(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.old = (state._runs_root, cli_common.FAKE_RUNS_DIR)
        state.set_runs_root(Path(self.tmp))
        cli_common.FAKE_RUNS_DIR = Path(self.tmp)

    def tearDown(self):
        state.set_runs_root(self.old[0])
        cli_common.FAKE_RUNS_DIR = self.old[1]
        shutil.rmtree(self.tmp)

    def test_run(self):
        run(run_trunk.main)
        run(run_branch.main, "--conditions", "control", "newcomer")
        self.assertEqual(run(ceiling_test.main), 0)
        out = state.run_dir("option_b") / "ceiling"
        records = [json.loads(x) for x in (out / "items.jsonl").read_text().splitlines()]
        self.assertEqual(len(records), 10 * 2 * 2)   # 10 branches x 2 orders x 2 judges
        newcomer = next(r for r in records if r["condition"] == "newcomer")
        self.assertFalse(newcomer["same_writer"])
        self.assertEqual(len(newcomer["set_a"]), 5)
        self.assertNotIn("Agent R", " ".join(newcomer["set_b"]))
        self.assertIn("Hit rate", (out / "ceiling_report.md").read_text().replace("hit rate", "Hit rate"))
        self.assertTrue((state.run_dir("option_b") / "transcripts/raw/ceiling/items.jsonl").exists())


if __name__ == "__main__":
    unittest.main()
