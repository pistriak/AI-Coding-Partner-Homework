# Homework 4 - 4-Agent Pipeline

This repository implements the required 4-agent bug-fix pipeline and applies a fix for bug `API-404` in the demo Express app.

## Implemented Agents
- `agents/research-verifier.agent.md`
- `agents/bug-implementer.agent.md`
- `agents/security-verifier.agent.md`
- `agents/unit-test-generator.agent.md`

## Implemented Skills
- `skills/research-quality-measurement.md`
- `skills/unit-tests-FIRST.md`

## Bug Context and Artifacts
- Context folder: `context/bugs/API-404/`
- `bug-context.md`
- `research/codebase-research.md`
- `research/verified-research.md`
- `implementation-plan.md`
- `fix-summary.md`
- `security-report.md`
- `test-report.md`

## Application Fix Summary
Fixed `GET /api/users/:id` lookup in `demo-bug-fix/src/controllers/userController.js` by validating numeric route params and converting them before strict comparison.

Added tests in `demo-bug-fix/tests/users.test.js` and test script in `demo-bug-fix/package.json`.

## Quick Run
See `HOWTORUN.md` for full instructions.

