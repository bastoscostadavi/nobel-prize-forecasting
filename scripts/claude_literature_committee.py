"""Claude model-locked entry point to the shared Literature protocol."""
import os
os.environ["NOBEL_LITERATURE_PROVIDER"] = "claude"
from literature_committee import main
if __name__ == "__main__":
    main()
