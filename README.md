# Agentic SDLC Pipeline

A generic, human-supervised GitHub Copilot workflow for moving a User Story through requirements, architecture, design review, structure planning, implementation planning, implementation, code review, verification, and PR preparation. It discovers the target repository's language, framework, build/test tools, conventions, and module boundaries; it does not prescribe an application stack.

The original capstone is titled **Agentic SDLC Use Case: Automated Documentation Sync** and describes the full eight-stage lifecycle, including commits and PR creation. The pipeline remains reusable for arbitrary stories and repositories. External actions (commit, push, merge, PR creation, and service writes) require separate authorization and are not performed by default.

## Customizations

- `.github/agents/` contains the orchestrator and bounded specialists for source retrieval, requirements, architecture, structure planning, design review, implementation planning, implementation, code review, verification, and PR materials.
- `.github/skills/` contains reusable discovery, stack-detection, architecture, structure/planning, safe implementation, review, verification, and gate procedures.
- `.github/prompts/` contains five optional start/resume/stage/review/PR entry points. Current VS Code documentation supports prompt files only in the **Local harness**. With the Copilot harness selected, choose `SDLC Orchestrator` directly; prompts are not a workflow dependency.
- `templates/` contains run-state and stage artifact templates. Run-specific artifacts belong under the target's `.sdlc/<run-id>/`, not in this pipeline source tree.
- `scripts/validate_workflow.py` validates customization metadata, persisted state, traceability, prerequisites, approvals, and stage transitions. `tests/` contains standard-library unit tests and synthetic state fixtures.

## Target Repository Operation

Use a reviewed, non-destructive installation into a disposable target copy first:

1. Confirm the target Git root and inspect its status. For a monorepo, identify the relevant module from the story and repository evidence.
2. Copy `.github/agents/` and `.github/skills/` into the target, preserving existing files. Copy `.github/prompts/` only if using the Local harness.
3. Copy `templates/`, `scripts/`, and relevant `docs/` under `.github/sdlc-pipeline/`. Do not copy this pipeline repo's `.github/copilot-instructions.md` over target instructions.
4. Open only the target repository in VS Code. Confirm the agent/customization source and target root before a run. The orchestrator stores state and workflow artifacts under `.sdlc/<run-id>/`.
5. Review every proposed structure and approve the exact structure-plan revision before application directories/files are created. The implementer must remain within the approved plan and task IDs.

For an empty repository, the architecture and structure planner propose options based on approved requirements; they must ask about material stack decisions. For an existing repository, they reuse its current conventions. For a monorepo, they record and respect module scope. None of these agents should create application files during planning.

Workspace tools and agent instructions are not an OS security boundary. Use Manual permissions, inspect diffs, preserve unrelated changes, and do not test against the only copy of a real application. This repository's fixtures are synthetic and do not modify target applications.

## Optional MCP

Direct user input and local documents work without MCP. MCP is provider-neutral and read-only for retrieval; no GitHub, Jira, or Confluence server, endpoint, credential, or write tool is configured or claimed as tested. Read [MCP integration guidance](docs/mcp-integration.md) before configuring a specific verified provider. Disable mutating tools and use per-call approvals. Preserve source provenance and report missing, partial, conflicting, or unavailable data honestly.

## Validation

From the pipeline root, run:

```powershell
python -m unittest discover -s tests -v
python scripts/validate_workflow.py --root .
python scripts/validate_workflow.py --root . --state tests/fixtures/workflow-states/empty-target.json
```

To check a proposed stage transition, add `--next-stage <stage>` to the last command. The validator checks metadata and state records; it does not run application tests, prove live Copilot customization discovery, or test MCP providers.

See [workflow architecture](docs/workflow.md) and [customization support](docs/customization-support.md) for stage gates, agent contracts, harness constraints, and limitations. No target application was modified as part of developing or testing this pipeline.
