# Docs Brain

This folder is the long-term memory of the project. The code does the work, but `rulechain/` remembers why.

## Mission
- catch conflicts before implementation
- force questions before guesses
- preserve accepted business logic
- map rules to tests
- keep future changes from wandering off into the woods with a flashlight and misplaced confidence

## Required Flow
1. Read `IMPLEMENTATION_PROTOCOL.md`.
2. Read `DOMAIN_RULES.md`, `DECISION_LOG.md`, and `TEST_MATRIX.md`.
3. Create or update a file in `CHANGE_REQUESTS/`.
4. Write ambiguities into `OPEN_QUESTIONS.md`.
5. Stop and wait for stakeholder answers if any conflict exists.
6. Implement with TDD: red, green, refactor.
7. Update the docs after the code change is complete.

## File Guide
- `IMPLEMENTATION_PROTOCOL.md`: the non-negotiable execution order
- `DOMAIN_RULES.md`: business rules and current behavioral truth
- `DECISION_LOG.md`: what was decided and why
- `TEST_MATRIX.md`: which rule is covered by which test
- `OPEN_QUESTIONS.md`: unresolved decisions blocking implementation
- `CHANGE_IMPACT.md`: checklist for regression and conflict analysis
- `CHANGE_REQUESTS/`: one markdown record per requested change

If the application later uses OpenAI, Claude, or Gemini for automated analysis, these files become the context bundle it reads before generating questions or implementation guidance.
