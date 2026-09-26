import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import {
  environment,
  response,
  spatialRank,
  field,
  harmonicBasis,
} from '../lib/cosmology-realization.ts';
const data = JSON.parse(
  readFileSync(new URL('../app/cosmology-transfer.json', import.meta.url)),
);
const raw = readFileSync(
  new URL(
    '../public/research/r1-coupled-environment-replay.json',
    import.meta.url,
  ),
);
const original = JSON.parse(raw);

test('all animated frames are exactly the retained physical-basis matrices', () => {
  assert.equal(createHash('sha256').update(raw).digest('hex'), data.sha256);
  assert.equal(data.rows.length, 9);
  assert.deepEqual(data.rows[0].matrix, [
    [0, 0, 0, 0],
    [0, 0, 0, 0],
  ]);
  original.rows.forEach((r, i) => {
    assert.equal(data.rows[i + 1].z, r.z);
    assert.deepEqual(data.rows[i + 1].matrix, r.U_XE_q2_Pi2);
  });
});
test('aligned and independent inputs have different spatial ranks at every audited epoch', () => {
  for (const r of data.rows.slice(1)) {
    assert.equal(
      spatialRank(response(r.matrix, environment('aligned', 1, 0.02))),
      1,
    );
    assert.equal(
      spatialRank(response(r.matrix, environment('independent', 1, 0.02))),
      2,
    );
    assert.equal(
      spatialRank(response(r.matrix, environment('zero', 1, 0.02))),
      0,
    );
    assert.equal(
      spatialRank(response(r.matrix, environment('independent', 0, 0.02))),
      1,
    );
  }
});
test('anchor, sign reversal and zero inputs obey linear transfer', () => {
  const e = environment('independent', 1, 0.02),
    r = data.rows.at(-1).matrix;
  assert.equal(spatialRank(response(data.rows[0].matrix, e)), 0);
  const plus = response(r, e),
    minus = response(r, environment('independent', -1, -0.02));
  plus.forEach((row, i) =>
    row.forEach((v, j) => assert.ok(v === -minus[i][j])),
  );
  assert.equal(plus[0][0], r[0][0]);
  assert.equal(plus[1][2], r[1][2] * 0.02);
});
test('all nine illustrative basis polynomials are harmonic and homogeneous of degree two', () => {
  const p = [0.3, 0.4, 0.2, Math.sqrt(0.71)],
    v = harmonicBasis(...p),
    scaled = harmonicBasis(...p.map((x) => 2 * x));
  v.forEach((x, i) => assert.ok(Math.abs(scaled[i] - 4 * x) < 1e-12));
  for (let i = 0; i < 9; i++) {
    let trace = 0;
    for (let j = 0; j < 4; j++) {
      const axis = [0, 0, 0, 0];
      axis[j] = 1;
      trace += harmonicBasis(...axis)[i];
    }
    assert.equal(trace, 0);
  }
  assert.equal(field(Array(9).fill(0), p), 0);
  assert.equal(field([1, 0, 0, 0, 0, 0, 0, 0, 0], p), p[0] ** 2 - p[1] ** 2);
});
