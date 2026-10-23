import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { createImpactSequence } from '../lib/impact-sequence.ts';
import collision from '../lib/collision-cues.json' with { type: 'json' };
import { exhibitSoundtracks } from '../lib/exhibit-soundtracks.mjs';

const cues = [3, 10.8, 19.1, 27];
const music = (seconds, extra = {}) => ({ slideId: 'science-decays', source: './audio/collision-fixture.mp3', seconds, ...extra });
const near = (actual, expected, message) => assert.ok(Math.abs(actual - expected) < 1e-9, `${message}: ${actual} versus ${expected}`);

function playback(sequence, start = 0, wall = 0, extra = {}) {
  let media = start;
  let now = wall;
  let value = sequence.tick(now, music(media, extra));
  return {
    to(target, intervals = [1 / 120]) {
      assert.ok(target >= media, 'ordinary playback moves forward');
      for (let i = 0; media < target; i++) {
        const next = Math.min(target, media + intervals[i % intervals.length]);
        now += next - media;
        media = next;
        value = sequence.tick(now, music(media, extra));
      }
      return value;
    },
    get wall() { return now; },
    get media() { return media; },
  };
}

test('incoming tracks start 1.4 seconds before each measured attack and meet on that attack', () => {
  const player = playback(createImpactSequence(cues));
  for (let i = 0; i < cues.length; i++) {
    const start = cues[i] - 1.4;
    near(player.to(start), i * 8, `incoming approach ${i} begins at the actual cue lead`);
    near(player.to(cues[i] - 0.001), i * 8 + 1.399, 'incoming tracks do not meet before the soundtrack attack');
    near(player.to(cues[i]), i * 8 + 1.4, 'the impact phase lands on the measured attack');
    near(player.to(cues[i] + 0.001), i * 8 + 1.401, 'an attack is not repeated by the following render');
  }
});

test('outgoing tracks retain their 2.2-second reveal and reading holds absorb unequal cue gaps', () => {
  const player = playback(createImpactSequence(cues));
  for (let i = 0; i < cues.length; i++) {
    const impact = player.to(cues[i]);
    near(impact % 8, 1.4, 'impact begins the original outgoing reveal');
    const complete = player.to(cues[i] + 2.2);
    near(complete - i * 8, 3.6, 'outgoing tracks complete after 2.2 playing seconds');
    if (i < cues.length - 1) {
      const nextStart = cues[i + 1] - 1.4;
      const reading = player.to((cues[i] + 2.2 + nextStart) / 2);
      assert.ok(reading > i * 8 + 3.6 && reading < (i + 1) * 8, 'the event stays readable until the next incoming approach');
      near(player.to(nextStart), (i + 1) * 8, 'the next event begins without a phase discontinuity');
    }
  }
});

test('ordinary playback is continuous and independent of render interval or fixed eight-second timers', () => {
  const fine = playback(createImpactSequence(cues));
  const uneven = playback(createImpactSequence(cues));
  for (const target of [0, 1.6, 3, 5.2, 7.6, 9.4, 10.8, 13, 16.2, 17.7, 19.1, 24, 25.6, 27, 31])
    near(uneven.to(target, [0.047, 0.17, 0.29, 0.083]), fine.to(target), `media timestamp ${target} determines the same visible phase`);
  const player = playback(createImpactSequence(cues));
  let previous = 0;
  for (let time = 0.02; time <= 31; time += 0.02) {
    const value = player.to(time);
    assert.ok(value >= previous && value - previous < 0.06, 'variable reading speed remains smooth across each event boundary');
    previous = value;
  }
});

test('first music joins wait for an attack with enough time for the complete incoming approach', () => {
  const sequence = createImpactSequence(cues);
  const player = playback(sequence, 2.2, 7.3);
  assert.equal(player.to(3), 0, 'an attack less than 1.4 seconds away cannot truncate the incoming tracks');
  assert.equal(player.to(9.3999), 0);
  assert.equal(player.to(9.4), 0);
  near(player.to(10.8), 1.4, 'the next eligible recorded attack gets the complete approach');
});

test('starting music resets a partial silent approach before waiting for its recorded impact', () => {
  const sequence = createImpactSequence(cues);
  sequence.tick(0);
  for (let time = 0.125; time <= 3.5; time += 0.125) sequence.tick(time);
  assert.equal(sequence.tick(3.6, music(0.1)), 0);
  const player = playback(sequence, 0.1, 3.6);
  assert.equal(player.to(1.599), 0, 'the incoming tracks wait at their start until the authored lead-in');
  near(player.to(3), 1.4, 'first contact still lands on the recording after a silent preview');
});

test('a stalled recording holds approach, impact and outgoing phases without consuming reading time', () => {
  for (const media of [2, 3, 4.2, 7]) {
    const sequence = createImpactSequence(cues);
    const player = playback(sequence);
    const before = player.to(media);
    for (let frame = 1; frame <= 30; frame++)
      assert.equal(sequence.tick(player.wall + frame * 0.1, music(media)), before, 'elapsed wall time cannot advance a stalled recording');
    const resumed = playback(sequence, media, player.wall + 3);
    assert.ok(resumed.to(media + 0.1) > before, 'only newly played audio resumes motion');
  }
});

test('pausing music holds the inspected event and resumes with a full future approach', () => {
  const sequence = createImpactSequence(cues);
  const player = playback(sequence);
  const before = player.to(4);
  for (let frame = 1; frame <= 110; frame++)
    assert.equal(sequence.tick(player.wall + frame * 0.1), before, 'music pause cannot start a replacement event timer');
  const resumed = playback(sequence, 4, 15);
  assert.equal(resumed.to(9.3999), before);
  assert.equal(resumed.to(9.4), 0, 'the same event begins its full approach again');
  near(resumed.to(10.8), 1.4, 'resume does not skip the inspected event');
});

test('offscreen suspension and long scheduler gaps discard unseen impacts', () => {
  for (const suspend of [false, true]) {
    const sequence = createImpactSequence(cues);
    const player = playback(sequence);
    const before = player.to(11.3);
    assert.equal(Math.floor(before / 8), 1);
    if (suspend) sequence.suspend();
    assert.equal(sequence.tick(100, music(20)), before, 'returning holds the inspected event despite an unheard attack');
    const resumed = playback(sequence, 20, 100);
    assert.equal(resumed.to(25.5999), before);
    assert.equal(resumed.to(25.6), 8, 'the next eligible attack restarts the current event approach');
    near(resumed.to(27), 9.4, 'unseen events cannot advance the playlist');
  }
});

test('seeking and audio-source changes rebase the attack cursor without firing crossed cues', () => {
  for (const change of [
    { seconds: 15, seeking: true },
    { seconds: 15 },
    { seconds: 15, source: './audio/reloaded-collision-fixture.mp3' },
  ]) {
    const sequence = createImpactSequence(cues);
    const player = playback(sequence);
    const before = player.to(4);
    assert.equal(sequence.tick(4.1, music(change.seconds, change)), before);
    if (change.seeking)
      assert.equal(sequence.tick(4.2, music(change.seconds, change)), before, 'successive seeking frames hold');
    const resumed = playback(sequence, change.seconds, 4.3, { source: change.source ?? './audio/collision-fixture.mp3' });
    assert.equal(resumed.to(17.6999), before);
    near(resumed.to(cues[2] - 1.4), 0, 'the complete incoming approach starts at its cue-relative boundary');
    near(resumed.to(19.1), 1.4, 'the next heard eligible attack advances only the inspected event');
  }
});

test('natural audio loops re-arm the opening attacks while retaining the current event', () => {
  const sequence = createImpactSequence(cues);
  const player = playback(sequence);
  const before = player.to(21);
  assert.equal(Math.floor(before / 8), 2);
  assert.equal(sequence.tick(player.wall + 0.05, music(0.05)), before);
  const loop = playback(sequence, 0.05, player.wall + 0.05);
  assert.equal(loop.to(1.5999), before);
  assert.equal(loop.to(1.6), 16);
  near(loop.to(3), 17.4, 'looping neither invents an impact nor jumps the event playlist');
});

test('mid-song replay returns to event zero and waits for a complete approach to a future attack', () => {
  const sequence = createImpactSequence(cues);
  const player = playback(sequence);
  player.to(15);
  sequence.restart();
  const replay = playback(sequence, 15, 30);
  assert.equal(replay.to(17.6999), 0);
  near(replay.to(cues[2] - 1.4), 0, 'replay starts the incoming approach at its cue-relative boundary');
  near(replay.to(19.1), 1.4, 'replay follows a real future attack rather than a reset timer');
});

test('the quiet outro holds the last event without inventing more soundtrack impacts', () => {
  const player = playback(createImpactSequence(cues));
  const held = player.to(35);
  assert.equal(Math.floor(held / 8), cues.length - 1);
  assert.ok(held % 8 > 3.6, 'the last outgoing tracks remain fully visible');
  assert.equal(player.to(120), held);
  const lateJoin = playback(createImpactSequence(cues), 30);
  assert.equal(lateJoin.to(120), 0, 'joining after all recorded attacks cannot fabricate a collision');
});

test('a silent first visit retains the original eight-unit loop until music is used', () => {
  const sequence = createImpactSequence(cues);
  assert.equal(sequence.tick(0), 0);
  for (let time = 0.125; time <= 16; time += 0.125)
    near(sequence.tick(time), time, 'silent presentation advances at its original speed');
  assert.equal(sequence.tick(16.1, music(0.1)), 16);
  for (let time = 16.2; time < 28; time += 0.1)
    assert.equal(sequence.tick(time), 16, 'after music engagement a pause holds the event rather than replacing the soundtrack cues');
});

test('recorded collision accents identify the exact delivered soundtrack and retain attack evidence', async () => {
  const track = exhibitSoundtracks.find((item) => item.slideId === 'science-decays');
  const bytes = await readFile(new URL(`../public/${track.source.slice(2)}`, import.meta.url));
  assert.equal(collision.slideId, track.slideId);
  assert.equal(collision.trackTitle, track.title);
  assert.equal(collision.source, track.source);
  assert.equal(collision.audioSha256, track.sha256);
  assert.equal(createHash('sha256').update(bytes).digest('hex'), collision.audioSha256);
  assert.ok(Math.abs(collision.durationSeconds - track.durationSeconds) < 0.1, 'ordinary MP3 padding cannot change the attack timeline');
  assert.equal(collision.fixedTempoBpm, null, 'actual recorded attacks replace an assumed metronome');
  assert.equal(collision.selectedAttackEvidence.length, collision.impactTimesSeconds.length);
  assert.ok(collision.minimumCueGapSeconds > 1.4 + 2.2, 'every gap leaves time for approach, reveal and inspection');
  collision.impactTimesSeconds.forEach((seconds, i) => {
    assert.ok(Number.isFinite(seconds) && seconds >= 1.4 && seconds + 2.2 < collision.durationSeconds);
    if (i > 0) assert.ok(seconds - collision.impactTimesSeconds[i - 1] >= collision.minimumCueGapSeconds);
    const attack = collision.selectedAttackEvidence[i];
    assert.equal(attack.timeSeconds, seconds);
    assert.ok(attack.fivePercentRiseSeconds <= seconds && seconds <= attack.twentyPercentRiseSeconds);
    assert.ok(attack.twentyPercentRiseSeconds <= attack.riseCrestSeconds, 'impact starts at the recorded attack rather than its later energy crest');
    assert.ok(attack.normalizedAttackStrength > 0);
  });
});

test('all delivered collision impacts meet on their recorded accents with a full approach and outgoing reveal', () => {
  assert.deepEqual(collision.impactTimesSeconds.slice(0, 5), [8.892, 16.784, 24.64, 32.441, 40.21]);
  const player = playback(createImpactSequence(collision.impactTimesSeconds), 0, 0, { source: collision.source });
  assert.equal(player.to(collision.impactTimesSeconds[0] - 1.4 - 0.001), 0, 'the opening cannot invent an early collision');
  collision.impactTimesSeconds.forEach((seconds, i) => {
    near(player.to(seconds - 1.4, [0.05]), i * 8, `recorded event ${i} starts the full incoming approach`);
    near(player.to(seconds - 0.001), i * 8 + 1.399, 'incoming tracks remain separated until the attack');
    near(player.to(seconds), i * 8 + 1.4, `recorded impact ${i} lands at ${seconds} seconds`);
    near(player.to(seconds + 2.2), i * 8 + 3.6, 'the full outgoing reveal survives variable soundtrack spacing');
  });
});

test('the delivered quiet outro holds the final measured collision without synthetic repeats', () => {
  const player = playback(createImpactSequence(collision.impactTimesSeconds), 0, 0, { source: collision.source });
  const held = player.to(collision.impactTimesSeconds.at(-1) + 9, [0.05]);
  assert.equal(Math.floor(held / 8), collision.impactTimesSeconds.length - 1);
  assert.ok(held % 8 > 3.6, 'the final outgoing event remains visible');
  assert.equal(player.to(collision.durationSeconds, [0.05]), held);
});
