import test from 'node:test';
import assert from 'node:assert/strict';
import { access, readFile } from 'node:fs/promises';
import {
  catalog,
  aiHandoff,
  aiHandoffJSON,
  museumUrl,
} from '../lib/ai-guide.mjs';
import { slides } from '../lib/museum-slides.mjs';
import { reviewEntries } from '../lib/museum-review.mjs';

test('science exhibits 1–10 have review questions; record exhibits retain statements', () => {
  assert.deepEqual(
    Object.keys(reviewEntries),
    slides.slice(0, -1).map(([id]) => id),
  );
  for (const entry of catalog.exhibits.slice(0, 10)) {
    assert.equal(entry.statement, reviewEntries[entry.id].statement);
    assert(
      entry.classification &&
        entry.question.endsWith('?') &&
        entry.sources.length,
    );
  }
});

test('the clipboard packet is valid JSON with current GitHub entry points', async () => {
  assert.deepEqual(JSON.parse(aiHandoffJSON), aiHandoff);
  assert.equal(aiHandoff.repository.branch, 'main');
  assert.equal(aiHandoff.start_here.length, 4);
  for (const source of aiHandoff.start_here) {
    assert(source.url.startsWith(aiHandoff.repository.raw_base_url));
    const path = source.url.slice(aiHandoff.repository.raw_base_url.length);
    assert.equal(source.path, path);
    assert.equal(
      source.github_url,
      `${aiHandoff.repository.url}/blob/main/${path}`,
    );
    await access(new URL(`../../${path}`, import.meta.url));
  }
});

test('every museum slide has a scoped retrieval entry and existing local sources', async () => {
  assert.deepEqual(
    catalog.exhibits.map(({ id, title }) => [id, title]),
    slides,
  );
  for (const entry of catalog.exhibits) {
    assert.equal(new URL(entry.url).hash, `#${entry.id}`);
    assert(entry.summary && entry.scope && entry.sources.length);
    for (const source of entry.sources) {
      assert.equal(new URL(source.url).protocol, 'https:');
      if (source.url.startsWith(museumUrl)) {
        await access(
          new URL(
            `../public/${source.url.slice(museumUrl.length)}`,
            import.meta.url,
          ),
        );
      } else if (source.url.startsWith(aiHandoff.repository.raw_base_url)) {
        await access(
          new URL(
            `../../${source.url.slice(aiHandoff.repository.raw_base_url.length)}`,
            import.meta.url,
          ),
        );
      }
    }
  }
});

test('downloadable context matches the clipboard and covers completion boundaries', async () => {
  const packet = JSON.parse(
    await readFile(
      new URL('../public/ai/handoff.json', import.meta.url),
      'utf8',
    ),
  );
  assert.deepEqual(packet, JSON.parse(aiHandoffJSON));
  assert.deepEqual(packet.retrieval_plan, catalog.retrieval_plan);
  assert(
    packet.retrieval_plan.suggested_searches.some((query) =>
      query.includes('site:github.com/'),
    ),
  );
  assert(
    packet.answer_guidance.some((line) =>
      line.includes('existing definition of done'),
    ),
  );
  assert(
    packet.answer_guidance.some((line) =>
      line.includes('historical numerical screens'),
    ),
  );
  const index = JSON.parse(
    await readFile(new URL('../public/ai/index.json', import.meta.url), 'utf8'),
  );
  assert.deepEqual(index, catalog);
});

test('offline packet contains verifiable verbatim source text and provenance', async () => {
  const { createHash } = await import('node:crypto');
  assert.equal(aiHandoff.schema, 'bhsm-ai-handoff/v2');
  assert(aiHandoff.offline_instruction.includes('embedded_source_snapshot'));
  assert(aiHandoff.embedded_source_snapshot.sources.length >= 8);
  for (const source of aiHandoff.embedded_source_snapshot.sources) {
    const full = (
      await readFile(new URL(`../../${source.path}`, import.meta.url), 'utf8')
    ).replaceAll('\r\n', '\n');
    assert.equal(
      source.text,
      full
        .split('\n')
        .slice(source.first_line - 1, source.last_line)
        .join('\n'),
    );
    assert.equal(
      source.normalized_source_sha256,
      createHash('sha256').update(full).digest('hex'),
    );
    assert.match(source.revision, /^[0-9a-f]{40}$/);
    assert(source.source_url.includes(source.revision));
  }
  for (const entry of catalog.exhibits.slice(10, 12))
    assert.equal(entry.question, null);
});

test('computing replay retains the exact recorded benchmark and its adverse precision result', async () => {
  const copy = JSON.parse(
    await readFile(
      new URL('../lib/cms-benchmark.json', import.meta.url),
      'utf8',
    ),
  );
  const source = JSON.parse(
    await readFile(
      new URL(
        '../../artifacts/cern_open_data_benchmark/results.json',
        import.meta.url,
      ),
      'utf8',
    ),
  );
  assert.deepEqual(copy, source);
  assert.equal(copy.correctness.all_kernels_equivalent, false);
  assert.equal(
    copy.correctness.scale_aware_float64_consistency.all_within_bound,
    true,
  );
});
