"""Store legal-rule provenance and review metadata."""
from alembic import op
import sqlalchemy as sa

revision = "0002_legal_rule_versions"
down_revision = "0001_initial"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("legal_rule_versions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("rule_code", sa.String(length=80), nullable=False),
        sa.Column("version", sa.String(length=80), nullable=False),
        sa.Column("effective_date", sa.Date(), nullable=False),
        sa.Column("source", sa.String(length=300), nullable=False),
        sa.Column("legal_reviewer", sa.String(length=160), nullable=False),
        sa.Column("verified_on", sa.Date(), nullable=True),
        sa.Column("change_history", sa.Text(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.UniqueConstraint("rule_code", "version", name="uq_legal_rule_code_version"),
    )
    op.create_index("ix_legal_rule_versions_rule_code", "legal_rule_versions", ["rule_code"])

def downgrade():
    op.drop_index("ix_legal_rule_versions_rule_code", table_name="legal_rule_versions")
    op.drop_table("legal_rule_versions")
