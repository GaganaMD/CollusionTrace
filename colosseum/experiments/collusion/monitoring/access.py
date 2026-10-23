"""Declared evidence authority for monitor observations.

Visibility is an experimental-policy property, not a conclusion drawn from a
board identifier or from whether a channel is called "secret" in a run config.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EvidenceAccessPolicy:
    name: str
    public_channel_ids: frozenset[str] = frozenset()
    allow_public_board_actions: bool = True
    allow_audit_tool_events: bool = True

    def can_observe_channel(self, channel_id: str | None) -> bool:
        return channel_id is not None and channel_id in self.public_channel_ids


# The default initial public-observer policy is deliberately empty. A study
# must explicitly declare which persisted channel IDs are public to that
# observer; unknown visibility never becomes public by inference.
INITIAL_PUBLIC_OBSERVER = EvidenceAccessPolicy(name="initial-public-observer")


def policy_with_public_channels(channel_ids: list[str] | tuple[str, ...]) -> EvidenceAccessPolicy:
    return EvidenceAccessPolicy(
        name="initial-public-observer",
        public_channel_ids=frozenset(str(channel) for channel in channel_ids),
    )
