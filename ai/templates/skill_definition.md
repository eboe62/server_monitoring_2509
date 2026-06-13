# TEMPLATE: SKILL SPECIFICATION MODEL
# Location: ai/templates/skill_definition.md
# Reference: ai/governance/SKILL_ACTIVATION_MODEL.md

# Skill Metadata

Skill Name:
[system_name_of_the_skill_in_snake_case]

Status:
[PROPOSED | ACTIVE | DEPRECATED | SUPERSEDED]

Owner:
[Role or Team responsible for maintaining this skill]

Version:
[X.Y.Z - Semantic Versioning]

Last Review:
[YYYY-MM-DD]

Superseded By:
[NONE | Link to the replacing skill_name]

ADR Dependencies:
- [NONE | List of mandatory ADR-0XXX codes that restrict this skill]

Governance Dependencies:
- [NONE | List of core governance documents required, e.g., DEVSECOPS_PRINCIPLES.md]

Related Skills:
- [List of skills that are frequently co-activated or complement this execution block]

---

# Core Directive & Purpose
[Clear, tight definition of what this skill does and why it exists in the system.
Example: "Enforces strict container compliance by auditing runtime parameters."]

# Execution Requirements
- [Mandatory gate 1: e.g., Must read specific configuration file before acting]
- [Mandatory gate 2: e.g., Must run local script check to verify compliance state]

# Behavior Rules & Constraints
1. [Constraint 1: What the AI is FORBIDDEN to do when this skill is active]
2. [Constraint 2: What formatting, logging, or language rules apply to its outputs]

# Expected Validation Output
[Describe the precise evidence the AI must print in the console to prove this skill was executed successfully.]
