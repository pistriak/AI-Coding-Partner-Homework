# Bug: API-404

**Title**: GET /api/users/:id returns 404 for valid user IDs  
**Priority**: High  
**Status**: Fixed

## Description
`GET /api/users/:id` historically returned `404` for existing users because route params arrive as strings while in-memory user IDs are numbers.

## Expected
`GET /api/users/123` returns user object and `200`.

## Actual (Before Fix)
`GET /api/users/123` returned `{ "error": "User not found" }` with `404`.

## Scope
- API route: `GET /api/users/:id`
- Controller lookup logic in `demo-bug-fix/src/controllers/userController.js`

