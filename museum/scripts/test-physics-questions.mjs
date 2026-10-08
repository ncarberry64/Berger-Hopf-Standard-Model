import test from 'node:test';
import assert from 'node:assert/strict';
import { access, readFile } from 'node:fs/promises';
import { execFileSync } from 'node:child_process';
import { physicsQuestions, questionTopics } from '../lib/physics-questions.mjs';
import { catalog } from '../lib/ai-guide.mjs';

const visuals = new Set([
  'geometry',
  'mass',
  'forces',
  'wave',
  'correlation',
  'uncertainty',
  'core',
  'expansion',
  'cycle',
  'darkmatter',
  'symmetry',
  'monopole',
  'test',
]);

test('every question has an answer, scientific scope and supported animation', () => {
  const ids = new Set();
  const topics = new Set(questionTopics.map(({ id }) => id));
  for (const question of physicsQuestions) {
    assert(!ids.has(question.id), `Duplicate question: ${question.id}`);
    ids.add(question.id);
    assert(topics.has(question.topic));
    assert(visuals.has(question.visual));
    for (const field of [
      'title',
      'answer',
      'detail',
      'status',
      'boundary',
      'caption',
    ])
      assert(question[field]?.trim(), `${question.id} lacks ${field}`);
    assert(question.sources.length, `${question.id} lacks supporting sources`);
  }
  for (const topic of questionTopics)
    assert(physicsQuestions.some((question) => question.topic === topic.id));
  for (const id of [
    'monopoles',
    'multiverse',
    'expansion',
    'dark-matter',
    'cp-violation',
  ])
    assert(ids.has(id), `Missing requested puzzle: ${id}`);
});

test('supporting sources exist in the tracked scientific record', async () => {
  const repoRoot = new URL('../../', import.meta.url);
  const tracked = new Set(
    execFileSync('git', ['ls-files', '-z'], {
      cwd: repoRoot,
      encoding: 'utf8',
    }).split('\0'),
  );
  for (const question of physicsQuestions) {
    for (const source of question.sources) {
      assert(source.title?.trim());
      assert(!source.path.includes('..') && !source.path.startsWith('/'));
      assert(
        tracked.has(source.path),
        `${question.id}: untracked source ${source.path}`,
      );
      await access(new URL(source.path, repoRoot));
    }
  }
});

test('the public question download preserves answers, scopes and citations', async () => {
  const download = JSON.parse(
    await readFile(
      new URL('../public/data/physics-questions.json', import.meta.url),
      'utf8',
    ),
  );
  assert.equal(download.schema, 'bhsm-physics-questions/v1');
  assert.deepEqual(download.topics, questionTopics);
  assert.deepEqual(download.questions, physicsQuestions);
  assert.equal(
    download.source_base_url,
    `${catalog.repository_url}/blob/main/`,
  );
  const entry = catalog.exhibits.find(({ id }) => id === 'big-questions');
  assert(entry.question.endsWith('?'));
  assert(
    entry.sources.some(({ url }) =>
      url.endsWith('/data/physics-questions.json'),
    ),
  );
});
