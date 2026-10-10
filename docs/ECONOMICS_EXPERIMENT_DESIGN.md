# Economics prediction experiment for 2026

The experiment uses a consolidated pool of 50 economic contributions, five factual versions of each participant's profile, 25 committee simulations and 25 independent one-shot predictions. Inputs were consolidated on 7 October 2026, before the Economics announcement.

## Candidate pool

`agent-data/economics/candidates/candidates.json` is the canonical input. Its 50 entries are contributions, not individual people. Alternative credited pools may exceed three names; each proposed award must name at most three unique people in total. The Claude draft of 156 entries is preserved. `consolidation_audit.json` records every source entry's disposition. The Codex research supplement identifies the additional research used in the merge; the earlier independent broad conversation draft was not saved as an original file.

Related contributions are consolidated to reduce duplicate candidacies. Distinct contributions by the same economist can remain separate. Historical contributors and previously honoured laureates stay outside prospective credit pools. Committee members and committee-centred achievements are excluded. Some retained entries are adjacent to previous prizes; overlap notes explain the boundary. The pool is an editorial coverage choice and does not encode nomination frequency or predicted odds.

## Committee simulations

All 11 people on the existing Economics roster participate, including secretary Per Krusell and the co-opted participants. **All 11 vote by modeling assumption; majority is six.** This does not establish actual voting rights. John Hassler chairs. Royal Swedish Academy ratification and external expert reports are outside the simulation. Disclosed professional connections are recorded; recusals are not adjudicated, consistent with the earlier experiments.

Five neutral factual profile versions preserve the same retained biography, research record, public statements, professional connections and source caveats. Version 1 is the factual baseline; versions 2–5 change headings, section order and bullet presentation. Persona instructions and speculation about private preferences are removed uniformly. Original profiles remain intact. The profile manifest records source hashes, omitted blocks and every generated hash.

| Simulations | Profile version | Repetitions |
|---|---|---|
| 01–05 | 1 | 5 |
| 06–10 | 2 | 5 |
| 11–15 | 3 | 5 |
| 16–20 | 4 | 5 |
| 21–25 | 5 | 5 |

The committee model is **GPT-5.6 Terra, high reasoning effort**. Each simulation uses a distinct deterministic candidate shuffle and blinded ballot IDs. Source provenance, merge decisions and canonical IDs are hidden from participants. Candidate, profile and prompt hashes are frozen before dispatch. Each stage receives only its permitted evidence in a fresh isolated tools-disabled session:

1. Eleven opening assessments each rank eight candidates.
2. A deterministic shortlist retains candidates ranked in the top eight by at least three participants, with the established eight-to-fifteen fallback/cap rules.
3. Eleven first-round discussions propose coherent recipient configurations.
4. The chair summarizes the first round without ruling.
5. Eleven second-round discussions respond to other participants.
6. A deterministic slate collects distinct configurations and includes no award.
7. Eleven private final ballots rank the slate; instant-runoff voting determines the result, using the established tie rules.

There are 45 model requests per complete simulation, or 1,125 requests for 25 simulations before validation retries. Three participant requests run concurrently. Invalid outputs are retained in the runtime audit and retried within the existing limit; accepted stages are resumed without repetition. Aggregate results preserve separate credit configurations and report both pooled frequencies and equal weight across the five profile versions.

## One-shot predictions

The one-shot model is **GPT-6.1 Sol, high reasoning effort**. Each of the 25 predictions starts a fresh conversation in an empty temporary directory. Tools, browsing, candidate files, committee profiles, prior answers and local instructions are disabled. The exact input is:

> Who will win the 2026 Nobel Prize in Economic Sciences? Predict the prize: the contribution, and the one to three laureates. Answer from your own knowledge only; do not search the web or read any files.

Raw responses, runtime events, request identities, token use and source hashes are saved. Primary-pick transcription is a separate clerical step bound to exact source excerpts; it does not add model requests or replace the raw answers. One-shot outputs are not constrained to the 50-entry committee pool.

### Additional Terra one-shot predictions

On 9 October 2026, an additional batch of **25 GPT-5.6 Terra one-shots at high reasoning effort** was requested to match the committee agents' model and reasoning setting. It uses the exact same question and prompt bytes as the Sol batch, with the same fresh-session, tools-disabled protocol and three concurrent requests. Candidate lists, profiles, committee discussions and earlier predictions are not supplied. The original Sol batch remains a separate arm.

The Terra arm is `economics-oneshot-gpt-5.6-terra-high-v1`. Requests, raw responses, execution records and source-bound transcriptions are saved under `results/economics/oneshot/gpt-5.6-terra/pred-NNN/`. Use `launch_economics_oneshot_terra.py` to resume missing responses and `transcribe_economics_oneshot_terra.py` to validate the clerical transcription map after all 25 responses are available.

## Results and resumption

Committee results live in `results/economics/committee/gpt-5.6-terra/sim-NN/`. `terra_committee_progress.json` and `terra_committee_summary.json` track execution and completed decisions. One-shot outputs live in `results/economics/oneshot/gpt-6.1-sol/pred-NNN/`.

Use `run_economics_committee_codex.py run --sims 1-25 --candidates agent-data/economics/candidates/candidates.json --jobs 3 --max-attempts 2` to resume the frozen committee batch. Use `launch_economics_oneshot.py` to resume missing one-shot responses. Existing validated outputs are reused.
