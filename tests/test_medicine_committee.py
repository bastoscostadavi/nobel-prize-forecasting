from __future__ import annotations

import contextlib
import copy
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location("medicine_protocol_test", ROOT / "scripts/medicine_committee.py")
assert SPEC and SPEC.loader
protocol = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(protocol)


class MedicineCommitteeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.results = self.root / "results/medicine/committee"
        self.patches = [mock.patch.object(protocol, "ROOT", self.root),
                        mock.patch.object(protocol, "RESULTS", self.results),
                        mock.patch.object(protocol, "MANIFEST", self.results / "terra_progress.json")]
        for patch in self.patches:
            patch.start()
        for member in protocol.MEMBERS:
            profile = self.root / f"agent-data/medicine/committee/{member}/profile.md"
            profile.parent.mkdir(parents=True)
            profile.write_text(f"Neutral documented biography of {member}.\n")
        for stage, relative in protocol.PROMPTS.items():
            prompt = self.root / relative
            prompt.parent.mkdir(parents=True, exist_ok=True)
            prompt.write_text(f"Synthetic prompt for {stage}.\n")
        self.data = {"schema_version": 1, "category": "medicine", "list_id": "alternative-list",
                     "candidate_count": 10, "candidates": [
                         {"candidate_id": f"M{i:03d}", "discovery": f"Synthetic discovery {i}",
                          "subfield": "Synthetic testing", "credited_names": [f"Zeta {i}", f"Alpha {i}"]}
                         for i in range(1, 11)]}
        self.source = self.root / "inputs/alternative.json"
        self.write(self.source, self.data)
        self.sim = self.results / protocol.COHORT / "sim-01"

    def tearDown(self):
        for patch in reversed(self.patches):
            patch.stop()
        self.temp.cleanup()

    def write(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(protocol.shared.encode(value), encoding="utf-8")

    def prepare(self, excluded=None):
        with contextlib.redirect_stdout(io.StringIO()):
            protocol.prepare(self.sim, self.source, excluded)

    def header(self, stage, member, chair=False):
        return {"schema_version": 1, "list_id": self.data["list_id"], "run": 1,
                "simulation_id": self.sim.name, "chair_id" if chair else "member_id": member,
                "model": protocol.MODEL, "reasoning_effort": protocol.EFFORT,
                "prompt": protocol.PROMPTS[stage]}

    def test_model_roster_and_module_isolation(self):
        import claude_committee
        self.assertEqual(len(protocol.MEMBERS), 6)
        self.assertEqual(protocol.CHAIR, "svenningsson-per")
        self.assertEqual(protocol.MODEL, "gpt-5.6-terra")
        self.assertEqual(protocol.EFFORT, "high")
        self.assertIsNot(protocol.shared, claude_committee)
        self.assertEqual(len(claude_committee.EXPECTED_MEMBERS), 8)
        with self.assertRaises(SystemExit):
            protocol.identity(self.results / "claude" / "sim-01")
        with self.assertRaises(SystemExit):
            protocol.identity(self.results / protocol.COHORT / "sim-001")

    def test_full_reviewed_pool_coverage_without_nomination_cap(self):
        list_id, candidates = protocol.load_candidates(ROOT / "agent-data/medicine/candidates/candidates.json")
        longlist, mapping = protocol._shuffle(candidates, list_id, "sim-01")
        self.assertEqual(list_id, "medicine-2026")
        self.assertEqual(len(longlist["candidates"]), 52)
        self.assertNotIn("M042", mapping["ballot_to_candidate"].values())
        self.assertEqual(set(mapping["ballot_to_candidate"].values()), {c["candidate_id"] for c in candidates})
        by_id = {c["candidate_id"]: c for c in candidates}
        for entry in longlist["candidates"]:
            cid = mapping["ballot_to_candidate"][entry["ballot_id"]]
            self.assertEqual(set(entry["credited_names"]), set(by_id[cid]["credited_names"]))
            self.assertEqual(set(entry), {"ballot_id", "discovery", "subfield", "credited_names"})
        self.assertGreater(max(len(c["credited_names"]) for c in longlist["candidates"]), 3)

    def test_default_is_current_canonical_list(self):
        canonical = self.root / "agent-data/medicine/candidates/candidates.json"
        self.assertEqual(protocol.default_candidates(), canonical)
        self.write(canonical, self.data)
        self.write(self.root / "results/medicine/candidates.json", {"invalid": True})
        packet, _, metadata = protocol.build_packet(self.sim)
        self.assertEqual(len(packet["candidates"]), 10)
        self.assertEqual(metadata["candidate_input"], "agent-data/medicine/candidates/candidates.json")
        self.assertEqual(metadata["excluded_candidates"], [])

    def test_shuffle_determinism_and_simulation_seeds(self):
        one = protocol.build_packet(self.sim, self.source)
        reordered = copy.deepcopy(self.data)
        reordered["candidates"].reverse()
        for candidate in reordered["candidates"]:
            candidate["credited_names"].reverse()
        self.write(self.source, reordered)
        two = protocol.build_packet(self.sim, self.source)
        self.assertEqual(one[:2], two[:2])
        self.assertNotEqual(one[2]["candidate_input_sha256"], two[2]["candidate_input_sha256"])
        self.assertEqual(one[2]["seed_label"], "medicine-committee-gpt-5.6-terra-v1:alternative-list/sim-01")
        other = protocol.build_packet(self.sim.with_name("sim-02"), self.source)
        self.assertNotEqual(one[1]["shuffle"], other[1]["shuffle"])
        self.assertNotEqual(one[0], other[0])

    def test_exclusion_is_explicit_and_preserves_remaining_coverage(self):
        all_packet, _, metadata = protocol.build_packet(self.sim, self.source)
        selected, mapping, metadata_excluded = protocol.build_packet(self.sim, self.source, ["M005"])
        self.assertEqual(metadata["excluded_candidates"], [])
        self.assertEqual(len(all_packet["candidates"]), 10)
        self.assertEqual(len(selected["candidates"]), 9)
        self.assertEqual(metadata_excluded["excluded_candidates"], ["M005"])
        self.assertNotIn("M005", mapping["ballot_to_candidate"].values())
        self.prepare(["M005"])
        self.assertEqual(len(protocol.check_packet(self.sim)), 9)
        with self.assertRaises(SystemExit):
            protocol.build_packet(self.sim, self.source, ["M999"])
        with self.assertRaises(SystemExit):
            protocol.build_packet(self.sim, self.source, ["M001", "M002", "M003"])

    def test_strict_names_ids_and_counts(self):
        for modify in (
            lambda d: d["candidates"][0].update(credited_names=[{}]),
            lambda d: d["candidates"][0].update(credited_names=["A", "A"]),
            lambda d: d["candidates"][0].update(candidate_id="M002"),
            lambda d: d.update(candidate_count=9),
            lambda d: d.update(category="physics"),
            lambda d: d.update(list_id=""),
        ):
            with self.subTest(modify=modify):
                invalid = copy.deepcopy(self.data)
                modify(invalid)
                self.write(self.source, invalid)
                with self.assertRaises(SystemExit):
                    protocol.load_candidates(self.source)

    def test_source_and_profile_hashes_freeze_inputs_at_every_stage(self):
        self.prepare()
        metadata = protocol.shared.load_json(self.sim / "metadata.json")
        self.assertEqual(metadata["candidate_input"], "inputs/alternative.json")
        self.assertEqual(set(metadata["profile_inputs"]), protocol.MEMBERS)
        self.assertEqual(metadata["candidate_input_sha256"], protocol.sha256(self.source))
        self.source.write_text(self.source.read_text() + " ")
        for stage in (lambda: protocol.check_packet(self.sim),
                      lambda: protocol.shared.check_chair(self.sim),
                      lambda: protocol.shared.check_final(self.sim, "svenningsson-per"),
                      lambda: protocol.check_round(self.sim, 1, "svenningsson-per")):
            with self.assertRaises(SystemExit):
                stage()
        self.write(self.source, self.data)
        profile = self.root / metadata["profile_inputs"]["svenningsson-per"]["path"]
        profile.write_text(profile.read_text() + "changed")
        with self.assertRaisesRegex(SystemExit, "profile sources changed"):
            protocol.check_packet(self.sim)

    def test_prompt_hashes_are_frozen(self):
        self.prepare()
        metadata = protocol.shared.load_json(self.sim / "metadata.json")
        self.assertEqual(set(metadata["prompt_inputs"]), set(protocol.PROMPTS))
        prompt = self.root / protocol.PROMPTS["opening"]
        prompt.write_text(prompt.read_text() + "changed")
        with self.assertRaisesRegex(SystemExit, "prompt sources changed"):
            protocol.shared.check_opening(self.sim, "svenningsson-per")

    def test_prepared_and_dispatched_packets_cannot_be_overwritten(self):
        self.prepare()
        self.prepare()
        self.write(self.sim / "opening/svenningsson-per.json", {})
        self.data["candidates"][0]["discovery"] = "Changed discovery"
        self.write(self.source, self.data)
        with self.assertRaisesRegex(SystemExit, "refusing to replace prepared input"):
            self.prepare()

    def test_tampered_crosswalk_rejected(self):
        self.prepare()
        mapping = protocol.shared.load_json(self.sim / "ballot_map.json")
        mapping["ballot_to_candidate"]["B001"] = "M999"
        self.write(self.sim / "ballot_map.json", mapping)
        with self.assertRaises(SystemExit):
            protocol.check_packet(self.sim)

    def test_complete_pipeline_winner_uses_nondefault_input(self):
        # Poison the default source to detect accidental fallback during tally.
        default = copy.deepcopy(self.data)
        default["list_id"] = "wrong-list"
        for candidate in default["candidates"]:
            candidate["candidate_id"] = "wrong-" + candidate["candidate_id"]
        self.write(self.root / "agent-data/medicine/candidates/candidates.json", default)
        self.prepare()
        longlist = protocol.shared.load_json(self.sim / "longlist.json")["candidates"]
        for member in sorted(protocol.MEMBERS):
            opening = {**self.header("opening", member), "rankings": [
                {"rank": i, "ballot_id": c["ballot_id"], "proposed_laureates": c["credited_names"][:1],
                 "assessment": {"nobel_worthiness": "Synthetic", "attribution": "Synthetic",
                                "maturity": "Synthetic", "uncertainties": []}}
                for i, c in enumerate(longlist[:8], start=1)]}
            self.write(self.sim / f"opening/{member}.json", opening)
        shortlist = protocol.shared.build_shortlist(self.sim)
        self.write(self.sim / "shortlist.json", shortlist)
        selected = shortlist["shortlist"][0]
        for stage in ("round1", "round2"):
            for member in sorted(protocol.MEMBERS):
                others = sorted(protocol.MEMBERS - {member})[:2]
                statement = {"case_for": "Synthetic", "case_against": "Synthetic", "uncertainties": [],
                             "conflict_note": "No synthetic conflict", "responses": [
                                 {"member_id": other, "point": "Synthetic", "response": "Synthetic"} for other in others]}
                self.write(self.sim / stage / f"{member}.json", {**self.header(stage, member),
                    "preferred_configuration": {"prize_parts": [{"ballot_id": selected["ballot_id"],
                        "laureates": selected["credited_names"][:1], "citation": "For synthetic testing"}]},
                    "alternatives": [], "statement": statement})
        self.write(self.sim / "chair_summary_round1.json", {**self.header("chair", protocol.CHAIR, True),
            "summary": {"leading_positions": [{"ballot_ids": [selected["ballot_id"]],
                        "explicit_supporters": sorted(protocol.MEMBERS), "synthesis": "Synthetic"}],
                        "areas_of_agreement": ["Synthetic"], "scientific_disputes": [], "attribution_disputes": [],
                        "maturity_disputes": [], "conflict_or_recusal_flags": [],
                        "questions_for_round2": ["Synthetic one", "Synthetic two"], "chair_observation": "Synthetic"}})
        slate = protocol.build_slate(self.sim)
        self.write(self.sim / "proposal_slate.json", slate)
        for member in protocol.MEMBERS:
            self.write(self.sim / "final_ballots" / f"{member}.json", {**self.header("final", member),
                "ranked_proposal_ids": ["P001", "P000"], "top_choice_rationale": "Synthetic", "recusal_note": "None"})
        decision = protocol.build_decision(self.sim)
        self.write(self.sim / "decision.json", decision)
        self.assertEqual(decision, protocol.validate_sim(self.sim))
        mapping = protocol.shared.load_json(self.sim / "ballot_map.json")["ballot_to_candidate"]
        self.assertEqual(decision["winner"]["prize_parts"][0]["candidate_id"], mapping[selected["ballot_id"]])
        self.assertEqual(decision["list_id"], "alternative-list")
        self.assertEqual(decision["committee_provider"], "openai")
        self.assertEqual(decision["rule"]["majority_votes"], 4)
        self.assertEqual(sum(decision["rounds"][0]["counts"].values()), 6)


if __name__ == "__main__":
    unittest.main()
