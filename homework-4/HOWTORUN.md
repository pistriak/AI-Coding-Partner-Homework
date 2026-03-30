# How To Run

## 1) Install dependencies
```bash
cd demo-bug-fix
npm install
```

## 2) Run the API
```bash
cd demo-bug-fix
npm start
```

API endpoints:
- `GET /health`
- `GET /api/users`
- `GET /api/users/:id`

## 3) Run tests
```bash
cd demo-bug-fix
npm test
```

Expected result: 4 passing tests.

## 4) Manual bug verification
```bash
curl http://localhost:3000/api/users/123
curl http://localhost:3000/api/users/999
curl http://localhost:3000/api/users/abc
```

Expected:
- `/123` -> `200` with user JSON
- `/999` -> `404` with `{"error":"User not found"}`
- `/abc` -> `400` with `{"error":"Invalid user id format"}`

