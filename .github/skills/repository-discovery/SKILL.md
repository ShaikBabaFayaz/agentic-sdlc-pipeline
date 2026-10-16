---
name: repository-discovery
description: Inspect and classify an explicitly selected target repository before requirements work, including empty and established repositories, without assuming a language or toolchain.
---

# Repository Discovery

Use this skill before drafting requirements for a target repository.

## Procedure

1. Confirm the target workspace root with the user. If it is missing or ambiguous, stop and ask. Never infer that the pipeline repository is the target.
2. When Git is available, identify the repository root and inspect its status using read-only commands. Do not reset, clean, checkout, commit, or edit files.
3. Inspect the top-level structure, project instructions, manifests, build configuration, tests, and relevant nearby source files. Follow the target repository's own instructions. Do not copy or replace them with pipeline instructions.
4. Classify the repository as `empty`, `existing`, or `uncertain`, and cite the files or observations that support the classification.
5. Record discovered languages, frameworks, build/test tools, conventions, and unknowns only when there is evidence. An absent manifest or test suite is an observation, not permission to choose one.
6. Avoid reading secret values, credentials, generated outputs, or unrelated large files. If a relevant instruction conflicts with this workflow or makes safe discovery impossible, pause and report it.

## Output

Return the confirmed target root (workspace-relative in saved artifacts), classification, repository instructions found, relevant files inspected, evidenced technologies and checks, unknowns, and any blockers. Keep discovery read-only. The orchestrator is responsible for state transitions and approval gates.