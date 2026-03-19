# Test Matrix

This file maps domain rules to automated test coverage.

## Employee CRUD
- Rule: create requires all employee fields
  - Coverage: `tests/test_employee_crud.py`
  - Expected checks:
    - valid create returns `201`
    - invalid salary returns `422`
- Rule: get by ID returns existing employee
  - Coverage: `tests/test_employee_crud.py`
- Rule: list returns created records
  - Coverage: `tests/test_employee_crud.py`
- Rule: delete removes record
  - Coverage: `tests/test_employee_crud.py`
- Rule: missing employee returns `404`
  - Coverage: `tests/test_employee_crud.py`

## Employee Update
- Rule: update supports full payload
  - Coverage: `tests/test_employee_crud.py`
- Rule: update supports partial payload
  - Coverage: `tests/test_employee_crud.py`
- Rule: omitted fields remain unchanged
  - Coverage: `tests/test_employee_crud.py`
- Rule: empty payload currently preserves existing values
  - Coverage: `tests/test_employee_crud.py`

## Salary Calculation
- Rule: India deduction is 10%
  - Coverage: `tests/test_salary_calculation.py`
- Rule: United States deduction is 12%
  - Coverage: `tests/test_salary_calculation.py`
- Rule: all other countries have no deduction
  - Coverage: `tests/test_salary_calculation.py`
- Rule: missing employee returns `404`
  - Coverage: `tests/test_salary_calculation.py`

## Salary Metrics
- Rule: country metrics return min, max, avg
  - Coverage: `tests/test_salary_metrics.py`
- Rule: missing country metrics return `404`
  - Coverage: `tests/test_salary_metrics.py`
- Rule: job title metrics return average salary
  - Coverage: `tests/test_salary_metrics.py`
- Rule: missing job title metrics return `404`
  - Coverage: `tests/test_salary_metrics.py`

## Gaps To Watch
- No automated UI tests currently verify placeholder copy or mandatory labels.
- No automated test currently enforces "fill at least one field below" as a backend error rule because empty payload is still allowed.
