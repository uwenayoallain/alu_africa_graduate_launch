from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from API.config import CAREER_SECTORS, EDUCATION_CAREERS, EMPLOYER_CONTRACTS


class EducationLevel(StrEnum):
    none = "No formal education"
    pre_primary = "Pre-primary"
    primary = "Primary education"
    lower_secondary = "Lower secondary education"
    upper_secondary = "Upper secondary education"
    tertiary = "Tertiary education"


class CareerField(StrEnum):
    ict = "ICT"
    science = "Science and engineering"
    social = "Education, health and social services"
    business = "Business, management and office work"
    sales = "Sales and services"
    trades = "Skilled trades and operators"
    agriculture = "Agriculture"
    other = "Elementary and other work"


class MainSector(StrEnum):
    agriculture = "Agriculture"
    industry = "Industry"
    services = "Services"


class EmployerType(StrEnum):
    private = "Private business or VUP"
    public = "Public institution"
    public_private = "Public-private enterprise"
    household = "Household"
    cooperative = "Cooperative"
    ngo = "NGO or international organisation"
    other = "Other"


class ContractType(StrEnum):
    oral = "Oral agreement"
    written = "Written contract"


class Residence(StrEnum):
    rural = "Rural"
    urban = "Urban"


class Province(StrEnum):
    kigali = "Kigali city"
    eastern = "Eastern Province"
    northern = "Northern Province"
    southern = "Southern Province"
    western = "Western Province"


class PredictionRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "age": 23,
                "education_level": "Primary education",
                "career_field": "Agriculture",
                "main_sector": "Agriculture",
                "employer_type": "Private business or VUP",
                "contract_type": "Oral agreement",
                "weekly_hours": 36,
                "residence": "Rural",
                "province": "Eastern Province",
            }
        }
    )

    age: int = Field(ge=16, le=30)
    education_level: EducationLevel
    career_field: CareerField
    main_sector: MainSector
    employer_type: EmployerType
    contract_type: ContractType
    weekly_hours: float = Field(ge=1, le=118)
    residence: Residence
    province: Province

    @model_validator(mode="after")
    def check_supported_pathway(self):
        education = self.education_level.value
        career = self.career_field.value
        sector = self.main_sector.value
        employer = self.employer_type.value
        contract = self.contract_type.value

        if career not in EDUCATION_CAREERS[education]:
            raise ValueError(
                f"{career} has too little survey coverage for {education}."
            )
        if sector not in CAREER_SECTORS[career]:
            raise ValueError(
                f"{sector} has too little survey coverage for {career}."
            )
        if contract not in EMPLOYER_CONTRACTS[employer]:
            raise ValueError(
                f"{contract} has too little survey coverage for {employer}."
            )
        return self


class PredictionResponse(BaseModel):
    predicted_monthly_income_rwf: float
    income_band: str
    model_name: str
    model_version: str
    benchmark_scope: str = "Employees aged 16-30 in the Rwanda Labour Force Survey 2024"
    program_use: str = (
        "Use this estimate to compare career pathways, not as a guaranteed salary."
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
