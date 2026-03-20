# Open Questions

This file is synchronized from change-request records.

## Change Request 4: lorem ipsum 
- Question 1: Should salary allow exactly two decimal places, or up to two decimal places?
  - Status: answered
  - Why this matters: That choice changes validation rules and determines whether whole numbers remain valid without trailing decimal digits.
  - Blocked implementation areas: salary schema validation, UI input behavior, tests, API examples
  - User answer: spaces only but inNot at the starting or at the end. If there is any space at the start or the end, just trim it.  Names can be two or three words, so spaces in between are expected. Some dots are also fine—for example, "Mr." or similar titles. Dots are acceptable if they use them, as are spaces between words. between only, 
- Question 2: If a salary value has more than two decimal places, should the system reject it or round it?
  - Status: answered
  - Why this matters: Rounding and rejection are both valid strategies, but they lead to different financial behavior.
  - Blocked implementation areas: create/update validation, salary calculations, metrics accuracy, regression tests
  - User answer: sadasd
