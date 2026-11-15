"""Create synthetic demo case and application draft tables."""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("case_records",
        sa.Column("id", sa.String(length=80), primary_key=True),
        sa.Column("person_name", sa.String(length=160), nullable=False),
        sa.Column("institution", sa.String(length=200), nullable=False),
        sa.Column("case_reference", sa.String(length=120), nullable=False),
        sa.Column("custody_start", sa.Date(), nullable=True),
        sa.Column("maximum_imprisonment_years", sa.Float(), nullable=True),
        sa.Column("first_time_offender", sa.Boolean(), nullable=True),
        sa.Column("conviction_status", sa.String(length=24), nullable=False),
        sa.Column("multiple_pending_cases", sa.Boolean(), nullable=True),
        sa.Column("demo", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_case_records_case_reference", "case_records", ["case_reference"])
    op.create_table("application_drafts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("case_id", sa.String(length=80), sa.ForeignKey("case_records.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("prepared_by", sa.String(length=120), nullable=False),
        sa.Column("notes", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_application_drafts_case_id", "application_drafts", ["case_id"])

def downgrade():
    op.drop_index("ix_application_drafts_case_id", table_name="application_drafts")
    op.drop_table("application_drafts")
    op.drop_index("ix_case_records_case_reference", table_name="case_records")
    op.drop_table("case_records")
