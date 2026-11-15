import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.database import Base
from app.main import seed_demo_records
from app.models import UserAccount
from app.core.auth import hash_password

@pytest.fixture
def db(tmp_path):
    test_engine = create_engine(f"sqlite:///{tmp_path / 'api-test.db'}")
    Base.metadata.create_all(bind=test_engine)
    with Session(test_engine) as session:
        seed_demo_records(session)
        session.add(UserAccount(username="test-superintendent", password_hash=hash_password("Test-Password-Only"), role="prison_superintendent", institution_id="DEMO-FACILITY", active=True))
        session.commit()
        yield session
    test_engine.dispose()
