from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
COMMITTEE = ROOT / "agent-data" / "physics" / "committee"
MEMBERS = (
    "danielsson-ulf",
    "eriksson-olle",
    "johansson-goran",
    "kroll-stefan",
    "lindroth-eva",
    "mehlig-bernhard",
    "olsson-eva",
    "pearce-mark",
)


class CommitteeProfileTests(unittest.TestCase):
    def test_profiles_are_versioned_in_each_member_directory(self) -> None:
        for member in MEMBERS:
            directory = COMMITTEE / member
            self.assertTrue((directory / "profile_v1.md").is_file(), member)
            self.assertTrue((directory / "profile_v2.md").is_file(), member)
            self.assertFalse((directory / "profile.md").exists(), member)

    def test_v2_profiles_use_factual_conditioning(self) -> None:
        forbidden = (
            "you prefer",
            "you value",
            "you respect",
            "you care about",
            "you tend to",
            "you are drawn to",
            "you are wary",
            "you are sceptical",
            "in discussion you",
            "likely vote",
        )
        for member in MEMBERS:
            text = (COMMITTEE / member / "profile_v2.md").read_text(
                encoding="utf-8"
            )
            lowered = text.lower()
            self.assertIn("## Attributed public statements", text, member)
            self.assertIn("Treat this record as factual context only.", text, member)
            for phrase in forbidden:
                self.assertNotIn(phrase, lowered, f"{member}: {phrase}")


if __name__ == "__main__":
    unittest.main()
