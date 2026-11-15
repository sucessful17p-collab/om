# API

Versioned API base: `/api/v1`. FastAPI OpenAPI UI: `/docs`.

- `POST /api/v1/auth/login` exchange a configured demo username/password for a 30-minute bearer token.
- `GET /api/v1/auth/me` return the authenticated account profile.
- `POST /api/v1/auth/logout` revoke the current server-side session.

- `GET /health` service health.
- `GET /api/v1/cases` synthetic demo case directory.
- `GET /api/v1/cases/{case_id}` retrieve a synthetic case.
- `GET /api/v1/legal-rules/section-479` retrieve the configured rule source, version and legal-review metadata.
- `POST /api/v1/screenings/section-479` run explainable screening for supplied facts.
- `POST /api/v1/applications` create a persisted preparation draft after requiring human-review acknowledgement.

Case, rule-history, screening and application endpoints require bearer authentication and enforce role checks. These controls have not been independently security reviewed and do not provide institution-level record isolation. Do not connect real records. Request and response models are in `backend/app/schemas/`.
