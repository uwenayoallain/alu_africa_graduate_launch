from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class EducationLevel(StrEnum):
    ond = "Ordinary National Diploma (OND)"
    hnd = "Higher National Diploma (HND)"
    bachelor = "Bachelor's degree"
    master = "Master's degree"
    mba = "MBA degree"
    doctorate = "PhD/Doctorate degree"


class CourseGroup(StrEnum):
    technology = "Technology and computing"
    engineering = "Engineering and built environment"
    business = "Business and economics"
    health = "Health and life sciences"
    social = "Social sciences"
    arts = "Arts, communication and humanities"
    law = "Law"
    education = "Education"
    other = "Other"


class JobLevel(StrEnum):
    entry = "Entry level"
    clerical = "Clerical and administrative"
    experienced = "Experienced/professional"
    managerial = "Managerial"
    executive = "Executive"


class SectorGroup(StrEnum):
    technology = "Technology and telecommunications"
    finance = "Finance and consulting"
    engineering = "Engineering, construction and energy"
    education = "Education"
    health = "Health"
    media = "Media, marketing and creative"
    public = "Public and nonprofit"
    trade = "Trade and services"
    other = "Other"


class QualificationRequirement(StrEnum):
    formal = "Formal requirement"
    advantage = "Gave an advantage"
    not_required = "Not required"
    unknown = "Unknown"


class NYSCPathway(StrEnum):
    yes = "Yes"
    no = "No"
    not_completed = "Not completed"


class PredictionRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "graduation_year": 2017,
                "education_level": "Bachelor's degree",
                "course_group": "Technology and computing",
                "first_job_level": "Entry level",
                "first_job_sector": "Technology and telecommunications",
                "qualification_requirement": "Gave an advantage",
                "first_job_via_nysc": "No",
                "course_preparation_score": 3,
                "employability_skill_count": 5,
                "problem_solving_skill": True,
                "communication_skill": True,
            }
        }
    )

    graduation_year: int = Field(ge=2013, le=2017)
    education_level: EducationLevel
    course_group: CourseGroup
    first_job_level: JobLevel
    first_job_sector: SectorGroup
    qualification_requirement: QualificationRequirement
    first_job_via_nysc: NYSCPathway
    course_preparation_score: int = Field(ge=1, le=4)
    employability_skill_count: int = Field(ge=0, le=6)
    problem_solving_skill: bool
    communication_skill: bool

    @model_validator(mode="after")
    def validate_skill_count(self) -> PredictionRequest:
        selected = int(self.problem_solving_skill) + int(self.communication_skill)
        if self.employability_skill_count < selected:
            raise ValueError(
                "employability_skill_count cannot be lower than the selected skill groups"
            )
        return self


class PredictionResponse(BaseModel):
    predicted_first_monthly_income_ngn_2018: float
    income_band: str
    model_name: str
    model_version: str
    benchmark_scope: str = "Nigerian graduates, first employment, 2013-2017 cohorts"
    program_use: str = (
        "Use this benchmark to compare training and internship pathways, not to value a person."
    )


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_name: str | None
    model_version: str | None


class RetrainResponse(BaseModel):
    message: str
    model_name: str
    model_version: str
    total_rows: int
    metrics: dict[str, dict[str, float]]
