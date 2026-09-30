"""One-shot baseline for the nominator sample.

Asks a model, in a single call, for 100 people representative of those who
nominate for a Nobel Prize, so it can be compared with the sample built from
real data in agent-data/<category>/nominators/. Output goes to results/<category>/nominators/.

Usage: python scripts/oneshot_nominators.py [--category physics] [--model claude-opus-5-5]
"""

import argparse
import csv
import json
from datetime import date
from pathlib import Path

import anthropic

ROOT = Path(__file__).resolve().parent.parent

PROMPT = """The Nobel Prize in {prize} is decided in October 2026. Nominations were due 31 January 2026.

Produce a sample of 100 real, living people who plausibly submitted a nomination for the 2026 Nobel Prize in {prize}.
The sample should be representative of the actual population of nominations: match the mix of eligible nominator
groups (per the Nobel statutes), countries, institutions and subfields in the proportions you believe they
contribute nominations, not the proportions of fame.

Exclude members of the 2026 Nobel Committee for {prize}.
For each person give: name, institution, country, subfield, nominator group (one of: "academy_member",
"nobel_committee_member", "laureate", "nordic_professor", "invited_university_professor", "other_invited"),
and a one-sentence reason they fit the sample. Do not say whom they would nominate.
Finally, give a short note explaining how you balanced the sample."""

SCHEMA = {
    "type": "object",
    "properties": {
        "nominators": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "institution": {"type": "string"},
                    "country": {"type": "string"},
                    "subfield": {"type": "string"},
                    "group": {
                        "type": "string",
                        "enum": [
                            "academy_member",
                            "nobel_committee_member",
                            "laureate",
                            "nordic_professor",
                            "invited_university_professor",
                            "other_invited",
                        ],
                    },
                    "reason": {"type": "string"},
                },
                "required": ["name", "institution", "country", "subfield", "group", "reason"],
                "additionalProperties": False,
            },
        },
        "balancing_note": {"type": "string"},
    },
    "required": ["nominators", "balancing_note"],
    "additionalProperties": False,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--category", default="physics")
    ap.add_argument("--model", default="claude-opus-5-5")
    args = ap.parse_args()

    client = anthropic.Anthropic()
    response = client.beta.messages.create(
        model=args.model,
        max_tokens=32000,
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        output_config={"effort": "high", "format": {"type": "json_schema", "schema": SCHEMA}},
        messages=[{"role": "user", "content": PROMPT.format(prize=args.category.capitalize())}],
    )
    if response.stop_reason == "refusal":
        raise SystemExit(f"Model refused: {response.stop_details}")
    if response.stop_reason == "max_tokens":
        raise SystemExit("Hit max_tokens; output truncated")

    data = json.loads(next(b.text for b in response.content if b.type == "text"))

    out = ROOT / "results" / args.category / "nominators"
    out.mkdir(parents=True, exist_ok=True)
    stem = f"oneshot_{response.model}_{date.today().isoformat()}"
    (out / f"{stem}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False))
    with open(out / f"{stem}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(SCHEMA["properties"]["nominators"]["items"]["required"]))
        w.writeheader()
        w.writerows(data["nominators"])
    print(f"{len(data['nominators'])} nominators -> {out / stem}.csv")


if __name__ == "__main__":
    main()
