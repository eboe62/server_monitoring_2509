# Copilot Governance – server_monitoring_2509

Operational Mode:
- Always separate analysis from execution.
- Do not execute changes during analysis phase.
- Wait for explicit approval before modifying any file.
- If execution is attempted without approval, the response is invalid.

Scope Control:
- Only modify files explicitly listed in the prompt.
- Never perform opportunistic refactors.
- No implicit improvements.
- If additional files are required, stop and request confirmation.
- Any out-of-scope modification invalidates the response.

Architectural Rules:
- ADR documents are normative and binding.

Architectural rules:
- ADR documents are normative.
- RULES.txt is binding.
- Micro-stack and Infra-stack boundaries are strict.
- No cross-service modifications unless explicitly requested.
- monitoring-net must remain external unless explicitly changed.
- No Swarm unless explicitly declared.

Execution rules:
- Always propose plan before modifying files.
- Wait for explicit approval.
- Only modify files explicitly listed in the prompt.
- If additional files are required, stop and request confirmation.
- Any out-of-scope modification invalidates the response.

Design Philosophy:
- Minimal changes only.
- Deterministic behavior preferred over clever solutions.
- Precision is more important than productivity.

If any rule conflicts with the user request, stop and request clarification.
