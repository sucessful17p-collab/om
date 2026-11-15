# Database schema

The Alembic migrations currently create:

- `case_records`: synthetic person/case linkage and screening inputs.
- `application_drafts`: draft preparation records referencing a case.
- `legal_rule_versions`: version, effective date, source, reviewer, verification date and change history for rules.
- `user_accounts`: demo user, PBKDF2 password hash, role and optional institution identifier.
- `auth_sessions`: expiring, revocable bearer-token sessions.

Foreign keys and lookup indexes are in place for these initial tables. User/role administration, institution tenancy, custody history, document, bail/release, legal-aid, evidence, provenance and audit tables are not implemented yet. Demo records and the configured demo Superintendent are seeded at API startup when credentials are provided through environment variables.
