---
name: resume-sdlc
description: Resume a saved SDLC run after reconciling workflow state and artifact revisions.
argument-hint: "Provide the target repository and state artifact path."
agent: SDLC Orchestrator
---

Resume the run identified by `${input:statePath:.sdlc/<run-id>/workflow-state.json}` using the SDLC Orchestrator. Confirm the target, read persistent state and linked artifacts, compare recorded revisions, and reconcile inconsistencies before continuing. Never infer progress from conversation history or skip an approval gate. Report blockers and the next permitted stage.