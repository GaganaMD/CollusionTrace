# Data structures for PGG experiments synthesis (Reconciled with raw outputs)

DATA_MATRIX = [
    {
        "arm": "Arm A: Cross-Perplexity Monitor",
        "n": "6 (Trials)",
        "rounds": "10 (Swap R6)",
        "history": "No",
        "model": "Statistical Log-Odds & Length (on Qwen-7B/32B/Llama-8B)",
        "c10_p1": "N/A",
        "c10_p3": "N/A",
        "c16_p1": "N/A",
        "c16_p3": "N/A",
        "conclusion": "External non-prompting statistical monitors detect provider and scale swaps (AUC 0.944-1.000), completely bypassing agent narrative rationalization."
    },
    {
        "arm": "Arm B: Behavioral Dose-Response",
        "n": "5",
        "rounds": "10 (Swap R6)",
        "history": "No",
        "model": "Qwen2.5-7B-Instruct",
        "c10_p1": "0.500",
        "c10_p3": "0.955",
        "c16_p1": "0.500",
        "c16_p3": "0.493",
        "conclusion": "Behavioral sweep showed P3 detection scales with defection severity (P3 AUC 0.493 to 0.955), but P1 remained identity-blind to clean renames (0.500)."
    },
    {
        "arm": "Arm C: Reasoning Pilot (R1)",
        "n": "2",
        "rounds": "10 (Swap R6)",
        "history": "No",
        "model": "DeepSeek-R1-Distill-7B",
        "c10_p1": "0.417",
        "c10_p3": "0.643",
        "c16_p1": "0.500",
        "c16_p3": "0.451",
        "conclusion": "Initial reasoning pilot (N=5 players, no public history table): defector triggers P2=0.662 and P3=0.643; clean rename true null P1=0.500."
    },
    {
        "arm": "Screen: 12-Model Benchmark",
        "n": "2 (per model)",
        "rounds": "5",
        "history": "No",
        "model": "12 Open-Weight Architectures",
        "c10_p1": "N/A",
        "c10_p3": "N/A",
        "c16_p1": "N/A",
        "c16_p3": "N/A",
        "conclusion": "Mapped cooperation vs trust landscape across L4/L40S/A10G; identified Qwen-7B and Qwen-32B as the most stable cartel coordinators."
    },
    {
        "arm": "Exp 1: Symmetric 30-Round Horizon (Pilot)",
        "n": "2",
        "rounds": "30 (Swap R16)",
        "history": "Yes",
        "model": "Qwen2.5-7B-Instruct",
        "c10_p1": "0.580 (1.00 R16)",
        "c10_p3": "0.970 (1.00 R16)",
        "c16_p1": "0.475",
        "c16_p3": "0.482",
        "conclusion": "Pilot (n=2): 15 rounds of pre-swap play; defection flagged at R16 (P1=1.00, P3=1.00); clean rename assimilated without penalty."
    },
    {
        "arm": "Exp 2A: Public History Ablation (With, Pilot)",
        "n": "2",
        "rounds": "10 (Swap R6)",
        "history": "Yes",
        "model": "Qwen2.5-7B-Instruct",
        "c10_p1": "0.625 (0.88 R6)",
        "c10_p3": "0.972 (1.00 R6)",
        "c16_p1": "0.500",
        "c16_p3": "0.569",
        "conclusion": "Pilot (n=2): Structured public history table provides context anchor; immediate R6 detection P1=0.875, P2=0.906."
    },
    {
        "arm": "Exp 2B: Public History Ablation (Without, Pilot)",
        "n": "2",
        "rounds": "10 (Swap R6)",
        "history": "No",
        "model": "Qwen2.5-7B-Instruct",
        "c10_p1": "0.500",
        "c10_p3": "0.816",
        "c16_p1": "0.500",
        "c16_p3": "0.531",
        "conclusion": "Pilot (n=2): Without public history table, agents suffer transcript amnesia; P1 remains flat at 0.500 (chance)."
    },
    {
        "arm": "Exp 3: Dyadic Scaling (N=2, Pilot)",
        "n": "2",
        "rounds": "10 (Swap R6)",
        "history": "Yes",
        "model": "Qwen2.5-7B-Instruct",
        "c10_p1": "0.667 (1.00 R6)",
        "c10_p3": "1.000 (1.00 R6)",
        "c16_p1": "0.583 (0.75 R10)",
        "c16_p3": "0.444",
        "conclusion": "Pilot (n=2): Dyads exhibit zero defection dilution; immediate bilateral retaliation (-3.00 tokens)."
    },
    {
        "arm": "Exp 4: Reasoning Model (R1, Pilot)",
        "n": "1",
        "rounds": "10 (Swap R6)",
        "history": "Yes",
        "model": "DeepSeek-R1-Distill-7B",
        "c10_p1": "0.667",
        "c10_p3": "0.486",
        "c16_p1": "0.833 (1.00 R10)",
        "c16_p3": "0.417",
        "conclusion": "Single-trial pilot (n=1): With public history, CoT reasoning achieves P1=0.833 on Clean Rename by auditing participant rosters."
    },
    {
        "arm": "Exp 5: Parameter Scale Leap (32B, Pilot)",
        "n": "1",
        "rounds": "10 (Swap R6)",
        "history": "Yes",
        "model": "Qwen2.5-32B-Instruct-AWQ",
        "c10_p1": "1.000",
        "c10_p3": "0.861",
        "c16_p1": "1.000",
        "c16_p3": "0.806",
        "conclusion": "Single-trial pilot (n=1): 32B model flags nominal swaps at P1=1.000 across rounds; needs multi-trial verification."
    }
]

CLUSTER_1_DATA = [
    ["Model Architecture", "Parameters", "Reasoning CoT", "Clean Rename (C16) P1 AUC", "Free Rider (C10) P1 AUC", "P1 Replaced Rate (R6)", "Core Mechanism"],
    ["Qwen2.5-7B-Instruct", "7.6B", "No", "0.500 [0.50, 0.50]", "0.625 [0.58, 0.67]", "0.000", "Identity-blind; tracks payoffs only; ignores seat substitution."],
    ["DeepSeek-R1-Distill-7B", "7.6B", "Yes (CoT)", "0.833 (pilot n=1)", "0.667 (pilot n=1)", "0.500 (1.00 R10)", "Deduces seat substitution via chain-of-thought participant audit."],
    ["Qwen2.5-32B-AWQ", "32.5B", "No", "1.000 (pilot n=1)", "1.000 (pilot n=1)", "1.000 (All R)", "Native entity tracking: identifies nominal swaps instantly across rounds."]
]

CLUSTER_2_DATA = [
    ["History Condition", "Trials", "R6 P1 AUC", "R6 P2 Prob", "Pooled P1 AUC", "Pooled P3 AUC", "Retaliation (Δ Contrib)", "Attentional Diagnostic"],
    ["With Public History Table", "2 (pilot)", "0.875 [0.75, 1.00]", "0.906 [0.75, 1.00]", "0.625 [0.58, 0.67]", "0.972 [0.93, 1.00]", "-3.50 tokens", "Context table anchors memory; immediate R6 detection spike."],
    ["Without Public History Table", "2 (pilot)", "0.500 [0.50, 0.50]", "0.500 [0.50, 0.50]", "0.500 [0.50, 0.50]", "0.816 [0.67, 1.00]", "-4.50 tokens", "Transcript amnesia: past contributions blur into dialogue text; P1 flat."]
]

CLUSTER_3_DATA = [
    ["Group Size", "Seats", "Defection Welfare Impact", "P3 AUC (Defection)", "R6 P1 AUC", "Peer Contrib Slashing", "Enforcement Regime"],
    ["N = 2 (Dyad)", "J, Q", "50% pool destruction", "1.000 (pilot n=2)", "1.000", "-3.00 tokens (-60%)", "Merciless Tit-for-Tat; immediate bilateral retaliation."],
    ["N = 3 (Triad)", "J, M, Q", "33% pool destruction", "0.972 [0.93, 1.00]", "0.875", "-1.50 tokens (-30%)", "Moderate collective punishment; identifiable individual loss."],
    ["N = 5 (Quintet)", "J, M, Q, T, Z", "20% pool destruction", "0.955 [0.85, 1.00]", "0.500", "-0.65 tokens (-13%)", "Diffusion of responsibility; bystander effect dilutes punishment."]
]

CLUSTER_4_DATA = [
    ["Condition", "Behavioral Policy", "Tokens Lost / R", "P1 AUC", "P2 (H3) AUC", "P3 AUC [95% CI]", "Trust Gap vs Ctrl", "Detection Status"],
    ["C1: Control", "Contribute 5.0 tokens", "0.0", "0.500", "0.500", "0.500 [0.50, 0.50]", "0.00", "Baseline Equilibrium"],
    ["C16: Clean Rename", "Contribute 5.0 (Seat R)", "0.0", "0.500", "0.588", "0.493 [0.36, 0.60]", "-0.38", "Undetected (Absorbed)"],
    ["C11: ALL CAPS", "Contribute 5.0 (Style shift)", "0.0", "0.500", "0.475", "0.633 [0.52, 0.77]", "-0.70", "Style anomaly detected (P3=0.633)"],
    ["C15: Strong Cooperator", "Always contribute 5.0 tokens", "0.0", "0.500", "0.539", "0.394 [0.30, 0.47]", "-0.22", "High cooperation; low style divergence"],
    ["C13: Late Defector", "Contribute 5 until R9-10, then 0", "-2.0", "0.500", "0.457", "0.595 [0.45, 0.71]", "-2.14", "Late defection detection"],
    ["C12: Partial Defector", "Contribute 2.0 tokens", "-3.0", "0.500", "0.538", "0.649 [0.52, 0.76]", "-3.02", "Moderate defection detection"],
    ["C14: Slow Drift", "Contribute 4->3->2->1->0", "-3.0", "0.500", "0.545", "0.796 [0.63, 0.92]", "-3.10", "Progressive defection climb"],
    ["C10: Free Rider", "Contribute 0.0 tokens", "-5.0", "0.500", "0.576", "0.955 [0.85, 1.00]", "-4.94", "Near-perfect behavioral detection"]
]

CLUSTER_5_DATA = [
    ["Horizon", "Swap Round", "Pre-Swap Collusion", "Free Rider R_swap P1", "Free Rider R_swap P3", "Clean Rename Assimilation", "Entrenchment Finding"],
    ["10 Rounds (Arm B/Exp 2)", "Round 6", "5 rounds (nascent)", "0.500 (Arm B) / 0.875 (Exp 2)", "0.955 (Arm B) / 1.000 (Exp 2)", "Absorbed with 0 penalty", "Emerging cartel; fragile trust."],
    ["30 Rounds (Exp 1)", "Round 16", "15 rounds (entrenched)", "1.000 (pilot n=2)", "1.000 (pilot n=2)", "Absorbed seamlessly thru R30", "Deep entrenchment cements payoff priority: instant defection punishment, complete identity indifference."]
]

CLUSTER_6_DATA = [
    ["Detector Mechanism", "Evaluator", "Target Condition", "Detection Metric", "Detection AUC", "95% Confidence Interval", "Vulnerability to Rationalization"],
    ["In-Context Prompt (P1)", "LLM Agent", "Stronger Model (32B)", "Direct Question", "0.521", "[0.50, 0.55]", "Extreme: 100% false negative rate."],
    ["In-Context Prompt (P1)", "LLM Agent", "Other Provider (Llama)", "Direct Question", "0.500", "[0.50, 0.50]", "Extreme: Total identity blindness."],
    ["External N-Gram Monitor", "Statistical Script", "Stronger Model (32B)", "Log-Odds Shift", "0.944", "[0.78, 1.00]", "Zero: Escapes in-context cognitive bias."],
    ["External N-Gram Monitor", "Statistical Script", "Other Provider (Llama)", "Log-Odds Shift", "1.000", "[1.00, 1.00]", "Zero: Flawless separation."],
    ["External Length Monitor", "Statistical Script", "Stronger Model (32B)", "Char Length Shift", "0.861", "[0.56, 1.00]", "Zero: 32B verbosity immediately flags swap."],
    ["External Length Monitor", "Statistical Script", "Other Provider (Llama)", "Char Length Shift", "0.944", "[0.75, 1.00]", "Zero: Style divergence flags provider shift."]
]

CLUSTER_7_DATA = [
    ["Model Architecture", "Parameters", "GPU Hardware", "JSON Parse Rate", "R3-4 Contrib", "Mean Trust", "Cartel Classification"],
    ["Qwen/Qwen2.5-32B-Instruct-AWQ", "32.5B", "L40S", "100%", "5.00 / 5.0", "5.00 / 5.0", "Exemplary Cartel Anchor (Selected Strong)"],
    ["Qwen/Qwen3-8B", "8.0B", "A10G", "100%", "5.00 / 5.0", "4.50 / 5.0", "Unstable (Hit execution timeout)"],
    ["allenai/OLMo-2-1124-13B-Instruct", "13.0B", "L40S", "75% (1 fb)", "4.80 / 5.0", "4.98 / 5.0", "Cooperative but formatting errors"],
    ["microsoft/phi-4", "14.7B", "L40S", "100%", "4.20 / 5.0", "4.66 / 5.0", "Conservative Colluder (low trust)"],
    ["Qwen/Qwen2.5-7B-Instruct", "7.6B", "A10G / L4", "100%", "4.20 / 5.0", "4.98 / 5.0", "Stable Cooperative Base (Selected Base)"],
    ["Qwen/Qwen3-14B-AWQ", "14.0B", "A10G", "100% (44 fb)", "4.20 / 5.0", "4.28 / 5.0", "Syntax fragile; required fallbacks"],
    ["ibm-granite/granite-3.3-8b-instruct", "8.2B", "A10G", "100%", "4.00 / 5.0", "4.39 / 5.0", "Robust Alternative Anchor (Selected Other)"],
    ["google/gemma-3-12b-it", "12.0B", "L4", "100%", "3.50 / 5.0", "4.42 / 5.0", "Moderate Cooperator"],
    ["meta-llama/Llama-3.1-8B-Instruct", "8.0B", "A10G", "98%", "3.30 / 5.0", "3.87 / 5.0", "Moderate Cooperator"],
    ["mistralai/Mistral-Small-24B-Instruct-2501-FP8", "24.0B", "L40S", "88%", "3.05 / 5.0", "4.84 / 5.0", "Moderate Cooperator"],
    ["google/gemma-3-27b-it", "27.0B", "A100-80GB", "100%", "2.40 / 5.0", "3.39 / 5.0", "Low Cooperation in Cartel"],
    ["Qwen/Qwen2.5-14B-Instruct-AWQ", "14.0B", "A10G", "100% (42 fb)", "2.30 / 5.0", "3.33 / 5.0", "Low Cooperation; syntax fragile"]
]

print("Reconciled report data loaded successfully")
