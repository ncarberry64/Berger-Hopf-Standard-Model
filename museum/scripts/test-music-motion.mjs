import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import cues from '../lib/music-cues.json' with { type: 'json' };
import { exhibitSoundtracks } from '../lib/exhibit-soundtracks.mjs';
import { EINSTEIN_CROSSING_SECONDS } from '../lib/einstein-ring.ts';
import { createPhraseSequence, createSceneTransport, musicBeat, musicPosition } from '../lib/music-motion.ts';

const highTracks = Object.entries(cues.tracks).filter(([, cue]) => cue.confidence === 'high');
const ambientTracks = Object.entries(cues.tracks).filter(([, cue]) => cue.confidence !== 'high');
const near = (actual, expected, message) => assert.ok(Math.abs(actual - expected) < 1e-9, `${message}: ${actual} versus ${expected}`);
const sample = (slideId, seconds, extra = {}) => ({ slideId, source: `./audio/${slideId}.mp3`, seconds, ...extra });

function runTimeline(transport, duration, pattern, musicAt, stopAt) {
  let now = 0;
  let position = transport.tick(0, musicAt?.(0), stopAt);
  for (let i = 0; now < duration; i++) {
    now = Math.min(duration, now + pattern[i % pattern.length]);
    position = transport.tick(now, musicAt?.(now), stopAt);
  }
  return position;
}

test('every delivered soundtrack has cues measured from its exact audio bytes', async () => {
  assert.deepEqual(Object.keys(cues.tracks).sort(), exhibitSoundtracks.map((track) => track.slideId).sort());
  for (const track of exhibitSoundtracks) {
    const cue = cues.tracks[track.slideId];
    const bytes = await readFile(new URL(`../public/${track.source.slice(2)}`, import.meta.url));
    assert.equal(cue.audioSha256, track.sha256, `${track.slideId} manifest and cues agree`);
    assert.equal(createHash('sha256').update(bytes).digest('hex'), cue.audioSha256, `${track.slideId} cues describe the delivered recording`);
    assert.ok(cue.energyStepSeconds > 0 && cue.energy.length > 2);
    assert.ok(cue.energy.every((value) => Number.isFinite(value) && value >= 0 && value <= 1));
    assert.ok(Math.abs((cue.energy.length - 1) * cue.energyStepSeconds - cue.durationSeconds) <= cue.energyStepSeconds);
    assert.ok(Math.abs(cue.durationSeconds - track.durationSeconds) < 0.1, 'decode padding cannot shift the timeline by an audible interval');
  }
});

test('only trustworthy pulse grids place each measured beat on a half-second scene accent', () => {
  assert.ok(highTracks.length > 0 && ambientTracks.length > 0, 'exercise both musical treatments');
  for (const [id, cue] of highTracks) {
    assert.ok(cue.tempoBpm > 0 && cue.beatOffsetSeconds >= 0);
    near(musicPosition(id, 0).position, 0, `${id} starts before its first onset`);
    for (const beat of [0, 1, 2, 4, 16, 64]) {
      const coordinate = musicPosition(id, cue.beatOffsetSeconds + beat * 60 / cue.tempoBpm);
      assert.equal(coordinate.grid, true);
      near(coordinate.position, beat / 2, `${id} beat ${beat}`);
    }
  }
  for (const [id] of ambientTracks) assert.equal(musicPosition(id, 30).grid, false, `${id} must not invent a steady pulse`);
});

test('the linear pulse clock moves forward throughout a beat without overshooting its next accent', () => {
  for (const [id, cue] of highTracks) {
    let previous = 2;
    for (let frame = 1; frame <= 120; frame++) {
      const time = cue.beatOffsetSeconds + (4 + frame / 120) * 60 / cue.tempoBpm;
      const next = musicPosition(id, time).position;
      assert.ok(next > previous && next <= 2.5 + 1e-12, `${id} must remain smooth and monotone`);
      previous = next;
    }
    near(previous, 2.5, `${id} lands on the following beat`);
  }
});

test('raw musical phase preserves the first onset and remains on the recording after a minute', () => {
  assert.equal(musicBeat('missing-exhibit', 20), null);
  for (const [id] of ambientTracks) assert.equal(musicBeat(id, 20), null, `${id} has no reliable beat phase`);
  for (const [id, cue] of highTracks) {
    const onset = musicBeat(id, cue.beatOffsetSeconds);
    assert.equal(onset.tempoBpm, cue.tempoBpm);
    near(onset.beat, 0, `${id} first measured attack`);
    assert.ok(musicBeat(id, 0).beat < 0, 'pre-onset phase must not be clamped into an early attack');
    const minute = musicBeat(id, cue.beatOffsetSeconds + 60);
    near(minute.beat, cue.tempoBpm, `${id} has no phase drift after sixty playing seconds`);
    const laterOnset = musicBeat(id, cue.beatOffsetSeconds + 137 * 60 / cue.tempoBpm);
    near(laterOnset.beat, 137, `${id} later attacks still have integer phase`);
  }
});

test('reading sequences launch at an actual four-beat bar despite an unrelated local clock', () => {
  const sequence = createPhraseSequence(8);
  assert.equal(sequence.tick(7.3, 40.8), 0);
  assert.equal(sequence.tick(8, 41.6), 0, 'a local two-second boundary cannot launch an offbeat chapter');
  assert.equal(sequence.tick(9, 43.2), 0);
  assert.equal(sequence.tick(9.3, 43.99), 0);
  assert.equal(sequence.tick(9.31, 44), 0, 'the next actual bar launches at beat 44');
  near(sequence.tick(9.9, 45), 0.5, 'progress comes from the playing beat after launch');
});

test('continuous chapter changes land every sixteen audible beats without local-clock drift', () => {
  const sequence = createPhraseSequence(8);
  sequence.tick(7.3, 40.8);
  sequence.tick(8, 42);
  sequence.tick(8.1, 44);
  for (let halfBeat = 1; halfBeat <= 96; halfBeat++) {
    const beat = 44 + halfBeat / 2;
    const position = sequence.tick(8.1 + halfBeat * 0.173, beat);
    near(position, halfBeat / 4, `reading sequence at beat ${beat}`);
    if (halfBeat % 32 === 0) {
      near(position % 8, 0, 'each chapter starts exactly on its sixteen-beat phrase');
      assert.equal(Math.floor(position / 8), halfBeat / 32);
    }
  }
});

test('buffering holds both an upcoming phrase launch and an active chapter', () => {
  const sequence = createPhraseSequence(8);
  assert.equal(sequence.tick(10, 40.8), 0);
  for (const time of [10.1, 11, 15, 20])
    assert.equal(sequence.tick(time, 40.8), 0, 'waiting for the bar follows media rather than wall time');
  sequence.tick(20.1, 42);
  sequence.tick(20.2, 44);
  assert.equal(sequence.tick(20.3, 45), 0.5);
  for (const time of [21, 25, 30])
    assert.equal(sequence.tick(time, 45), 0.5, 'a stalled recording cannot consume the reading interval');
  assert.equal(sequence.tick(30.1, 46), 1);
});

test('suspension, skipped audio and looping repeat the current entry at a fresh bar rather than skipping it', () => {
  for (const interruption of ['suspend', 'seek', 'loop']) {
    const sequence = createPhraseSequence(8);
    sequence.tick(0, 0);
    for (let beat = 1; beat <= 21; beat++) sequence.tick(beat / 2, beat);
    if (interruption === 'suspend') sequence.suspend();
    const arrival = interruption === 'loop' ? 1.2 : 200.8;
    const bar = interruption === 'loop' ? 4 : 204;
    assert.equal(sequence.tick(100, arrival), 10.5, `${interruption} preserves the inspected point until the fresh bar`);
    sequence.tick(100.1, arrival + 1);
    assert.equal(sequence.tick(100.2, bar - 0.01), 10.5, 'unseen music does not advance to a different entry');
    assert.equal(sequence.tick(100.3, bar), 8, 'the current entry starts again at the next actual bar');
    assert.equal(sequence.tick(100.4, bar + 1), 8.5);
    assert.equal(Math.floor(sequence.tick(100.5, bar + 2) / 8), 1, 'the same entry remains readable');
  }
});

test('replay restarts on the next actual bar and silent sequences retain a usable presentation clock', () => {
  const sequence = createPhraseSequence(8);
  sequence.tick(0, 0);
  for (let beat = 1; beat <= 21; beat++) sequence.tick(beat / 2, beat);
  sequence.restart();
  assert.equal(sequence.tick(71.3, 103.1), 0);
  assert.equal(sequence.tick(72, 103.8), 0, 'an unrelated local bar cannot restart the reading sequence');
  assert.equal(sequence.tick(72.3, 104), 0);
  assert.equal(sequence.tick(72.4, 104.5), 0.25);

  const silent = createPhraseSequence(8);
  assert.equal(silent.tick(1, null), 0);
  assert.equal(silent.tick(1.5, null), 0.5);
  assert.equal(silent.tick(9.5, null), 8.5);
  silent.suspend();
  assert.equal(silent.tick(100, null), 8.5, 'returning to a silent scene discards unseen wall time');
  assert.equal(silent.tick(100.25, null), 8.75);
  assert.equal(silent.tick(100.3, 40.8), 8.75, 'starting music holds the current entry until an actual bar');
  silent.tick(100.4, 42);
  assert.equal(silent.tick(100.5, 44), 8, 'music joins by repeating the current entry, preserving reading time');
});

test('ambient choreography follows recorded swells while remaining monotone and preserving average speed', () => {
  for (const [id, cue] of ambientTracks) {
    let previous = musicPosition(id, 0).position;
    const advances = [];
    for (let frame = 1; frame < cue.energy.length; frame++) {
      const next = musicPosition(id, frame * cue.energyStepSeconds).position;
      assert.ok(next > previous, `${id} cannot rewind during a quiet passage`);
      advances.push((next - previous) / cue.energyStepSeconds);
      previous = next;
    }
    assert.ok(Math.max(...advances) - Math.min(...advances) > 0.05, `${id} actually changes rate with its waveform`);
    near(previous, (cue.energy.length - 1) * cue.energyStepSeconds, `${id} retains its overall presentation duration`);
  }
});

test('a stopped or buffering recording cannot advance the synchronized scene', () => {
  for (const [id, cue] of [highTracks[0], ambientTracks[0]]) {
    const transport = createSceneTransport();
    const start = cue.confidence === 'high' ? cue.beatOffsetSeconds : 0;
    runTimeline(transport, 1, [0.05], (now) => sample(id, start + now));
    const held = transport.tick(1.1, sample(id, start + 1));
    for (let frame = 2; frame <= 20; frame++)
      assert.equal(transport.tick(1 + frame / 10, sample(id, start + 1)), held);
    const resumed = transport.tick(3.1, sample(id, start + 1.1));
    assert.ok(resumed > held && resumed - held < 0.2, 'resuming follows new audio progress without catching up elapsed wall time');
  }
});

test('different scheduler intervals reach the same musical position', () => {
  for (const [id, cue] of [highTracks[0], ambientTracks[0]]) {
    const start = cue.confidence === 'high' ? cue.beatOffsetSeconds : 0;
    const musicAt = (now) => sample(id, start + now);
    const fine = runTimeline(createSceneTransport(), 24, [1 / 120], musicAt);
    const uneven = runTimeline(createSceneTransport(), 24, [0.041, 0.17, 0.087, 0.32], musicAt);
    near(uneven, fine, `${id} is driven by playback position rather than callback count`);
    near(fine, musicPosition(id, start + 24).position - musicPosition(id, start).position, `${id} retains its soundtrack coordinate`);
  }
});

test('seeks, loops, and source or exhibit changes re-anchor without jumps or backwards motion', () => {
  for (const change of [
    (s) => ({ ...s, seconds: 120, seeking: true }),
    (s) => ({ ...s, seconds: 120 }),
    (s) => ({ ...s, seconds: 0 }),
    (s) => ({ ...s, source: './audio/replacement.mp3', seconds: 15 }),
    (s) => ({ ...s, slideId: 'details', seconds: 15 }),
  ]) {
    const transport = createSceneTransport();
    const [id, cue] = highTracks[0];
    const at = (now) => sample(id, cue.beatOffsetSeconds + now);
    const before = runTimeline(transport, 3, [0.05], at);
    const changed = change(at(3));
    assert.equal(transport.tick(3.05, changed), before, 'discontinuity itself holds the current scene');
    if (changed.seeking) {
      assert.equal(transport.tick(3.1, { ...changed, seconds: changed.seconds + 10 }), before, 'all seeking events hold');
      changed.seconds += 10;
    }
    const resumed = transport.tick(3.15, { ...changed, seconds: changed.seconds + 0.05, seeking: false });
    assert.ok(resumed >= before && resumed - before < 0.15, 'the next ordinary sample joins gently');
  }
});

test('manual suspension preserves inspection position and discards unseen music progress', () => {
  const transport = createSceneTransport();
  const id = highTracks[0][0];
  const before = runTimeline(transport, 4, [0.1], (now) => sample(id, now));
  transport.suspend();
  assert.equal(transport.tick(100, sample(id, 100)), before);
  const resumed = transport.tick(100.1, sample(id, 100.1));
  assert.ok(resumed > before && resumed - before < 0.2);
});

test('long hidden-tab gaps never fast-forward the reveal', () => {
  for (const withMusic of [false, true]) {
    const transport = createSceneTransport();
    const musicAt = withMusic ? (now) => sample('blackhole-tracker', now) : undefined;
    const before = runTimeline(transport, 2, [0.1], musicAt);
    assert.equal(transport.tick(60, musicAt?.(60)), before);
    const resumed = transport.tick(60.1, musicAt?.(60.1));
    assert.ok(resumed >= before && resumed - before <= 0.101, 'returning cannot consume the elapsed hidden minute');
  }
});

test('the Einstein ring annotation stops at exact alignment and stays there', () => {
  const alignment = EINSTEIN_CROSSING_SECONDS / 2;
  assert.equal(alignment, 9);
  const transport = createSceneTransport();
  const held = runTimeline(transport, 20, [0.037, 0.113, 0.071], (now) => sample('blackhole-tracker', now), alignment);
  assert.equal(held, alignment, 'measurement arrows must describe exact source alignment');
  assert.equal(transport.tick(20.1, sample('blackhole-tracker', 20.1), alignment), alignment);
  transport.suspend();
  assert.equal(transport.tick(40, sample('blackhole-tracker', 40), alignment), alignment);
});

test('cadence transport retains media seconds for authored presentation sequences', () => {
  const transport = createSceneTransport('cadence');
  const position = runTimeline(transport, 8, [0.047, 0.093, 0.17], (now) => sample('science-decays', 42 + now));
  near(position, 8, 'cadence advances by eight actually played seconds');
  for (const [id] of highTracks) {
    const coordinate = musicPosition(id, 8, 'cadence');
    assert.equal(coordinate.grid, false);
    assert.equal(coordinate.position, 8, 'cadence does not retime the established cycle to another tempo');
  }
});

test('silent fallback and independent scenes keep their wall-time presentation speed', () => {
  const silent = runTimeline(createSceneTransport(), 8, [0.06, 0.14, 0.23]);
  near(silent, 8, 'silence does not prevent animation');
  const independent = runTimeline(createSceneTransport('independent'), 8, [0.06, 0.14, 0.23], (now) => sample('details', now * 3));
  near(independent, 8, 'independent scientific clocks ignore soundtrack speed');
  assert.deepEqual(musicPosition('missing-exhibit', 8), { position: 8, grid: false });
});
