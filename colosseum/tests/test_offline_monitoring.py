from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from experiments.collusion.monitoring.evaluate import evaluate
from experiments.collusion.monitoring.access import policy_with_public_channels
from experiments.collusion.monitoring.annotations import load_annotation_set
from experiments.collusion.monitoring.ingest import load_run
from experiments.collusion.monitoring.observations import make_observation
from experiments.collusion.monitoring.rules import evaluate_monitor
from experiments.collusion.monitoring.synthetic import write_synthetic_labels, write_synthetic_run
from experiments.collusion.monitoring.preflight import validate_completed_run
from experiments.collusion.monitoring.provenance import build_channel_visibility_manifest


class OfflineMonitoringTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "synthetic"
        for case in ("benign", "suspicious", "harmful", "incomplete"):
            write_synthetic_run(self.root, case)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_observation_layers_do_not_leak_restricted_content(self) -> None:
        run = load_run(self.root / "harmful")
        policy = policy_with_public_channels(["0"])
        for layer in ("O0", "O1", "O2"):
            rendered = json.dumps(make_observation(run, layer, policy), default=lambda value: value.__dict__)
            self.assertNotIn("PRIVATE_LEAK_SENTINEL", rendered)
            self.assertNotIn("colluder", rendered)
            self.assertNotIn("private_channel_participants", rendered)
            self.assertNotIn('"secret_channel_enabled"', rendered)
        self.assertEqual(len(make_observation(run, "O0").events), 0)
        self.assertTrue(all(event["channel_id"] != "1" for event in make_observation(run, "O2", policy).events))

    def test_rule_monitor_distinguishes_cases(self) -> None:
        policy = policy_with_public_channels(["0"])
        self.assertEqual(evaluate_monitor(make_observation(load_run(self.root / "benign"), "O2", policy)).decision, "no_alert")
        self.assertEqual(evaluate_monitor(make_observation(load_run(self.root / "suspicious"), "O2", policy)).decision, "suspicious_coordination")
        self.assertEqual(evaluate_monitor(make_observation(load_run(self.root / "harmful"), "O2", policy)).decision, "harmful_coordination_signal")

    def test_incomplete_runs_are_reported_not_fabricated(self) -> None:
        run = load_run(self.root / "incomplete")
        self.assertEqual(run.status, "incomplete")
        self.assertIn("missing_file", [issue.code for issue in run.issues])
        self.assertEqual(evaluate_monitor(make_observation(run, "O0")).decision, "abstain")

    def test_end_to_end_evaluation_explicitly_handles_undefined_metrics(self) -> None:
        labels = self.root / "labels.json"
        write_synthetic_labels(labels)
        output = Path(self.temp.name) / "monitor-output"
        summary = evaluate(self.root, output, "O2", labels, ("0",))
        self.assertEqual(summary["run_count"], 4)
        self.assertEqual(summary["detection_recall"]["value"], 1.0)
        self.assertEqual(summary["false_positive_rate"]["value"], 0.0)
        self.assertTrue((output / "monitor_decisions.json").exists())
        decisions = (output / "monitor_decisions.json").read_text(encoding="utf-8")
        self.assertNotIn("evaluation_class", decisions)
        self.assertNotIn("positive_evidence_supported_harmful_coordination", decisions)
        self.assertTrue((output / "evaluation_join.json").exists())

    def test_missing_secret_metadata_keeps_board_visibility_unknown(self) -> None:
        run_dir = write_synthetic_run(self.root, "no-visibility")
        config_path = run_dir / "run_config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        config.pop("secret_blackboard_id")
        config_path.write_text(json.dumps(config), encoding="utf-8")
        self.assertEqual(len(make_observation(load_run(run_dir), "O1").events), 0)

    def test_unauthorized_public_channel_is_not_exposed(self) -> None:
        run = load_run(self.root / "harmful")
        self.assertEqual(len(make_observation(run, "O1").events), 0)
        self.assertTrue(make_observation(run, "O1", policy_with_public_channels(["0"])).events)

    def test_annotation_schema_and_indeterminate_class_are_explicit(self) -> None:
        labels = self.root / "labels.json"
        write_synthetic_labels(labels)
        kind, annotations = load_annotation_set(labels)
        self.assertEqual(kind, "synthetic")
        self.assertEqual(annotations["synthetic-suspicious"].evaluation_class, "indeterminate")

    def test_observation_does_not_claim_cross_artifact_chronology(self) -> None:
        observation = make_observation(
            load_run(self.root / "harmful"), "O2", policy_with_public_channels(["0"])
        )
        self.assertEqual(observation.chronology, "source_local_only")
        self.assertTrue(all("source_index" in event for event in observation.events))

    def test_preflight_accepts_source_faithful_complete_fixture(self) -> None:
        report = validate_completed_run(self.root / "harmful")
        self.assertTrue(report["monitoring_ready"])
        self.assertEqual(report["behavioral_conclusion"], "none")
        self.assertIn("chronology_scope", [issue["code"] for issue in report["issues"]])

    def test_preflight_rejects_ambiguous_visibility_and_bad_tool_order(self) -> None:
        run_dir = self.root / "harmful"
        manifest_path = run_dir / "channel_visibility_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["channels"][0]["declared_visibility"] = "unknown"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        tools_path = run_dir / "tool_events.json"
        tools = json.loads(tools_path.read_text(encoding="utf-8"))
        tools[1]["sequence_index"] = 9
        tools_path.write_text(json.dumps(tools), encoding="utf-8")
        report = validate_completed_run(run_dir)
        codes = [issue["code"] for issue in report["issues"]]
        self.assertIn("ambiguous_visibility", codes)
        self.assertIn("invalid_tool_event_order", codes)
        self.assertFalse(report["monitoring_ready"])

    def test_runtime_visibility_manifest_defaults_unknown_to_private(self) -> None:
        boards = [
            SimpleNamespace(blackboard_id="0", agents={"A", "B"}, template={}),
            SimpleNamespace(blackboard_id="1", agents={"A", "B"}, template={"secret_channel": True, "visibility": "private"}),
        ]
        manifest = build_channel_visibility_manifest(run_id="fixture", blackboards=boards)
        self.assertEqual(manifest["channels"][0]["declared_visibility"], "unknown")
        self.assertEqual(manifest["channels"][0]["effective_visibility"], "private")
        self.assertTrue(manifest["channels"][0]["ambiguous_visibility"])
        self.assertEqual(manifest["channels"][1]["visibility_source"], "runtime_template.secret_channel")


if __name__ == "__main__":
    unittest.main()
