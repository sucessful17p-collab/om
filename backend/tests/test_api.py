from fastapi import HTTPException
from sqlalchemy import select
from app.main import create_application, list_cases
from app.models import ApplicationDraftRecord, LegalRuleVersion, UserAccount
from app.schemas.section_479 import ApplicationDraft, CaseRecord, LegalRuleRecord

def test_demo_directory_and_application_handler_persist_draft(db):
    cases = list_cases(db)
    assert len(cases) >= 2
    assert CaseRecord.model_validate(cases[0]).demo is True
    rule = db.scalar(select(LegalRuleVersion))
    assert LegalRuleRecord.model_validate(rule).verified_on is None
    user = db.query(UserAccount).filter_by(username="test-superintendent").one()
    payload = ApplicationDraft(case_id=cases[0].id, prepared_by="Untrusted request field", notes="Integration test only", human_review_acknowledged=True)
    response = create_application(payload, db, user)
    assert response.id is not None
    stored = db.scalar(select(ApplicationDraftRecord).where(ApplicationDraftRecord.id == response.id))
    assert stored.case_id == cases[0].id
    assert stored.prepared_by == user.username

def test_application_handler_requires_review_acknowledgement(db):
    user = db.query(UserAccount).filter_by(username="test-superintendent").one()
    payload = ApplicationDraft(case_id="DEMO-UT-1042", prepared_by="Test reviewer", human_review_acknowledged=False)
    try:
        create_application(payload, db, user)
    except HTTPException as exc:
        assert exc.status_code == 422
    else:
        raise AssertionError("missing human acknowledgement was accepted")

def test_application_handler_rejects_unknown_case(db):
    user = db.query(UserAccount).filter_by(username="test-superintendent").one()
    payload = ApplicationDraft(case_id="MISSING", prepared_by="Test reviewer", human_review_acknowledged=True)
    try:
        create_application(payload, db, user)
    except HTTPException as exc:
        assert exc.status_code == 404
    else:
        raise AssertionError("unknown case was accepted")
