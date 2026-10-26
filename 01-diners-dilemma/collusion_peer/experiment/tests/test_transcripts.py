"""Tests for the transcript logging and the readable export."""
import contextlib
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import experiment  # noqa: F401  (puts the harness on sys.path)
from experiment import cli_common, export_transcripts, run_branch, run_trunk, state
from experiment.clients import Clients, transcript_file
from experiment.fake_client import FakeClient


def run(main, *args):
    """Call a CLI main() with output silenced; return its exit code."""
    with contextlib.redirect_stdout(io.StringIO()):
        return main(["--model-set", "option_b", "--fake", *args])


class TestTranscriptFile(unittest.TestCase):
    def test_paths(self):
        root = Path("/x")
        self.assertEqual(transcript_file(root, "r5.equal_told.t3.refl.Q>J"),
                         root / "equal_told" / "trial_3.jsonl")
        self.assertEqual(transcript_file(root, "r0.trunk.t11.s1.J"), root / "trunk" / "trial_11.jsonl")
        self.assertEqual(transcript_file(root, "judge.abc123"), root / "judge" / "notes.jsonl")


class TestLogging(unittest.TestCase):
    def test_reasks_are_logged_with_attempts(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake = FakeClient(fail={"r0.trunk.t0.s1.J": 1})
            clients = Clients(fake, fake, transcript_dir=Path(tmp))
            req = {"custom_id": "r0.trunk.t0.s1.J", "model": "gpt-4o-mini",
                   "messages": [{"role": "system", "content": "SYS"}, {"role": "user", "content": "USR"}]}
            clients.execute([req], "test")
            clients.execute([req], "test")
            lines = [json.loads(x) for x in (Path(tmp) / "trunk" / "trial_0.jsonl").read_text().splitlines()]
            self.assertEqual([x["attempt"] for x in lines], [1, 2])
            self.assertEqual((lines[0]["system_prompt"], lines[0]["user_prompt"]), ("SYS", "USR"))
            self.assertIn("Sorry", json.dumps(lines[0]["raw_reply"]))       # the failed reply is kept
            self.assertIn("intended_action", json.dumps(lines[1]["raw_reply"]))


class TestLoggingNeverKillsARun(unittest.TestCase):
    def test_unwritable_folder_warns_and_keeps_replies(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake = FakeClient()
            clients = Clients(fake, fake, transcript_dir=Path(tmp))
            Path(tmp).chmod(0o500)   # becomes read-only after the start-up check
            try:
                req = {"custom_id": "r0.trunk.t0.s1.J", "model": "gpt-4o-mini",
                       "messages": [{"role": "system", "content": "S"}, {"role": "user", "content": "U"}]}
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    replies = clients.execute([req], "test")
                self.assertIn("r0.trunk.t0.s1.J", replies)
                self.assertIn("WARNING: could not write transcripts", out.getvalue())
            finally:
                Path(tmp).chmod(0o700)

    def test_unwritable_folder_fails_before_spending(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp).chmod(0o500)
            try:
                with self.assertRaises(OSError):
                    Clients(FakeClient(), FakeClient(), transcript_dir=Path(tmp) / "raw")
            finally:
                Path(tmp).chmod(0o700)


class TestPipelineTranscripts(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.old = (state._runs_root, cli_common.FAKE_RUNS_DIR)
        state.set_runs_root(Path(self.tmp))
        cli_common.FAKE_RUNS_DIR = Path(self.tmp)

    def tearDown(self):
        state.set_runs_root(self.old[0])
        cli_common.FAKE_RUNS_DIR = self.old[1]
        shutil.rmtree(self.tmp)

    def test_every_game_has_raw_and_readable_transcripts(self):
        run(run_trunk.main)
        run(run_branch.main, "--conditions", "newcomer", "control")
        run(export_transcripts.main)
        root = state.run_dir("option_b")
        raw = sorted(p.relative_to(root / "transcripts" / "raw").as_posix()
                     for p in (root / "transcripts" / "raw").rglob("*.jsonl"))
        self.assertEqual(len([p for p in raw if p.startswith("trunk/")]), 8)
        self.assertEqual(len([p for p in raw if p.startswith("newcomer/")]), 5)
        # every request of a branch lands in that branch's file, prompts included
        raw_file = root / "transcripts/raw/newcomer/trial_0.jsonl"
        lines = [json.loads(x) for x in raw_file.read_text().splitlines()]
        self.assertTrue(all(".newcomer.t0." in x["request_id"] for x in lines))
        self.assertTrue(any("no longer in the game" in (x["system_prompt"] or "") for x in lines))
        readable = (root / "transcripts/readable/newcomer/trial_0.md").read_text()
        for heading in ("Private plans", "Public announcements", "Trust ratings", "Probe answers"):
            self.assertIn(heading, readable)
        self.assertTrue((root / "transcripts/readable/trunk/trial_7.md").exists())
        self.assertIn("| `trunk/selection.json`", (root / "ARTIFACTS.md").read_text())


if __name__ == "__main__":
    unittest.main()
