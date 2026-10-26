# PROGRESS v2 (2026-10-21 IST; pre-sprint work, disclose to Apart)
- [x] Old v1 branch work tagged `pilot-v1-backup` (local) and copy in ~/compute/pilot_v1_backup; branch reset to main.
- [x] Vendored subset of algorithmic_pricing_llms (commit 1138244, MIT) in third_party/.
- [x] PREREG v2 committed before runs (2877eab).
- [x] EN/HI/FR packs (machine, hand-patched for junk/gendered verbs), back-translation sheet unreviewed.
- [x] 10 pytest tests pass.
- [x] Runs M, negname, budget, D0, DC (seed 1, 60 rounds). Checks 1-3 pass; check 4 FAILS (DC-D0 +0.134, CI [-0.059,0.332]) -> Drop to Plan A by rule.
- [x] REPORT.md. Seeds 2-3 not run (rule: only if checks 1-4 pass).
- [x] Addendum 1 (explicit seller-goal prompt, D0/DC rerun): check 4 passes (DC-D0 +0.206, CI [0.087,0.322]); DC clean null on 9 contrasts -> Go (clean-null branch), caveats in REPORT.md.
