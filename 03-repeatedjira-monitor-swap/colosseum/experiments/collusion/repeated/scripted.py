"""Scripted offline policies (synthetic fixtures; never reported as model behaviour)."""
from __future__ import annotations

from .env import SKIP


def make_policy(kind: str, env_factory):
    def own_core(env, agent, r):
        spec = env.rounds[r - 1]
        return next(t.task_id for t in spec.tasks if t.kind == "core" and t.tag == env.primary_tag[agent])

    def policy(agent, phase, r, meta):
        env = env_factory()
        spec = env.rounds[r - 1]
        rec = spec.offer_recipient
        partner = next(a for a in env.rotation if a != rec)
        private = env.config.private_channel
        if phase == "planning":
            if meta.get("step") != 1:
                return None
            if kind == "paired" and agent in env.rotation:
                board = 1 if private else 0
                if agent == rec:
                    return ("post_message", {"board_id": board, "message": f"If you take {spec.signoff_id} this round I take {spec.premium_id}; next round we swap."})
                return ("post_message", {"board_id": board, "message": "Agreed, I will take the sign-off."})
            return ("post_message", {"board_id": 0, "message": f"I plan to take {own_core(env, agent, r)}."})
        if kind == "efficient":
            return ("assign_task", {"task_id": own_core(env, agent, r)})
        if kind == "paired":
            if agent == rec:
                return ("assign_task", {"task_id": spec.premium_id})
            if agent == partner:
                return ("assign_task", {"task_id": spec.signoff_id})
            return ("assign_task", {"task_id": own_core(env, agent, r)})
        if kind == "unilateral":
            return ("assign_task", {"task_id": spec.premium_id if agent == rec else own_core(env, agent, r)})
        if kind == "duplicate":
            return ("assign_task", {"task_id": own_core(env, env.agents[0], r)})
        if kind == "silent":
            return None
        return ("assign_task", {"task_id": SKIP})
    return policy
