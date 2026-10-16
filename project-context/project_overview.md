Here is a well-formatted, clean, and professional version of your GitHub Copilot Capstone Project guide, structured using Markdown for maximum readability.

---

# GitHub Copilot Capstone Project

## Agentic SDLC

### GitHub Copilot Agent Mode Project Overview

In this capstone, you will build an **Agentic SDLC Pipeline** implementation from scratch using GitHub Copilot's capabilities and features. The SDLC implementation is entirely driven through GitHub Copilot **Agents, Prompts, Instructions, Skills, and Hooks** as needed.

You will practice the complete software delivery lifecycle—from writing requirements to merging a production-ready Pull Request—with GitHub Copilot as your AI pair programmer at every step.

---

### Step 1: Requirements

Use GitHub Copilot Chat/CLI to collaboratively define and document the functional and non-functional requirements for a given User Story.

* **Read Input:** Read a new User Story from JIRA, Confluence, or a Word document.
* **Collaborate:** Let Copilot ask or clarify questions on the story, and respond to those questions.
* **Capture & Commit:** Capture the final requirements in `requirements.md` and commit the file.

---

### Step 2: Architecture

Use GitHub Copilot Chat/CLI to design the high-level system architecture. Ask Copilot to propose component diagrams, technology choices, and data flow.

* **Get Recommendations:** Ask for an architecture recommendation based on your `requirements.md`.
* **Document:** Document the proposed architecture in `architecture.md`.
* **Map Responsibilities:** Identify the key components and their individual responsibilities.

---

### Step 3: Design Review

Use GitHub Copilot Chat/CLI to conduct a structured design review of the architecture before writing any production code (treating Copilot as a senior reviewer).

* **Identify Risks:** Share `architecture.md` with Copilot Chat and ask it to identify risks and gaps.
* **Log Findings:** Document review findings and agreed design decisions in `design-review.md`.
* **Refine:** Update `architecture.md` if any issues are found.

---

### Step 4: Implementation Planning

Use GitHub Copilot Chat/CLI to break the approved architecture down into a prioritized, dependency-ordered task list.

* **Generate Breakdown:** Ask Copilot to generate a task breakdown from `architecture.md`.
* **Document Plan:** Document the plan in `impl-plan.md`, ordered strictly by dependency.
* **Track Blockers:** Identify any blocked tasks that cannot start until another finishes.

---

### Step 5: Implementation

Use GitHub Copilot Chat/CLI to implement the changes suggested by GitHub Copilot and approved by the human-in-the-loop, leveraging all available Copilot features.

---

### Step 6: Review

Use GitHub Copilot Chat/CLI to perform a structured code review of your implementation before creating the PR, with Copilot acting as a peer reviewer.

#### Code Review Checklist

Ask Copilot to evaluate each of the following areas:

| Review Area | Review Question |
| --- | --- |
| **Correctness** | Does each component behave as specified in `requirements.md`? |
| **Security** | Are secrets excluded from output? Is user input validated? |
| **Error Handling** | Are all API failures, missing files, and empty repos handled gracefully? |
| **Test Coverage** | Do tests cover the happy path **AND** the 'Not Found' / missing-field edge cases? |
| **Code Clarity** | Are function names self-explanatory? Is logic easy to follow without comments? |
| **DRY Principle** | Is there duplicated logic that Copilot can refactor into a shared function? |
| **Dependency Safety** | Does Copilot flag any known-vulnerable package versions? |

---

### Step 7: Verify

Use GitHub Copilot to generate and run a comprehensive verification suite, verifying both the code (unit and integration tests) and the final output document (content quality check).

---

### Step 8: PR Using Agentic SDLC

Use GitHub Copilot Agent Mode to create the Pull Request—including the PR description, changelog entry, and review checklist—completing the full agentic SDLC cycle.

#### Required PR Description Sections

*(Copilot must generate all of the following sections)*

1. **Summary:** 2-3 sentence overview of what was built and why.
2. **Changes Made:** Bulleted list of all files added/modified and the reason for each.
3. **Test Evidence:** Paste the test run output or provide a link to CI results.
4. **Known Limitations:** Anything marked 'Not Found' or left out of scope.
5. **Reviewer Checklist:** A tick-list the reviewer must complete before approving.

---

Would you like to customize any specific section or add more detailed instructions for a particular step?