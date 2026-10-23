import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { createChapterSequence } from '../lib/chapter-cues.ts';
import piano from '../lib/exhibit3-chapters.json' with { type: 'json' };
import { exhibitSoundtracks } from '../lib/exhibit-soundtracks.mjs';

// Illustrative cue positions keep transport behavior independent of the
// delivered recording's separately reviewed piano annotations.
const cues = [0.75, 8.96, 17.79, 25.62];
const music = (seconds, extra = {}) => ({
  slideId: 'berger-hopf',
  source: './audio/time-and-space.mp3',
  seconds,
  ...extra,
});

function playback(sequence, start = 0, wall = 0, extra = {}) {
  let media = start;
  let now = wall;
  let chapter = sequence.tick(now, music(media, extra));
  return {
    to(target, interval = 1 / 120) {
      assert.ok(target >= media, 'ordinary playback moves forward');
      while (media < target) {
        const next = Math.min(target, media + interval);
        now += next - media;
        media = next;
        chapter = sequence.tick(now, music(media, extra));
      }
      return chapter;
    },
    get wall() { return now; },
    get media() { return media; },
  };
}

test('chapters change at the actual piano cues, with the first note establishing Hopf', () => {
  const player = playback(createChapterSequence(cues));
  const expected = [0, 1, 2, 0];
  for (let i = 0; i < cues.length; i++) {
    assert.equal(player.to(cues[i] - 0.0001), i === 0 ? 0 : expected[i - 1], 'a chapter cannot change before its note');
    assert.equal(player.to(cues[i]), expected[i], `cue ${i} lands on its exact media timestamp`);
    assert.equal(player.to(cues[i] + 0.0001), expected[i], 'the same note cannot fire twice');
  }
});

test('unequal render intervals preserve the same chapter sequence and reading time', () => {
  for (const interval of [1 / 144, 1 / 60, 0.037, 0.11]) {
    const player = playback(createChapterSequence(cues));
    for (const [seconds, expected] of [[5, 0], [9.1, 1], [17.7, 1], [18, 2], [25.7, 0], [29, 0]])
      assert.equal(player.to(seconds, interval), expected, `${interval}-second callbacks at media ${seconds}`);
  }
});

test('the silent tour uses ten seconds until the music first engages', () => {
  const sequence = createChapterSequence(cues);
  let now = 0;
  let chapter = sequence.tick(now);
  function silentTo(target) {
    while (now < target) {
      now = Math.min(target, now + 0.125);
      chapter = sequence.tick(now);
    }
    return chapter;
  }
  assert.equal(chapter, 0);
  assert.equal(silentTo(9.999), 0);
  assert.equal(silentTo(10), 1);
  assert.equal(silentTo(20), 2);
  assert.equal(silentTo(30), 0);
  assert.equal(silentTo(40), 1);
  assert.equal(sequence.tick(40.1, music(0.1)), 0, 'starting the recording near its beginning restores Hopf');
  assert.equal(sequence.tick(40.75, music(0.75)), 0, 'the first low note establishes the initial chapter');
  assert.equal(sequence.tick(100), 0, 'after music engages, silence cannot start a replacement ten-second clock');
});

test('buffering holds a chapter until media playback actually crosses its note', () => {
  const sequence = createChapterSequence(cues);
  const player = playback(sequence);
  assert.equal(player.to(8.95), 0);
  for (const wall of [9, 9.5, 12, 18, 28])
    assert.equal(sequence.tick(wall, music(8.95)), 0, 'wall-clock time cannot substitute for a stalled recording');
  assert.equal(sequence.tick(28.01, music(8.96)), 1, 'newly played audio releases the pending cue');
  for (const wall of [29, 39, 59]) assert.equal(sequence.tick(wall, music(8.96)), 1);
});

test('pausing music holds the chapter and resuming waits for the next unheard cue', () => {
  const sequence = createChapterSequence(cues);
  const player = playback(sequence);
  assert.equal(player.to(9.1), 1);
  for (const wall of [10, 20, 30]) assert.equal(sequence.tick(wall), 1);
  assert.equal(sequence.tick(30.1, music(9.1)), 1);
  const resumed = playback(sequence, 9.1, 30.1);
  assert.equal(resumed.to(17.7899), 1);
  assert.equal(resumed.to(17.79), 2);
});

test('offscreen or animation suspension never catches up unseen chapter changes', () => {
  const sequence = createChapterSequence(cues);
  const player = playback(sequence);
  assert.equal(player.to(9.1), 1);
  sequence.suspend();
  assert.equal(sequence.tick(100, music(23)), 1, 'returning keeps the inspected chapter despite a missed note');
  const resumed = playback(sequence, 23, 100);
  assert.equal(resumed.to(25.6199), 1);
  assert.equal(resumed.to(25.62), 2, 'the next heard piano note advances one chapter');
});

test('replay in the middle of music starts at Hopf and advances on the next piano note', () => {
  const sequence = createChapterSequence(cues);
  const player = playback(sequence);
  assert.equal(player.to(20), 2);
  sequence.restart();
  assert.equal(sequence.tick(20, music(20)), 0);
  const replay = playback(sequence, 20, 20);
  assert.equal(replay.to(25.6199), 0);
  assert.equal(replay.to(25.62), 1, 'a mid-song replay follows heard cues instead of jumping to the absolute old chapter');
});

test('replay before the first piano note lets that note establish Hopf', () => {
  const sequence = createChapterSequence(cues);
  playback(sequence).to(18);
  sequence.restart();
  const replay = playback(sequence, 0.2, 100);
  assert.equal(replay.to(0.75), 0);
  assert.equal(replay.to(8.96), 1);
});

test('seeking rebases the cue cursor without firing notes that were not heard', () => {
  const sequence = createChapterSequence(cues);
  const player = playback(sequence);
  assert.equal(player.to(9.1), 1);
  assert.equal(sequence.tick(9.2, music(23, { seeking: true })), 1);
  assert.equal(sequence.tick(9.3, music(23.2, { seeking: true })), 1);
  assert.equal(sequence.tick(9.4, music(23.2)), 1);
  const resumed = playback(sequence, 23.2, 9.4);
  assert.equal(resumed.to(25.62), 2);
});

test('a seek completed between frames also cannot consume unheard cues', () => {
  const sequence = createChapterSequence(cues);
  const player = playback(sequence);
  assert.equal(player.to(9.1), 1);
  assert.equal(sequence.tick(9.2, music(23)), 1, 'an audio jump much larger than elapsed scene time is a discontinuity');
  const resumed = playback(sequence, 23, 9.2);
  assert.equal(resumed.to(25.62), 2);
});

test('a new audio source rebases without inheriting the previous cue cursor', () => {
  const sequence = createChapterSequence(cues);
  const player = playback(sequence);
  assert.equal(player.to(9.1), 1);
  const nextSource = './audio/reloaded-time-and-space.mp3';
  assert.equal(sequence.tick(9.2, music(15, { source: nextSource })), 1);
  const resumed = playback(sequence, 15, 9.2, { source: nextSource });
  assert.equal(resumed.to(17.79), 2);
});

test('a natural recording loop restores Hopf and re-arms the opening piano cues', () => {
  const sequence = createChapterSequence(cues.slice(0, 3));
  const player = playback(sequence);
  assert.equal(player.to(18), 2);
  // The fixture's end is arbitrary; crossing back to the start identifies a
  // new pass of the same recording without relying on a production duration.
  assert.equal(player.to(30), 2);
  assert.equal(sequence.tick(30.04, music(0.04)), 0);
  const loop = playback(sequence, 0.04, 30.04);
  assert.equal(loop.to(0.75), 0);
  assert.equal(loop.to(8.96), 1);
});

test('the reviewed piano cues identify the exact delivered exhibit-three recording', async () => {
  const track = exhibitSoundtracks.find((item) => item.slideId === 'berger-hopf');
  const bytes = await readFile(new URL(`../public/${track.source.slice(2)}`, import.meta.url));
  assert.equal(piano.slideId, track.slideId);
  assert.equal(piano.trackTitle, track.title);
  assert.equal(piano.source, track.source);
  assert.equal(piano.audioSha256, track.sha256);
  assert.equal(createHash('sha256').update(bytes).digest('hex'), piano.audioSha256);
  assert.ok(Math.abs(piano.durationSeconds - track.durationSeconds) < 0.1, 'only ordinary MP3 decode padding separates the timelines');
  assert.equal(piano.fixedTempoBpm, null, 'piano chapter cuts are actual recorded attacks rather than a repeating beat grid');
});

test('actual piano chapter cues are ordered, readable and backed by measured attacks', () => {
  assert.ok(piano.cueTimesSeconds.length >= 4, 'the full tour has several reviewed transitions');
  assert.ok(piano.minimumCueGapSeconds >= 6, 'chapters retain enough reading time instead of cutting on every bass ripple');
  assert.equal(piano.selectedAttackEvidence.length, piano.cueTimesSeconds.length);
  piano.cueTimesSeconds.forEach((seconds, i) => {
    assert.ok(Number.isFinite(seconds) && seconds >= 0 && seconds < piano.durationSeconds);
    if (i > 0)
      assert.ok(seconds - piano.cueTimesSeconds[i - 1] >= piano.minimumCueGapSeconds, `chapter cue ${i} preserves readable spacing`);
    const attack = piano.selectedAttackEvidence[i];
    assert.equal(attack.timeSeconds, seconds);
    assert.ok(attack.fivePercentRiseSeconds <= seconds && seconds <= attack.twentyPercentRiseSeconds);
    assert.ok(attack.twentyPercentRiseSeconds <= attack.deepRiseCrestSeconds, 'the chapter changes at the note attack, before its energy crest');
  });
});

test('the delivered intro changes chapters at 8.979, 17.796 and 25.631 seconds', () => {
  assert.deepEqual(piano.cueTimesSeconds.slice(0, 4), [0.767, 8.979, 17.796, 25.631]);
  const player = playback(createChapterSequence(piano.cueTimesSeconds), 0, 0, { source: piano.source });
  for (const [seconds, expected] of [[0.767, 0], [8.979, 1], [17.796, 2], [25.631, 0]]) {
    assert.equal(player.to(seconds - 0.0001), expected === 0 && seconds === 0.767 ? 0 : (expected + 2) % 3, 'the chapter holds until the actual low-piano attack');
    assert.equal(player.to(seconds), expected, `the recorded attack at ${seconds} changes the chapter`);
    assert.equal(player.to(seconds + 0.0001), expected, 'rendering a second frame cannot repeat the cut');
  }
});

test('the quiet recorded outro holds its last chapter without inventing piano notes', () => {
  const player = playback(createChapterSequence(piano.cueTimesSeconds), 0, 0, { source: piano.source });
  const finalCue = piano.cueTimesSeconds.at(-1);
  const expected = (piano.cueTimesSeconds.length - 1) % 3;
  assert.equal(player.to(finalCue + 0.1, 0.05), expected);
  assert.equal(player.to(piano.durationSeconds, 0.05), expected, 'a fixed interval cannot introduce unrecorded chapter transitions');
});
