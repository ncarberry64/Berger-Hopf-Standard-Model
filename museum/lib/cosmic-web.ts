// Deterministic visual geometry only: this is not a cosmological solver or survey catalogue.
export type Vec3 = [number, number, number];
const add = (a: Vec3, b: Vec3): Vec3 => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
const sub = (a: Vec3, b: Vec3): Vec3 => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const dot = (a: Vec3, b: Vec3) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const cross = (a: Vec3, b: Vec3): Vec3 => [
  a[1] * b[2] - a[2] * b[1],
  a[2] * b[0] - a[0] * b[2],
  a[0] * b[1] - a[1] * b[0],
];
export const unit = (v: Vec3): Vec3 => {
  const r = Math.hypot(...v);
  return r > 1e-10 ? [v[0] / r, v[1] / r, v[2] / r] : [0, 0, 1];
};
export const mix = (a: Vec3, b: Vec3, t: number): Vec3 =>
  unit([
    a[0] * (1 - t) + b[0] * t,
    a[1] * (1 - t) + b[1] * t,
    a[2] * (1 - t) + b[2] * t,
  ]);
let seed = 917206;
function random() {
  seed ^= seed << 13;
  seed ^= seed >>> 17;
  seed ^= seed << 5;
  return (seed >>> 0) / 4294967296;
}
function sphere(): Vec3 {
  const y = 2 * random() - 1,
    a = random() * Math.PI * 2,
    r = Math.sqrt(1 - y * y);
  return [r * Math.cos(a), y, r * Math.sin(a)];
}
const normal = () =>
  Math.sqrt(-2 * Math.log(Math.max(random(), 1e-8))) *
  Math.cos(2 * Math.PI * random());
// Irregular spherical Voronoi cells reserve broad voids. Their shared borders
// supply a branched skeleton, which is rendered as a nonuniform density field.
const voids: Vec3[] = [];
while (voids.length < 48) {
  const v = sphere();
  if (voids.every((w) => Math.hypot(...sub(v, w)) > 0.2)) voids.push(v);
}
const faces: { ids: number[]; normal: Vec3 }[] = [];
for (let i = 0; i < voids.length; i++)
  for (let j = i + 1; j < voids.length; j++)
    for (let k = j + 1; k < voids.length; k++) {
      const a = voids[i],
        b = voids[j],
        c = voids[k];
      let n = unit(cross(sub(b, a), sub(c, a)));
      if (dot(n, a) < 0) n = [-n[0], -n[1], -n[2]];
      const d = dot(n, a);
      if (
        voids.every(
          (v, l) => l === i || l === j || l === k || dot(n, v) < d + 1e-8,
        )
      )
        faces.push({ ids: [i, j, k], normal: n });
    }
export const webNodes = faces.map((f) => f.normal);
export const webEdges: {
  i: number;
  j: number;
  weight: number;
  bend: number;
}[] = [];
for (let i = 0; i < faces.length; i++)
  for (let j = i + 1; j < faces.length; j++) {
    if (faces[i].ids.filter((k) => faces[j].ids.includes(k)).length === 2)
      webEdges.push({
        i,
        j,
        weight: 0.45 + random() * 0.9,
        bend: (random() - 0.5) * 0.11,
      });
  }
export function filamentPoint(
  edge: (typeof webEdges)[number],
  t: number,
  offset = 0,
): Vec3 {
  const a = webNodes[edge.i],
    b = webNodes[edge.j],
    n = unit(cross(a, b));
  const wobble =
    Math.sin(Math.PI * t) * (edge.bend * Math.sin(t * 7 + edge.i) + offset);
  return unit([
    a[0] * (1 - t) + b[0] * t + n[0] * wobble,
    a[1] * (1 - t) + b[1] * t + n[1] * wobble,
    a[2] * (1 - t) + b[2] * t + n[2] * wobble,
  ]);
}
export type WebParticle = {
  position: Vec3;
  diffuse: Vec3;
  size: number;
  warm: boolean;
  brightness: number;
  target: number;
};
export const webParticles: WebParticle[] = Array.from(
  { length: 5200 },
  (_, i) => {
    const edge = webEdges[i % webEdges.length],
      t = random();
    let position: Vec3;
    if (i < 3650) {
      const spine = filamentPoint(edge, t, normal() * 0.018);
      const width = (i % 9 === 0 ? 0.025 : 0.0045) * edge.weight;
      position = unit(
        add(spine, [normal() * width, normal() * width, normal() * width]),
      );
    } else if (i < 5050) {
      const node = webNodes[i % webNodes.length],
        width = 0.003 + random() ** 2 * 0.025;
      position = unit(
        add(node, [normal() * width, normal() * width, normal() * width]),
      );
    } else position = sphere();
    return {
      position,
      diffuse: sphere(),
      size: 0.28 + random() ** 3 * 0.65,
      warm: i > 3650 && i % 3 === 0,
      brightness: 0.24 + random() * 0.58,
      target: i % 3,
    };
  },
);
export function cosmicProjection(v: Vec3, turn: number): Vec3 {
  const x = v[0] * Math.cos(turn) + v[2] * Math.sin(turn),
    z = -v[0] * Math.sin(turn) + v[2] * Math.cos(turn);
  return [480 + 260 * x, 310 - 260 * v[1], z];
}

// Widely separated concentrations on the visible side of the schematic surface.
export const webHubs = (
  [
    [-0.65, -0.3, 0.7],
    [0.5, 0.55, 0.7],
    [0.6, -0.5, 0.7],
  ] as Vec3[]
).map((target) => {
  const t = unit(target);
  return webNodes.reduce(
    (best, v, i) => (dot(v, t) > dot(webNodes[best], t) ? i : best),
    0,
  );
});
