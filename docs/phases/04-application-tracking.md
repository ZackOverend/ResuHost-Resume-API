# Phase 4: Application Tracking

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
