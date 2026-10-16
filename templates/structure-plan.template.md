# Project Structure Plan

## Inputs and scope

- Run ID: `<run-id>`
- Target kind: `empty | existing | monorepo`
- Target module/root: `<workspace-relative path>`
- Requirements revision: `<revision>`
- Architecture revision: `<revision>`
- Technology/repository evidence: `<artifact IDs and paths>`
- Status: `draft | awaiting_approval | approved | rejected | superseded`

## Proposed tree

```text
<Only paths justified by approved requirements and repository evidence>
```

## Path decisions

| Path | Action (`reuse/modify/add`) | Purpose | Owner (`pipeline/target`) | Requirement IDs | Dependencies/config impacts | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| `<path>` | `<action>` | `<purpose>` | `<owner>` | `<IDs>` | `<impact or none>` | `<check>` |

## Existing files and module boundaries

- Files/modules to reuse: `<paths and evidence>`
- Files/modules to modify: `<paths and scope>`
- Monorepo boundaries/shared API impacts: `<paths or not applicable>`
- Files explicitly out of scope: `<paths or none>`

## Alternatives, risks, and decisions

| ID | Question/risk/alternative | Impact | Human decision/evidence |
| --- | --- | --- | --- |
| `<ID>` | `<details>` | `<impact>` | `pending` |

## Approval record

- Decision: `requested | approved | rejected`
- Human approver/time: `<pending>`
- Exact artifact revision: `<revision/digest>`
- Approved paths and conditions: `<pending>`
- Evidence reference: `<pending>`

> This is a proposal. Do not create directories or application files until approval of this exact revision is recorded.