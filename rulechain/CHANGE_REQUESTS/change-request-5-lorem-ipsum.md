# Change Request

## Business Input
- Date: 2026-03-20
- Topic: lorem ipsum 
- Request summary: Salary should be full number and not any decimal value.

## Implementation Analysis
### Why This Matters
- Generated from current rules and request summary.

### Conflict Check
- Existing rules reviewed:
  - rulechain/DOMAIN_RULES.md
  - rulechain/DECISION_LOG.md
  - rulechain/TEST_MATRIX.md
- Existing tests reviewed:
  - tests relevant to the affected area
- Conflicts found:
  - Current workflow status: answered

### Open Questions
- Question 1: Should salary allow exactly two decimal places, or up to two decimal places?
  - Why this matters: That choice changes validation rules and determines whether whole numbers remain valid without trailing decimal digits.
  - Blocked implementation areas:
    - salary schema validation
    - UI input behavior
    - tests
    - API examples
  - User answer: Ignore what we have in existing names; for the new names only, from now onwards.
- Question 2: If a salary value has more than two decimal places, should the system reject it or round it?
  - Why this matters: Rounding and rejection are both valid strategies, but they lead to different financial behavior.
  - Blocked implementation areas:
    - create/update validation
    - salary calculations
    - metrics accuracy
    - regression tests
  - User answer: spaces only but inNot at the starting or at the end. If there is any space at the start or the end, just trim it.  Names can be two or three words, so spaces in between are expected. Some dots are also fine—for example, "Mr." or similar titles. Dots are acceptable if they use them, as are spaces between words. between only, 

### TDD Status
- Red: not started
- Green: not started
- Refactor: not started

### Documentation Files To Update After Answers
- rulechain/DOMAIN_RULES.md
- rulechain/DECISION_LOG.md
- rulechain/TEST_MATRIX.md
- active change request file
