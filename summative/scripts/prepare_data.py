from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[1]
RAW_PATH = PROJECT_DIR / "data" / "raw" / "graduate_survey_2018.csv"
CLEAN_PATH = PROJECT_DIR / "data" / "africa_graduate_first_income.csv"


def income_midpoint(value: object) -> float | None:
    text = str(value)
    if not text or text == "nan":
        return None
    numbers = [int(item.replace(",", "")) for item in re.findall(r"\d[\d,]*", text)]
    if text.startswith("Under") and numbers:
        return numbers[0] / 2
    if "and more" in text and numbers:
        return numbers[0] + 25_000
    if len(numbers) >= 2:
        return (numbers[0] + numbers[1] + 1) / 2
    return None


def group_course(value: object) -> str:
    text = str(value).lower()
    if any(
        term in text
        for term in (
            "computer",
            "information",
            "software",
            "data",
            "mathematics",
            "statistics",
        )
    ):
        return "Technology and computing"
    if any(
        term in text
        for term in (
            "engineering",
            "architecture",
            "building",
            "quantity survey",
            "estate",
            "geology",
            "surveying",
        )
    ):
        return "Engineering and built environment"
    if any(
        term in text
        for term in (
            "business",
            "account",
            "econom",
            "finance",
            "management",
            "marketing",
            "banking",
            "insurance",
        )
    ):
        return "Business and economics"
    if any(
        term in text
        for term in (
            "medicine",
            "medical",
            "nursing",
            "pharmacy",
            "health",
            "biology",
            "biochemistry",
            "microbiology",
            "chemistry",
            "agric",
        )
    ):
        return "Health and life sciences"
    if any(
        term in text
        for term in (
            "political",
            "psychology",
            "sociology",
            "international",
            "public administration",
            "geography",
        )
    ):
        return "Social sciences"
    if "law" in text:
        return "Law"
    if "education" in text:
        return "Education"
    if any(
        term in text
        for term in (
            "communication",
            "english",
            "history",
            "language",
            "literature",
            "art",
            "philosophy",
            "relig",
            "theatre",
        )
    ):
        return "Arts, communication and humanities"
    return "Other"


def group_sector(value: object) -> str:
    text = str(value).lower()
    if any(term in text for term in ("technology", "telecommunication", "ecommerce", "internet")):
        return "Technology and telecommunications"
    if any(term in text for term in ("bank", "financial", "consult", "insurance")):
        return "Finance and consulting"
    if any(
        term in text
        for term in ("engineering", "construction", "real estate", "oil", "gas", "mining", "power")
    ):
        return "Engineering, construction and energy"
    if "education" in text:
        return "Education"
    if any(term in text for term in ("health", "pharma")):
        return "Health"
    if any(term in text for term in ("media", "advert", "marketing", "creative", "art", "design")):
        return "Media, marketing and creative"
    if any(term in text for term in ("government", "defence", "ngo", "nonprofit")):
        return "Public and nonprofit"
    if any(
        term in text
        for term in ("trade", "service", "hospitality", "travel", "transport", "manufacturing")
    ):
        return "Trade and services"
    return "Other"


def normalize_education(value: object) -> str:
    text = str(value)
    if text == "PhDs/Doctorate Degree":
        return "PhD/Doctorate degree"
    return text


def normalize_job_level(value: object) -> str:
    text = str(value)
    if text in {"Experience", "Experience/Professional"}:
        return "Experienced/professional"
    if text == "Executive Director":
        return "Executive"
    return text


def normalize_qualification(value: object) -> str:
    text = str(value)
    if text.startswith("Yes: the qualification was a formal"):
        return "Formal requirement"
    if "give me an advantage" in text:
        return "Gave an advantage"
    if text.startswith("No:"):
        return "Not required"
    return "Unknown"


def normalize_nysc(value: object) -> str:
    text = str(value)
    if text == "I have not completed my NYSC":
        return "Not completed"
    if text in {"Yes", "No"}:
        return text
    return "Not completed"


def prepare_dataframe(raw: pd.DataFrame) -> pd.DataFrame:
    columns = raw.columns
    income = raw[columns[14]].map(income_midpoint)
    data = raw.loc[income.notna()].copy()
    skills = data[columns[35]].fillna("")
    skill_count = skills.map(
        lambda value: 0
        if value == "None of the above"
        else len([item for item in value.split(",") if item.strip()])
    )
    preparation_map = {
        "Strongly Disagree": 1,
        "Disagree": 2,
        "Agree": 3,
        "Strongly Agree": 4,
        "No": 1,
    }

    clean = pd.DataFrame(
        {
            "graduation_year": pd.to_numeric(data[columns[2]], errors="coerce"),
            "education_level": data[columns[5]].map(normalize_education),
            "course_group": data[columns[3]].map(group_course),
            "first_job_level": data[columns[11]].map(normalize_job_level),
            "first_job_sector": data[columns[13]].map(group_sector),
            "qualification_requirement": data[columns[15]].map(normalize_qualification),
            "first_job_via_nysc": data[columns[10]].map(normalize_nysc),
            "course_preparation_score": data[columns[33]].map(preparation_map),
            "employability_skill_count": skill_count.clip(0, 6),
            "problem_solving_skill": skills.str.contains(
                "solve complex problems", case=False, regex=False
            ),
            "communication_skill": skills.str.contains(
                "communication skills", case=False, regex=False
            ),
            "first_monthly_income_ngn": income.loc[data.index],
        }
    )
    clean = clean.dropna().reset_index(drop=True)
    clean["graduation_year"] = clean["graduation_year"].astype(int)
    clean["course_preparation_score"] = clean["course_preparation_score"].astype(int)
    clean["employability_skill_count"] = clean["employability_skill_count"].astype(int)
    clean["problem_solving_skill"] = clean["problem_solving_skill"].astype(int)
    clean["communication_skill"] = clean["communication_skill"].astype(int)
    return clean


def main() -> None:
    if not RAW_PATH.exists():
        raise SystemExit("Raw survey missing. Run `uv run python scripts/download_data.py`.")
    raw = pd.read_csv(RAW_PATH).drop_duplicates()
    clean = prepare_dataframe(raw)
    CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    clean.to_csv(CLEAN_PATH, index=False)
    print(f"Prepared {len(clean):,} labelled first-employment records.")
    tech_rows = (
        clean["first_job_sector"] == "Technology and telecommunications"
    ).sum()
    print(f"Technology pathway rows: {tech_rows:,}.")
    print(f"Saved {CLEAN_PATH}")


if __name__ == "__main__":
    main()
