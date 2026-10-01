export const meta = {
  name: 'physics-committee-claude',
  description: 'Run Claude physics committee simulations: openings, shortlist, two discussion rounds with chair summary, slate, final ballots, tally',
  phases: [
    { title: 'Opening', detail: '8 private opening rankings per simulation' },
    { title: 'Round 1', detail: '8 statements per simulation' },
    { title: 'Chair', detail: 'chair synthesis of round 1' },
    { title: 'Round 2', detail: '8 statements per simulation' },
    { title: 'Final ballots', detail: '8 private exhaustive ballots per simulation' },
    { title: 'Coordinator', detail: 'deterministic shortlist, slate and tally scripts' },
  ],
}

// args: { sims: ["results/physics/<list>/run-<n>/committee/claude/sim-XX", ...], model: "sonnet", effort: "high", profile_version: "v1" | "v2" }
const ROOT = '/Users/davicosta/Desktop/projects/nobel-prize-forecasting'
const MEMBERS = [
  'danielsson-ulf', 'eriksson-olle', 'johansson-goran', 'kroll-stefan',
  'lindroth-eva', 'mehlig-bernhard', 'olsson-eva', 'pearce-mark',
]
const CHAIR = 'pearce-mark'
const PROFILE_VERSION = args.profile_version || 'v2'
if (!['v1', 'v2'].includes(PROFILE_VERSION)) {
  throw new Error(`profile_version must be "v1" or "v2"; got ${JSON.stringify(PROFILE_VERSION)}`)
}
const PROMPT = {
  opening: 'prompts/physics_committee_claude_opening_v1.md',
  round1: 'prompts/physics_committee_claude_round1_v1.md',
  chair: 'prompts/physics_committee_claude_chair_summary_v1.md',
  round2: 'prompts/physics_committee_claude_round2_v1.md',
  final: 'prompts/physics_committee_claude_final_ballot_v1.md',
}
const OUTPUT = {
  opening: m => `opening/${m}.json`,
  round1: m => `round1/${m}.json`,
  chair: () => 'chair_summary_round1.json',
  round2: m => `round2/${m}.json`,
  final: m => `final_ballots/${m}.json`,
}
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
  const m = sim.match(/results\/physics\/([^/]+)\/run-(\d+)\/committee\/(claude[^/]*)\/(sim-\d+)$/)
  const arm = m[3]
  const expected = arm === 'claude-profile-v2' ? 'v2' : 'v1'
  if (expected !== PROFILE_VERSION) throw new Error(`${sim} is a profile ${expected} arm but profile_version is ${PROFILE_VERSION}`)
  return { list: m[1], run: Number(m[2]), arm, simId: m[4] }
}

const memberPrompt = (stage, sim, member) => {
  const { list, run, simId } = parse(sim)
  return `Work in ${ROOT}. You are the simulated committee member "${member}" (Nobel Committee for Physics, 2026).

Read the protocol ${PROMPT[stage]} and follow it exactly. Assignment:
- SIM (simulation directory): ${sim}
- list_id: ${list}
- run: ${run}
- simulation_id: ${simId}
- member_id: ${member}
- your profile: agent-data/physics/committee/${member}/profile_${PROFILE_VERSION}.md
- your output file: ${sim}/${OUTPUT[stage](member)}
- model metadata: copy committee_model and reasoning_effort from ${sim}/metadata.json

Where the protocol uses the legacy generic name \`profile.md\`, it means the assigned \`profile_${PROFILE_VERSION}.md\` path above.
Read only the files the protocol allows for this stage. Write only your own output file. Then run the self-check command given at the end of the protocol and fix your file until it prints OK.
Return ok (true only if the check printed OK), runtime_model (the exact model ID you are running as), and a one-line note.`
}

const coordinator = (sim, command, phase) =>
  agent(`Work in ${ROOT}. Run exactly this command and nothing else, then report: \`python3 scripts/claude_committee.py ${command} ${sim}\`. Do not edit any file. Return ok=true only if every printed line starts with "OK", and output = the command's full output.`,
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
const short = sim => sim.replace('results/physics/', '').replace(/\/committee\/claude[^/]*\//, '/')
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
