"""Send a phone notification (ntfy) for each model as it finishes the screen.

Watches screen/screen_log.jsonl; for every new entry it summarises that model's
output with analyze_screen.summarise() and posts a 3-4 line status. Exits when
the rerun script is no longer running and no new entries remain.
Usage: harness/.venv/bin/python screen/notify_models.py
"""
import json
import subprocess
import time
import urllib.request
from pathlib import Path

from analyze_screen import LOG, OUT_DIR, label, pct, summarise

TOPIC = (Path.home() / ".claude2/hooks/ntfy-topic").read_text().strip()
TOTAL = 15
RERUNS = 2


def send(title, body):
    req = urllib.request.Request(f"https://ntfy.sh/{TOPIC}", data=body.encode(), headers={"Title": title})
    try:
        urllib.request.urlopen(req, timeout=10)
    except OSError:
        pass


def running():
    return subprocess.run(["pgrep", "-f", "run_screen_v4.sh$"], capture_output=True).returncode == 0


def message(e, n_main, n_rerun):
    model = e["model"]
    cost = e.get("or_usage_after", 0) - e.get("or_usage_before", 0) if isinstance(e.get("or_usage_after"), (int, float)) else None
    cost_s = "OpenAI-billed" if model.startswith("gpt-") else (f"${cost:.2f}" if cost is not None else "cost n/a")
    tag = " (rerun, fixed parser)" if e.get("rerun") else ""
    progress = f"Rerun {n_rerun}/{RERUNS}" if e.get("rerun") else f"Model {n_main}/{TOTAL}"
    f = OUT_DIR / f"{model.replace('/', '_')}_endogenous.json"
    if e["exit"] != 0 or not f.exists():
        why = "stopped at $0.80 spend cap" if e["exit"] == 99 else f"failed (exit {e['exit']})"
        return f"{progress}: {model} {why}{tag}", f"{progress} after {e['seconds']} s, {cost_s}.\nNo results saved; see screen/logs/."
    s = summarise(f)
    p = s["parse"]
    cls = label(s["late"]).strip("*")
    body = (f"{cls}: {pct(s['late'])} CHEAP in rounds 3-4 (by round: {' / '.join(pct(x) for x in s['per_round'])}).\n"
            f"Broke commitment {pct(s['breaks'])}, lied {pct(s['lies'])}, mean payoff {s['payoff']:.2f}.\n"
            f"Parse plan/announce/choice/reflect: {pct(p['stage1'])}/{pct(p['stage2'])}/{pct(p['stage3'])}/{pct(p['reflection'])}.\n"
            f"{progress}, {e['seconds']} s, {cost_s}.")
    return f"{model}: {cls}{tag}", body


def main():
    seen = len(LOG.read_text().splitlines())
    while True:
        lines = LOG.read_text().splitlines()
        for line in lines[seen:]:
            e = json.loads(line)
            entries = [json.loads(x) for x in lines]
            n_main = sum(1 for x in entries if not x.get("rerun"))
            n_rerun = sum(1 for x in entries if x.get("rerun"))
            send(*message(e, n_main, n_rerun))
        seen = len(lines)
        if not running():
            break
        time.sleep(15)


if __name__ == "__main__":
    main()
