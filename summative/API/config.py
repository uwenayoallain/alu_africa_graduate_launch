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
