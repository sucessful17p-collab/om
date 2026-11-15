# Architecture

NYAYA PULSE is a modular monorepo. `frontend/` contains a Vite + React + TypeScript client. `backend/` contains a FastAPI service, Pydantic schemas, SQLAlchemy models, Alembic migrations and isolated legal-rule logic. Docker Compose uses PostgreSQL; local development defaults to SQLite.

## Implemented path

Synthetic undertrial case input → validated API schema → versioned Section 479 screening function → structured outcome, explanation and review flags → dashboard/application preparation UI. Synthetic cases and application drafts persist in the database. The rules engine does not grant release or make final legal findings.

## Planned boundaries

Basic bearer authentication and role checks on core routes are implemented. User administration, institution-level isolation and audit logging remain planned, alongside custody-document extraction, bail timelines, legal aid, juvenile confidentiality, settlement review, evidence ingestion/provenance, notifications and analytics. Evidence originals and derivatives should use encrypted object storage with append-only provenance records; these capabilities are not yet implemented.

## Data

Alembic migrations create synthetic cases, application drafts, versioned rule metadata, demo accounts and revocable sessions. The API auto-creates schema for local development and Compose applies migrations before startup. Core case/screening routes enforce roles, but institution-level object isolation and durable audit history are not implemented; this database is demo-only and must not receive real case data.
