---
name: code-review
description: Review implementation changes against approved requirements, task scope, security, error handling, tests, and repository conventions without editing code.
---

# Code Review

## Use when

Use after an implementer reports completion and before final verification or PR preparation.

## Inputs

- Approved requirements and implementation-plan revisions.
- Target/module scope, current diff, repository instructions, and test evidence.
- Code-review template and linked requirement/task IDs.

## Procedure

1. Review changes read-only and verify they stay within approved target/module/task scope.
2. Check correctness, security/secrets, error paths, boundary conditions, empty/existing/monorepo behavior, test coverage, readability, duplication, and dependency safety.
3. Report concrete, reproducible findings first, ordered by severity. Cite paths, requirement/task IDs, impact, and a suggested fix.
4. Distinguish confirmed defects from questions or risks. Do not infer passing tests from code inspection.

## Output and handoff

Write `code-review.md` with reviewed revision, scope, findings, and what was/was not checked. Blocking issues return to implementation or planning; resolved findings need evidence and re-review. The reviewer does not edit code or approve its own findings.