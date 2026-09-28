# Phase 5: Rendering and Document Quality

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
