import test from 'node:test';
import assert from 'node:assert/strict';
import transfer from '../app/cosmology-transfer.json' with { type: 'json' };
import { cosmologySurfacePoint } from '../lib/cosmology-surface.ts';
import { environment, field, response, spatialRank } from '../lib/cosmology-realization.ts';

const slice = Math.sqrt(3) / 2;
const directions = [
  [1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1],
  [Math.SQRT1_2, 0, Math.SQRT1_2],
  [Math.SQRT1_2, 0, -Math.SQRT1_2],
];
const valueAt = (coefficients, direction) => field(coefficients, [...direction.map((v) => v * slice), 0.5]);
const near = (actual, expected) => assert.ok(Math.abs(actual - expected) < 1e-12, `${actual} versus ${expected}`);

function surface(coefficients) {
  const values = directions.map((direction) => valueAt(coefficients, direction));
  const scale = Math.max(...values.map(Math.abs));
  return directions.map((direction, i) => cosmologySurfacePoint(direction, values[i], scale));
}

test('the exact h1 field puts positive cyan lobes outward, negative gold inward and nodes on the reference sphere', () => {
  const coefficients = [1, 0, 0, 0, 0, 0, 0, 0, 0];
  const points = surface(coefficients);
  assert.ok(Math.hypot(...points[0].point) > 1 && points[0].signed > 0);
  assert.ok(Math.hypot(...points[2].point) < 1 && points[2].signed < 0);
  assert.deepEqual(points[4], { point: [0, 0, 1], signed: 0 });
  near(points[0].point[0], -points[1].point[0]);
  near(points[2].point[1], -points[3].point[1]);
  directions.forEach((direction, i) => {
    const point = points[i].point;
    near(point[0] * direction[1] - point[1] * direction[0], 0);
    near(point[0] * direction[2] - point[2] * direction[0], 0);
    near(point[1] * direction[2] - point[2] * direction[1], 0);
  });
});

test('deformation orientation comes from the selected exact field rather than a fixed decorative shape', () => {
  const h1 = surface([1, 0, 0, 0, 0, 0, 0, 0, 0]);
  const h3 = surface([0, 0, 1, 0, 0, 0, 0, 0, 0]);
  assert.ok(h1[0].signed > 0 && h1[2].signed < 0);
  assert.equal(h3[0].signed, 0);
  assert.equal(h3[2].signed, 0);
  assert.ok(h3[5].signed > 0 && Math.hypot(...h3[5].point) > 1);
  assert.ok(h3[6].signed < 0 && Math.hypot(...h3[6].point) < 1);
});

test('separate normalization preserves shape under amplitude rescaling and reverses displacement with field sign', () => {
  const coefficients = [0.5, 0, 0.3, 0, 0, 0, 0, 0, 0];
  const original = surface(coefficients);
  const rescaled = surface(coefficients.map((v) => v * 1e-8));
  const negative = surface(coefficients.map((v) => -v));
  original.forEach((item, i) => {
    near(rescaled[i].signed, item.signed);
    item.point.forEach((v, axis) => near(rescaled[i].point[axis], v));
    near(negative[i].signed, -item.signed);
    near(Math.hypot(...negative[i].point) + Math.hypot(...item.point), 2);
  });
});

test('zero input stays round at every saved epoch and leaves the computed response and ranks intact', () => {
  const zero = environment('zero', 1, 0.02);
  for (const epoch of transfer.rows) {
    const computed = response(epoch.matrix, zero);
    const snapshot = structuredClone(computed);
    assert.equal(spatialRank(computed), 0);
    for (const row of computed) {
      const points = surface(row);
      points.forEach((item, i) => {
        assert.equal(item.signed, 0);
        assert.deepEqual(item.point, directions[i]);
        near(Math.hypot(...item.point), 1);
      });
    }
    assert.deepEqual(computed, snapshot, 'drawing the surface cannot mutate saved response coefficients');
  }
});

test('all saved nonzero responses use bounded radial displacements without modifying coefficient readouts', () => {
  for (const epoch of transfer.rows.slice(1)) {
    for (const pattern of ['independent', 'aligned']) {
      const computed = response(epoch.matrix, environment(pattern, 1, 0.02));
      const snapshot = structuredClone(computed);
      const rank = spatialRank(computed);
      for (const row of computed) {
        surface(row).forEach((item) => {
          assert.ok(item.signed >= -1 && item.signed <= 1);
          const radius = Math.hypot(...item.point);
          assert.ok(radius >= 0.739999999999 && radius <= 1.260000000001);
        });
      }
      assert.deepEqual(computed, snapshot);
      assert.equal(spatialRank(computed), rank);
    }
  }
});
