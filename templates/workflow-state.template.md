# Workflow State Reference

> The machine-readable source of truth is `workflow-state.json`, created from `workflow-state.template.json`. This Markdown file describes its fields. Store one state file per target run under `.sdlc/<run-id>/`; keep paths workspace-relative and omit credentials, machine-specific absolute paths, and private remote URLs.

## Run

- Schema version: `1`
- Run ID: `<unique-run-id>`
- Created (UTC): `<timestamp>`
- Updated (UTC): `<timestamp>`
- Status: `active | blocked | waiting_approval | complete | abandoned`
- Current stage: `discovery | requirements | architecture | structure_planning | design_review | planning | implementation | review | verification | pr_preparation | complete`
- Next action: `<action or none>`

## Target

- Workspace-relative root: `.`
- Repository marker/name: `<non-sensitive identifier>`
- Base commit: `<commit or unknown>`
- Classification: `unknown | empty | existing | monorepo`
- Selected module scope: `<workspace-relative paths, or empty before discovery>`
- Root confirmed by user: `yes | no`
- Workflow artifact directory: `.sdlc/<run-id>/`

## Detected Stack

Record only discovered or human-approved values. Each non-empty technology claim must link to evidence.

- Languages/frameworks/build systems/package managers/dependencies: `<values or unknown>`
- Source/test directories and conventions: `<values or unknown>`
- Evidence paths and observations: `<references>`
- Proposed stack for empty target: `<only after architecture decision; otherwise none>`

## Story and Integration Plan

- Story summary: `<summary>`
- Required capabilities: `<capability IDs or none>`
- Optional capabilities: `<capability IDs or none>`
- Selected source IDs: `<source IDs>`

### Capability Bindings

| Capability | MCP server/tool ID | Operation class | Mapping evidence | User confirmed | Status |
| --- | --- | --- | --- | --- | --- |
| `<capability>` | `<verified ID or none>` | `read-only` | `<reference>` | `yes/no` | `available/not_configured/disabled/disconnected/denied/failed` |

## Sources

| Source ID | Type | Provider/capability | Resource or local path | Retrieved (UTC) | Revision | Citations | Fields present/missing | Completeness/status | Limitation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `<source-id>` | `direct/local/mcp` | `<provider/capability or n/a>` | `<reference>` | `<time>` | `<revision or unknown>` | `<anchors or unknown>` | `<fields>` | `complete/partial/not_configured/disabled/disconnected/denied/failed` | `<details or none>` |

## Requirements and Tasks

- Requirement IDs: `<stable IDs linked to source IDs>`
- Tasks: `<task ID, requirement IDs, dependencies, status, evidence>`
- Source conflicts: `<source IDs, status, linked blocker ID>`

## Artifacts

The JSON state keeps `active_artifacts` as a map from artifact type to the one current artifact ID and revision. Historical artifacts and approvals may remain recorded, but only an approval for the active ID/revision satisfies a gate.

| Artifact ID | Path | Status | Revision | Linked IDs |
| --- | --- | --- | --- | --- |
| `<artifact-id>` | `<workspace-relative path>` | `pending/draft/approved/incomplete/invalidated` | `<commit or digest>` | `<requirement/source/task IDs>` |

### Active Artifact References

| Type | Active artifact ID | Active revision |
| --- | --- | --- |
| `<requirements/architecture/...>` | `<artifact-id>` | `<revision>` |

## Prerequisites

| ID | Requirement | Status | Waiver approval ID | Evidence reference | Checked (UTC) |
| --- | --- | --- | --- | --- | --- |
| `<prerequisite-id>` | `<condition>` | `pending/met/blocked/waived` | `<human approval ID or none>` | `<path or URL>` | `<time>` |

## Approvals

| Approval ID | Gate | Decision | Human approver | Time (UTC) | Artifact type/ID/revision | Scope/rationale | Evidence reference |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `<approval-id>` | `requirements` | `requested/approved/rejected` | `<human or pending>` | `<time or pending>` | `<type, ID, exact revision>` | `<scope and rationale>` | `<human-authored evidence or pending>` |

Prerequisite waivers use gate `prerequisite_waiver`, identify `prerequisite_id`, and include a human approver, time, rationale, scope, and evidence reference.

> Agents must not create an `approved` decision based on their own output. A local record is auditable but is not cryptographic identity proof.

## Blockers

| Blocker ID | Reason | Owner | Status | Opened | Resolution/evidence |
| --- | --- | --- | --- | --- | --- |
| `<blocker-id>` | `<reason>` | `<owner>` | `open/resolved` | `<time>` | `<details or reference>` |

## Source Conflicts

| Conflict ID | Status | Blocker ID/status | Resolution evidence |
| --- | --- | --- | --- |
| `<conflict-id>` | `open/resolved` | `<matching open/resolved blocker>` | `<required when resolved>` |

Every open conflict must link to an open blocker. A resolved conflict must link to a resolved blocker and include resolution evidence.

## Verification Evidence

| Check ID | Required | Command/procedure | Status | Exit status | Evidence reference |
| --- | --- | --- | --- | --- | --- |
| `<check-id>` | `yes/no` | `<actual command or procedure>` | `passed/failed/blocked/not_run` | `<code or n/a>` | `<output reference>` |

An artifact marked `passed` requires actual evidence for every required check. `accepted_limitations` requires a separate human approval tied to the active verification artifact ID and revision.

## Rework Log

| Rework ID | Cause | From stage | To stage | Affected artifact IDs | Status | Evidence reference |
| --- | --- | --- | --- | --- | --- | --- |
| `RW-001` | `<cause>` | `<stage>` | `<stage>` | `<artifact IDs>` | `open/resolved` | `<failure or resolution evidence>` |

## Transition Rules

`discovery -> requirements -> architecture -> structure_planning -> design_review -> planning -> implementation -> review -> verification -> pr_preparation -> complete`.
Rework may return to an earlier responsible stage. The validator checks legal next-stage transitions, required artifact revisions, traceability, blockers, and human approval evidence. An agent statement or tool-call approval is not a human gate approval.