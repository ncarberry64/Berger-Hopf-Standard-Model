import assert from 'node:assert/strict';
import test from 'node:test';
import {
  lifecycleFrame,
  lifecycleOffset,
  lifecycleSceneDurations,
  lifecycleScaleDuration,
} from '../lib/lifecycle-tour.ts';

const stageStarts = [0, 6, 12, 18, 28, 34];
const expectedDurations = [6, 6, 6, 10, 6, 6];
const epsilon = 0.000001;

function closeTo(actual, expected, description) {
  assert.ok(
    Math.abs(actual - expected) < 1e-9,
    `${description}: expected ${expected}, received ${actual}`,
  );
}

test('the reading tour has six primary scenes and forty seconds per scale', () => {
  assert.deepEqual([...lifecycleSceneDurations], expectedDurations);
  assert.equal(lifecycleScaleDuration, 40);
});

test('continuous playback visits all six scenes at all four scales', () => {
  const visited = new Set();
  for (let seconds = 0; seconds < 160; seconds += 0.5) {
    const frame = lifecycleFrame(seconds);
    assert.ok(Number.isInteger(frame.stage) && frame.stage >= 0 && frame.stage < 6);
    assert.ok(Number.isInteger(frame.scale) && frame.scale >= 0 && frame.scale < 4);
    assert.ok(frame.progress >= 0 && frame.progress < 1);
    visited.add(`${frame.scale}:${frame.stage}`);
  }

  assert.equal(visited.size, 24, 'every scale must receive the complete tour');
  for (let scale = 0; scale < 4; scale += 1) {
    for (let stage = 0; stage < 6; stage += 1) {
      assert.ok(visited.has(`${scale}:${stage}`));
      const midpoint = lifecycleFrame(scale * 40 + stageStarts[stage] + expectedDurations[stage] / 2);
      assert.equal(midpoint.scale, scale);
      assert.equal(midpoint.stage, stage);
      closeTo(midpoint.progress, 0.5, `scale ${scale}, stage ${stage} midpoint`);
    }
  }
});

test('each exact scene boundary begins the next scene with fresh progress', () => {
  for (let scale = 0; scale < 4; scale += 1) {
    for (let stage = 1; stage < 6; stage += 1) {
      const boundary = scale * 40 + stageStarts[stage];
      const before = lifecycleFrame(boundary - epsilon);
      const at = lifecycleFrame(boundary);
      const after = lifecycleFrame(boundary + epsilon);
      assert.equal(before.scale, scale);
      assert.equal(before.stage, stage - 1);
      assert.ok(before.progress > 0.9999);
      assert.equal(at.scale, scale);
      assert.equal(at.stage, stage);
      assert.equal(at.progress, 0);
      assert.equal(after.stage, stage);
      assert.ok(after.progress > 0 && after.progress < 0.0001);
    }
  }
});

test('daughter products appear within decay, without a seventh peer scene', () => {
  for (let scale = 0; scale < 4; scale += 1) {
    const revealTime = scale * 40 + 22;
    const before = lifecycleFrame(revealTime - epsilon);
    const at = lifecycleFrame(revealTime);
    const after = lifecycleFrame(revealTime + epsilon);
    assert.equal(before.stage, 3);
    assert.equal(before.daughtersVisible, false);
    assert.equal(at.stage, 3);
    closeTo(at.progress, 0.4, `scale ${scale} daughter reveal`);
    assert.equal(at.daughtersVisible, true);
    assert.equal(after.stage, 3);
    assert.equal(after.daughtersVisible, true);
    assert.equal(lifecycleFrame(scale * 40 + 28 - epsilon).daughtersVisible, true);
    assert.equal(lifecycleFrame(scale * 40 + 28).daughtersVisible, false);

    for (const stage of [0, 1, 2, 4, 5]) {
      const frame = lifecycleFrame(scale * 40 + stageStarts[stage] + expectedDurations[stage] * 0.8);
      assert.equal(frame.daughtersVisible, false, `daughters are not a separate scene at stage ${stage}`);
    }
  }
});

test('scale boundaries advance from de-encapsulation to the next excitation', () => {
  for (let scale = 1; scale < 4; scale += 1) {
    const before = lifecycleFrame(scale * 40 - epsilon);
    const at = lifecycleFrame(scale * 40);
    assert.equal(before.scale, scale - 1);
    assert.equal(before.stage, 5);
    assert.ok(before.progress > 0.9999);
    assert.deepEqual(at, { scale, stage: 0, progress: 0, daughtersVisible: false });
  }
});

test('the complete four-scale tour wraps cleanly and preserves later cycle positions', () => {
  const last = lifecycleFrame(160 - epsilon);
  assert.equal(last.scale, 3);
  assert.equal(last.stage, 5);
  assert.ok(last.progress > 0.9999);
  const start = { scale: 0, stage: 0, progress: 0, daughtersVisible: false };
  assert.deepEqual(lifecycleFrame(0), start);
  assert.deepEqual(lifecycleFrame(160), start);
  assert.deepEqual(lifecycleFrame(320), start);

  for (const offset of [0.25, 6, 22, 39.75, 80, 119.5, 159.5]) {
    const initial = lifecycleFrame(offset);
    const repeated = lifecycleFrame(320 + offset);
    assert.equal(repeated.scale, initial.scale);
    assert.equal(repeated.stage, initial.stage);
    assert.equal(repeated.daughtersVisible, initial.daughtersVisible);
    closeTo(repeated.progress, initial.progress, `wrapped offset ${offset}`);
  }
});

test('manual scale and scene offsets land at the requested start by default', () => {
  for (let scale = 0; scale < 4; scale += 1) {
    for (let stage = 0; stage < 6; stage += 1) {
      const offset = lifecycleOffset(scale, stage);
      assert.equal(offset, scale * 40 + stageStarts[stage]);
      const frame = lifecycleFrame(offset);
      assert.equal(frame.scale, scale);
      assert.equal(frame.stage, stage);
      assert.equal(frame.progress, 0);
      assert.equal(frame.daughtersVisible, false);
    }
  }
});

test('manual offsets round-trip progress throughout each scene and scale', () => {
  for (let scale = 0; scale < 4; scale += 1) {
    for (let stage = 0; stage < 6; stage += 1) {
      for (const progress of [0, 0.125, 0.4, 0.75, 0.999]) {
        const offset = lifecycleOffset(scale, stage, progress);
        closeTo(offset, scale * 40 + stageStarts[stage] + expectedDurations[stage] * progress, 'absolute scene offset');
        const frame = lifecycleFrame(offset);
        assert.equal(frame.scale, scale);
        assert.equal(frame.stage, stage);
        closeTo(frame.progress, progress, `scale ${scale}, stage ${stage} round trip`);
        assert.equal(frame.daughtersVisible, stage === 3 && progress >= 0.4);
      }
    }
  }
});
