# ResuHost Phased Implementation Plan

**Owner:** Zack Overend  
**Created:** 2026-08-29  
**Status:** In implementation — Phase 0 API foundation complete  
**Version:** 0.2  
**Repositories:**

- API: `/Users/zackaryoverend/Development/ResuHost-Resume-API`
- Frontend: `/Users/zackaryoverend/Development/resuhost-resume-frontend`

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

Next vertical slice:

- Complete the Phase 0 frontend API-client foundation, then begin the Master Profile aggregate API and workspace.

## Purpose

ResuHost should help a job seeker maintain an accurate career record, evaluate a job, prepare a truthful job-specific resume, export a reliable application document, and track the application through its outcome.

The immediate objective is a personal tool that supports an active search for a January 2027 role. A broader hosted product remains possible, but it must not delay a useful personal workflow.

The primary product hypothesis is:

> If ResuHost can turn a selected job into a verified, tailored application package in under 15 minutes, it will materially improve application quality without consuming time needed for networking and interviews.

## Current State

### API

The API currently provides:

- FastAPI and Pydantic request/response handling
- SQLAlchemy with PostgreSQL
- User, experience, education, project, activity, and skill-category CRUD
- JSON resume snapshots
- Ollama/OpenAI-compatible bullet tailoring
- Jinja HTML templates rendered to PDF through WeasyPrint
- Docker-based local deployment
- API-key middleware
- Basic CI import and table-creation checks

### Frontend

The frontend currently provides:

- A Next.js marketing site
- A resume demo that loads the first API user
- Job-description input and model selection
- In-memory tailored bullets
- In-memory snapshots
- PDF download through Next.js route handlers
- A public self-hosting section under active development

### Current Risks

The current tailored-PDF route temporarily writes AI output into the master profile, creates a snapshot, renders it, and attempts to restore the original content. A failed restoration could corrupt the source resume.

Other important gaps are:

- No migration framework
- No meaningful automated API or frontend tests
- No first-class frontend for creating and managing the master profile
- No explicit ordering for resume entries
- Unvalidated string dates
- No job or application records
- No durable resume-variant lifecycle
- No deterministic checks for fabricated metrics or claims
- A generic user listing is used to select the displayed profile
- Current authentication is suitable only for a tightly controlled personal deployment

## Scope and Principles

### In Scope for the Personal Release

- Master Profile management
- Manual job capture
- Transparent fit and gap analysis
- Evidence-backed tailoring suggestions
- Accept, edit, and reject review
- Immutable resume variants
- Reliable HTML/PDF rendering
- Application status and follow-up tracking

### Explicitly Deferred

- Mass application submission
- Autonomous answers to sensitive screening questions
- LinkedIn automation
- Generic browser agents
- Broad job-board scraping
- Native mobile applications
- Billing and subscriptions
- Multi-tenant SaaS administration
- A general-purpose AI LaTeX IDE

### Guiding Principles

1. **The master profile is the source of truth.** AI output never silently replaces it.
2. **AI proposes; the user decides.** Consequential changes require review.
3. **Evidence before embellishment.** Claims must trace to existing career information.
4. **Variants are historical records.** Updating the master profile does not mutate an application resume.
5. **Explain uncertainty.** Matching and verification expose gaps rather than hiding them in a score.
6. **Quality over volume.** The product optimizes application preparation, not indiscriminate submission.
7. **One vertical slice at a time.** Each phase ships a usable API and frontend capability together.

## Domain Boundaries

| Object | Purpose | Mutation policy |
|---|---|---|
| Master Profile | Complete, verified career history | Edited explicitly by the user |
| Job | Original opportunity and extracted requirements | Raw description preserved |
| Job Analysis | Requirement-to-evidence assessment | Recomputed and versioned |
| Tailoring Run | Model suggestions and verification results | Immutable after completion |
| Resume Variant | Approved presentation for a specific purpose | Versioned; never silently updated |
| Application | Record of the package used and subsequent outcome | Status changes recorded as events |
| Template | Visual document formatting | Never owns career facts |

## Target Architecture

```text
Next.js frontend
|
|-- Master Profile
|-- Job workspace
|-- Tailoring review
|-- Resume preview
`-- Application tracker
        |
        v
Next.js server route handlers
        |
        | server-only API credential
        v
FastAPI /v1
|
|-- Profile service
|-- Job service
|-- Analysis service
|-- Tailoring service
|-- Verification service
|-- Rendering service
`-- Application service
        |
        v
PostgreSQL
|
|-- Existing master-profile records
|-- Jobs and analyses
|-- Tailoring runs
|-- Resume variants
`-- Applications and events
```

The browser must not receive the FastAPI service credential. The Next.js server remains the browser-facing backend-for-frontend.

## Proposed Data Model

The exact schema will be finalized during the relevant phase. These fields define the required capabilities.

### Existing Master Profile

Retain the existing user, experience, education, project, activity, and skill-category models initially. Add:

- Explicit `sort_order`
- `created_at` and `updated_at`
- `archived_at` where records should be recoverable
- Validated month-precision dates
- A deterministic profile-version hash

### Job

```text
id
user_id
company
title
location
source_url
source_name
description
description_hash
status
posted_at
closing_at
created_at
updated_at
```

### JobAnalysis

```text
id
job_id
profile_version_hash
requirements
matching_evidence
gaps
recommendation
model
prompt_version
created_at
```

### TailoringRun

```text
id
user_id
job_id
base_profile_hash
status
model
prompt_version
suggestions
verification
error_code
created_at
completed_at
```

### ResumeVariant

```text
id
user_id
job_id
tailoring_run_id
label
status
data
verification
source_profile_hash
created_at
approved_at
archived_at
```

### Application

```text
id
user_id
job_id
resume_variant_id
status
submission_url
applied_at
follow_up_at
notes
created_at
updated_at
```

Application status changes should also be stored as timeline events so history is not lost.

## Frontend Information Architecture

```text
Public
|-- /
|-- /demo
`-- /self-host

Workspace
|-- /app
|   |-- Today
|   |-- Jobs
|   |-- Applications
|   `-- Follow-ups
|-- /app/profile
|   |-- Overview
|   |-- Contact
|   |-- Experience
|   |-- Projects
|   |-- Education
|   |-- Activities
|   `-- Skills
|-- /app/jobs/[jobId]
|   |-- Posting
|   |-- Fit
|   |-- Tailor
|   `-- Application
`-- /app/resumes/[variantId]
    |-- Content
    |-- Changes
    |-- Verification
    `-- Preview
```

The existing `/demo` remains a safe showcase or sandbox. It does not become the authenticated application workspace.

## Phase 0: Stabilize the Foundation

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

## Phase 1: Master Profile Workspace

### Objective

Let the user create and manage complete career information without seed scripts or direct database access.

### API Deliverables

- Add a dedicated aggregate profile endpoint.
- Add partial updates through `PATCH`.
- Add explicit ordering for all profile sections.
- Add validated month-precision dates and current-role handling.
- Add archive and restore behavior for career records.
- Add created, updated, archived, and verification timestamps as appropriate.
- Return a deterministic `profile_version` hash with the aggregate profile.
- Preserve permanent deletion behind an explicit operation.

Proposed endpoints:

```http
GET   /v1/users/{user_id}/profile
PATCH /v1/users/{user_id}/profile

POST  /v1/users/{user_id}/experiences
PATCH /v1/users/{user_id}/experiences/{experience_id}
POST  /v1/users/{user_id}/experiences/{experience_id}/archive
POST  /v1/users/{user_id}/experiences/{experience_id}/restore
```

Equivalent endpoints apply to projects, education, activities, and skill categories.

### Frontend Deliverables

- Add `/app/profile` overview.
- Add contact-information editing.
- Add create, edit, reorder, archive, restore, and delete flows for:
  - Experiences
  - Projects
  - Education
  - Activities
  - Skill categories
- Add a base-resume preview.
- Add clear loading, empty, validation, saved, unsaved, and error states.
- Preserve in-progress form input after recoverable failures.
- Warn when profile edits make an existing variant stale without modifying that variant.

### Profile Overview Copy Direction

**Headline:** `Your career profile`

**Description:** `Keep your complete work history here. ResuHost uses verified information from this profile to create job-specific resumes.`

Use an actionable readiness checklist rather than an arbitrary completion percentage:

- Contact details added
- At least one experience or project
- Dates reviewed
- Accomplishments include outcomes where available
- Skills have supporting experience where appropriate
- No unreviewed AI suggestions

### Primary User Flows

First-time setup:

```text
Open Profile
-> Add contact details
-> Add experience
-> Add accomplishments
-> Add projects and skills
-> Review master profile
-> Preview base resume
```

Returning edit:

```text
Profile overview
-> Select section
-> Edit entry
-> Validate inline
-> Save
-> Identify stale variants without changing them
```

### Acceptance Gate

- No profile-management flow depends on `users[0]`.
- Every master-profile entity can be created, edited, ordered, archived, and restored.
- Invalid date ranges are caught inline and by the API.
- A base PDF can be generated without changing profile data.
- Every profile mutation changes the profile-version hash.
- Existing resume variants remain unchanged after profile edits.
- Profile API integration and frontend component tests pass.

## Phase 2: Non-Destructive Tailoring and Resume Variants

### Objective

Replace destructive bullet rewriting with evidence-backed suggestions and immutable resume variants.

### API Deliverables

- Add `TailoringRun` and `ResumeVariant` models.
- Define a canonical `ResumeDocument` schema used by every renderer.
- Return bullet-level suggestions instead of replacement arrays.
- Identify source content using section, entry UUID, bullet index, and source-text hash.
- Add deterministic verification for:
  - Missing source entries
  - Stale source hashes
  - New or altered metrics
  - Employer, title, and date changes
  - Bullets assigned to the wrong entry
  - Newly introduced named technologies or credentials
- Create variants from individually approved or edited suggestions.
- Render PDFs directly from variant data.
- Deprecate and remove the destructive `apply-tailor` workflow after frontend migration.

Proposed endpoints:

```http
POST /v1/users/{user_id}/tailoring-runs
GET  /v1/tailoring-runs/{run_id}
POST /v1/tailoring-runs/{run_id}/variants
GET  /v1/resume-variants/{variant_id}
POST /v1/resume-variants/{variant_id}/approve
GET  /v1/resume-variants/{variant_id}/pdf
```

### Suggestion Contract

```json
{
  "id": "suggestion-uuid",
  "section": "experience",
  "entry_id": "experience-uuid",
  "source_index": 1,
  "source_hash": "sha256:...",
  "original_text": "Reduced processing time by 30%.",
  "proposed_text": "Cut batch-processing time by 30% through pipeline optimization.",
  "reason": "Connects the accomplishment to the role's performance requirement.",
  "matched_requirements": ["performance optimization"],
  "verification": {
    "status": "pass",
    "issues": []
  }
}
```

### Frontend Deliverables

- Replace the all-at-once tailored display with an explicit review workflow.
- Show original text, proposed text, reason, matched requirement, and verification state.
- Add accept, edit, and reject actions for every suggestion.
- Permit accept-all only for verified suggestions.
- Create a durable draft variant from reviewed selections.
- Preview, approve, and export the variant.
- Remove the temporary master-mutation PDF route.

### Primary User Flow

```text
Provide job description
-> Generate suggestions
-> Review each suggestion
-> Accept, edit, or reject
-> Verify selected changes
-> Create resume variant
-> Preview and export
```

### Acceptance Gate

- Tailoring never changes master-profile rows.
- Every variant records its source-profile hash and tailoring run.
- New numeric claims fail deterministic verification.
- The user can accept some suggestions and reject others.
- The exported PDF exactly represents the approved variant.
- Failed tailoring or export cannot corrupt profile or variant data.

This phase creates the first trustworthy application-ready release.

## Phase 3: Job Workspace and Fit Analysis

### Objective

Connect analysis and tailoring to a persistent job instead of an anonymous block of pasted text.

### API Deliverables

- Add `Job` and `JobAnalysis`.
- Support manual creation and pasted descriptions.
- Preserve original descriptions and compute content hashes.
- Detect duplicates by source URL and description hash.
- Extract required and preferred qualifications separately.
- Extract responsibilities, location, workplace type, compensation, and authorization language when present.
- Map requirements to specific profile evidence.
- Store gaps and uncertainty explicitly.
- Add safe URL import only after SSRF, timeout, size, and content-type protections exist.

Proposed endpoints:

```http
POST  /v1/jobs
GET   /v1/jobs
GET   /v1/jobs/{job_id}
PATCH /v1/jobs/{job_id}
POST  /v1/jobs/{job_id}/analyze
GET   /v1/jobs/{job_id}/analyses/latest
POST  /v1/jobs/{job_id}/tailoring-runs
```

### Frontend Deliverables

- Add job list and manual-job creation routes.
- Add job detail with Posting, Fit, Tailor, and Application sections.
- Show matching evidence, gaps, uncertain qualifications, and possible disqualifiers.
- Link every claimed match to master-profile evidence.
- Start tailoring from the persistent job workspace.
- Treat a numeric match score as secondary and explain its inputs if shown.

### Acceptance Gate

- A pasted job becomes a durable record.
- Duplicate jobs are detected.
- Required and preferred qualifications remain distinct.
- Every claimed match links to profile evidence.
- A user can create a resume variant from a job.
- The job, analysis, tailoring run, and resulting variant remain connected.

## Phase 4: Application Tracking

### Objective

Manage each shortlisted role from preparation through its final outcome.

### API Deliverables

- Add `Application` and application timeline events.
- Enforce a documented status state machine.
- Connect the approved resume variant actually used.
- Add submission URL, notes, applied date, and follow-up date.
- Add filtering by status, company, date, and follow-up state.

Suggested statuses:

```text
shortlisted
preparing
ready
applied
screening
interviewing
offer
rejected
withdrawn
archived
```

Proposed endpoints:

```http
POST  /v1/applications
GET   /v1/applications
GET   /v1/applications/{application_id}
PATCH /v1/applications/{application_id}
POST  /v1/applications/{application_id}/events
GET   /v1/applications/{application_id}/events
```

### Frontend Deliverables

- Add application table and board views.
- Add a Ready to Apply checklist.
- Add follow-up queue and reminders within the product.
- Add status history and notes.
- Link to the exact submitted resume variant.
- Add manual outcome recording.

### Ready to Apply Checklist

- Job is still available
- Required qualifications reviewed
- Resume variant approved
- PDF generated successfully
- Contact details verified
- Screening answers reviewed
- Submission link available

### Acceptance Gate

- Every submitted application records the resume variant used.
- Status changes retain timestamps and history.
- Follow-ups due today are visible.
- Rejected and archived roles do not clutter active work.
- Referenced application documents remain recoverable.

Completion of Phases 0 through 4 is the target boundary for the January 2027 job search.

## Phase 5: Rendering and Document Quality

### Objective

Improve document reliability and evaluate LaTeX without making it the source of truth.

### API Deliverables

- Extract a shared renderer interface around `ResumeDocument`.
- Retain the existing HTML/WeasyPrint renderer.
- Add PDF page-count checks.
- Extract and validate PDF text.
- Detect missing sections and obvious overflow.
- Store render metadata and a content hash.
- Evaluate a sandboxed LaTeX renderer using deterministic Jinja templates.
- Centralize LaTeX escaping.
- Apply compilation timeouts and filesystem/network restrictions.
- Return safe compilation diagnostics.
- Support `.tex` download if the renderer is retained.

### Frontend Deliverables

- Add PDF preview.
- Display page count and document-integrity warnings.
- Add template selection.
- Add LaTeX export only if it passes the decision gate.
- Keep structured content editing as the primary experience.

### LaTeX Decision Gate

Retain LaTeX only if it materially improves at least one of:

- Document quality
- Template flexibility
- ATS text extraction
- User-controlled export
- Overleaf interoperability

If it primarily adds deployment and compilation complexity, HTML remains the default and only renderer.

## Phase 6: Controlled Discovery and Application Assistance

### Objective

Surface appropriate jobs and reduce repetitive preparation without autonomous submission.

### API Deliverables

- Define a common `JobSource` adapter interface.
- Add Greenhouse and Lever company-board adapters first.
- Consider JobSpy behind the same interface.
- Add scheduled retrieval, deduplication, per-source rate limits, and health monitoring.
- Add company and role watchlists.
- Add a verified screening-answer bank.

### Frontend Deliverables

- Add discovery inbox.
- Add saved searches and company watchlists.
- Add shortlist, dismiss, and archive actions.
- Explain why each job appeared.
- Show source and freshness.
- Add copy-ready screening answers with explicit user confirmation.

### Guardrails

- One failed source cannot stop other sources.
- Discovery never submits an application.
- Sensitive demographic, disability, legal, and authorization answers are never inferred.
- Browser autofill, if pursued, begins with one ATS and requires confirmation before submission.

## Vertical Delivery Order

Implementation should proceed in working slices rather than completing an entire backend layer before frontend integration.

| Slice | API | Frontend | Proof |
|---|---|---|---|
| Foundation | Migrations and tests | Typed API client and error states | CI passes |
| Profile | Aggregate profile and partial updates | Master Profile workspace | No seed scripts needed |
| Variant | Variant and tailoring-run models | Suggestion review | Master remains unchanged |
| Export | Render from variant | Preview and download | PDF integrity passes |
| Job | Job CRUD | Job capture and detail | Durable job record |
| Analysis | Evidence mapping | Fit view | Traceable claims |
| Tracking | Application lifecycle | Board and follow-ups | Status history retained |
| Discovery | Source adapters | Discovery inbox | Dedupe and source isolation |

## Testing Strategy

### API

- Schema and model unit tests
- Migration upgrade tests
- CRUD integration tests
- Ownership and authorization tests
- Tailoring structured-output tests
- Deterministic claim-verification tests
- Malformed model-output tests
- Renderer snapshot and text-extraction tests
- Timeout and upstream-failure tests
- URL-import SSRF tests
- Application state-transition tests

### Frontend

- API adapter tests
- Profile form and validation tests
- Archive and restore tests
- Tailoring review tests
- Partial accept, edit, and reject tests
- Loading, empty, saved, stale, and error states
- Keyboard navigation tests
- Long job-title, description, and bullet handling
- PDF generation and download failure tests
- Application status and follow-up tests

### End-to-End Critical Path

```text
Create or edit profile
-> add job
-> analyze fit
-> tailor resume
-> reject one suggestion
-> approve variant
-> generate PDF
-> create application
-> mark applied
-> schedule follow-up
```

This becomes the primary Playwright workflow.

## Success Criteria

### Primary

- A selected job can become an approved, verified application PDF in less than 15 minutes.

### Supporting

- Every tailored claim is traceable to master-profile content.
- Master-profile corruption incidents remain at zero.
- PDF generation and text extraction succeed consistently.
- Application tracking requires minimal duplicate entry.
- The user can understand why a job matches and where genuine gaps exist.

### Counter-Metrics

- Unsupported claims must not increase as tailoring becomes faster.
- Application volume must not be optimized at the expense of fit or quality.
- Profile editing must not silently invalidate historical application records.
- Model and rendering failures must not cause data loss.

## Privacy and Ethical Review

The product will not employ:

- Fabricated career claims
- Opaque consequential recommendations
- Automatic sensitive-question answers
- Unattended application submission
- Pressure based on application counts or artificial profile-completion scores
- Silent profile mutation
- Hidden data retention

Before public hosting, add:

- Per-user authentication and authorization
- Data export and account deletion
- Retention controls
- Encrypted secrets
- Audit logging
- Model-provider disclosure
- Clear disclosure of data sent outside the local deployment

## Known Edge Cases

- The master profile changes while a tailoring run is pending.
- A source bullet is deleted after a variant was created.
- The model returns missing, duplicate, or unknown entry IDs.
- A model changes a metric while preserving similar wording.
- A job posting changes at the same URL.
- Two postings have identical descriptions but different locations.
- PDF generation succeeds but extracted text is incomplete.
- A resume exceeds its page target.
- A user leaves during tailoring and returns later.
- An application references an archived variant.
- The model provider is unavailable or rate-limited.
- A URL import attempts to access a private network address.

Each relevant phase must define recovery behavior for its edge cases before passing its acceptance gate.

## Open Questions

### Product

- Is ResuHost permanently personal/local-first, or should hosted multi-user use shape early authentication decisions?
- Which January 2027 role families should drive the first fit-analysis fixtures?
- Is one-page output a hard rule or a template preference?
- Should the base profile include private evidence not eligible for resume output?

### Engineering

- Should the current `Resume` snapshot table be migrated to `ResumeVariant` or temporarily retained as a legacy concept?
- Should master bullets be normalized into their own table after the initial personal release?
- Should long-running model calls use an in-process task initially or a durable job queue?
- Should profile import ship before or after trustworthy tailoring?
- Does LaTeX provide enough value over WeasyPrint to justify a second rendering runtime?

These questions do not block Phase 0. They must be resolved before the phase that depends on them.

## Decision Log

Record decisions here as implementation proceeds.

| Date | Decision | Reason | Revisit trigger |
|---|---|---|---|
| 2026-08-29 | Master Profile precedes job tailoring | Tailoring requires a trustworthy source record | Research shows imported resumes are sufficient without profile management |
| 2026-08-29 | Tailoring creates variants and never rewrites the master profile | Protects factual integrity and historical applications | None; foundational invariant |
| 2026-08-29 | Keep HTML/WeasyPrint as the initial renderer | It already works and reduces time to a usable personal tool | Phase 5 rendering evaluation |
| 2026-08-29 | Defer autonomous submission | High maintenance and trust cost relative to January objective | Core workflow is proven and a specific ATS need emerges |

## Definition of Done for the Personal Release

The personal release is complete when:

- The Master Profile is fully manageable through the frontend.
- A job can be saved and analyzed against profile evidence.
- Tailoring suggestions can be accepted, edited, or rejected.
- Deterministic verification blocks unsupported metrics and identity changes.
- An approved resume variant can be previewed and downloaded as a valid PDF.
- The master profile remains unchanged throughout tailoring and export.
- The application records the exact resume variant used.
- Follow-up dates and outcome history are visible.
- The critical end-to-end workflow passes automatically.

Discovery, LaTeX, autofill, billing, and multi-user hosting are not required for this release.
