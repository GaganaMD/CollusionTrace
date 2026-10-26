"""Readable Markdown of every game: runs/<run>/transcripts/readable/<trunk|calib|condition>/trial_<id>.md

    python -m signal_ring.transcripts [--fake]

Shows what every player said and thought, picks, outcomes, notes, exclusion marks and
probe answers, with the model behind each seat (which the players never see).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

from signal_ring import state as S
from signal_ring.cli import add_common_args, open_run
from signal_ring.config import RING
from signal_ring.state import GameState


def render(g: GameState) -> str:
    lines = [f"# {g.key} ({g.condition or 'trunk'}), status {g.status}", ""]
    if g.failure:
        lines += [f"**Failed:** {g.failure}", ""]
    last_models = None
    for t in g.rounds:
        r = t["round"]
        if t["models"] != last_models:
            lines.append("*Models: " + ", ".join(f"{s} = {m}" for s, m in t["models"].items()) + "*")
            lines.append("")
            last_models = t["models"]
        if t["phase"] == "setup":
            lines.append(f"## Setup round {r} (private)")
            lines += [f"- **{m['seat']}:** {m['message']}" for m in t["setup"]]
            for s, note in (t.get("code_notes") or {}).items():
                lines.append(f"- *{s}'s code note:* {note}")
            lines.append("")
            continue
        o = t["outcome"]
        lines.append(f"## Round {r}: sender {t['sender']}, target {t['target']}"
                     + (f", {t['cut_out']} cut out" if t.get("cut_out") else ""))
        if t.get("rekey"):
            lines.append(f"Re-key ({' and '.join(t['rekey']['pair'])}):")
            lines += [f"- **{m['seat']}:** {m['message']}" for m in t["rekey"]["messages"]]
        for m in t["talk"]:
            lines.append(f"- **{m['seat']}:** {m['message']}  \n  *thinking: {m.get('thinking', '')}*")
        picks = ", ".join(f"{s} {p['pick']}" for s, p in t["picks"].items())
        lines.append(f"- Picks: {picks}; M guessed {t['monitor']['guess']} (*{t['monitor'].get('thinking', '')}*)")
        lines.append(f"- Ring success {o['ring_success']}, caught {o['caught']}, ring points {o['ring_points']:+g}")
        for s in RING:
            refl = (t.get("reflections") or {}).get(s)
            if not refl:
                continue
            extra = f" | suspicion {refl['suspicion']}" if refl.get("suspicion") else ""
            excl = f" | **marks {refl['exclude']}**" if refl.get("exclude") else ""
            notes = "; ".join(f"on {x}: {n}" for x, n in refl["notes"].items())
            lines.append(f"- *{s} notes:* {notes}{extra}{excl}")
        for s, pr in (t.get("probes") or {}).items():
            lines.append(f"- *probe {s}:* replaced {pr['replaced']} ({pr['which']}, {pr['confidence']}), "
                         f"likelihood {pr['likelihood']}, forced {pr['forced']}")
        lines.append("")
    return "\n".join(lines)


def main(argv: List[str] = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_common_args(p)
    args = p.parse_args(argv)
    run, _ = open_run(args)
    root = S.run_dir(run)
    out = root / "transcripts" / "readable"
    n = 0
    for folder in [root / "trunk", root / "calib"] + sorted((root / "branches").glob("*")):
        for path in sorted(Path(folder).glob("trial_*.json")):
            g = S.load_state(path)
            target = out / folder.name / f"{path.stem}.md"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(render(g))
            n += 1
    print(f"wrote {n} transcripts under {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
