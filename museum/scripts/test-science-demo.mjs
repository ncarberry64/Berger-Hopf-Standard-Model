import test from 'node:test';
import assert from 'node:assert/strict';
import { collisionDemo } from '../lib/collision-demo.ts';

test('collision output conserves four-momentum and each supplied rest mass', () => {
  for (const energy of [6, 10, 20])
    for (const angle of [5, 55, 90, 175]) {
      const masses = [1, 2, 0.5, 3];
      const r = collisionDemo(energy, masses, angle, [-1, 1, -1, 1]);
      assert.equal(r.status, 'kinematics-only');
      assert.ok(r.residual < 1e-12);
      [...r.incoming, ...r.outgoing].forEach((v, i) => {
        assert.ok(
          Math.abs(
            v.E ** 2 - v.px ** 2 - v.py ** 2 - v.pz ** 2 - masses[i] ** 2,
          ) < 1e-11,
        );
      });
    }
});
test('threshold and charge failures produce no event', () => {
  for (const r of [
    collisionDemo(2, [1, 1, 1, 1], 90, [-1, 1, -1, 1]),
    collisionDemo(6, [1, 1, 1, 1], 90, [-1, -1, -1, 1]),
  ]) {
    assert.equal(r.outgoing.length, 0);
    assert.equal(r.residual, null);
  }
});
test('massless final states are finite; invalid values fail instead of becoming data', () => {
  const r = collisionDemo(6, [1, 1, 0, 0], 90, [-1, 1, 0, 0]);
  assert.equal(r.outgoing[0].E, 3);
  assert.throws(() => collisionDemo(6, [1, 1, NaN, 0], 90, [-1, 1, 0, 0]));
  assert.throws(() => collisionDemo(6, [-1, 1, 0, 0], 90, [-1, 1, 0, 0]));
});

import { invariantMass, larmorHz, trackPoints } from '../lib/science-media.ts';
test('invariant subsystem mass is unchanged by a longitudinal Lorentz boost', () => {
  const v = [
    { E: 5, px: 3, py: 0, pz: 4 },
    { E: 5, px: -3, py: 0, pz: -4 },
  ];
  const beta = 0.6,
    gamma = 1.25;
  const boosted = v.map((q) => ({
    ...q,
    E: gamma * (q.E - beta * q.pz),
    pz: gamma * (q.pz - beta * q.E),
  }));
  assert.ok(Math.abs(invariantMass(v) - invariantMass(boosted)) < 1e-12);
});
test('reference moments reproduce CODATA Larmor benchmarks and field scaling', () => {
  assert.ok(
    Math.abs(larmorHz(1.41060679545e-26, 1) / 1e6 - 42.577478461) < 1e-7,
  );
  assert.ok(
    Math.abs(larmorHz(-9.2847646917e-24, 1) / 1e6 - 28024.9513861) < 1e-4,
  );
  assert.equal(larmorHz(1e-26, 0), 0);
  assert.equal(larmorHz(-1e-26, 0.5), larmorHz(1e-26, 1) / 2);
  assert.throws(() => larmorHz(1e-26, -1));
});
test('neutral display tracks are straight and conjugate curvatures are mirrored', () => {
  const positive = trackPoints(0, 1, 2, 1),
    negative = trackPoints(0, -1, 2, 1),
    neutral = trackPoints(0, 0, 2, 1);
  positive.forEach((p, i) => {
    assert.ok(Math.abs(p[0] - negative[i][0]) < 1e-10);
    assert.ok(Math.abs(p[1] + negative[i][1] - 540) < 1e-10);
    assert.equal(neutral[i][1], 270);
  });
});
