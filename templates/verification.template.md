# Verification

## Verification scope

- Run ID: `<run-id>`
- Target/module: `<path>`
- Requirements/plan revisions: `<revisions>`
- Change revision: `<commit/digest>`

## Checks

| Check ID | Requirement/task IDs | Command or procedure | Working directory/environment | Result (`passed/failed/blocked/not_run`) | Exit status | Evidence/output reference | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `VERIFY-001` | `<IDs>` | `<exact command or procedure>` | `<environment>` | `<result>` | `<code or n/a>` | `<reference>` | `<notes>` |

## Coverage gaps and limitations

- Acceptance criteria without a check: `<IDs and reason>`
- Tests or commands unavailable/not run: `<details>`
- Output-document quality checks: `<result/evidence>`
- Known environment limitations: `<details or none>`

## Conclusion

- Overall status: `passed | failed | partial | blocked`
- Failures routed to stage/task: `<IDs or none>`
- Verifier/time: `<identity and UTC time>`

> Record only checks actually run. A planned command is not test evidence.