import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import cues from '../lib/music-cues.json' with { type: 'json' };
import { exhibitSoundtracks } from '../lib/exhibit-soundtracks.mjs';
import { EINSTEIN_CROSSING_SECONDS } from '../lib/einstein-ring.ts';
import { createSceneTransport, musicPosition } from '../lib/music-motion.ts';

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

test('pulse easing moves forward throughout a beat without overshooting its next accent', () => {
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

test('exhibit seven retains its eight-second choreography with actual media progress', () => {
  const transport = createSceneTransport('cadence');
  const position = runTimeline(transport, 8, [0.047, 0.093, 0.17], (now) => sample('science-decays', 42 + now));
  near(position, 8, 'one collision cycle lasts eight playing seconds');
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
