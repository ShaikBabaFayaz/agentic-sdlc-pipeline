---
name: implementation-planning
description: Break approved requirements, architecture, structure, and design decisions into traceable dependency-ordered implementation and verification tasks.
---

# Implementation Planning

## Use when

Use after architecture, structure, and design review are approved and blocking findings are resolved or explicitly accepted.

## Inputs

- Approved requirements, architecture, structure plan, and design-review revisions.
- Repository conventions, module boundaries, and discovered verification commands.
- Implementation-plan template and any user constraints on scope/order.

## Procedure

1. Create stable task IDs in dependency order; identify parallelizable work only where dependencies permit.
2. For each task specify purpose, requirement IDs, proposed file/module scope, prerequisite task IDs, measurable completion criteria, and verification evidence.
3. Include tests, documentation, migrations/configuration, code review, and verification where they are required by evidence.
4. Record blocked tasks with the exact missing dependency or decision. Do not invent commands or mark work complete.

## Output

Produce `impl-plan.md` and a traceability map from requirement to design/structure decisions, tasks, and tests. Return blockers and approval needs. No implementation begins until the human approves the exact plan revision.