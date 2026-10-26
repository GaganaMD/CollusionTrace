"""Write readable transcripts of every game and an index of all artifacts.

Usage (from /home/vsskl/collusion_peer):
    harness/.venv/bin/python -m experiment.export_transcripts --model-set option_b

Outputs under experiment/runs/<model_set>/:
    transcripts/readable/trunk/trial_<id>.md          rounds before the swap, every trunk trial
    transcripts/readable/<condition>/trial_<id>.md    a full branch, every round
    ARTIFACTS.md                                      what every file and folder contains

Each transcript shows, per round: private plans, public announcements (in speaking
order), final choices with payoffs, private choice reasoning, every trust rating and
note, and the probe answers. For memory-log variants, a branch transcript ends with the
log each player saw at the swap round. The raw prompts and replies behind them are in
transcripts/raw/ (written while the games run).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List

from experiment import cli_common
from experiment.config import CONDITIONS, MAX_TRIALS, RoundPlan, variant_of
from experiment.engine import player_log
from experiment.state import (BranchState, branch_path, condition_path, load_state, run_dir,
                              trunk_path)


def _one_line(text: Any) -> str:
    """Text on one line, safe inside a Markdown table cell."""
    return " ".join(str(text or "").split()).replace("|", "/")


def render_round(trial: Dict[str, Any], probes: List[Dict[str, Any]]) -> List[str]:
    """Markdown for one round of one game."""
    names = trial["announcement_order"]
    agents, payoffs = trial["agents"], trial["outcomes"]["payoffs"]
    models = trial.get("seat_models", {})
    L = [f"## Round {trial['round_id'] + 1}", "",
         f"Swapped seat this round: **{trial['seat']}** ({models.get(trial['seat'], '?')})", "",
         "### Private plans (seen only by the agent itself)", ""]
    L += [f"- **{a}** ({models.get(a, '?')}) plans **{agents[a]['stage1']['intended_action']}**: "
          f"{_one_line(agents[a]['stage1']['reasoning'])}" for a in names]
    L += ["", "### Public announcements (in speaking order; seen by everyone after the speaker)", ""]
    L += [f"{i + 1}. **{a}** announces **{agents[a]['stage2']['stated_action']}**: "
          f"\"{_one_line(agents[a]['stage2']['message'])}\"" for i, a in enumerate(names)]
    L += ["", "### Final choices (public after the round)", "",
          "| Agent | Choice | Payoff | Announcement ≠ plan | Choice ≠ announcement | Label |",
          "|---|---|---|---|---|---|"]
    for a in names:
        ag = agents[a]
        L.append(f"| {a} | {ag['stage3']['choice']} | {payoffs.get(a, 0):.2f} | "
                 f"{ag['promise_deception']} | {ag['commitment_breaking']} | {ag['typology']} |")
    L += ["", "### Choice reasoning (private)", ""]
    L += [f"- **{a}**: {_one_line(agents[a]['stage3']['reasoning'])}" for a in names]
    L += ["", "### Trust ratings after the round (private; carried into the next round's plan)", "",
          "| Rater \\ About | " + " | ".join(names) + " |", "|---|" + "---|" * len(names)]
    for rater in names:
        notes = (agents[rater].get("reflection") or {}).get("takeaways", {})
        cells = ["–" if t == rater else str(notes.get(t, {}).get("score", "?")) for t in names]
        L.append(f"| {rater} | " + " | ".join(cells) + " |")
    L += [""]
    for rater in names:
        reflection = agents[rater].get("reflection") or {}
        accused = reflection.get("accusations") or {}   # detection-bonus runs only
        for target, note in reflection.get("takeaways", {}).items():
            score, text = note.get("score", "?"), _one_line(note.get("assessment"))
            mark = " **[accuses them of having been swapped]**" if accused.get(target) == "yes" else ""
            L.append(f"- {rater} on {target} ({score}/5){mark}: {text}")
    mine = [p for p in probes if p["round_id"] == trial["round_id"]]
    if mine:
        L += ["", "### Probe answers (side question; never shown to other agents or kept in memory)",
              "",
              "| Agent | Replaced? | Which | Confidence | R is the old Q? | Confidence |",
              "|---|---|---|---|---|---|"]
        for p in mine:
            if not p["parse_ok"]:
                L.append(f"| {p['agent']} | (no valid answer) | | | | |")
                continue
            L.append(f"| {p['agent']} | {p['replaced']} | {p['which']} | {p['confidence']} | "
                     f"{p.get('same_as_q', '–')} | {p.get('same_confidence', '–')} |")
    return L + [""]


def render(b: BranchState) -> str:
    """Markdown transcript of a whole trunk or branch."""
    plan = RoundPlan(**b.config["rounds"])
    if b.condition:
        c = CONDITIONS[b.condition]
        title = f"# {b.model_set}: trial {b.trial_id}, condition {c.number}. {c.label}"
        about = (f"Rounds 1–{plan.swap} are the shared trunk (identical in every condition). "
                 f"From round {plan.swap + 1}, seat Q is played as: name "
                 f"{'R' if c.rename else 'Q'}, model role '{c.seat_role}', "
                 f"told: {'yes' if c.told else 'no'}.")
    else:
        title = f"# {b.model_set}: trunk trial {b.trial_id}"
        about = f"Rounds 1–{plan.swap}, all seats on the base model."
    L = [title, "", about, "",
         f"Status: **{b.status}**. Re-asked replies: {len(b.reasks)}.", ""]
    if b.failure:
        L += [f"Failure: {b.failure}", ""]
    if b.history:
        L += [f"Earlier failed attempts: {[h['failure'] for h in b.history]}", ""]
    for trial in b.rounds:
        L += render_round(trial, b.probes)
    if b.condition and variant_of(b.config).memory_log and len(b.rounds) > plan.swap:
        L += ["", f"## Memory log shown to each player in round {plan.swap + 1} (the swap round)", "",
              "Each player's system prompt starts with this text in every call of the round.", ""]
        for name in b.rounds[plan.swap]["announcement_order"]:
            L += [f"### {name}", "", "```", player_log(b, plan.swap, name, plan, variant_of(b.config)),
                  "```", ""]
    return "\n".join(L)


def artifact_index(model_set: str) -> str:
    """ARTIFACTS.md: every output folder and file, with what it holds."""
    root = run_dir(model_set)

    def count(pattern: str) -> str:
        n = len(list(root.glob(pattern)))
        return f"{n} file{'' if n == 1 else 's'}"

    rows = [
        ("trunk/run_config.json",
         "Settings fixed for the whole run (models, rounds, prompts, harness version)"),
        ("trunk/trial_<id>.json",
         f"Trunk game state per trial: rounds, memory, probes ({count('trunk/trial_*.json')})"),
        ("trunk/selection.json", "Which trunk trials passed the cooperation rule and were kept"),
        ("branches/<condition>/trial_<id>.json",
         f"Full game state per branch: rounds 1–end, probes, re-asks "
         f"({count('branches/*/trial_*.json')})"),
        ("conditions/<condition>.json",
         f"All kept trials of a condition in harness format, viewer-compatible "
         f"({count('conditions/*.json')})"),
        ("transcripts/raw/<trunk or condition>/trial_<id>.jsonl",
         "Every request sent: exact system and user prompts, raw reply, attempt and session; "
         "branch files cover the rounds after the swap, trunk files the rounds before "
         f"({count('transcripts/raw/*/trial_*.jsonl')})"),
        ("transcripts/raw/judge/notes.jsonl", "Raw change-judge requests and replies"),
        ("transcripts/raw/ceiling/items.jsonl", "Raw ceiling-test requests and replies"),
        ("ceiling/items.jsonl, ceiling/ceiling_report.md",
         "Ceiling test: can a model tell from the messages alone that the seat's writer changed?"),
        ("transcripts/readable/<trunk or condition>/trial_<id>.md",
         f"Readable transcript per game: plans, announcements, choices, ratings, probes "
         f"({count('transcripts/readable/*/trial_*.md')})"),
        ("judge_notes.jsonl", "Change-judge labels (identity / style / behavior) per note"),
        ("hand_check.csv, hand_check_key.json", "30-note hand-check sheet and its answer key"),
        ("api_errors.jsonl", "Requests that still failed after all API retries"),
        ("report.md, report.csv", "Metrics and pre-registered contrasts"),
    ]
    L = [f"# Artifacts: {model_set}", "", "| Path | Contents | Present |", "|---|---|---|"]
    for path, what in rows:
        first = path.split(",")[0].replace("<condition>", "*").replace("<id>", "*")
        first = first.replace("<trunk or condition>", "*")
        L.append(f"| `{path}` | {what} | {'yes' if list(root.glob(first)) else 'not yet'} |")
    L += ["", "Raw transcripts are append-only. After a stop and resume, a raw file can hold lines "
          "from an abandoned, partly played round (earlier `session`) before the replayed round "
          "(new `session`); `attempt` counts re-asks within one session. The state files "
          "(`trunk/`, `branches/`) are authoritative: raw lines for a round that isn't in the "
          "state file, or from an earlier session than the one that completed it, are "
          "abandoned attempts."]
    return "\n".join(L) + "\n"


def export(model_set: str) -> int:
    """Write every readable transcript and the index; return the number of transcripts."""
    out = run_dir(model_set) / "transcripts" / "readable"
    written = 0
    paths = [trunk_path(model_set, t) for t in range(MAX_TRIALS)]
    paths += [branch_path(model_set, c, t) for c in CONDITIONS for t in range(MAX_TRIALS)]
    for path in (p for p in paths if p.exists()):
        b = load_state(path)
        folder = b.condition or "trunk"
        target = out / folder / f"trial_{b.trial_id}.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render(b))
        written += 1
    (run_dir(model_set) / "ARTIFACTS.md").write_text(artifact_index(model_set))
    return written


def main(argv: List[str] = None) -> int:
    """Export readable transcripts and the artifact index. Returns an exit code."""
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model-set", required=True, choices=sorted(cli_common.MODEL_SETS))
    cli_common.add_variant_arg(parser)
    parser.add_argument("--fake", action="store_true", help="export experiment/runs_fake/")
    args = parser.parse_args(argv)
    run = cli_common.run_name(args)
    cli_common.setup_output(args.fake, run)
    n = export(run)
    print(f"wrote {n} readable transcripts and {run_dir(run) / 'ARTIFACTS.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
