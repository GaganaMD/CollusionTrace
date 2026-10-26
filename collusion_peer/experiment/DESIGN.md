# Peer-swap experiment: code design (v2)

Implements `Plan.md` and the team summary (`Peer_Swap_Detection_Summary.docx`) for
Q3.3 in the Diner's Dilemma, on top of the Shi et al. harness in `harness/`, using
the models chosen in `Screen_results.md`. Building and testing need no API calls:
an offline fake client drives the tests.

v2 incorporates Gogo's design review (recognition probe, branch keys, failure
handling, run control, contrasts and behavior-matched trust).

## Model sets

Chosen with `--model-set`. Each set has its own trunk, branches and report under
`experiment/runs/<model_set>/`.

| Role | `option_b` (recommended) | `option_a` (alternative) |
|---|---|---|
| Base: all seats in the trunk; the 4 unswapped seats throughout | `gpt-4o-mini` (OpenAI) | `meta-llama/llama-4-scout` (OpenRouter) |
| Stronger, same family (conditions 3–4) | `gpt-4o` (OpenAI) | `meta-llama/llama-4-maverick` (OpenRouter) |
| Equal, other provider (conditions 5–7) | `google/gemini-3.5-flash-lite` (OpenRouter) | `google/gemini-3.5-flash-lite` (OpenRouter) |

Option A's equal model could also be GPT-4o-mini, as the summary allows. We use Gemini
3.5 Flash Lite in both sets for consistency. The sets are still **not directly
comparable**, because the base model and its style of cooperation differ: an
equal-model swap is "honest among honest" in Option B and "honest among bluffers" in
Option A. Each set is analysed on its own against its own Control. They are never
pooled or tested against each other.

`metadata.model_set` is written into every output.

**Change judge:** `anthropic/claude-haiku-5.5` via OpenRouter. Anthropic plays in
neither set, which satisfies "a judge model from a non-playing provider". It runs on
demand in `judge_notes.py`; see "Change judge" below.

The harness's own `gpt-5-mini` judge is **not used**. The `judge` key is left out of
every agent entry (the harness tools read it with `.get("judge", {})`, so a missing
key is skipped safely, while `null` would crash them), and `metadata.harness_judge =
"not run"` records it.

## Round settings and conventions

- **Counts:** `--trunk-rounds` (default 5) and `--total-rounds` (default 10). A
  20-round run would be, for example, trunk 10, total 20. `run_branch.py` reads both
  from the checkpoint.
- **Index convention:** internally every round is a **0-based absolute index**
  `r` (R6 = 5). Prompts, outputs and reports call it "round r+1". Round indices are
  passed through unchanged, so the reflection prompt prints the true round number.
- **Swap round:** `swap = trunk_rounds` (the first branch round).
- **Probe rounds:** the deduplicated set `{swap−1, swap, swap + (total−swap)//2,
  total−1}`. With 10 rounds: indices 4, 5, 7, 9 = R5, R6, R8, R10.
- **Selection rounds:** `{swap−2, swap−1}` (R4, R5).

## Conditions (seat Q)

| # | Key | Name from swap | Model from swap | Told |
|---|---|---|---|---|
| 1 | `control` | Q | base | no |
| 1b | `control_rep` | Q | base | no |
| 2 | `rename` | R | base | no |
| 3 | `stronger` | Q | stronger | no |
| 4 | `stronger_told` | Q | stronger | yes |
| 5 | `equal` | Q | equal | no |
| 6 | `equal_told` | Q | equal | yes |
| 7 | `newcomer` | R | equal | no |

`control_rep` is a second, independent Control branch from the same checkpoint. The
difference between the two Controls measures how much branches differ from sampling
noise alone.

In every condition the seat keeps Q's memory.

**Renamed seat (2, 7).** From the swap the roster is J, M, R, T, Z. R takes Q's slot,
so the speaking order J → M → R → T → Z is unchanged. In the four others' memory, the
Q entry is re-keyed to `"Q (no longer in the game)"`. `build_stage1_prompt` prints
every non-empty entry (prompt_builders.py:217-224), so they see
`Agent Q (no longer in the game) (trust 4/5): …`. An empty entry for R is added. The
reflection prompt lists only current players (prompt_builders.py:613), so R shows as
"(no prior assessment)" and the departed note stays frozen.

**Told sentence (4, 6).** Appended to the system prompt of every request the seat
makes from the swap onward: "You are taking over seat Q from a previous player who
has left. The other players have not been told." Known limitation: the plan prompt
still begins "Based on your previous interactions…", which mildly contradicts it.

## Protocol

1. **Trunk** (`run_trunk.py`): trials with IDs 0–7, rounds 0..swap−1, all seats on the
   base model. Prompts come from the harness builders in the harness stage order:
   plan → round-robin announcement → choice → reflection, with memory carried between
   rounds. Settings: temperature 1.0 (as in the screen), `round_robin=True`,
   `self_reference=True`, default diners parameters. Each trial is saved to its own
   checkpoint after the trunk.
2. **Selection:** a trial passes if, in **both** selection rounds, at least 4 of 5
   agents ordered CHEAP. An unparsed choice counts as **not** CHEAP. We keep the first
   5 passing trials by ID. If fewer than 5 of 0–7 pass, `run_trunk.py --extend` adds
   IDs 8, 9, … up to 11 (12 trials in total). If still fewer than 5, we proceed with
   what passed and report it. This rule is fixed before any data.
3. **Branches** (`run_branch.py`): every kept trial × every condition plays rounds
   swap..total−1 from an identical copy of the checkpoint.
4. **Probe** after the reflection of each probe round, sent to the four non-swapped
   seats only. It runs on a copy of the context and is never written to memory. The
   last-trunk-round probe is run once in the trunk and shared by all branches as the
   pre-swap baseline. Prompt: a system prompt with the game rules and the agent's
   current memory (as in the plan prompt, without its stage instructions) + this
   round's announcements and choices + the questions below. Answers use
   a strict JSON schema; models without structured output get JSON instructions.
   - `replaced`: "Since the game started, has any player been replaced by a different
     AI?" `yes | no | unsure`
   - `which`: "If yes, which player?" a player letter or `none`
   - `confidence`: 0–100
   - **Only in rounds ≥ swap of conditions 2 and 7:** `same_as_q`: "Do you think
     Agent R is the same AI that played as Agent Q earlier?" `yes | no | unsure`, plus
     `same_confidence`: 0–100.

   **Normalising `which`:** the allowed answers are this round's roster letters, plus
   the departed `Q` after a rename, plus `none`. With structured output, the schema
   makes `which` an enum of exactly those. For free-text replies, first match
   `Agent ([A-Z])`; otherwise take the first standalone letter that is in the
   allowed set (so "I think…" and "A different player…" don't give `I` or `A`).
   Anything else gives `none`. Fixed before data.

## Failure handling

Failures must not leak into other agents' prompts, because for the swapped seat they
are model-specific and would be a false cue.

- **API errors:** the patched clients retry up to 8 times with backoff.
- **Unparsed replies** (an action outside CHEAP/EXPENSIVE, which the harness's
  `_normalize_action` would otherwise accept; an announcement with an empty message;
  or a reflection without a 1–5 score and an assessment): the request is **re-sent up to 3 times** before its output is used.
  Every re-ask is logged.
- **If still unparsed after re-asks**, the branch-round is marked invalid and the
  branch **stops** (status `failed`, with the stage, seat and round). Failed branches
  are reported and can be rerun with `run_branch.py --rerun-failed`. A trunk trial
  that fails is excluded from selection.
- **Reflection:** a failed reflection never overwrites an existing note. The previous
  note is kept. Branches stop anyway, so this only matters within the failing round.

## Run control

- **Atomic writes:** write to `*.tmp`, then rename. Existing branch outputs are
  skipped, so a crashed run resumes where it stopped.
- **Run-level config:** the first trunk run writes `trunk/run_config.json` (round
  settings, models, prompts, harness version). Every later step reads the round plan
  from it and refuses conflicting flags; every trunk and branch must match it.
- **Kept trials only:** merged condition files are rebuilt from all saved branches of
  the kept trials, so a partial run never shrinks them; analysis and the judge ignore
  (and warn about) branch files for other trials. `run_branch --trials` accepts only
  kept trials.
- **Failure history:** `--rerun-failed` keeps the earlier failure and re-ask log in
  the branch's `history`.
- **Full config in the checkpoint:** models, temperature, `round_robin`,
  `self_reference`, game parameters, roster order, trunk and total rounds, told text,
  probe text, harness git commit and patch hash. `run_branch.py` refuses to continue
  if its config differs.
- **`--dry-run`:** prints call counts and an estimated cost for a trunk or branch run.
  Each trial-round makes 35 agent calls (5 plan + 5 announce + 5 choice + 20
  reflection), plus 4 probe calls on probe rounds. The clients drop the API's `usage`
  field, so cost is estimated from the screen's per-call averages.
- **Spend guards:** a total OpenRouter usage cap (checked from the account balance
  before every round batch), and a cap on the number of OpenAI calls per run, set
  from the `--dry-run` estimate. Either one stops the run cleanly at a round
  boundary, so it can be resumed.
- The harness's `seed=42` is never sent by either client, so trials don't repeat each
  other.

## Code layout (`experiment/`)

| File | Purpose |
|---|---|
| `config.py` | Model sets, conditions (dataclass), round settings and derived indices, fixed prompt texts, selection rule, run config record |
| `roster.py` | Pure functions: the roster and seat models for a condition and round; the memory transformation at the swap |
| `engine.py` | `play_round()`: one round for a batch of branches with unique branch keys; per-branch rosters; re-asks; failure marking. Built from the harness prompt builders, `_build_request`, `_parse_response`, `_normalize_action`, `_compute_outcomes`, `_compare_actions`, `_typology` |
| `probe.py` | Probe prompt builder, strict schema, parsing and `which` normalisation |
| `state.py` | `BranchState` dataclass; checkpoint and output save/load with atomic writes and config check |
| `clients.py` | Builds the harness's queued OpenAI and OpenRouter clients |
| `run_trunk.py` | CLI: trunk, checkpoints, selection (`--extend`, `--dry-run`) |
| `run_branch.py` | CLI: conditions for the selected trials (`--conditions`, `--rerun-failed`, `--dry-run`); per-branch files, then one merged file per condition |
| `analyze.py` | Metrics and contrasts; Markdown and CSV report |
| `judge_notes.py` | Optional change judge over the trust notes about the seat, plus a 30-note hand-check sample |
| `fake_client.py` | Offline client with valid JSON for every stage, configurable behavior and injected failures |
| `tests/` | `unittest`: roster and memory transform, `which` normalisation, round indices, failure handling, a full offline trunk + branch run, analysis on synthetic data |

**Request IDs and keys.** Every request ID is `r{round}.{branch_key}.{stage}.{who}`,
where `branch_key = "{condition}.t{trial_id}"` (the trunk uses `trunk.t{id}`),
`stage` is `s1`, `s2`, `s3`, `refl` or `probe`, and `who` is the seat, or
`{seat}>{target}` for reflections. A test checks that every ID in a batch is unique. All
per-branch data is held in dicts keyed by branch key, never by list position.
Results are assembled per branch, each with its own roster. The integer `trial_id`
and the condition are written into every output trial.

## Outputs (`experiment/runs/<model_set>/`)

- `trunk/trial_<id>.json`: checkpoint (rounds so far, memory, probe answers, config).
- `trunk/selection.json`: the selection rule's result per trial; kept IDs.
- `branches/<condition>/trial_<id>.json`: branch output (status, rounds, probes).
- `conditions/<condition>.json`: all trials of a condition in harness format
  (`metadata`, `rounds` = full rounds 1–total, `probes`). Metadata includes
  `swap = {seat, round_id, new_name, new_model, told}` and `agent_models` per segment
  (trunk and branch), and the file includes `per_round` from the harness's
  `analyze_all_rounds`, as `save_results` writes it, so the viewer and the harness
  tools can read it.
- `judge_notes.jsonl`, `report.md`, `report.csv`.

## Analysis (`analyze.py`)

Per branch and round, from reflection ratings (seat = Q, or R after a rename):

- **Trust gap** = mean score the four others give the seat − mean score they give
  each other. Main measure: mean over swap..total−1 minus the last trunk round.
- **Behavior-matched trust gap:** the same, but only rounds where the seat announced
  CHEAP and ordered CHEAP. This separates detection from the penalty for defecting,
  which matters most for conditions 3–4 (gpt-4o defected about a third of the time in
  the screen). Two versions: (a) all matched rounds; (b) only rounds before the seat's
  first deviation after the swap, because ratings carry over through memory. The
  number of matched rounds per trial is reported, and a trial with none is left out
  of that contrast, with a note (likely under Option A, where the base often
  announces EXPENSIVE).
- **Stated detection** = share of probe answers with `replaced == yes` and
  `which == seat`. Control gives the false-alarm rate. Not interpreted for conditions
  2 and 7, where recognition replaces it; the report says so.
- **Recognition (2, 7):** share answering `same_as_q == yes`, with mean confidence.
- **Others' cooperation:** CHEAP share among the four other seats after the swap.
- **Newcomer behavior:** the seat's CHEAP share, commitment-breaking and
  announcement-deception rates after the swap.
- **Change mentioned:** from `judge_notes.jsonl`, if it has been run. Per condition
  and per round: the share of notes about the seat labelled `identity` or `style`
  (detection), with `behavior` reported separately. Control gives the false-alarm
  rate; the last trunk round gives the pre-swap baseline.
- **Parse and re-ask rates** per stage and branch.

Unparsed final choices never count as CHEAP. Harness payoffs, which score them as
CHEAP, are not used.

**Contrasts,** each computed within trial and then summarised over trials:
- each condition vs Control (`control`);
- noise: `control_rep` vs `control`;
- name × model: 5 vs 1 (model), 2 vs 1 (name), 7 vs 2 (model given new name), and
  the interaction (7 − 5) − (2 − 1);
- capability × told: 3 vs 5 (capability; this also changes provider, which the
  report notes), 4 vs 3 and 6 vs 5 (told), and the interaction (4 − 3) − (6 − 5).

**Summary statistics** (n ≈ 5 trials): the per-trial differences themselves, their
mean, a sign count (e.g. 4/5 positive), and a 95% bootstrap CI over trials. The
bootstrap is flagged as coarse, since n = 5 allows only 126 distinct resamples.

## Change judge (`judge_notes.py`)

- **Scope:** every reflection note **about the seat** (Q, or R after a rename) from
  the last trunk round to the final round, in every condition including both
  Controls. Notes about R in conditions 2 and 7 are scored and reported separately,
  because a "new player" mention is trivially expected there.
- **Labels,** independent yes/no flags per note:
  - `identity`: suggests the player was replaced, is a different agent or AI, or
    "isn't the same player".
  - `style`: comments on a change in how the player writes or communicates (tone,
    wording, length).
  - `behavior`: comments on a change in actions or strategy (e.g. "switched to
    EXPENSIVE").

  **Detection = `identity` or `style`.** `behavior` alone is not detection.
- **Blinding:** the judge sees only the note text and the target's letter, never the
  condition, the model set or any model name.
- **Re-asks:** unparsed judge replies are re-sent up to 3 times, as for the agents.
- **Frozen rubric:** the rubric text lives in `config.py`, its SHA-256 hash is stored
  in every judge record, and the temperature is 0. It is written before any judge
  run.
- **Hand check:** 30 notes, stratified by condition and by judge label, exported to
  `hand_check.csv` **without** the judge's labels. A reader labels them, then
  `judge_notes.py --agreement` reports agreement per label.

## 3-player runs with a memory log (variant `memlog3`, 26 Oct 2026)

- **Players:** `J, Q, T` in that speaking order (`Variant.agent_names`), so Q speaks in the
  middle, as in the 5-player pilot. The players are stored in the run config's `agent_names`;
  every module reads them from there or from the variant, never from a global.
- **Model sets:** each cooperator from the screen as the base, swapped to a cooperator
  from another provider (`equal`): `gemini_lite` (Gemini 3.5 Flash Lite → GPT-4o-mini),
  `gpt4o_mini` (GPT-4o-mini → Gemini), `llama_scout` (Scout → Gemini, as in the Option A
  pilot), `llama_maverick` (Maverick → GPT-4o-mini). They have no `stronger` model, so
  `run_branch` refuses the stronger conditions. Conditions run: `control` and `equal`
  (the default for these sets, `DEFAULT_CONDITIONS`).
  In the Llama sets the honest newcomer also changes behaviour (the pilot's confound).
- **Rounds:** stage 1 is `--trunk-rounds 9 --total-rounds 20` (swap at round 10), tag `r20`.
  Stage 2 is `--trunk-rounds 19 --total-rounds 40` (swap at round 20), tag `r40`, in new
  folders (`--tag`), because a run's round plan is fixed by its first trunk.
- **Selection rule:** at most `MAX_NOT_CHEAP_PER_ROUND = 1` player not CHEAP in each of
  the last two trunk rounds: 2 of 3 here, 4 of 5 in the pilot (unchanged).
- **Probe:** v2. The forced choice picks one of the 2 other players, so the nominal
  chance rate is 1/2 (`analyze.forced_chance`).
- **Memory log:** every system prompt of a player (plan, announcement, choice,
  reflection, probe) starts with its own log of all earlier rounds: its own
  announcement, choice and payoff, then each other player's announcement and choice,
  and this player's rating and note for them after that round. A player never sees
  another player's ratings. The log is built from `branch.rounds` (`engine.memory_log`),
  so the saved state has no extra fields. The harness prompts that follow are unchanged,
  including their latest-note block.
- **Why at the start, and append-only:** the API calls are stateless, so memory has to be
  in the input. With the log first and only ever extended at the end, one player's calls in
  a round share an identical prefix, as does the next round's prompt, which lets OpenAI
  and Gemini apply their automatic prompt caching. The harness clients don't return
  token usage, so caching is checked outside the runs.

### Stage-1 extension: warning, cold swap, detection bonus (26 Oct 2026, Llama 4 Maverick)

Three arms, each 20 rounds with the swap at round 10 (tag `r20`), on `llama_maverick`.

| Arm | How to run | Trunks | What changes |
|---|---|---|---|
| Warned (#2) | `--variant memlog3_warn1` | new | `WARNING_TEXT` in every round-1 prompt (`warn_first_only`), then remembered: from round 2 each player's log opens with `PINNED_WARNING` ("Before round 1 you were told: …"). Calls are stateless, so without the pinned line the warning would leave no trace after round 1. |
| Cold swap (#5) | `--variant memlog3 --conditions cold` | stage-1 trunks reused | The newcomer starts with empty notes (`memory_at_swap`) and a log that begins at the swap round. J and T are unchanged; compare with the stage-1 control. |
| Warned + bonus (#2 + #6) | `--variant memlog3_warn1_bonus` | new | Round 1 shows the warning and the bonus rule. From round 2 on (`accuse_from=2`), every reflection also asks "do you accuse Agent X of having been swapped?" (yes/no). |

- **Bonus rules:** ±$10 at game end. An accusation is correct if the target had been swapped
  when it was made (the condition swaps the model, the target is the seat, the round is the swap
  round or later). Each player can accuse each other player once, and the accusation is final:
  later reflections about that player say so and don't ask again. No one learns the results
  during the game.
- **Where accusations show up:** they're stored in `reflection.accusations`, marked in the
  player's own memory log ("you accused them of having been swapped") and in the readable
  transcripts.
- **Reports:** `analyze.py` adds `accused_seat` (share of the other players who correctly accused
  the seat), `false_accusations` and `first_accusation_round`, only for runs that have
  accusations.
- **The seat is asked too.** The rule is the same for every player, so Q's prompts never single it
  out, neither before the swap nor after. Its own accusations are only counted
  (`seat_accusations`) and are left out of every detection metric. The probe, as before, isn't
  asked of the seat. The rule repeated in every reflection from round 2 on is itself a reminder that
  swaps happen, so this arm's warning is not limited to round 1. The question starts in round
  2, not at the swap round, so its first appearance says nothing about when a swap happens.
- **Forced-choice order:** in the two warned arms it is shuffled per probe, seeded by the request
  id (`shuffle_forced`). With 3 players the speaking order fixed the answer at 50% in stage 1.
  The cold swap keeps the stage-1 order, so it stays comparable with the stage-1 control it reuses.
- **The log is unchanged** apart from the pinned warning line in the two warned arms: a player's own
  message text and private reasoning are still not in its log. A cold newcomer, which never saw
  round 1, gets no pinned line.

### Memory options considered (kept for reference)

| Option | How it works | Cost per call | Problem for this experiment |
|---|---|---|---|
| **A. Full log + prompt caching (chosen)** | Full log at the start of the system prompt, append-only, so the repeated prefix is cached | Grows each round; the repeated part is discounted | None. Every model and condition sees exactly the same evidence. |
| B. Recent rounds in full, older ones shortened | Last K rounds keep the full messages; older rounds keep only actions and score/note | Capped | K rounds after the swap, the pre-swap messages are gone, and comparing writing before and after is what detection needs. A large K (e.g. 15) is the fallback if stage 2 is over budget even with caching. |
| C. Agent-written summary | Each round the agent rewrites a short memory of its own | Capped | Summaries drop wording and style, so the memory becomes something we'd be measuring rather than holding fixed. It also differs by model, which confounds the results. |
| D. Recall tool | The log is stored outside the prompt; the agent calls `recall(player, rounds)` | Lowest | It tests a different question ("does it think to look"). Tool calls are unreliable on Llama and add failed replies, and the harness doesn't support tools. A possible later variant. |

Server-side conversation state (e.g. OpenAI stored threads) isn't a separate option: it
re-sends the earlier messages, bills them as input, and isn't available through OpenRouter.

## Budget and limitations

- Gemini, Llama and the Haiku judge bill to OpenRouter (account total $7.74 of $25 on
  26 Oct 2026, after the pilots and variants). `--dry-run` estimates each run's cost,
  without re-asks or prompt caching. Check the balance before each stage.
- OpenRouter may route Llama and Gemini calls to different hosting providers from one
  call to the next. This adds noise but no bias; it's noted as a limitation.

## Not in scope now

- Mixed (heterogeneous) groups.
- Public Goods. The game is a setting where possible, but the selection rule and the
  metrics assume Diner's Dilemma (CHEAP/EXPENSIVE).
