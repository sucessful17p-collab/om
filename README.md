# NYAYA PULSE

NYAYA PULSE is a decision-support prototype for undertrial rights workflows, custody accountability and evidence integrity. It is not a substitute for a lawyer, court, forensic expert or statutory decision-maker. All bundled records are fictional demo data.

## Current implementation

- Section 479 screening with versioned rules, explanations, conservative handling of unknown facts and human-review flags.
- A FastAPI API with health check, persistent demo case list, screening and application-draft endpoints.
- A responsive React dashboard and screening workspace with a clearly labelled synthetic case.
- SQLAlchemy persistence and Alembic migration; SQLite locally and PostgreSQL in Compose.
- Password-hashed demo login, short-lived signed bearer sessions, logout revocation and server-side role checks on core routes.
- API documentation at `/docs` when the backend is running.

Supporting modules in the requested product brief are represented in the repository structure and roadmap; they are not described as implemented until their workflows and persistence exist.

## Run locally

Backend (Python 3.11+):

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:SECRET_KEY = "replace-with-a-random-secret-at-least-32-characters"
$env:DEMO_SUPERINTENDENT_USERNAME = "demo-superintendent"
$env:DEMO_SUPERINTENDENT_PASSWORD = "DemoOnly-ChangeMe"
alembic upgrade head
uvicorn app.main:app --reload
```

Frontend (Node 20+):

```powershell
cd frontend
npm install
npm run dev
```

The frontend expects `http://localhost:8000/api/v1`; set `VITE_API_URL` to override. Demo mode can render the included synthetic sample if the API is not running.

## Docker

Copy `.env.example` to `.env`, change the development demo password and secret, then run `docker compose up --build`. Open `http://localhost:8080`; the seeded demo login is read from `.env`. The API is at `http://localhost:8000/docs`. Do not expose this development configuration to the public internet.

## Rules and safeguards

See [LEGAL_SAFEGUARDS.md](docs/LEGAL_SAFEGUARDS.md), [SECURITY.md](docs/SECURITY.md), [ARCHITECTURE.md](docs/ARCHITECTURE.md), [DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md), and [AI_LIMITATIONS.md](docs/AI_LIMITATIONS.md). Rules include source metadata and a version. Their legal interpretation must be validated by qualified counsel before operational use. No decision made by the system grants release.

## Developer commands

```powershell
cd backend
alembic upgrade head
python -m pytest
```

Tests cover the rules, password/session handling, role checks and persisted draft handler. User administration, MFA, rate limiting, institution-level isolation, evidence processing and the remaining module workflows are not production capabilities.
