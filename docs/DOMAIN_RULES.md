# Domain Rules

This file is the business-logic contract for the application.

## Employee Resource
- An employee record contains:
  - `full_name`
  - `job_title`
  - `country`
  - `salary`
- Records are persisted in the configured database.

## Create Employee
- Endpoint: `POST /employees`
- Required fields:
  - `full_name`
  - `job_title`
  - `country`
  - `salary`
- Salary must be greater than zero.
- UI guidance for create form should clearly show all fields as `Mandatory`.

## Update Employee
- Endpoint: `PUT /employees/{employee_id}`
- Required input:
  - path parameter `employee_id`
- Request body fields are optional:
  - `full_name`
  - `job_title`
  - `country`
  - `salary`
- If only one field is provided, only that field is updated.
- Omitted fields remain unchanged.
- An empty payload currently preserves the existing record unchanged.
- UI guidance for update form should clearly show:
  - employee ID is mandatory
  - the user should fill at least one field below

## Delete Employee
- Endpoint: `DELETE /employees/{employee_id}`
- `employee_id` must refer to an existing employee.

## Salary Calculation
- Endpoint: `GET /employees/{employee_id}/salary/calculate`
- Tax rules:
  - India: 10% deduction
  - United States: 12% deduction
  - all other countries: 0% deduction

## Salary Metrics
- Country metrics endpoint returns:
  - minimum salary
  - maximum salary
  - average salary
- Job title metrics endpoint returns:
  - average salary for the given title

## Error Behavior
- Non-existent employee IDs return `404`.
- Invalid input returns `422`.

## Known Questions To Revisit
- Should an empty update payload continue returning `200`, or should it become `400`?
- Should country values be normalized more aggressively than current string matching?
