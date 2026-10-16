# Requirements

## Story

- Title: `<title>`
- Summary: `<summary>`
- User-provided story/source IDs: `<IDs>`
- Target repository marker: `<non-sensitive marker>`
- Status: `draft | incomplete | awaiting_approval | approved`

## Source Records

| Source ID | Type | Provider/capability | Resource or local path | Retrieved/version | Citation | Completeness/status | Missing data or limitation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `<source-id>` | `direct/local/mcp` | `<provider/capability or n/a>` | `<reference>` | `<time; revision or unknown>` | `<anchor or unknown>` | `<complete/partial/failure status>` | `<details or none>` |

## Functional Requirements

| Requirement ID | Requirement | Acceptance criteria | Source IDs | Status |
| --- | --- | --- | --- | --- |
| `REQ-001` | `<requirement>` | `<observable, testable outcome>` | `<source IDs>` | `draft/confirmed/blocked` |

## Non-Functional Requirements

| Requirement ID | Requirement | Acceptance criteria or measure | Source IDs | Status |
| --- | --- | --- | --- | --- |
| `NFR-001` | `<requirement or none identified>` | `<measure or open question>` | `<source IDs>` | `draft/confirmed/blocked` |

## Assumptions and Decisions Needed

| ID | Statement or question | Owner | Status | Evidence/decision |
| --- | --- | --- | --- | --- |
| `Q-001` | `<assumption or question>` | `<human/agent>` | `open/answered/accepted` | `<reference>` |

## Conflicts and Incomplete Data

| ID | Source IDs | Conflict or missing information | Impact | Resolution required |
| --- | --- | --- | --- | --- |
| `GAP-001` | `<source IDs>` | `<details or none>` | `<impact>` | `<human clarification or none>` |

## Approval Record

- Decision: `requested | approved | rejected | waived`
- Human approver: `<name/identity or pending>`
- Approved at (UTC): `<timestamp or pending>`
- Exact artifact revision: `<commit or content digest>`
- Scope and conditions: `<scope>`
- Human-authored evidence reference: `<issue/review/commit reference or pending>`

> Agent-generated claims and tool-call confirmations are not requirements approval. Do not mark approved until a human records evidence for this exact revision.