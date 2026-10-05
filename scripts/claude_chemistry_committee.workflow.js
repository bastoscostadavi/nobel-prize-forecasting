export const meta = {
  name: 'chemistry-committee-claude',
  description: 'Run Claude Chemistry committee simulations: openings, shortlist, two discussion rounds with chair summary, slate, final ballots, tally',
  phases: [
    { title: 'Opening', detail: '8 private opening rankings per simulation' },
    { title: 'Round 1', detail: '8 statements per simulation' },
    { title: 'Chair', detail: 'chair synthesis of round 1' },
    { title: 'Round 2', detail: '8 statements per simulation' },
    { title: 'Final ballots', detail: '8 private exhaustive ballots per simulation' },
    { title: 'Coordinator', detail: 'deterministic shortlist, slate and tally scripts' },
  ],
}

// args: { sims: ["results/chemistry/committee/claude/sim-NN", ...], list_id: "<list_id from metadata.json>", model: "sonnet", effort: "high", }
const ROOT = '/Users/davicosta/Desktop/projects/nobel-prize-forecasting'
const MEMBERS = [
  'aili-daniel', 'aqvist-johan', 'brzezinski-peter', 'chabes-andrei',
  'linke-heiner', 'somfai-peter', 'sparr-emma', 'zou-xiaodong',
]
const CHAIR = 'linke-heiner'
const PROMPT = {
  opening: 'prompts/chemistry_committee_claude_opening_v1.md',
  round1: 'prompts/chemistry_committee_claude_round1_v1.md',
  chair: 'prompts/chemistry_committee_claude_chair_summary_v1.md',
  round2: 'prompts/chemistry_committee_claude_round2_v1.md',
  final: 'prompts/chemistry_committee_claude_final_ballot_v1.md',
}
const OUTPUT = {
  opening: m => `opening/${m}.json`,
  round1: m => `round1/${m}.json`,
  chair: () => 'chair_summary_round1.json',
  round2: m => `round2/${m}.json`,
  final: m => `final_ballots/${m}.json`,
}
// Profile file per arm; claude-terra-vN arms use the neutral GPT-made variants.
const PROFILE = { claude: 'profile.md', 'claude-terra-v1': 'profile_terra_v1.md', 'claude-terra-v2': 'profile_terra_v2.md',
  'claude-terra-v3': 'profile_terra_v3.md', 'claude-terra-v4': 'profile_terra_v4.md', 'claude-terra-v5': 'profile_terra_v5.md' }
const PHASE = { opening: 'Opening', round1: 'Round 1', chair: 'Chair', round2: 'Round 2', final: 'Final ballots' }

const MEMBER_RESULT = {
  type: 'object',
  properties: {
    ok: { type: 'boolean', description: 'true only if the self-check command printed OK' },
    runtime_model: { type: 'string', description: 'The exact model ID you are running as, from your own system information' },
    note: { type: 'string' },
  },
  required: ['ok', 'runtime_model', 'note'],
}
const COORD_RESULT = {
  type: 'object',
  properties: { ok: { type: 'boolean' }, output: { type: 'string' } },
  required: ['ok', 'output'],
}

const parse = sim => {
  const m = sim.match(/results\/chemistry\/committee\/(claude[^/]*)\/(sim-\d+)$/)
  if (!m || !args.list_id) throw new Error(`bad Chemistry sim path or missing list_id: ${sim}`)
  const arm = m[1]
  return { list: args.list_id, run: 1, arm, simId: m[2] }
}

const memberPrompt = (stage, sim, member) => {
  const { list, run, arm, simId } = parse(sim)
  const profile = PROFILE[arm]
  if (!profile) throw new Error(`no profile file for arm ${arm}`)
  return `Work in ${ROOT}. You are the simulated committee member "${member}" (Nobel Committee for Chemistry, 2026).

Read the protocol ${PROMPT[stage]} and follow it exactly. Assignment:
- SIM (simulation directory): ${sim}
- list_id: ${list}
- run: ${run}
- simulation_id: ${simId}
- member_id: ${member}
- your profile: agent-data/chemistry/committee/${member}/${profile}${profile === 'profile.md' ? '' : ' (for this simulation, this file stands in for the profile.md the protocol names; read it and not profile.md)'}
- your output file: ${sim}/${OUTPUT[stage](member)}
- model metadata: copy committee_model and reasoning_effort from ${sim}/metadata.json

Read only the files the protocol allows for this stage. Write only your own output file. Then run the self-check command given at the end of the protocol and fix your file until it prints OK.
Return ok (true only if the check printed OK), runtime_model (the exact model ID you are running as), and a one-line note.`
}

const coordinator = (sim, command, phase) =>
  agent(`Work in ${ROOT}. Run exactly this command and nothing else, then report: \`python3 scripts/claude_chemistry_committee.py ${command} ${sim}\`. Do not edit any file. Return ok=true only if every printed line starts with "OK", and output = the command's full output.`,
    { label: `${command}: ${sim.split('/').slice(2, 4).join('/')}/${parse(sim).simId}`, phase: 'Coordinator', schema: COORD_RESULT, model: 'sonnet', effort: 'low' })
    .then(r => {
      if (!r || !r.ok) throw new Error(`${command} failed for ${sim}: ${r ? r.output : 'no result'}`)
      return r
    })

const runtimeModels = {}
const stage = (sim, name, members) =>
  parallel(members.map(member => () =>
    agent(memberPrompt(name, sim, member), {
      label: `${name}: ${parse(sim).list}/run-${parse(sim).run}/${parse(sim).simId}/${member}`,
      phase: PHASE[name], schema: MEMBER_RESULT, model: args.model, effort: args.effort,
    }))).then(results => {
      results.forEach(r => { if (r) runtimeModels[r.runtime_model] = (runtimeModels[r.runtime_model] || 0) + 1 })
      const bad = results.map((r, i) => (!r || !r.ok) ? members[i] : null).filter(Boolean)
      if (bad.length) throw new Error(`${name} failed for ${sim}: ${bad.join(', ')}`)
      return results
    })

// args.state[sim] (optional, for resuming): members whose validated file already exists per stage
// ({opening, round1, chair, round2, final}: [member ids]) and whether shortlist / slate already validate.
// args.keep_openings[sim] is the older form covering openings only.
// state keys may be the full sim path or the short form <list>/run-<n>/sim-XX
const short = sim => sim.replace(/^results\/chemistry\/committee\//, '')
const st = sim => ((args.state || {})[sim]) || ((args.state || {})[short(sim)]) || { opening: ((args.keep_openings || {})[sim]) || [] }
const todo = (sim, name, members) => {
  const done = st(sim)[name] || []
  return done === '*' ? [] : members.filter(m => !done.includes(m))
}
const skipIf = (flag, fn) => (flag ? Promise.resolve({ ok: true, output: 'already validated' }) : fn())

const results = await pipeline(
  args.sims,
  sim => stage(sim, 'opening', todo(sim, 'opening', MEMBERS)),
  (_, sim) => skipIf(st(sim).shortlist, () => coordinator(sim, 'shortlist', 'Coordinator')),
  (_, sim) => stage(sim, 'round1', todo(sim, 'round1', MEMBERS)),
  (_, sim) => stage(sim, 'chair', todo(sim, 'chair', [CHAIR])),
  (_, sim) => stage(sim, 'round2', todo(sim, 'round2', MEMBERS)),
  (_, sim) => skipIf(st(sim).slate, () => coordinator(sim, 'slate', 'Coordinator')),
  (_, sim) => stage(sim, 'final', todo(sim, 'final', MEMBERS)),
  (_, sim) => coordinator(sim, 'tally', 'Coordinator'),
  (_, sim) => coordinator(sim, 'validate', 'Coordinator').then(r => ({ sim, output: r.output })),
)
const done = results.filter(Boolean)
const failed = args.sims.filter((sim, i) => !results[i])
log(`complete: ${done.length}/${args.sims.length}; runtime models: ${JSON.stringify(runtimeModels)}`)
return { complete: done, failed, runtime_models: runtimeModels }
