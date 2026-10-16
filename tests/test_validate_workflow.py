import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate_workflow


FIXTURES = ROOT / "tests" / "fixtures" / "workflow-states"


def read_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def add_artifact(state: dict, artifact_type: str, status: str, revision: str = "rev-1") -> None:
    artifact_id = f"{artifact_type}-artifact-{len(state['artifacts']) + 1}"
    state["artifacts"].append(
        {
            "artifact_id": artifact_id,
            "type": artifact_type,
            "path": f".sdlc/{state['run_id']}/{artifact_type}.md",
            "revision": revision,
            "status": status,
            "requirement_ids": list(state["requirement_ids"]),
        }
    )
    state.setdefault("active_artifacts", {})[artifact_type] = {
        "artifact_id": artifact_id,
        "revision": revision,
    }


def add_approval(state: dict, gate: str, artifact_type: str, revision: str = "rev-1") -> None:
    active = state["active_artifacts"][artifact_type]
    state["approvals"].append(
        {
            "approval_id": f"{gate}-approval",
            "gate": gate,
            "decision": "approved",
            "approver_type": "human",
            "approver": "reviewer@example.invalid",
            "approved_at": "2026-10-16T00:00:00Z",
            "artifact_type": artifact_type,
            "artifact_id": active["artifact_id"],
            "artifact_revision": revision,
            "scope": "fixture scope",
            "evidence_ref": "review-record-1",
        }
    )


def add_prerequisite_waiver(state: dict, prerequisite_id: str) -> None:
    approval_id = f"waiver-{prerequisite_id}"
    state["prerequisites"] = [
        {
            "prerequisite_id": prerequisite_id,
            "status": "waived",
            "waiver_approval_id": approval_id,
        }
    ]
    state["approvals"].append(
        {
            "approval_id": approval_id,
            "gate": "prerequisite_waiver",
            "decision": "approved",
            "approver_type": "human",
            "approver": "reviewer@example.invalid",
            "approved_at": "2026-10-16T00:00:00Z",
            "prerequisite_id": prerequisite_id,
            "rationale": "The condition is not applicable to this run.",
            "scope": "This run only",
            "evidence_ref": "waiver-record-1",
        }
    )


def add_prerequisite_waiver(state: dict, prerequisite_id: str) -> None:
    approval_id = f"waiver-{prerequisite_id}"
    state["prerequisites"] = [
        {
            "prerequisite_id": prerequisite_id,
            "status": "waived",
            "waiver_approval_id": approval_id,
        }
    ]
    state["approvals"].append(
        {
            "approval_id": approval_id,
            "gate": "prerequisite_waiver",
            "decision": "approved",
            "approver_type": "human",
            "approver": "reviewer@example.invalid",
            "approved_at": "2026-10-16T00:00:00Z",
            "prerequisite_id": prerequisite_id,
            "rationale": "The condition does not apply to this run.",
            "scope": "This run only",
            "evidence_ref": "waiver-record-1",
        }
    )


def add_prior_stage_evidence(state: dict, through: str) -> None:
    stages = [
        ("requirements", "approved", "requirements"),
        ("architecture", "approved", "architecture"),
        ("structure_plan", "approved", "structure_plan"),
        ("design_review", "accepted", None),
        ("implementation_plan", "approved", "implementation_plan"),
        ("implementation_report", "complete", None),
        ("code_review", "accepted", None),
    ]
    for artifact_type, status, gate in stages:
        add_artifact(state, artifact_type, status)
        if gate:
            add_approval(state, gate, artifact_type)
        if artifact_type == through:
            return


class CustomizationTests(unittest.TestCase):
    def test_agent_prompt_and_skill_metadata(self) -> None:
        self.assertEqual(validate_workflow.validate_customizations(ROOT), [])

    def copied_customizations(self, temp_root: Path) -> Path:
        shutil.copytree(ROOT / ".github", temp_root / ".github")
        return temp_root

    def test_unverified_mcp_tool_on_source_retriever_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = self.copied_customizations(Path(temporary_directory))
            path = root / ".github" / "agents" / "source-retriever.agent.md"
            content = path.read_text(encoding="utf-8").replace(
                "tools: ['read', 'search']",
                "tools: ['read', 'search', 'unverified-mcp/write']",
            )
            path.write_text(content, encoding="utf-8")
            self.assertTrue(
                any(
                    "source-retriever may only enable local read/search" in error
                    for error in validate_workflow.validate_customizations(root)
                )
            )

    def test_missing_skill_reference_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = self.copied_customizations(Path(temporary_directory))
            path = root / ".github" / "agents" / "project-structure-planner.agent.md"
            content = path.read_text(encoding="utf-8").replace(
                "../skills/project-structure-planning/SKILL.md",
                "../skills/missing-skill/SKILL.md",
            )
            path.write_text(content, encoding="utf-8")
            self.assertTrue(
                any(
                    "must reference skill project-structure-planning" in error
                    or "Invalid skill reference" in error
                    for error in validate_workflow.validate_customizations(root)
                )
            )

    def test_read_only_specialists_reject_edit_tool(self) -> None:
        for agent_name in sorted(validate_workflow.READ_ONLY_AGENT_NAMES):
            with self.subTest(agent=agent_name), tempfile.TemporaryDirectory() as temporary_directory:
                root = self.copied_customizations(Path(temporary_directory))
                path = root / ".github" / "agents" / f"{agent_name}.agent.md"
                content = path.read_text(encoding="utf-8")
                content = content.replace("tools: ['read', 'search']", "tools: ['read', 'search', 'edit']")
                content = content.replace("tools: ['read', 'search', 'execute']", "tools: ['read', 'search', 'execute', 'edit']")
                path.write_text(content, encoding="utf-8")
                self.assertTrue(
                    any(
                        f"Read-only agent has edit tool: {agent_name}" in error
                        for error in validate_workflow.validate_customizations(root)
                    )
                )


class RepositoryStateTests(unittest.TestCase):
    def test_empty_existing_and_monorepo_fixtures_are_valid_without_fixed_stack(self) -> None:
        for fixture in ("empty-target.json", "existing-target.json", "monorepo-target.json"):
            with self.subTest(fixture=fixture):
                self.assertEqual(validate_workflow.validate_state(read_fixture(fixture)), [])

    def test_stack_values_require_evidence(self) -> None:
        state = read_fixture("existing-target.json")
        state["detected_stack"]["evidence"] = []
        self.assertTrue(any("require repository evidence" in error for error in validate_workflow.validate_state(state)))

    def test_monorepo_must_select_module_before_architecture(self) -> None:
        state = read_fixture("monorepo-target.json")
        state["stage"] = "architecture"
        state["target"]["module_scope"] = []
        self.assertTrue(any("module_scope" in error for error in validate_workflow.validate_state(state)))

    def test_task_traceability_rejects_unknown_requirement(self) -> None:
        state = read_fixture("existing-target.json")
        state["requirement_ids"] = ["REQ-001"]
        state["tasks"] = [{"task_id": "TASK-001", "requirement_ids": ["REQ-404"]}]
        self.assertTrue(any("references unknown requirements" in error for error in validate_workflow.validate_state(state)))

    def test_task_ids_must_be_unique(self) -> None:
        state = read_fixture("existing-target.json")
        state["tasks"] = [
            {"task_id": "TASK-1", "requirement_ids": [], "depends_on": []},
            {"task_id": "TASK-1", "requirement_ids": [], "depends_on": []},
        ]
        self.assertTrue(any("Duplicate task_id" in error for error in validate_workflow.validate_state(state)))

    def test_task_dependency_must_reference_a_task(self) -> None:
        state = read_fixture("existing-target.json")
        state["tasks"] = [{"task_id": "TASK-1", "requirement_ids": [], "depends_on": ["TASK-MISSING"]}]
        self.assertTrue(any("depends on unknown task" in error for error in validate_workflow.validate_state(state)))

    def test_task_dependency_cycle_is_rejected(self) -> None:
        state = read_fixture("existing-target.json")
        state["tasks"] = [
            {"task_id": "TASK-1", "requirement_ids": [], "depends_on": ["TASK-2"]},
            {"task_id": "TASK-2", "requirement_ids": [], "depends_on": ["TASK-1"]},
        ]
        self.assertTrue(any("dependency cycle" in error for error in validate_workflow.validate_state(state)))

    def test_malformed_requirement_ids_do_not_crash_validation(self) -> None:
        state = read_fixture("existing-target.json")
        state["requirement_ids"] = [{"unexpected": "object"}]
        self.assertTrue(any("array of strings" in error for error in validate_workflow.validate_state(state)))


class GateTests(unittest.TestCase):
    def requirements_ready_state(self) -> dict:
        state = read_fixture("existing-target.json")
        state["stage"] = "requirements"
        state["requirement_ids"] = ["REQ-001"]
        add_artifact(state, "requirements", "approved")
        return state

    def test_transition_requires_human_approval_for_exact_revision(self) -> None:
        state = self.requirements_ready_state()
        self.assertTrue(any("human approval" in error for error in validate_workflow.validate_transition(state, "architecture")))
        add_approval(state, "requirements", "requirements")
        self.assertEqual(validate_workflow.validate_transition(state, "architecture"), [])

    def test_agent_claim_cannot_approve(self) -> None:
        state = self.requirements_ready_state()
        approval = {
            "approval_id": "agent-approval",
            "gate": "requirements",
            "decision": "approved",
            "approver_type": "agent",
            "approver": "requirements-analyst",
            "approved_at": "2026-10-16T00:00:00Z",
            "artifact_type": "requirements",
            "artifact_revision": "rev-1",
            "scope": "all",
            "evidence_ref": "chat",
        }
        state["approvals"].append(approval)
        self.assertTrue(any("Only a human-authored" in error for error in validate_workflow.validate_state(state)))

    def test_stale_approval_revision_is_rejected(self) -> None:
        state = self.requirements_ready_state()
        add_approval(state, "requirements", "requirements", revision="old-revision")
        self.assertTrue(any("exact artifact ID and revision" in error for error in validate_workflow.validate_state(state)))

    def test_newer_active_draft_invalidates_older_approval(self) -> None:
        state = self.requirements_ready_state()
        add_approval(state, "requirements", "requirements")
        add_artifact(state, "requirements", "draft", revision="rev-2")
        self.assertTrue(
            any(
                "active artifact revision" in error or "approved" in error
                for error in validate_workflow.validate_transition(state, "architecture")
            )
        )

    def test_waived_prerequisite_requires_human_approval(self) -> None:
        state = self.requirements_ready_state()
        add_approval(state, "requirements", "requirements")
        state["prerequisites"] = [{"prerequisite_id": "P1", "status": "waived"}]
        self.assertTrue(
            any("Waived prerequisite" in error for error in validate_workflow.validate_transition(state, "architecture"))
        )

    def test_valid_human_waiver_allows_transition(self) -> None:
        state = self.requirements_ready_state()
        add_approval(state, "requirements", "requirements")
        add_prerequisite_waiver(state, "P1")
        self.assertEqual(validate_workflow.validate_transition(state, "architecture"), [])

    def test_waiver_without_rationale_is_rejected(self) -> None:
        state = self.requirements_ready_state()
        add_approval(state, "requirements", "requirements")
        add_prerequisite_waiver(state, "P1")
        state["approvals"][-1].pop("rationale")
        self.assertTrue(any("rationale, scope, and evidence" in error for error in validate_workflow.validate_state(state)))

    def test_illegal_transition_is_rejected(self) -> None:
        state = read_fixture("empty-target.json")
        self.assertTrue(any("Illegal stage transition" in error for error in validate_workflow.validate_transition(state, "implementation")))

    def test_required_partial_mcp_source_requires_blocker(self) -> None:
        for source_status in ("not_configured", "disconnected", "partial"):
            with self.subTest(source_status=source_status):
                state = read_fixture("existing-target.json")
                state["story_sources"][0].update(
                    {"source_type": "mcp", "status": source_status, "required": True}
                )
                self.assertTrue(
                    any(
                        "needs an open blocker" in error
                        for error in validate_workflow.validate_state(state)
                    )
                )

    def test_conflicting_sources_require_blocker(self) -> None:
        state = read_fixture("existing-target.json")
        state["source_conflicts"] = [{"conflict_id": "CONFLICT-1", "status": "open", "blocker_id": "BLOCK-1"}]
        self.assertTrue(any("corresponding open blocker" in error for error in validate_workflow.validate_state(state)))

    def test_open_source_conflict_cannot_reference_resolved_blocker(self) -> None:
        state = read_fixture("existing-target.json")
        state["source_conflicts"] = [{"conflict_id": "CONFLICT-1", "status": "open", "blocker_id": "BLOCK-1"}]
        state["blockers"] = [{"blocker_id": "BLOCK-1", "reason": "conflict", "status": "resolved"}]
        self.assertTrue(any("corresponding open blocker" in error for error in validate_workflow.validate_state(state)))

    def test_resolved_source_conflict_requires_resolution_evidence(self) -> None:
        state = read_fixture("existing-target.json")
        state["source_conflicts"] = [{"conflict_id": "CONFLICT-1", "status": "resolved", "blocker_id": "BLOCK-1"}]
        state["blockers"] = [{"blocker_id": "BLOCK-1", "reason": "conflict", "status": "resolved"}]
        self.assertTrue(any("resolution_evidence" in error for error in validate_workflow.validate_state(state)))

    def test_resolved_source_conflict_with_resolved_blocker_and_evidence_is_valid(self) -> None:
        state = read_fixture("existing-target.json")
        state["source_conflicts"] = [{"conflict_id": "CONFLICT-1", "status": "resolved", "blocker_id": "BLOCK-1", "resolution_evidence": "decision-record-1"}]
        state["blockers"] = [{"blocker_id": "BLOCK-1", "reason": "conflict", "status": "resolved"}]
        self.assertEqual(validate_workflow.validate_state(state), [])

    def test_open_blocker_conflict_pair_is_valid(self) -> None:
        state = read_fixture("existing-target.json")
        state["status"] = "blocked"
        state["source_conflicts"] = [{"conflict_id": "CONFLICT-1", "status": "open", "blocker_id": "BLOCK-1"}]
        state["blockers"] = [{"blocker_id": "BLOCK-1", "source_id": "story-local-1", "reason": "conflicting data", "status": "open"}]
        self.assertEqual(validate_workflow.validate_state(state), [])

    def test_open_blocker_prevents_transition(self) -> None:
        state = read_fixture("existing-target.json")
        state["status"] = "blocked"
        state["blockers"] = [{"blocker_id": "BLOCK-1", "reason": "missing decision", "status": "open"}]
        self.assertTrue(any("Open blockers" in error or "status blocked" in error for error in validate_workflow.validate_transition(state, "requirements")))

    def test_unresolved_high_review_finding_blocks_verification(self) -> None:
        state = read_fixture("existing-target.json")
        state["stage"] = "review"
        add_prior_stage_evidence(state, "implementation_report")
        state["review_findings"] = [{"finding_id": "CR-1", "severity": "high", "status": "open"}]
        self.assertTrue(any("unresolved blocker/high" in error for error in validate_workflow.validate_transition(state, "verification")))

    def test_unresolved_design_blocker_blocks_planning(self) -> None:
        state = read_fixture("existing-target.json")
        state["stage"] = "design_review"
        add_prior_stage_evidence(state, "structure_plan")
        add_artifact(state, "design_review", "accepted")
        state["review_findings"] = [{"finding_id": "DR-1", "severity": "blocker", "status": "open"}]
        self.assertTrue(any("unresolved blocker/high" in error for error in validate_workflow.validate_transition(state, "planning")))

    def test_resolved_design_blocker_allows_planning(self) -> None:
        state = read_fixture("existing-target.json")
        state["stage"] = "design_review"
        add_prior_stage_evidence(state, "structure_plan")
        add_artifact(state, "design_review", "accepted")
        state["review_findings"] = [{"finding_id": "DR-1", "severity": "blocker", "status": "resolved", "disposition_evidence": "resolution-1"}]
        self.assertEqual(validate_workflow.validate_transition(state, "planning"), [])

    def test_failed_verification_blocks_pr_preparation(self) -> None:
        state = read_fixture("existing-target.json")
        state["stage"] = "verification"
        add_prior_stage_evidence(state, "code_review")
        add_artifact(state, "verification", "failed")
        state["verification_evidence"] = [
            {
                "check_id": "TEST-1",
                "command": "test-command --suite focused",
                "status": "failed",
                "exit_status": 1,
                "evidence_ref": "test-output-1",
            }
        ]
        self.assertTrue(any("passing verification or human-approved limitations" in error for error in validate_workflow.validate_transition(state, "pr_preparation")))

    def verification_ready_state(self, artifact_status: str = "passed") -> dict:
        state = read_fixture("existing-target.json")
        state["stage"] = "verification"
        add_prior_stage_evidence(state, "code_review")
        add_artifact(state, "verification", artifact_status)
        return state

    def test_passed_verification_requires_actual_records(self) -> None:
        state = self.verification_ready_state()
        self.assertTrue(
            any("actual verification evidence" in error for error in validate_workflow.validate_transition(state, "pr_preparation"))
        )

    def test_passed_verification_requires_each_required_check_to_pass(self) -> None:
        state = self.verification_ready_state()
        state["verification_evidence"] = [
            {"check_id": "TEST-1", "command": "test command", "status": "failed", "required": True, "exit_status": 1, "evidence_ref": "test-output"}
        ]
        self.assertTrue(
            any("required check that did not pass" in error for error in validate_workflow.validate_transition(state, "pr_preparation"))
        )

    def test_passed_verification_with_evidence_allows_pr_preparation(self) -> None:
        state = self.verification_ready_state()
        state["verification_evidence"] = [
            {"check_id": "TEST-1", "command": "test command", "status": "passed", "required": True, "exit_status": 0, "evidence_ref": "test-output"}
        ]
        self.assertEqual(validate_workflow.validate_transition(state, "pr_preparation"), [])

    def test_accepted_verification_limitations_require_human_approval(self) -> None:
        state = self.verification_ready_state("accepted_limitations")
        state["verification_evidence"] = [
            {"check_id": "TEST-1", "command": "test command", "status": "not_run", "required": True, "evidence_ref": "limitation-record"}
        ]
        self.assertTrue(
            any("human approval" in error for error in validate_workflow.validate_transition(state, "pr_preparation"))
        )
        add_approval(state, "verification_limitations", "verification")
        self.assertEqual(validate_workflow.validate_transition(state, "pr_preparation"), [])

    def test_artifacts_must_remain_inside_run_directory(self) -> None:
        state = self.requirements_ready_state()
        state["artifacts"][0]["path"] = "src/application.py"
        self.assertTrue(any("inside this run directory" in error for error in validate_workflow.validate_state(state)))

    def test_later_stage_cannot_skip_earlier_approvals(self) -> None:
        state = read_fixture("existing-target.json")
        state["stage"] = "implementation"
        add_artifact(state, "implementation_plan", "approved")
        add_approval(state, "implementation_plan", "implementation_plan")
        self.assertTrue(any("requirements" in error for error in validate_workflow.validate_state(state)))
        self.assertTrue(any("architecture" in error for error in validate_workflow.validate_state(state)))

    def test_rework_records_preserve_cause_route_and_evidence(self) -> None:
        state = read_fixture("existing-target.json")
        state["rework_history"] = [
            {
                "rework_id": "RW-1",
                "cause": "verification failed",
                "from_stage": "verification",
                "to_stage": "implementation",
                "affected_artifact_ids": ["verification-1"],
                "resolution_status": "open",
                "evidence_ref": "test-output-1",
            }
        ]
        self.assertEqual(validate_workflow.validate_state(state), [])
        state["rework_history"][0].pop("evidence_ref")
        self.assertTrue(any("requires evidence_ref" in error for error in validate_workflow.validate_state(state)))

    def test_executed_verification_requires_command_result_and_evidence(self) -> None:
        state = read_fixture("existing-target.json")
        state["verification_evidence"] = [{"check_id": "TEST-1", "status": "passed"}]
        errors = validate_workflow.validate_state(state)
        self.assertTrue(any("actual command/procedure" in error for error in errors))
        self.assertTrue(any("exit_status" in error for error in errors))


if __name__ == "__main__":
    unittest.main()