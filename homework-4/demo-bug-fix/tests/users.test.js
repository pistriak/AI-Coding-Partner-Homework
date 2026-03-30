const test = require('node:test');
const assert = require('node:assert/strict');
const request = require('supertest');
const app = require('../server');

test('GET /api/users returns all users', async () => {
  const response = await request(app).get('/api/users');

  assert.equal(response.status, 200);
  assert.equal(Array.isArray(response.body), true);
  assert.equal(response.body.length, 3);
});

test('GET /api/users/:id returns 200 for an existing user id', async () => {
  const response = await request(app).get('/api/users/123');

  assert.equal(response.status, 200);
  assert.deepEqual(response.body, {
    id: 123,
    name: 'Alice Smith',
    email: 'alice@example.com'
  });
});

test('GET /api/users/:id returns 404 for unknown id', async () => {
  const response = await request(app).get('/api/users/999');

  assert.equal(response.status, 404);
  assert.deepEqual(response.body, { error: 'User not found' });
});

test('GET /api/users/:id returns 400 for non-numeric id', async () => {
  const response = await request(app).get('/api/users/abc');

  assert.equal(response.status, 400);
  assert.deepEqual(response.body, { error: 'Invalid user id format' });
});

