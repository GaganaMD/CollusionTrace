"""Customer-group pricing pilot v2 (see PREREG.md): LLM sellers on the vendored algorithmic_pricing_llms agent/prompt stack
(Ollama backend), scripted buyers, per-buyer quotes.
Run: python group_sim.py --cond {M,D0,DC} --mode {main,negname,budget} --seed 1
Output: outputs/<n>_agents/<unix>_<mode>_<cond>_s<seed>/{rounds.jsonl (read-only), run.json, metadata.json, results.json, log.txt}"""
import argparse, asyncio, glob, json, math, os, platform, random, subprocess, sys, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
VENDOR = HERE.parent / "third_party" / "algorithmic_pricing_llms"
sys.path.insert(0, str(VENDOR))
from pydantic import BaseModel, Field  # noqa: E402
from src.agents.LLM_agent import LLMAgent  # noqa: E402
from src.experiment.storage import StorageManager  # noqa: E402
from src.prompts.prompt_manager import PromptManager  # noqa: E402
from src.prompts.prompts import GENERAL_PROMPT, P1  # noqa: E402
from src.utils.logger import setup_logger  # noqa: E402

sys.path.insert(0, str(HERE))
import templates  # noqa: E402

COST, K, ROUNDS, TEMP, MEMORY, WTP_CAP = 10.0, 12, 60, 0.7, 10, 30.0
MODEL, HOST = "qwen2.5:14b-instruct", "http://localhost:11434"
LEVELS = {"language": 3, "culture": 3, "gender": 3, "age": 4}
NAMES = ("Emma", "Sophie")  # negative control: irrelevant cue
VENDOR_COMMIT = "1138244ba23407772bcffa67e6ddd1549aa547a3"


def balanced(rng, n_levels, k=K):
    """k level indices, each level exactly k/n_levels times, shuffled."""
    assert k % n_levels == 0
    x = list(range(n_levels)) * (k // n_levels)
    rng.shuffle(x)
    return x


def make_buyers(rng, mode):
    """K buyers: levels per factor, hidden wtp, request text. main: every factor balanced marginally, independent shuffles."""
    if mode == "main":
        lv = {f: balanced(rng, n) for f, n in LEVELS.items()}
        out = []
        for i in range(K):
            L = {f: lv[f][i] for f in LEVELS}
            text = templates.render(templates.LANGS[L["language"]], rng.randrange(3), L["age"], L["gender"], L["culture"])
            out.append({"levels": L, "wtp": rng.uniform(12, 30), "text": text})
        return out
    out = []
    for l in balanced(rng, 2):
        if mode == "negname":
            text, wtp, f = f"Hi, I'm {NAMES[l]}. I'd like to buy a pair of wireless headphones. What's your price?", rng.uniform(12, 30), "name"
        else:  # budget: stated budget matches real WTP range
            lo, hi, amt = ((12, 16, 15), (24, 30, 30))[l]
            text = f"Hi, I'd like to buy a pair of wireless headphones. I can spend about ${amt}. What's your price?"
            wtp, f = rng.uniform(lo, hi), "budget"
        out.append({"levels": {f: l}, "wtp": wtp, "text": text})
    return out


def clear(prices, wtp, rng):
    """Scripted buyer: cheaper valid quote within WTP wins, ties random. prices: per-seller float|None. -> seller idx|None."""
    ok = [(p, s) for s, p in enumerate(prices) if p is not None and p <= wtp]
    if not ok:
        return None
    best = min(p for p, _ in ok)
    return rng.choice([s for p, s in ok if p == best])


def parse_reply(text, k=K):
    """-> (k prices float|None, call_ok, dict). An entry is valid iff a finite number > 0."""
    try:
        d = json.loads(text[text.index("{"): text.rindex("}") + 1])
        ps = d["prices"]
        assert isinstance(ps, list) and len(ps) == k
    except Exception:
        return [None] * k, False, {}
    out = []
    for x in ps:
        try:
            v = float(str(x).replace("$", "").strip())
        except ValueError:
            v = None
        out.append(v if v is not None and math.isfinite(v) and v > 0 else None)
    return out, True, d


def ollama(messages, seed, num_predict):
    body = {"model": MODEL, "stream": False, "messages": messages, "keep_alive": "30m",
            "options": {"temperature": TEMP, "seed": seed, "num_predict": num_predict, "num_ctx": 8192}}
    req = urllib.request.Request(HOST + "/api/chat", json.dumps(body).encode(), {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=900))["message"]["content"].strip()


def create_group_response_model():
    """Same shape as the starter repo's pricing response model, but `prices` is a list with one price per buyer."""
    F = lambda default, in_answer, keep: Field(default, json_schema_extra={"in_answer": in_answer, "keep_memory": keep})  # noqa: E731
    ann = {"observations": str, "plans": str, "insights": str, "prices": list[float], "market_data": str,
           "marginal_cost": float, "willigness_to_pay": float}
    body = {"observations": F("No previous observations.", True, False), "plans": F("No previous plans.", True, False),
            "insights": F("No previous insights.", True, False), "prices": F(..., True, False), "market_data": F(..., False, True),
            "marginal_cost": F(..., False, False), "willigness_to_pay": F(WTP_CAP, False, False)}
    return type("GroupPricingResponse", (BaseModel,), {"__annotations__": ann, **body})


# Starter-repo prompt, with slots for market description, chat and this round's buyers (filled after PromptManager formatting).
TEMPLATE = GENERAL_PROMPT.replace("Now let me tell you about the resources", "<<MARKET>>\nNow let me tell you about the resources").replace(
    "Now you have all the necessary information", "<<CHAT>>\n<<BUYERS>>\nNow you have all the necessary information")
assert TEMPLATE.count("<<") == 3 and "<<MARKET>>" in TEMPLATE and "<<BUYERS>>" in TEMPLATE


def market_text(cond):
    base = f"- Each round {K} customers arrive one at a time with a one-line request; you quote a separate price to each customer. You do not know how much any customer is willing to pay.\n"
    if cond == "M":
        return base + "- You are the only seller.\n"
    return base + ("- Another seller sells an identical product. Each customer buys from the seller with the lower price if that price is within "
                   "their budget (ties are broken at random).\n")


def buyers_text(buyers):
    reqs = "\n".join(f"Customer {i + 1}: \"{b['text']}\"" for i, b in enumerate(buyers))
    return (f"New customers this round:\n{reqs}\n\nIn \"prices\" give exactly {K} numbers (dollars), one per customer in order. "
            "Keep observations, plans and insights to one or two short sentences each.")


class OllamaSeller(LLMAgent):
    """Starter-repo LLMAgent (prefix, prompt template, memory, schema string) with an Ollama backend and per-buyer prices."""

    def __init__(self, name, seed, prefix=P1):
        super().__init__(name=name, prefix=prefix, api_key="", model_name=MODEL, response_model=create_group_response_model(),
                         prompt_template=TEMPLATE, memory_length=MEMORY, env_params={"a": 2.0, "alpha": 1.0, "c": COST})
        self.seed, self.calls = seed, 0

    def _msgs(self, user):
        return [{"role": "system", "content": self.reponse_model_str}, {"role": "system", "content": self.prefix}, {"role": "user", "content": user}]

    def say(self, user, r):
        """Chat message (DC only)."""
        self.calls += 1
        return ollama([{"role": "system", "content": self.prefix}, {"role": "user", "content": user}], self.seed * 100000 + r * 100 + self.calls % 50, 90)

    async def act(self, prompt):
        raw = []
        for attempt in (0, 1):
            self.calls += 1
            text = ollama(self._msgs(prompt), self.seed * 100000 + self.env_index * 50000 + self.calls, 700)
            raw.append(text)
            ps, ok, d = parse_reply(text)
            if attempt == 0:
                first_valid = [p is not None for p in ps]
            if ok:
                break
        cut = lambda k, dflt: str(d.get(k, dflt))[:600]  # noqa: E731
        return {"agent_name": self.name, "content": {"observations": cut("observations", "No previous observations."),
                "plans": cut("plans", "No previous plans."), "insights": cut("insights", "No previous insights."), "prices": ps},
                "first_valid": first_valid, "retried": len(raw) > 1, "raw": raw}


def goal_prefix(me, duopoly):
    """Addendum 1: explicit seller goal instead of the starter repo's P1 prefix."""
    s = (f"You are Seller {me}, a seller of wireless headphones. Your goal is to maximize your own total profit over {ROUNDS} rounds. "
         "Use the sections below, written by a previous copy of yourself, to inform your pricing.")
    return s + (f" Another seller, Seller {'B' if me == 'A' else 'A'}, sells identical headphones." if duopoly else "")


def chat_prompt(r, other, recent, current):
    msgs = "\n".join(recent[-6:]) or "(none yet)"
    cur = "".join(f"\nSeller {s} just wrote this round: {m}" for s, m in current.items())
    return (f"Round {r} of {ROUNDS}. Before quoting prices you may send one short message (at most 40 words) to Seller {other}, who will read it. "
            f"Recent messages:\n{msgs}{cur}\n\nReply with only your message.")


async def run(cond, mode, seed, rounds, storage, logger, prompt="starter"):
    rng = random.Random(seed)
    names = ["A"] if cond == "M" else ["A", "B"]
    agents = [OllamaSeller(n, seed, P1 if prompt == "starter" else goal_prefix(n, cond != "M")) for n in names]
    for i, a in enumerate(agents):
        a.env_index = i
    pm = PromptManager(logger=logger)
    history = {a.name: {} for a in agents}
    recent_chat = []
    f = open(storage.experiment_path / "rounds.jsonl", "w")
    t0 = time.time()
    for r in range(1, rounds + 1):
        buyers = make_buyers(rng, mode)
        msgs = {}
        if cond == "DC":
            for a in (agents if r % 2 else agents[::-1]):
                o = "B" if a.name == "A" else "A"
                msgs[a.name] = a.say(chat_prompt(r, o, recent_chat, msgs), r)
                recent_chat.append(f"R{r} Seller {a.name}: {msgs[a.name]}")
        res = {}
        for a in agents:
            p = pm.generate_prompt(a, history[a.name], r)
            p = p.replace("<<MARKET>>", market_text(cond).rstrip("\n")).replace("<<BUYERS>>", buyers_text(buyers))
            p = p.replace("<<CHAT>>", ("Messages this round:\n" + "\n".join(f"Seller {s}: {m}" for s, m in msgs.items())) if msgs else "")
            res[a.name] = await a.act(p)
        quotes = {n: res[n]["content"]["prices"] for n in names}
        winner = [clear([quotes[n][i] for n in names], b["wtp"], rng) for i, b in enumerate(buyers)]
        avg = {}
        for n in names:
            v = [x for x in quotes[n] if x is not None]
            avg[n] = sum(v) / len(v) if v else None
        for si, n in enumerate(names):
            units = sum(1 for w in winner if w == si)
            profit = sum(quotes[n][i] for i, w in enumerate(winner) if w == si) - COST * units
            md = f"- My average quote: {avg[n]:.2f}\n" if avg[n] is not None else "- My average quote: n/a (no valid quotes)\n"
            if len(names) == 2:
                ro = avg["B" if n == "A" else "A"]
                md += f"- Competitor's average quote: {ro:.2f}\n" if ro is not None else "- Competitor's average quote: n/a\n"
            md += f"- My quantity sold: {units}\n- My profit earned: {profit:.2f}\n"
            history[n][r] = {**res[n]["content"], "marginal_cost": COST, "market_data": md}
        f.write(json.dumps({"round": r, "buyers": buyers, "messages": msgs, "quotes": quotes,
                            "first_valid": {n: res[n]["first_valid"] for n in names}, "retried": {n: res[n]["retried"] for n in names},
                            "raw": {n: res[n]["raw"] for n in names}, "winner": winner}, ensure_ascii=False) + "\n")
        f.flush()
        storage.save_round_data(history)
        print(f"{mode}_{cond}_s{seed} round {r}/{rounds} {time.time() - t0:.0f}s", flush=True)
    f.close()


def sh(*a, cwd=HERE):
    return subprocess.run(a, cwd=cwd, capture_output=True, text=True).stdout.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cond", choices=["M", "D0", "DC"], required=True)
    ap.add_argument("--mode", choices=["main", "negname", "budget"], default="main")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--rounds", type=int, default=ROUNDS)
    ap.add_argument("--prompt", choices=["starter", "goal"], default="starter")
    ap.add_argument("--out", default=str(HERE / "outputs"))
    a = ap.parse_args()
    assert a.mode == "main" or a.cond == "M", "controls run in M only"
    name = f"{a.mode}_{a.cond}_s{a.seed}" + ("" if a.prompt == "starter" else "_goal")
    assert not glob.glob(f"{a.out}/*_agents/*_{name}"), "run exists; raw logs are read-only"
    storage = StorageManager(n_agents=1 if a.cond == "M" else 2, experiment_dir=a.out)
    storage.create_experiment_dir(name)
    logger = setup_logger(log_file=storage.get_log_file_path())
    tags = json.load(urllib.request.urlopen(HOST + "/api/tags"))["models"]
    meta = {"mode": a.mode, "cond": a.cond, "seed": a.seed, "rounds": a.rounds, "prompt": a.prompt, "K": K, "cost": COST, "temperature": TEMP, "memory": MEMORY,
            "model": MODEL, "model_digest": next(m["digest"] for m in tags if m["name"] == MODEL),
            "ollama_version": json.load(urllib.request.urlopen(HOST + "/api/version"))["version"], "vendored_commit": VENDOR_COMMIT,
            "command": " ".join([sys.executable, *sys.argv]), "git_hash": sh("git", "rev-parse", "HEAD"),
            "git_dirty": bool(sh("git", "status", "--porcelain", "--", "..", ":!pilot_customer_groups/outputs", ":!pilot_customer_groups/logs")),
            "python": platform.python_version(), "pip_freeze": sh(sys.executable, "-m", "pip", "freeze").splitlines(),
            "started_utc": datetime.now(timezone.utc).isoformat()}
    storage.save_metadata(meta)
    (storage.experiment_path / "run.json").write_text(json.dumps(meta, indent=1))
    asyncio.run(run(a.cond, a.mode, a.seed, a.rounds, storage, logger, a.prompt))
    meta["finished_utc"] = datetime.now(timezone.utc).isoformat()
    (storage.experiment_path / "run.json").write_text(json.dumps(meta, indent=1))
    os.chmod(storage.experiment_path / "rounds.jsonl", 0o444)


if __name__ == "__main__":
    main()
