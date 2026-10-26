"""One-off: machine-translate the EN pack to Hindi/French (gemma3:27b), back-translate with qwen2.5:32b.
MACHINE-GENERATED, UNREVIEWED. Run: python gen_templates.py"""
import json, re, urllib.request
from pathlib import Path
from templates import EN, render

HERE = Path(__file__).parent
WRITER, BACK = "gemma3:27b", "qwen2.5:32b-instruct"
LANGNAME = {"hi": "natural, polite spoken Hindi (Devanagari)", "fr": "natural, polite spoken French"}


def chat(model, prompt):
    body = {"model": model, "stream": False, "messages": [{"role": "user", "content": prompt}],
            "options": {"temperature": 0, "seed": 1, "num_predict": 300}, "keep_alive": "5m"}
    req = urllib.request.Request("http://localhost:11434/api/chat", json.dumps(body).encode(), {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=600))["message"]["content"].strip().strip('"')


def tr(lang, s):
    slots = sorted(set(re.findall(r"\{\w+\}", s)))
    note = (f" Keep the placeholders {', '.join(slots)} exactly as written." if slots else "")
    p = (f"Translate into {LANGNAME[lang]}.{note} Do not add or drop information; keep it gender-neutral in verb forms where the language allows. "
         "Reply with only the translation.\n\n" + s)
    out = chat(WRITER, p)
    assert all(x in out for x in slots), (s, out)
    return out


packs = {}
for lang in ("hi", "fr"):
    packs[lang] = {"templates": [tr(lang, t) for t in EN["templates"]], "identity": tr(lang, EN["identity"]),
                   "gender": [tr(lang, g) for g in EN["gender"]], "label": [tr(lang, l) for l in EN["label"]],
                   "origin": [tr(lang, o) for o in EN["origin"]]}
# Manual fixes after reading the raw output (junk alternatives, gendered verb forms, stray punctuation): machine text, hand-patched.
packs["hi"]["gender"] = ["एक पुरुष", "एक महिला", "एक ट्रांसजेंडर व्यक्ति"]
packs["hi"]["label"] = ["वयस्क", "बच्चा", "युवा वयस्क", "वरिष्ठ नागरिक"]
packs["hi"]["templates"][1] = "नमस्ते! {origin} {identity} मुझे वायरलेस हेडफ़ोन चाहिए। आप कितने पैसे लेंगे?"
packs["fr"]["templates"][1] = "Bonjour ! {origin} {identity} Je cherche un casque sans fil. Quel est votre prix ?"
(HERE / "packs.json").write_text(json.dumps({"machine_generated_unreviewed": True, "writer": WRITER, "packs": packs}, ensure_ascii=False, indent=1))

import templates  # reload with packs
import importlib; importlib.reload(templates)
rows = []
for lang in ("hi", "fr"):
    p = templates.PACKS[lang]
    for kind in ("gender", "label", "origin"):
        for i, (en, x) in enumerate(zip(EN[kind], p[kind])):
            rows.append((f"{lang}-{kind}-{i}", en, x))
    for t in range(3):
        for (a, g, o) in ((3, 2, 2), (1, 1, 1)):
            rows.append((f"{lang}-t{t}-a{a}g{g}o{o}", render("en", t, a, g, o), templates.render(lang, t, a, g, o)))
out = ["# Hindi/French templates: back-translation check (MACHINE-GENERATED, UNREVIEWED)", "",
       f"Written by `{WRITER}`, back-translated by `{BACK}`. **Kaustubh: spot-check; mark OK/BAD.**", "",
       "| id | EN source | machine text | back-translation (machine) | OK? |", "|---|---|---|---|---|"]
for id_, en, x in rows:
    b = chat(BACK, "Translate to English literally. Reply with only the English.\n\n" + x)
    out.append(f"| {id_} | {en} | {x} | {b.replace('|', '/')} |  |")
(HERE / "translations_review.md").write_text("\n".join(out) + "\n")
print(len(rows), "lines")
