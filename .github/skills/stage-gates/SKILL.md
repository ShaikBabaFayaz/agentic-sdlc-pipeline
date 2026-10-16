---
name: stage-gates
description: Apply artifact prerequisites, human approval evidence, blockers, and rework rules before advancing the Agentic SDLC workflow.
---

# Stage Gates

The orchestrator owns stage transitions. Use this checklist before changing run state or reporting a gate as passed.

## Requirements gate

- Confirm the target root and run ID match the state artifact.
- Confirm story inputs and their source records are linked to the requirements. Required sources are complete, or a human has explicitly accepted a recorded fallback/limitation. Partial or conflicting criteria are not silently treated as complete.
- Confirm requirement IDs and acceptance criteria are present, with assumptions, open questions, and non-functional requirements recorded where applicable.
- Set prerequisites to `met`, `pending`, `blocked`, or `waived`, with evidence references. A waiver requires a human decision and rationale.
- Set the state to `waiting_approval` until a human-authored approval record references the exact requirements revision and scope.

## Approval evidence

An agent statement, generated approval entry, or tool-call permission is not business approval. Record approver, gate, decision, time, artifact revision, scope/conditions, and an evidence reference. Do not infer approval from silence or from a response that cannot be tied to the artifact revision. If the human approval source cannot be verified, leave the gate waiting.

## Blockers and rework

- Record missing inputs, MCP availability failures, incomplete source data, ambiguous target, and unresolved conflicts as blockers with status and next action.
- A failed check returns to the earliest stage responsible for its cause. A changed requirement invalidates linked downstream decisions/tasks/evidence and records the affected artifact IDs in the rework log.
- Resume only after recording the resolution and rechecking prerequisites. Never mark unavailable checks or integrations as successful.
- This skill guides behavior; it does not provide deterministic enforcement. Report any prerequisite that could not be independently checked.