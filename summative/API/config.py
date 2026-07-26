MODEL_FEATURES = [
    "age",
    "education_level",
    "career_field",
    "main_sector",
    "employer_type",
    "contract_type",
    "weekly_hours",
    "residence",
    "province",
]

TARGET = "monthly_income_rwf"

NUMERIC_FEATURES = ["age", "weekly_hours"]
CATEGORICAL_FEATURES = [
    feature for feature in MODEL_FEATURES if feature not in NUMERIC_FEATURES
]

EDUCATION_LEVELS = {
    "No formal education",
    "Pre-primary",
    "Primary education",
    "Lower secondary education",
    "Upper secondary education",
    "Tertiary education",
}

CAREER_FIELDS = {
    "ICT",
    "Science and engineering",
    "Education, health and social services",
    "Business, management and office work",
    "Sales and services",
    "Skilled trades and operators",
    "Agriculture",
    "Elementary and other work",
}

MAIN_SECTORS = {"Agriculture", "Industry", "Services"}

EMPLOYER_TYPES = {
    "Private business or VUP",
    "Public institution",
    "Public-private enterprise",
    "Household",
    "Cooperative",
    "NGO or international organisation",
    "Other",
}

CONTRACT_TYPES = {"Oral agreement", "Written contract"}
RESIDENCE_TYPES = {"Rural", "Urban"}

PROVINCES = {
    "Kigali city",
    "Eastern Province",
    "Northern Province",
    "Southern Province",
    "Western Province",
}

EDUCATION_CAREERS = {
    "No formal education": {
        "Agriculture",
        "Elementary and other work",
    },
    "Pre-primary": {
        "Agriculture",
        "Elementary and other work",
    },
    "Primary education": {
        "Education, health and social services",
        "Sales and services",
        "Skilled trades and operators",
        "Agriculture",
        "Elementary and other work",
    },
    "Lower secondary education": {
        "Education, health and social services",
        "Sales and services",
        "Skilled trades and operators",
        "Agriculture",
        "Elementary and other work",
    },
    "Upper secondary education": CAREER_FIELDS,
    "Tertiary education": CAREER_FIELDS - {"Agriculture"},
}

CAREER_SECTORS = {
    "ICT": {"Services"},
    "Science and engineering": {"Industry", "Services"},
    "Education, health and social services": {"Services"},
    "Business, management and office work": {"Industry", "Services"},
    "Sales and services": {"Industry", "Services"},
    "Skilled trades and operators": {"Industry", "Services"},
    "Agriculture": {"Agriculture", "Industry", "Services"},
    "Elementary and other work": {"Agriculture", "Industry", "Services"},
}

EMPLOYER_CONTRACTS = {
    "Private business or VUP": {"Oral agreement", "Written contract"},
    "Public institution": {"Oral agreement", "Written contract"},
    "Public-private enterprise": {"Written contract"},
    "Household": {"Oral agreement", "Written contract"},
    "Cooperative": {"Oral agreement"},
    "NGO or international organisation": {"Oral agreement", "Written contract"},
    "Other": {"Oral agreement"},
}
