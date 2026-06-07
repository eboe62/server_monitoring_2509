# Repository Commit Message Template

## Objective

Generate commit messages aligned with repository governance.

## Rules

* Be concise.
* Be precise.
* Describe only implemented changes.
* Do not describe intentions.
* Do not describe future work.
* Do not exaggerate impact.
* Do not use marketing language.
* Do not use optimistic refactor language.
* Respect approved scope.
* Respect approved ADRs.

## Preferred Format

<type>: <short description>

Examples:

docs: update ADR-00xx references

ci: add docker compose validation

security: restrict smtp container capabilities

monitoring: add promtail positions persistence

## Constraints

Avoid:

* improved
* enhanced
* optimized
* modernized
* refactored (unless actual refactor occurred)
* fixed everything
* cleanup

Prefer factual descriptions based on evidence.

## Output

Return only the commit message.
