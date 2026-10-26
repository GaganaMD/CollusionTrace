"""Tests for boolean probe answers and re-deriving probes from raw transcripts."""
import contextlib
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import experiment  # noqa: F401  (puts the harness on sys.path)
from experiment import cli_common, reparse_probes, run_branch, run_trunk, state
from experiment.probe import allowed_which, parse_probe

ALLOWED = allowed_which(["J", "M", "Q", "T", "Z"], None)


def run(main, *args):
    """Call a CLI main() with output silenced; return its exit code."""
    with contextlib.redirect_stdout(io.StringIO()):
        return main(["--model-set", "option_b", "--fake", *args])


class TestBooleanAnswers(unittest.TestCase):
    def test_booleans(self):
        p = parse_probe({"replaced": True, "which": "Q", "confidence": 80}, ALLOWED, ask_same=False)
        self.assertEqual(p, {"replaced": "yes", "which": "Q", "confidence": 80})
        p = parse_probe({"content": '{"replaced": false, "which": "none", "confidence": 90}'}, ALLOWED, False)
        self.assertEqual(p["replaced"], "no")
        p = parse_probe({"content": '{"replaced": "True", "which": "none", "confidence": 9}'}, ALLOWED, False)
        self.assertEqual(p["replaced"], "yes")


class TestBooleansElsewhere(unittest.TestCase):
    def test_ceiling_and_judge_accept_booleans(self):
        from experiment import ceiling_test, judge_notes
        self.assertEqual(ceiling_test.parse_answer({"same_author": True, "confidence": 70}),
                         {"same_author": "yes", "confidence": 70})
        self.assertEqual(ceiling_test.parse_answer({"content": '{"same_author": false, "confidence": 70}'}),
                         {"same_author": "no", "confidence": 70})
        self.assertEqual(judge_notes.parse_labels({"identity": False, "style": "true", "behavior": "no"}),
                         {"identity": False, "style": True, "behavior": False})


class TestReparse(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.old = (state._runs_root, cli_common.FAKE_RUNS_DIR)
        state.set_runs_root(Path(self.tmp))
        cli_common.FAKE_RUNS_DIR = Path(self.tmp)

    def tearDown(self):
        state.set_runs_root(self.old[0])
        cli_common.FAKE_RUNS_DIR = self.old[1]
        shutil.rmtree(self.tmp)

    def test_first_parseable_attempt_wins(self):
        run(run_trunk.main)
        run(run_branch.main, "--conditions", "equal")
        raw = state.run_dir("option_b") / "transcripts/raw/equal/trial_0.jsonl"
        lines = [json.loads(x) for x in raw.read_text().splitlines()]
        target = next(x for x in lines if ".probe.J" in x["request_id"])
        # Pretend the first attempt was a boolean 'yes' that the old parser rejected,
        # followed by a re-ask answering 'no'.
        session = target["session"]
        lines.insert(lines.index(target), {**target, "attempt": 1,
                                            "raw_reply": {"replaced": True, "which": "Q", "confidence": 70}})
        target["attempt"] = 2
        lines.append({**target, "session": "00000000T000000",            # older session: ignored
                      "raw_reply": {"replaced": "yes", "which": "T", "confidence": 1}})
        raw.write_text("".join(json.dumps(x) + "\n" for x in lines))
        self.assertEqual(session > "00000000T000000", True)

        self.assertEqual(run(reparse_probes.main), 0)
        b = state.load_state(state.branch_path("option_b", "equal", 0))
        r = int(target["request_id"].split(".")[0][1:])
        p = next(x for x in b.probes if x["round_id"] == r and x["agent"] == "J")
        self.assertEqual((p["replaced"], p["which"], p["parsed_from_attempt"]), ("yes", "Q", 1))
        self.assertEqual(p["before_reparse"]["replaced"], "no")
        # Rerunning is stable: before_reparse keeps the original answer.
        run(reparse_probes.main)
        b2 = state.load_state(state.branch_path("option_b", "equal", 0))
        p2 = next(x for x in b2.probes if x["round_id"] == r and x["agent"] == "J")
        self.assertEqual(p2["before_reparse"]["replaced"], "no")


if __name__ == "__main__":
    unittest.main()
