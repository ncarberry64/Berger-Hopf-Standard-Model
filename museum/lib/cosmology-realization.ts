export type Pattern = 'independent' | 'aligned' | 'zero';
export type Matrix = number[][];

// Fixed illustrative inputs, not a fit or a physical anchor-state inference.
export function environment(
  pattern: Pattern,
  density: number,
  velocity: number,
): Matrix {
  const e = Array.from({ length: 4 }, () => Array<number>(9).fill(0));
  if (pattern !== 'zero') {
    e[0][0] = density;
    e[2][pattern === 'aligned' ? 0 : 2] = velocity;
  }
  return e;
}

export function response(u: Matrix, e: Matrix): Matrix {
  if (
    u.length !== 2 ||
    u.some((r) => r.length !== 4) ||
    e.length !== 4 ||
    e.some((r) => r.length !== 9)
  )
    throw new Error('Invalid transfer dimensions');
  return u.map((row) =>
    Array.from({ length: 9 }, (_, j) =>
      row.reduce((v, k, i) => v + k * e[i][j], 0),
    ),
  );
}

// Stable rank diagnostic for the two output rows, with the same relative 1e-8
// singular-value threshold used by the retained numerical audit.
export function spatialRank(x: Matrix): number {
  const a = Math.hypot(...x[0]),
    b = Math.hypot(...x[1]);
  if (Math.max(a, b) === 0) return 0;
  const first = a >= b ? x[0] : x[1],
    second = a >= b ? x[1] : x[0];
  const norm = Math.max(a, b),
    unit = first.map((v) => v / norm);
  const projection = second.reduce((s, v, i) => s + v * unit[i], 0);
  const orthogonal = Math.hypot(
    ...second.map((v, i) => v - projection * unit[i]),
  );
  const trace = a * a + b * b;
  const determinant = (norm * orthogonal) ** 2;
  const largestSquared =
    (trace + Math.sqrt(Math.max(0, trace * trace - 4 * determinant))) / 2;
  return Math.sqrt(determinant) / largestSquared > 1e-8 ? 2 : 1;
}

// Nine independent trace-free homogeneous quadratic polynomials on unit S3.
// These are an explicit illustrative basis, not claimed to be orthonormal.
export function harmonicBasis(
  x: number,
  y: number,
  z: number,
  w: number,
): number[] {
  return [
    x * x - y * y,
    2 * x * y,
    2 * x * z,
    2 * x * w,
    y * y - z * z,
    2 * y * z,
    2 * y * w,
    z * z - w * w,
    2 * z * w,
  ];
}

export function field(coefficients: number[], point: number[]): number {
  return harmonicBasis(point[0], point[1], point[2], point[3]).reduce(
    (s, v, i) => s + v * coefficients[i],
    0,
  );
}
