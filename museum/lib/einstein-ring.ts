/** Ordinary isolated point-mass lens, in units of its Einstein angle.
 * Inverse ray map: beta = theta - theta / |theta|^2.
 * A finite, uniform-brightness circular source avoids the point-source
 * divergence. Its lensed regions are computed, rather than decorative arcs.
 */
export const EINSTEIN_SOURCE_RADIUS = 0.14;
export const EINSTEIN_CROSSING_SECONDS = 18;

type Point = [number, number];
export type EinsteinImage = {
  kind: 'ring' | 'primary' | 'secondary';
  path: string;
  area: number;
};

export function einsteinSourceOffset(progress: number) {
  if (!Number.isFinite(progress) || progress < 0 || progress > 1)
    throw new RangeError('Crossing progress must be between zero and one.');
  return -2.4 + 4.8 * progress;
}

function imageRadius(radialSourceCoordinate: number) {
  return (radialSourceCoordinate + Math.hypot(radialSourceCoordinate, 2)) / 2;
}

function path(points: Point[]) {
  return (
    points
      .map(
        ([x, y], index) =>
          `${index ? 'L' : 'M'}${x.toFixed(5)},${y.toFixed(5)}`,
      )
      .join('') + 'Z'
  );
}

function signedArea(points: Point[]) {
  return (
    points.reduce((sum, p, index) => {
      const next = points[(index + 1) % points.length];
      return sum + p[0] * next[1] - next[0] * p[1];
    }, 0) / 2
  );
}

function boundaries(
  offset: number,
  radius: number,
  start: number,
  end: number,
) {
  const outer: Point[] = [];
  const inner: Point[] = [];
  const samples = 192;
  for (let index = 0; index <= samples; index++) {
    const angle = start + ((end - start) * index) / samples;
    const c = Math.cos(angle),
      s = Math.sin(angle);
    const radial = offset * c;
    const discriminant = Math.max(0, radius * radius - (offset * s) ** 2);
    const halfWidth = Math.sqrt(discriminant);
    const rOuter = imageRadius(radial + halfWidth);
    const rInner = imageRadius(radial - halfWidth);
    outer.push([rOuter * c, rOuter * s]);
    inner.push([rInner * c, rInner * s]);
  }
  return { outer, inner };
}

export function einsteinRingFrame(
  offset: number,
  sourceRadius = EINSTEIN_SOURCE_RADIUS,
) {
  if (!Number.isFinite(offset) || Math.abs(offset) > 2.4)
    throw new RangeError(
      'Source offset must lie within the illustrated crossing.',
    );
  if (!Number.isFinite(sourceRadius) || sourceRadius <= 0 || sourceRadius > 0.5)
    throw new RangeError(
      'The finite source radius must be positive and at most 0.5.',
    );
  const u = Math.abs(offset);
  const images: EinsteinImage[] = [];
  if (u <= sourceRadius) {
    const { outer, inner } = boundaries(offset, sourceRadius, 0, Math.PI * 2);
    // Separate oppositely wound loops retain the central hole of the image.
    images.push({
      kind: 'ring',
      path: path(outer) + path([...inner].reverse()),
      area: Math.abs(signedArea(outer)) - Math.abs(signedArea(inner)),
    });
  } else {
    const direction = offset < 0 ? Math.PI : 0;
    const halfAngle = Math.asin(sourceRadius / u);
    for (const [kind, center] of [
      ['primary', direction],
      ['secondary', direction + Math.PI],
    ] as const) {
      const { outer, inner } = boundaries(
        offset,
        sourceRadius,
        center - halfAngle,
        center + halfAngle,
      );
      const points = [...outer, ...inner.reverse()];
      images.push({
        kind,
        path: path(points),
        area: Math.abs(signedArea(points)),
      });
    }
  }
  const root = Math.hypot(u, 2);
  const sign = offset < 0 ? -1 : 1;
  const amplification = u === 0 ? null : (u * u + 2) / (u * root);
  const pointImages =
    amplification === null
      ? null
      : {
          plus: [(sign * (u + root)) / 2, 0] as Point,
          minus: [(sign * (u - root)) / 2, 0] as Point,
          separation: root,
          fluxRatio: (amplification + 1) / (amplification - 1),
        };
  return { offset, sourceRadius, thetaEinstein: 1, images, pointImages };
}
