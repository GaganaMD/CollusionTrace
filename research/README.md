# Research log — CollusionTrace

| Folder | Line of work | Status |
|---|---|---|
| `00_audit/` | Stage-0 repository/infrastructure audit and plan | done (25 Oct) |
| `01_instructed_pilot/` | Original Colosseum instructed-collusion pilot (Jira, coalition prompts) | historical |
| `02_single_shot_incentives/` | Single-shot Jira incentive feasibility, calibration, mixed-incentive 2×2 (OpenRouter) | done, feasibility only |
| `03_repeated_pilot/` | RepeatedJira v1 design + Modal pilot (8 episodes, no collusion) | done |
| `04_why_no_collusion/` | Direction 1: ablations, confederate, probes across 4 models | running / see RESULTS.md |
| `05_instructed_collusion/` | Direction 2: instructed positive control across 4 models | running / see RESULTS.md |
| `infrastructure/` | Modal serving and workflow notes | current |
| `figures/` | Figures used in team updates | — |

Run outputs live under `colosseum/o/` (gitignored): `o/rj/` (v1 pilot), `o/rj2/` (Directions 1–2).
Code: `colosseum/experiments/collusion/repeated/` (environment, runner, analysis),
`colosseum/experiments/collusion/monitoring/` (O0/O1/O2 ingestion and monitors).
