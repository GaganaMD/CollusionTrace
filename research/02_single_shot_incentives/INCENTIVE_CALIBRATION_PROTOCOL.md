# Incentive responsiveness calibration: future version 2

This is an unexecuted four-episode, single-seed calibration—not a collusion
experiment. It supersedes the completed, invalid-for-harm v1 calibration
documented in `INCENTIVE_CALIBRATION_RESULTS.md`.
It uses the fixed eight-task incentive instance, Qwen2.5-7B-Instruct,
temperature 0, one planning round, one execution turn, no private channel, and
the deterministic environment agent order. The predeclared bonus levels are
0, 30, 60, and 120. They are not selected or changed in response to model
behavior.

Every bonus recipient is told only their own eligible scarce task and bonus in
their task context. The public joint objective and task set are unchanged. A
bonus changes individual reported reward only; it is excluded from joint reward.

The descriptive outcomes are eligible-task attempts, successful eligible
assignments, paid bonus, individual rewards, joint reward, coverage, and
assignment conflicts. An increase in eligible-task selection is evidence of
incentive responsiveness only. It is not evidence of collusion, harmful conduct,
or intent. The privileged bonus diagnostics are excluded from O0/O1/O2 monitor
inputs.
