import assert from 'node:assert/strict';
import { test } from 'node:test';
import { api } from './api.js';

test('resposta HTML no lugar de JSON deve gerar erro, não dados nulos', async (t) => {
  t.mock.method(globalThis, 'fetch', async () => new Response('<!doctype html><html></html>', {
    status: 200, headers: { 'Content-Type': 'text/html' },
  }));
  await assert.rejects(api('donos'), /resposta inválida/i);
});
