/** Artist-controlled geometry for the museum's conceptual bubble cycle.
 * These functions animate a visual analogy; they do not solve a field equation.
 */
export const PARTICLE_CYCLE_SECONDS = 46;
export const PARTICLE_SURFACE_Y = 344;
export const particleCyclePhases = [
  {
    name: 'Ripples',
    start: 0,
    end: 6,
    color: '#71e5eb',
    title: 'Ripples converge and reinforce one another.',
    copy: 'Two wave packets cross the surface. Their crests begin to align, building a localized disturbance through constructive interference.',
  },
  {
    name: 'Rogue wave',
    start: 6,
    end: 12,
    color: '#87edec',
    title: 'A rogue crest rises from the interference.',
    copy: 'The overlapping ripples concentrate into a tall, sharply localized wave. The crest reaches the strongest point of this illustrated cycle.',
  },
  {
    name: 'Separation',
    start: 12,
    end: 17,
    color: '#bda7f5',
    title: 'The crest narrows, then pinches off.',
    copy: 'A rounded cap grows at the crest. Its connecting neck thins until a bubble separates from the rippled surface.',
  },
  {
    name: 'Pilot waves',
    start: 17,
    end: 25,
    color: '#ffbc77',
    title: 'A bubble travels with its pilot waves.',
    copy: 'Waves pass through the transparent bubble while a connected ripple travels across the surface beneath it. A second bubble approaches.',
  },
  {
    name: 'Collision',
    start: 25,
    end: 30,
    color: '#ff9c91',
    title: 'Two bubbles meet at a collision event.',
    copy: 'The approaching bubbles compress at contact and form a brief joined configuration. The collision leads into an illustrated decay event.',
  },
  {
    name: 'Daughters',
    start: 30,
    end: 38,
    color: '#d2adff',
    title: 'Daughter bubbles separate and become unstable.',
    copy: 'Three daughter bubbles carry the outgoing disturbance. Each deforms and wobbles on its own rhythm; the first unstable boundary begins to rupture.',
  },
  {
    name: 'Return',
    start: 38,
    end: 46,
    color: '#71e5eb',
    title: 'The bubbles pop; ripples return to the surface.',
    copy: 'The remaining daughters rupture in sequence. Returning disturbances depict the proposed transfer of residual inertia to the surface, which settles back into the starting ripple pattern.',
  },
] as const;

export const cycleClamp = (value: number) => Math.max(0, Math.min(1, value));
export function cycleSmooth(value: number) {
  const t = cycleClamp(value);
  return t * t * (3 - 2 * t);
}
export const cycleTime = (seconds: number) =>
  ((seconds % PARTICLE_CYCLE_SECONDS) + PARTICLE_CYCLE_SECONDS) %
  PARTICLE_CYCLE_SECONDS;

export function particleCycleFrame(seconds: number) {
  const t = cycleTime(seconds);
  const phaseIndex = particleCyclePhases.findIndex((phase) => t < phase.end);
  const detach = cycleSmooth((t - 12) / 5);
  const travel = cycleSmooth((t - 17) / 8);
  const collision = cycleSmooth((t - 25) / 2.4);
  const daughterSpread = cycleSmooth((t - 29.3) / 5.7);
  const parentOpacity =
    cycleSmooth((t - 11.8) / 1.8) * (1 - cycleSmooth((t - 27.2) / 2.2));
  const parent = {
    x: 300 + 250 * travel + 27 * collision,
    y: 218 - 28 * detach + Math.sin(t * 1.6) * 5 * travel * (1 - collision),
    r: 34 + 10 * detach,
    opacity: parentOpacity,
    squeeze: collision * 0.28,
  };
  const incoming = {
    x: 900 - 295 * cycleSmooth((t - 21) / 6.4),
    y: 190 + Math.sin((t - 21) * 1.4) * 6 * (1 - collision),
    r: 37,
    opacity: cycleSmooth((t - 21) / 2) * (1 - cycleSmooth((t - 27.2) / 2.2)),
    squeeze: collision * 0.28,
  };
  const daughters = [
    { dx: -155, dy: -65, radius: 28, popAt: 35.6, color: '#71e5eb' },
    { dx: 55, dy: -96, radius: 32, popAt: 38, color: '#bda7f5' },
    { dx: 174, dy: 55, radius: 25, popAt: 40.4, color: '#ffbc77' },
  ].map((daughter, index) => {
    const pop = cycleSmooth((t - daughter.popAt) / 0.8);
    const x = 590 + daughter.dx * daughterSpread;
    const y = 190 + daughter.dy * daughterSpread;
    const returnProgress = cycleSmooth((t - daughter.popAt - 0.15) / 1.2);
    const ringAge = Math.max(0, t - daughter.popAt - 1.35);
    return {
      ...daughter,
      x,
      y,
      pop,
      returnProgress,
      r: daughter.radius * (0.6 + 0.4 * daughterSpread),
      opacity: cycleSmooth((t - 29.2) / 1.8) * (1 - pop),
      wobble: (0.035 + 0.105 * cycleSmooth((t - 32) / 3)) * (1 + index * 0.12),
      ruptureOpacity:
        t < daughter.popAt ? 0 : 1 - cycleSmooth((t - daughter.popAt) / 2.1),
      returnOpacity:
        cycleSmooth((t - daughter.popAt) / 0.3) *
        (1 - cycleSmooth((t - daughter.popAt - 1.5) / 2.2)),
      ringRadius: ringAge * 63,
      ringOpacity:
        cycleSmooth(ringAge / 0.45) *
        Math.exp(-ringAge * 0.48) *
        (1 - cycleSmooth((t - 43) / 3)),
    };
  });
  return {
    t,
    phaseIndex,
    phase: particleCyclePhases[phaseIndex],
    detach,
    travel,
    collision,
    crest: cycleSmooth((t - 2) / 10) * (1 - cycleSmooth((t - 12.2) / 3)),
    neck: cycleSmooth((t - 11.7) / 1) * (1 - cycleSmooth((t - 15.6) / 1.2)),
    parent,
    incoming,
    daughters,
    merge: cycleSmooth((t - 26.8) / 1.5) * (1 - cycleSmooth((t - 29.2) / 1.7)),
    packets: cycleSmooth(t / 1.5) * (1 - cycleSmooth((t - 11) / 4)),
  };
}

/** Periodic background with localized, gated crest/wake/return disturbances. */
export function particleSurfaceHeight(
  x: number,
  baseY: number,
  seconds: number | ReturnType<typeof particleCycleFrame>,
) {
  const f = typeof seconds === 'number' ? particleCycleFrame(seconds) : seconds;
  const phase = (f.t / PARTICLE_CYCLE_SECONDS) * Math.PI * 2;
  const depth = Math.exp(-(((baseY - PARTICLE_SURFACE_Y) / 47) ** 2));
  const baseline =
    Math.sin(x * 0.039 + baseY * 0.045 - phase * 12) * 3.6 +
    Math.cos(x * 0.022 - baseY * 0.073 + phase * 7) * 2.1;
  const approach = cycleSmooth(f.t / 9.2);
  const centers = [95 + 205 * approach, 850 - 550 * approach];
  const packets =
    centers.reduce(
      (sum, center) =>
        sum +
        Math.exp(-(((x - center) / 98) ** 2)) * Math.cos((x - center) * 0.055),
      0,
    ) *
    16 *
    f.packets *
    depth;
  const crest =
    156 *
    f.crest *
    Math.exp(-(((x - 300) / (44 - 10 * f.crest)) ** 2)) *
    depth ** 2;
  const pilot =
    Math.sin((x - f.parent.x) * 0.08 - f.t * 2.5) *
    Math.exp(-(((x - f.parent.x) / 100) ** 2)) *
    12 *
    f.travel *
    f.parent.opacity *
    depth;
  const returning = f.daughters.reduce((sum, daughter) => {
    const distance = Math.hypot(
      x - daughter.x,
      (baseY - PARTICLE_SURFACE_Y) * 2.5,
    );
    return (
      sum +
      Math.exp(-(((distance - daughter.ringRadius) / 30) ** 2)) *
        Math.cos((distance - daughter.ringRadius) * 0.1) *
        20 *
        daughter.ringOpacity
    );
  }, 0);
  return baseline + packets + crest + pilot + returning;
}

/** Closed, irregular membrane; use the same outline for fill and refraction clip. */
export function bubbleOutline(
  radius: number,
  wobble: number,
  time: number,
  seed = 0,
  squeeze = 0,
) {
  return (
    Array.from({ length: 81 }, (_, index) => {
      const angle = (index / 80) * Math.PI * 2;
      const distortion =
        1 +
        wobble * Math.sin(angle * 3 + time * (2.3 + seed * 0.31) + seed * 2) +
        wobble * 0.55 * Math.cos(angle * 5 - time * 1.7 + seed);
      const x = Math.cos(angle) * radius * distortion * (1 - squeeze);
      const y = Math.sin(angle) * radius * distortion * (1 + squeeze * 0.75);
      return `${index ? 'L' : 'M'}${x.toFixed(2)} ${y.toFixed(2)}`;
    }).join(' ') + 'Z'
  );
}
