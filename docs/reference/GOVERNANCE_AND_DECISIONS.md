# Governance and Decisions

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
