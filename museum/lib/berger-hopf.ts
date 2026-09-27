// Unit S3 in C2. A common phase traces one Hopf fiber.
export function hopfPoint(eta: number, phi: number, phase: number) {
  return [
    Math.cos(eta) * Math.cos(phase),
    Math.cos(eta) * Math.sin(phase),
    Math.sin(eta) * Math.cos(phase + phi),
    Math.sin(eta) * Math.sin(phase + phi),
  ];
}

export function hopfBase([x, y, z, w]: number[]) {
  return [
    2 * (x * z + y * w),
    2 * (y * z - x * w),
    x * x + y * y - z * z - w * w,
  ];
}

export function projectFiber(point: number[], angle: number) {
  const [x, y, z, w] = point;
  const d = 1 - w;
  const xx = (x * Math.cos(angle) - z * Math.sin(angle)) / d;
  const zz = (x * Math.sin(angle) + z * Math.cos(angle)) / d;
  return [260 + xx * 78, 228 + ((y / d) * 0.78 + zz * 0.34) * 78];
}

// Repository scalar proxy: a = 1 / fiberScale with the base scale held at one.
// This educational response is dimensionless; it is not a particle mass.
export function bergerLevel(k: number, j: number, fiberScale: number) {
  const q = k - 2 * j;
  return (
    (q * q) / (fiberScale * fiberScale) + 2 * ((2 * j + 1) * k - 2 * j * j)
  );
}
