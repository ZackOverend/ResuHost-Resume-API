# Phase 3: Job Workspace and Fit Analysis

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
