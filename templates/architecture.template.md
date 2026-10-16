# Architecture

## Context and revisions

- Run ID: `<run-id>`
- Target repository marker: `<non-sensitive ID>`
- Target kind/module scope: `<empty | existing | monorepo; module>`
- Approved requirements revision: `<revision>`
- Discovery/technology evidence: `<artifact IDs and paths>`
- Status: `draft | awaiting_approval | approved | rejected | superseded`

## Requirements and constraints

| Requirement ID | Architectural implication | Evidence/source IDs |
| --- | --- | --- |
| `<REQ-ID>` | `<implication>` | `<IDs>` |

## Current system and stack evidence

| Area | Observed value | Evidence | Confidence/unknowns |
| --- | --- | --- | --- |
| Languages/frameworks/build/test | `<observed or unknown>` | `<paths>` | `<notes>` |
| Existing architecture/module boundary | `<observed or empty>` | `<paths>` | `<notes>` |

## Options and decisions

| Decision ID | Options considered | Proposed option | Rationale/evidence | Consequences/risks | Human decision |
| --- | --- | --- | --- | --- | --- |
| `ADR-001` | `<options>` | `<proposal>` | `<evidence and REQ IDs>` | `<trade-offs>` | `pending/accepted/rejected` |

## Components and responsibilities

| Component | Responsibility | Interfaces/data | Requirement IDs | Existing or proposed |
| --- | --- | --- | --- | --- |
| `<component>` | `<responsibility>` | `<interfaces/data>` | `<IDs>` | `existing/proposed` |

## Data flow

```mermaid
flowchart LR
  Input[Story and repository context] --> Proposed[Proposed components]
  Proposed --> Output[Observable outcomes]
```

Replace this illustrative diagram with the flow evidenced by the actual requirements and target.

## Security, operations, dependencies, and validation

- Security/privacy boundaries: `<details or open questions>`
- External integrations and read/write boundaries: `<details or none>`
- Dependencies/configuration impacts: `<details>`
- Failure handling and observability: `<details>`
- Verification approach: `<checks derived from target evidence>`
- Unresolved questions/blockers: `<IDs or none>`

## Approval record

- Decision: `requested | approved | rejected`
- Human approver/time: `<pending>`
- Exact artifact revision: `<revision/digest>`
- Scope/conditions/evidence reference: `<pending>`