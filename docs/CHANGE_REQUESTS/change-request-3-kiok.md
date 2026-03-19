# Change Request

## Business Input
- Date: 2026-03-20
- Topic: kiok
- Request summary: Employee full name should reject numbers and special characters


## Implementation Analysis
### Why This Matters
- Generated from current rules and request summary.

### Conflict Check
- Existing rules reviewed:
  - docs/DOMAIN_RULES.md
  - docs/DECISION_LOG.md
  - docs/TEST_MATRIX.md
- Existing tests reviewed:
  - tests relevant to the affected area
- Conflicts found:
  - Current workflow status: answered

### Open Questions
- Question 1: Which characters should still be allowed in the full name field, for example spaces, hyphens, apostrophes, or periods?
  - Why this matters: The exact allowed-character set defines the validation rule and prevents accidentally blocking legitimate real-world names.
  - Blocked implementation areas:
    - schema validation
    - employee create/update endpoints
    - UI validation hints
    - edge-case tests
  - User answer: spaces only but inNot at the starting or at the end. If there is any space at the start or the end, just trim it.  Names can be two or three words, so spaces in between are expected. Some dots are also fine—for example, "Mr." or similar titles. Dots are acceptable if they use them, as are spaces between words. between only, 
- Question 2: How should the system handle existing employee records that already contain numbers or special characters in the full name?
  - Why this matters: Changing validation for new requests is straightforward, but existing data may need to be grandfathered, flagged, or cleaned up.
  - Blocked implementation areas:
    - existing database records
    - update behavior
    - migration strategy
    - regression tests
  - User answer: Ignore what we have in existing names; for the new names only, from now onwards.

### TDD Status
- Red: not started
- Green: not started
- Refactor: not started

### Documentation Files To Update After Answers
- docs/DOMAIN_RULES.md
- docs/DECISION_LOG.md
- docs/TEST_MATRIX.md
- active change request file
