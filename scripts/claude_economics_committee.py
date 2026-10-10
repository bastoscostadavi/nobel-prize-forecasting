"""Claude model-locked entry point to the shared Economic Sciences protocol."""
import os
os.environ["NOBEL_ECONOMICS_PROVIDER"] = "claude"
from economics_committee import main
if __name__ == "__main__":
    main()
