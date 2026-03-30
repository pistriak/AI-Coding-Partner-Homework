# Skill: Unit Tests FIRST

Apply this checklist to every generated test set.

## FIRST Definition
- `Fast`: Runs quickly without external network/services.
- `Independent`: Tests do not depend on execution order.
- `Repeatable`: Stable outcomes across runs and environments.
- `Self-validating`: Explicit assertions with clear pass/fail.
- `Timely`: Tests target newly changed behavior immediately.

## Practical Checks
- Use in-memory app/server where possible.
- Avoid shared mutable state between tests.
- Avoid real clocks/randomness unless controlled.
- Assert status codes and response bodies directly.
- Map each new test to a specific code change from `fix-summary.md`.

## Report Requirement
`test-report.md` must include one short note per FIRST letter describing compliance evidence.

