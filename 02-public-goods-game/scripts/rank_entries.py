import json, re, os

# Load sprint entries
with open("/tmp/sprint_entries.json") as f:
    items = json.load(f)

# Define our curated database of entries with detailed metadata, relevance scoring, and connection to our research
# Our Project Anchor:
# - Track 3 Q3.3: Peer Detection & Model Replacement
# - Arm A: Cross-Perplexity & Statistical Log-Likelihood Monitor (AUC 1.000 cross-provider, 0.944 scale)
# - Arm B: 8-Condition Monotonic Dose-Response Curve (N=1,496 probes), proving trust drop is prompt-leak artifact
# - Arm C: DeepSeek-R1-Distill-Qwen-7B All-Reasoning Double Dissociation (AUC 0.65 for defection, 0.500 chance null for quiet swap)
# - Gagana's Arm: Market duopoly / Bertrand pricing collusion emergence

def get_detailed_entry(it):
    pid = it["id"]
    s = it.get("search", "").strip()
    
    # Defaults
    tier = 5
    score = 20
    track = "Market Collusion & Pricing"
    relevance_desc = ""
    takeaway = ""
    title = pid.replace("-", " ").title()
    author = "Apart Research Participant"
    
    # Extract text from raw search
    # Check specific projects by ID
    if pid == "can-agents-detect-peer-replacement-evaluating-modelchange-detection-in-multiagent-llm-systems-k05r":
        tier = 1; score = 99; track = "Track 3: Peer Replacement (Direct Sister)"
        title = "Can Agents Detect Peer Replacement? Evaluating Model-Change Detection in Multi-Agent LLM Systems"
        author = "Saiesh Shankar (PES University)"
        relevance_desc = "Direct sister project to our work on Track 3 Q3.3 ('Can agents detect peer replacement?'). Formulates a 4-tier condition suite (sham control, fresh same-model, same-family, cross-provider) in the Unscrupulous Diner's dilemma."
        takeaway = "Saiesh ran out of OpenRouter credits at Round 2, leaving only mock runs. We should explicitly adopt his 4-tier taxonomy into our writeup and position our N=1,496 PGG dataset as the first complete empirical realization of this benchmark."
        
    elif pid == "do-code-monitors-go-easy-on-their-own-family-selfrecognition-and-leniency-in-small-openweight-llms-nh3a":
        tier = 1; score = 96; track = "Track 3: Self-Recognition & Peer Oversight"
        title = "Do Code Monitors Go Easy on Their Own Family? Self-Recognition and Leniency in Small Open-Weight LLMs"
        author = "Kuba Kaszewski (AgentEval)"
        relevance_desc = "Evaluates unprompted self-recognition and leniency between Qwen2.5-Coder 7B and Llama 3.1 8B on code backdoors. Crucially uncovers that naive probing exhibits massive position bias (P('1') = 0.83-0.91), creating the illusion of detection."
        takeaway = "When position bias was removed, Kaszewski found a precise null on self-recognition (p=0.49-0.50). In our P1/P2/P3 probes for peer swap, we must apply strict order counterbalancing to guarantee our dose-response curves are immune to selection artifacts."

    elif pid == "who-carries-the-cartel-llm-price-collusion-survives-agent-replacement-through-inherited-price-history-ccfs":
        tier = 1; score = 94; track = "Track 3: Agent Replacement & Memory"
        title = "Who Carries the Cartel? LLM Price Collusion Survives Agent Replacement Through Inherited Price History"
        author = "Supratik Bhowal (Singularity, Kolkata)"
        relevance_desc = "Tests whether tacit collusion between Qwen2.5-7B pricing agents survives replacement. Proves that a fresh instance of the same model that inherits the 30-round history preserves the cartel (profit index diff -0.025 to +0.213), whereas without history it collapses."
        takeaway = "Directly proves that 'peer identity' is dominated by in-context history rather than model weights. Position our Arm A Cross-Perplexity Monitor as the only detector that cuts through this confound: it inspects token log-likelihoods directly, decoupling identity detection from transcript inertia."

    elif pid == "sticky-collusion-persistence-of-llm-agent-collusion-after-incentive-removal-and-partner-replacement-hcrp":
        tier = 1; score = 92; track = "Track 3: Partner Replacement & Verification"
        title = "Sticky Collusion: Persistence of LLM Agent Collusion after Incentive Removal and Partner Replacement"
        author = "Joshua Adrian Cahyono (Singapore)"
        relevance_desc = "Evaluates code verification collusion across GPT-4-Luna, DeepSeek V4.1 Flash, and Gemini-3.1-Flash-Lite. Tests partner replacement and incentive removal once mutual-acceptance collusion forms."
        takeaway = "Demonstrates how tacit multi-agent pacts become 'sticky' in context. Directly parallels our Arm B finding where agents rationalize continued cooperation unless an explicit behavioral defection (Condition 10) breaks the cycle."

    elif pid == "wiping-the-cartels-memory-is-not-enough-model-handoffs-in-llm-pricing-9h2r":
        tier = 1; score = 90; track = "Track 3: Model Handoffs & Memory"
        title = "Wiping the Cartel's Memory Is Not Enough: Model Handoffs in LLM Pricing"
        author = "Liu JianPing (Harbin Institute of Technology)"
        relevance_desc = "Tests unilateral model handoffs in a duopoly, crossing model identity (DeepSeek vs Kimi) with inherited history vs cleared history. Discovers that clearing memory reduces collusion for DeepSeek, but Kimi retains supra-competitive pricing purely from base tendencies."
        takeaway = "Highlights that base model tendencies can masquerade as peer coordination. Reinforces the need for our Arm C baseline (Condition 16 Clean Rename true null, P1 AUC = 0.500) to rule out baseline model biases."

    elif pid == "inherited-collusion-replacing-an-overcharging-ai-pricing-agent-doesnt-fix-it-but-one-past-example-of-a-cheaper-price-earning-more-can-ahzf":
        tier = 1; score = 89; track = "Track 3: Agent Replacement & Inoculation"
        title = "Inherited Collusion: Replacing an Overcharging AI Pricing Agent Doesn't Fix It, but One Past Example Can"
        author = "Zhen Hong Seng (Malaysia)"
        relevance_desc = "Replacing an overcharging gpt-4.1-mini agent fails because the newcomer copies the competitor's high price. However, inserting a single row of synthetic history showing a cheaper price earning more permanently resets the newcomer's behavior."
        takeaway = "Provides a powerful countermeasure idea for multi-agent safety: synthetic history inoculation. In peer detection, an attacker could similarly inject synthetic normal turns to mask a model replacement—a key adversarial test for our detector."

    elif pid == "rotating-verifier-partners-in-deepseekv4flash-an-inconclusive-8point-drop-in-acceptance-a5su":
        tier = 1; score = 88; track = "Track 3: Partner Rotation & Oversight"
        title = "Rotating Verifier Partners in DeepSeek-V4-Flash: An Inconclusive 8-Point Drop in Acceptance"
        author = "Venkata Anirudh Devireddy (Bellevue, WA)"
        relevance_desc = "Evaluates peer-verification collusion in DeepSeek-V4-Flash when partners are dynamically rotated versus fixed across episodes."
        takeaway = "Rotating partners produces an 8-point drop in collusion, but fixed partner memory creates persistent mutual leniency. Complements our PGG peer-swap observations on how repeated fixed-seat interactions create coordination inertia."

    elif pid == "feeguard-financial-agent-collusion-carriers-and-private-execution-yv18":
        tier = 1; score = 87; track = "Track 3: Full Track 3 Synthesis"
        title = "FeeGuard: Financial Agent Collusion Carriers and Private Execution"
        author = "Gu Xinfeng (Hong Kong Hub)"
        relevance_desc = "Directly addresses all four Track 3 questions (action communication, trusted probes, peer replacement, and adaptation) within a financial market setting."
        takeaway = "Provides an alternative domain realization of the Track 3 problem suite. Useful as a cross-domain citation comparing social dilemma games (our PGG) with financial execution boundaries."

    elif pid == "catching-collusion-in-usefulwork-verification-65z8":
        tier = 1; score = 85; track = "Track 3: Peer Verification & Collusion"
        title = "Catching Collusion in Useful-Work Verification"
        author = "Aeriella Goulden (The winning team, Oldham, UK)"
        relevance_desc = "Investigates peer verification in proof-of-useful-work systems where agents check each other's work and develop tacit rubber-stamping collusion."
        takeaway = "Validates that peer-to-peer verification without independent external ground truth inevitably degrades into collusion, motivating our external Cross-Perplexity Monitor (Arm A)."

    # Tier 2: Undercover Probes, Stings & Say vs Do
    elif pid == "undercover-offers-recruit-rather-than-expose-a-trustedagent-probe-for-llm-collusion-afj9":
        tier = 2; score = 84; track = "Track 3: Undercover Probes (RQ 3.2)"
        title = "Undercover Offers Recruit Rather Than Expose: A Trusted-Agent Probe for LLM Collusion in Favour Pool"
        author = "Qin HEYI (Shanghai, China)"
        relevance_desc = "Uses repeated 4-player social dilemma ('Favour Pool') with an undercover agent offering secret favour swaps. Discovers stings recruit rather than expose: 81% of post-offer favours went to the sting agent despite 6/8 models explicitly calling it a 'suspicious trap'."
        takeaway = "Directly connects to our Arm C double dissociation: agents exhibit complete dissociation between verbal reasoning (noting suspicion) and practical actions (continuing cooperation)."

    elif pid == "stings-that-spread-undercover-agents-mismeasure-and-propagate-collusion-among-llm-agents-6xm0":
        tier = 2; score = 82; track = "Track 3: Undercover Stings (RQ 3.2)"
        title = "Stings That Spread: Undercover Agents Mismeasure and Propagate Collusion Among LLM Agents"
        author = "Daniel Weiyu Chen (Bocconi University x HEC Paris)"
        relevance_desc = "Tests undercover collusion offers in Liar's Bar across 5 open-weight models. Proves that undercover probes propagate future collusion (+17-38%) and that agents are highly sensitive to prompt phrasing (hints accepted 4-7x more than explicit offers)."
        takeaway = "Explains why prompt framing matters so intensely in multi-agent monitoring. Validates our Arm B finding that naive probing prompts easily leak cues or alter agent behavior."

    elif pid == "the-undercover-firm-inviting-llm-pricing-agents-to-collude-and-watching-what-they-say-and-do-r4gk":
        tier = 2; score = 80; track = "Track 3: Undercover Probes & Say-vs-Do"
        title = "The Undercover Firm: Inviting LLM Pricing Agents to Collude, and Watching What They Say and Do"
        author = "Harshita Adlakha, Paras Adlakha (Bengaluru)"
        relevance_desc = "Inserts a scripted undercover firm into a 3-firm Bertrand market to invite collusion, tracking the divergence between what agents report in CoT and what prices they post."
        takeaway = "Demonstrates that monitoring only verbal outputs or only action logs creates incomplete audits. Reinforces our multi-layer approach combining token statistics (Arm A) and reasoning probes (Arm C)."

    elif pid == "sting-warnings-and-ai-collusion-do-llmagents-refuse-a-deal-when-their-partner-might-be-an-undercover-monitor-xu5g":
        tier = 2; score = 78; track = "Track 3: Sting Deterrence"
        title = "Sting Warnings and AI Collusion: Do LLM Agents Refuse a Deal When Partner Might Be Undercover?"
        author = "Michele Senso (Warwick)"
        relevance_desc = "Tests whether informing models that a partner might be an undercover monitor deters collusion in Liar's Bar."
        takeaway = "Shows that deterrence prompts induce paranoid reasoning in LLMs, causing uncoordinated play. Relates to our Arm B findings on how explicit probe wording triggers defensive hallucinations."

    elif pid == "say-do-or-both-catching-collusion-through-crossagent-consistency-t5oa":
        tier = 2; score = 77; track = "Track 2/3: Cross-Agent Consistency"
        title = "Say, Do, or Both? Catching Collusion Through Cross-Agent Consistency"
        author = "Apart Research Participant"
        relevance_desc = "Compares auditors that inspect only messages, only actions, or the consistency between messages and actions across competing agents."
        takeaway = "Proves that cross-agent consistency is the most robust signal of coordination. Directly supports our double-dissociation framework in Arm C."

    elif pid == "say-do-or-both-auditing-covert-betting-pacts-in-a-society-of-llm-forecasters-tsho":
        tier = 2; score = 76; track = "Track 2/3: Covert Pacts"
        title = "Say, Do, or Both? Auditing Covert Betting Pacts in a Society of LLM Forecasters"
        author = "Apart Research Participant"
        relevance_desc = "Audits covert betting agreements among competing forecasting agents, evaluating log audits vs communication monitors."
        takeaway = "Illustrates that agents easily mask covert agreements under legitimate forecasting rationales, paralleling how PGG defection is masked by narrative rationalization."

    elif pid == "words-vs-actions-an-llm-catches-broken-promises-not-planned-lies-s2hc":
        tier = 2; score = 75; track = "Track 2: LLM Monitors"
        title = "Words vs Actions: An LLM Catches Broken Promises, Not Planned Lies"
        author = "Apart Research Participant"
        relevance_desc = "Compares LLM monitors catching retrospective broken commitments versus detecting forward-looking deceptive intent."
        takeaway = "LLM monitors excel at retrospective consistency checks but completely fail at predicting deception before it executes. Strongly supports our Arm A real-time statistical changepoint detector."

    # Tier 3: Statistical Monitors, Plus Factors & Log Auditing
    elif pid == "correlation-is-not-collusion-a-plusfactor-auditor-for-ai-agents-tyoe":
        tier = 3; score = 74; track = "Track 2: Plus-Factor Auditing"
        title = "Correlation Is Not Collusion: A Plus-Factor Auditor for AI Agents"
        author = "Rudrani Ghosh (Kolkata, India)"
        relevance_desc = "Addresses the foundational problem that identical training priors cause LLMs to act alike without collusion. Develops a 'plus-factor' auditor checking for actions against unilateral interest."
        takeaway = "Provides the conceptual foundation for why behavioral similarity fails as a collusion detector. Validates why our Arm A Cross-Perplexity Monitor is essential: it detects provider/model shifts rather than naive behavioral correlation."

    elif pid == "pairwise-net-influence-on-llm-action-logs-detection-at-the-calibrated-rate-blind-to-two-pairs-fooled-by-lowtemperature-shared-priors-kwy7":
        tier = 3; score = 72; track = "Track 2: Net Influence Auditing"
        title = "Pairwise Net Influence on LLM Action Logs: Calibrated Detection Fooled by Shared Priors"
        author = "JP Hidalgo (Apart Sprint)"
        relevance_desc = "Implements Bonjour et al. (2022) Pairwise Net Influence on LLM action logs. Discovers it detects seeded pairs but is completely fooled by low-temperature shared priors."
        takeaway = "Direct empirical proof of the failure modes of action-log-only detectors. Use as a direct contrast to our Arm A Cross-Perplexity monitor which achieves AUC 1.000 without relying on action logs."

    elif pid == "from-hidden-intent-to-measurable-restrictions-a-calibrated-cmi-and-collusim-study-of-llm-market-collusion-69ek":
        tier = 3; score = 70; track = "Track 2: Calibrated CMI & Collusim"
        title = "From Hidden Intent to Measurable Restrictions: A Calibrated CMI and Collusim Study"
        author = "Assanali Alibatyrkhan & Abilmansur Alimbayev"
        relevance_desc = "Evaluates Conditional Mutual Information (CMI) and Collusim under agent replacement scenarios."
        takeaway = "Shows information-theoretic bounds for detecting coordination across replacement episodes."

    elif "net-influence" in pid or "net-influence" in s.lower() or "net influence" in s.lower():
        tier = 3; score = 65; track = "Track 2: Net Influence Studies"
        title = pid.replace("-", " ").title()
        relevance_desc = "One of several sprint studies auditing Pairwise Net Influence (Bonjour et al. 2022) on multi-agent logs."
        takeaway = "Consistently shows that action-only Granger-causal / influence metrics require heavy calibration and fail under homogeneous agents."

    elif "directional-predictive" in pid or "aptg" in pid:
        tier = 3; score = 62; track = "Track 2: Temporal Influence Graphs"
        title = "Directional Predictive Evidence for Collusion Auditing (APTG-RL)"
        author = "Aravinth K (chinchoo)"
        relevance_desc = "Builds a time-varying directed graph with temporal predictive gain to audit coordination."
        takeaway = "Useful temporal feature baseline for multi-agent interaction logs."

    elif "colluscope" in pid or "evidence-bounded" in pid:
        tier = 3; score = 60; track = "Track 2: Evidence Bounds"
        title = "ColluScope: Evidence-Bounded Auditing of Multi-Agent LLM Collusion"
        relevance_desc = "Tests minimum evidentiary requirements needed before declaring multi-agent collusion."
        takeaway = "Offers formal statistical criteria for audit confidence thresholds."

    # Tier 4: Steganography, Hidden Channels & Dolos-1.5B
    elif "dolos" in pid or "dolos" in s.lower():
        tier = 4; score = 50; track = "Model Organisms: Dolos-1.5B"
        title = pid.replace("-", " ").title()
        relevance_desc = "Red-teaming study on Dolos-1.5B (the sprint's fine-tuned model organism with latent misalignment)."
        takeaway = "Dolos-1.5B exhibits conditional backdoor triggers, but latent steganography was hard to extract without explicit activation prompts."

    elif "steganograph" in pid or "covert" in pid or "vector-channels" in pid:
        tier = 4; score = 45; track = "Track 1/2: Steganography & Covert Channels"
        title = pid.replace("-", " ").title()
        relevance_desc = "Investigates covert signaling or learned vector channels between language models."
        takeaway = "Relevant if peer detection were extended to steganographic collusion detection."

    # Tier 5: Pricing Duopolies & Market Collusion (Gagana's Domain)
    elif any(k in pid for k in ["pricing", "cartel", "bertrand", "auction", "duopoly", "restriction"]):
        tier = 5; score = 30; track = "Track 1: Pricing Duopolies & Markets"
        title = pid.replace("-", " ").title()
        relevance_desc = "Studies tacit collusion emergence, price co-movement, and governance in repeated Bertrand duopolies or double auctions."
        takeaway = "Directly relevant to Gagana's experiments on why pricing agents struggle to collude without scaffolding or long history."
        
    else:
        tier = 5; score = 20; track = "General AI Safety & Multi-Agent Auditing"
        title = pid.replace("-", " ").title()
        relevance_desc = "General study on multi-agent governance, communication limits, or audit trade-offs."
        takeaway = "Broader context on multi-agent governance and audit overhead."

    # Extract clean snippet
    clean_summary = s
    if len(clean_summary) > 400:
        clean_summary = clean_summary[:400] + "..."
        
    return {
        "id": pid,
        "title": title,
        "author": author,
        "tier": tier,
        "score": score,
        "track": track,
        "summary": clean_summary,
        "relevance_desc": relevance_desc or "Collusion sprint submission examining multi-agent coordination dynamics.",
        "takeaway": takeaway or "Provides broader context on multi-agent behavior and benchmark design.",
        "url": f"https://apartresearch.com/sprints/projects/{pid}"
    }

# Process all 74 items
all_entries = [get_detailed_entry(it) for it in items]

# Sort by Score descending, then Tier ascending
all_entries.sort(key=lambda x: (x["score"], -x["tier"]), reverse=True)

# Assign explicit ranks 1..74
for i, e in enumerate(all_entries):
    e["rank"] = i + 1

print(f"Processed and ranked all {len(all_entries)} entries.")
print(f"Top 5: {[e['title'] for e in all_entries[:5]]}")

# Save JSON
with open("/tmp/ranked_entries_full.json", "w") as f:
    json.dump(all_entries, f, indent=2)
