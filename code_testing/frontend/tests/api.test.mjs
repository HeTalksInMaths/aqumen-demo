import test from 'node:test';
import assert from 'node:assert/strict';

import { fetchQuestionBlocking, transformStep7ToReact } from '../../../minimal/frontend/src/api.js';

const sampleAssessment = {
  title: 'Adversarial Matrix Factorization',
  difficulty: 'Advanced',
  code: ['<<START>>', 'matrix_factorization()', '<<END>>'],
  errors: [
    { id: 'E1', description: 'Incorrect loss function' },
    { id: 'E2', description: 'Missing regularization' }
  ],
  metadata: { reviewer: 'strong' }
};

test('transformStep7ToReact converts pipeline payload into frontend shape', () => {
  const result = transformStep7ToReact(sampleAssessment);
  assert.deepStrictEqual(result, {
    title: 'Adversarial Matrix Factorization',
    difficulty: 'Advanced',
    code: ['<<START>>', 'matrix_factorization()', '<<END>>'],
    errors: [
      { id: 'E1', description: 'Incorrect loss function' },
      { id: 'E2', description: 'Missing regularization' }
    ],
    _metadata: { reviewer: 'strong' }
  });
});

test('transformStep7ToReact rejects incomplete assessment payloads', () => {
  assert.throws(() => transformStep7ToReact({}), /Invalid assessment format/);
});

test('fetchQuestionBlocking posts to the API and returns transformed data', async () => {
  const calls = [];
  const originalFetch = globalThis.fetch;

  globalThis.fetch = async (...args) => {
    calls.push(args);
    return {
      ok: true,
      json: async () => ({ success: true, assessment: sampleAssessment })
    };
  };

  try {
    const result = await fetchQuestionBlocking('matrix factorization', 2, {
      selectedDifficulty: 'Advanced',
      selectedSubtopic: 'Optimization'
    });

    assert.strictEqual(result.title, sampleAssessment.title);
    assert.deepStrictEqual(result.code, sampleAssessment.code);

    assert.ok(calls.length === 1, 'expected one fetch call');
    const [url, options] = calls[0];
    assert.ok(url.endsWith('/api/generate'));
    assert.strictEqual(options.method, 'POST');
    assert.strictEqual(options.headers['Content-Type'], 'application/json');

    const body = JSON.parse(options.body);
    assert.strictEqual(body.topic, 'matrix factorization');
    assert.strictEqual(body.max_retries, 2);
    assert.strictEqual(body.selected_difficulty, 'Advanced');
    assert.strictEqual(body.selected_subtopic, 'Optimization');
  } finally {
    if (originalFetch) {
      globalThis.fetch = originalFetch;
    } else {
      delete globalThis.fetch;
    }
  }
});

test('fetchQuestionBlocking surfaces HTTP failures', async () => {
  const originalFetch = globalThis.fetch;
  globalThis.fetch = async () => ({
    ok: false,
    status: 503,
    json: async () => ({ detail: 'Service unavailable' })
  });

  try {
    await assert.rejects(
      fetchQuestionBlocking('matrix factorization'),
      /Service unavailable/
    );
  } finally {
    if (originalFetch) {
      globalThis.fetch = originalFetch;
    } else {
      delete globalThis.fetch;
    }
  }
});

test('fetchQuestionBlocking surfaces pipeline failures', async () => {
  const originalFetch = globalThis.fetch;
  globalThis.fetch = async () => ({
    ok: true,
    json: async () => ({ success: false, error: 'pipeline crash' })
  });

  try {
    await assert.rejects(
      fetchQuestionBlocking('matrix factorization'),
      /pipeline crash/
    );
  } finally {
    if (originalFetch) {
      globalThis.fetch = originalFetch;
    } else {
      delete globalThis.fetch;
    }
  }
});
