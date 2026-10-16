---
name: technology-stack-detection
description: Detect evidenced languages, frameworks, build systems, package managers, dependencies, and tests for an explicitly selected existing repository, empty repository, or monorepo module.
---

# Technology Stack Detection

## Use when

Use after confirming the target root and before architecture or structure planning. Repeat discovery when the target module or relevant files change.

## Inputs

- Confirmed target root and repository classification.
- User Story, approved requirements, and relevant file/module scope.
- Repository instructions and access to the existing workspace.

## Procedure

1. Inspect repository files, manifests, lockfiles, build configuration, CI, docs, source/test directories, and representative code. For a monorepo, inspect the root workspace plus the candidate modules and identify the story-relevant module.
2. Record each conclusion with a file/path or command-output reference. Distinguish direct evidence, likely inference, and unknown. Do not infer a framework from one file extension or select a stack for an empty repository.
3. Identify existing conventions, architecture boundaries, testing tools, and dependency management. Do not read secret values.
4. If evidence conflicts or the relevant module is unclear, ask the user and mark detection incomplete.

## Output

Return repository kind; module scope; languages, frameworks, build systems, package managers and relevant dependencies; source/test locations; conventions; evidence references; confidence/unknowns; and verification commands found. The orchestrator records this evidence in workflow state. No files are modified.