#!/usr/bin/env python3
"""Run isolated GPT-6 Luna/high Physics committee simulations."""

from __future__ import annotations

import os


os.environ["PHYSICS_COMMITTEE_MODEL"] = "gpt-6-luna"
os.environ["PHYSICS_COMMITTEE_EFFORT"] = "high"
os.environ["PHYSICS_COMMITTEE_PROMPT_SLUG"] = "luna"
os.environ["PHYSICS_COMMITTEE_PROGRESS_SLUG"] = "luna"
os.environ["PHYSICS_COMMITTEE_RUNTIME_SLUG"] = "luna"
os.environ["PHYSICS_COMMITTEE_COORDINATOR_SCRIPT"] = "luna_committee.py"

from run_terra_committee_codex import main  # noqa: E402


if __name__ == "__main__":
    main()
