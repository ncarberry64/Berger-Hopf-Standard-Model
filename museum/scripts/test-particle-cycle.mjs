import test from 'node:test';
import assert from 'node:assert/strict';
import {
  PARTICLE_CYCLE_SECONDS,
  particleCyclePhases,
  particleCycleFrame,
  particleSurfaceHeight,
  bubbleOutline,
} from '../lib/particle-cycle.ts';

test('one continuous cycle covers all seven phases and returns exactly to its starting geometry', () => {
  assert.equal(particleCyclePhases[0].start, 0);
  assert.equal(particleCyclePhases.at(-1).end, PARTICLE_CYCLE_SECONDS);
  for (let index = 1; index < particleCyclePhases.length; index++)
    assert.equal(
      particleCyclePhases[index - 1].end,
      particleCyclePhases[index].start,
    );
  assert.deepEqual(particleCycleFrame(46), particleCycleFrame(0));
  for (const x of [50, 300, 550, 900])
    for (const y of [300, 344, 420]) {
      assert.equal(
        particleSurfaceHeight(x, y, 46),
        particleSurfaceHeight(x, y, 0),
      );
      assert.ok(
        Math.abs(
          particleSurfaceHeight(x, y, 45.9999) - particleSurfaceHeight(x, y, 0),
        ) < 0.01,
      );
    }
});

test('the rogue crest precedes a connected neck and a detached traveling bubble', () => {
  assert.ok(particleCycleFrame(11.9).crest > 0.99);
  assert.equal(particleCycleFrame(6).parent.opacity, 0);
  assert.ok(particleCycleFrame(14).neck > 0.8);
  const detached = particleCycleFrame(19);
  assert.equal(detached.neck, 0);
  assert.equal(detached.parent.opacity, 1);
  assert.ok(detached.parent.x > 300);
  assert.ok(particleSurfaceHeight(300, 344, 11.9) > 120);
});

test('incoming contact produces daughters with distinct sequential rupture times', () => {
  const before = particleCycleFrame(24);
  const contact = particleCycleFrame(27);
  assert.ok(
    before.incoming.x - before.parent.x > before.incoming.r + before.parent.r,
  );
  assert.ok(
    contact.incoming.x - contact.parent.x <
      contact.incoming.r + contact.parent.r,
  );
  const daughters = particleCycleFrame(34).daughters;
  assert.ok(daughters.every((daughter) => daughter.opacity === 1));
  assert.equal(new Set(daughters.map(({ x, y }) => `${x},${y}`)).size, 3);
  assert.equal(particleCycleFrame(37).daughters[0].opacity, 0);
  assert.equal(particleCycleFrame(37).daughters[1].opacity, 1);
  assert.equal(particleCycleFrame(40).daughters[1].opacity, 0);
  assert.equal(particleCycleFrame(40).daughters[2].opacity, 1);
  assert.ok(
    particleCycleFrame(43).daughters.every(
      (daughter) => daughter.opacity === 0,
    ),
  );
});

test('all rendered geometry remains finite and daughter membranes wobble independently', () => {
  for (let t = 0; t < 46; t += 0.25) {
    const frame = particleCycleFrame(t);
    for (const d of frame.daughters)
      for (const key of [
        'x',
        'y',
        'r',
        'opacity',
        'pop',
        'returnProgress',
        'ringRadius',
      ])
        assert.ok(Number.isFinite(d[key]));
    for (const x of [20, 300, 590, 980])
      assert.ok(Number.isFinite(particleSurfaceHeight(x, 344, t)));
  }
  assert.notEqual(bubbleOutline(30, 0.1, 34, 0), bubbleOutline(30, 0.1, 34, 1));
  assert.ok(bubbleOutline(30, 0.1, 34).endsWith('Z'));
});

test('returning streams reach the surface before the landing ripples expand', () => {
  for (const [index, popAt] of [35.6, 38, 40.4].entries()) {
    const inFlight = particleCycleFrame(popAt + 1).daughters[index];
    assert.ok(inFlight.returnProgress < 1);
    assert.equal(inFlight.ringOpacity, 0);
    const landed = particleCycleFrame(popAt + 1.5).daughters[index];
    assert.equal(landed.returnProgress, 1);
    assert.ok(landed.ringOpacity > 0);
  }
});
