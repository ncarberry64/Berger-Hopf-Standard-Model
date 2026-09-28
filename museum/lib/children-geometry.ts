const TAU = Math.PI * 2;

export function curve(points: number[][]) {
  return points
    .map(([x, y], i) => `${i ? 'L' : 'M'}${x.toFixed(2)},${y.toFixed(2)}`)
    .join(' ');
}

// Circles sampled on S³ in R⁴, rotated in the x–w plane, then perspective
// projected into R³ and onto the screen. This is a projection, not a 3D ball.
export function hypersphereCurves(time: number) {
  return Array.from({ length: 18 }, (_, ring) => {
    const eta = [0.28, Math.PI / 4, 1.29][ring % 3];
    const phi = (TAU * Math.floor(ring / 3)) / 6;
    return curve(
      Array.from({ length: 81 }, (_, i) => {
        const t = (TAU * i) / 80;
        const x = Math.cos(eta) * Math.cos(t);
        const y = Math.cos(eta) * Math.sin(t);
        const z = Math.sin(eta) * Math.cos(phi);
        const w = Math.sin(eta) * Math.sin(phi);
        const a = time * 0.3;
        const xr = x * Math.cos(a) - w * Math.sin(a);
        const wr = x * Math.sin(a) + w * Math.cos(a);
        const scale = 67 / (1.8 - wr);
        return [
          110 + scale * (xr + 0.3 * z),
          58 + scale * (0.8 * y + 0.35 * z),
        ];
      }),
    );
  });
}

export function harmonicCurve(mode: number, time: number) {
  return curve(
    Array.from({ length: 101 }, (_, i) => {
      const fraction = i / 100;
      return [
        28 + 170 * fraction,
        20 +
          (mode - 1) * 35 +
          12 *
            Math.sin(mode * Math.PI * fraction) *
            Math.cos(time * 1.5 * mode),
      ];
    }),
  );
}

export function hexagon(radius: number) {
  return curve(
    Array.from({ length: 7 }, (_, i) => [
      110 + radius * Math.cos((i * TAU) / 6),
      58 + radius * Math.sin((i * TAU) / 6),
    ]),
  );
}
