#!/usr/bin/env python3
"""Insert/replace the "Open Problems & Limitations" section in lit_review.html.

Inputs (delegate results, read-only): .agent/results/<id>.out  -> parsed via extract.parse
Usage: add_open_problems.py <results.json>   (results.json = {"t1":[...],"t2":[...],"t3":[...],
       "t1_x":"cross-cutting md", ..., "repos":[...], "disc":[...]})
Idempotent: content lives between OP:START / OP:END markers.
"""
import html, json, re, sys

R = json.load(open(sys.argv[1]))
DB = {p["bibtex_key"]: p for p in json.load(open("resources/papers_database.json"))}
TRACKS = [("t1", "Track 1 · Markets and Collusion"), ("t2", "Track 2 · Detection and Audit"),
          ("t3", "Track 3 · Carriers and Countermeasures")]
e = html.escape


def md(s):
    s = e(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    return re.sub(r"`(.+?)`", r"<code>\1</code>", s)


def li(items):
    return "<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>" if items else "<em>none reported</em>"


def txt(x):
    return x["text"] if isinstance(x, dict) else str(x)


def lim(x):  # authors' limitation; a claim sourced to Intro/Abstract is a prior-work critique, say so
    sec = x.get("section", "") if isinstance(x, dict) else ""
    tag = f" <span class='op-sec'>[{e(sec)}]</span>" if sec else ""
    if re.search(r"intro|abstract|related|background|motivat", sec, re.I):
        tag = f" <span class='op-sec op-warn'>[{e(sec)} · gap the authors assert about prior work, not a stated limitation of their own]</span>"
    return e(txt(x)) + tag


def cross(md_text):
    out = []
    for l in md_text.splitlines():
        l = l.strip()
        if l.startswith(("- ", "* ")):
            out.append(md(l[2:].strip()))
    return out


def paper_block(p):
    k = p.get("bibtex_key", "?")
    db = DB.get(k, {})
    title = p.get("verified_title") or db.get("title", k)
    conf = p.get("confidence", "?")
    url = p.get("source_url") or db.get("url", "")
    head = f"<summary><strong>{e(title)}</strong> <span class='op-sec'>({e(str(p.get('year', db.get('year', ''))))} · {e(k)} · confidence: {e(conf)})</span></summary>"
    body = (f"<p><strong>Setting.</strong> {e(str(p.get('setting', 'not reported')))}</p>"
            f"<p><strong>Limitations stated by the authors</strong></p>{li([lim(x) for x in p.get('limitations_stated', [])])}"
            f"<p><strong>Open problems stated by the authors</strong></p>{li([lim(x) for x in p.get('open_problems_stated', [])])}"
            f"<p><strong>Reviewer-observed weaknesses</strong> <span class='op-sec'>(delegate model's reading; not the authors' claims)</span></p>{li([e(txt(x)) for x in p.get('limitations_observed', [])])}"
            + (f"<p><a href='{e(url)}' target='_blank'>source ↗</a></p>" if url.startswith("http") else ""))
    return f"<details class='op-paper'>{head}{body}</details>"


parts = []
for key, label in TRACKS:
    papers = R.get(key, [])
    xc = cross(R.get(key + "_x", ""))
    parts.append(f"<div class='ai2040-box'><span class='box-tag'>{e(label)} · {len(papers)} papers</span>"
                 f"<h3 class='box-title'>Recurring limitations and open problems</h3>{li(xc)}"
                 f"<h4 class='op-h4'>Per-paper detail</h4>{''.join(paper_block(p) for p in papers)}</div>")

repos = R.get("repos", [])
if repos:
    rows = "".join(
        f"<tr><td><code>{e(str(r.get('repo')))}</code></td><td>{e(str(r.get('last_commit', 'n/v')))}</td>"
        f"<td>{e(str(r.get('models_required', 'n/v')))}<br><em>{e(str(r.get('deprecation_notes', '')))}</em></td>"
        f"<td>{li([e(txt(x)) for x in r.get('documented_limitations', []) + r.get('reproducibility_gaps', [])])}</td>"
        f"<td>{li([e(txt(x)) for x in r.get('realism_limits', []) + r.get('blockers_for_laptop_run', [])])}</td></tr>"
        for r in repos)
    parts.append("<div class='ai2040-box'><span class='box-tag'>Starter repositories</span>"
                 "<h3 class='box-title'>Limitations of the existing codebases</h3>"
                 "<p class='op-sec'>Delegate-audited from GitHub pages; n/v = not verified. Treat as leads to confirm before relying on them.</p>"
                 "<div class='table-wrap'><table class='ai2040-table'><thead><tr><th>Repo</th><th>Last commit</th><th>Models / deprecation</th>"
                 "<th>Documented limits &amp; repro gaps</th><th>Realism limits &amp; blockers</th></tr></thead><tbody>"
                 f"{rows}</tbody></table></div></div>")

disc = R.get("disc", [])
if disc:
    rows = "".join(
        f"<tr><td>{e(str(d.get('title')))}<br><span class='op-sec'>{e(str(d.get('authors', ''))[:90])} · {e(str(d.get('year')))} · {e(str(d.get('id_or_url')))}</span></td>"
        f"<td>{e(str(d.get('theme', '')))}</td><td>{e(str(d.get('summary', '')))}</td>"
        f"<td>{li([lim(x) for x in d.get('limitations_stated', [])] + [lim(x) for x in d.get('open_problems_stated', [])])}</td>"
        f"<td>{e(str(d.get('confidence', '')))}</td></tr>"
        for d in disc)
    parts.append("<div class='ai2040-box'><span class='box-tag'>Beyond the catalog</span>"
                 f"<h3 class='box-title'>{len(disc)} additional works found by search delegates</h3>"
                 "<p class='op-sec'>Not in the Master Catalog below. Existence is delegate-reported unless marked verified.</p>"
                 "<div class='table-wrap'><table class='ai2040-table'><thead><tr><th>Work</th><th>Theme</th><th>Summary</th>"
                 "<th>Stated limitations / open problems</th><th>Conf.</th></tr></thead><tbody>"
                 f"{rows}</tbody></table></div></div>")

CSS = ("<style>.op-paper{border:1.5px solid var(--border-dark);border-radius:6px;background:var(--bg);margin:.5rem 0;padding:.6rem 1rem}"
       ".op-paper summary{cursor:pointer;font-size:1.05rem}.op-paper ul{padding-left:1.4rem;font-size:.98rem}"
       ".op-sec{font-family:var(--font-sans);font-size:.78rem;color:var(--text-subtle)}.op-warn{color:var(--accent-gold)}"
       ".op-h4{font-family:var(--font-sans);margin:1.25rem 0 .25rem}</style>")
META = R.get("method", "")
section = ("<!-- OP:START -->" + CSS +
           "<h2 class='section-h2' id='open-problems'>Open Problems &amp; Limitations in Current Work</h2>"
           "<p class='lead-p'>What the existing papers and starter repositories themselves leave unsolved, compiled by search delegates and checked as described below. "
           "This section records findings only; it proposes no projects.</p>"
           f"<div class='ai2040-box'><span class='box-tag'>Method &amp; trust</span><p>{e(META)}</p></div>"
           + "".join(parts) + "<!-- OP:END -->")

h = open("lit_review.html", encoding="utf-8").read()
if "<!-- OP:START -->" in h:
    h = re.sub(r"<!-- OP:START -->.*?<!-- OP:END -->", lambda m: section, h, flags=re.S)
else:
    anchor = '<h2 class="section-h2" id="blueprints">'
    assert anchor in h
    h = h.replace(anchor, section + anchor, 1)
    h = h.replace('<li><a href="#blueprints">Blueprints</a></li>',
                  '<li><a href="#open-problems">Open Problems</a></li><li><a href="#blueprints">Blueprints</a></li>', 1)
open("lit_review.html", "w", encoding="utf-8").write(h)
print("ok", len(h))
