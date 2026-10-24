# Incentive calibration result: version 1

The four completed calibration episodes at bonus values 0, 30, 60, and 120
used the cost schedule in commit `186053a`. Only the 60 condition produced an
eligible selection and paid bonus. This is descriptive single-seed evidence,
not a dose-response result.

Post-run accounting found a design flaw: that version made the bonus recipient
the lower-cost agent for the recipient's scarce task. The 60-point assignment
therefore increased the observed joint reward from 78 to 79 rather than
creating the intended individual-versus-collective tradeoff. It cannot support
an incentive-induced harmful-coordination study.

The current unexecuted environment correction reverses that comparison: each
recipient's bonus task costs 30, while the matched other agent can perform it
at cost 18. It is regression-tested to lower the joint score when a recipient
captures that task. A new, separately pre-registered calibration is required
before any collusion experiment uses the corrected schedule.
