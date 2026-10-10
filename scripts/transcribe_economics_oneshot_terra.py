"""Validate source-bound clerical transcriptions of the 25 Terra forecasts.

Reuse the established validator in a private module; preserve the Sol arm.
This step makes no model requests.
"""
import importlib.util
from pathlib import Path

import economics_oneshot_terra as protocol

_SPEC = importlib.util.spec_from_file_location(
    '_economics_terra_transcription',
    Path(__file__).with_name('transcribe_economics_oneshot_sol.py'),
)
assert _SPEC and _SPEC.loader
transcriber = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(transcriber)
transcriber.protocol = protocol

if __name__ == '__main__':
    transcriber.main()
