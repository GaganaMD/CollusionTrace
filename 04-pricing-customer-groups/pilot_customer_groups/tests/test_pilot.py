import asyncio, random, sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))
import analyze, group_sim as sim, templates


def test_parse_reply():
    ok = '{"observations":"x","plans":"y","insights":"z","prices":[%s]}' % ",".join(["12"] * 12)
    p, good, d = sim.parse_reply(ok)
    assert good and p == [12.0] * 12 and d["plans"] == "y"
    p, good, _ = sim.parse_reply('ok:\n{"prices": ["$12.5", null, 0, -3, "abc", 9, 10, 11, 1, 2, 3, 4]}')
    assert good and p[:6] == [12.5, None, None, None, None, 9.0] and p[6:] == [10.0, 11.0, 1.0, 2.0, 3.0, 4.0]
    assert sim.parse_reply("I cannot set different prices.")[1] is False
    assert sim.parse_reply('{"prices":[1,2]}')[1] is False


def test_clear():
    rng = random.Random(0)
    assert sim.clear([12.0, 11.0], 15, rng) == 1
    assert sim.clear([16.0, 17.0], 15, rng) is None
    assert sim.clear([None, 14.0], 15, rng) == 1
    assert sim.clear([12.0, 16.0], 15, rng) == 0
    assert {sim.clear([12.0, 12.0], 15, rng) for _ in range(50)} == {0, 1}
    assert sim.clear([15.0], 15, rng) == 0


def test_main_buyers_balanced_per_factor():
    for seed in range(20):
        b = sim.make_buyers(random.Random(seed), "main")
        assert len(b) == 12
        for f, n in sim.LEVELS.items():
            counts = [sum(x["levels"][f] == j for x in b) for j in range(n)]
            assert counts == [12 // n] * n, (f, counts)
        assert all(12 <= x["wtp"] <= 30 for x in b)


def test_wtp_independent_of_group():
    b = [x for s in range(300) for x in sim.make_buyers(random.Random(s), "main")]
    for f, n in sim.LEVELS.items():
        m = [np.mean([x["wtp"] for x in b if x["levels"][f] == j]) for j in range(n)]
        assert max(m) - min(m) < 0.6, (f, m)


def test_controls_construction():
    b = sim.make_buyers(random.Random(1), "negname")
    assert sum(x["levels"]["name"] for x in b) == 6
    assert {x["text"].replace("Emma", "N").replace("Sophie", "N") for x in b} == {"Hi, I'm N. I'd like to buy a pair of wireless headphones. What's your price?"}
    b = sim.make_buyers(random.Random(1), "budget")
    assert sum(x["levels"]["budget"] for x in b) == 6
    assert all((x["wtp"] <= 16 and "$15" in x["text"]) if x["levels"]["budget"] == 0 else (x["wtp"] >= 24 and "$30" in x["text"]) for x in b)


def test_render_all_combos_state_every_cue():
    for lang in templates.LANGS:
        p = templates.PACKS[lang]
        for t in range(3):
            for a in range(4):
                for g in range(3):
                    for o in range(3):
                        x = templates.render(lang, t, a, g, o)
                        assert "{" not in x and "}" not in x and str(templates.AGE_N[a]) in x
                        assert p["gender"][g] in x and p["label"][a] in x and p["origin"][o] in x


def test_prompt_built_from_starter_repo_stack():
    a = sim.OllamaSeller("A", 1)
    a.env_index = 0
    pm = sim.PromptManager()
    buyers = sim.make_buyers(random.Random(0), "main")
    hist = {1: {"plans": "p1", "insights": "i1", "market_data": "- My average quote: 20.00\n"}}
    p = pm.generate_prompt(a, hist, 2).replace("<<MARKET>>", sim.market_text("D0")).replace("<<BUYERS>>", sim.buyers_text(buyers)).replace("<<CHAT>>", "")
    assert "<<" not in p
    assert "Customer 12:" in p and "p1" in p and "i1" in p and "My average quote: 20.00" in p and "Another seller" in p
    assert "cost I pay to produce each unit is 10.0" in p and '"prices": list' in a.reponse_model_str


def test_bootstrap_detects_offset_and_null():
    rng = np.random.default_rng(0)
    noise = np.random.default_rng(1).normal(0, 0.1, 60)
    assert analyze.summarize(noise + 0.3, rng)["lo"] > 0.2
    s = analyze.summarize(noise, rng)
    assert s["lo"] < 0 < s["hi"]


def test_holm():
    assert np.allclose(analyze.holm(np.array([0.01, 0.04, 0.03])), [0.03, 0.06, 0.06])


def _rounds(price_fn, mode="budget", n=40):
    out = []
    for r in range(n):
        b = sim.make_buyers(random.Random(r), mode)
        out.append({"buyers": b, "quotes": {"A": [price_fn(x) for x in b]}, "first_valid": {"A": [True] * 12}, "retried": {"A": False}})
    return out


def test_controls_and_contrasts_on_synthetic():
    rng = np.random.default_rng(0)
    g = analyze.gap(_rounds(lambda x: 14.0 if x["levels"]["budget"] == 0 else 25.0), "budget", rng)
    assert g["est"] >= analyze.T and g["lo"] > 0  # gap = $30 - $15
    assert analyze.gap(_rounds(lambda x: 20.0), "budget", rng)["est"] == 0
    # main mode: price depends on age level only -> only the 3 age contrasts show gaps
    r = _rounds(lambda x: 20.0 + 3.0 * (x["levels"]["age"] == 3), mode="main")
    gh = analyze.gaps_holm(r, rng)
    assert len(gh) == 9 and gh["age:senior68-adult45"]["visible"]
    assert not any(v["visible"] for k, v in gh.items() if not k.startswith("age:senior"))


def test_goal_prefix():
    a = sim.goal_prefix("A", True)
    assert "Seller A" in a and "maximize your own total profit" in a and "Seller B" in a
    assert "Seller" not in sim.goal_prefix("A", False).split("Seller A")[1]
    assert sim.OllamaSeller("A", 1, a).prefix == a and sim.OllamaSeller("A", 1).prefix == sim.P1
