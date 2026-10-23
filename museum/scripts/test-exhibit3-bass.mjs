import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import bass from '../lib/exhibit3-bass.json' with { type: 'json' };
import { exhibitSoundtracks } from '../lib/exhibit-soundtracks.mjs';
import { bergerMotion } from '../lib/berger-motion.ts';
import { bergerLevel, hopfBase, hopfPoint } from '../lib/berger-hopf.ts';
import {
  createSceneTransport,
  exhibit3BassPosition,
  exhibit3BassSpeed,
  musicPosition,
} from '../lib/music-motion.ts';

const near = (actual, expected, message, tolerance = 1e-9) =>
  assert.ok(Math.abs(actual - expected) < tolerance, `${message}: ${actual} versus ${expected}`);
const span = (bass.energy.length - 1) * bass.energyStepSeconds;
const sample = (seconds, extra = {}) => ({ slideId: 'berger-hopf', source: bass.source, seconds, ...extra });

function play(transport, start, duration, intervals) {
  let wall = 0;
  let position = transport.tick(wall, sample(start));
  for (let i = 0; wall < duration; i++) {
    wall = Math.min(duration, wall + intervals[i % intervals.length]);
    position = transport.tick(wall, sample(start + wall));
  }
  return position;
}

test('exhibit three uses a measured low-frequency envelope from its delivered recording', async () => {
  const track = exhibitSoundtracks.find((item) => item.slideId === 'berger-hopf');
  const bytes = await readFile(new URL(`../public/${track.source.slice(2)}`, import.meta.url));
  assert.equal(bass.slideId, track.slideId);
  assert.equal(bass.source, track.source);
  assert.equal(bass.audioSha256, track.sha256);
  assert.equal(createHash('sha256').update(bytes).digest('hex'), bass.audioSha256);
  assert.deepEqual(bass.bassBandHz, [30, 160]);
  assert.equal(bass.fixedTempoBpm, null, 'actual bass energy replaces a fixed-tempo assumption for this exhibit');
  assert.ok(bass.energy.every((value) => Number.isFinite(value) && value >= 0 && value <= 1));
  assert.ok(Math.abs(span - bass.durationSeconds) < bass.energyStepSeconds);
});

test('motion speeds up at measured bass peaks and relaxes in measured quiet passages', () => {
  const ranked = bass.energy.map((energy, i) => ({ energy, time: i * bass.energyStepSeconds })).sort((a, b) => a.energy - b.energy);
  const quiet = ranked[Math.floor(ranked.length * 0.05)];
  const peak = ranked[Math.floor(ranked.length * 0.95)];
  assert.ok(peak.energy - quiet.energy > 0.5, 'the recording contains a meaningful bass contrast');
  assert.ok(exhibit3BassSpeed(peak.time) > exhibit3BassSpeed(quiet.time) + 0.5, 'the audible bass contrast changes the animation speed');
  for (let i = 1; i < ranked.length; i += 31) {
    const time = ranked[i].time + bass.energyStepSeconds / 3;
    if (time >= span) continue;
    const epsilon = 1e-5;
    const measuredRate = (exhibit3BassPosition(time + epsilon) - exhibit3BassPosition(time - epsilon)) / (2 * epsilon);
    near(measuredRate, exhibit3BassSpeed(time), 'the speed is the derivative of the displayed animation clock', 1e-5);
  }
});

test('the bass clock remains positive and continuous across every measured envelope boundary', () => {
  assert.equal(exhibit3BassPosition(-10), 0);
  assert.equal(exhibit3BassPosition(0), 0);
  let previous = 0;
  const epsilon = 1e-7;
  for (let i = 1; i < bass.energy.length; i++) {
    const time = i * bass.energyStepSeconds;
    const position = exhibit3BassPosition(time);
    assert.ok(position > previous, 'quiet bass cannot freeze or reverse the animation');
    assert.ok(exhibit3BassSpeed(time) > 0 && exhibit3BassSpeed(time) < 3, 'bass has a bounded forward presentation speed');
    assert.ok(exhibit3BassPosition(time + epsilon) - exhibit3BassPosition(time - epsilon) < epsilon * 6, 'sample boundaries cannot cause position jumps');
    previous = position;
  }
  near(previous, span, 'bass changes local speed while preserving the overall presentation duration');
  near(exhibit3BassPosition(span + 12), span + 12, 'motion continues smoothly after the measured recording');
});

test('bass mode follows the measured clock without a whole-beat grid or callback-rate drift', () => {
  const time = 19.37;
  assert.deepEqual(musicPosition('berger-hopf', time, 'bass'), { position: exhibit3BassPosition(time), grid: false });
  const fine = play(createSceneTransport('bass'), 17.3, 20, [1 / 120]);
  const irregular = play(createSceneTransport('bass'), 17.3, 20, [0.037, 0.19, 0.11, 0.27]);
  near(irregular, fine, 'unequal browser scheduling cannot change the bass response');
  near(fine, exhibit3BassPosition(37.3) - exhibit3BassPosition(17.3), 'only recorded bass progress advances the scene');
  assert.deepEqual(musicPosition('details', time, 'bass'), { position: time, grid: false }, 'the exhibit-three bass recording cannot retime another exhibit');
});

test('buffering and manual pause hold the native visual phase without a bass catch-up jump', () => {
  const transport = createSceneTransport('bass');
  const before = play(transport, 17.3, 2, [0.05]);
  const visual = bergerMotion(before, before, 1);
  for (const wall of [2.1, 2.3, 2.5, 2.7]) {
    const held = transport.tick(wall, sample(19.3));
    assert.equal(held, before);
    assert.deepEqual(bergerMotion(held, held, 1), visual, 'buffering keeps the existing native orbit and metric phase');
  }
  transport.suspend();
  const held = transport.tick(100, sample(120));
  assert.equal(held, before);
  assert.deepEqual(bergerMotion(held, held, 1), visual, 'inspection pauses preserve the drawing');
  const resumed = transport.tick(100.1, sample(120.1));
  near(resumed - held, exhibit3BassPosition(120.1) - exhibit3BassPosition(120), 'resuming consumes only newly played bass');
});

test('scrubbing, looping and source changes preserve native phase then join the new bass speed', () => {
  for (const change of [
    { seconds: 120, seeking: true },
    { seconds: 1 },
    { seconds: 0 },
    { seconds: 50, source: './audio/reloaded-recording.mp3' },
  ]) {
    const transport = createSceneTransport('bass');
    const before = play(transport, 17.3, 2, [0.05]);
    const visual = bergerMotion(before, before, 2);
    const current = sample(change.seconds, change);
    const held = transport.tick(2.1, current);
    assert.equal(held, before, 'a discontinuous media timestamp does not relocate the animation');
    assert.deepEqual(bergerMotion(held, held, 2), visual);
    const after = transport.tick(2.2, { ...current, seconds: current.seconds + 0.1, seeking: false });
    near(after - held, exhibit3BassPosition(current.seconds + 0.1) - exhibit3BassPosition(current.seconds), 'the next audio interval sets speed without resetting phase');
  }
});

test('bass changes the common speed while retaining the original Berger and Hopf motion', () => {
  const time = exhibit3BassPosition(19.37), elapsed = 2.4;
  for (const stage of [0, 1, 2]) {
    const motion = bergerMotion(time, elapsed, stage);
    near(motion.orbit, time * (stage === 2 ? 1.1 : 0.65), 'the native orbit keeps its original angular relationship');
    near(motion.angle, time * 0.12 + 0.55, 'camera rotation shares the same speed control');
    near(motion.fiberScale, 1 + 0.3 * Math.sin(elapsed * 0.65), 'metric deformation retains its native smooth cycle');
    near(motion.dashOffset, -time * 12, 'the original moving pathway shares the same clock');
    assert.equal(motion.accent, undefined, 'bass does not add a separate pulsing light effect');
  }
});

test('bass-driven native motion preserves the Hopf map and the existing metric calculation', () => {
  const eta = 0.58, phi = Math.PI;
  const expectedBase = hopfBase(hopfPoint(eta, phi, 0));
  for (const seconds of [0, 0.82, 17.85, 50.17, 129.6, 186.76, 231]) {
    const time = exhibit3BassPosition(seconds);
    for (const stage of [0, 1, 2]) {
      const motion = bergerMotion(time, time, stage);
      const point = hopfPoint(eta, phi, motion.orbit);
      near(point.reduce((sum, value) => sum + value * value, 0), 1, 'the moving point remains on S3');
      hopfBase(point).forEach((value, axis) => near(value, expectedBase[axis], `the Hopf base point remains fixed on axis ${axis}`));
      near(bergerLevel(2, 0, motion.fiberScale), 4 / motion.fiberScale ** 2 + 4, 'the Berger level uses the existing geometric spectrum rule');
    }
  }
});
