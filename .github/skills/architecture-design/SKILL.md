---
name: architecture-design
description: Design and compare solution architecture options from approved requirements and discovered repository evidence without imposing a fixed application stack.
---

# Architecture Design

## Use when

Use after requirements clarification and human approval, before structure planning or application edits.

## Inputs

- Requirements artifact and exact approved revision.
- Repository/module discovery and technology evidence, or an evidence-backed empty-repository classification.
- Constraints, user decisions, unresolved questions, and architecture template.

## Procedure

1. Map each architecture decision to requirement IDs and repository evidence.
2. For existing code, fit the current architecture and module boundaries unless approved requirements justify a change. For an empty repository, present options; do not silently choose a language/framework.
3. Describe components, responsibilities, interfaces, data/control flow, persistence/integration boundaries, operational/security concerns, and testing approach as relevant.
4. Compare viable alternatives and consequences. Record assumptions, dependencies, risks, and questions.

## Output

Produce `architecture.md` with decisions, options, diagrams where useful, traceability, evidence, risks, and unresolved decisions. Do not implement or declare the architecture approved. Return the exact revision and approval needs to the orchestrator.