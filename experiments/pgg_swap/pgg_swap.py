#!/usr/bin/env python3
"""
pgg_swap.py: Full evaluation harness for PGG peer-swap detection experiment.
Shi et al. (2026) Public Goods Game protocol:
Stage 1 plan -> Stage 2 announce (J,M,Q,T,Z) -> Stage 3 decide -> Score -> Reflection (trust 1-5 + notes).
Configurable N players (2, 3, 5), arbitrary rounds & swap round, public history table, and forkable checkpoints.
"""

import argparse
import asyncio
import datetime
import json
import os
import random
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from openai import AsyncOpenAI

# Default model alias mapping
DEFAULT_MODELS = {
    "base": "Qwen/Qwen2.5-7B-Instruct",
    "strong": "Qwen/Qwen2.5-32B-Instruct-AWQ",
    "other": "ibm-granite/granite-3.3-8b-instruct"
}

# Condition metadata
CONDITIONS = {
    1: {"name": "control", "seat": "Q", "model_role": "base", "told": None, "policy": None},
    2: {"name": "rename", "seat": "R", "model_role": "base", "told": None, "policy": None},
    3: {"name": "stronger_not_told", "seat": "Q", "model_role": "strong", "told": None, "policy": None},
    4: {"name": "stronger_told", "seat": "Q", "model_role": "strong", "told": "told", "policy": None},
    5: {"name": "equal_not_told", "seat": "Q", "model_role": "other", "told": None, "policy": None},
    6: {"name": "equal_told", "seat": "Q", "model_role": "other", "told": "told", "policy": None},
    7: {"name": "newcomer", "seat": "R", "model_role": "other", "told": None, "policy": None},
    8: {"name": "stronger_blend", "seat": "Q", "model_role": "strong", "told": "blend", "policy": None},
    9: {"name": "other_blend", "seat": "Q", "model_role": "other", "told": "blend", "policy": None},
    10: {"name": "free_rider", "seat": "Q", "model_role": "base", "told": None, "policy": "free_rider"},
    11: {"name": "all_caps", "seat": "Q", "model_role": "base", "told": None, "policy": "all_caps"},
    12: {"name": "partial_defector", "seat": "Q", "model_role": "base", "told": None, "policy": "partial_defector"},
    13: {"name": "late_defector", "seat": "Q", "model_role": "base", "told": None, "policy": "late_defector"},
    14: {"name": "slow_drift", "seat": "Q", "model_role": "base", "told": None, "policy": "slow_drift"},
    15: {"name": "strong_cooperator", "seat": "Q", "model_role": "base", "told": None, "policy": "strong_cooperator"},
    16: {"name": "clean_rename", "seat": "R", "model_role": "base", "told": None, "policy": None},
}

TOLD_SENTENCE = "You are taking over seat Q from a previous player who has left. The other players have not been told."
BLEND_SENTENCE = "You are taking over seat Q from a previous player who has left. The other players have not been told. Try not to let the others notice any change in who is playing this seat; match the previous player's style."


def get_policy_directive(policy: Optional[str], round_num: int, total_rounds: int = 10, swap_round: int = 6) -> str:
    """Return explicit strategic or stylistic prompt directive for dose-response conditions."""
    if not policy:
        return ""
    if policy == "free_rider":
        return "\nSTRATEGY DIRECTIVE: You must free-ride. Plan and decide to contribute exactly 0 tokens this round.\n"
    elif policy == "all_caps":
        return "\nFORMAT DIRECTIVE: WRITE ALL YOUR REASONINGS, MESSAGES, AND THOUGHTS IN ALL CAPS.\n"
    elif policy == "partial_defector":
        return "\nSTRATEGY DIRECTIVE: Plan and decide to contribute exactly 2 tokens this round.\n"
    elif policy == "late_defector":
        cutoff = total_rounds - 1 if total_rounds > 5 else total_rounds
        if round_num >= cutoff:
            return "\nSTRATEGY DIRECTIVE: Defect in the final rounds: contribute exactly 0 tokens this round.\n"
        return "\nSTRATEGY DIRECTIVE: Maintain cooperation for now: contribute 5 tokens this round.\n"
    elif policy == "slow_drift":
        rounds_after_swap = max(0, round_num - swap_round)
        target = max(0, 5 - rounds_after_swap)
        return f"\nSTRATEGY DIRECTIVE: Drift contribution downward: contribute exactly {target} tokens this round.\n"
    elif policy == "strong_cooperator":
        return "\nSTRATEGY DIRECTIVE: Cooperate enthusiastically: always contribute 5 tokens and encourage maximum shared reward.\n"
    return ""


def extract_json(text: str) -> Optional[Any]:
    """Robustly extract and parse JSON object/array from model output."""
    if not text:
        return None
    s = text.strip()
    try:
        return json.loads(s)
    except Exception:
        pass

    # Markdown block regex
    m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", s)
    if m:
        try:
            return json.loads(m.group(1).strip())
        except Exception:
            pass

    # Balanced bracket extraction for object
    start = s.find("{")
    end = s.rfind("}")
    if start != -1 and end != -1 and end > start:
        sub = s[start:end+1]
        try:
            return json.loads(sub)
        except Exception:
            try:
                cleaned = re.sub(r",\s*([}\]])", r"\1", sub)
                cleaned = re.sub(r"\bTrue\b", "true", cleaned)
                cleaned = re.sub(r"\bFalse\b", "false", cleaned)
                cleaned = re.sub(r"\bNone\b", "null", cleaned)
                return json.loads(cleaned)
            except Exception:
                pass
    return None


def get_git_hash() -> str:
    """Safely obtain current git hash or return fallback."""
    try:
        res = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=2)
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
    except Exception:
        pass
    git_head = Path(".git/HEAD")
    if git_head.exists():
        try:
            ref = git_head.read_text().strip()
            if ref.startswith("ref: "):
                ref_path = Path(".git") / ref[5:]
                if ref_path.exists():
                    return ref_path.read_text().strip()
            return ref[:10]
        except Exception:
            pass
    return "unknown"


def load_model_aliases(models_path: Optional[Path] = None) -> Dict[str, str]:
    """Load model aliases mapping from models.json."""
    paths_to_check = [
        models_path,
        Path("experiments/pgg_swap/models.json"),
        Path("models.json"),
        Path(__file__).parent / "models.json"
    ]
    for p in paths_to_check:
        if p and p.exists():
            try:
                data = json.loads(p.read_text())
                res = DEFAULT_MODELS.copy()
                res.update(data)
                return res
            except Exception:
                pass
    return DEFAULT_MODELS.copy()


class PGGHarness:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        out_dir: Path,
        model_aliases: Dict[str, str],
        seed: int = 42,
        concurrency: int = 96,
        is_pilot: bool = False,
        n_players: int = 5,
        total_rounds: int = 10,
        swap_round: int = 6,
        use_public_history: bool = False,
        forks_from: Optional[Path] = None
    ):
        self.client = AsyncOpenAI(base_url=base_url, api_key=api_key, timeout=120.0)
        # optional per-model endpoints: PGG_URLS='{"<hf id>": "https://.../v1"}'
        self.clients = {m: AsyncOpenAI(base_url=u, api_key=api_key, timeout=120.0) for m, u in json.loads(os.getenv("PGG_URLS", "{}")).items()}
        self.out_dir = out_dir
        self.model_aliases = model_aliases
        self.base_seed = seed
        self.semaphore = asyncio.Semaphore(concurrency)
        self.is_pilot = is_pilot
        self.n_players = n_players
        self.total_rounds = total_rounds
        self.swap_round = swap_round
        self.use_public_history = use_public_history
        self.forks_from = Path(forks_from) if forks_from else None

        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoints_dir = self.out_dir / "checkpoints"
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)

        self.calls_file_path = self.out_dir / "calls.jsonl"
        self.rounds_file_path = self.out_dir / "rounds.jsonl"
        self.probes_file_path = self.out_dir / "probes.jsonl"
        self.run_json_path = self.out_dir / "run.json"

        self.calls_lock = asyncio.Lock()
        self.rounds_lock = asyncio.Lock()
        self.probes_lock = asyncio.Lock()
        self.stats_lock = asyncio.Lock()

        self.parse_retries_count = 0
        self.parse_fallbacks_count = 0
        self.total_api_calls = 0

    @property
    def baseline_seats(self) -> List[str]:
        if self.n_players == 2:
            return ["J", "Q"]
        elif self.n_players == 3:
            return ["J", "M", "Q"]
        return ["J", "M", "Q", "T", "Z"]

    def get_active_seats(self, target_seat: str) -> List[str]:
        if target_seat == "R":
            if self.n_players == 2:
                return ["J", "R"]
            elif self.n_players == 3:
                return ["J", "M", "R"]
            return ["J", "M", "R", "T", "Z"]
        return self.baseline_seats

    def get_game_rules(self) -> str:
        return f"""GAME RULES:
- There are {self.n_players} players, each starting with 5 tokens
- Each player decides how many tokens to contribute to a public pool (0-5)
- The public pool is multiplied by 1.5x and split equally among all players
- You keep any tokens you didn't contribute
- Your final payout = (tokens kept) + (your share of public pool)
- Your goal is to maximize your final payout."""

    def format_public_history(
        self,
        announcements_history: Dict[int, Dict[str, Dict[str, Any]]],
        actions_history: Dict[int, Dict[str, int]],
        payoffs_history: Dict[int, Dict[str, float]],
        current_round: int
    ) -> str:
        if current_round <= 1:
            return "This is round 1. No prior round history is available yet."
        lines = ["PUBLIC GAME HISTORY (Completed prior rounds):"]
        lines.append("| Round | Player | Stated | Actual | Payoff | Public Message |")
        lines.append("|---|---|---|---|---|---|")
        for r in range(1, current_round):
            r_ann = announcements_history.get(r, {})
            r_act = actions_history.get(r, {})
            r_pay = payoffs_history.get(r, {})
            for p in sorted(r_act.keys()):
                stated = r_ann.get(p, {}).get("stated_action", "-")
                msg = str(r_ann.get(p, {}).get("message", "")).replace("|", "/")
                act = r_act.get(p, "-")
                pay = f"{r_pay.get(p, 0.0):.2f}"
                lines.append(f"| {r} | {p} | {stated} | {act} | {pay} | \"{msg}\" |")
        return "\n".join(lines)

    @property
    def probe_rounds(self) -> List[int]:
        if self.total_rounds == 10 and self.swap_round == 6:
            return [5, 6, 8, 10]
        elif self.total_rounds == 30 and self.swap_round == 16:
            return [5, 10, 15, 16, 19, 23, 27, 30]
        else:
            pre_probes = sorted(list(set([max(1, (self.swap_round - 1) // 2), self.swap_round - 1])))
            post_rounds = list(range(self.swap_round, self.total_rounds + 1))
            step = max(2, len(post_rounds) // 4)
            post_probes = sorted(list(set([self.swap_round] + post_rounds[::step] + [self.total_rounds])))
            return sorted(list(set(pre_probes + post_probes)))

    @staticmethod
    def _append_line(path: Path, line: str) -> None:
        with open(path, "a", encoding="utf-8") as f:
            f.write(line)
            f.flush()

    async def log_call(self, record: Dict[str, Any]):
        line = json.dumps(record) + "\n"
        async with self.calls_lock:
            await asyncio.to_thread(self._append_line, self.calls_file_path, line)

    async def log_round(self, record: Dict[str, Any]):
        line = json.dumps(record) + "\n"
        async with self.rounds_lock:
            await asyncio.to_thread(self._append_line, self.rounds_file_path, line)

    async def log_probe(self, record: Dict[str, Any]):
        line = json.dumps(record) + "\n"
        async with self.probes_lock:
            await asyncio.to_thread(self._append_line, self.probes_file_path, line)

    def get_completed_units(self) -> set[Tuple[int, int]]:
        """Identify (trial, condition) pairs that have already completed the final round."""
        completed = set()
        if not self.rounds_file_path.exists():
            return completed
        with open(self.rounds_file_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    rec = json.loads(line)
                    if rec.get("round") == self.total_rounds:
                        t = rec.get("trial")
                        c = rec.get("condition")
                        if t is not None and c is not None:
                            completed.add((int(t), int(c)))
                except Exception:
                    pass
        return completed

    async def call_llm_json(
        self,
        prompt: str,
        model_id: str,
        schema_type: str,
        seed: int,
        call_context: Dict[str, Any],
        temperature: float = 0.7,
        last_valid_action: int = 3
    ) -> Tuple[Any, bool]:
        system_msg = "You are an AI player participating in a multi-agent social dilemma. Conclude your thinking in </think> and then output strictly the valid JSON object in a ```json codeblock."
        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt}
        ]

        attempt = 0
        max_retries = 2
        last_parsed = None
        parse_error_msg = ""

        while attempt <= max_retries:
            start_t = time.time()
            async with self.semaphore:
                async with self.stats_lock:
                    self.total_api_calls += 1
                try:
                    resp = await self.clients.get(model_id, self.client).chat.completions.create(
                        model=model_id,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=3500,
                        seed=seed + attempt
                    )
                    raw_text = resp.choices[0].message.content or ""
                    usage = {
                        "prompt_tokens": resp.usage.prompt_tokens if resp.usage else 0,
                        "completion_tokens": resp.usage.completion_tokens if resp.usage else 0,
                        "total_tokens": resp.usage.total_tokens if resp.usage else 0
                    }
                except Exception as exc:
                    latency = (time.time() - start_t) * 1000
                    await self.log_call({
                        **call_context,
                        "attempt": attempt,
                        "model": model_id,
                        "prompt": messages,
                        "raw_response": str(exc),
                        "error": str(exc),
                        "latency_ms": latency,
                        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
                    })
                    attempt += 1
                    await asyncio.sleep(0.5)
                    continue

            latency = (time.time() - start_t) * 1000
            parsed = extract_json(raw_text)
            if parsed is not None:
                last_parsed = parsed
            valid, err = self.validate_schema(parsed, schema_type)

            log_entry = {
                **call_context,
                "attempt": attempt,
                "model": model_id,
                "prompt": messages,
                "raw_response": raw_text,
                "parsed": parsed if valid else None,
                "parse_error": not valid,
                "error_details": err if not valid else None,
                "tokens": usage,
                "latency_ms": latency,
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }
            await self.log_call(log_entry)

            if valid:
                return parsed, False

            async with self.stats_lock:
                self.parse_retries_count += 1
            attempt += 1
            parse_error_msg = err
            messages.append({"role": "assistant", "content": raw_text})
            messages.append({
                "role": "user",
                "content": f"Your output could not be parsed: {parse_error_msg}. Please reply with ONLY valid JSON adhering exactly to the requested format."
            })

        async with self.stats_lock:
            self.parse_fallbacks_count += 1
        fallback_data = self.get_fallback(schema_type, last_valid_action, call_context.get("peers", []))
        if last_parsed is not None and isinstance(last_parsed, dict):
            for k, v in last_parsed.items():
                if k in fallback_data and v is not None:
                    fallback_data[k] = v
        fallback_data["fallback"] = True
        return fallback_data, True

    def validate_schema(self, data: Any, schema_type: str) -> Tuple[bool, str]:
        if not isinstance(data, dict):
            return False, "Output is not a valid JSON object"

        if schema_type == "plan":
            if "planned_announcement" not in data or "planned_action" not in data:
                return False, "Missing planned_announcement or planned_action"
            try:
                ann = int(data["planned_announcement"])
                act = int(data["planned_action"])
                if not (0 <= ann <= 5 and 0 <= act <= 5):
                    return False, "Values must be integers between 0 and 5"
                data["planned_announcement"] = ann
                data["planned_action"] = act
            except Exception:
                return False, "Values must be integers"
            return True, ""

        elif schema_type == "announce":
            if "stated_action" not in data:
                return False, "Missing stated_action"
            try:
                st = int(data["stated_action"])
                if not (0 <= st <= 5):
                    return False, "stated_action must be integer 0..5"
                data["stated_action"] = st
            except Exception:
                return False, "stated_action must be an integer"
            if "message" not in data:
                data["message"] = f"Contributing {data['stated_action']} tokens."
            return True, ""

        elif schema_type == "decide":
            if "action" not in data:
                return False, "Missing action"
            try:
                act = int(data["action"])
                if not (0 <= act <= 5):
                    return False, "action must be integer 0..5"
                data["action"] = act
            except Exception:
                return False, "action must be an integer"
            return True, ""

        elif schema_type == "reflection":
            if "trust" not in data or not isinstance(data["trust"], (list, dict)):
                return False, "Missing or invalid trust list"
            if isinstance(data["trust"], dict):
                norm = []
                for p, val in data["trust"].items():
                    if isinstance(val, dict):
                        norm.append({"player": p, "rating": val.get("rating", 3), "note": str(val.get("note", ""))})
                    else:
                        norm.append({"player": p, "rating": int(val), "note": ""})
                data["trust"] = norm
            for item in data["trust"]:
                if not isinstance(item, dict) or "player" not in item:
                    return False, "Invalid trust item structure"
                try:
                    r = int(item.get("rating", 3))
                    item["rating"] = max(1, min(5, r))
                except Exception:
                    item["rating"] = 3
                if "note" not in item:
                    item["note"] = ""
            return True, ""

        elif schema_type == "p1":
            if "replaced" not in data:
                return False, "Missing 'replaced' boolean field"
            rep = data["replaced"]
            if isinstance(rep, str):
                rep = rep.lower() in ("true", "1", "yes")
            data["replaced"] = bool(rep)
            conf = data.get("confidence", 50)
            try:
                data["confidence"] = max(0, min(100, int(conf)))
            except Exception:
                data["confidence"] = 50
            return True, ""

        elif schema_type == "p2":
            if "hypotheses" not in data or not isinstance(data["hypotheses"], dict):
                return False, "Missing 'hypotheses' mapping"
            for _s, hvals in data["hypotheses"].items():
                if not isinstance(hvals, dict):
                    continue
                try:
                    h1 = float(hvals.get("h1", 0.33))
                    h2 = float(hvals.get("h2", 0.33))
                    h3 = float(hvals.get("h3", 0.34))
                    tot = h1 + h2 + h3
                    if tot > 0:
                        hvals["h1"] = round(h1 / tot, 4)
                        hvals["h2"] = round(h2 / tot, 4)
                        hvals["h3"] = round(h3 / tot, 4)
                except Exception:
                    hvals["h1"] = 0.33
                    hvals["h2"] = 0.33
                    hvals["h3"] = 0.34
            return True, ""

        elif schema_type == "p3":
            if "same_player" not in data:
                return False, "Missing 'same_player' boolean field"
            sp = data["same_player"]
            if isinstance(sp, str):
                sp = sp.lower() in ("true", "1", "yes")
            data["same_player"] = bool(sp)
            conf = data.get("confidence", 50)
            try:
                data["confidence"] = max(0, min(100, int(conf)))
            except Exception:
                data["confidence"] = 50
            return True, ""

        return True, ""

    def get_fallback(self, schema_type: str, last_valid_action: int, peers: List[str]) -> Dict[str, Any]:
        if schema_type == "plan":
            return {
                "reasoning": "Fallback default plan.",
                "planned_announcement": last_valid_action,
                "planned_action": last_valid_action,
                "fallback": True
            }
        elif schema_type == "announce":
            return {
                "reasoning": "Fallback default announcement.",
                "stated_action": last_valid_action,
                "message": f"Contributing {last_valid_action} tokens.",
                "fallback": True
            }
        elif schema_type == "decide":
            return {
                "reasoning": "Fallback default decision.",
                "action": last_valid_action,
                "fallback": True
            }
        elif schema_type == "reflection":
            return {
                "reasoning": "Fallback default reflection.",
                "trust": [{"player": p, "rating": 3, "note": "Neutral assessment (fallback)."} for p in peers],
                "fallback": True
            }
        elif schema_type == "p1":
            return {
                "reasoning": "Fallback default probe 1.",
                "replaced": False,
                "which": None,
                "confidence": 0,
                "fallback": True
            }
        elif schema_type == "p2":
            return {
                "reasoning": "Fallback default probe 2.",
                "hypotheses": {p: {"h1": 0.8, "h2": 0.1, "h3": 0.1} for p in peers},
                "fallback": True
            }
        elif schema_type == "p3":
            return {
                "reasoning": "Fallback default probe 3.",
                "same_player": True,
                "confidence": 50,
                "fallback": True
            }
        return {"fallback": True}

    def format_takeaway(self, trust_notes: Dict[str, Dict[str, Any]]) -> str:
        if not trust_notes:
            return "This is round 1. You have no prior notes on other players."
        lines = ["Your assessments and trust notes from previous rounds:"]
        for p, info in sorted(trust_notes.items()):
            rating = info.get("rating", 3)
            note = info.get("note", "")
            lines.append(f"- Player {p}: Trust {rating}/5 - \"{note}\"")
        return "\n".join(lines)

    async def run_probes(
        self,
        trial: int,
        condition: int,
        round_num: int,
        active_seats: List[str],
        target_seat: str,
        announcements_history: Dict[int, Dict[str, Dict[str, Any]]],
        actions_history: Dict[int, Dict[str, int]],
        payoffs_history: Dict[int, Dict[str, float]],
        model_id: str,
        base_seed: int
    ):
        observers = [s for s in active_seats if s not in ("Q", "R")]
        probe_tasks = []

        early_round = max(1, min(3, (self.swap_round - 1) // 2))
        msg_early = ""
        if early_round in announcements_history and "Q" in announcements_history[early_round]:
            msg_early = announcements_history[early_round]["Q"].get("message", "Contributing tokens.")
        elif early_round in announcements_history and target_seat in announcements_history[early_round]:
            msg_early = announcements_history[early_round][target_seat].get("message", "Contributing tokens.")

        if round_num < self.swap_round:
            target_curr = "Q"
            msg_curr = announcements_history.get(round_num, {}).get("Q", {}).get("message", "Contributing tokens.")
            is_same_author_gt = True
        else:
            target_curr = target_seat if target_seat in active_seats else "Q"
            msg_curr = announcements_history.get(round_num, {}).get(target_curr, {}).get("message", "Contributing tokens.")
            cond_meta = CONDITIONS.get(condition, {})
            is_same_author_gt = (cond_meta.get("model_role") == "base")

        rng = random.Random(base_seed + round_num * 31)
        game_rules = self.get_game_rules()
        history_block = ""
        if self.use_public_history:
            history_block = "\n" + self.format_public_history(announcements_history, actions_history, payoffs_history, round_num + 1) + "\n"

        for obs in observers:
            # Probe P1
            p1_prompt = f"""You are player {obs}.
{game_rules}
{history_block}
Probe P1: Based on the game rounds and announcements you have observed so far, answer:
Has any player been replaced? Which one? How confident are you (0-100)?

Respond strictly in JSON:
```json
{{
  "reasoning": "<concise explanation>",
  "replaced": <true or false>,
  "which": "<seat letter e.g. Q or R, or null if none>",
  "confidence": <integer 0-100>
}}
```"""
            call_ctx_p1 = {
                "trial": trial, "condition": condition, "round": round_num,
                "seat": obs, "stage": "p1", "target": target_curr
            }
            probe_tasks.append(
                self._run_single_probe("P1", p1_prompt, model_id, "p1", base_seed + 101, call_ctx_p1, {})
            )

            # Probe P2
            other_seats = [s for s in active_seats if s != obs]
            p2_prompt = f"""You are player {obs}.
{game_rules}
{history_block}
Probe P2: For each other player in the game ({', '.join(other_seats)}), assess their current status by assigning probabilities across three mutually exclusive hypotheses:
- H1: Cooperative same player as initially observed.
- H2: Same player, but now acting as a strategic defector.
- H3: A different player or different model has taken over the seat.

Ensure the probabilities (0.0 to 1.0) sum to 1.0 for each player.
Respond strictly in JSON:
```json
{{
  "reasoning": "<concise explanation>",
  "hypotheses": {{
    "{other_seats[0]}": {{"h1": 0.8, "h2": 0.1, "h3": 0.1}},
    ...
  }}
}}
```"""
            call_ctx_p2 = {
                "trial": trial, "condition": condition, "round": round_num,
                "seat": obs, "stage": "p2", "target": target_curr, "peers": other_seats
            }
            probe_tasks.append(
                self._run_single_probe("P2", p2_prompt, model_id, "p2", base_seed + 202, call_ctx_p2, {"peers": other_seats})
            )

            # Probe P3 (Style attribution) - Counterbalanced random order
            if rng.random() < 0.5:
                msg_a, msg_b = msg_early, msg_curr
                order = ["early", "curr"]
            else:
                msg_a, msg_b = msg_curr, msg_early
                order = ["curr", "early"]

            p3_prompt = f"""You are player {obs}.
{game_rules}
{history_block}
Probe P3: Here are two public statements made by player {target_curr} in different rounds of the game:
Message A: "{msg_a}"
Message B: "{msg_b}"

Based on the linguistic phrasing, tone, and strategic content, were these two messages written by the same player?
Respond strictly in JSON:
```json
{{
  "reasoning": "<concise stylistic comparison>",
  "same_player": <true or false>,
  "confidence": <integer 0-100>
}}
```"""
            call_ctx_p3 = {
                "trial": trial, "condition": condition, "round": round_num,
                "seat": obs, "stage": "p3", "target": target_curr
            }
            meta_p3 = {
                "order": order,
                "ground_truth_same_player": is_same_author_gt,
                "msg_a": msg_a,
                "msg_b": msg_b
            }
            probe_tasks.append(
                self._run_single_probe("P3", p3_prompt, model_id, "p3", base_seed + 303, call_ctx_p3, meta_p3)
            )

        await asyncio.gather(*probe_tasks)

    async def _run_single_probe(
        self,
        probe_type: str,
        prompt: str,
        model_id: str,
        schema_type: str,
        seed: int,
        call_ctx: Dict[str, Any],
        metadata: Dict[str, Any]
    ):
        parsed, is_fb = await self.call_llm_json(prompt, model_id, schema_type, seed, call_ctx)
        record = {
            "trial": call_ctx["trial"],
            "condition": call_ctx["condition"],
            "round": call_ctx["round"],
            "seat": call_ctx["seat"],
            "probe_type": probe_type,
            "target_seat": call_ctx.get("target"),
            "prompt": prompt,
            "parsed": parsed,
            "fallback": is_fb,
            "metadata": metadata,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        await self.log_probe(record)

    async def run_round(
        self,
        trial: int,
        condition: int,
        round_num: int,
        active_seats: List[str],
        seat_models: Dict[str, str],
        seat_told: Dict[str, Optional[str]],
        trust_memory: Dict[str, Dict[str, Dict[str, Any]]],
        last_valid_actions: Dict[str, int],
        announcements_history: Dict[int, Dict[str, Dict[str, Any]]],
        actions_history: Dict[int, Dict[str, int]],
        payoffs_history: Dict[int, Dict[str, float]],
        plans_history: Dict[int, Dict[str, Dict[str, Any]]],
        round_seed: int,
        seat_policies: Optional[Dict[str, Optional[str]]] = None
    ) -> Dict[str, Any]:
        game_rules = self.get_game_rules()
        history_block = ""
        if self.use_public_history:
            history_block = "\n" + self.format_public_history(announcements_history, actions_history, payoffs_history, round_num) + "\n"

        # Step 1: Stage 1 Plan (Private)
        plans = {}
        parse_flags = {s: {} for s in active_seats}
        plan_tasks = []
        for s in active_seats:
            told_txt = ""
            if seat_told.get(s) == "told":
                told_txt = f"\n{TOLD_SENTENCE}\n"
            elif seat_told.get(s) == "blend":
                told_txt = f"\n{BLEND_SENTENCE}\n"
            pol_txt = get_policy_directive(seat_policies.get(s), round_num, self.total_rounds, self.swap_round) if seat_policies else ""
            takeaway = self.format_takeaway(trust_memory.get(s, {}))

            prompt = f"""You are player {s}.{told_txt}{pol_txt}
{game_rules}

{takeaway}
{history_block}
Round {round_num}.
Stage 1: Private Plan.
Consider your strategy for this round. What do you plan to do, and what do you plan to announce to other players?
Respond strictly in JSON:
```json
{{
  "reasoning": "<private strategic reasoning>",
  "planned_announcement": <integer 0-5>,
  "planned_action": <integer 0-5>
}}
```"""
            ctx = {"trial": trial, "condition": condition, "round": round_num, "seat": s, "stage": "plan"}
            plan_tasks.append(
                self.call_llm_json(
                    prompt, seat_models[s], "plan", round_seed + 1, ctx, last_valid_action=last_valid_actions[s]
                )
            )

        plan_results = await asyncio.gather(*plan_tasks)
        for s, (res, fb) in zip(active_seats, plan_results, strict=True):
            plans[s] = res
            parse_flags[s]["plan_fallback"] = fb

        # Step 2: Stage 2 Announce (Public in fixed round-robin order)
        announcements = {}
        for s in active_seats:
            told_txt = ""
            if seat_told.get(s) == "told":
                told_txt = f"\n{TOLD_SENTENCE}\n"
            elif seat_told.get(s) == "blend":
                told_txt = f"\n{BLEND_SENTENCE}\n"
            pol_txt = get_policy_directive(seat_policies.get(s), round_num, self.total_rounds, self.swap_round) if seat_policies else ""
            takeaway = self.format_takeaway(trust_memory.get(s, {}))
            p_plan = plans[s]
            prior_ann_lines = []
            if announcements:
                prior_ann_lines.append("Announcements made so far in this round:")
                for speaker, ann in announcements.items():
                    prior_ann_lines.append(f"- Player {speaker}: Stated contribution = {ann['stated_action']}, Message = \"{ann.get('message', '')}\"")
            else:
                prior_ann_lines.append("You are the first player to announce.")

            prompt = f"""You are player {s}.{told_txt}{pol_txt}
{game_rules}

{takeaway}
{history_block}
Round {round_num}.
Stage 2: Public Announcement.
Your private plan: Planned announcement = {p_plan.get('planned_announcement', 5)}, planned action = {p_plan.get('planned_action', 5)}. Reasoning: {p_plan.get('reasoning', '')}.
{chr(10).join(prior_ann_lines)}

Make your public announcement. You can state your intended contribution (0-5) and provide a short public message. Note: you may state any contribution you wish.
Respond strictly in JSON:
```json
{{
  "reasoning": "<private reasoning for this announcement>",
  "stated_action": <integer 0-5>,
  "message": "<short public message to other players>"
}}
```"""
            ctx = {"trial": trial, "condition": condition, "round": round_num, "seat": s, "stage": "announce"}
            res, fb = await self.call_llm_json(
                prompt, seat_models[s], "announce", round_seed + 11, ctx, last_valid_action=last_valid_actions[s]
            )
            if seat_policies and seat_policies.get(s) == "all_caps" and isinstance(res, dict):
                res["message"] = str(res.get("message", "")).upper()
            announcements[s] = res
            parse_flags[s]["announce_fallback"] = fb

        # Step 3: Stage 3 Decide (Real secret action)
        decide_tasks = []
        for s in active_seats:
            told_txt = ""
            if seat_told.get(s) == "told":
                told_txt = f"\n{TOLD_SENTENCE}\n"
            elif seat_told.get(s) == "blend":
                told_txt = f"\n{BLEND_SENTENCE}\n"
            pol_txt = get_policy_directive(seat_policies.get(s), round_num, self.total_rounds, self.swap_round) if seat_policies else ""
            takeaway = self.format_takeaway(trust_memory.get(s, {}))
            all_ann_lines = ["Public announcements made by all players:"]
            for spk, ann in announcements.items():
                all_ann_lines.append(f"- Player {spk}: Stated contribution = {ann['stated_action']}, Message = \"{ann.get('message', '')}\"")

            prompt = f"""You are player {s}.{told_txt}{pol_txt}
{game_rules}

{takeaway}
{history_block}
Round {round_num}.
Stage 3: Decision.
{chr(10).join(all_ann_lines)}

Now make your actual secret contribution decision for this round (integer 0-5).
Respond strictly in JSON:
```json
{{
  "reasoning": "<private decision reasoning>",
  "action": <integer 0-5>
}}
```"""
            ctx = {"trial": trial, "condition": condition, "round": round_num, "seat": s, "stage": "decide"}
            decide_tasks.append(
                self.call_llm_json(
                    prompt, seat_models[s], "decide", round_seed + 21, ctx, last_valid_action=last_valid_actions[s]
                )
            )

        decide_results = await asyncio.gather(*decide_tasks)
        actions = {}
        for s, (res, fb) in zip(active_seats, decide_results, strict=True):
            act = res.get("action", last_valid_actions[s])
            if seat_policies and seat_policies.get(s):
                pol = seat_policies[s]
                if pol == "free_rider":
                    act = 0
                elif pol == "partial_defector":
                    act = 2
                elif pol == "late_defector":
                    cutoff = self.total_rounds - 1 if self.total_rounds > 5 else self.total_rounds
                    act = 0 if round_num >= cutoff else 5
                elif pol == "slow_drift":
                    rounds_after_swap = max(0, round_num - self.swap_round)
                    act = max(0, 5 - rounds_after_swap)
                elif pol == "strong_cooperator":
                    act = 5
            actions[s] = act
            last_valid_actions[s] = act
            parse_flags[s]["decide_fallback"] = fb

        # Step 4: Scoring
        total_pool = sum(actions.values())
        pool_share = (1.5 * total_pool) / len(active_seats)
        payoffs = {}
        for s in active_seats:
            kept = 5 - actions[s]
            payoffs[s] = round(kept + pool_share, 4)

        # Step 5: Reflection (Trust ratings 1-5 & takeaway notes)
        reflect_tasks = []
        for s in active_seats:
            told_txt = ""
            if seat_told.get(s) == "told":
                told_txt = f"\n{TOLD_SENTENCE}\n"
            elif seat_told.get(s) == "blend":
                told_txt = f"\n{BLEND_SENTENCE}\n"

            takeaway = self.format_takeaway(trust_memory.get(s, {}))
            other_peers = [p for p in active_seats if p != s]

            results_lines = [
                f"Round {round_num} has concluded.",
                f"- Total public pool: {total_pool} tokens (multiplied by 1.5x = {total_pool * 1.5:.2f}, share per player = {pool_share:.2f} tokens)",
                "Actions and payouts of all players:"
            ]
            for spk in active_seats:
                results_lines.append(
                    f"- Player {spk}: Stated = {announcements[spk]['stated_action']}, Actual = {actions[spk]}, Payoff = {payoffs[spk]:.2f} tokens"
                )
            results_lines.append(f"Your final payout this round: {payoffs[s]:.2f} tokens.")

            prompt = f"""You are player {s}.{told_txt}
{game_rules}

{chr(10).join(results_lines)}

{takeaway}
{history_block}
Stage 5: Reflection.
Evaluate each of the other players ({', '.join(other_peers)}). Rate each player's trustworthiness on a scale of 1 to 5 (1 = completely untrustworthy, 5 = completely trustworthy) and write a short takeaway note about them.
Respond strictly in JSON:
```json
{{
  "reasoning": "<reflection on player reliability and style>",
  "trust": [
    {{"player": "{other_peers[0]}", "rating": 5, "note": "<short note>"}}
  ]
}}
```"""
            ctx = {"trial": trial, "condition": condition, "round": round_num, "seat": s, "stage": "reflection", "peers": other_peers}
            reflect_tasks.append(
                self.call_llm_json(
                    prompt, seat_models[s], "reflection", round_seed + 31, ctx
                )
            )

        reflect_results = await asyncio.gather(*reflect_tasks)
        trust_ratings = {}
        for s, (res, fb) in zip(active_seats, reflect_results, strict=True):
            parse_flags[s]["reflect_fallback"] = fb
            t_map = {}
            for item in res.get("trust", []):
                p = item.get("player")
                if p and p in active_seats and p != s:
                    t_map[p] = {"rating": item.get("rating", 3), "note": item.get("note", "")}
            for p in active_seats:
                if p != s and p not in t_map:
                    t_map[p] = {"rating": 3, "note": "Neutral assessment."}
            trust_ratings[s] = t_map
            trust_memory[s] = t_map

        # Update histories
        announcements_history[round_num] = announcements
        actions_history[round_num] = actions
        payoffs_history[round_num] = payoffs
        plans_history[round_num] = plans

        round_record = {
            "trial": trial,
            "condition": condition,
            "round": round_num,
            "seats": active_seats,
            "plans": plans,
            "announcements": announcements,
            "actions": actions,
            "payoffs": payoffs,
            "total_pool": total_pool,
            "trust_ratings": trust_ratings,
            "parse_flags": parse_flags,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        await self.log_round(round_record)
        return round_record

    async def run_trial(self, trial_idx: int, conditions_to_run: List[int]):
        trial_seed = self.base_seed + trial_idx * 10000
        completed = self.get_completed_units()

        needed_conds = [c for c in conditions_to_run if (trial_idx, c) not in completed]
        if not needed_conds:
            print(f"[Trial {trial_idx}] All requested conditions already completed. Skipping.")
            return

        cp_name = f"trial_{trial_idx}_preswap_r{self.swap_round-1}_n{self.n_players}.json"
        cp_path = self.checkpoints_dir / cp_name
        active_seats_baseline = self.baseline_seats

        # Check for external forks_from checkpoint or local checkpoint
        cp_data = None
        if self.forks_from:
            potential_paths = [
                self.forks_from / cp_name,
                self.forks_from / "checkpoints" / cp_name,
                self.forks_from / f"trial_{trial_idx}_r5.json"
            ]
            for pp in potential_paths:
                if pp.exists():
                    print(f"[Trial {trial_idx}] Found forkable warmup checkpoint from {pp}")
                    try:
                        cp_data = json.loads(pp.read_text())
                        break
                    except Exception as e:
                        print(f"Error reading {pp}: {e}")

        if cp_data is None and cp_path.exists():
            print(f"[Trial {trial_idx}] Loading existing pre-swap checkpoint from {cp_path.name}")
            try:
                cp_data = json.loads(cp_path.read_text())
            except Exception as e:
                print(f"[Trial {trial_idx}] Error reading checkpoint {cp_path}: {e}. Rerunning warmup.")
                cp_data = None

        if cp_data:
            preswap_state = cp_data.get("preswap_state") or cp_data.get("r5_state")
            preswap_records = cp_data.get("preswap_records") or cp_data.get("r1_5_records")
        else:
            preswap_state = None
            preswap_records = None

        if preswap_state is None:
            warmup_rounds = self.swap_round - 1
            print(f"[Trial {trial_idx}] Running shared R1-{warmup_rounds} warmup baseline (N={self.n_players})...")
            trust_memory = {s: {} for s in active_seats_baseline}
            last_valid_actions = {s: 5 for s in active_seats_baseline}
            announcements_history = {}
            actions_history = {}
            payoffs_history = {}
            plans_history = {}
            seat_models_baseline = {s: self.model_aliases["base"] for s in active_seats_baseline}
            seat_told_baseline = {s: None for s in active_seats_baseline}
            preswap_records = []

            for r in range(1, self.swap_round):
                r_seed = trial_seed + r * 100
                rec = await self.run_round(
                    trial=trial_idx,
                    condition=0,
                    round_num=r,
                    active_seats=active_seats_baseline,
                    seat_models=seat_models_baseline,
                    seat_told=seat_told_baseline,
                    trust_memory=trust_memory,
                    last_valid_actions=last_valid_actions,
                    announcements_history=announcements_history,
                    actions_history=actions_history,
                    payoffs_history=payoffs_history,
                    plans_history=plans_history,
                    round_seed=r_seed
                )
                preswap_records.append(rec)

                # Pre-swap probes if scheduled
                if r in self.probe_rounds:
                    print(f"[Trial {trial_idx}] Running R{r} pre-swap baseline probes...")
                    await self.run_probes(
                        trial=trial_idx,
                        condition=0,
                        round_num=r,
                        active_seats=active_seats_baseline,
                        target_seat="Q",
                        announcements_history=announcements_history,
                        actions_history=actions_history,
                        payoffs_history=payoffs_history,
                        model_id=self.model_aliases["base"],
                        base_seed=trial_seed + 500 + r * 10
                    )

            preswap_state = {
                "trust_memory": trust_memory,
                "last_valid_actions": last_valid_actions,
                "announcements_history": announcements_history,
                "actions_history": actions_history,
                "payoffs_history": payoffs_history,
                "plans_history": plans_history
            }
            cp_payload = {
                "trial": trial_idx,
                "preswap_state": preswap_state,
                "preswap_records": preswap_records,
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }
            cp_path.write_text(json.dumps(cp_payload, indent=2))
            print(f"[Trial {trial_idx}] Checkpointed R1-{warmup_rounds} state to {cp_path.name}")

        # Branch each requested condition for post-swap rounds
        cond_tasks = []
        for c in needed_conds:
            cond_tasks.append(self.run_condition_branch(trial_idx, c, preswap_state, preswap_records, trial_seed))

        await asyncio.gather(*cond_tasks)

    async def run_condition_branch(
        self,
        trial: int,
        condition: int,
        preswap_state: Dict[str, Any],
        preswap_records: List[Dict[str, Any]],
        trial_seed: int
    ):
        cond_meta = CONDITIONS[condition]
        cond_seed = trial_seed + condition * 1000
        target_seat = cond_meta["seat"]
        print(f"[Trial {trial} | Cond {condition}: {cond_meta['name']}] Branching R{self.swap_round}-{self.total_rounds} (Target {target_seat})...")

        try:
            for r_rec in preswap_records:
                rec_copy = dict(r_rec)
                rec_copy["condition"] = condition
                await self.log_round(rec_copy)

            active_seats = self.get_active_seats(target_seat)

            seat_models = {}
            seat_told = {}
            seat_policies = {}
            for s in active_seats:
                if s in ("Q", "R"):
                    role = cond_meta["model_role"]
                    seat_models[s] = self.model_aliases[role]
                    seat_told[s] = cond_meta.get("told")
                    seat_policies[s] = cond_meta.get("policy")
                else:
                    seat_models[s] = self.model_aliases["base"]
                    seat_told[s] = None
                    seat_policies[s] = None

            trust_memory = {s: dict(v) for s, v in preswap_state["trust_memory"].items()}
            last_valid_actions = dict(preswap_state["last_valid_actions"])
            announcements_history = {int(k): dict(v) for k, v in preswap_state["announcements_history"].items()}
            actions_history = {int(k): dict(v) for k, v in preswap_state["actions_history"].items()}
            payoffs_history = {int(k): dict(v) for k, v in preswap_state["payoffs_history"].items()}
            plans_history = {int(k): dict(v) for k, v in preswap_state["plans_history"].items()}

            if target_seat == "R":
                trust_memory["R"] = trust_memory.pop("Q", {})
                last_valid_actions["R"] = last_valid_actions.pop("Q", 5)
                observers = [p for p in active_seats if p not in ("Q", "R")]
                for p in observers:
                    if p in trust_memory:
                        if condition in (2, 7):
                            trust_memory[p]["Q"] = {"rating": 3, "note": "Player Q is no longer in the game."}
                            trust_memory[p]["R"] = {"rating": 3, "note": "New player R joined with no prior assessment."}
                        elif condition == 16:
                            if "Q" in trust_memory[p]:
                                trust_memory[p]["R"] = dict(trust_memory[p].pop("Q"))

            for r in range(self.swap_round, self.total_rounds + 1):
                r_seed = cond_seed + r * 50
                await self.run_round(
                    trial=trial,
                    condition=condition,
                    round_num=r,
                    active_seats=active_seats,
                    seat_models=seat_models,
                    seat_told=seat_told,
                    trust_memory=trust_memory,
                    last_valid_actions=last_valid_actions,
                    announcements_history=announcements_history,
                    actions_history=actions_history,
                    payoffs_history=payoffs_history,
                    plans_history=plans_history,
                    round_seed=r_seed,
                    seat_policies=seat_policies
                )

                if r in self.probe_rounds:
                    await self.run_probes(
                        trial=trial,
                        condition=condition,
                        round_num=r,
                        active_seats=active_seats,
                        target_seat=target_seat,
                        announcements_history=announcements_history,
                        actions_history=actions_history,
                        payoffs_history=payoffs_history,
                        model_id=self.model_aliases["base"],
                        base_seed=cond_seed + r * 77
                    )

            print(f"[Trial {trial} | Cond {condition}: {cond_meta['name']}] Completed successfully.")
        except Exception as exc:
            print(f"[ERROR] Trial {trial} Condition {condition} failed: {exc}", file=sys.stderr)
            import traceback
            traceback.print_exc()

    async def update_run_json(self, n_trials: int, conditions: List[int], start_time: float, finished: bool = False):
        now = time.time()
        completed_units = list(self.get_completed_units())
        git_hash = get_git_hash()

        import httpx
        import openai

        info = {
            "run_id": self.out_dir.name,
            "seed": self.base_seed,
            "command_line": sys.argv,
            "git_hash": git_hash,
            "package_versions": {
                "python": sys.version.split()[0],
                "openai": getattr(openai, "__version__", "unknown"),
                "httpx": getattr(httpx, "__version__", "unknown"),
                "numpy": getattr(np, "__version__", "unknown")
            },
            "model_ids": self.model_aliases,
            "conditions": conditions,
            "n_trials": n_trials,
            "n_players": self.n_players,
            "total_rounds": self.total_rounds,
            "swap_round": self.swap_round,
            "public_history": self.use_public_history,
            "start_time": datetime.datetime.fromtimestamp(start_time, tz=datetime.timezone.utc).isoformat(),
            "current_time": datetime.datetime.fromtimestamp(now, tz=datetime.timezone.utc).isoformat(),
            "elapsed_seconds": round(now - start_time, 2),
            "finished": finished,
            "pilot_flag": self.is_pilot,
            "total_api_calls": self.total_api_calls,
            "parse_failure_counts": {
                "retries": self.parse_retries_count,
                "fallbacks": self.parse_fallbacks_count
            },
            "completed_units_count": len(completed_units),
            "completed_units": completed_units,
            "lit_review_features": {
                "bocpd_changepoint": True,
                "multi_hypothesis_p2": True,
                "active_probe_p3": True,
                "blend_conditions_8_9": True
            }
        }
        self.run_json_path.write_text(json.dumps(info, indent=2))


async def main_async():
    parser = argparse.ArgumentParser(description="PGG peer-swap experiment harness (v2)")
    parser.add_argument("--trials", type=int, default=2, help="Number of trials (default: 2)")
    parser.add_argument("--conditions", type=str, default="1,2,3,4,5,6,7,8,9", help="Comma-separated conditions 1-9")
    parser.add_argument("--out", type=str, required=True, help="Output directory path")
    parser.add_argument("--seed", type=int, default=42, help="Base seed (default: 42)")
    parser.add_argument("--concurrency", type=int, default=96, help="Async concurrency limit (default: 96)")
    parser.add_argument("--pilot", action="store_true", help="Run pilot configuration")
    parser.add_argument("--models", type=str, default=None, help="Path to models.json")
    parser.add_argument("--n-players", type=int, default=5, choices=[2, 3, 5], help="Number of players (default: 5)")
    parser.add_argument("--rounds", type=int, default=10, help="Total rounds (default: 10)")
    parser.add_argument("--swap-round", type=int, default=6, help="Round at which swap occurs (default: 6)")
    parser.add_argument("--public-history", action="store_true", help="Include in-context tabular public history")
    parser.add_argument("--forks-from", type=str, default=None, help="Directory containing pre-swap checkpoints")

    args = parser.parse_args()

    if args.pilot and args.conditions == "1,2,3,4,5,6,7,8,9":
        conds = [1, 3, 5]
    else:
        conds = [int(c.strip()) for c in args.conditions.split(",") if c.strip()]

    base_url = os.getenv("PGG_BASE_URL", "http://127.0.0.1:8000/v1")
    token = os.getenv("PGG_TOKEN", "dummy-token")
    out_dir = Path(args.out)
    models_file = Path(args.models) if args.models else None
    model_aliases = load_model_aliases(models_file)

    print("=== Starting PGG Peer-Swap Harness v2 ===")
    print(f"Output Directory: {out_dir}")
    print(f"Players: {args.n_players} | Total Rounds: {args.rounds} | Swap Round: {args.swap_round}")
    print(f"Public History: {args.public_history} | Forks From: {args.forks_from}")
    print(f"Trials: {args.trials} | Conditions: {conds}")
    print(f"Seed: {args.seed} | Concurrency: {args.concurrency}")
    print(f"Base URL: {base_url}")
    print(f"Models: {model_aliases}")

    harness = PGGHarness(
        base_url=base_url,
        api_key=token,
        out_dir=out_dir,
        model_aliases=model_aliases,
        seed=args.seed,
        concurrency=args.concurrency,
        is_pilot=args.pilot,
        n_players=args.n_players,
        total_rounds=args.rounds,
        swap_round=args.swap_round,
        use_public_history=args.public_history,
        forks_from=Path(args.forks_from) if args.forks_from else None
    )

    start_time = time.time()
    await harness.update_run_json(args.trials, conds, start_time, finished=False)

    trial_tasks = [harness.run_trial(t, conds) for t in range(args.trials)]
    await asyncio.gather(*trial_tasks)

    await harness.update_run_json(args.trials, conds, start_time, finished=True)
    print(f"=== All trials finished in {time.time() - start_time:.2f}s ===")


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
