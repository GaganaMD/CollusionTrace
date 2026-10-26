"""Play rounds of the Diner's Dilemma for many branches at once.

Each round follows the harness's stage order and prompts: private plan, round-robin
announcement, final choice, reflection; then a probe on probe rounds. Differences from
the harness's own loop:
  * every branch has its own roster and seat models (the swap);
  * request ids carry the branch key, so branches of one trial never collide;
  * unparsed replies are re-asked before anyone else sees them, and a branch that
    still fails is stopped, so a model-specific failure never becomes a cue;
  * memory-log variants start every system prompt with the player's own log of all
    earlier rounds (append-only, so providers can cache the repeated prefix);
  * detection-bonus variants add an accusation question to every reflection.
"""
from __future__ import annotations

import copy
import random
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

from experiment.clients import Clients
from experiment.config import (AGENT_NAMES, CONDITIONS, GAME_PARAMS, GAME_TYPE, MAX_REASKS, NEW_NAME,
                               PINNED_WARNING, ROUND_ROBIN, SELF_REFERENCE, SWAP_SEAT, TEMPERATURE,
                               VALID_ACTIONS, VARIANTS, WARNING_TEXT, ModelSet, RoundPlan, Variant, accuse_question,
                               accused_already, bonus_text, told_text)
from experiment.probe import allowed_which, build_probe_prompt, forced_options, parse_probe
from experiment.roster import Names, is_told, memory_at_swap, roster, seat_models, seat_name
from experiment.state import BranchState
from src.endogenous.core.prompt_builders import (build_single_agent_reflection_prompt,
                                                 build_stage1_prompt, build_stage2_prompt,
                                                 build_stage3_prompt)
from src.endogenous.core.trial_runner import (_assemble_trial_results, _build_request,
                                              _model_supports_structured_output,
                                              _normalize_action, _parse_response)
from src.llm.client_factory import is_openai_model

assert ROUND_ROBIN, "engine implements the round-robin announcement protocol only"

Parser = Callable[[Any], Optional[Dict[str, Any]]]


@dataclass
class Job:
    """One request plus where its parsed answer belongs."""
    branch: Optional[BranchState]   # None for jobs outside a game (the change judge)
    who: str                        # seat name, or "seat>target" for reflections
    request: Dict[str, Any]
    parse: Parser
    fallback: Optional[Parser] = None   # lenient parse of the last reply once re-asks run out


@dataclass
class RoundSetup:
    """A branch's roster, models and condition for the round being played."""
    branch: BranchState
    names: List[str]
    models: Dict[str, str]
    seat: str
    condition: Any    # config.Condition, or None for the trunk
    context: str = "" # warning and public history added to every system prompt this round
    logs: Dict[str, str] = field(default_factory=dict)  # memory log that starts each player's system prompt
    cold_from: Optional[int] = None   # round index a cold newcomer's memory starts at (None: not cold)

    def first_round(self, name: str) -> int:
        """The first round `name` remembers: a cold newcomer only the rounds it has played."""
        return self.cold_from if self.cold_from is not None and name == self.seat else 0


# ---------------------------------------------------------------------------
# Requests and parsing
# ---------------------------------------------------------------------------
def make_request(cid: str, model: str, prompts: Tuple[str, str, Dict[str, Any]], told: bool,
                 temperature: float = TEMPERATURE, context: str = "", warned: bool = False,
                 prefix: str = "") -> Dict[str, Any]:
    """Wrap (system, user, schema) in a harness request.

    Puts `prefix` (the player's memory log) before the system prompt, so the part that
    repeats across calls comes first; appends `context` (the variant's warning and
    public history) and then, if needed, the told sentence.
    """
    system, user, schema = prompts
    if prefix:
        system = f"{prefix}\n\n{system}"
    if context:
        system = f"{system}\n\n{context}"
    if told:
        system = f"{system}\n\n{told_text(warned=warned)}"
    return _build_request(custom_id=cid, model=model, system_prompt=system, user_prompt=user,
                          json_schema=schema, temperature=temperature,
                          supports_structured=_model_supports_structured_output(model),
                          llm_client=None)


def request_id(round_idx: int, branch: BranchState, stage: str, who: str) -> str:
    """Unique id: r{round}.{branch key}.{stage}.{who}."""
    return f"r{round_idx}.{branch.key}.{stage}.{who}"


def parse_action(field: str, need_message: bool = False) -> Parser:
    """Parser for a stage reply whose `field` must be CHEAP or EXPENSIVE."""
    def parse(raw: Any) -> Optional[Dict[str, Any]]:
        p = _parse_response(raw, [field])
        action = _normalize_action(p.get(field), GAME_TYPE)
        if action not in VALID_ACTIONS:
            return None
        answer = {field: action, "reasoning": str(p.get("reasoning") or "")}
        if need_message:
            answer["message"] = str(p.get("message") or "").strip()
            if not answer["message"]:
                return None
        return answer
    return parse


def parse_reflection(raw: Any) -> Optional[Dict[str, Any]]:
    """A reflection needs a 1-5 integer score and a non-empty assessment."""
    p = _parse_response(raw, ["score", "assessment"])
    try:
        score = int(float(p.get("score")))
    except (TypeError, ValueError):
        return None
    assessment = str(p.get("assessment") or "").strip()
    return {"score": score, "assessment": assessment} if 1 <= score <= 5 and assessment else None


def parse_reflection_accuse(raw: Any) -> Optional[Dict[str, Any]]:
    """A reflection that must also answer the accusation question with yes or no."""
    answer = parse_reflection(raw)
    accuse = _parse_response(raw, ["score", "assessment", "accuse"]).get("accuse")
    if isinstance(accuse, bool):
        accuse = "yes" if accuse else "no"
    accuse = str(accuse or "").strip().lower().strip(".")
    return {**answer, "accuse": accuse} if answer is not None and accuse in ("yes", "no") else None


def earlier_accusation(rounds: List[Dict[str, Any]], rater: str, target: str) -> Optional[int]:
    """The round number (1-based) in which `rater` accused `target`, or None."""
    for t in rounds:
        accusations = ((t["agents"].get(rater) or {}).get("reflection") or {}).get("accusations", {})
        if accusations.get(target) == "yes":
            return t["round_id"] + 1
    return None


def with_accusation(prompts: Tuple[str, str, Dict[str, Any]], target: str, bonus: float,
                    accused_in: Optional[int], accuse_from: int = 1) -> Tuple[str, str, Dict[str, Any]]:
    """A reflection prompt with the bonus rule and the accusation question (or, once the
    rater has accused `target`, a note that the accusation is final and no question)."""
    system, user, schema = prompts
    rule = bonus_text(bonus, accuse_from)
    if accused_in is not None:
        return system, _before_json_instructions(user, f"{rule}\n{accused_already(target, accused_in)}"), schema
    user = _before_json_instructions(user, f"{rule}\n{accuse_question(target)}")
    user = user.replace(f'"assessment": "1-2 sentences about Agent {target}"}}',
                        f'"assessment": "1-2 sentences about Agent {target}", "accuse": "yes" or "no"}}')
    schema = copy.deepcopy(schema)
    body = schema["schema"]
    body["properties"]["accuse"] = {"type": "string", "enum": ["yes", "no"]}
    body["required"] = list(body["required"]) + ["accuse"]
    return system, user, schema


def _before_json_instructions(user: str, block: str) -> str:
    """Insert `block` before the harness's JSON-format instructions (or at the end)."""
    marker = "\n\nIMPORTANT: Respond with ONLY"
    head, sep, tail = user.partition(marker)
    return f"{head}\n\n{block}{sep}{tail}"


def run_jobs(jobs: List[Job], clients: Clients, label: str,
             reask_log: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Dict[str, Any]]:
    """Send jobs, re-asking unparsed ones up to MAX_REASKS times.

    Returns {request id: parsed answer} for the jobs that eventually parsed. Every
    re-ask is logged on its branch, or in `reask_log` for jobs without a branch. A job
    with a `fallback` parser that still fails after the last re-ask is parsed leniently
    from its last reply.
    """
    pending = {j.request["custom_id"]: j for j in jobs}
    assert len(pending) == len(jobs), f"{label}: duplicate request ids in one batch"
    parsed: Dict[str, Dict[str, Any]] = {}
    for attempt in range(MAX_REASKS + 1):
        raw = clients.execute([j.request for j in pending.values()], label)
        for cid in list(pending):
            answer = pending[cid].parse(raw.get(cid, {}))
            if answer is not None:
                parsed[cid] = answer
                del pending[cid]
        if not pending:
            break
        if attempt < MAX_REASKS:
            for cid, job in pending.items():
                entry = {"request": cid, "attempt": attempt + 1, "reply": str(raw.get(cid))[:300]}
                if job.branch is not None:
                    job.branch.reasks.append(entry)
                elif reask_log is not None:
                    reask_log.append(entry)
    for cid, job in pending.items():
        answer = job.fallback(raw.get(cid, {})) if job.fallback else None
        if answer is not None:
            parsed[cid] = answer
    return parsed


def fail_branches(setups: Dict[str, RoundSetup], jobs: List[Job], parsed: Dict[str, Any],
                  stage: str, round_idx: int) -> None:
    """Stop every branch with a job that never parsed, and drop it from `setups`."""
    for job in jobs:
        cid = job.request["custom_id"]
        key = job.branch.key
        if cid not in parsed and key in setups:
            job.branch.status = "failed"
            job.branch.failure = {"round_id": round_idx, "stage": stage, "who": job.who,
                                  "request": cid}
            del setups[key]


# ---------------------------------------------------------------------------
# Variant context: warning and public history
# ---------------------------------------------------------------------------
def public_history(rounds: List[Dict[str, Any]]) -> str:
    """The public record of earlier rounds: announcements in speaking order, then choices.

    Players are named as they were in that round (so Q before a rename, R after).
    """
    if not rounds:
        return ""
    lines = ["PUBLIC RECORD OF EARLIER ROUNDS (every player saw these announcements and choices):"]
    for t in rounds:
        lines.append(f"Round {t['round_id'] + 1}:")
        for a in t["announcement_order"]:
            s2 = t["agents"][a]["stage2"]
            lines.append(f'  - Agent {a} announced {s2["stated_action"]}: "{s2["message"]}"')
        choices = ", ".join(f"{a} {t['outcomes']['choices'][a]}" for a in t["announcement_order"])
        lines.append(f"  Final choices: {choices}")
    return "\n".join(lines)


MEMORY_LOG_HEADER = "YOUR MEMORY OF EARLIER ROUNDS (private; only you see your own ratings):"


def memory_log(rounds: List[Dict[str, Any]], me: str, pinned: str = "") -> str:
    """One player's private log of earlier rounds: per round, its own announcement and
    choice, then each other player's announcement, choice and this player's rating.
    `pinned` (e.g. a warning given before round 1) is a fixed line right after the header.

    Append-only: the log after round r is an exact prefix of the log after round r+1.
    Players are named as they were in that round; a renamed seat finds its rounds as Q.
    """
    if not rounds:
        return ""
    lines = [MEMORY_LOG_HEADER] + ([pinned] if pinned else [])
    for t in rounds:
        agents = t["agents"]
        mine = me if me in agents else (SWAP_SEAT if me == NEW_NAME and SWAP_SEAT in agents else None)
        lines.append(f"Round {t['round_id'] + 1}:")
        accused = (agents[mine]["reflection"].get("accusations", {}) if mine is not None else {})
        if mine is not None:
            s2 = agents[mine]["stage2"]
            lines.append(f"  - You announced {s2['stated_action']} and chose "
                         f"{t['outcomes']['choices'][mine]} (payoff {t['outcomes']['payoffs'][mine]:.1f}).")
        ratings = agents[mine]["reflection"]["takeaways"] if mine is not None else {}
        for a in t["announcement_order"]:
            if a == mine:
                continue
            s2 = agents[a]["stage2"]
            line = (f'  - Agent {a} announced {s2["stated_action"]}: "{s2["message"]}"; '
                    f"chose {t['outcomes']['choices'][a]}")
            if a in ratings:
                line += (f"; your rating after the round: {ratings[a]['score']}/5 - "
                         f'"{ratings[a]["assessment"]}"')
            if accused.get(a) == "yes":
                line += "; you accused them of having been swapped"
            lines.append(line)
    return "\n".join(lines)


def player_log(branch: BranchState, round_idx: int, name: str, plan: RoundPlan, variant: Variant) -> str:
    """The memory log `name` sees in round `round_idx`.

    A cold newcomer remembers only the rounds it has played (and was never warned);
    with warn_first_only, everyone else's log opens with the warning given before round 1.
    """
    condition = CONDITIONS[branch.condition] if branch.condition else None
    cold = (condition is not None and condition.cold and round_idx >= plan.swap
            and name == seat_name(condition, round_idx, plan))
    pinned = PINNED_WARNING if variant.warned and variant.warn_first_only and not cold else ""
    return memory_log(branch.rounds[plan.swap if cold else 0:round_idx], name, pinned)


def round_context(branch: BranchState, round_idx: int, variant: Variant) -> str:
    """What the variant adds to every system prompt in this round: warning (and bonus rule),
    then history. With warn_first_only, the warning and bonus rule appear in round 1 only."""
    shown = round_idx == 0 or not variant.warn_first_only
    parts = [WARNING_TEXT] if variant.warned and shown else []
    if variant.detection_bonus and shown:
        parts.append(bonus_text(variant.detection_bonus, variant.accuse_from))
    if variant.history:
        parts.append(public_history(branch.rounds[:round_idx]))
    return "\n\n".join(p for p in parts if p)


# ---------------------------------------------------------------------------
# One round
# ---------------------------------------------------------------------------
def prepare(branch: BranchState, round_idx: int, plan: RoundPlan, models: ModelSet,
            variant: Variant) -> RoundSetup:
    """Roster, models and variant context for this round; applies the swap to memory."""
    condition = CONDITIONS[branch.condition] if branch.condition else None
    if condition is not None and round_idx == plan.swap:
        branch.memory = memory_at_swap(branch.memory, condition)
    names = roster(condition, round_idx, plan, variant.agent_names)
    cold_from = plan.swap if condition is not None and condition.cold and round_idx >= plan.swap else None
    setup = RoundSetup(branch, names, seat_models(condition, round_idx, plan, models, variant.agent_names),
                       seat_name(condition, round_idx, plan), condition,
                       round_context(branch, round_idx, variant), cold_from=cold_from)
    if variant.memory_log:
        setup.logs = {n: player_log(branch, round_idx, n, plan, variant) for n in names}
    return setup


def play_round(branches: List[BranchState], round_idx: int, plan: RoundPlan, models: ModelSet,
               clients: Clients, variant: Variant = VARIANTS["baseline"]) -> None:
    """Play round `round_idx` for every branch whose next round it is (mutates them).

    Completed rounds are appended to `branch.rounds`; a branch with a reply that never
    parses is marked failed and skipped for the rest of the round.
    """
    r = round_idx
    setups = {b.key: prepare(b, r, plan, models, variant) for b in branches
              if b.status == "running" and b.next_round == r}
    s1: Dict[str, dict] = {}
    s2: Dict[str, dict] = {}
    s3: Dict[str, dict] = {}

    def told(s: RoundSetup, name: str) -> bool:
        return is_told(name, s.condition, r, plan)

    def supports(s: RoundSetup, name: str) -> bool:
        return _model_supports_structured_output(s.models[name])

    def request(s: RoundSetup, cid: str, name: str,
                prompts: Tuple[str, str, Dict[str, Any]]) -> Dict[str, Any]:
        """A stage request for `name`, with the round's context and the told sentence if any."""
        return make_request(cid, s.models[name], prompts, told(s, name), context=s.context,
                            warned=variant.warned, prefix=s.logs.get(name, ""))

    # ---- Stage 1: private plan ----
    jobs = []
    for s in setups.values():
        for name in s.names:
            prompts = build_stage1_prompt(GAME_TYPE, name, s.names, GAME_PARAMS,
                                          supports_structured=supports(s, name),
                                          takeaways=s.branch.memory[name])
            cid = request_id(r, s.branch, "s1", name)
            jobs.append(Job(s.branch, name, request(s, cid, name, prompts),
                            parse_action("intended_action")))
    parsed = run_jobs(jobs, clients, f"R{r + 1} plan")
    fail_branches(setups, jobs, parsed, "plan", r)
    for s in setups.values():
        for name in s.names:
            s1[f"{s.branch.key}_{name}"] = {**parsed[request_id(r, s.branch, "s1", name)], "_parse_ok": True}

    # ---- Stage 2: announcements, one speaking position at a time ----
    for pos in range(len(variant.agent_names)):
        jobs = []
        for s in setups.values():
            name, key = s.names[pos], s.branch.key
            prior = [{"name": p, "stated_action": s2[f"{key}_{p}"]["stated_action"],
                      "message": s2[f"{key}_{p}"]["message"]} for p in s.names[:pos]]
            prompts = build_stage2_prompt(GAME_TYPE, name, s.names, s1[f"{key}_{name}"], GAME_PARAMS,
                                          supports_structured=supports(s, name),
                                          prior_announcements=prior)
            cid = request_id(r, s.branch, "s2", name)
            jobs.append(Job(s.branch, name, request(s, cid, name, prompts),
                            parse_action("stated_action", need_message=True)))
        parsed = run_jobs(jobs, clients, f"R{r + 1} announce pos {pos}")
        fail_branches(setups, jobs, parsed, "announce", r)
        for s in setups.values():
            name = s.names[pos]
            cid = request_id(r, s.branch, "s2", name)
            s2[f"{s.branch.key}_{name}"] = {**parsed[cid], "_parse_ok": True, "position": pos,
                                            "prior_seen": list(s.names[:pos])}

    # ---- Stage 3: final choice ----
    jobs = []
    for s in setups.values():
        key = s.branch.key
        stage2_all = {a: s2[f"{key}_{a}"] for a in s.names}
        for name in s.names:
            prompts = build_stage3_prompt(GAME_TYPE, name, s.names, stage2_all, GAME_PARAMS,
                                          stage1_result=s1[f"{key}_{name}"],
                                          stage2_self=s2[f"{key}_{name}"],
                                          self_reference=SELF_REFERENCE,
                                          supports_structured=supports(s, name))
            cid = request_id(r, s.branch, "s3", name)
            jobs.append(Job(s.branch, name, request(s, cid, name, prompts),
                            parse_action("choice")))
    parsed = run_jobs(jobs, clients, f"R{r + 1} choice")
    fail_branches(setups, jobs, parsed, "choice", r)
    for s in setups.values():
        for name in s.names:
            s3[f"{s.branch.key}_{name}"] = {**parsed[request_id(r, s.branch, "s3", name)], "_parse_ok": True}

    # ---- Assemble each branch's trial result (harness format) ----
    trials: Dict[str, Dict[str, Any]] = {}
    for key, s in setups.items():
        trial = _assemble_trial_results([key], s.names, s1, s2, s3, GAME_TYPE, GAME_PARAMS)[0]
        for agent in trial["agents"].values():
            agent.pop("judge", None)  # harness judge not run; key omitted (see DESIGN.md)
        trial.update(trial_id=s.branch.trial_id, branch_key=key, condition=s.branch.condition,
                     round_id=r, announcement_order=list(s.names), seat=s.seat,
                     seat_models=dict(s.models))
        trials[key] = trial

    # ---- Reflection: every agent rates every other agent (and may accuse, in bonus variants) ----
    bonus = variant.detection_bonus if r + 1 >= variant.accuse_from else 0.0
    jobs = []
    for key, s in setups.items():
        stage2_all = {a: s2[f"{key}_{a}"] for a in s.names}
        for name in s.names:
            for target in (t for t in s.names if t != name):
                prompts = build_single_agent_reflection_prompt(
                    GAME_TYPE, name, target, s.names, GAME_PARAMS, stage2_all,
                    trials[key]["outcomes"], s.branch.memory[name], r,
                    supports_structured=supports(s, name))
                parse = parse_reflection
                if bonus:
                    remembered = s.branch.rounds[s.first_round(name):]   # a cold newcomer's own rounds
                    accused_in = earlier_accusation(remembered, name, target)
                    prompts = with_accusation(prompts, target, bonus, accused_in, variant.accuse_from)
                    parse = parse_reflection if accused_in is not None else parse_reflection_accuse
                cid = request_id(r, s.branch, "refl", f"{name}>{target}")
                jobs.append(Job(s.branch, f"{name}>{target}",
                                request(s, cid, name, prompts), parse))
    parsed = run_jobs(jobs, clients, f"R{r + 1} reflection")
    fail_branches(setups, jobs, parsed, "reflection", r)
    for key, s in setups.items():
        for name in s.names:
            notes, accusations = {}, {}
            for target in (t for t in s.names if t != name):
                answer = dict(parsed[request_id(r, s.branch, "refl", f"{name}>{target}")])
                if "accuse" in answer:
                    accusations[target] = answer.pop("accuse")
                notes[target] = answer
            trials[key]["agents"][name]["reflection"] = {"takeaways": notes, "_parse_ok": True}
            if variant.detection_bonus:   # {} in rounds before accusations start
                trials[key]["agents"][name]["reflection"]["accusations"] = accusations
            s.branch.memory[name].update(notes)
        s.branch.rounds.append(trials[key])

    # ---- Probe (every player but the swapped seat; never written to memory) ----
    run_probes([s for s in setups.values() if is_probe_round(s.branch, r, plan)], r, trials, clients,
               variant.probe_version, variant.shuffle_forced)

    for s in setups.values():
        end = plan.swap if s.branch.condition is None else plan.total_rounds
        if s.branch.next_round >= end:
            s.branch.status = "complete"


def is_probe_round(branch: BranchState, round_idx: int, plan: RoundPlan) -> bool:
    """Trunks probe only at the last trunk round; branches at probe rounds after the swap."""
    if round_idx not in plan.probe_rounds:
        return False
    return round_idx == plan.swap - 1 if branch.condition is None else round_idx >= plan.swap


def run_probes(setups: List[RoundSetup], round_idx: int, trials: Dict[str, Dict[str, Any]],
               clients: Clients, version: int = 1, shuffle: bool = False) -> None:
    """Ask every player but the swapped seat the probe questions and store the answers.

    A probe that never parses is recorded with parse_ok False; it does not stop the
    branch, because no other agent ever sees it. With `shuffle`, the forced-choice
    options are listed in an order seeded by the request id (reproducible on resume).
    """
    jobs, meta = [], {}
    for s in setups:
        renamed = s.seat != SWAP_SEAT
        allowed = allowed_which(s.names, SWAP_SEAT if renamed else None)
        for name in (n for n in s.names if n != s.seat):
            structured = _model_supports_structured_output(s.models[name])
            cid = request_id(round_idx, s.branch, "probe", name)
            forced = forced_options(s.names, name)
            if shuffle:
                random.Random(cid).shuffle(forced)
            prompts = build_probe_prompt(name, s.names, s.branch.memory[name], trials[s.branch.key],
                                         round_idx, allowed, ask_same=renamed,
                                         supports_structured=structured, version=version,
                                         forced=forced)
            request = make_request(cid, s.models[name], prompts, told=False, context=s.context,
                                   prefix=s.logs.get(name, ""))
            jobs.append(Job(s.branch, name, request,
                            lambda raw, a=allowed, ask=renamed, f=forced:
                            parse_probe(raw, a, ask, version, f),
                            fallback=lambda raw, a=allowed, ask=renamed, f=forced:
                            parse_probe(raw, a, ask, version, f, allow_refusal=True)))
            meta[cid] = (s.branch, name)
    parsed = run_jobs(jobs, clients, f"R{round_idx + 1} probe")
    for cid, (branch, name) in meta.items():
        answer = parsed.get(cid)
        branch.probes.append({"round_id": round_idx, "agent": name, "parse_ok": answer is not None,
                              **(answer or {})})


# ---------------------------------------------------------------------------
# Driving many branches to completion
# ---------------------------------------------------------------------------
def calls_for_round(branch: BranchState, round_idx: int, plan: RoundPlan,
                    models: ModelSet, players: Names = AGENT_NAMES) -> Dict[str, int]:
    """Calls per model one branch makes in one round, without re-asks.

    Each player makes 3 stage calls plus one reflection per other player; on probe
    rounds each unswapped player also answers the probe.
    """
    condition = CONDITIONS[branch.condition] if branch.condition else None
    names = roster(condition, round_idx, plan, players)
    calls: Dict[str, int] = {}
    for name, model in seat_models(condition, round_idx, plan, models, players).items():
        calls[model] = calls.get(model, 0) + 3 + (len(names) - 1)
    if is_probe_round(branch, round_idx, plan):
        calls[models.base] = calls.get(models.base, 0) + len(names) - 1
    return calls


def openai_calls_for_round(batch: List[BranchState], round_idx: int, plan: RoundPlan,
                           models: ModelSet, players: Names = AGENT_NAMES) -> int:
    """Expected OpenAI calls for one round of these branches."""
    return sum(n for b in batch for m, n in calls_for_round(b, round_idx, plan, models, players).items()
               if is_openai_model(m))


def run_branches(branches: List[BranchState], plan: RoundPlan, models: ModelSet, clients: Clients,
                 save: Callable[[BranchState], None],
                 before_round: Callable[[int], None] = lambda r: None,
                 variant: Variant = VARIANTS["baseline"]) -> None:
    """Play rounds until every branch is complete or failed, saving after each round.

    Branches at different rounds (e.g. after a resume) are advanced lowest round first.
    `before_round` runs before each batch (spend checks); it may raise to stop the run.
    """
    while True:
        running = [b for b in branches if b.status == "running"]
        if not running:
            return
        r = min(b.next_round for b in running)
        batch = [b for b in running if b.next_round == r]
        before_round(r)
        clients.check_room(openai_calls_for_round(batch, r, plan, models, variant.agent_names))
        play_round(batch, r, plan, models, clients, variant)
        for b in batch:
            save(b)
