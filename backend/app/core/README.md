# Core services

Bearer authentication, password hashing, revocable sessions and core route role checks are in `app/core/auth.py`. Configuration is in `app/database.py`. Account administration, MFA, institution-level authorization, rate limiting, structured audit logging and production security middleware remain unimplemented.
