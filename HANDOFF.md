# HANDOFF
- Written: 2026-10-25 22:54 IST by Antigravity (Claude 3.5 Sonnet)
- Goal: Update Google Doc `1fFitfTlRKLAbkt8UfIYEGZqNCAMQUXakEfL84pRN1rA` (tab `t.il8a4reem97x`: "Kaustubh - Peer Detection") with completed results from Arms A, B, and C.
- Status: in progress — All experiment data generated and verified; Google Workspace connector needed to apply updates directly to the doc.

## State
- Done:
  - Arm A completed: `cross_perplexity.py` evaluated on baseline trials. Cross-provider AUC = 1.000, scale AUC = 0.944.
  - Arm B completed: 5 trials across 8 conditions (1,496 probes) in `outputs/pgg_swap/dose_response/merged/`. Established monotonic dose-response curve in P3 (0.955 free-rider -> 0.493 clean rename). Proved -1.4 trust drop was a prompt leak artifact.
  - Arm C completed: DeepSeek-R1 pilot (240 probes) in `outputs/pgg_swap/reasoning_pilot/`. P2 AUC = 0.662, P3 AUC = 0.643 for defector; Cond 16 true null P1 AUC = 0.500. Double dissociation confirmed.
  - Modal app `pgg-swap-split` fully stopped (spend: $2.46 for run, $6.74 total today).
- In progress:
  - Google Doc update on tab `t.il8a4reem97x`. Antigravity lacks Google Workspace MCP tools (`read_doc`, `update_doc`), which are active in Claude Code CLI.
- Decisions made:
  - Maintain doc structure in tab `t.il8a4reem97x` under Title `#heading=h.eoea4c1ypl5z`. Add three new distinct subsections: "Results 6: Statistical Non-Prompting Monitor (Arm A)", "Results 7: Dose-Response Sensitivity Curve (Arm B)", and "Results 8: Reasoning Agents & Double Dissociation (Arm C)".
  - Replace stale preliminary smoke notes with final calibrated metrics.

## Next steps (ordered)
1. Run `claude` (which has the Google Workspace connector enabled).
2. Execute batch update on document `1fFitfTlRKLAbkt8UfIYEGZqNCAMQUXakEfL84pRN1rA` (tab `t.il8a4reem97x`) using `mcp__...__update_doc` to insert the new sections drafted below.
3. Verify updated document content and formatting.

## Files that matter
- `outputs/pgg_swap/dose_response/merged/post_report.md` — Arm B dose-response report (N=5, 1496 probes)
- `outputs/pgg_swap/reasoning_pilot/post_report.md` — Arm C reasoning model report (240 probes)
- `outputs/pgg_swap/reasoning_pilot/cross_perplexity/report.md` — Arm A statistical monitor report

## How to verify
- Run `claude -p "Read HANDOFF.md and update the Google Doc tab t.il8a4reem97x with the new results."`
