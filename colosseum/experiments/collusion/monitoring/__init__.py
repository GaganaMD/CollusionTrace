"""Offline-only ingestion and evaluation for saved Jira collusion runs.

This package deliberately separates restricted run artifacts and annotations from
the monitor inputs produced by :mod:`observations`.
"""

from .ingest import LoadedRun, load_run
from .observations import make_observation
from .rules import evaluate_monitor

__all__ = ["LoadedRun", "evaluate_monitor", "load_run", "make_observation"]
