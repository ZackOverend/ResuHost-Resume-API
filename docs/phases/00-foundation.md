# Phase 0: Stabilize the Foundation

### Objective

Make both repositories safe to evolve without changing the existing product behavior.

### API Deliverables

- Add Alembic and create a baseline migration.
- Add pytest and an isolated PostgreSQL test configuration.
- Add API integration fixtures and factories.
- Split create, patch, and response Pydantic schemas.
- Replace list defaults with `Field(default_factory=list)`.
- Add consistent error response structures.
- Prevent raw internal exception details from reaching clients.
- Configure model provider host and credentials server-side.
- Validate model names and job-description input length.
- Introduce `/v1` for new endpoints while retaining legacy routes during migration.
- Document API environment variables and supported deployment modes.

### Frontend Deliverables

- Create a typed, server-only API client with normalized errors and timeouts.
- Configure a server-only `PRIMARY_USER_ID` for personal mode.
- Stop selecting `users[0]`.
- Add route-level loading and error states.
- Add Vitest and Testing Library.
- Add Playwright when the first complete vertical workflow exists.
- Document frontend environment variables.
- Reconcile self-hosting documentation with implemented API paths after current local edits are finalized.

### Acceptance Gate

- A clean database is created through migrations.
- Existing profile CRUD and PDF generation have integration coverage.
- Frontend build and lint pass.
- The browser cannot access the backend API credential.
- The demo loads the explicitly configured personal user.
- Existing resume generation behavior remains available.
