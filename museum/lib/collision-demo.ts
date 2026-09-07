// Relativistic two-body kinematics in arbitrary demonstration units.
// This computes phase space, never a BHSM amplitude or a process probability.
export type FourVector = { E: number; px: number; py: number; pz: number };
export function collisionDemo(
  energy: number,
  masses: number[],
  angle: number,
  charges: number[],
) {
  if (
    masses.length !== 4 ||
    charges.length !== 4 ||
    ![energy, angle, ...masses, ...charges].every(Number.isFinite) ||
    energy <= 0 ||
    masses.some((m) => m < 0)
  )
    throw new Error('Invalid demonstration inputs');
  if (Math.abs(charges[0] + charges[1] - charges[2] - charges[3]) > 1e-9)
    return {
      status: 'charge-blocked',
      incoming: [],
      outgoing: [],
      residual: null,
    };
  if (energy <= Math.max(masses[0] + masses[1], masses[2] + masses[3]))
    return {
      status: 'threshold-closed',
      incoming: [],
      outgoing: [],
      residual: null,
    };
  const pair = (a: number, b: number, theta: number): FourVector[] => {
    const s = energy * energy;
    const p =
      Math.sqrt(Math.max(0, (s - (a + b) ** 2) * (s - (a - b) ** 2))) /
      (2 * energy);
    const x = p * Math.sin(theta),
      z = p * Math.cos(theta);
    return [
      { E: (s + a * a - b * b) / (2 * energy), px: x, py: 0, pz: z },
      { E: (s + b * b - a * a) / (2 * energy), px: -x, py: 0, pz: -z },
    ];
  };
  const incoming = pair(masses[0], masses[1], 0),
    outgoing = pair(masses[2], masses[3], (angle * Math.PI) / 180);
  const residual = Math.max(
    ...(['E', 'px', 'py', 'pz'] as const).map((k) =>
      Math.abs(
        incoming[0][k] + incoming[1][k] - outgoing[0][k] - outgoing[1][k],
      ),
    ),
  );
  return { status: 'kinematics-only', incoming, outgoing, residual };
}
