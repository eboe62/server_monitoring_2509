  # Claude Code Project Governance

  ## SYSTEM STOP PROTOCOL (MANDATORY)
  > **STOP:** Before any code modification, refactoring, or infrastructure execution, you MUST read and comply with `./AI_ENTRYPOINT.md`.
  > You are strictly required to separate the **Analysis Phase** from the **Execution Phase**. You must present a comprehensive Analysis Report and wait for user confirmation before writing or modifying any code.

  ## Project Context
  - **Architecture:** Single-node Docker Compose, WSL2 (Ubuntu), Node.js v24.11.1.
  - **AI Ecosystem:** Unified Governance across GitHub Copilot, Gemini CLI, and Claude Code, governed by the authoritative definitions in the root directory.

  ## Build and Test Commands
  - **Check Environment:** `node -v && npm -v`
  - **Database Status:** `docker compose -f infra/db/docker-compose.yml ps` (Adjust path if needed)

  ## Development Guidelines
  - Always prioritize user instructions and approved ADRs over general defaults.
  - Adhere to the principles in `.ai/governance/05_ANALYSIS_PROTOCOL.md` and `ai/governance/20_EXECUTION_PROTOCOL.md`.
