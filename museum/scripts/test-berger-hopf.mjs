import test from 'node:test';
import assert from 'node:assert/strict';
import {
  hopfPoint,
  hopfBase,
  projectFiber,
  bergerLevel,
} from '../lib/berger-hopf.ts';
const near = (a, b) =>
  assert.ok(Math.abs(a - b) < 1e-10, `${a} differs from ${b}`);

test('animated fibers close on the unit three-sphere and map to one fixed base point', () => {
  for (const eta of [0.36, 0.58, 0.8])
    for (let n = 0; n < 6; n++) {
      const phi = (n * Math.PI) / 3;
      const base = hopfBase(hopfPoint(eta, phi, 0));
      near(
        base.reduce((sum, x) => sum + x * x, 0),
        1,
      );
      for (let i = 0; i <= 96; i++) {
        const point = hopfPoint(eta, phi, (i * Math.PI) / 48);
        near(
          point.reduce((sum, x) => sum + x * x, 0),
          1,
        );
        hopfBase(point).forEach((x, k) => near(x, base[k]));
        assert.ok(projectFiber(point, 1.2).every(Number.isFinite));
      }
      hopfPoint(eta, phi, Math.PI * 2).forEach((x, k) =>
        near(x, hopfPoint(eta, phi, 0)[k]),
      );
    }
});

test('round-sphere degeneracy and fiber-sensitive splitting follow the repository proxy', () => {
  for (let k = 0; k <= 10; k++)
    for (let j = 0; j <= k; j++) near(bergerLevel(k, j, 1), k * (k + 2));
  for (const s of [0.7, 0.8, 1, 1.2, 1.3]) {
    near(bergerLevel(2, 1, s), 8);
    near(bergerLevel(2, 0, s), 4 / (s * s) + 4);
  }
  assert.ok(bergerLevel(2, 0, 0.7) > 8);
  assert.ok(bergerLevel(2, 0, 1.3) < 8);
});
