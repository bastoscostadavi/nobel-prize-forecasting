#!/usr/bin/env python3
"""Summarize the completed GPT-6 Luna Physics committee sensitivity arm.

This configures the shared deterministic committee summarizer for the Luna
cohort. It reads only validated saved decisions and never calls a model.
"""

from __future__ import annotations

import summarize_terra_committees as shared


shared.MODEL = "gpt-6-luna"
shared.COHORT_DIRECTORY = "gpt-6-luna"
shared.REASONING = "high"
shared.DISPLAY_NAME = "Luna"
shared.ARM_ID = "physics-committee-gpt-6-luna-high-v1"
shared.RUNTIME_DIRECTORY = "luna_committee_runtime"
shared.EXPECTED_COUNT = 60
shared.OUTPUT_JSON = shared.RESULTS / "luna_committee_summary.json"
shared.OUTPUT_CSV = shared.RESULTS / "luna_committee_summary.csv"


if __name__ == "__main__":
    shared.write_summary()
