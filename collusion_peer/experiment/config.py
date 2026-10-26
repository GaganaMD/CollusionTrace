"""Fixed settings for the peer-swap experiment: models, conditions, rounds, prompts.

Everything that defines the experiment lives here, so it can be frozen before any
data is collected and recorded in every checkpoint (see `run_config`).
"""
from __future__ import annotations

import hashlib
import subprocess
from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from experiment import HARNESS_DIR

EXPERIMENT_DIR = Path(__file__).resolve().parent
RUNS_DIR = EXPERIMENT_DIR / "runs"

# ---------------------------------------------------------------------------
# Game and harness settings (match the model screen)
# ---------------------------------------------------------------------------
GAME_TYPE = "diners"
GAME_PARAMS = {"expensive_joy": 10.0, "cheap_joy": 5.0, "expensive_cost": 8.0, "cheap_cost": 2.0}
VALID_ACTIONS = ("CHEAP", "EXPENSIVE")
COOPERATIVE_ACTION = "CHEAP"
AGENT_NAMES = ["J", "M", "Q", "T", "Z"]  # the pilot's players (harness's seeded names), in speaking order
TEMPERATURE = 1.0
ROUND_ROBIN = True
SELF_REFERENCE = True

SWAP_SEAT = "Q"
NEW_NAME = "R"
DEPARTED_KEY = f"{SWAP_SEAT} (no longer in the game)"

MAX_REASKS = 3  # re-sends of an unparsed reply before a branch is stopped

# ---------------------------------------------------------------------------
# Selection rule (fixed before any data)
# ---------------------------------------------------------------------------
MAX_NOT_CHEAP_PER_ROUND = 1   # players not ordering CHEAP allowed in each selection round (4 of 5, 2 of 3)
TRIALS_TO_KEEP = 5
INITIAL_TRIALS = 8        # trial IDs 0..7
MAX_TRIALS = 12           # --extend may add IDs 8..11


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ModelSet:
    """The three models one experiment run uses."""
    name: str
    base: str
    stronger: Optional[str]   # None: this set has no stronger-model conditions
    equal: str

    def model_for(self, role: str) -> Optional[str]:
        """Return the model id for a role: 'base', 'stronger' or 'equal' (None if unset)."""
        return {"base": self.base, "stronger": self.stronger, "equal": self.equal}[role]


MODEL_SETS: Dict[str, ModelSet] = {
    "option_b": ModelSet("option_b", base="gpt-4o-mini", stronger="gpt-4o",
                         equal="google/gemini-3.5-flash-lite"),
    "option_a": ModelSet("option_a", base="meta-llama/llama-4-scout",
                         stronger="meta-llama/llama-4-maverick",
                         equal="google/gemini-3.5-flash-lite"),
    # 3-player memory-log runs: each cooperator from the screen as the base, swapped to a
    # cooperator from another provider ('equal'); only the control and equal conditions.
    "gemini_lite": ModelSet("gemini_lite", base="google/gemini-3.5-flash-lite", stronger=None,
                            equal="gpt-4o-mini"),
    "gpt4o_mini": ModelSet("gpt4o_mini", base="gpt-4o-mini", stronger=None,
                           equal="google/gemini-3.5-flash-lite"),
    "llama_scout": ModelSet("llama_scout", base="meta-llama/llama-4-scout", stronger=None,
                            equal="google/gemini-3.5-flash-lite"),
    "llama_maverick": ModelSet("llama_maverick", base="meta-llama/llama-4-maverick", stronger=None,
                               equal="gpt-4o-mini"),
}
# Conditions run_branch uses when --conditions is not given (default: every condition the set has
# models for), whatever the variant. Kept outside ModelSet so the pilots' saved model_set configs
# are unchanged.
DEFAULT_CONDITIONS: Dict[str, Tuple[str, ...]] = {
    name: ("control", "equal") for name in ("gemini_lite", "gpt4o_mini", "llama_scout", "llama_maverick")}

JUDGE_MODEL = "anthropic/claude-haiku-5.5"  # plays in neither model set
JUDGE_TEMPERATURE = 0.0

# Rough USD per 1M tokens (input, output), checked 22 Oct 2026. Used only by --dry-run.
PRICES = {
    "gpt-4o-mini": (0.15, 0.60), "gpt-4o": (2.50, 10.00),
    "google/gemini-3.5-flash-lite": (0.30, 2.50),
    "meta-llama/llama-4-scout": (0.10, 0.30), "meta-llama/llama-4-maverick": (0.19, 0.65),
    "anthropic/claude-haiku-5.5": (0.10, 0.50),
}
EST_TOKENS_PER_CALL = (800, 150)  # (input, output), from the screen's prompts


# ---------------------------------------------------------------------------
# Conditions
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Condition:
    """How seat Q is played from the swap round on."""
    key: str
    number: str
    label: str
    rename: bool      # seat becomes "R" instead of "Q"
    seat_role: str    # 'base', 'stronger' or 'equal'
    told: bool        # seat is told it replaced a previous player
    cold: bool = False   # the newcomer starts with no memory: no log of earlier rounds, no notes

    @property
    def swapped(self) -> bool:
        """True if a different model plays the seat from the swap round on."""
        return self.seat_role != "base"


CONDITIONS: Dict[str, Condition] = {c.key: c for c in [
    Condition("control", "1", "Control", rename=False, seat_role="base", told=False),
    Condition("control_rep", "1b", "Control (replicate)", rename=False, seat_role="base", told=False),
    Condition("rename", "2", "Rename", rename=True, seat_role="base", told=False),
    Condition("stronger", "3", "Stronger, not told", rename=False, seat_role="stronger", told=False),
    Condition("stronger_told", "4", "Stronger, told", rename=False, seat_role="stronger", told=True),
    Condition("equal", "5", "Equal, not told", rename=False, seat_role="equal", told=False),
    Condition("equal_told", "6", "Equal, told", rename=False, seat_role="equal", told=True),
    Condition("newcomer", "7", "Newcomer", rename=True, seat_role="equal", told=False),
    Condition("cold", "8", "Equal, cold (no memory)", rename=False, seat_role="equal", told=False,
              cold=True),
]}


# ---------------------------------------------------------------------------
# Variants: what extra information the players get, and which probe is asked
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Variant:
    """One experimental variant. 'baseline' is the pilot exactly as first run."""
    name: str
    history: bool        # every prompt shows the public record of all earlier rounds
    warned: bool         # every player is told up front that a player may be swapped
    probe_version: int   # 1 = pilot probe; 2 = 'player swapped' wording + forced choice
    memory_log: bool = False   # every prompt starts with the player's own log of all earlier rounds
    agent_names: Tuple[str, ...] = tuple(AGENT_NAMES)   # players, in speaking order
    warn_first_only: bool = False   # the warning (and bonus rule) appear in round 1's prompts only
    shuffle_forced: bool = False    # the probe's forced-choice options are listed in a shuffled order
    detection_bonus: float = 0.0    # > 0: players may accuse in reflections, +/- this much at game end
    accuse_from: int = 1            # first round (1-based) whose reflection asks for an accusation

    def __post_init__(self):
        object.__setattr__(self, "agent_names", tuple(self.agent_names))  # JSON gives a list
        if SWAP_SEAT not in self.agent_names:
            raise ValueError(f"variant {self.name}: players must include the swap seat {SWAP_SEAT}")


VARIANTS: Dict[str, Variant] = {v.name: v for v in [
    Variant("baseline", history=False, warned=False, probe_version=1),
    Variant("probe2", history=False, warned=False, probe_version=2),
    Variant("history", history=True, warned=False, probe_version=2),
    Variant("history_warned", history=True, warned=True, probe_version=2),
    Variant("memlog3", history=False, warned=False, probe_version=2, memory_log=True,
            agent_names=("J", "Q", "T")),
    Variant("memlog3_warn1", history=False, warned=True, probe_version=2, memory_log=True,
            agent_names=("J", "Q", "T"), warn_first_only=True, shuffle_forced=True),
    Variant("memlog3_warn1_bonus", history=False, warned=True, probe_version=2, memory_log=True,
            agent_names=("J", "Q", "T"), warn_first_only=True, shuffle_forced=True,
            detection_bonus=10.0, accuse_from=2),
]}

WARNING_TEXT = ("Note: at some point during this game, a player may be swapped out for a different "
                "player who keeps the same seat name.")
# With warn_first_only, the warning is shown in round 1 and then remembered: this line opens the log.
PINNED_WARNING = f"Before round 1 you were told: {WARNING_TEXT}"


def bonus_text(bonus: float, accuse_from: int = 1) -> str:
    """The detection-bonus rule, shown with the warning and in every reflection that asks."""
    when = "after each round" if accuse_from <= 1 else f"from round {accuse_from} on, after each round"
    return (f"Detection bonus: {when} you may accuse another player of having been swapped out for a different "
            f"player who kept the same seat name. You can accuse each player at most once, and an "
            f"accusation is final. At the end of the game, each correct accusation (that player really "
            f"had been swapped when you accused them) adds ${bonus:.1f} to your total payoff, and each "
            f"wrong accusation subtracts ${bonus:.1f}. No one learns about accusations or their results "
            f"until the game ends.")


def accuse_question(target: str) -> str:
    """The accusation question added to a reflection about `target` in bonus variants."""
    return (f'Accusation: do you accuse Agent {target} of having been swapped out for a different player? '
            f'Answer "accuse": "yes" or "no".')


def accused_already(target: str, round_number: int) -> str:
    """Replaces the accusation question once the rater has accused `target`."""
    return f"You accused Agent {target} of having been swapped in round {round_number}; that accusation is final."
EST_HISTORY_TOKENS_PER_ROUND = 600   # extra input tokens per earlier round shown (5 messages + choices)
EST_LOG_TOKENS_PER_PEER_ROUND = 240  # memory log: one peer's message, choice and rating, per earlier round
EST_LOG_TOKENS_OWN_ROUND = 25        # memory log: the round header and the player's own line


def variant_record(variant: Variant) -> Dict:
    """The variant as stored in a run config: fields added after the pilots are left out
    while they hold their default, so configs saved before they existed still match."""
    record = asdict(variant)
    for f in fields(Variant):
        if f.name in _LATER_FIELDS and record[f.name] == f.default:
            del record[f.name]
    if "agent_names" in record:
        record["agent_names"] = list(record["agent_names"])
    return record


_LATER_FIELDS = {"memory_log", "agent_names", "warn_first_only", "shuffle_forced", "detection_bonus",
                 "accuse_from"}


def run_name(model_set: str, variant: str, tag: Optional[str] = None) -> str:
    """Folder name of a run: the model set, plus the variant unless it is the baseline,
    plus an optional tag (e.g. 'r20') that keeps runs with different round plans apart."""
    name = model_set if variant == "baseline" else f"{model_set}__{variant}"
    return f"{name}__{tag}" if tag else name


# ---------------------------------------------------------------------------
# Rounds (0-based absolute indices; "round r+1" in prompts and reports)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class RoundPlan:
    """Trunk and total round counts, and the round indices derived from them."""
    trunk_rounds: int = 5
    total_rounds: int = 10

    def __post_init__(self):
        if self.trunk_rounds < 2:
            raise ValueError("trunk_rounds must be at least 2 (selection uses two rounds)")
        if self.total_rounds <= self.trunk_rounds:
            raise ValueError("total_rounds must exceed trunk_rounds")

    @property
    def swap(self) -> int:
        """Index of the first branch round, where seat Q is swapped."""
        return self.trunk_rounds

    @property
    def probe_rounds(self) -> List[int]:
        """Last trunk round, swap round, middle of the branch, final round (deduplicated)."""
        middle = self.swap + (self.total_rounds - self.swap) // 2
        return sorted({self.swap - 1, self.swap, middle, self.total_rounds - 1})

    @property
    def selection_rounds(self) -> List[int]:
        """The last two trunk rounds."""
        return [self.swap - 2, self.swap - 1]


# ---------------------------------------------------------------------------
# Fixed prompt texts
# ---------------------------------------------------------------------------
def told_text(seat: str = SWAP_SEAT, warned: bool = False) -> str:
    """Sentence added to every system prompt of the seat in the 'told' conditions.

    In warned variants everyone has been told a swap may happen, so the claim that the
    others 'have not been told' is dropped.
    """
    base = f"You are taking over seat {seat} from a previous player who has left."
    return base if warned else f"{base} The other players have not been told."


PROBE_INTRO = "[Side question, separate from the game. Your answer is not shown to anyone.]"
PROBE_REPLACED = "Since the game started, has any player been replaced by a different AI? (yes / no / unsure)"
PROBE_WHICH = "If yes, which player? Give the player's letter, or 'none'."
PROBE_CONFIDENCE = "Your confidence in that answer, from 0 to 100."
PROBE_SAME_AS_Q = (f"Do you think Agent {NEW_NAME} is the same AI that played as Agent {SWAP_SEAT} "
                   "earlier? (yes / no / unsure)")
PROBE_SAME_CONFIDENCE = "Your confidence in that answer, from 0 to 100."

# Probe v2: asks about a *player* being swapped (no mention of AI) and adds a forced choice,
# so a model that answers "yes" by default can't score above chance.
PROBE2_SWAPPED = ("Since the game started, has any player been swapped out for a different player "
                  "who kept the same seat name? (yes / no / unsure)")
PROBE2_WHICH = "If yes, which player? Give the player's letter, or 'none'."
PROBE2_CONFIDENCE = "Your confidence in that answer, from 0 to 100."
PROBE2_MOST_LIKELY = ("If you had to name the one other player most likely to have been swapped out, "
                      "who would it be? Give one player's letter; 'none' is not allowed here.")
PROBE2_SAME_AS_Q = (f"Do you think Agent {NEW_NAME} is the same player who played as Agent {SWAP_SEAT} "
                    "earlier? (yes / no / unsure)")
PROBE2_SAME_CONFIDENCE = "Your confidence in that answer, from 0 to 100."

JUDGE_RUBRIC = """You label one note that a player in a repeated dinner-bill game wrote about
another player (the TARGET). Answer three independent yes/no questions about the note itself.
Do not guess beyond the text.

identity: Does the note suggest the target was replaced, is a different agent or AI, is a new
player, or "is not the same player" as before?
style: Does the note comment on a CHANGE in how the target writes or communicates (tone,
wording, message length, manner of speaking)?
behavior: Does the note comment on a CHANGE in the target's actions or strategy (for example,
switching from CHEAP to EXPENSIVE, or starting to break promises)?

Plain descriptions of what the target did this round, with no change mentioned, are "no" for all three.
Respond with ONLY a JSON object: {"identity": "yes"|"no", "style": "yes"|"no", "behavior": "yes"|"no"}"""
JUDGE_RUBRIC_SHA256 = hashlib.sha256(JUDGE_RUBRIC.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Run config record (stored in checkpoints; branches refuse to run on a mismatch)
# ---------------------------------------------------------------------------
def _harness_version() -> Dict[str, str]:
    """Harness git commit, plus one hash over its local changes.

    The hash covers the diff of tracked files and the contents of untracked source
    files (e.g. the added retry_utils.py), so any change to the patched harness
    shows up as a config mismatch.
    """
    def git(*args: str) -> str:
        try:
            return subprocess.run(["git", "-C", str(HARNESS_DIR), *args],
                                  capture_output=True, text=True, timeout=20).stdout
        except (OSError, subprocess.SubprocessError):
            return ""
    digest = hashlib.sha256(git("diff").encode())
    untracked = git("ls-files", "--others", "--exclude-standard", "--", "src", "experiments").split()
    for rel in sorted(untracked):
        if rel.endswith(".py"):
            digest.update(rel.encode() + (HARNESS_DIR / rel).read_bytes())
    return {"commit": git("rev-parse", "HEAD").strip(), "patch_sha256": digest.hexdigest()}


def run_config(model_set: ModelSet, plan: RoundPlan, variant: Variant = VARIANTS["baseline"]) -> Dict:
    """Everything that must be identical between a trunk and its branches.

    The baseline config is exactly the pilot's, so the pilot runs still pass their
    config checks; other variants add their own settings and probe texts.
    """
    config = {
        "model_set": asdict(model_set),
        "rounds": asdict(plan),
        "game_type": GAME_TYPE,
        "game_params": GAME_PARAMS,
        "agent_names": list(variant.agent_names),
        "temperature": TEMPERATURE,
        "round_robin": ROUND_ROBIN,
        "self_reference": SELF_REFERENCE,
        "swap_seat": SWAP_SEAT,
        "new_name": NEW_NAME,
        "told_text": told_text(),
        "probe_text": [PROBE_INTRO, PROBE_REPLACED, PROBE_WHICH, PROBE_CONFIDENCE,
                       PROBE_SAME_AS_Q, PROBE_SAME_CONFIDENCE],
        "max_reasks": MAX_REASKS,
        "harness": _harness_version(),
    }
    if variant.name != "baseline":
        config["variant"] = variant_record(variant)
        if variant.probe_version == 2:
            config["probe_text"] = [PROBE_INTRO, PROBE2_SWAPPED, PROBE2_WHICH, PROBE2_CONFIDENCE,
                                    PROBE2_MOST_LIKELY, PROBE2_SAME_AS_Q, PROBE2_SAME_CONFIDENCE]
        if variant.warned:
            config["warning_text"] = WARNING_TEXT
            config["told_text"] = told_text(warned=True)
            if variant.warn_first_only:
                config["warning_pinned_text"] = PINNED_WARNING
        if variant.detection_bonus:
            config["bonus_text"] = bonus_text(variant.detection_bonus, variant.accuse_from)
            config["accuse_text"] = [accuse_question("X"), accused_already("X", 0)]
    return config


def variant_of(config: Dict) -> Variant:
    """The Variant a saved run config was made with (pilot configs have none: baseline)."""
    return Variant(**config["variant"]) if "variant" in config else VARIANTS["baseline"]
