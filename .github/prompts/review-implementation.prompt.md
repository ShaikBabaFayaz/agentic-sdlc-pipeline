---
name: review-implementation
description: Ask the orchestrator to run the read-only implementation review stage for an approved change.
argument-hint: "Provide the run ID, target/module, and implementation revision."
agent: SDLC Orchestrator
---

Ask the SDLC Orchestrator to verify the implementation stage prerequisites and delegate a read-only review to `code-reviewer`. Review only the approved target, module, task IDs, and revision. Record findings in the run artifact; do not edit or fix code during review. If approvals or evidence are missing, stop and report the blocker.