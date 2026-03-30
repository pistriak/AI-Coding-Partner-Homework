# Codebase Research: API-404

## Goal
Identify why `GET /api/users/:id` can fail and locate exact code path.

## Findings
1. Route wiring sends `/api/users/:id` to `getUserById` in controller.
   - Reference: `demo-bug-fix/src/routes/users.js:14`
2. User IDs are numeric in the in-memory data store.
   - Reference: `demo-bug-fix/src/controllers/userController.js:7-10`
3. Current controller now validates ID input and converts it to number before strict lookup.
   - Reference: `demo-bug-fix/src/controllers/userController.js:22-27`
4. Controller returns `404` only when user is absent after normalized lookup.
   - Reference: `demo-bug-fix/src/controllers/userController.js:29-31`
5. Server exports `app` and uses `require.main === module`, enabling isolated test execution.
   - Reference: `demo-bug-fix/server.js:24-33`

## Risk Notes
- Missing input validation could allow ambiguous parsing (`123abc`) and inconsistent behavior.
- Regression risk exists for `/api/users` and unknown IDs if lookup logic is changed.

