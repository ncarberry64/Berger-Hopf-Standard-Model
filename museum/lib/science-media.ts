export type FourVector = { E: number; px: number; py: number; pz: number };

/** Invariant mass from a measured subsystem; not the full collision energy. */
export function invariantMass(vectors: FourVector[]) {
  const sum = vectors.reduce(
    (a, v) => ({
      E: a.E + v.E,
      px: a.px + v.px,
      py: a.py + v.py,
      pz: a.pz + v.pz,
    }),
    { E: 0, px: 0, py: 0, pz: 0 },
  );
  return Math.sqrt(
    Math.max(0, sum.E ** 2 - sum.px ** 2 - sum.py ** 2 - sum.pz ** 2),
  );
}

/** Spin-1/2 Larmor frequency in Hz; CODATA moment in J/T, field in T. */
export function larmorHz(moment: number, field: number) {
  if (!Number.isFinite(moment) || !Number.isFinite(field) || field < 0)
    throw new Error('Finite moment and nonnegative field required');
  return (
    (Math.abs(moment) * field) / (Math.PI * (6.62607015e-34 / (2 * Math.PI)))
  );
}

/** Normalized display trajectory, intentionally not detector propagation. */
export function trackPoints(
  phi: number,
  charge: number,
  pt: number,
  progress: number,
) {
  return Array.from({ length: 65 }, (_, i) => {
    const t = (Math.max(0, Math.min(1, progress)) * i) / 64;
    const bend = charge * Math.min(4.1, 6 / Math.max(0.5, pt));
    const a = phi + bend * t;
    const radius = 218 * t;
    return [400 + radius * Math.cos(a), 270 - radius * Math.sin(a)];
  });
}
