export const orbitals = [
  {
    label: '1s',
    n: 1,
    l: 0,
    m: 0,
    extent: 5,
    detail: 'Spherical density, with no radial node.',
  },
  {
    label: '2s',
    n: 2,
    l: 0,
    m: 0,
    extent: 13,
    detail:
      'A dark radial node separates the inner density from the outer ring.',
  },
  {
    label: '2p',
    n: 2,
    l: 1,
    m: 0,
    extent: 10,
    detail: 'Two lobes separated by an angular nodal plane.',
  },
  {
    label: '3s',
    n: 3,
    l: 0,
    m: 0,
    extent: 26,
    detail: 'Two radial nodes produce concentric dark rings.',
  },
  {
    label: '3p',
    n: 3,
    l: 1,
    m: 0,
    extent: 23,
    detail: 'A radial node and an angular node divide the lobes.',
  },
  {
    label: '3d',
    n: 3,
    l: 2,
    m: 1,
    extent: 20,
    detail:
      'A real d-xz orbital section: four lobes and two angular nodal planes.',
  },
  {
    label: '4f',
    n: 4,
    l: 3,
    m: 0,
    extent: 34,
    detail:
      'An f orbital section shows a more intricate angular nodal pattern.',
  },
];
export type Orbital = (typeof orbitals)[number];

function laguerre(k: number, alpha: number, x: number) {
  if (!k) return 1;
  let prev = 1,
    current = 1 + alpha - x;
  for (let j = 2; j <= k; j++) {
    const next =
      ((2 * j - 1 + alpha - x) * current - (j - 1 + alpha) * prev) / j;
    prev = current;
    current = next;
  }
  return current;
}

function legendre(l: number, m: number, x: number) {
  let pmm = 1;
  for (let j = 1; j <= m; j++)
    pmm *= -(2 * j - 1) * Math.sqrt(Math.max(0, 1 - x * x));
  if (l === m) return pmm;
  let prev = pmm,
    current = x * (2 * m + 1) * pmm;
  for (let j = m + 2; j <= l; j++) {
    const next = ((2 * j - 1) * x * current - (j + m - 1) * prev) / (j - m);
    prev = current;
    current = next;
  }
  return current;
}

// Hydrogenic x–z plane section, in Bohr-radius units. Overall normalization
// cancels in the per-image brightness scaling. m=1 uses a real orbital section.
export function orbitalDensity(state: Orbital, x: number, z: number) {
  const r = Math.hypot(x, z),
    rho = (2 * r) / state.n;
  const radial =
    Math.exp(-rho / 2) *
    rho ** state.l *
    laguerre(state.n - state.l - 1, 2 * state.l + 1, rho);
  const angular = legendre(state.l, state.m, r ? z / r : 1);
  return (radial * angular) ** 2;
}

export function orbitalPixels(state: Orbital, size = 192) {
  const density = new Float64Array(size * size);
  let max = 0;
  for (let y = 0; y < size; y++)
    for (let x = 0; x < size; x++) {
      const value = orbitalDensity(
        state,
        ((2 * x) / (size - 1) - 1) * state.extent,
        (1 - (2 * y) / (size - 1)) * state.extent,
      );
      density[y * size + x] = value;
      max = Math.max(max, value);
    }
  const stops = [
    [0, 3, 2, 8],
    [0.12, 30, 7, 63],
    [0.35, 102, 22, 131],
    [0.58, 231, 77, 39],
    [0.78, 255, 181, 48],
    [1, 255, 252, 227],
  ];
  const pixels = new Uint8ClampedArray(size * size * 4);
  density.forEach((value, i) => {
    const t = (value / max) ** 0.38;
    const hi = Math.max(
      1,
      stops.findIndex((stop) => stop[0] >= t),
    );
    const a = stops[hi - 1],
      b = stops[hi],
      f = (t - a[0]) / (b[0] - a[0]);
    for (let c = 0; c < 3; c++)
      pixels[i * 4 + c] = a[c + 1] + (b[c + 1] - a[c + 1]) * f;
    pixels[i * 4 + 3] = 255;
  });
  return pixels;
}

export function matterCycle(
  index: number,
  start: number,
  time: number,
  cycling: boolean,
) {
  return cycling
    ? (index + Math.floor(Math.max(0, time - start) / 6)) % 4
    : index;
}
