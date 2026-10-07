#!/usr/bin/env python3
"""Run 25 independent GPT-6.1 Sol Literature forecasts, with three requests at once."""

import importlib.util
from pathlib import Path

import literature_oneshot as literature

_SPEC = importlib.util.spec_from_file_location(
    "_literature_oneshot_dispatcher", Path(__file__).with_name("run_physics_oneshot_codex.py")
)
assert _SPEC and _SPEC.loader
dispatcher = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(dispatcher)
dispatcher.protocol = literature.shared

if __name__ == "__main__":
    dispatcher.main()
