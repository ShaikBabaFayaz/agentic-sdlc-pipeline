---
name: test-verification-discovery
description: Discover repository-specific build, test, lint, type-check, and output-validation procedures across unknown stacks, then record actual results and limitations.
---

# Test and Verification Discovery

## Use when

Use during planning to identify verification tasks and after implementation to execute approved, safe checks.

## Inputs

- Confirmed target/module, requirements and acceptance criteria, changed paths, repository instructions.
- Manifests, CI configuration, test directories, project docs, and verification template.

## Procedure

1. Find commands from repository evidence, not assumptions. Inspect root and relevant module configuration separately in monorepos.
2. Map every acceptance criterion to a test, inspection, or documented manual check. Identify gaps and output-document checks.
3. Before execution, assess side effects. Ask before installs, destructive operations, migrations, or network-dependent checks.
4. Record exact command, working directory, environment/version when available, exit status, concise output/evidence, and whether the check passed, failed, was blocked, or was not run.
5. Route failures to their cause. Never present an unavailable or skipped check as successful.

## Output

Produce or update `verification.md` with requirement-to-check traceability, actual execution evidence, failures, skipped checks, and limitations. Do not edit product code or suppress failures.