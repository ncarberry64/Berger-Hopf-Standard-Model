// Deterministic visual choreography, not particle dynamics or a physical rate.
export type Point = [number, number, number];
export type Dot = { point: Point; radius: number; color: string };
const TAU = 2 * Math.PI;
export const yellow = '#ffe073';
export const red = '#ff655b';
const seed = (i: number) => {
  const x = Math.sin(i * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
};
export function coneRadius(u: number, kind: number, phase: number) {
  return (
    10 +
    190 * Math.abs(u - (kind === 1 ? 0.64 : 0.52)) ** 1.45 +
    (kind === 2 ? 13 * u * (1 + Math.sin(phase * TAU)) : 0)
  );
}
export function electromagneticCloud(phase: number): Dot[] {
  return Array.from({ length: 380 }, (_, i) => {
    const u = 0.025 + 0.575 * (1 - Math.cbrt(seed(i + 1)));
    const r = coneRadius(u, 1, phase) * Math.sqrt(seed(i + 401)) * 0.92;
    const angle = seed(i + 801) * TAU + phase * TAU;
    return {
      point: [(u - 0.5) * 425, r * Math.cos(angle), r * Math.sin(angle)],
      radius: 2.5 + seed(i + 1201) * 1.5,
      color: yellow,
    };
  });
}
export function originCloud(): Dot[] {
  return Array.from({ length: 460 }, (_, i) => {
    const r = 157 * Math.cbrt(seed(i + 9));
    const y = 2 * seed(i + 501) - 1;
    const angle = seed(i + 1001) * TAU;
    const h = Math.sqrt(1 - y * y);
    return {
      point: [r * h * Math.cos(angle), r * y, r * h * Math.sin(angle)],
      radius: 2 + seed(i + 1501) * 1.4,
      color: yellow,
    };
  });
}
export function weakCollision(phase: number, lane: number): Dot {
  const q = (((phase * 2 + Math.floor(lane / 2) / 4) % 1) + 1) % 1;
  const side = lane % 2 ? 1 : -1;
  const distance = Math.abs(q - 0.5) * 2;
  const u = 0.77 + side * 0.19 * distance;
  const angle = phase * TAU * 4 + (lane * Math.PI) / 2;
  const r = coneRadius(u, 2, phase) * 0.78 * distance;
  return {
    point: [(u - 0.5) * 425, r * Math.cos(angle), r * Math.sin(angle)],
    radius: q < 0.5 ? 4 : 2.6,
    color: q < 0.5 ? yellow : red,
  };
}
export function surfaceCollision(phase: number, lane: number): Dot[] {
  const q = (((phase + lane / 3) % 1) + 1) % 1;
  const collision = q >= 0.55;
  const separation = collision
    ? ((q - 0.55) / 0.45) * 0.85
    : (1 - q / 0.55) * 0.95;
  const count = collision ? 6 : 2;
  return Array.from({ length: count }, (_, i) => {
    const direction = collision ? (i * TAU) / count : i * Math.PI;
    const longitude = (lane * TAU) / 3 + separation * Math.cos(direction);
    const latitude =
      (lane - 1) * 0.42 + separation * Math.sin(direction) * 0.55;
    const r = 169;
    return {
      point: [
        r * Math.cos(latitude) * Math.cos(longitude),
        r * Math.sin(latitude),
        r * Math.cos(latitude) * Math.sin(longitude),
      ],
      radius: collision ? 2.3 : 5.2,
      color: collision ? red : yellow,
    };
  });
}
