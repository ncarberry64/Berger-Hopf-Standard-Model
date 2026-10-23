import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { slides } from '../lib/museum-slides.mjs';
import { exhibitSoundtracks } from '../lib/exhibit-soundtracks.mjs';

test('every numbered exhibit has a different licensed local recording', async () => {
  assert.deepEqual(exhibitSoundtracks.map((track) => track.slideId), slides.map(([id]) => id));
  assert.equal(new Set(exhibitSoundtracks.map((track) => track.source)).size, slides.length);
  assert.equal(new Set(exhibitSoundtracks.map((track) => track.sha256)).size, slides.length);
  const metadata = JSON.parse(await readFile(new URL('../public/audio/exhibit-soundtracks.json', import.meta.url), 'utf8'));
  assert.deepEqual(metadata, exhibitSoundtracks);
  for (const track of exhibitSoundtracks) {
    assert.match(track.source, /^\.\/audio\/scott-buckley-[a-z-]+\.mp3$/);
    assert.equal(new URL(track.creditUrl).hostname, 'www.scottbuckley.com.au');
    assert.equal(track.licenseUrl, 'https://creativecommons.org/licenses/by/4.0/');
    assert.ok(track.durationSeconds > 120);
    const bytes = await readFile(new URL(`../public/${track.source.slice(2)}`, import.meta.url));
    assert.equal(bytes.length, track.bytes);
    assert.ok(bytes.length < 25 * 1024 * 1024, 'each track fits the hosting asset limit');
    assert.equal(createHash('sha256').update(bytes).digest('hex'), track.sha256);
  }
});

test('public credits identify every new recording and preserve original source credit', async () => {
  const credits = await readFile(new URL('../public/soundtrack-credits.html', import.meta.url), 'utf8');
  for (const track of exhibitSoundtracks) assert.ok(credits.includes(track.creditUrl));
  for (const credit of ['Scott Buckley', 'CC BY 4.0', 'transcoded', 'PaulYudin', 'Inspiring Epic', 'Epic Cinematic Victory']) {
    assert.ok(credits.includes(credit));
  }
});
