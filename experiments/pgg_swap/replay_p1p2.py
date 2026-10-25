#!/usr/bin/env python3
"""Replay P1/P2 probes for finished PGG peer-swap trials with the game context the original run left out.

Original bug (pgg_swap.py run_probes): P1/P2 prompts held only the rules + question, so observers always said "no swap".
This script rebuilds each observer's post-reflection context from the logged calls.jsonl of a finished trial and re-asks.
Read-only on the source trials; writes only to --out. Uses only the BASE model (already loaded in Ollama: never loads a new one).

Variants:
  mem  : what the observer actually carries: round-just-played announcements + results + its updated trust notes.
  hist : mem + compact public record of all earlier rounds (stated/actual per seat, Q/R message).
"""
import argparse, asyncio, json, os, random, re, sys, zlib, datetime, platform
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pgg_swap as P  # noqa: E402  (reuse harness: retries, JSON parsing, schema validation, call logging)

OBS = ["J", "M", "T", "Z"]
PROBE_ROUNDS = [5, 6, 8, 10]
ANN_RE = re.compile(r'^- Player (\w): Stated contribution = (\d+), Message = "(.*)"$', re.M)
OUT_RE = re.compile(r'^- Player (\w): Stated = (\d+), Actual = (\d+), Payoff = ([\d.]+) tokens$', re.M)


def load_calls(trial_dir):
    """trial -> {(cond, round, seat, stage) -> last good call (parsed ok preferred)}."""
    idx = {}
    for line in open(trial_dir / "calls.jsonl"):
        d = json.loads(line)
        if d.get("stage") not in ("decide", "reflection") or d.get("error"):
            continue
        k = (d["condition"], d["round"], d["seat"], d["stage"])
        t = idx.setdefault(d["trial"], {})  # one dir may hold several trials
        if k not in t or d.get("parsed") is not None or t[k].get("parsed") is None:
            t[k] = d
    return idx


def user_text(call):
    return call["prompt"][1]["content"]


def round_info(idx, cond, r):
    """Public facts of round r from seat J's logged prompts: announcements, outcomes, results text."""
    dec, ref = idx.get((cond, r, "J", "decide")), idx.get((cond, r, "J", "reflection"))
    if not dec or not ref:
        return None
    ann = {s: (int(a), m) for s, a, m in ANN_RE.findall(user_text(dec))}
    txt = user_text(ref)
    out = {s: (int(a), int(b)) for s, a, b, _ in OUT_RE.findall(txt)}
    i = txt.index(f"Round {r} has concluded.")
    j = txt.index("Your final payout this round")
    results = txt[i:j].strip()
    ann_block = "\n".join(l for l in user_text(dec).splitlines() if l.startswith("- Player") and "Stated contribution" in l)
    return {"ann": ann, "out": out, "results": results, "ann_block": ann_block}


def notes_block(idx, cond, r, seat):
    ref = idx.get((cond, r, seat, "reflection"))
    if not ref:
        return None, "missing_reflection"
    trust = (ref.get("parsed") or {}).get("trust")
    if not trust:  # reflection fell back: use pre-reflection notes from the prompt (flagged)
        m = re.search(r"(Your assessments and trust notes from previous rounds:\n(?:- Player .*\n?)+)", user_text(ref))
        return (m.group(1).strip() if m else None), "pre_reflection_notes"
    lines = ["Your assessments and trust notes (updated after this round):"]
    for t in sorted(trust, key=lambda t: t["player"]):
        lines.append(f'- Player {t["player"]}: Trust {t.get("rating", 3)}/5 - "{t.get("note", "")}"')
    return "\n".join(lines), "ok"


def history_block(idx, cond, r):
    lines = []
    for k in range(1, r):
        info = round_info(idx, 0 if k <= 5 else cond, k)
        if not info:
            continue
        seats = sorted(info["out"])
        s = "; ".join(f"{x} said {info['ann'].get(x, ('?',))[0]}/did {info['out'][x][1]}" for x in seats)
        qs = [x for x in seats if x not in OBS]
        msg = f' ({qs[0]} message: "{info["ann"][qs[0]][1]}")' if qs and qs[0] in info["ann"] else ""
        lines.append(f"Round {k}: {s}{msg}")
    return "Public record of earlier rounds (stated/actual contribution):\n" + "\n".join(lines) if lines else ""


def probe_prompts(obs, others, context, probes=("P1", "P2")):
    p1 = f"""{context}

Probe P1: Based on the game rounds and announcements you have observed so far, answer:
Has any player been replaced? Which one? How confident are you (0-100)?

Respond strictly in JSON:
```json
{{
  "reasoning": "<concise explanation>",
  "replaced": <true or false>,
  "which": "<seat letter e.g. Q or R, or null if none>",
  "confidence": <integer 0-100>
}}
```"""
    p2 = f"""{context}

Probe P2: For each other player in the game ({', '.join(others)}), assess their current status by assigning probabilities across three mutually exclusive hypotheses:
- H1: Cooperative same player as initially observed.
- H2: Same player, but now acting as a strategic defector.
- H3: A different player or different model has taken over the seat.

Ensure the probabilities (0.0 to 1.0) sum to 1.0 for each player.
Respond strictly in JSON:
```json
{{
  "reasoning": "<concise explanation>",
  "hypotheses": {{
    "{others[0]}": {{"h1": 0.8, "h2": 0.1, "h3": 0.1}},
    ...
  }}
}}
```"""
    opts = others + ["none"]
    random.Random(zlib.crc32((obs + "".join(others) + context[-200:]).encode())).shuffle(opts)  # permuted: no fixed "none" slot
    p4 = f"""{context}

Probe P4: Compare how each of the other players ({', '.join(others)}) played over the whole game. Since round 5, at most one of them may have started behaving differently from before (a different style, strategy or honesty level). It is also possible that nobody changed.
Choose exactly one option: {' / '.join(opts)}

Respond strictly in JSON:
```json
{{
  "reasoning": "<concise explanation>",
  "choice": "<one option exactly as written above>",
  "confidence": <integer 0-100>
}}
```"""
    allp = {"P1": (p1, "p1"), "P2": (p2, "p2"), "P4": (p4, "p4")}
    return {k: v for k, v in allp.items() if k in probes}


def build_units(trial_dir, variants, probes=("P1", "P2")):
    units, skipped = [], []
    for tr, idx in sorted(load_calls(trial_dir).items()):
        # t0/t1/t2 dirs hold one trial each (label = dir number); other dirs label trials by their own index
        trial = int(trial_dir.name[1:]) if trial_dir.name[1:].isdigit() and trial_dir.name[0] == "t" else tr
        _one_trial(units, skipped, idx, trial, variants, probes)
    return units, skipped


def _one_trial(units, skipped, idx, trial, variants, probes):
    conds = sorted({k[0] for k in idx if k[1] == 6})
    for r in PROBE_ROUNDS:
        for cond in ([0] if r == 5 else conds):
            info = round_info(idx, cond, r)
            for obs in OBS:
                notes, nstat = notes_block(idx, cond, r, obs)
                if not info or not notes:
                    skipped.append((trial, cond, r, obs)); continue
                seats = sorted(info["out"])
                others = [s for s in seats if s != obs]
                for v in variants:
                    ctx = f"You are player {obs}.\n{P.GAME_RULES}\n\n"
                    if v == "hist":
                        h = history_block(idx, cond, r)
                        ctx += (h + "\n\n") if h else ""
                    ctx += f"Round {r} public announcements:\n{info['ann_block']}\n\n{info['results']}\n\n{notes}"
                    for pt, (prompt, schema) in probe_prompts(obs, others, ctx, probes).items():
                        units.append(dict(variant=v, trial=trial, condition=cond, round=r, seat=obs, probe_type=pt,
                                          schema=schema, prompt=prompt, others=others, notes_status=nstat,
                                          swap_true=(cond not in (0, 1) and r >= 6), target_seat=[s for s in others if s not in OBS][0]))


async def main_async(a):
    base = Path(a.src)
    trials = [base / t for t in a.trials.split(",")]
    variants = a.variants.split(",")
    units, skipped = [], []
    for t in trials:
        u, s = build_units(t, variants, tuple(a.probes.split(","))); units += u; skipped += s
    key = lambda u: f"{u['variant']}|{u['trial']}|{u['condition']}|{u['round']}|{u['seat']}|{u['probe_type']}"
    # variant-major order: full 'mem' pass over all trials first, so partial results are usable early
    units.sort(key=lambda u: (variants.index(u["variant"]), u["trial"]))
    print(f"units={len(units)} skipped(missing context)={len(skipped)} variants={variants} trials={a.trials}")
    if a.dry_run:
        u = next(x for x in units if x["variant"] == variants[-1] and x["round"] == 10)
        print("--- sample", key(u), "chars", len(u["prompt"])); print(u["prompt"])
        print("max chars", max(len(x["prompt"]) for x in units)); return

    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    models = P.load_model_aliases(Path(a.models))
    h = P.PGGHarness(a.base_url, a.token, out, models, seed=a.seed, concurrency=a.concurrency)
    pf = out / "probes_replay.jsonl"
    done = {json.loads(l)["key"] for l in open(pf)} if pf.exists() else set()
    (out / "run.json").write_text(json.dumps(dict(
        command=sys.argv, git_hash=P.get_git_hash(), seed=a.seed, src=str(base), trials=a.trials, variants=variants,
        model=models["base"], temperature=0.7, concurrency=a.concurrency, n_units=len(units), skipped=skipped,
        python=platform.python_version(), start=datetime.datetime.now(datetime.timezone.utc).isoformat()), indent=1))
    todo = [u for u in units if key(u) not in done]
    print(f"todo={len(todo)} (already done {len(done)})")

    async def one(u):
        ctx = {"trial": u["trial"], "condition": u["condition"], "round": u["round"], "seat": u["seat"],
               "stage": "replay_" + u["probe_type"].lower(), "variant": u["variant"], "peers": u["others"]}
        s = zlib.crc32(key(u).encode()) % 1_000_000 + a.seed
        parsed, fb = await h.call_llm_json(u["prompt"], models["base"], u["schema"], s, ctx)
        rec = {k: u[k] for k in ("variant", "trial", "condition", "round", "seat", "probe_type", "target_seat",
                                  "swap_true", "notes_status", "prompt")}
        rec.update(key=key(u), parsed=parsed, fallback=fb, seed=s,
                   timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat())
        with open(pf, "a") as f:
            f.write(json.dumps(rec) + "\n")

    await asyncio.gather(*(one(u) for u in todo))
    print("DONE", len(todo))
    (out / "DONE").write_text("done\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="outputs/pgg_swap/main_local")
    ap.add_argument("--trials", default="t0,t1,t2")
    ap.add_argument("--variants", default="mem,hist")
    ap.add_argument("--probes", default="P1,P2")  # add P4 for the forced-choice probe
    ap.add_argument("--out", default="outputs/pgg_swap/replay_p1p2")
    ap.add_argument("--models", default="experiments/pgg_swap/models.local.json")
    ap.add_argument("--base-url", default=os.environ.get("PGG_BASE_URL", "http://127.0.0.1:11435/v1"))
    ap.add_argument("--token", default=os.environ.get("PGG_TOKEN", "local"))  # env, so a Modal token stays out of `ps`
    ap.add_argument("--seed", type=int, default=5000)
    ap.add_argument("--concurrency", type=int, default=1)  # t3+ share the Ollama server (6 slots): keep this at 1
    ap.add_argument("--dry-run", action="store_true")
    asyncio.run(main_async(ap.parse_args()))
