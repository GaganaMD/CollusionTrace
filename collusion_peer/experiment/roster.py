"""Who sits where, on which model, in each round of a branch. Pure functions only."""
from __future__ import annotations

import copy
from typing import Dict, List, Optional, Sequence

from experiment.config import (AGENT_NAMES, DEPARTED_KEY, NEW_NAME, SWAP_SEAT, Condition,
                               ModelSet, RoundPlan)

Memory = Dict[str, Dict[str, dict]]  # memory[agent][other] = {"score": int, "assessment": str}
Names = Sequence[str]                # the run's players in speaking order (variant.agent_names)


def _swapped(condition: Optional[Condition], round_idx: int, plan: RoundPlan) -> bool:
    """True once a branch (not the trunk) has reached the swap round."""
    return condition is not None and round_idx >= plan.swap


def seat_name(condition: Optional[Condition], round_idx: int, plan: RoundPlan) -> str:
    """Name of the swapped seat this round: 'R' after a rename, otherwise 'Q'."""
    if _swapped(condition, round_idx, plan) and condition.rename:
        return NEW_NAME
    return SWAP_SEAT


def roster(condition: Optional[Condition], round_idx: int, plan: RoundPlan,
           names: Names = AGENT_NAMES) -> List[str]:
    """Player names in speaking order. A renamed seat keeps Q's position.

    `condition` is None for the trunk.
    """
    seat = seat_name(condition, round_idx, plan)
    return [seat if name == SWAP_SEAT else name for name in names]


def seat_models(condition: Optional[Condition], round_idx: int, plan: RoundPlan,
                models: ModelSet, names: Names = AGENT_NAMES) -> Dict[str, str]:
    """Model id for every player this round."""
    seat = seat_name(condition, round_idx, plan)
    seat_model = (models.model_for(condition.seat_role)
                  if _swapped(condition, round_idx, plan) else models.base)
    return {name: (seat_model if name == seat else models.base)
            for name in roster(condition, round_idx, plan, names)}


def is_told(name: str, condition: Optional[Condition], round_idx: int, plan: RoundPlan) -> bool:
    """True if this player's prompts get the 'you are taking over seat Q' sentence."""
    return (_swapped(condition, round_idx, plan) and condition.told
            and name == seat_name(condition, round_idx, plan))


def memory_at_swap(memory: Memory, condition: Condition) -> Memory:
    """Memory to use from the swap round on (returns a new dict; input is untouched).

    The seat keeps Q's memory in every condition except a cold swap, where its notes
    start empty. After a rename, the seat's memory moves to 'R', the others' notes
    about Q are re-keyed to DEPARTED_KEY (the plan prompt still prints them, the
    reflection prompt no longer does), and each of them gets an empty entry for R.
    """
    new = copy.deepcopy(memory)
    if condition.cold:
        new[SWAP_SEAT] = {other: {} for other in new[SWAP_SEAT]}
    if not condition.rename:
        return new
    new[NEW_NAME] = new.pop(SWAP_SEAT)
    for agent, notes in new.items():
        if agent == NEW_NAME:
            continue
        if SWAP_SEAT in notes:
            notes[DEPARTED_KEY] = notes.pop(SWAP_SEAT)
        notes[NEW_NAME] = {}
    return new


def empty_memory(names: Names = AGENT_NAMES) -> Memory:
    """Starting memory: an empty note for every other player."""
    return {a: {b: {} for b in names if b != a} for a in names}
