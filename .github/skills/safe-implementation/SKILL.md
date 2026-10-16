---
name: safe-implementation
description: Implement only human-approved task IDs in the confirmed target and module, preserving repository conventions and avoiding unrelated or unapproved changes.
---

# Safe Implementation

## Use when

Use only after requirements, architecture, structure plan, and implementation plan have the required human approvals.

## Inputs

- Confirmed target root and monorepo module scope.
- Approved task IDs and exact plan/structure revisions.
- Repository instructions, stack evidence, existing Git status, and available checks.

## Procedure

1. Recheck target identity, module scope, current status, and task approvals. Stop if the baseline has unexpected changes or approval evidence is stale.
2. Read nearby implementation and tests. Follow the discovered language, architecture, conventions, and dependency tooling.
3. Edit only files in the approved scope. Do not create directories or dependencies absent from the approved structure plan. Do not refactor unrelated code.
4. Ask before destructive commands, dependency installation, migrations, network access, or scope expansion. Never commit, push, merge, or write external resources without separate explicit authorization.
5. Run safe, relevant checks and preserve actual output/status. If a check fails, report the evidence; do not hide or relabel failure.

## Output

Return completed task IDs, changed paths, rationale, commands/results, remaining blockers, and any proposed scope change. Route scope/design changes to the orchestrator for approval before proceeding.