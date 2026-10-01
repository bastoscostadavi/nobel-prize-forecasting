#!/usr/bin/env python3
"""Model-locked GPT-6 Luna/high adapter for the Physics committee protocol."""

from __future__ import annotations

import os


os.environ["PHYSICS_COMMITTEE_MODEL"] = "gpt-6-luna"
os.environ["PHYSICS_COMMITTEE_EFFORT"] = "high"
os.environ["PHYSICS_COMMITTEE_PROMPT_SLUG"] = "luna"
os.environ["PHYSICS_COMMITTEE_PROGRESS_SLUG"] = "luna"

from terra_committee import main  # noqa: E402


if __name__ == "__main__":
    main()
