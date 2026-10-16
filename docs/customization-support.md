# Customization Support

Support details verified against current VS Code documentation on 2026-10-16. Recheck the selected VS Code/Copilot version and organization policy before rollout.

| Customization | Repository location | Intended use | Harness note |
| --- | --- | --- | --- |
| Shared instructions | `.github/copilot-instructions.md` | Pipeline-repository rules; preserve target-owned instructions | Copilot customization supported |
| Custom agents | `.github/agents/*.agent.md` | Orchestrator and bounded specialist roles with tool lists | Workspace agents supported; tools vary by harness |
| Agent Skills | `.github/skills/<name>/SKILL.md` | On-demand repeatable procedures | Supported by Copilot; names must match directories |
| Prompt files | `.github/prompts/*.prompt.md` | Manual start/resume/stage/review/PR shortcuts | Current VS Code docs: Local harness only, not Copilot harness |

Prompt files use `.prompt.md` with optional YAML fields such as `name`, `description`, `argument-hint`, `agent`, `model`, and `tools`. These prompts set `agent: SDLC Orchestrator` and guide its saved-state/gate process; they do not define an alternate workflow. Use them only when the Local harness is selected. In Copilot-harness sessions, select the SDLC Orchestrator custom agent directly; do not claim the prompt slash commands are available there.

Custom agents use `.agent.md` and YAML frontmatter. The orchestrator allow-lists its specialist agents and enables the `agent` tool for delegation. Specialized agents have role-appropriate built-in tool groups (read-only where possible). MCP names remain dynamic and must be selected only after actual server/tool verification; no server IDs or write tool IDs are embedded in customizations.

Skills use `SKILL.md` with required `name` and `description`. For workspace skills, the `name` must match the containing directory. Skills are discoverable in Copilot, but discovery does not guarantee automatic invocation; the orchestrator/agents explicitly reference the relevant procedures.

## Verification

Run the static metadata checks from the pipeline root:

```powershell
python scripts/validate_workflow.py --root .
```

Then use VS Code's Agent Customizations diagnostics with the intended harness to verify actual discovery. For prompt files, select Local and confirm the five prompt entries appear. With Copilot harness selected, confirm the orchestrator and skills appear and invoke the orchestrator directly. File-format checks cannot prove that a specific account, policy, or installed VS Code build exposes a customization.

References: [custom agents](https://code.visualstudio.com/docs/agent-customization/custom-agents), [prompt files](https://code.visualstudio.com/docs/agent-customization/prompt-files), [Agent Skills](https://code.visualstudio.com/docs/agent-customization/agent-skills), and [customization overview](https://code.visualstudio.com/docs/agent-customization/overview).