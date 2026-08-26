# MedicoSync — Secure Healthcare Records Backend

**Problem:** Doctors lose consultation time and risk losing patient history because records live scattered across phone photos, notebooks, and memory.

**Solution:** A backend that stores patient records securely, ties every record to the doctor who owns it, and is built to let doctors share a patient's care with another doctor without losing that ownership model.

This repo is a from-scratch rebuild of an earlier version of MedicoSync, this time built feature-by-feature with compliance and testing built in from the start, not bolted on after.

---

## What's actually built and deployed

Everything below is live on Render, backed by a Supabase Postgres database and Supabase Storage, and has been manually tested end-to-end against the deployed API, not just locally.

- **Auth** — registration and login with Argon2 password hashing and JWT issuance. Account lockout after repeated failed logins is tracked in Redis, so it works correctly across multiple app workers, not just one.
- **Patient records** — doctors can create, list, fetch, update, and delete patients. Patients are linked to doctors through a join table (`DoctorPatientLink`), not a plain foreign key, because a patient can eventually be shared across multiple doctors.
- **Record uploads** — doctors can upload files (PDF, JPEG, PNG) tied to a patient. Files go to Supabase Storage (S3-compatible API), and a time-limited signed URL is generated for retrieval.
- **OTP-verified share links** — a doctor can generate a short-lived link (token + OTP) that lets another doctor view one specific record without a full account. The link expires, the OTP can be resent (rate-limited, with a 30-second cooldown), and the originating doctor can revoke it instantly. Verification returns the record and confirms which doctor it came from. The frontend currently has the doctor-facing "generate" UI only — there's no dedicated recipient page yet for entering the token/OTP, though the API itself works end-to-end.

## Not built yet

- **Audit trail and configurable data retention policy** — planned, not implemented.

## Architecture

Requests flow through five layers, each with one job:

```
Router      -> parses the HTTP request, validates shape with Pydantic
Controller  -> coordinates the request, calls the right service
Service     -> business rules (e.g. does this doctor own this patient?)
Repository  -> builds queries, talks to the database
Database    -> PostgreSQL
```

**Transaction boundary:** the request-scoped database session (`get_db()`, a FastAPI dependency) owns the transaction. It commits once if the whole request succeeds, and rolls back once if anything raises — anywhere in Controller, Service, or Repository. Individual layers only `flush()`, which pushes SQL to Postgres so IDs and timestamps come back, but nothing is durable until `get_db()` commits at the end. This means every request is atomic by default without any single layer having to remember to commit.

## What I actually learned building this

**Where the real bottleneck is.** Load testing (Locust) the login endpoint showed throughput staying flat from 1 worker to 4 workers — roughly 6 RPS either way. Live CPU monitoring during the test showed the process pinned at 100%. The cause is Argon2's password hashing, which is deliberately CPU-heavy for security. Adding more app workers doesn't help when the bottleneck is CPU, not I/O — the fix is a separate scaling strategy for auth traffic, not just spinning up more workers.

**A schema/code mismatch that only showed up under real testing.** The `Patient` model was designed for doctor-to-doctor sharing (a join table), but the CRUD code was still written as if a patient belonged to exactly one doctor via a direct column. It only surfaced once I tested patient creation end-to-end and got a clear database error — a good example of why testing against a real database catches things a code review alone won't.

**Storage config vs. storage code.** Records were originally uploaded through MinIO for local development. After deploying, uploads failed in production because the deployed app was still pointed at a local MinIO address that only exists on a dev machine. Since the upload code was written against the generic S3 API from the start, moving to real Supabase Storage in production was a config change — new credentials and endpoint — not a rewrite.

## Currently working on

With Auth, Patient CRUD, Record uploads, and OTP sharing all live and tested, I'm now going deeper on API design patterns and database performance/optimization — the next layer once the core product actually works, not a substitute for finishing it.

## Tech stack

FastAPI, async SQLAlchemy 2.0, PostgreSQL (via Supabase), Redis, Argon2, JWT, Supabase Storage (S3-compatible), deployed on Render.

## Testing

Unit and integration tests run against real Postgres and Redis instances, not mocks, so failure modes (constraint violations, lockout timing, connection errors) reflect what actually happens in production rather than what a mock assumes will happen.

## Live demo

- App: `https://medicosync-frontend.netlify.app`
- API: `https://medicosync-backend.onrender.com`
- Interactive API docs: `https://medicosync-backend.onrender.com/docs`

## Running it locally

```bash
git clone https://github.com/FanoyG/medicosync.git
cd medicosync/backend
python -m venv .venv
.venv\Scripts\activate        # Windows; use `source .venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
```

You'll need a `.env` file with:

```dotenv
DATABASE_URL=          # Postgres connection string, used by Alembic
DB_CONNECTION=         # Postgres connection string, used by the app (postgresql+psycopg://...)
SECRET_KEY=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_BUCKET_NAME=
AWS_REGION=
AWS_ENDPOINT_URL=      # Supabase Storage S3 endpoint, or a local MinIO endpoint for dev
```

Then apply migrations and start the server:

```bash
alembic upgrade head
uvicorn main:app --reload
```

Visit `http://127.0.0.1:8000/docs` to try the API directly.

## Contributing

This is a solo learning/portfolio project, but issues and pull requests are welcome:

1. Fork the repo and create a branch off `main`.
2. Keep changes scoped to one feature or fix per PR.
3. Note in the PR description what you tested and how (unit test, manual Swagger check, etc.) — this project treats "tested against a real database," not mocks, as the bar.

## License

MIT — see `LICENSE`.