---
name: run-sdlc-stage
description: Request one explicitly named, currently permitted SDLC stage through the orchestrator.
argument-hint: "Provide the stage name and relevant run ID or state path."
agent: SDLC Orchestrator
---

Ask the SDLC Orchestrator to run only the requested stage `${input:stage:requirements}` for `${input:runId:<run-id>}`. First verify the saved state, target, prerequisites, artifact revisions, and required human approvals. If the stage is blocked, unauthorized, or its specialist is unavailable, record the blocker and stop; do not substitute another workflow or advance further.