# Change Impact Checklist

Use this checklist before implementing any new behavior.

## Review Areas
- API validation
- API response codes
- UI labels and hints
- Domain rules
- Tests
- Seed/demo data
- README and operational docs

## Required Questions
Ask questions before implementation if any of the following are true:
- the new requirement changes an existing documented rule
- the UI request implies backend behavior changes
- tests and docs disagree
- a new field or endpoint changes existing validation assumptions
- a user request is compatible with multiple behaviors

## Expected Output For Each Change
- impacted files
- impacted rules
- new tests required
- possible regressions
- unresolved questions
