# Implementation Protocol

This protocol is the required execution order for any future code or behavior change in this repository.

## Mandatory Workflow
1. Read `docs/DOMAIN_RULES.md`.
2. Read `docs/DECISION_LOG.md`.
3. Read `docs/TEST_MATRIX.md`.
4. Read the active file in `docs/CHANGE_REQUESTS/`.
5. Check whether the requested change conflicts with:
   - existing endpoint behavior
   - existing UI copy and validation
   - existing tests
   - documented business rules
   - earlier decisions
6. If any ambiguity, conflict, or missing acceptance criteria exists:
   - write the questions into `docs/OPEN_QUESTIONS.md`
   - present all questions to the user first
   - wait for answers before implementation
7. If the change is clear:
   - write or update failing tests first
   - confirm the failing state
   - implement the minimum code needed to make tests pass
   - refactor without changing behavior
8. After implementation, update:
   - `docs/DOMAIN_RULES.md`
   - `docs/DECISION_LOG.md`
   - `docs/TEST_MATRIX.md`
   - the active `docs/CHANGE_REQUESTS/...md`
   - any user-facing docs affected by the change

## TDD Gate
No feature or behavior change is complete unless the following are true:
- `Red`: at least one relevant failing test existed before the implementation
- `Green`: the new or changed tests pass
- `Refactor`: the final code was cleaned without changing tested behavior

## Conflict Detection Rules
Before any implementation, compare the request against:
- validation logic in the API
- labels or hints in the UI
- existing response codes
- test expectations
- prior product decisions

If two sources disagree, do not guess. Ask first.

## Automatic Project Memory
The system does not "remember" changes outside the repository. The repo must therefore act as project memory.

That means every accepted logic change must be written back into these docs so future work can re-read and apply it consistently.
