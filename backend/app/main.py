from contextlib import asynccontextmanager
from datetime import date
import os
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import ACCESS_TTL, bearer, get_current_user, hash_password, issue_token, require_roles, revoke_session, verify_password
from app.legal_rules.section_479 import RULE_SOURCE, RULE_SOURCE_URL, RULE_VERSION, screen_section_479
from app.schemas.section_479 import ApplicationDraft, CaseRecord, LegalRuleRecord, LoginRequest, ScreeningInput, ScreeningResult, TokenResponse, UserProfile
from app.database import Base, SessionLocal, engine, get_db
from app.models import ApplicationDraftRecord, AuthSession, CaseRecordModel, LegalRuleVersion, UserAccount

def seed_demo_records(db: Session):
    first = db.get(CaseRecordModel, "DEMO-UT-1042")
    if first is None:
        db.add(CaseRecordModel(id="DEMO-UT-1042", person_name="Aarav Kumar", institution="Demo Central Correctional Facility", case_reference="DEMO/2024/118", custody_start=date(2024, 2, 1), maximum_imprisonment_years=6, first_time_offender=True, conviction_status="undertrial", multiple_pending_cases=False, punishable_with_death=False, life_imprisonment_specified=False, custody_record_verified=True, sentence_limit_verified=True, record_conflict=False, court_order_continued_detention=False, demo=True))
    elif first.demo:
        first.punishable_with_death = False
        first.life_imprisonment_specified = False
        first.custody_record_verified = True
        first.sentence_limit_verified = True
        first.record_conflict = False
        first.court_order_continued_detention = False
    second = db.get(CaseRecordModel, "DEMO-UT-1078")
    if second is None:
        db.add(CaseRecordModel(id="DEMO-UT-1078", person_name="Meera Das", institution="Demo District Correctional Facility", case_reference="DEMO/2023/064", custody_start=date(2023, 5, 12), maximum_imprisonment_years=None, first_time_offender=None, conviction_status="undertrial", multiple_pending_cases=None, punishable_with_death=None, life_imprisonment_specified=None, custody_record_verified=False, sentence_limit_verified=False, record_conflict=True, court_order_continued_detention=None, demo=True))
    elif second.demo:
        second.punishable_with_death = None
        second.life_imprisonment_specified = None
        second.custody_record_verified = False
        second.sentence_limit_verified = False
        second.record_conflict = True
        second.court_order_continued_detention = None
    rule = db.scalar(select(LegalRuleVersion).where(LegalRuleVersion.rule_code == "BNSS-479", LegalRuleVersion.version == RULE_VERSION))
    if rule is None:
        db.add(LegalRuleVersion(rule_code="BNSS-479", version=RULE_VERSION, effective_date=date(2024, 7, 1), source=f"{RULE_SOURCE}; {RULE_SOURCE_URL}", legal_reviewer="Pending qualified legal review", verified_on=None, change_history="Initial configured screening rule; legal verification pending.", active=True))
    elif "India Code" not in rule.source:
        rule.source = f"{RULE_SOURCE}; {RULE_SOURCE_URL}"
        rule.change_history += " Source metadata updated to point to official India Code text."
    demo_username = os.getenv("DEMO_SUPERINTENDENT_USERNAME", "")
    demo_password = os.getenv("DEMO_SUPERINTENDENT_PASSWORD", "")
    if demo_username and demo_password and db.scalar(select(UserAccount.id).where(UserAccount.username == demo_username)) is None:
        db.add(UserAccount(username=demo_username, password_hash=hash_password(demo_password), role="prison_superintendent", institution_id="DEMO-FACILITY", active=True))
    db.commit()

@asynccontextmanager
async def lifespan(_: FastAPI):
    if os.getenv("AUTO_CREATE_SCHEMA", "true").lower() == "true":
        Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_demo_records(db)
    yield

app = FastAPI(title="NYAYA PULSE API", version="0.1.0", description="Decision-support prototype. Not legal advice or a release decision.", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://localhost:8080"], allow_methods=["*"], allow_headers=["*"])

@app.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(select(1))
    return {"status": "ok", "rule_version": RULE_VERSION, "mode": "synthetic-demo", "database": "connected"}

@app.post("/api/v1/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(UserAccount).where(UserAccount.username == payload.username))
    if user is None or not user.active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password", headers={"WWW-Authenticate": "Bearer"})
    return TokenResponse(access_token=issue_token(user, db), expires_in=int(ACCESS_TTL.total_seconds()))

@app.get("/api/v1/auth/me", response_model=UserProfile)
def current_profile(user: UserAccount = Depends(get_current_user)):
    return user

@app.post("/api/v1/auth/logout")
def logout(credentials=Depends(bearer), user: UserAccount = Depends(get_current_user), db: Session = Depends(get_db)):
    revoke_session(user, credentials.credentials, db)
    return {"status": "signed_out"}

@app.get("/api/v1/legal-rules/section-479", response_model=list[LegalRuleRecord])
def get_section_479_rule_history(db: Session = Depends(get_db), _: UserAccount = Depends(require_roles("system_administrator", "prison_superintendent", "authorised_prison_officer", "legal_aid_advocate", "dlsa_slsa_reviewer"))):
    return list(db.scalars(select(LegalRuleVersion).where(LegalRuleVersion.rule_code == "BNSS-479").order_by(LegalRuleVersion.version)))

@app.get("/api/v1/cases", response_model=list[CaseRecord])
def list_cases(db: Session = Depends(get_db), _: UserAccount = Depends(require_roles("system_administrator", "prison_superintendent", "authorised_prison_officer", "legal_aid_advocate", "dlsa_slsa_reviewer", "court_liaison_officer"))):
    return list(db.scalars(select(CaseRecordModel).order_by(CaseRecordModel.id)))

@app.get("/api/v1/cases/{case_id}", response_model=CaseRecord)
def get_case(case_id: str, db: Session = Depends(get_db), _: UserAccount = Depends(require_roles("system_administrator", "prison_superintendent", "authorised_prison_officer", "legal_aid_advocate", "dlsa_slsa_reviewer", "court_liaison_officer"))):
    case = db.get(CaseRecordModel, case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@app.post("/api/v1/screenings/section-479", response_model=ScreeningResult)
def screen(payload: ScreeningInput, _: UserAccount = Depends(require_roles("system_administrator", "prison_superintendent", "authorised_prison_officer", "legal_aid_advocate", "dlsa_slsa_reviewer"))):
    return screen_section_479(payload)

@app.post("/api/v1/applications", response_model=ApplicationDraft, status_code=201)
def create_application(payload: ApplicationDraft, db: Session = Depends(get_db), user: UserAccount = Depends(require_roles("prison_superintendent"))):
    if not payload.human_review_acknowledged:
        raise HTTPException(status_code=422, detail="Authorised human review must be acknowledged")
    if db.get(CaseRecordModel, payload.case_id) is None:
        raise HTTPException(status_code=404, detail="Case not found")
    draft = ApplicationDraftRecord(case_id=payload.case_id, prepared_by=user.username, notes=payload.notes, status="draft")
    db.add(draft)
    db.commit()
    return payload.model_copy(update={"id": draft.id, "prepared_by": user.username})
