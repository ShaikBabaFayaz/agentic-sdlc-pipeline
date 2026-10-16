---
name: project-structure-planning
description: Propose a requirement-traceable directory and file tree for an empty target or scoped additions to an existing repository or monorepo without creating files.
---

# Project Structure Planning

## Use when

Use after requirements and architecture are approved and before any application directory or file is created or changed.

## Inputs

- Approved requirements and architecture revisions.
- Target classification, module boundaries, stack evidence, and repository conventions.
- Existing files, tests, manifests, and the structure-plan template.

## Procedure

1. For an empty repository, propose the smallest suitable structure consistent with approved requirements and explicitly approved technology choices. Ask about material decisions that remain open.
2. For an existing repository, extend its established layout. Mark every item as `reuse`, `modify`, or `add`; avoid recreating folders, unnecessary frameworks, and unrelated refactors.
3. For a monorepo, scope proposed paths to the selected module and identify any shared module/API impacts.
4. For every proposed path, record purpose, owner (pipeline artifact or target application), linked requirement IDs, dependencies/configuration changes, and test implications.
5. Identify conflicts, migration risks, security impacts, and approvals needed. Do not execute the proposal.

## Output and evidence

Write a proposed tree and per-path table to `structure-plan.md`, with evidence references and the exact requirements/architecture revisions used. Return blockers and required human decisions. Structural edits remain prohibited until the orchestrator records human approval for that revision.