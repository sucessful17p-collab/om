"""Add explicit statutory and verification facts to demo case records."""
from alembic import op
import sqlalchemy as sa

revision = "0003_section_479_review_facts"
down_revision = "0002_legal_rule_versions"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("case_records", sa.Column("punishable_with_death", sa.Boolean(), nullable=True))
    op.add_column("case_records", sa.Column("life_imprisonment_specified", sa.Boolean(), nullable=True))
    op.add_column("case_records", sa.Column("custody_record_verified", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("case_records", sa.Column("sentence_limit_verified", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("case_records", sa.Column("record_conflict", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("case_records", sa.Column("court_order_continued_detention", sa.Boolean(), nullable=True))

def downgrade():
    op.drop_column("case_records", "court_order_continued_detention")
    op.drop_column("case_records", "record_conflict")
    op.drop_column("case_records", "sentence_limit_verified")
    op.drop_column("case_records", "custody_record_verified")
    op.drop_column("case_records", "life_imprisonment_specified")
    op.drop_column("case_records", "punishable_with_death")
