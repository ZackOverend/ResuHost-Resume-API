# Phase 6: Controlled Discovery and Application Assistance

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
