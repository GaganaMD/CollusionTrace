#!/usr/bin/env python3
"""Screen ONE open-weight model on Modal like Siva's model screen: download (CPU) -> deploy -> wait healthy
-> N trials of rounds 1-5 (no swap branches) -> ALWAYS stop the app (GPU billing).

usage: PGG_TOKEN=... python3 experiments/pgg_swap/screen_one.py '{"id":"Qwen/Qwen2.5-14B-Instruct","slug":"qwen25-14b","gpu":"L40S","flags":[]}'
Writes outputs/pgg_swap/screen/<slug>/{driver.log,status.json,calls.jsonl,rounds.jsonl,probes.jsonl,run.json}.
"""
import json, os, re, signal, subprocess, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = json.loads(sys.argv[1])
SLUG, MODEL = SPEC["slug"], SPEC["id"]
OUT = ROOT / "outputs/pgg_swap/screen" / SLUG
OUT.mkdir(parents=True, exist_ok=True)
APP = f"pgg-scr-{SLUG}"
ENV = dict(os.environ, SCREEN_MODEL=MODEL, SCREEN_GPU=SPEC.get("gpu", "A10G"), SCREEN_APP=APP,
           SCREEN_FLAGS=json.dumps(SPEC.get("flags", [])))
assert ENV.get("PGG_TOKEN"), "PGG_TOKEN must be in the environment"
T0 = time.time()
status = {"slug": SLUG, "model": MODEL, "gpu": ENV["SCREEN_GPU"], "phase": "start", "ok": False}


def log(msg):
    line = f"[{time.time() - T0:6.0f}s] {msg}"
    print(line, flush=True)
    with open(OUT / "driver.log", "a") as f:
        f.write(line + "\n")


def save(**kw):
    status.update(kw, elapsed_s=round(time.time() - T0))
    (OUT / "status.json").write_text(json.dumps(status, indent=1))


def run(cmd, timeout):
    return subprocess.run(cmd, cwd=ROOT, env=ENV, capture_output=True, text=True, timeout=timeout)


def stop_app():
    r = run(["modal", "app", "stop", APP], 120)
    if r.returncode != 0:  # fall back to id lookup
        ls = run(["modal", "app", "list"], 120).stdout
        for line in ls.splitlines():
            if APP in line and "deployed" in line:
                run(["modal", "app", "stop", re.search(r"ap-\w+", line).group(0)], 120)
    log("app stop requested")


def main():
    try:
        save(phase="download")
        r = run(["modal", "run", "experiments/pgg_swap/serve_modal_screen.py::download"], 1800)
        log(f"download rc={r.returncode} {r.stdout[-200:].strip()!r}")
        if r.returncode != 0:
            return save(phase="download_failed", err=(r.stdout + r.stderr)[-500:])
        save(phase="deploy")
        r = run(["modal", "deploy", "experiments/pgg_swap/serve_modal_screen.py"], 900)
        m = re.search(r"https://\S+serve\S*\.modal\.run", r.stdout + r.stderr)
        if r.returncode != 0 or not m:
            return save(phase="deploy_failed", err=(r.stdout + r.stderr)[-500:])
        url = m.group(0).rstrip("│ ")
        log(f"deployed {url}")
        save(phase="wait_ready")
        ready = False
        for _ in range(SPEC.get("wait", 40)):  # x10 s incl. loading weights; a crashed server just burns this wait, keep it short
            try:
                h = json.load(urllib.request.urlopen(url + "/healthz", timeout=30))
                if h.get("all_up"):
                    ready = True
                    break
            except Exception:
                pass
            time.sleep(10)
        if not ready:
            return save(phase="backend_never_ready")
        log("backend ready")
        (OUT / "models.json").write_text(json.dumps({"base": MODEL}))
        save(phase="run_trials")
        env2 = dict(ENV, PGG_BASE_URL=url + "/v1")
        if SPEC.get("extra_body"):
            env2["PGG_EXTRA_BODY"] = json.dumps(SPEC["extra_body"])
        r = subprocess.run(
            [sys.executable, "experiments/pgg_swap/pgg_swap_pc.py", "--trials", str(SPEC.get("trials", 2)), "--conditions", "",
             "--seed", "300", "--concurrency", "32", "--models", str(OUT / "models.json"), "--out", str(OUT)],
            cwd=ROOT, env=env2, capture_output=True, text=True, timeout=900)
        log(f"harness rc={r.returncode} {r.stdout[-150:].strip()!r}")
        save(phase="done", ok=(r.returncode == 0), harness_rc=r.returncode, err=(r.stderr[-400:] if r.returncode else ""))
    except subprocess.TimeoutExpired as e:
        save(phase="timeout:" + str(status["phase"]))
    finally:
        stop_app()


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, lambda *a: sys.exit(1))  # finally-block still stops the app
    main()
