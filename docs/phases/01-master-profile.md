# Phase 1: Master Profile Workspace

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
