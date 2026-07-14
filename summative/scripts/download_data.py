"""Download the Stutern Nigerian Graduate Report survey from Kaggle."""

from __future__ import annotations

import shutil
import urllib.request
import zipfile
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_DIR / "data" / "raw"
ARCHIVE_PATH = RAW_DIR / "nigerian-graduate-report-2018.zip"
RAW_PATH = RAW_DIR / "graduate_survey_2018.csv"
DATASET_URL = (
    "https://www.kaggle.com/api/v1/datasets/download/"
    "stutern/nigerian-gradaute-report-2018"
)


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if RAW_PATH.exists():
        print(f"Dataset already exists: {RAW_PATH}")
        return

    print("Downloading the Stutern Nigerian Graduate Report survey...")
    with urllib.request.urlopen(DATASET_URL, timeout=180) as response:
        with ARCHIVE_PATH.open("wb") as archive:
            shutil.copyfileobj(response, archive)

    with zipfile.ZipFile(ARCHIVE_PATH) as archive:
        csv_member = next(name for name in archive.namelist() if name.lower().endswith(".csv"))
        with archive.open(csv_member) as source, RAW_PATH.open("wb") as destination:
            shutil.copyfileobj(source, destination)

    ARCHIVE_PATH.unlink(missing_ok=True)
    print(f"Saved {RAW_PATH}")


if __name__ == "__main__":
    main()
