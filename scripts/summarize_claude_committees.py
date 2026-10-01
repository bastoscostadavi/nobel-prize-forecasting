#!/usr/bin/env python3
"""Summarize the completed Claude Physics committee arm without model calls."""

from __future__ import annotations

import summarize_terra_committees as shared


shared.MODEL = "claude-sonnet-5-5"
shared.COHORT_DIRECTORY = "claude"
shared.REASONING = "high"
shared.DISPLAY_NAME = "Claude"
shared.ARM_ID = "physics-committee-claude-sonnet-5-5-high-v1"
shared.RUNTIME_DIRECTORY = "claude_committee_runtime"
shared.EXPECTED_COUNT = 60
shared.OUTPUT_JSON = shared.RESULTS / "claude_committee_summary.json"
shared.OUTPUT_CSV = shared.RESULTS / "claude_committee_summary.csv"


if __name__ == "__main__":
    shared.write_summary()
