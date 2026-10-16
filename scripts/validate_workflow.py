"""Validate pipeline customizations and persisted workflow state using stdlib only."""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any


STAGES = (
    "discovery",
    "requirements",
    "architecture",
    "structure_planning",
    "design_review",
    "planning",
    "implementation",
    "review",
    "verification",
    "pr_preparation",
    "complete",
)
STATUSES = ("active", "blocked", "waiting_approval", "complete", "abandoned")
SOURCE_STATUSES = (
    "complete",
    "partial",
    "not_configured",
    "disabled",
    "disconnected",
    "denied",
    "failed",
)
REPOSITORY_KINDS = ("unknown", "empty", "existing", "monorepo")
TRANSITIONS = {
    "discovery": {"requirements"},
    "requirements": {"architecture"},
    "architecture": {"structure_planning"},
    "structure_planning": {"design_review"},
    "design_review": {"architecture", "structure_planning", "planning"},
    "planning": {"architecture", "structure_planning", "implementation"},
    "implementation": {"planning", "review"},
    "review": {"implementation", "planning", "verification"},
    "verification": {"implementation", "planning", "pr_preparation"},
    "pr_preparation": {"verification", "complete"},
    "complete": set(),
}

REQUIRED_FIELDS = (
    "schema_version",
    "run_id",
    "status",
    "stage",
    "target",
    "detected_stack",
    "story_sources",
    "integration_plan",
    "requirement_ids",
    "tasks",
    "artifacts",
    "active_artifacts",
    "prerequisites",
    "approvals",
    "blockers",
    "source_conflicts",
    "review_findings",
    "verification_evidence",
    "rework_history",
)

EXPECTED_AGENT_NAMES = {
    "SDLC Orchestrator",
    "source-retriever",
    "requirements-analyst",
    "architecture-designer",
    "design-reviewer",
    "project-structure-planner",
    "implementation-planner",
    "implementer",
    "code-reviewer",
    "test-verifier",
    "pr-preparer",
}
EXPECTED_PROMPTS = {
    "start-sdlc",
    "resume-sdlc",
    "run-sdlc-stage",
    "review-implementation",
    "prepare-pr",
}
REQUIRED_AGENT_SKILLS = {
    "SDLC Orchestrator": {
        "repository-discovery",
        "technology-stack-detection",
        "source-retrieval",
        "stage-gates",
    },
    "source-retriever": {"source-retrieval"},
    "requirements-analyst": {"repository-discovery", "source-retrieval", "stage-gates"},
    "architecture-designer": {"technology-stack-detection", "architecture-design"},
    "design-reviewer": {"architecture-design", "project-structure-planning", "stage-gates"},
    "project-structure-planner": {"technology-stack-detection", "project-structure-planning"},
    "implementation-planner": {"implementation-planning", "test-verification-discovery", "stage-gates"},
    "implementer": {"safe-implementation"},
    "code-reviewer": {"code-review", "stage-gates"},
    "test-verifier": {"test-verification-discovery"},
    "pr-preparer": {"stage-gates", "test-verification-discovery"},
}
READ_ONLY_AGENT_NAMES = EXPECTED_AGENT_NAMES - {"SDLC Orchestrator", "implementer"}
NO_EXECUTE_AGENT_NAMES = READ_ONLY_AGENT_NAMES - {"test-verifier"}


def _frontmatter(path: Path) -> tuple[dict[str, Any], str, list[str]]:
    errors: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        return {}, "", [f"Cannot read {path}: {error}"]

    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", text, re.DOTALL)
    if not match:
        return {}, "", [f"Missing valid YAML frontmatter: {path}"]

    metadata: dict[str, Any] = {}
    for line in match.group(1).splitlines():
        if not line or line[0].isspace() or line.lstrip().startswith("#"):
            continue
        field = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):\s*(.*?)\s*$", line)
        if not field:
            errors.append(f"Unsupported frontmatter line in {path}: {line}")
            continue
        key, value = field.groups()
        if value.startswith(("[", "'", '"')):
            try:
                value = ast.literal_eval(value)
            except (SyntaxError, ValueError):
                errors.append(f"Invalid supported YAML subset for {key} in {path}")
                continue
        metadata[key] = value
    return metadata, text[match.end() :], errors


def _safe_relative_path(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    posix_path = PurePosixPath(value)
    windows_path = PureWindowsPath(value)
    return (
        not posix_path.is_absolute()
        and not windows_path.is_absolute()
        and ".." not in posix_path.parts
        and ".." not in windows_path.parts
    )


def validate_customizations(root: Path) -> list[str]:
    errors: list[str] = []
    agents_dir = root / ".github" / "agents"
    skills_dir = root / ".github" / "skills"
    prompts_dir = root / ".github" / "prompts"

    agent_paths = sorted(agents_dir.glob("*.agent.md"))
    skill_paths = sorted(skills_dir.glob("*/SKILL.md"))
    prompt_paths = sorted(prompts_dir.glob("*.prompt.md"))
    if not agent_paths:
        errors.append(f"No custom agents found under {agents_dir}")
    if not skill_paths:
        errors.append(f"No skills found under {skills_dir}")
    if not prompt_paths:
        errors.append(f"No prompt files found under {prompts_dir}")

    agent_names: set[str] = set()
    agent_metadata: dict[str, dict[str, Any]] = {}
    for path in agent_paths:
        metadata, body, frontmatter_errors = _frontmatter(path)
        errors.extend(frontmatter_errors)
        name = metadata.get("name")
        description = metadata.get("description")
        if not isinstance(name, str) or not name.strip():
            errors.append(f"Agent has no name: {path}")
            continue
        if name in agent_names:
            errors.append(f"Duplicate agent name: {name}")
        agent_names.add(name)
        agent_metadata[name] = metadata
        if not isinstance(description, str) or not description.strip():
            errors.append(f"Agent has no description: {path}")
        if not body.strip():
            errors.append(f"Agent has no instruction body: {path}")
        if name != "source-retriever":
            tools = metadata.get("tools")
            if not isinstance(tools, list) or not tools:
                errors.append(f"Agent must declare allowed tools: {path}")
        else:
            tools = metadata.get("tools")
            if not isinstance(tools, list) or not tools:
                errors.append("source-retriever must have an explicit tool allow-list")
        tools = metadata.get("tools", [])
        if not isinstance(tools, list) or not all(isinstance(tool, str) for tool in tools):
            errors.append(f"Agent tools must be an array of tool names: {path}")
            tools = []
        if name in READ_ONLY_AGENT_NAMES and "edit" in tools:
            errors.append(f"Read-only agent has edit tool: {name}")
        if name in NO_EXECUTE_AGENT_NAMES and "execute" in tools:
            errors.append(f"Non-executing agent has execute tool: {name}")
        if name == "source-retriever" and set(tools) - {"read", "search"}:
            errors.append("source-retriever may only enable local read/search until MCP tools are verified")
        allowed_agents = metadata.get("agents")
        if allowed_agents is not None and not isinstance(allowed_agents, list):
            errors.append(f"Agent allow-list must be a list: {path}")
        skill_references = {
            reference.rstrip(".,;")
            for reference in re.findall(r"#file:([^\s)]+)", body)
        }
        expected_skills = REQUIRED_AGENT_SKILLS.get(name, set())
        for skill_name in expected_skills:
            expected_reference = f"../skills/{skill_name}/SKILL.md"
            if expected_reference not in skill_references:
                errors.append(f"Agent {name} must reference skill {skill_name} with #file:")
        for reference in skill_references:
            skill_path = (path.parent / reference).resolve()
            if not skill_path.is_file() or skill_path.name != "SKILL.md":
                errors.append(f"Invalid skill reference in {path}: {reference}")

    missing_agents = EXPECTED_AGENT_NAMES - agent_names
    for name in sorted(missing_agents):
        errors.append(f"Required specialist agent is missing: {name}")

    orchestrator = agent_metadata.get("SDLC Orchestrator", {})
    delegated_agents = orchestrator.get("agents", [])
    if isinstance(delegated_agents, list):
        missing_delegates = EXPECTED_AGENT_NAMES - {"SDLC Orchestrator"} - set(
            delegated_agents
        )
        for name in sorted(missing_delegates):
            errors.append(f"Orchestrator does not allow specialist: {name}")
        if delegated_agents and "agent" not in orchestrator.get("tools", []):
            errors.append("Orchestrator must enable the agent tool to delegate")

    for path in skill_paths:
        metadata, body, frontmatter_errors = _frontmatter(path)
        errors.extend(frontmatter_errors)
        name = metadata.get("name")
        description = metadata.get("description")
        if name != path.parent.name:
            errors.append(f"Skill name must match its directory: {path}")
        if not isinstance(description, str) or not description.strip():
            errors.append(f"Skill has no description: {path}")
        elif len(description) > 1024:
            errors.append(f"Skill description exceeds 1024 characters: {path}")
        if not body.strip():
            errors.append(f"Skill has no procedure/body: {path}")

    prompt_names: set[str] = set()
    for path in prompt_paths:
        metadata, body, frontmatter_errors = _frontmatter(path)
        errors.extend(frontmatter_errors)
        name = metadata.get("name")
        if not isinstance(name, str) or not name.strip():
            errors.append(f"Prompt has no name: {path}")
            continue
        prompt_names.add(name)
        if name != path.name.removesuffix(".prompt.md"):
            errors.append(f"Prompt name must match its file name: {path}")
        if not isinstance(metadata.get("description"), str):
            errors.append(f"Prompt has no description: {path}")
        if metadata.get("agent") != "SDLC Orchestrator":
            errors.append(f"Prompt must target SDLC Orchestrator: {path}")
        if "orchestrator" not in body.lower():
            errors.append(f"Prompt must delegate workflow decisions to the orchestrator: {path}")
    for name in sorted(EXPECTED_PROMPTS - prompt_names):
        errors.append(f"Required prompt is missing: {name}")

    return errors


def _artifact_by_id(state: dict[str, Any], artifact_id: str) -> dict[str, Any] | None:
    for artifact in state.get("artifacts", []):
        if isinstance(artifact, dict) and artifact.get("artifact_id") == artifact_id:
            return artifact
    return None


def _artifact(state: dict[str, Any], artifact_type: str) -> dict[str, Any] | None:
    active_artifacts = state.get("active_artifacts")
    if not isinstance(active_artifacts, dict):
        return None
    active = active_artifacts.get(artifact_type)
    if not isinstance(active, dict):
        return None
    artifact = _artifact_by_id(state, active.get("artifact_id", ""))
    if (
        artifact
        and artifact.get("type") == artifact_type
        and artifact.get("revision") == active.get("revision")
    ):
        return artifact
    return None


def _has_human_approval(
    state: dict[str, Any], gate: str, artifact_type: str
) -> bool:
    artifact = _artifact(state, artifact_type)
    if not artifact:
        return False
    revision = artifact.get("revision")
    for approval in state.get("approvals", []):
        if not isinstance(approval, dict):
            continue
        if (
            approval.get("gate") == gate
            and approval.get("decision") == "approved"
            and approval.get("approver_type") == "human"
            and approval.get("artifact_type") == artifact_type
            and approval.get("artifact_id") == artifact.get("artifact_id")
            and approval.get("artifact_revision") == revision
            and approval.get("approver")
            and approval.get("evidence_ref")
        ):
            return True
    return False


def _has_artifact(
    state: dict[str, Any], artifact_type: str, statuses: set[str]
) -> bool:
    artifact = _artifact(state, artifact_type)
    return bool(artifact and artifact.get("status") in statuses)


def _has_prerequisite_waiver(state: dict[str, Any], prerequisite: dict[str, Any]) -> bool:
    waiver_id = prerequisite.get("waiver_approval_id")
    if not waiver_id:
        return False
    return any(
        isinstance(approval, dict)
        and approval.get("approval_id") == waiver_id
        and approval.get("gate") == "prerequisite_waiver"
        and approval.get("decision") == "approved"
        and approval.get("approver_type") == "human"
        and approval.get("prerequisite_id") == prerequisite.get("prerequisite_id")
        and approval.get("approver")
        and approval.get("approved_at")
        and approval.get("rationale")
        and approval.get("scope")
        and approval.get("evidence_ref")
        for approval in state.get("approvals", [])
    )


def _open_blocking_findings(state: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        finding
        for finding in state.get("review_findings", [])
        if isinstance(finding, dict)
        and finding.get("status", "open") == "open"
        and finding.get("severity") in ("blocker", "high")
    ]


def _verification_gate_errors(state: dict[str, Any]) -> list[str]:
    artifact = _artifact(state, "verification")
    if not artifact:
        return ["PR preparation requires an active verification artifact"]
    status = artifact.get("status")
    evidence = state.get("verification_evidence", [])
    if not evidence:
        return ["Verification cannot pass without actual verification evidence"]
    if status == "passed":
        failed_required = [
            record
            for record in evidence
            if isinstance(record, dict)
            and record.get("required", True)
            and record.get("status") != "passed"
        ]
        if failed_required:
            return ["Passed verification artifact contains a required check that did not pass"]
        return []
    if status == "accepted_limitations":
        if not _has_human_approval(state, "verification_limitations", "verification"):
            return ["Accepted verification limitations require human approval of the exact verification revision"]
        return []
    return ["PR preparation requires passing verification or human-approved limitations"]


def validate_state(state: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(state, dict):
        return ["Workflow state must be a JSON object"]

    for field in REQUIRED_FIELDS:
        if field not in state:
            errors.append(f"Missing required state field: {field}")
    if errors:
        return errors

    if state.get("schema_version") != 1:
        errors.append("Unsupported schema_version; expected 1")
    run_id = state.get("run_id")
    if not isinstance(run_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", run_id):
        errors.append("run_id must be a non-empty path-safe identifier")
    if state.get("stage") not in STAGES:
        errors.append(f"Unknown stage: {state.get('stage')}")
    if state.get("status") not in STATUSES:
        errors.append(f"Unknown workflow status: {state.get('status')}")
    if state.get("status") == "complete" and state.get("stage") != "complete":
        errors.append("Workflow status complete requires stage complete")

    target = state.get("target")
    if not isinstance(target, dict):
        errors.append("target must be an object")
        target = {}
    if not _safe_relative_path(target.get("root")):
        errors.append("target.root must be a safe workspace-relative path")
    if target.get("repository_kind") not in REPOSITORY_KINDS:
        errors.append("target.repository_kind must be unknown, empty, existing, or monorepo")
    module_scope = target.get("module_scope")
    if not isinstance(module_scope, list) or not all(isinstance(p, str) for p in module_scope):
        errors.append("target.module_scope must be an array of workspace-relative paths")
    elif target.get("repository_kind") == "monorepo" and state.get("stage") not in ("discovery", "requirements") and not module_scope:
        errors.append("A monorepo must identify module_scope before architecture planning")

    stack = state.get("detected_stack")
    if not isinstance(stack, dict):
        errors.append("detected_stack must be an object")
        stack = {}
    stack_keys = (
        "languages",
        "frameworks",
        "build_systems",
        "package_managers",
        "dependencies",
        "source_directories",
        "test_directories",
        "conventions",
    )
    if any(stack.get(key) for key in stack_keys) and not stack.get("evidence"):
        errors.append("Detected stack values require repository evidence")
    if not isinstance(stack.get("evidence", []), list):
        errors.append("detected_stack.evidence must be an array")

    for field in ("story_sources", "requirement_ids", "tasks", "artifacts", "prerequisites", "approvals", "blockers", "source_conflicts", "review_findings", "verification_evidence", "rework_history"):
        if not isinstance(state.get(field), list):
            errors.append(f"{field} must be an array")

    requirement_ids = state.get("requirement_ids", [])
    if not isinstance(requirement_ids, list) or not all(isinstance(item, str) for item in requirement_ids):
        errors.append("requirement_ids must be an array of strings")
        requirement_ids = []
    elif len(requirement_ids) != len(set(requirement_ids)):
        errors.append("requirement_ids must be unique")

    source_ids: set[str] = set()
    for source in state.get("story_sources", []):
        if not isinstance(source, dict):
            errors.append("story_sources entries must be objects")
            continue
        source_id = source.get("source_id")
        if not isinstance(source_id, str) or not source_id:
            errors.append("Every story source requires source_id")
            continue
        if source_id in source_ids:
            errors.append(f"Duplicate source_id: {source_id}")
        source_ids.add(source_id)
        if source.get("source_type") not in ("direct", "local", "mcp"):
            errors.append(f"Invalid source_type for {source_id}")
        if source.get("status") not in SOURCE_STATUSES:
            errors.append(f"Invalid source status for {source_id}")
        if source.get("required") is True and source.get("status") != "complete":
            accepted_fallback = source.get("fallback_approval_id") and any(
                approval.get("approval_id") == source.get("fallback_approval_id")
                and approval.get("approver_type") == "human"
                and approval.get("decision") == "approved"
                for approval in state.get("approvals", [])
                if isinstance(approval, dict)
            )
            if not accepted_fallback and not any(
                blocker.get("source_id") == source_id and blocker.get("status") == "open"
                for blocker in state.get("blockers", [])
                if isinstance(blocker, dict)
            ):
                errors.append(f"Required incomplete source {source_id} needs an open blocker or human-approved fallback")

    blockers_by_id: dict[str, dict[str, Any]] = {}
    for blocker in state.get("blockers", []):
        if not isinstance(blocker, dict):
            errors.append("blockers entries must be objects")
            continue
        blocker_id = blocker.get("blocker_id")
        if not isinstance(blocker_id, str) or not blocker_id:
            errors.append("Every blocker requires blocker_id")
            continue
        if blocker.get("status") not in ("open", "resolved"):
            errors.append(f"Invalid blocker status: {blocker.get('status')}")
        blockers_by_id[blocker_id] = blocker

    for conflict in state.get("source_conflicts", []):
        if not isinstance(conflict, dict):
            errors.append("source_conflicts entries must be objects")
            continue
        conflict_status = conflict.get("status")
        blocker = blockers_by_id.get(conflict.get("blocker_id"))
        if conflict_status == "open":
            if not blocker or blocker.get("status") != "open":
                errors.append("Every open source conflict must reference a corresponding open blocker")
        elif conflict_status == "resolved":
            if not blocker or blocker.get("status") != "resolved":
                errors.append("Every resolved source conflict must reference a resolved blocker")
            if not conflict.get("resolution_evidence"):
                errors.append("Every resolved source conflict requires resolution_evidence")
        else:
            errors.append(f"Invalid source conflict status: {conflict_status}")

    open_blockers = [
        blocker
        for blocker in state.get("blockers", [])
        if isinstance(blocker, dict) and blocker.get("status") == "open"
    ]
    if state.get("status") == "blocked" and not open_blockers:
        errors.append("Blocked workflow status requires an open blocker")
    if state.get("status") == "active" and open_blockers:
        errors.append("Active workflow cannot contain open blockers")

    active_artifacts = state.get("active_artifacts")
    if not isinstance(active_artifacts, dict):
        errors.append("active_artifacts must map artifact types to active IDs and revisions")
        active_artifacts = {}
    artifact_ids: set[str] = set()
    artifact_types: set[str] = set()
    for artifact in state.get("artifacts", []):
        if not isinstance(artifact, dict):
            errors.append("artifacts entries must be objects")
            continue
        artifact_id = artifact.get("artifact_id")
        if not isinstance(artifact_id, str) or not artifact_id:
            errors.append("Every artifact requires artifact_id")
        elif artifact_id in artifact_ids:
            errors.append(f"Duplicate artifact_id: {artifact_id}")
        else:
            artifact_ids.add(artifact_id)
        if not _safe_relative_path(artifact.get("path")):
            errors.append(f"Artifact path must be workspace-relative: {artifact.get('path')}")
        elif isinstance(run_id, str) and not artifact["path"].startswith(f".sdlc/{run_id}/"):
            errors.append(f"Workflow artifact must be inside this run directory: {artifact['path']}")
        if not isinstance(artifact.get("revision"), str) or not artifact.get("revision"):
            errors.append(f"Artifact {artifact_id or '<unknown>'} requires a revision")
        if not isinstance(artifact.get("type"), str) or not artifact.get("type"):
            errors.append(f"Artifact {artifact_id or '<unknown>'} requires a type")
        else:
            artifact_types.add(artifact["type"])
        linked_requirements = artifact.get("requirement_ids", [])
        if not isinstance(linked_requirements, list) or not set(linked_requirements).issubset(set(requirement_ids)):
            errors.append(f"Artifact {artifact_id or '<unknown>'} references unknown requirements")

    for artifact_type in artifact_types:
        active = active_artifacts.get(artifact_type)
        if not isinstance(active, dict):
            errors.append(f"Artifact type {artifact_type} requires an active artifact ID and revision")
            continue
        active_artifact = _artifact_by_id(state, active.get("artifact_id", ""))
        if (
            not active_artifact
            or active_artifact.get("type") != artifact_type
            or active_artifact.get("revision") != active.get("revision")
        ):
            errors.append(f"Active artifact reference for {artifact_type} is stale or invalid")
    for artifact_type in active_artifacts:
        if artifact_type not in artifact_types:
            errors.append(f"Active artifact reference has no matching artifact: {artifact_type}")

    task_ids: set[str] = set()
    task_order: dict[str, int] = {}
    task_dependencies: dict[str, list[str]] = {}
    for index, task in enumerate(state.get("tasks", [])):
        if not isinstance(task, dict):
            errors.append("tasks entries must be objects")
            continue
        task_id = task.get("task_id")
        if not isinstance(task_id, str) or not task_id:
            errors.append("Every task requires task_id")
            continue
        if task_id in task_ids:
            errors.append(f"Duplicate task_id: {task_id}")
        task_ids.add(task_id)
        task_order[task_id] = index
        task_requirements = task.get("requirement_ids", [])
        if (
            not isinstance(task_requirements, list)
            or not all(isinstance(item, str) for item in task_requirements)
            or not set(task_requirements).issubset(set(requirement_ids))
        ):
            errors.append(f"Task {task_id} references unknown requirements")
        dependencies = task.get("depends_on", [])
        if not isinstance(dependencies, list) or not all(isinstance(item, str) for item in dependencies):
            errors.append(f"Task {task_id} depends_on must be an array of task IDs")
            dependencies = []
        task_dependencies[task_id] = dependencies

    for task_id, dependencies in task_dependencies.items():
        for dependency in dependencies:
            if dependency not in task_ids:
                errors.append(f"Task {task_id} depends on unknown task {dependency}")
            elif task_order[dependency] >= task_order[task_id]:
                errors.append(f"Task {task_id} is not ordered after dependency {dependency}")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit_task(task_id: str) -> None:
        if task_id in visiting:
            errors.append(f"Task dependency cycle includes {task_id}")
            return
        if task_id in visited:
            return
        visiting.add(task_id)
        for dependency in task_dependencies.get(task_id, []):
            if dependency in task_ids:
                visit_task(dependency)
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in task_ids:
        visit_task(task_id)

    for approval in state.get("approvals", []):
        if not isinstance(approval, dict):
            errors.append("approvals entries must be objects")
            continue
        if approval.get("decision") == "approved":
            if approval.get("approver_type") != "human":
                errors.append("Only a human-authored approval can have decision=approved")
            if not approval.get("approval_id"):
                errors.append("Approved records require approval_id")
            if not approval.get("approver") or not approval.get("approved_at") or not approval.get("evidence_ref"):
                errors.append(f"Approval {approval.get('approval_id', '<unknown>')} is missing human evidence fields")
            if approval.get("gate") == "prerequisite_waiver":
                prerequisite = next(
                    (
                        item
                        for item in state.get("prerequisites", [])
                        if isinstance(item, dict)
                        and item.get("prerequisite_id") == approval.get("prerequisite_id")
                    ),
                    None,
                )
                if not prerequisite or prerequisite.get("status") != "waived":
                    errors.append("Prerequisite waiver approval must reference a waived prerequisite")
                if not approval.get("rationale") or not approval.get("scope"):
                    errors.append("Prerequisite waiver approval requires rationale and scope")
                continue
            artifact = _artifact_by_id(state, approval.get("artifact_id", ""))
            if (
                not artifact
                or artifact.get("type") != approval.get("artifact_type")
                or artifact.get("revision") != approval.get("artifact_revision")
            ):
                errors.append(f"Approval {approval.get('approval_id', '<unknown>')} must reference the exact artifact ID and revision")

    for prerequisite in state.get("prerequisites", []):
        if not isinstance(prerequisite, dict):
            errors.append("prerequisites entries must be objects")
            continue
        if not prerequisite.get("prerequisite_id"):
            errors.append("Every prerequisite requires prerequisite_id")
        if prerequisite.get("status") not in ("pending", "met", "blocked", "waived"):
            errors.append(f"Invalid prerequisite status: {prerequisite.get('status')}")
        elif prerequisite.get("status") == "waived" and not _has_prerequisite_waiver(state, prerequisite):
            errors.append(f"Waived prerequisite {prerequisite.get('prerequisite_id', '<unknown>')} requires human approval, rationale, scope, and evidence")

    for finding in state.get("review_findings", []):
        if not isinstance(finding, dict):
            errors.append("review_findings entries must be objects")
            continue
        if not finding.get("finding_id"):
            errors.append("Every review finding requires finding_id")
        if finding.get("severity") not in ("blocker", "high", "medium", "low"):
            errors.append(f"Invalid review finding severity: {finding.get('severity')}")
        if finding.get("status") not in ("open", "resolved", "accepted", "rejected"):
            errors.append(f"Invalid review finding status: {finding.get('status')}")
    for evidence in state.get("verification_evidence", []):
        if not isinstance(evidence, dict):
            errors.append("verification_evidence entries must be objects")
            continue
        if evidence.get("status") not in ("passed", "failed", "blocked", "not_run", "accepted_limitations"):
            errors.append(f"Invalid verification status: {evidence.get('status')}")
        if not evidence.get("check_id") or not evidence.get("command"):
            errors.append("Verification evidence requires check_id and the actual command/procedure")
        if evidence.get("status") in ("passed", "failed"):
            if not isinstance(evidence.get("exit_status"), int):
                errors.append(f"Executed check {evidence.get('check_id', '<unknown>')} requires an exit_status")
            if not evidence.get("evidence_ref"):
                errors.append(f"Executed check {evidence.get('check_id', '<unknown>')} requires an evidence_ref")

    for rework in state.get("rework_history", []):
        if not isinstance(rework, dict):
            errors.append("rework_history entries must be objects")
            continue
        if not rework.get("rework_id") or not rework.get("cause"):
            errors.append("Rework entries require rework_id and cause")
        if rework.get("from_stage") not in STAGES or rework.get("to_stage") not in STAGES:
            errors.append(f"Rework {rework.get('rework_id', '<unknown>')} requires valid from_stage and to_stage")
        if rework.get("from_stage") == rework.get("to_stage"):
            errors.append(f"Rework {rework.get('rework_id', '<unknown>')} must route to a different stage")
        if not isinstance(rework.get("affected_artifact_ids"), list):
            errors.append(f"Rework {rework.get('rework_id', '<unknown>')} requires affected_artifact_ids")
        if rework.get("resolution_status") not in ("open", "resolved"):
            errors.append(f"Rework {rework.get('rework_id', '<unknown>')} requires resolution_status")
        if not rework.get("evidence_ref"):
            errors.append(f"Rework {rework.get('rework_id', '<unknown>')} requires evidence_ref")

    errors.extend(_validate_stage_evidence(state))
    return errors


def _validate_stage_evidence(state: dict[str, Any]) -> list[str]:
    stage = state.get("stage")
    if stage not in STAGES:
        return []
    errors: list[str] = []
    stage_index = STAGES.index(stage)

    def require_artifact(artifact_type: str, statuses: set[str]) -> None:
        if not _has_artifact(state, artifact_type, statuses):
            errors.append(f"Stage {stage} requires {artifact_type} artifact with status {sorted(statuses)}")

    def require_approval(gate: str, artifact_type: str) -> None:
        if not _has_human_approval(state, gate, artifact_type):
            errors.append(f"Stage {stage} requires human approval for {artifact_type}")

    if stage_index >= STAGES.index("architecture"):
        require_artifact("requirements", {"approved"})
        require_approval("requirements", "requirements")
    if stage_index >= STAGES.index("structure_planning"):
        require_artifact("architecture", {"approved"})
        require_approval("architecture", "architecture")
    if stage_index >= STAGES.index("design_review"):
        require_artifact("structure_plan", {"proposed", "approved"})
    if stage_index >= STAGES.index("planning"):
        require_artifact("structure_plan", {"approved"})
        require_approval("structure_plan", "structure_plan")
        require_artifact("design_review", {"accepted"})
    if stage_index >= STAGES.index("implementation"):
        require_artifact("implementation_plan", {"approved"})
        require_approval("implementation_plan", "implementation_plan")
    if stage_index >= STAGES.index("review"):
        require_artifact("implementation_report", {"complete"})
    if stage_index >= STAGES.index("planning") and _open_blocking_findings(state):
        errors.append("Planning and later stages are blocked by unresolved blocker/high findings")
    if stage_index >= STAGES.index("verification"):
        require_artifact("code_review", {"accepted"})
    if stage_index >= STAGES.index("pr_preparation"):
        errors.extend(_verification_gate_errors(state))
    if stage == "complete":
        require_artifact("pr_summary", {"ready"})
        require_approval("final_acceptance", "pr_summary")
    return errors


def validate_transition(state: dict[str, Any], next_stage: str) -> list[str]:
    errors = validate_state(state)
    current_stage = state.get("stage")
    if next_stage not in STAGES:
        return errors + [f"Unknown next stage: {next_stage}"]
    if next_stage not in TRANSITIONS.get(current_stage, set()):
        return errors + [f"Illegal stage transition: {current_stage} -> {next_stage}"]
    if errors:
        return errors
    if state.get("status") in ("blocked", "abandoned", "complete"):
        errors.append(f"Cannot advance a workflow with status {state.get('status')}")
    if any(p.get("status") in ("pending", "blocked") for p in state.get("prerequisites", []) if isinstance(p, dict)):
        errors.append("All prerequisites must be met or explicitly waived before advancing")
    if any(b.get("status") == "open" for b in state.get("blockers", []) if isinstance(b, dict)):
        errors.append("Open blockers must be resolved before advancing")

    current = current_stage
    if current == "discovery":
        target = state.get("target", {})
        if target.get("repository_kind") == "unknown":
            errors.append("Discovery must classify the target before requirements")
        if not state.get("story_sources"):
            errors.append("Requirements cannot start without a story source")
    if current == "requirements":
        if not _has_artifact(state, "requirements", {"approved"}):
            errors.append("Architecture requires an approved requirements artifact")
        if not _has_human_approval(state, "requirements", "requirements"):
            errors.append("Architecture requires human approval of the exact requirements revision")
    elif current == "architecture":
        if not _has_artifact(state, "architecture", {"approved"}):
            errors.append("Structure planning requires an approved architecture artifact")
        if not _has_human_approval(state, "architecture", "architecture"):
            errors.append("Structure planning requires human approval of the architecture revision")
    elif current == "structure_planning":
        if not _has_artifact(state, "structure_plan", {"proposed", "approved"}):
            errors.append("Design review requires a proposed structure plan")
    elif current == "design_review":
        if not _has_artifact(state, "design_review", {"accepted"}):
            errors.append("Planning requires an accepted design review")
        if _open_blocking_findings(state):
            errors.append("Planning is blocked by unresolved blocker/high design findings")
        if not _has_artifact(state, "structure_plan", {"approved"}):
            errors.append("Planning requires an approved structure plan")
        if not _has_human_approval(state, "structure_plan", "structure_plan"):
            errors.append("Planning requires human approval of the exact structure plan")
    elif current == "planning":
        if not _has_artifact(state, "implementation_plan", {"approved"}):
            errors.append("Implementation requires an approved implementation plan")
        if not _has_human_approval(state, "implementation_plan", "implementation_plan"):
            errors.append("Implementation requires human approval of the exact plan revision")
    elif current == "implementation":
        if not _has_artifact(state, "implementation_report", {"complete"}):
            errors.append("Review requires a completed implementation report")
    elif current == "review":
        if not _has_artifact(state, "code_review", {"accepted"}):
            errors.append("Verification requires an accepted code review")
        if _open_blocking_findings(state):
            errors.append("Verification is blocked by unresolved high-severity review findings")
    elif current == "verification":
        errors.extend(_verification_gate_errors(state))
    elif current == "pr_preparation":
        if not _has_artifact(state, "pr_summary", {"ready"}):
            errors.append("Completion requires PR materials marked ready")
        if not _has_human_approval(state, "final_acceptance", "pr_summary"):
            errors.append("Completion requires human final acceptance of the exact PR summary")
    return errors


def load_state(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        with path.open(encoding="utf-8") as state_file:
            state = json.load(state_file)
    except (OSError, json.JSONDecodeError) as error:
        return None, [f"Cannot load workflow state {path}: {error}"]
    if not isinstance(state, dict):
        return None, ["Workflow state root must be a JSON object"]
    return state, []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--state", type=Path, help="Optional workflow-state.json to validate")
    parser.add_argument("--next-stage", help="Validate a proposed transition from the saved stage")
    args = parser.parse_args(argv)

    errors = validate_customizations(args.root.resolve())
    if args.state:
        state, state_errors = load_state(args.state)
        errors.extend(state_errors)
        if state is not None:
            if args.next_stage:
                errors.extend(validate_transition(state, args.next_stage))
            else:
                errors.extend(validate_state(state))
    elif args.next_stage:
        errors.append("--next-stage requires --state")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("PASS: customizations and requested workflow state checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())