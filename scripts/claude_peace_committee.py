"""Claude model-locked entry point to the shared Peace protocol."""
import os
os.environ["NOBEL_PEACE_PROVIDER"] = "claude"
from peace_committee import main
if __name__ == "__main__":
    main()
