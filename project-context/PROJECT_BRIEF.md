# Agentic SDLC Pipeline — Project Brief

## 1. Project Objective

Build a reusable Agentic Software Development Life Cycle (SDLC) pipeline driven primarily through GitHub Copilot Chat and Agent Mode.

The pipeline must help developers move from a User Story to a reviewed, tested, pull-request-ready software change.

## 2. Generality Requirement

This is a generic workflow, not an application dedicated to a particular business domain, customer, or User Story.

It must support:
- Different User Stories, including new features, bug fixes, enhancements, and refactoring.
- Empty repositories that need an initial application structure.
- Existing repositories with code, tests, architecture, dependencies, and established conventions.
- Different programming languages, frameworks, build systems, and test tools.
- User Stories supplied through documents or other supported input sources.

The workflow must discover project-specific details rather than assume them.

## 3. Required SDLC Stages

1. Requirements discovery and clarification.
2. Architecture design.
3. Design review and agreed decisions.
4. Dependency-ordered implementation planning.
5. Human-approved implementation.
6. Structured code review.
7. Code and output verification.
8. Pull request preparation.

Expected workflow artifacts include requirements.md, architecture.md, design-review.md, and impl-plan.md, plus implementation files, verification evidence, changelog entries, and PR documentation as appropriate.

## 4. Orchestration Requirement

The pipeline must have a clearly defined orchestrator responsible for:
- Coordinating the SDLC stages.
- Tracking workflow progress.
- Checking prerequisites before advancing.
- Delegating specialist tasks when appropriate.
- Preserving decisions and results in project artifacts.
- Handling failures, rework, and incomplete stages.
- Requesting human input or approval at defined decision gates.

Do not assume that a prompt alone provides deterministic enforcement. Use verifiable artifacts and appropriate automated checks where necessary.

## 5. Human Oversight

Copilot proposes and performs work within the approved scope. The human remains responsible for requirements clarification, important design decisions, approval of consequential changes, and final acceptance.

Do not treat assumptions as approved decisions.

## 6. Source of Truth

Use the accompanying original capstone Word document as the source for the assignment's stated lifecycle steps and deliverables.

Use this brief to clarify the intended generic scope and orchestrator requirement.

If a requirement is missing or ambiguous, identify the gap and ask for clarification rather than inventing a mandatory requirement.

## 7. Success Criteria

The pipeline should demonstrate that it can:
- Process different User Stories without rewriting its core workflow.
- Handle empty and existing repositories appropriately.
- Adapt to the repository's technology and conventions.
- Maintain traceability from requirements to implementation and tests.
- Identify review findings and verification failures.
- Produce accurate PR documentation backed by actual evidence.
- Keep humans involved in important decisions.

## 8. Current Phase

The current phase is project setup and architecture planning.

Do not implement the full pipeline until its architecture, orchestration approach, responsibilities, and acceptance criteria have been reviewed and approved.