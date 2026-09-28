# Delivery and Quality

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
