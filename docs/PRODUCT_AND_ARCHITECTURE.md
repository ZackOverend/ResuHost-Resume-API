# Product and Architecture

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
