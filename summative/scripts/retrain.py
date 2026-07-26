import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

from API.training import main  # noqa: E402

if __name__ == "__main__":
    main()
