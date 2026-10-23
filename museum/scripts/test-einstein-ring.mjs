import test from 'node:test';
import assert from 'node:assert/strict';
import {
  EINSTEIN_SOURCE_RADIUS,
  EINSTEIN_CROSSING_SECONDS,
  einsteinSourceOffset,
  einsteinRingFrame,
} from '../lib/einstein-ring.ts';

function vertices(path) {
  return [...path.matchAll(/[ML](-?[\d.]+),(-?[\d.]+)/g)].map((match) => [
    Number(match[1]),
    Number(match[2]),
  ]);
}

test('the finite source crosses the line of sight and aligns halfway through the tour', () => {
  assert.equal(EINSTEIN_CROSSING_SECONDS, 18);
  assert.equal(einsteinSourceOffset(0), -2.4);
  assert.equal(einsteinSourceOffset(0.5), 0);
  assert.equal(einsteinSourceOffset(1), 2.4);
  assert.throws(() => einsteinSourceOffset(-0.01), RangeError);
  assert.throws(() => einsteinSourceOffset(NaN), RangeError);
});

test('every computed image boundary inverse-maps to the declared source edge', () => {
  for (const offset of [
    -2.4, -0.7, -0.15, -0.14, -0.08, 0, 0.08, 0.14, 0.15, 0.7, 2.4,
  ]) {
    const frame = einsteinRingFrame(offset);
    for (const image of frame.images) {
      assert.ok(image.area > 0);
      assert.doesNotMatch(image.path, /NaN|Infinity/);
      for (const [x, y] of vertices(image.path)) {
        const r2 = x * x + y * y;
        const betaX = x * (1 - 1 / r2);
        const betaY = y * (1 - 1 / r2);
        assert.ok(
          Math.abs(Math.hypot(betaX - offset, betaY) - EINSTEIN_SOURCE_RADIUS) <
            5e-5,
        );
      }
    }
  }
});

test('exact alignment creates a finite annulus bracketing the Einstein angle', () => {
  const frame = einsteinRingFrame(0);
  assert.equal(frame.images.length, 1);
  assert.equal(frame.images[0].kind, 'ring');
  assert.equal(frame.pointImages, null);
  const radii = vertices(frame.images[0].path).map(([x, y]) =>
    Math.hypot(x, y),
  );
  assert.ok(Math.min(...radii) < 1 && Math.max(...radii) > 1);
  assert.ok(Math.min(...radii) > 0, 'the ring is an image with a central hole');
  const rho = EINSTEIN_SOURCE_RADIUS;
  const expectedArea = Math.PI * rho * Math.hypot(rho, 2);
  assert.ok(Math.abs(frame.images[0].area / expectedArea - 1) < 0.0002);
});

test('off-axis images satisfy the lens equation and the Einstein-radius product identity', () => {
  for (const offset of [-2.4, -0.7, -0.2, 0.2, 0.7, 2.4]) {
    const frame = einsteinRingFrame(offset);
    assert.deepEqual(
      frame.images.map((image) => image.kind),
      ['primary', 'secondary'],
    );
    const p = frame.pointImages;
    for (const [x] of [p.plus, p.minus])
      assert.ok(Math.abs(x - 1 / x - offset) < 1e-12);
    assert.ok(Math.abs(p.plus[0] * p.minus[0] + 1) < 1e-12);
    assert.ok(
      Math.abs(Math.abs(p.plus[0] - p.minus[0]) - p.separation) < 1e-12,
    );
    assert.ok(p.fluxRatio > 1 && Number.isFinite(p.fluxRatio));
  }
});

test('symmetric crossings have the same image areas and magnifications', () => {
  for (const offset of [0.05, 0.14, 0.7, 2.4]) {
    const left = einsteinRingFrame(-offset),
      right = einsteinRingFrame(offset);
    assert.equal(left.images.length, right.images.length);
    // Tangent-ray endpoints contain a square root of a near-zero discriminant.
    left.images.forEach((image, index) =>
      assert.ok(Math.abs(image.area - right.images[index].area) < 1e-9),
    );
    assert.equal(left.pointImages?.fluxRatio, right.pointImages?.fluxRatio);
  }
});

test('invalid source geometry is rejected rather than rendered as a fake ring', () => {
  for (const offset of [Infinity, NaN, 3])
    assert.throws(() => einsteinRingFrame(offset), RangeError);
  for (const radius of [0, -0.1, 1, NaN])
    assert.throws(() => einsteinRingFrame(0, radius), RangeError);
});
