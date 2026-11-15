from datetime import date
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

class ScreeningInput(BaseModel):
    custody_start: date | None = None
    assessment_date: date = Field(default_factory=date.today)
    maximum_imprisonment_years: float | None = Field(default=None, gt=0, le=100)
    first_time_offender: bool | None = None
    conviction_status: Literal["undertrial", "convicted", "unknown"] = "unknown"
    punishable_with_death: bool | None = None
    life_imprisonment_specified: bool | None = None
    multiple_pending_cases: bool | None = None
    court_order_continued_detention: bool | None = None
    accused_delay_days: int | None = Field(default=None, ge=0, le=36500)
    accused_delay_verified: bool = False
    record_conflict: bool = False
    custody_record_verified: bool = False
    sentence_limit_verified: bool = False

class ScreeningResult(BaseModel):
    status: Literal["potentially_eligible_for_court_consideration", "not_indicated", "legal_review_required"]
    rule_version: str
    elapsed_days: int | None
    excluded_delay_days: int | None
    credited_custody_days: int | None
    threshold_days: int | None
    threshold_fraction: float | None
    reasons: list[str]
    review_flags: list[str]
    disclaimer: str = "Screening is decision support only. It does not determine legal eligibility or grant release; the competent court decides."

class CaseRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    person_name: str
    institution: str
    case_reference: str
    custody_start: date | None
    maximum_imprisonment_years: float | None
    first_time_offender: bool | None
    conviction_status: Literal["undertrial", "convicted", "unknown"]
    multiple_pending_cases: bool | None
    punishable_with_death: bool | None
    life_imprisonment_specified: bool | None
    custody_record_verified: bool
    sentence_limit_verified: bool
    record_conflict: bool
    court_order_continued_detention: bool | None
    demo: bool

class ApplicationDraft(BaseModel):
    id: int | None = None
    case_id: str = Field(min_length=1, max_length=80)
    prepared_by: str = Field(min_length=2, max_length=120)
    notes: str = Field(default="", max_length=4000)
    human_review_acknowledged: bool = False
    status: Literal["draft"] = "draft"

class LegalRuleRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    rule_code: str
    version: str
    effective_date: date
    source: str
    legal_reviewer: str
    verified_on: date | None
    change_history: str
    active: bool

class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=120)
    password: str = Field(min_length=1, max_length=256)

class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int

class UserProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    role: str
    institution_id: str | None
