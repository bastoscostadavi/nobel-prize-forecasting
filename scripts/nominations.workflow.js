export const meta = {
  name: 'physics-nominations',
  description: 'Simulate Nobel Physics 2026 nominations: 100 persona nominators per run, then merge into a candidate list',
  phases: [
    { title: 'Nominate', detail: 'one agent per nominator per run' },
    { title: 'Merge', detail: 'one agent per run groups nominations into candidates' },
  ],
}

const ROOT = '/Users/davicosta/Desktop/projects/nobel-prize-forecasting'
const LIST = args.list
const PROFILES = `${ROOT}/agent-data/physics/nominators/${LIST}`

const NOMINATION = {
  type: 'object',
  properties: {
    discovery: { type: 'string', description: 'Short title of the discovery or invention' },
    nominees: {
      type: 'array', minItems: 1, maxItems: 3,
      items: {
        type: 'object',
        properties: { name: { type: 'string' }, affiliation: { type: 'string' } },
        required: ['name', 'affiliation'],
      },
    },
    subfield: { type: 'string' },
    motivation: { type: 'string', description: 'At most 150 words' },
  },
  required: ['discovery', 'nominees', 'subfield', 'motivation'],
}

const MERGE = {
  type: 'object',
  properties: {
    n_nominations: { type: 'integer' },
    n_candidates: { type: 'integer' },
    top: {
      type: 'array',
      items: {
        type: 'object',
        properties: { discovery: { type: 'string' }, nominees: { type: 'string' }, n_nominations: { type: 'integer' } },
        required: ['discovery', 'nominees', 'n_nominations'],
      },
    },
  },
  required: ['n_nominations', 'n_candidates', 'top'],
}

const nominatePrompt = (slug, run) => `Read your profile at ${PROFILES}/${slug}/profile.md. You are the person described there. Use only the Read tool (for that one file) and the Write tool (for your nomination file). Do not use web search, web fetch, or read any other file.

It is January 2026. You have received a confidential invitation from the Nobel Committee for Physics to nominate candidates for the 2026 Nobel Prize in Physics. The deadline is 31 January 2026.

Rules for a valid nomination:
- One discovery or invention, with at most three nominees who share it.
- Nominees must be living. You cannot nominate yourself.
- Base it only on what you would know as of January 2026.

Nominate as this person would: draw on their field, expertise, taste and connections as described in the profile. Write a motivation of at most 150 words.

Save your nomination as JSON to ${ROOT}/results/physics/${LIST}/run-${run}/nominations/${slug}.json with keys: nominator ("${slug}"), discovery, nominees (list of {name, affiliation}), subfield, motivation. Then return the same nomination.`

const mergePrompt = (run) => `Merge the Nobel Physics nominations of one simulated run into a candidate list.

Input: every JSON file in ${ROOT}/results/physics/${LIST}/run-${run}/nominations/ (one nomination per file, written by a nominator agent). Read them all (e.g. with Bash: cat). Do not use the web.

Group nominations that refer to the same discovery, even if worded differently or naming different subsets of people. For each group (a candidate):
- discovery: a clear canonical title
- nominees: the up to 3 people named most often for it (ties: keep the earliest-named), separated by "; "
- other_names: any other people named in that group, "; "-separated (empty if none)
- subfield
- n_nominations: number of nominations in the group
- nominators: the nominator slugs, "; "-separated

Write ${ROOT}/results/physics/${LIST}/run-${run}/candidates.csv with header candidate_id,discovery,nominees,other_names,subfield,n_nominations,nominators, sorted by n_nominations descending (candidate_id = c01, c02, ...). Quote fields properly. Every nomination file must appear in exactly one group.

Return n_nominations (files read), n_candidates, and the top 10 candidates.`

const runs = args.runs
const results = await pipeline(
  runs,
  // args.skip[run] = number of leading slugs (alphabetical) whose nomination file already exists for that run
  (run) => parallel(args.slugs.slice((args.skip || {})[run] || 0).map(slug => () =>
    agent(nominatePrompt(slug, run), { label: `run ${run}: ${slug}`, phase: 'Nominate', schema: NOMINATION }))),
  (noms, run) => {
    const ok = noms.filter(Boolean).length
    log(`${LIST} run ${run}: ${ok} new nominations (${(args.skip || {})[run] || 0} already on disk)`)
    return agent(mergePrompt(run), { label: `merge run ${run}`, phase: 'Merge', schema: MERGE })
      .then(m => ({ run, returned: ok, merge: m }))
  },
)
return { list: LIST, results }
