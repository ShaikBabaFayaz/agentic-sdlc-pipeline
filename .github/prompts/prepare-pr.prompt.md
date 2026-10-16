---
name: prepare-pr
description: Prepare draft PR materials from approved changes and recorded review and verification evidence.
argument-hint: "Provide the run ID and target repository."
agent: SDLC Orchestrator
---

Ask the SDLC Orchestrator to verify review, verification, and approval prerequisites, then delegate documentation to `pr-preparer`. Include only evidence actually recorded for this run: summary, changed files and reasons, test results, known limitations, changelog note, and reviewer checklist. Draft `pr-summary.md` only. Do not create a PR, commit, push, merge, or write to an external service without separate explicit authorization.