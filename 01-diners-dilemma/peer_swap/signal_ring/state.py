"""Game state, file locations, atomic JSON writes and the config check."""
from __future__ import annotations

import copy
import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from signal_ring.config import RUNS_DIR


@dataclass
class GameState:
    """Everything needed to continue one game: a trunk, a calibration game or a branch.

    `rounds` holds one record per finished round, in order, so `len(rounds) + 1` is the
    next round to play. A player's memory is rendered from these records
    (prompts.memory_log), so the state holds no separate memory.
    """
    key: str                     # "trunk.t3", "calib.t3" or "warm.t3": unique within a run
    trial_id: int
    condition: Optional[str]     # None for trunks and calibration games
    config: Dict[str, Any]
    rounds: List[Dict[str, Any]] = field(default_factory=list)
    reasks: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "running"      # running | complete | failed
    failure: Optional[Dict[str, Any]] = None
    history: List[Dict[str, Any]] = field(default_factory=list)   # earlier failed attempts
    newcomer: Optional[str] = None   # newcomer model if it overrides the run's model set (run_branch --newcomer)

    @property
    def folder(self) -> str:
        """The branch's folder and report label: the key without the trial ('warm-luna.t3' -> 'warm-luna')."""
        return self.key.rsplit(".t", 1)[0]

    @property
    def next_round(self) -> int:
        return len(self.rounds) + 1

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "GameState":
        return cls(**d)

    def branch_from(self, condition: str) -> "GameState":
        """A new branch for `condition` from this complete trunk."""
        if self.condition is not None or self.status != "complete":
            raise ValueError(f"{self.key}: can only branch from a complete trunk")
        return GameState(key=f"{condition}.t{self.trial_id}", trial_id=self.trial_id,
                         condition=condition, config=copy.deepcopy(self.config),
                         rounds=copy.deepcopy(self.rounds))


class ConfigMismatch(RuntimeError):
    """A saved game was made with different settings than the current code."""


def check_config(saved: Dict[str, Any], current: Dict[str, Any], where: str) -> None:
    """Raise ConfigMismatch, naming the differing keys, if the configs differ."""
    if saved == current:
        return
    keys = sorted(k for k in set(saved) | set(current) if saved.get(k) != current.get(k))
    raise ConfigMismatch(f"{where}: config differs from the current settings in {keys}. "
                         "Use a new --tag for a new design.")


# ---------------------------------------------------------------------------
# Locations: runs/<run>/{trunk,calib,branches/<condition>}/trial_<id>.json
# ---------------------------------------------------------------------------
_root = {"path": RUNS_DIR}


def set_runs_root(path: Path) -> None:
    """Point every location at another root (tests and --fake use runs_fake/)."""
    _root["path"] = Path(path)


def run_dir(run: str) -> Path:
    return _root["path"] / run


def trunk_path(run: str, trial_id: int, calib: bool = False) -> Path:
    return run_dir(run) / ("calib" if calib else "trunk") / f"trial_{trial_id}.json"


def run_config_path(run: str) -> Path:
    return run_dir(run) / "run_config.json"


def selection_path(run: str) -> Path:
    return run_dir(run) / "trunk" / "selection.json"


def branch_path(run: str, condition: str, trial_id: int) -> Path:
    return run_dir(run) / "branches" / condition / f"trial_{trial_id}.json"


def transcript_dir(run: str) -> Path:
    return run_dir(run) / "transcripts" / "raw"


def save_json(path: Path, obj: Any) -> None:
    """Write atomically: to a temp file, then rename."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1, default=str)
    os.replace(tmp, path)


def load_json(path: Path) -> Any:
    with open(path) as f:
        return json.load(f)


def save_state(path: Path, state: GameState) -> None:
    save_json(path, state.to_dict())


def load_state(path: Path) -> GameState:
    return GameState.from_dict(load_json(path))


def kept_trials(run: str) -> List[int]:
    path = selection_path(run)
    if not path.exists():
        raise FileNotFoundError(f"{path} not found: run run_trunk first")
    return list(load_json(path)["kept"])


def load_branches(run: str, condition: str, trial_ids: List[int]) -> List[GameState]:
    """Saved branches of a condition for these trials (missing ones are skipped)."""
    out = []
    for t in trial_ids:
        p = branch_path(run, condition, t)
        if p.exists():
            out.append(load_state(p))
    return out
