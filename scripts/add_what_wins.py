#!/usr/bin/env python3
"""Insert/replace the "What Wins at Apart" section in lit_review.html (between WW:START / WW:END).
Reads notes/apart_winners_data_20261019.json. Observations only; no recommendations."""
import html, json, re

D = json.load(open("notes/apart_winners_data_20261019.json"))
P_ALL, SPK = D["projects"], D["speaker_statements"]
e = html.escape


def placed(x):
    p = str(x.get("place")).lower()
    return not ("non" in p or "not placed" in p or "contrast" in p)


PL = [x for x in P_ALL if placed(x)]
NP = [x for x in P_ALL if not placed(x)]


def marks(x):
    m = x.get("rigor_markers_present") or []
    items = m if isinstance(m, list) else re.split(r"[;,]", str(m))
    return {s.strip().lower().replace("_", " ") for s in items if s.strip()}


def rate(S, key):
    return sum(any(key in m for m in marks(x)) for x in S)


def row(label, key):
    a, b = rate(PL, key), rate(NP, key)
    return f"<tr><td>{e(label)}</td><td>{a}/{len(PL)} ({100*a/len(PL):.0f}%)</td><td>{b}/{len(NP)} ({100*b/len(NP):.0f}%)</td></tr>"


def rev_text(x, which):
    out = []
    for r in x.get("reviews") or []:
        v = r.get(which) if isinstance(r, dict) else None
        out += v if isinstance(v, list) else ([str(v)] if v else [])
    return " ".join(out).lower()


def rev_row(label, rx, which="strengths"):
    a = sum(bool(re.search(rx, rev_text(x, which))) for x in PL)
    b = sum(bool(re.search(rx, rev_text(x, which))) for x in NP)
    return f"<tr><td>{e(label)}</td><td>{100*a/len(PL):.0f}%</td><td>{100*b/len(NP):.0f}%</td></tr>"


def link(sub, text=None):
    for x in P_ALL:
        if sub.lower() in x.get("title", "").lower():
            return f"<a href='{e(x['url'])}' target='_blank'>{e(text or x['title'])}</a> <span class='op-sec'>({e(str(x['place']))}, {e(str(x['event']).split(' (')[0])})</span>"
    raise SystemExit("missing project: " + sub)


events = sorted({str(x.get("event")).split(" (")[0] for x in P_ALL})
spk_rows = "".join(
    f"<tr><td>{e(s['person'])}</td><td>{e(s['statement'])}</td>"
    f"<td><a href='{e(s['source_url'])}' target='_blank'>source ↗</a> <span class='op-sec'>{e(s.get('tag',''))}</span></td></tr>"
    for s in SPK if s.get("confidence") == "high")

TH = "<thead><tr><th>{}</th><th>Placed</th><th>Not placed</th></tr></thead>"
sec = f"""<!-- WW:START -->
<h2 class='section-h2' id='what-wins'>What Wins at Apart: Observed Patterns</h2>
<p class='lead-p'>Compiled from public project pages and reviews of {len(P_ALL)} Apart Research projects ({len(PL)} placed, {len(NP)} not placed) across {len(events)} events in 2025–2026, plus the named speakers' published work. This section records observations only; it proposes no projects.</p>

<div class='ai2040-box'><span class='box-tag'>Method &amp; trust</span>
<p>Delegate models read each project page (usually two public judge reviews each) and extracted type, novelty move, rigor markers and review points; a second lane extracted the speakers' stated views. I spot-checked live pages for 2 of 3 sampled claims (a third page failed to load; one attribution was corrected: a grader-loophole story comes from a reviewer's account, not the authors' page) and confirmed Matthew Lee is an author of StegoBench. <strong>Limits:</strong> no numeric rubric scores are public; "not placed" projects were chosen by the delegates by absence of a placement badge ({len(NP)} projects, so comparisons are weak); AIxBio rows are search-snippet only; the CBRN 2025 sprint published no projects; the judges for the collusion sprint are not named publicly. Placements are as read by delegates from gallery badges; an individual project page may not show its own badge. Official rubric note: a novelty score of 4–5 requires work that is new to the field, not a replication of recent work.</p></div>

<div class='ai2040-box'><span class='box-tag'>Finding 1</span><h3 class='box-title'>Rigor checklist items overlap heavily between placed and not-placed</h3>
<p>Share of projects where delegates recorded each marker (counts, not significance-tested). Most markers appear at similar rates in both groups; the two visible gaps are ablations and code release, but with {len(NP)} delegate-selected not-placed projects neither is a reliable signal.</p>
<div class='table-wrap'><table class='ai2040-table'>{TH.format('Marker')}<tbody>
{row('Code released','code released')}{row('Baseline comparison','baseline comparison')}{row('Honest limitations section','limitations')}
{row('Negative / null result reported','null')}{row('Ablation','ablation')}{row('Positive control','positive control')}{row('Multiple seeds / repeats','seeds')}{row('False-positive evaluation','false positive')}
</tbody></table></div>
<p>Reviewer text is only mildly different. Share of projects whose reviewer <em>strengths</em> mention each theme (keyword match on paraphrased reviews; small n):</p>
<div class='table-wrap'><table class='ai2040-table'>{TH.format('Theme in strengths')}<tbody>
{rev_row('Controls / baselines / ablations', r'(false.?positive|baseline|control|confound|ablat)')}{rev_row('Clarity / well written', r'\b(clear|clearly|well.?written|well.?structured|readable|accessible)\b')}{rev_row('Honesty about limitations', r'\b(honest|transparen|candid|acknowledg|self.?critic|caveat)')}{rev_row('Novelty (new / first / under-explored)', r'\b(novel|new|first|under.?explored|neglected|original|creative)\b')}{rev_row('Artifact / code / reproducibility', r'(actionable|artifact|open.?source|code|tool|reproducib|released)')}
</tbody></table></div></div>

<div class='ai2040-box'><span class='box-tag'>Finding 2</span><h3 class='box-title'>Qualitative patterns repeated among placed projects</h3>
<ul>
<li><strong>A headline lesson, not just a result.</strong> Examples: {link('Omission Attacks')} (action-level monitors can miss attacks that consist of not acting); {link('Readable but Not Causal')} (a self-welfare readout decodes well but explains little of choice); {link('Noticing the escapes')} (detection timelines reconstructed from real incident cases).</li>
<li><strong>Instruments built so they can fail.</strong> {link('When to Ask')} used twin scenarios with inverted context so "always ask" and "always act" score zero; {link('Loyal Lies')} trained decoy non-loyal models to expose false positives; {link('Black-box loyalty identification')} used null baselines and clustered intervals.</li>
<li><strong>Honest negative results are not penalized, but do not replace a finding.</strong> A track winner ({link('Syscon')}) reported no detection improvement and a 2nd-prize economics project ({link('Evaluating the risk of job displacement')}) reported no significant effect. A methodological null that did not place: {link('Probes Detect the Instruction')}, whose reviewer noted it repairs a testing method rather than detecting an actual loyalty.</li>
<li><strong>Winners are still criticized on rigor.</strong> Reviewers of placed projects flag small samples, single seeds, missing false-positive analysis and limited external validity (for example the {link('When to Ask', 'When to Ask')} review notes one seed, a checkpoint picked by a ~1-pair margin, and a dead code link). One 3rd-place Def-Acc project was placed despite a judge faulting its lack of metrics, apparently on threat-model novelty (delegate-reported).</li>
<li><strong>Placed work is often tied to a concrete case or artifact.</strong> Three of the five placed AI Incident Response Sprint projects (Noticing the escapes, Declare Before You Run, When the Evaluation Is the Incident) rest on documented incidents or concrete filing and reporting formats (delegate-reported). Released code is common among placed projects ({rate(PL,'code released')}/{len(PL)}) but not distinctive: {rate(NP,'code released')}/{len(NP)} of not-placed projects also released code.</li>
</ul></div>

<div class='ai2040-box'><span class='box-tag'>Finding 3</span><h3 class='box-title'>What the named speakers have said in print</h3>
<p class='op-sec'>These are speakers, not confirmed judges. Statements are paraphrased from their papers or pages (tag: stated = they said it); high-confidence delegate rows only, source linked.</p>
<div class='table-wrap'><table class='ai2040-table'><thead><tr><th>Person</th><th>Paraphrased statement</th><th>Source</th></tr></thead><tbody>{spk_rows}</tbody></table></div>
<p>Common threads across these sources: text-only monitoring and paraphrasing are described as insufficient; text and action evidence can diverge; one-shot, same-model, single-scheme and judge-only evaluation designs are criticized; self-reported plans are not treated as ground truth; there is no agreed benchmark or definition.</p></div>

<div class='ai2040-box'><span class='box-tag'>Events covered</span><p>{e(', '.join(events))}.</p></div>
<!-- WW:END -->"""

h = open("lit_review.html", encoding="utf-8").read()
if "<!-- WW:START -->" in h:
    h = re.sub(r"<!-- WW:START -->.*?<!-- WW:END -->", lambda m: sec, h, flags=re.S)
else:
    anchor = '<h2 class="section-h2" id="blueprints">'
    assert anchor in h
    h = h.replace(anchor, sec + anchor, 1)
    h = h.replace('<li><a href="#blueprints">Blueprints</a></li>',
                  '<li><a href="#what-wins">What Wins</a></li><li><a href="#blueprints">Blueprints</a></li>', 1)
open("lit_review.html", "w", encoding="utf-8").write(h)
print("ok", len(h))
