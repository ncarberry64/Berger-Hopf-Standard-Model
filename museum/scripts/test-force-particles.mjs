import test from 'node:test';
import assert from 'node:assert/strict';
import {
  electromagneticCloud,
  originCloud,
  coneRadius,
  weakCollision,
  surfaceCollision,
  yellow,
  red,
} from '../lib/force-particles.ts';

test('the electromagnetic cloud fills only the left cone at every sampled phase', () => {
  for (let phase = 0; phase <= 1; phase += 0.05) {
    const cloud = electromagneticCloud(phase);
    assert.equal(cloud.length, 380);
    for (const {
      point: [x, y, z],
      color,
    } of cloud) {
      const u = x / 425 + 0.5;
      assert.ok(u > 0 && u < 0.64);
      assert.ok(Math.hypot(y, z) <= coneRadius(u, 1, phase));
      assert.equal(color, yellow);
    }
  }
});
test('weak collision paths stay within the right cone and converge before scattering', () => {
  for (let phase = 0; phase <= 1; phase += 0.01)
    for (let lane = 0; lane < 8; lane++) {
      const {
        point: [x, y, z],
      } = weakCollision(phase, lane);
      const u = x / 425 + 0.5;
      assert.ok(u > 0.52 && u < 1);
      assert.ok(Math.hypot(y, z) <= coneRadius(u, 2, phase) + 1e-9);
    }
  assert.ok(
    weakCollision(0.25, 0).point.every(
      (v, i) => v === weakCollision(0.25, 1).point[i],
    ),
  );
  assert.equal(weakCollision(0.1, 0).color, yellow);
  assert.equal(weakCollision(0.3, 0).color, red);
  assert.ok(weakCollision(0.3, 0).radius < weakCollision(0.1, 0).radius);
});
test('the origin has a deterministic yellow interior and smaller red surface products', () => {
  const cloud = originCloud();
  assert.deepEqual(cloud, originCloud());
  assert.equal(cloud.length, 460);
  assert.ok(
    cloud.every(
      (dot) => Math.hypot(...dot.point) < 168 && dot.color === yellow,
    ),
  );
  const incoming = surfaceCollision(0.1, 0),
    outgoing = surfaceCollision(0.7, 0);
  assert.equal(incoming.length, 2);
  assert.equal(outgoing.length, 6);
  assert.ok(incoming.every((dot) => dot.color === yellow));
  assert.ok(
    outgoing.every(
      (dot) => dot.color === red && dot.radius < incoming[0].radius,
    ),
  );
  assert.ok(
    [...incoming, ...outgoing].every(
      (dot) => Math.abs(Math.hypot(...dot.point) - 169) < 1e-9,
    ),
  );
});
