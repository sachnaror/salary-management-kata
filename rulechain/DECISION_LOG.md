# Decision Log

This file records product and implementation decisions that affect future work.

## 2026-03-20
- Chosen project memory model: documentation-driven workflow using files in `rulechain/`.
- Chosen TDD gate: every non-trivial change must follow red -> green -> refactor.
- Chosen clarification rule: if a request can conflict with existing logic, questions must be raised before implementation.
- Chosen update behavior: `PUT /employees/{employee_id}` supports partial updates.
- Chosen update payload behavior: empty update payload currently leaves the record unchanged.
- Chosen create-form UX rule: all create fields are presented as `Mandatory`.
- Chosen update-form UX rule: employee ID is mandatory, and the user is instructed to fill at least one field below.

## Logging Guidance
Each future decision entry should include:
- date
- short decision statement
- reason
- whether it changes earlier behavior
