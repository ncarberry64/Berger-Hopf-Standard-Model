import test from 'node:test';
import assert from 'node:assert/strict';
import { collisionDemo } from '../lib/collision-demo.ts';

test('collision output conserves four-momentum and each supplied rest mass', () => {
  for (const energy of [6, 10, 20]) for (const angle of [5, 55, 90, 175]) {
    const masses = [1, 2, .5, 3];
    const r = collisionDemo(energy, masses, angle, [-1, 1, -1, 1]);
    assert.equal(r.status, 'kinematics-only');
    assert.ok(r.residual < 1e-12);
    [...r.incoming, ...r.outgoing].forEach((v, i) => {
      assert.ok(Math.abs(v.E ** 2 - v.px ** 2 - v.py ** 2 - v.pz ** 2 - masses[i] ** 2) < 1e-11);
    });
  }
});
test('threshold and charge failures produce no event', () => {
  for (const r of [collisionDemo(2, [1,1,1,1], 90, [-1,1,-1,1]), collisionDemo(6, [1,1,1,1], 90, [-1,-1,-1,1])]) {
    assert.equal(r.outgoing.length, 0);
    assert.equal(r.residual, null);
  }
});
test('massless final states are finite; invalid values fail instead of becoming data', () => {
  const r = collisionDemo(6, [1,1,0,0], 90, [-1,1,0,0]);
  assert.equal(r.outgoing[0].E, 3);
  assert.throws(() => collisionDemo(6, [1,1,NaN,0], 90, [-1,1,0,0]));
  assert.throws(() => collisionDemo(6, [-1,1,0,0], 90, [-1,1,0,0]));
});
