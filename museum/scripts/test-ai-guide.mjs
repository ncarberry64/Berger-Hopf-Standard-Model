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

test('the clipboard packet is valid JSON with current GitHub entry points', async () => {
  assert.deepEqual(JSON.parse(aiHandoffJSON), aiHandoff);
  assert.equal(aiHandoff.repository.branch, 'main');
  assert.equal(aiHandoff.start_here.length, 4);
  for (const source of aiHandoff.start_here) {
    assert(source.url.startsWith(aiHandoff.repository.raw_base_url));
    const path = source.url.slice(aiHandoff.repository.raw_base_url.length);
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
