PUBLIC_FEATURES = [
    "graduation_year",
    "education_level",
    "course_group",
    "first_job_level",
    "first_job_sector",
    "qualification_requirement",
    "first_job_via_nysc",
    "course_preparation_score",
    "employability_skill_count",
    "problem_solving_skill",
    "communication_skill",
]

MODEL_FEATURES = PUBLIC_FEATURES
TARGET = "first_monthly_income_ngn"

NUMERIC_FEATURES = [
    "graduation_year",
    "course_preparation_score",
    "employability_skill_count",
    "problem_solving_skill",
    "communication_skill",
]
CATEGORICAL_FEATURES = [
    feature for feature in MODEL_FEATURES if feature not in NUMERIC_FEATURES
]

EDUCATION_LEVELS = {
    "Ordinary National Diploma (OND)",
    "Higher National Diploma (HND)",
    "Bachelor's degree",
    "Master's degree",
    "MBA degree",
    "PhD/Doctorate degree",
}

COURSE_GROUPS = {
    "Technology and computing",
    "Engineering and built environment",
    "Business and economics",
    "Health and life sciences",
    "Social sciences",
    "Arts, communication and humanities",
    "Law",
    "Education",
    "Other",
}

JOB_LEVELS = {
    "Entry level",
    "Clerical and administrative",
    "Experienced/professional",
    "Managerial",
    "Executive",
}

SECTOR_GROUPS = {
    "Technology and telecommunications",
    "Finance and consulting",
    "Engineering, construction and energy",
    "Education",
    "Health",
    "Media, marketing and creative",
    "Public and nonprofit",
    "Trade and services",
    "Other",
}

QUALIFICATION_REQUIREMENTS = {
    "Formal requirement",
    "Gave an advantage",
    "Not required",
    "Unknown",
}

NYSC_PATHWAYS = {
    "Yes",
    "No",
    "Not completed",
}
