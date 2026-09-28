# ResuHost Documentation

Start with the [roadmap](ROADMAP.md) for current status and navigation.

## Core Documents

- [Roadmap](ROADMAP.md) — progress, current phase, and next work
- [Product and architecture](PRODUCT_AND_ARCHITECTURE.md) — product boundaries and technical direction
- [Delivery and quality](reference/DELIVERY_AND_QUALITY.md) — sequencing, tests, and success measures
- [Governance and decisions](reference/GOVERNANCE_AND_DECISIONS.md) — risks, open questions, decisions, and release criteria

## Phase Plans

Each phase file contains its objective, API and frontend deliverables, workflows, and acceptance gate.

1. [Foundation](phases/00-foundation.md)
2. [Master Profile](phases/01-master-profile.md)
3. [Tailoring and resume variants](phases/02-tailoring-and-variants.md)
4. [Job workspace and fit analysis](phases/03-job-workspace.md)
5. [Application tracking](phases/04-application-tracking.md)
6. [Rendering and document quality](phases/05-rendering.md)
7. [Controlled discovery and assistance](phases/06-discovery-and-assistance.md)

## Maintenance Rules

- Update `ROADMAP.md` when work starts, completes, or changes direction.
- Update a phase file when its scope or acceptance gate changes.
- Record durable cross-phase decisions in the governance decision log.
- Keep setup and operational instructions in the repository root `README.md`.
- Prefer links over duplicating the same requirement in multiple files.
