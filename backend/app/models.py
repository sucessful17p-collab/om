from datetime import date, datetime, timezone
from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class CaseRecordModel(Base):
    __tablename__ = "case_records"
    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    person_name: Mapped[str] = mapped_column(String(160), nullable=False)
    institution: Mapped[str] = mapped_column(String(200), nullable=False)
    case_reference: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    custody_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    maximum_imprisonment_years: Mapped[float | None] = mapped_column(Float, nullable=True)
    first_time_offender: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    conviction_status: Mapped[str] = mapped_column(String(24), nullable=False)
    multiple_pending_cases: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    punishable_with_death: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    life_imprisonment_specified: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    custody_record_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    sentence_limit_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    record_conflict: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    court_order_continued_detention: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    demo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)

class ApplicationDraftRecord(Base):
    __tablename__ = "application_drafts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_id: Mapped[str] = mapped_column(ForeignKey("case_records.id", ondelete="RESTRICT"), nullable=False, index=True)
    prepared_by: Mapped[str] = mapped_column(String(120), nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)

class LegalRuleVersion(Base):
    __tablename__ = "legal_rule_versions"
    __table_args__ = (UniqueConstraint("rule_code", "version", name="uq_legal_rule_code_version"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rule_code: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(80), nullable=False)
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    source: Mapped[str] = mapped_column(String(300), nullable=False)
    legal_reviewer: Mapped[str] = mapped_column(String(160), nullable=False)
    verified_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    change_history: Mapped[str] = mapped_column(Text, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

class UserAccount(Base):
    __tablename__ = "user_accounts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(300), nullable=False)
    role: Mapped[str] = mapped_column(String(48), nullable=False, index=True)
    institution_id: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)

class AuthSession(Base):
    __tablename__ = "auth_sessions"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
