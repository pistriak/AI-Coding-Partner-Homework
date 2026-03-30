# Implementation Plan: API-404

## Scope
Fix ID type handling in single-user lookup and add regression tests for changed behavior.

## Planned Changes
1. **Controller fix**
   - File: `demo-bug-fix/src/controllers/userController.js`
   - Before: route param treated as string and compared against numeric `users[].id`.
   - After: validate numeric format, convert to number, then strict compare.
   - Added behavior: return `400` for non-numeric IDs.

2. **Testability improvement**
   - File: `demo-bug-fix/server.js`
   - Before: server started on import, making integration tests brittle.
   - After: start listening only when run directly (`require.main === module`).

3. **Automated tests**
   - Files: `demo-bug-fix/package.json`, `demo-bug-fix/tests/users.test.js`
   - Add `npm test` script and tests for:
     - `GET /api/users` returns list
     - `GET /api/users/123` returns existing user
     - `GET /api/users/999` returns 404
     - `GET /api/users/abc` returns 400

## Test Command
```bash
cd demo-bug-fix
npm test
```

