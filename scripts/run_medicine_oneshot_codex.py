#!/usr/bin/env python3
"""Run the 60 zero-context GPT-6 Sol Medicine predictions through Codex CLI."""

import medicine_oneshot as medicine
import run_physics_oneshot_codex as dispatcher


dispatcher.protocol = medicine.shared


if __name__ == "__main__":
    dispatcher.main()
