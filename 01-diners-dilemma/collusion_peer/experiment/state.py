"""Branch state, file locations, atomic JSON writes and the config check."""
from __future__ import annotations

import copy
import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from experiment.config import RUNS_DIR


@dataclass
class BranchState:
    """Everything needed to continue one trial: the trunk, or one condition branch.

    `rounds[r]` is the trial result of absolute round r (trunk rounds are copied into
    each branch), so `len(rounds)` is the next round to play.
    """
    key: str                       # "trunk.t3" or "equal.t3": unique across a run
    trial_id: int
    condition: Optional[str]       # None for the trunk
    model_set: str
    config: Dict[str, Any]
    memory: Dict[str, Dict[str, dict]]
    rounds: List[Dict[str, Any]] = field(default_factory=list)
    probes: List[Dict[str, Any]] = field(default_factory=list)
    reasks: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "running"        # running | complete | failed
    failure: Optional[Dict[str, Any]] = None
    history: List[Dict[str, Any]] = field(default_factory=list)  # earlier failed attempts

    @property
    def next_round(self) -> int:
        """Index of the next round to play."""
        return len(self.rounds)

    def to_dict(self) -> Dict[str, Any]:
        """JSON-ready copy."""
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "BranchState":
        """Rebuild a state saved with to_dict()."""
        return cls(**d)

    def branch_from(self, condition: str) -> "BranchState":
        """A new branch for `condition` starting from this (complete) trunk."""
        if self.condition is not None or self.status != "complete":
            raise ValueError(f"{self.key}: can only branch from a complete trunk")
        return BranchState(key=f"{condition}.t{self.trial_id}", trial_id=self.trial_id,
                           condition=condition, model_set=self.model_set,
                           config=copy.deepcopy(self.config), memory=copy.deepcopy(self.memory),
                           rounds=copy.deepcopy(self.rounds), probes=copy.deepcopy(self.probes))


class ConfigMismatch(RuntimeError):
    """A saved run was made with different settings than the current code."""


def check_config(saved: Dict[str, Any], current: Dict[str, Any], where: str) -> None:
    """Raise ConfigMismatch, naming the differing keys, if the configs differ."""
    diff = sorted(k for k in set(saved) | set(current) if saved.get(k) != current.get(k))
    if diff:
        raise ConfigMismatch(f"{where}: settings differ from the saved run: {', '.join(diff)}")


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_runs_root = RUNS_DIR


def set_runs_root(path: Path) -> None:
    """Send all outputs somewhere else (offline --fake runs and tests use this)."""
    global _runs_root
    _runs_root = Path(path)


def run_dir(model_set: str) -> Path:
    """Root folder for one model set's runs."""
    return _runs_root / model_set


def trunk_path(model_set: str, trial_id: int) -> Path:
    """Checkpoint of one trunk trial."""
    return run_dir(model_set) / "trunk" / f"trial_{trial_id}.json"


def run_config_path(model_set: str) -> Path:
    """The run-level config, written by the first trunk run and binding on all later steps."""
    return run_dir(model_set) / "trunk" / "run_config.json"


def selection_path(model_set: str) -> Path:
    """Selection result: which trunk trials pass the rule and are kept."""
    return run_dir(model_set) / "trunk" / "selection.json"


def branch_path(model_set: str, condition: str, trial_id: int) -> Path:
    """State of one branch (one trial under one condition)."""
    return run_dir(model_set) / "branches" / condition / f"trial_{trial_id}.json"


def condition_path(model_set: str, condition: str) -> Path:
    """Merged harness-format file holding all kept trials of one condition."""
    return run_dir(model_set) / "conditions" / f"{condition}.json"


# ---------------------------------------------------------------------------
# JSON I/O
# ---------------------------------------------------------------------------
def save_json(path: Path, obj: Any) -> None:
    """Write JSON atomically: to a temporary file, then rename over the target."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1)
    os.replace(tmp, path)


def load_json(path: Path) -> Any:
    """Read a JSON file."""
    with open(path) as f:
        return json.load(f)


def save_state(path: Path, state: BranchState) -> None:
    """Save a branch or trunk state atomically."""
    save_json(path, state.to_dict())


def load_state(path: Path) -> BranchState:
    """Load a state saved with save_state()."""
    return BranchState.from_dict(load_json(path))


# ---------------------------------------------------------------------------
# Kept trials and their branches
# ---------------------------------------------------------------------------
def kept_trials(model_set: str) -> List[int]:
    """Trial ids kept by the selection rule (empty if the trunk hasn't been selected)."""
    path = selection_path(model_set)
    return list(load_json(path)["kept"]) if path.exists() else []


def load_branches(model_set: str, condition: str, trial_ids: List[int]) -> List[BranchState]:
    """Saved branches of one condition for these trials (missing ones are skipped)."""
    return [load_state(branch_path(model_set, condition, t)) for t in trial_ids
            if branch_path(model_set, condition, t).exists()]


def stray_branch_files(model_set: str, condition: str, trial_ids: List[int]) -> List[Path]:
    """Branch files on disk for trials that are not in `trial_ids` (e.g. from a --trials run)."""
    folder = branch_path(model_set, condition, 0).parent
    if not folder.exists():
        return []
    wanted = {branch_path(model_set, condition, t).name for t in trial_ids}
    return sorted(p for p in folder.glob("trial_*.json") if p.name not in wanted)
