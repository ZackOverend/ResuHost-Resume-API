# ResuHost Roadmap

**Owner:** Zack Overend  
**Created:** 2026-08-29  
**Status:** In implementation — Phase 2 complete pending merge
**Version:** 0.7
**Repositories:**

- API: `/Users/zackaryoverend/Development/ResuHost-Resume-API`
- Frontend: `/Users/zackaryoverend/Development/resuhost-resume-frontend`

## Documentation Map

- [Product and architecture](PRODUCT_AND_ARCHITECTURE.md) — purpose, scope, principles, domain boundaries, system architecture, data model, and frontend information architecture
- [Phase 0: Foundation](phases/00-foundation.md)
- [Phase 1: Master Profile](phases/01-master-profile.md)
- [Phase 2: Tailoring and variants](phases/02-tailoring-and-variants.md) — current phase
- [Phase 3: Job workspace](phases/03-job-workspace.md)
- [Phase 4: Application tracking](phases/04-application-tracking.md)
- [Phase 5: Rendering](phases/05-rendering.md)
- [Phase 6: Discovery and assistance](phases/06-discovery-and-assistance.md)
- [Delivery and quality](reference/DELIVERY_AND_QUALITY.md) — delivery order, testing, and success criteria
- [Governance and decisions](reference/GOVERNANCE_AND_DECISIONS.md) — privacy, edge cases, open questions, decision log, and release definition of done

The roadmap is the status authority. Phase files define scope and acceptance gates; reference files hold cross-cutting guidance.

## Implementation Progress

### 2026-08-29 — Phase 0 API foundation

Completed:

- Added Alembic with an initial schema migration.
- Added safe adoption of complete pre-Alembic databases at the baseline revision.
- Updated Docker startup and CI to apply migrations.
- Added an application factory for isolated configuration and testing.
- Added request IDs and consistent API error envelopes.
- Moved model-provider host and credentials out of the tailoring request.
- Added a server-side model allowlist and bounded job-description input.
- Replaced mutable Pydantic collection defaults.
- Added pytest infrastructure and initial app, schema, migration, and user CRUD coverage.

Verification:

- 15 tests pass locally.
- 1 PostgreSQL CRUD integration test is skipped locally because `TEST_DATABASE_URL` is not configured.
- CI supplies a disposable PostgreSQL service and is configured to run the integration test.
- The initial Alembic revision renders successfully in offline SQL mode.

### 2026-08-29 — Phase 0 frontend foundation

Completed:

- Added a typed, server-only API boundary with validated runtime configuration.
- Added upstream timeouts, safe error parsing, and normalized route-handler failures.
- Added a committed environment-variable template.
- Replaced implicit `users[0]` selection with `PRIMARY_USER_ID`.
- Added route-level loading and retryable error states for the demo.
- Added Vitest and initial API-client and route-handler coverage.

Verification:

- 10 frontend tests pass.
- TypeScript and targeted lint checks pass.
- The Next.js production build succeeds.
- Full-repository lint still reports pre-existing findings in the smooth-scroll provider and the uncommitted self-host page; Phase 0 did not modify those files.

### 2026-08-29 — Phase 1 Master Profile API foundation

Completed:

- Added lifecycle metadata, explicit ordering, verification timestamps, and archive state to Master Profile records.
- Added validated `YYYY-MM` date ranges and explicit current-record handling.
- Added the aggregate `GET /v1/users/{user_id}/profile` endpoint with a deterministic profile-version hash.
- Added partial contact updates through `PATCH /v1/users/{user_id}/profile`.
- Added create, partial update, reorder, archive, restore, and guarded permanent-delete operations for experiences, education, projects, activities, and skill categories.
- Kept legacy endpoints available during the `/v1` migration.

Verification:

- 31 tests pass locally.
- The PostgreSQL integration suite remains configured for CI and is skipped locally without `TEST_DATABASE_URL`.
- The complete Alembic migration chain renders successfully in offline SQL mode.
- The generated FastAPI route table contains all planned Phase 1 Master Profile resource operations.

### 2026-08-29 — Phase 1 Master Profile workspace

Completed:

- Added the `/profile` workspace with contact, experience, project, education, activity, and skill-group management.
- Added create, partial edit, reorder, archive, restore, and guarded permanent-delete flows.
- Added explicit review controls for contact details and every active career record.
- Invalidated review timestamps whenever the corresponding content changes.
- Added actionable readiness checks based on profile content and review state.
- Added a base-resume preview that uses only active records in their explicit order.
- Preserved form drafts after recoverable save failures and added specific saved/error feedback.
- Kept all backend credentials behind allowlisted same-origin route handlers.

Verification:

- 32 backend tests pass locally, with 1 PostgreSQL integration suite skipped without `TEST_DATABASE_URL`.
- 17 frontend tests pass.
- Frontend TypeScript and targeted ESLint checks pass.
- The Next.js production build succeeds and includes the dynamic profile and preview routes.
- Pre-existing user-owned navbar, footer, and self-host changes remain outside the Phase 1 commits.

Next vertical slice:

- Complete the Phase 2 API workflow for creating tailoring runs and immutable resume variants.

### 2026-08-29 — Phase 2 API foundation

Completed:

- Added persistent `TailoringRun` and `ResumeVariant` models and migration.
- Defined a canonical `ResumeDocument` schema with bullet-level source identity.
- Added deterministic verification for missing or stale sources, wrong entry assignment, and newly introduced metrics.
- Added `/v1` endpoints to create and retrieve tailoring runs.
- Added per-suggestion accept, edit, and reject decisions with verification at variant creation time.
- Added immutable draft variant creation, retrieval, approval, and direct PDF export.

Verification:

- 43 backend tests pass locally.
- 1 PostgreSQL integration test is skipped locally because `TEST_DATABASE_URL` is not configured.

### 2026-09-28 — Phase 2 API hardening

Completed:

- Moved suggestion identity to the server: the model references bullets by short labels (`b1`, `b2`, ...), and the API assigns suggestion IDs, source hashes, and original text.
- Discarded proposals with unknown bullet labels or unchanged text instead of failing the whole run.
- Fixed verification of bullets that follow a blank bullet by locating them by source index rather than list position.
- Rejected variant requests that select more than one change for the same source bullet.
- Added deterministic checks for newly introduced named terms (technologies, employers, titles, months) and credential language, using the source bullet and its entry as evidence.
- Made tailoring runs use application-injected settings.
- Added PostgreSQL integration coverage for the tailoring-run, variant, approval, and PDF lifecycle.

Verification:

- 65 backend tests pass locally against a disposable PostgreSQL database.

Known limitations:

- Named-term detection is heuristic: capitalized words that begin a sentence are not checked, and numbers written as words are not treated as metrics.

In progress:

- Migrate the frontend review flow before removing the destructive legacy `apply-tailor` endpoint.

### 2026-09-28 — Phase 2 frontend migration

Completed:

- Replaced the all-at-once tailored display with an explicit review workflow grouped per source bullet.
- Added per-suggestion accept, edit, and reject actions; choosing an alternative for a bullet rejects the previously chosen one.
- Disabled accepting suggestions that fail deterministic verification and showed the verification issues inline.
- Restricted accept-all to verified suggestions, picking at most one change per source bullet.
- Added draft variant creation, preview, approval, and PDF download through allowlisted route handlers.
- Removed the destructive demo tailoring routes, the `apply-tailor` master-mutation flow, and the legacy `/resume/{id}/tailor` and `apply-tailor` API endpoints.

Verification:

- 31 frontend tests pass; TypeScript, the production build, and targeted lint are clean.
- End-to-end API check with a stubbed model provider: run creation, grouped alternatives, failing-suggestion rejection at variant creation, accept/edit/reject variant creation, approval, PDF export, and unchanged master-profile bullets all behave as specified.
- The interactive browser pass of `/tailor` was not completed: the frontend dev server repeatedly exhausted memory on the review machine. UI interactions remain covered by the frontend test suite.

Remaining:

- Decide whether the Phase 2 acceptance gate is met and merge both branches.
