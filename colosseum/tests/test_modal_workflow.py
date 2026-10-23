from __future__ import annotations

import contextlib
import io
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from experiments.collusion import modal_workflow
from experiments.collusion.modal_config import load_prepared_config, validate_modal_config


ROOT = Path(__file__).resolve().parents[1]
SMOKE = ROOT / "experiments/collusion/configs/collusion_jira_modal_smoke.yaml"
COMPARISON = ROOT / "experiments/collusion/configs/collusion_jira_modal_comparison.yaml"


class ModalWorkflowTests(unittest.TestCase):
    def test_prepares_https_endpoint_and_redacts_no_values(self) -> None:
        cfg = load_prepared_config(
            SMOKE,
            environ={
                "MODAL_VLLM_BASE_URL": "https://example--server.modal.run/v1/",
                "MODAL_VLLM_API_KEY": "test-only-token",
            },
        )
        validate_modal_config(cfg)
        spec = cfg["llm_models"][0]["llm"]["vllm"]["models"][0]
        self.assertEqual(spec["base_url"], "https://example--server.modal.run/v1/")
        self.assertEqual(spec["served_model_name"], "Qwen/Qwen2.5-7B-Instruct")

    def test_rejects_non_https_and_legacy_max_tokens(self) -> None:
        cfg = load_prepared_config(
            SMOKE,
            environ={"MODAL_VLLM_BASE_URL": "http://localhost:8000/v1", "MODAL_VLLM_API_KEY": "x"},
        )
        with self.assertRaisesRegex(ValueError, "HTTPS"):
            validate_modal_config(cfg)
        cfg["llm_models"][0]["llm"]["vllm"]["models"][0]["base_url"] = "https://x.modal.run/v1"
        cfg["llm_models"][0]["llm"]["vllm"]["params"]["max_tokens"] = 1
        with self.assertRaisesRegex(ValueError, "max_tokens"):
            validate_modal_config(cfg)

    def test_research_configs_use_greedy_decoding(self) -> None:
        environ = {
            "MODAL_VLLM_BASE_URL": "https://example--server.modal.run/v1",
            "MODAL_VLLM_API_KEY": "test-only-token",
        }
        for path in (SMOKE, COMPARISON):
            cfg = load_prepared_config(path, environ=environ)
            params = cfg["llm_models"][0]["llm"]["vllm"]["params"]
            self.assertEqual(params["temperature"], 0, path.name)
            self.assertEqual(params["max_completion_tokens"], 512, path.name)

    def test_rejects_stochastic_decoding(self) -> None:
        cfg = load_prepared_config(
            SMOKE,
            environ={
                "MODAL_VLLM_BASE_URL": "https://example--server.modal.run/v1",
                "MODAL_VLLM_API_KEY": "test-only-token",
            },
        )
        cfg["llm_models"][0]["llm"]["vllm"]["params"]["temperature"] = 0.1
        with self.assertRaisesRegex(ValueError, "temperature: 0"):
            validate_modal_config(cfg)

    def test_dry_run_never_calls_runner(self) -> None:
        env = {
            **os.environ,
            "MODAL_VLLM_BASE_URL": "https://example--server.modal.run/v1",
            "MODAL_VLLM_API_KEY": "test-only-token",
        }
        stdout = io.StringIO()
        with patch.dict(os.environ, env, clear=True), patch.object(
            sys, "argv", ["modal_workflow", "run", "--config", str(SMOKE), "--dry-run"]
        ), contextlib.redirect_stdout(stdout):
            modal_workflow.main()
        self.assertIn('"dry_run": true', stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
