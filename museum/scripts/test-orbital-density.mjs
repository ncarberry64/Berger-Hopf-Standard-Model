import test from 'node:test';
import assert from 'node:assert/strict';
import {
  orbitals,
  orbitalDensity,
  orbitalPixels,
  matterCycle,
} from '../lib/orbital-density.ts';

test('hydrogenic sections retain radial and angular nodes', () => {
  const [s1, s2, p2, , p3, d3] = orbitals;
  assert(orbitalDensity(s1, 0, 0) > 0);
  assert.equal(orbitalDensity(s2, 2, 0), 0);
  assert.equal(orbitalDensity(p2, 2, 0), 0);
  assert.equal(orbitalDensity(p3, 0, 6), 0);
  assert.equal(orbitalDensity(d3, 0, 3), 0);
  assert.equal(orbitalDensity(d3, 3, 0), 0);
  assert(orbitalDensity(d3, 3, 3) > 0);
});

test('density sections are finite, symmetric and reproducible', () => {
  for (const state of orbitals) {
    for (const [x, z] of [
      [0, 0],
      [1, 2],
      [4, 6],
      [20, 30],
    ]) {
      const d = orbitalDensity(state, x, z);
      assert(Number.isFinite(d) && d >= 0);
      assert.equal(d, orbitalDensity(state, -x, -z));
    }
    const pixels = orbitalPixels(state, 48);
    assert.equal(pixels.length, 48 * 48 * 4);
    assert.deepEqual(pixels, orbitalPixels(state, 48));
    assert(pixels.some((v, i) => i % 4 !== 3 && v > 200));
  }
});

test('matter cycle advances in order, wraps and respects held selections', () => {
  assert.deepEqual(
    [0, 5.99, 6, 12, 18, 24].map((t) => matterCycle(0, 0, t, true)),
    [0, 0, 1, 2, 3, 0],
  );
  assert.equal(matterCycle(2, 17, 22.9, true), 2);
  assert.equal(matterCycle(2, 17, 23, true), 3);
  assert.equal(matterCycle(1, 0, 999, false), 1);
});
