import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from app.core.auth import get_current_user, hash_password, issue_token, require_roles, revoke_session, verify_password
from app.main import login
from app.models import UserAccount
from app.schemas.section_479 import LoginRequest

def test_password_hash_uses_salted_verification():
    stored = hash_password("a-long-demo-password")
    assert stored != "a-long-demo-password"
    assert verify_password("a-long-demo-password", stored)
    assert not verify_password("incorrect", stored)

def test_token_is_session_backed_and_revocable(db, monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "a-test-secret-with-at-least-32-characters")
    user = db.query(UserAccount).filter_by(username="test-superintendent").one()
    token = issue_token(user, db)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    assert get_current_user(credentials, db).id == user.id
    revoke_session(user, token, db)
    with pytest.raises(HTTPException) as exc:
        get_current_user(credentials, db)
    assert exc.value.status_code == 401

def test_role_policy_denies_non_superintendent_draft_access(db):
    reviewer = db.query(UserAccount).filter_by(username="test-superintendent").one()
    assert require_roles("prison_superintendent")(reviewer) is reviewer
    reviewer.role = "family_external_enquirer"
    with pytest.raises(HTTPException) as exc:
        require_roles("prison_superintendent")(reviewer)
    assert exc.value.status_code == 403

def test_login_rejects_bad_password_and_issues_a_token(db, monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "a-test-secret-with-at-least-32-characters")
    user = db.query(UserAccount).filter_by(username="test-superintendent").one()
    with pytest.raises(HTTPException) as exc:
        login(LoginRequest(username=user.username, password="incorrect"), db)
    assert exc.value.status_code == 401
    response = login(LoginRequest(username=user.username, password="Test-Password-Only"), db)
    assert response.expires_in == 1800
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=response.access_token)
    assert get_current_user(credentials, db).username == user.username
