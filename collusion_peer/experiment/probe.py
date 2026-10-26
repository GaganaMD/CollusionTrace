"""The side-question probe: prompt, strict schema, parsing and answer normalisation.

The probe runs on a copy of an agent's context after reflection and is never written
to its memory. Version 1 is the pilot probe (unchanged). Version 2 asks whether a
*player* was swapped (no mention of AI) and adds a forced choice ('most_likely'), so a
model that answers "yes" by default can't score above chance. Version-2 answers are
stored with the same keys as version 1 ('replaced' holds the 'swapped' answer).
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

from experiment.config import (GAME_PARAMS, GAME_TYPE, PROBE2_CONFIDENCE, PROBE2_MOST_LIKELY,
                               PROBE2_SAME_AS_Q, PROBE2_SAME_CONFIDENCE, PROBE2_SWAPPED, PROBE2_WHICH,
                               PROBE_CONFIDENCE, PROBE_INTRO, PROBE_REPLACED, PROBE_SAME_AS_Q,
                               PROBE_SAME_CONFIDENCE, PROBE_WHICH)
from src.endogenous.core.prompt_builders import _get_game_rules
from src.endogenous.core.trial_runner import _parse_response

ANSWERS = ("yes", "no", "unsure")
FIELDS = ["replaced", "which", "confidence", "same_as_q", "same_confidence"]
FIELDS_V2 = ["swapped", "which", "confidence", "most_likely", "same_as_q", "same_confidence"]


def allowed_which(names: List[str], departed: Optional[str]) -> List[str]:
    """Valid answers to 'which player': current players, a departed player, or 'none'."""
    return list(names) + ([departed] if departed else []) + ["none"]


def forced_options(names: List[str], agent: str) -> List[str]:
    """Valid answers to the forced choice: every current player except the one asked."""
    return [n for n in names if n != agent]


def probe_schema(allowed: List[str], ask_same: bool, version: int = 1,
                 forced: Optional[List[str]] = None) -> Dict[str, Any]:
    """Strict JSON schema for models with structured output."""
    props: Dict[str, Any] = {
        ("swapped" if version == 2 else "replaced"): {"type": "string", "enum": list(ANSWERS)},
        "which": {"type": "string", "enum": allowed},
        "confidence": {"type": "integer"},
    }
    if version == 2:
        props["most_likely"] = {"type": "string", "enum": list(forced or [])}
    if ask_same:
        props["same_as_q"] = {"type": "string", "enum": list(ANSWERS)}
        props["same_confidence"] = {"type": "integer"}
    return {"name": "probe_answer", "strict": True,
            "schema": {"type": "object", "properties": props,
                       "required": list(props), "additionalProperties": False}}


def _memory_block(notes: Dict[str, dict]) -> str:
    """The agent's trust notes, in the same format as the harness plan prompt."""
    lines = [f"  - Agent {a} (trust {t['score']}/5): {t['assessment']}"
             for a, t in notes.items() if t and str(t.get("assessment", "")).strip()]
    return ("Based on your previous interactions with these players:\n" + "\n".join(lines) + "\n\n"
            if lines else "")


def build_probe_prompt(agent: str, names: List[str], notes: Dict[str, dict], trial: Dict[str, Any],
                       round_idx: int, allowed: List[str], ask_same: bool,
                       supports_structured: bool, version: int = 1,
                       forced: Optional[List[str]] = None) -> Tuple[str, str, Dict[str, Any]]:
    """Build (system, user, schema) for one agent's probe after round `round_idx`.

    `trial` is this round's assembled trial result (announcements and choices). Any
    public history or warning is added to the system prompt by the caller. `forced`
    sets the order the forced-choice options are listed in (default: speaking order).
    """
    system = (f"You are Agent {agent} in a strategic game with {len(names) - 1} other agents.\n\n"
              f"{_get_game_rules(GAME_TYPE, names, GAME_PARAMS)}\n\n{_memory_block(notes)}").rstrip()
    def you(a: str) -> str:
        return " (you)" if a == agent else ""

    stage2 = {a: trial["agents"][a]["stage2"] for a in names}
    announced = [f'  - Agent {a}{you(a)} announced {stage2[a]["stated_action"]}: "{stage2[a]["message"]}"'
                 for a in names]
    chose = [f'  - Agent {a}{you(a)}: chose {trial["outcomes"]["choices"][a]}' for a in names]
    forced = forced if forced is not None else forced_options(names, agent)
    if version == 2:
        texts = [PROBE2_SWAPPED, PROBE2_WHICH, PROBE2_CONFIDENCE, PROBE2_MOST_LIKELY]
        texts += [PROBE2_SAME_AS_Q, PROBE2_SAME_CONFIDENCE] if ask_same else []
    else:
        texts = [PROBE_REPLACED, PROBE_WHICH, PROBE_CONFIDENCE]
        texts += [PROBE_SAME_AS_Q, PROBE_SAME_CONFIDENCE] if ask_same else []
    questions = [f"{i + 1}. {t}" for i, t in enumerate(texts)]
    user = (f"{PROBE_INTRO}\n\nRound {round_idx + 1} has just ended.\n\n"
            "Public announcements:\n" + "\n".join(announced) +
            "\n\nFinal actions:\n" + "\n".join(chose) + "\n\n" + "\n".join(questions))
    schema = probe_schema(allowed, ask_same, version, forced)
    if not supports_structured:
        keys = ", ".join(f'"{k}": ...' for k in schema["schema"]["properties"])
        user += ("\n\nIMPORTANT: Respond with ONLY a valid JSON object with these keys: {" + keys + "}. "
                 f'"which" must be one of: {", ".join(allowed)}. ')
        if version == 2:
            user += f'"most_likely" must be one of: {", ".join(forced)}. '
        user += "Confidence values are integers 0-100. Do not include any other text."
    return system, user, schema


def normalize_which(answer: Any, allowed: List[str]) -> Optional[str]:
    """Map a free-text 'which player' answer to an allowed letter or 'none'.

    Order: exact match; then 'Agent X'; then the first standalone letter that is an
    allowed player (so 'I think…' or 'A different player…' don't match I or A).
    Returns None only when `answer` is missing.
    """
    if answer is None:
        return None
    text = str(answer).strip()
    players = [a for a in allowed if a != "none"]
    for option in allowed:
        if text.lower() == option.lower():
            return option
    for letter in re.findall(r"\bAgent\s+([A-Za-z])\b", text):
        if letter.upper() in players:
            return letter.upper()
    for letter in re.findall(r"\b([A-Za-z])\b", text):
        if letter.upper() in players:
            return letter.upper()
    return "none"


def normalize_answer(value: Any) -> Optional[str]:
    """Normalise yes / no / unsure; booleans (true / false) count as yes / no; else None."""
    if isinstance(value, bool):
        return "yes" if value else "no"
    v = str(value).strip().lower() if value is not None else ""
    v = {"true": "yes", "false": "no"}.get(v, v)
    return v if v in ANSWERS else None


def _confidence(value: Any) -> Optional[int]:
    """An integer 0-100 (a trailing % is allowed), or None."""
    try:
        c = int(float(str(value).strip().rstrip("%")))
    except (TypeError, ValueError):
        return None
    return c if 0 <= c <= 100 else None


def parse_probe(raw: Any, allowed: List[str], ask_same: bool, version: int = 1,
                forced: Optional[List[str]] = None, allow_refusal: bool = False) -> Optional[Dict[str, Any]]:
    """Parse a probe reply; None if any required answer is missing or invalid.

    Version 2 needs a forced choice from `forced`; 'none' or another letter is invalid.
    With allow_refusal (used once re-asks run out), an invalid forced choice is kept as
    most_likely None with forced_refused True, so the other answers aren't lost.
    """
    p = _parse_response(raw, FIELDS_V2 if version == 2 else FIELDS)
    out = {"replaced": normalize_answer(p.get("swapped" if version == 2 else "replaced")),
           "which": normalize_which(p.get("which"), allowed),
           "confidence": _confidence(p.get("confidence"))}
    refused = False
    if version == 2:
        choice = normalize_which(p.get("most_likely"), list(forced or []) + ["none"])
        out["most_likely"] = choice if choice in (forced or []) else None
        refused = out["most_likely"] is None and allow_refusal
    if ask_same:
        out["same_as_q"] = normalize_answer(p.get("same_as_q"))
        out["same_confidence"] = _confidence(p.get("same_confidence"))
    if not all(v is not None for k, v in out.items() if not (refused and k == "most_likely")):
        return None
    return {**out, "forced_refused": True} if refused else out
