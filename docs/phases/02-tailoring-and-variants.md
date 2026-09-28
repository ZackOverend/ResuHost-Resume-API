# Phase 2: Non-Destructive Tailoring and Resume Variants

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
