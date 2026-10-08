'use client';
/* oxlint-disable jsx-a11y/prefer-tag-over-role -- A labeled inline SVG is the animated diagram. */
import { useId, type ReactNode } from 'react';
import { useSceneClock } from './science-console';

export type BigQuestionVisualKind =
  | 'geometry'
  | 'mass'
  | 'forces'
  | 'wave'
  | 'correlation'
  | 'uncertainty'
  | 'core'
  | 'expansion'
  | 'cycle'
  | 'darkmatter'
  | 'symmetry'
  | 'monopole'
  | 'test';

const GOLD = '#ffbc77';
const PURPLE = '#bda7f5';
const BLUE = '#71e5eb';
const FAINT = '#514763';
const TAU = Math.PI * 2;
const field = Array.from({ length: 96 }, (_, i) => ({
  x: 29 + ((i * 137.51) % 542),
  y: 25 + ((i * 83.19) % 268),
  phase: i * 1.71,
  color: [PURPLE, BLUE, GOLD][i % 3],
}));

const descriptions: Record<BigQuestionVisualKind, string> = {
  geometry: 'Linked geometric fibers rotate through a projected closed space.',
  mass: 'A localized bubble displaces the surrounding virtual particle field and contains a bound structure.',
  forces:
    'Three localized structures exchange moving geometric disturbances along connecting channels.',
  wave: 'A wave pattern meets a detector, illustrating modes and localized detection.',
  correlation:
    'Schematic correlated records; no calculated probabilities or communication channel.',
  uncertainty:
    'A localized packet and its reciprocal mode pattern trade width qualitatively.',
  core: 'Multiple geometric funnels meet one shared core.',
  expansion:
    'Distances between markers grow on a closed geometry; the illustration resets to repeat.',
  cycle:
    'Schematic field build-up and inward return precede an instantaneous whole-cosmos white-hole release. The faded restart is editorial replay, not a computed rebound.',
  darkmatter:
    'Visible matter is surrounded by a schematic collective geometric response.',
  symmetry:
    'Conjugate channels share exactly opposite phases in a schematic symmetry illustration.',
  monopole: 'Flux circulates along closed loops with no isolated endpoint.',
  test: 'Symbolic prediction and observation lanes illustrate comparison without numerical data.',
};

function description(kind: BigQuestionVisualKind, variant: string) {
  if (variant === 'light')
    return 'Schematic causal cone and light-like propagation; no computed speed or calibrated spacetime scale.';
  if (variant === 'spin')
    return 'Effective spinor illustration: a 360-degree transformation reverses the phase sign and 720 degrees restores it. The diagram shows phase, not an object rotating bodily.';
  if (
    kind === 'symmetry' &&
    (variant === 'cp-violation' || variant === 'matter-excess')
  )
    return 'Conjugate channels with a purely illustrative phase offset. The CP response and matter excess remain uncomputed.';
  return descriptions[kind];
}

function dot(
  x: number,
  y: number,
  color: string,
  key: string | number,
  r = 3.5,
  opacity = 1,
) {
  return (
    <circle key={key} cx={x} cy={y} r={r} fill={color} opacity={opacity} />
  );
}

function polyline(points: number[][]) {
  return points
    .map(([x, y], i) => `${i ? 'L' : 'M'}${x.toFixed(2)},${y.toFixed(2)}`)
    .join(' ');
}

function wavePath(
  x0: number,
  x1: number,
  y: number,
  amplitude: number,
  frequency: number,
  phase: number,
) {
  return polyline(
    Array.from({ length: 90 }, (_, i) => {
      const x = x0 + ((x1 - x0) * i) / 89;
      return [
        x,
        y +
          Math.sin(((x - x0) / (x1 - x0)) * TAU * frequency + phase) *
            amplitude,
      ];
    }),
  );
}

function arrow(
  x: number,
  y: number,
  angle: number,
  color: string,
  key: string | number,
) {
  return (
    <path
      key={key}
      d="M-8 -5L0 0L-8 5"
      transform={`translate(${x} ${y}) rotate(${angle})`}
      fill="none"
      stroke={color}
      strokeWidth="2"
    />
  );
}

function scene(
  kind: BigQuestionVisualKind,
  time: number,
  variant: string,
): ReactNode {
  if (variant === 'light') {
    const progress = (time * 0.18) % 1;
    const x = 118 * progress;
    const y = 100 * progress;
    return (
      <>
        <path
          d="M181 60L300 160L419 60ZM181 260L300 160L419 260Z"
          fill={PURPLE}
          fillOpacity=".1"
          stroke={PURPLE}
          strokeOpacity=".35"
        />
        <path
          d="M58 160H542M300 283V38"
          fill="none"
          stroke={FAINT}
          strokeWidth="1.5"
        />
        {arrow(542, 160, 0, FAINT, 'space')}
        {arrow(300, 38, -90, FAINT, 'time')}
        <path
          d="M181 60L300 160L419 60"
          fill="none"
          stroke={BLUE}
          strokeWidth="2"
        />
        <path
          d={`M${300 - x} ${160 - y}H${300 + x}`}
          stroke={BLUE}
          strokeWidth="1.2"
          opacity={0.7 * (1 - progress)}
        />
        {dot(300 - x, 160 - y, BLUE, 'left-light', 4, 1 - progress * 0.4)}
        {dot(300 + x, 160 - y, BLUE, 'right-light', 4, 1 - progress * 0.4)}
        <circle
          cx="300"
          cy="160"
          r="12"
          fill="none"
          stroke={GOLD}
          opacity=".4"
        />
        {dot(300, 160, GOLD, 'event', 5)}
        <text x="316" y="49" fill={PURPLE} fontSize="16">
          time
        </text>
        <text x="493" y="185" fill={PURPLE} fontSize="16">
          space
        </text>
      </>
    );
  }
  if (variant === 'spin') {
    // A phase diagram represents an effective spinor, never bodily rotation.
    const progress = (time % 12) / 12;
    const phase = progress * TAU;
    const phasePath = (imaginary: boolean) =>
      polyline(
        Array.from({ length: 91 }, (_, i) => {
          const a = (i * TAU) / 90;
          return [
            75 + i * 5,
            155 - (imaginary ? Math.sin(a) : Math.cos(a)) * 51,
          ];
        }),
      );
    return (
      <>
        <text x="300" y="49" textAnchor="middle" fill={PURPLE} fontSize="17">
          effective spinor phase
        </text>
        <path d="M63 155H537" stroke={FAINT} />
        {[75, 300, 525].map((x) => (
          <path
            key={x}
            d={`M${x} 85V224`}
            stroke={FAINT}
            strokeDasharray="3 7"
          />
        ))}
        <path
          d={phasePath(false)}
          stroke={GOLD}
          strokeWidth="2.4"
          fill="none"
        />
        <path
          d={phasePath(true)}
          stroke={BLUE}
          strokeWidth="1.8"
          fill="none"
          opacity=".55"
        />
        <path
          d={`M${75 + progress * 450} 85V224`}
          stroke={PURPLE}
          opacity=".5"
        />
        {dot(
          75 + progress * 450,
          155 - Math.cos(phase) * 51,
          GOLD,
          'real-phase',
          5,
        )}
        {dot(
          75 + progress * 450,
          155 - Math.sin(phase) * 51,
          BLUE,
          'imaginary-phase',
          4,
        )}
        <text x="75" y="253" textAnchor="middle" fill={GOLD} fontSize="16">
          0° · ψ
        </text>
        <text x="300" y="253" textAnchor="middle" fill={PURPLE} fontSize="16">
          360° · −ψ
        </text>
        <text x="525" y="253" textAnchor="middle" fill={GOLD} fontSize="16">
          720° · ψ
        </text>
      </>
    );
  }
  switch (kind) {
    case 'geometry': {
      return (
        <>
          <ellipse
            cx="300"
            cy="267"
            rx="139"
            ry="15"
            fill="none"
            stroke={FAINT}
            opacity=".5"
          />
          {Array.from({ length: 14 }, (_, f) => {
            const phi = (f * TAU) / 14;
            const eta = 0.63;
            const a = time * 0.17;
            const points = Array.from({ length: 68 }, (_, i) => {
              const u = (i * TAU) / 67;
              const d = 1 - Math.sin(eta) * Math.sin(u + phi);
              const x = (Math.cos(eta) * Math.cos(u)) / d;
              const y = (Math.cos(eta) * Math.sin(u)) / d;
              const z = (Math.sin(eta) * Math.cos(u + phi)) / d;
              const rotatedX = x * Math.cos(a) - z * Math.sin(a);
              const rotatedZ = x * Math.sin(a) + z * Math.cos(a);
              return [
                300 + rotatedX * 78,
                151 + (y * 0.65 + rotatedZ * 0.37) * 78,
              ];
            });
            return (
              <path
                key={f}
                d={polyline(points)}
                fill="none"
                stroke={[GOLD, PURPLE, BLUE][f % 3]}
                strokeWidth={f % 3 === 0 ? 1.7 : 1.1}
                opacity={f % 3 === 0 ? 0.8 : 0.43}
              />
            );
          })}
          <path
            d="M55 117H89M55 117V211H89M545 117H511M545 117V211H511"
            stroke={PURPLE}
            fill="none"
            opacity=".6"
          />
        </>
      );
    }
    case 'mass': {
      const radius = 91 + 3 * Math.sin(time * 0.9);
      return (
        <>
          {field.map((p, i) => {
            const dx = p.x - 300;
            const dy = p.y - 160;
            const distance = Math.hypot(dx, dy);
            const pushed =
              distance < radius + 12
                ? (radius + 12) / Math.max(distance, 1)
                : 1;
            return dot(
              300 + dx * pushed,
              160 + dy * pushed,
              p.color,
              i,
              1.3 + 0.6 * Math.sin(time * 2 + p.phase),
              0.25 + (0.22 * (1 + Math.sin(time * 1.3 + p.phase))) / 2,
            );
          })}
          <circle
            cx="300"
            cy="160"
            r={radius}
            fill="#120f22"
            fillOpacity=".76"
            stroke={GOLD}
            strokeWidth="2"
          />
          <circle
            cx="300"
            cy="160"
            r={radius + 7}
            fill="none"
            stroke={PURPLE}
            strokeWidth="1"
            strokeDasharray="2 7"
            opacity=".4"
          />
          {[1, 0.8, 0.6].map((scale, i) => (
            <ellipse
              key={scale}
              cx="300"
              cy="160"
              rx={67 * scale}
              ry={52 * scale}
              fill={BLUE}
              fillOpacity={0.025 + 0.015 * Math.sin(time + i)}
              stroke={BLUE}
              strokeOpacity=".18"
            />
          ))}
          <path
            d="M288 156L309 150L303 174Z"
            fill={PURPLE}
            fillOpacity=".13"
            stroke={PURPLE}
            strokeWidth="2"
          />
          {dot(288, 156, GOLD, 'q1', 6)}
          {dot(309, 150, BLUE, 'q2', 6)}
          {dot(303, 174, PURPLE, 'q3', 6)}
          {Array.from({ length: 32 }, (_, i) => {
            const a = i * 2.39996;
            const r = Math.sqrt((i + 0.5) / 32);
            return dot(
              300 + 65 * r * Math.cos(a),
              160 + 50 * r * Math.sin(a),
              BLUE,
              `cloud${i}`,
              1.6,
              0.14 + (0.15 * (1 + Math.sin(time * 0.6 + i))) / 2,
            );
          })}
          {[0, 1, 2, 3].map((i) => {
            const a = (i * TAU) / 4 + 0.4;
            return arrow(
              300 + (radius + 25) * Math.cos(a),
              160 + (radius + 25) * Math.sin(a),
              (a * 180) / Math.PI,
              GOLD,
              i,
            );
          })}
        </>
      );
    }
    case 'forces': {
      const nodes = [
        [140, 210],
        [300, 85],
        [460, 210],
      ];
      return (
        <>
          {[
            [0, 1],
            [1, 2],
            [2, 0],
          ].map(([a, b], i) => {
            const [ax, ay] = nodes[a];
            const [bx, by] = nodes[b];
            const cx = (ax + bx) / 2;
            const cy = (ay + by) / 2 + (i === 2 ? 44 : -28);
            const u = (time * 0.24 + i / 3) % 1;
            const x = (1 - u) ** 2 * ax + 2 * (1 - u) * u * cx + u ** 2 * bx;
            const y = (1 - u) ** 2 * ay + 2 * (1 - u) * u * cy + u ** 2 * by;
            return (
              <g key={i}>
                <path
                  d={`M${ax} ${ay}Q${cx} ${cy} ${bx} ${by}`}
                  fill="none"
                  stroke={[GOLD, BLUE, PURPLE][i]}
                  strokeWidth="2"
                  opacity=".5"
                />
                {dot(x, y, [GOLD, BLUE, PURPLE][i], 'pulse', 5)}
                <circle
                  cx={x}
                  cy={y}
                  r="11"
                  stroke={[GOLD, BLUE, PURPLE][i]}
                  fill="none"
                  opacity=".3"
                />
              </g>
            );
          })}
          {nodes.map(([x, y], i) => (
            <g key={i}>
              <circle
                cx={x}
                cy={y}
                r={28 + 2 * Math.sin(time * 1.4 + i)}
                fill="#141124"
                stroke={[GOLD, PURPLE, BLUE][i]}
                strokeWidth="1.7"
              />
              {dot(x, y, [GOLD, PURPLE, BLUE][i], 'node', 7)}
              <circle cx={x} cy={y} r="15" fill="none" stroke={FAINT} />
            </g>
          ))}
        </>
      );
    }
    case 'wave': {
      if (variant === 'double-slit')
        return (
          <>
            {[0, 1, 2, 3].map((i) => (
              <path
                key={i}
                d={`M${64 + ((time * 25 + i * 37) % 149)} 68V252`}
                stroke={BLUE}
                opacity=".35"
              />
            ))}
            <path
              d="M225 54V117M225 135V185M225 203V266"
              stroke={PURPLE}
              strokeWidth="9"
            />
            {[126, 194].map((y) => (
              <g key={y}>
                {Array.from({ length: 6 }, (_, i) => {
                  const r = (time * 31 + i * 42) % 252;
                  return (
                    <path
                      key={i}
                      d={`M225 ${y - r}A${r} ${r} 0 0 1 225 ${y + r}`}
                      fill="none"
                      stroke={y === 126 ? GOLD : BLUE}
                      opacity={0.5 * (1 - r / 260)}
                    />
                  );
                })}
              </g>
            ))}
            <rect
              x="498"
              y="56"
              width="13"
              height="208"
              rx="4"
              fill="#20182a"
              stroke={PURPLE}
            />
            {Array.from({ length: 25 }, (_, i) => (
              <circle
                key={i}
                cx="504.5"
                cy={65 + i * 8}
                r="2.8"
                fill={GOLD}
                opacity={
                  0.1 +
                  0.75 *
                    Math.cos((i - 12) * 0.7) ** 2 *
                    Math.exp(-(((i - 12) / 12) ** 2))
                }
              />
            ))}
          </>
        );
      const pulse = (time * 0.45) % 1;
      return (
        <>
          <path d="M65 160H483" stroke={FAINT} strokeDasharray="3 8" />
          {[0, 1, 2].map((i) => (
            <path
              key={i}
              d={wavePath(72, 456, 160, 25 + i * 11, 3, -time * 2.2 + i * 0.38)}
              fill="none"
              stroke={[GOLD, PURPLE, BLUE][i]}
              strokeWidth={i === 0 ? 2.3 : 1.2}
              opacity={i === 0 ? 0.85 : 0.4}
            />
          ))}
          <rect
            x="482"
            y="74"
            width="17"
            height="172"
            rx="4"
            fill="#20182a"
            stroke={PURPLE}
          />
          {[0, 1, 2, 3, 4, 5, 6].map((i) => (
            <circle
              key={i}
              cx="490.5"
              cy={91 + i * 23}
              r="3"
              fill={BLUE}
              opacity={0.2 + 0.7 * Math.max(0, Math.sin(time * 2.2 - i * 0.9))}
            />
          ))}
          {dot(
            74 + pulse * 405,
            160 + 25 * Math.sin(pulse * TAU * 3 - time * 2.2),
            GOLD,
            'wave-marker',
            4,
          )}
          <circle
            cx="530"
            cy="160"
            r={9 + 15 * pulse}
            fill="none"
            stroke={GOLD}
            opacity={1 - pulse}
          />
          {dot(530, 160, GOLD, 'event', 5, 0.4 + 0.6 * (1 - pulse))}
        </>
      );
    }
    case 'correlation': {
      const angle = 28 * Math.sin(time * 0.8);
      return (
        <>
          <path
            d="M184 160C250 103 350 103 416 160M184 160C250 217 350 217 416 160"
            fill="none"
            stroke={PURPLE}
            strokeDasharray="3 7"
            opacity=".32"
          />
          {[160, 440].map((x, i) => (
            <g key={i}>
              <circle
                cx={x}
                cy="160"
                r="52"
                fill="#171225"
                stroke={i ? BLUE : GOLD}
                strokeWidth="1.8"
              />
              <circle
                cx={x}
                cy="160"
                r="66"
                fill="none"
                stroke={PURPLE}
                opacity=".23"
              />
              <g
                transform={`translate(${x} 160) rotate(${angle + (i ? 180 : 0)})`}
              >
                <path
                  d="M0 30V-30M-7 -20L0 -30L7 -20"
                  fill="none"
                  stroke={i ? BLUE : GOLD}
                  strokeWidth="3"
                />
                {dot(0, 0, PURPLE, 'state', 5)}
              </g>
            </g>
          ))}
          <path
            d="M285 151H315M285 169H315"
            stroke={PURPLE}
            strokeWidth="3"
            opacity=".7"
          />
        </>
      );
    }
    case 'uncertainty': {
      const spread = 37 + (23 * (1 + Math.sin(time * 0.8))) / 2;
      const reciprocal = 1900 / spread;
      const packet = (cx: number, width: number, carrier: number) =>
        polyline(
          Array.from({ length: 101 }, (_, i) => {
            const x = cx - 112 + i * 2.24;
            const envelope = Math.exp(-(((x - cx) / width) ** 2) / 2);
            return [
              x,
              159 -
                envelope *
                  (carrier ? Math.cos((x - cx) / carrier - time) : 1) *
                  60,
            ];
          }),
        );
      return (
        <>
          <rect
            x="42"
            y="63"
            width="235"
            height="194"
            rx="16"
            fill="#100d1b"
            stroke={FAINT}
          />
          <rect
            x="323"
            y="63"
            width="235"
            height="194"
            rx="16"
            fill="#100d1b"
            stroke={FAINT}
          />
          <path d="M58 160H261M339 160H542" stroke={FAINT} />
          <path
            d={packet(159, spread, 0)}
            fill="none"
            stroke={GOLD}
            strokeWidth="2.5"
          />
          <path
            d={packet(440, reciprocal, 7)}
            fill="none"
            stroke={BLUE}
            strokeWidth="2.3"
          />
          <path
            d={`M${159 - spread} 222H${159 + spread}M${440 - reciprocal} 222H${440 + reciprocal}`}
            stroke={PURPLE}
            strokeWidth="2"
          />
          <path
            d="M287 149L300 136L313 149M300 136V181M287 170L300 183L313 170"
            fill="none"
            stroke={PURPLE}
            opacity=".7"
          />
        </>
      );
    }
    case 'core': {
      return (
        <>
          {Array.from({ length: 9 }, (_, i) => {
            const a = (i * TAU) / 9 - Math.PI / 2;
            const x = 300 + 205 * Math.cos(a);
            const y = 160 + 111 * Math.sin(a);
            const cx = 300 + 100 * Math.cos(a + 0.4);
            const cy = 160 + 90 * Math.sin(a + 0.4);
            const u = (time * 0.2 + i / 9) % 1;
            const qx = (1 - u) ** 2 * x + 2 * (1 - u) * u * cx + u ** 2 * 300;
            const qy = (1 - u) ** 2 * y + 2 * (1 - u) * u * cy + u ** 2 * 160;
            return (
              <g key={i}>
                <path
                  d={`M${x} ${y}Q${cx} ${cy} 300 160`}
                  fill="none"
                  stroke={i % 2 ? PURPLE : BLUE}
                  strokeWidth="1.5"
                  opacity=".5"
                />
                <ellipse
                  cx={x}
                  cy={y}
                  rx="17"
                  ry="9"
                  fill="#181225"
                  stroke={PURPLE}
                  transform={`rotate(${(a * 180) / Math.PI} ${x} ${y})`}
                />
                {dot(qx, qy, i % 2 ? PURPLE : BLUE, 'inflow', 3.5)}
              </g>
            );
          })}
          <circle
            cx="300"
            cy="160"
            r={22 + Math.sin(time * 2)}
            fill="#3b2534"
            stroke={GOLD}
            strokeWidth="2"
          />
          <circle
            cx="300"
            cy="160"
            r="36"
            fill="none"
            stroke={GOLD}
            opacity=".25"
          />
          {dot(300, 160, GOLD, 'core', 6)}
        </>
      );
    }
    case 'expansion': {
      const phase = (time % 10) / 10;
      const scale = 0.62 + phase * 0.38;
      const fade =
        phase > 0.91
          ? (1 - phase) / 0.09
          : phase < 0.06
            ? 0.35 + (phase / 0.06) * 0.65
            : 1;
      const rx = 220 * scale;
      const ry = 121 * scale;
      return (
        <g opacity={fade}>
          <ellipse
            cx="300"
            cy="160"
            rx={rx}
            ry={ry}
            fill="#181126"
            fillOpacity=".45"
            stroke={PURPLE}
            strokeWidth="1.8"
          />
          {[0.25, 0.5, 0.8].map((v) => (
            <ellipse
              key={v}
              cx="300"
              cy="160"
              rx={rx * v}
              ry={ry}
              fill="none"
              stroke={PURPLE}
              opacity=".22"
            />
          ))}
          {[0.32, 0.65].map((v) => (
            <ellipse
              key={v}
              cx="300"
              cy="160"
              rx={rx}
              ry={ry * v}
              fill="none"
              stroke={BLUE}
              opacity=".25"
            />
          ))}
          {Array.from({ length: 10 }, (_, i) => {
            const a = (i * TAU) / 10;
            return dot(
              300 + rx * 0.85 * Math.cos(a),
              160 + ry * 0.85 * Math.sin(a),
              i % 2 ? BLUE : GOLD,
              i,
              4,
            );
          })}
          <path
            d={`M${300 - rx * 0.69} ${160 - ry * 0.5}H${300 + rx * 0.69}`}
            stroke={GOLD}
            strokeDasharray="3 6"
            opacity=".55"
          />
          {arrow(300 - rx - 16, 160, 180, GOLD, 'left')}
          {arrow(300 + rx + 16, 160, 0, GOLD, 'right')}
        </g>
      );
    }
    case 'cycle': {
      const phase = (time % 12) / 12;
      const inward = Math.min(1, Math.max(0, (phase - 0.45) / 0.3)) * 0.9;
      const release = phase >= 0.81;
      const web =
        phase < 0.75
          ? Math.max(0, Math.sin((phase - 0.12) * Math.PI * 1.3))
          : 0;
      // Hold the returned structure; flash the whole surface together. The fade
      // permits an editorial restart without animating a physical rebound.
      const fade = phase > 0.93 ? (1 - phase) / 0.07 : 1;
      return (
        <g opacity={fade}>
          {Array.from({ length: 24 }, (_, i) => {
            const a = (i * TAU) / 24;
            const radius = 1 - inward;
            const x = 300 + 201 * radius * Math.cos(a);
            const y = 160 + 116 * radius * Math.sin(a);
            const next = ((i + 7) * TAU) / 24;
            return (
              <g key={i} opacity={release ? 0 : phase >= 0.75 ? 0.2 : 1}>
                <path
                  d={`M${x} ${y}L${300 + 201 * radius * Math.cos(next)} ${160 + 116 * radius * Math.sin(next)}`}
                  stroke={PURPLE}
                  opacity={web * 0.16}
                />
                {dot(x, y, [BLUE, PURPLE, GOLD][i % 3], 'field', 2.7, 0.6)}
              </g>
            );
          })}
          <ellipse
            cx="300"
            cy="160"
            rx="217"
            ry="128"
            fill="none"
            stroke={FAINT}
            strokeDasharray="2 8"
          />
          <circle
            cx="300"
            cy="160"
            r={10 + inward * 25}
            fill={GOLD}
            opacity={release ? 0 : phase >= 0.75 ? 0.08 : 0.2 + inward * 0.55}
          />
          {release && (
            <ellipse
              cx="300"
              cy="160"
              rx="217"
              ry="128"
              fill="#fff5df"
              fillOpacity=".46"
              stroke={GOLD}
              strokeWidth="2"
              data-release="whole-cosmos"
            />
          )}
        </g>
      );
    }
    case 'darkmatter': {
      return (
        <>
          {[1, 1.35, 1.72, 2.14].map((v, i) => (
            <ellipse
              key={v}
              cx="300"
              cy="161"
              rx={96 * v + 2 * Math.sin(time + i)}
              ry={43 * v + 2 * Math.cos(time + i)}
              fill="none"
              stroke={PURPLE}
              strokeWidth={i ? 1.2 : 2}
              opacity={0.47 - i * 0.07}
              transform={`rotate(-15 300 161)`}
            />
          ))}
          <ellipse
            cx="300"
            cy="161"
            rx="91"
            ry="37"
            fill="#3f2534"
            fillOpacity=".32"
            transform="rotate(-15 300 161)"
          />
          <g transform="rotate(-15 300 161)">
            {Array.from({ length: 48 }, (_, i) => {
              const a = i * 2.39996 + time * 0.1;
              const r = Math.sqrt((i + 1) / 49);
              return dot(
                300 + r * 88 * Math.cos(a),
                161 + r * 35 * Math.sin(a),
                i % 4 ? GOLD : BLUE,
                i,
                i % 4 ? 1.7 : 2.4,
                0.75,
              );
            })}
            {Array.from({ length: 8 }, (_, i) => {
              const a = (i * TAU) / 8 + time * 0.15;
              return arrow(
                300 + 179 * Math.cos(a),
                161 + 78 * Math.sin(a),
                (Math.atan2(78 * Math.cos(a), -179 * Math.sin(a)) * 180) /
                  Math.PI,
                PURPLE,
                `response${i}`,
              );
            })}
          </g>
          {dot(300, 161, GOLD, 'visible-core', 6)}
        </>
      );
    }
    case 'symmetry': {
      const sharedPhase = time * 1.1;
      const cpOffset =
        variant === 'cp-violation' || variant === 'matter-excess' ? 0.85 : 0;
      return (
        <>
          <path d="M300 49V271" stroke={FAINT} strokeDasharray="3 7" />
          {[0, 1].map((side) => {
            const cx = side ? 441 : 159;
            const phase = side ? -sharedPhase + cpOffset : sharedPhase;
            return (
              <g key={side} data-conjugate-phase={phase.toFixed(4)}>
                <circle
                  cx={cx}
                  cy="160"
                  r="79"
                  fill="none"
                  stroke={PURPLE}
                  opacity=".3"
                />
                <ellipse
                  cx={cx}
                  cy="160"
                  rx="62"
                  ry="25"
                  fill="none"
                  stroke={side ? BLUE : GOLD}
                  transform={`rotate(${side ? -35 : 35} ${cx} 160)`}
                  opacity=".7"
                />
                <path
                  d={wavePath(cx - 92, cx + 92, 160, 34, 2, phase)}
                  fill="none"
                  stroke={side ? BLUE : GOLD}
                  strokeWidth="2"
                />
                {dot(
                  cx + 62 * Math.cos(phase),
                  160 + 25 * Math.sin(phase),
                  side ? BLUE : GOLD,
                  'phase',
                  4.5,
                )}
                {dot(cx, 160, PURPLE, 'channel', 4)}
              </g>
            );
          })}
          <path d="M281 38H319M281 282H319" stroke={PURPLE} opacity=".5" />
        </>
      );
    }
    case 'monopole': {
      return (
        <>
          <rect
            x="252"
            y="124"
            width="96"
            height="72"
            rx="20"
            fill="#1b1424"
            stroke={PURPLE}
          />
          <path d="M300 125V195" stroke={FAINT} />
          {[0, 1, 2, 3, 4].map((i) => {
            const rx = 88 + i * 30;
            const ry = 57 + i * 17;
            const a = time * 0.6 + i * 0.6;
            return (
              <g key={i}>
                <ellipse
                  cx="300"
                  cy="160"
                  rx={rx}
                  ry={ry}
                  fill="none"
                  stroke={i % 2 ? PURPLE : BLUE}
                  strokeWidth="1.4"
                  opacity={0.7 - i * 0.1}
                />
                {dot(
                  300 + rx * Math.cos(a),
                  160 + ry * Math.sin(a),
                  i % 2 ? PURPLE : BLUE,
                  'flux',
                  3.4,
                )}
                {arrow(300, 160 - ry, 0, i % 2 ? PURPLE : BLUE, 'direction')}
              </g>
            );
          })}
          {dot(277, 160, GOLD, 'left', 7)}
          {dot(323, 160, BLUE, 'right', 7)}
        </>
      );
    }
    case 'test': {
      if (variant === 'collisions') {
        const phase = (time % 7) / 7;
        const incoming = Math.min(1, phase * 2);
        const outgoing = Math.max(0, (phase - 0.5) * 2);
        return (
          <>
            <path
              d="M80 160H300L520 76M300 160L520 244"
              fill="none"
              stroke={FAINT}
              strokeDasharray="4 8"
            />
            <path
              d="M520 160H300"
              fill="none"
              stroke={FAINT}
              strokeDasharray="4 8"
            />
            <circle
              cx="300"
              cy="160"
              r={25 + 8 * Math.sin(phase * Math.PI)}
              fill="#3b2534"
              fillOpacity=".35"
              stroke={PURPLE}
            />
            {phase < 0.5 ? (
              <>
                {dot(80 + incoming * 220, 160, GOLD, 'incoming-left', 8)}
                {dot(520 - incoming * 220, 160, BLUE, 'incoming-right', 8)}
              </>
            ) : (
              <>
                {dot(
                  300 + outgoing * 220,
                  160 - outgoing * 84,
                  GOLD,
                  'outgoing-up',
                  7,
                )}
                {dot(
                  300 + outgoing * 220,
                  160 + outgoing * 84,
                  BLUE,
                  'outgoing-down',
                  7,
                )}
              </>
            )}
          </>
        );
      }
      // These are symbolic comparison lanes, not a chart of BHSM results.
      const scanner = (time * 0.14) % 1;
      return (
        <>
          <path
            d="M74 68V260H533"
            fill="none"
            stroke={FAINT}
            strokeWidth="1.5"
          />
          {[0, 1, 2].map((i) => {
            const y = 90 + i * 68;
            return (
              <g key={i}>
                <rect
                  x="104"
                  y={y}
                  width="377"
                  height="18"
                  rx="4"
                  fill="none"
                  stroke={FAINT}
                  strokeDasharray="4 5"
                />
                <rect
                  x="104"
                  y={y}
                  width="225"
                  height="7"
                  rx="2"
                  fill={PURPLE}
                  opacity=".6"
                />
                <rect
                  x="104"
                  y={y + 11}
                  width="225"
                  height="7"
                  rx="2"
                  fill={GOLD}
                  opacity=".6"
                />
                <path
                  d={`M${104 + scanner * 377} ${y - 5}V${y + 23}`}
                  stroke={BLUE}
                  strokeWidth="1.5"
                  opacity=".8"
                />
                <circle
                  cx="515"
                  cy={y + 9}
                  r="10"
                  fill="none"
                  stroke={BLUE}
                  opacity={0.35 + 0.2 * Math.sin(time + i)}
                />
                <path
                  d={`M511 ${y + 9}H519M515 ${y + 5}V${y + 13}`}
                  stroke={BLUE}
                  opacity=".65"
                />
              </g>
            );
          })}
        </>
      );
    }
  }
}

export function BigQuestionVisual({
  motion,
  kind,
  variant,
}: {
  motion: boolean;
  kind: BigQuestionVisualKind;
  variant: string;
}) {
  const { ref, time } = useSceneClock(motion);
  const id = useId().replace(/:/g, '');
  // A paused scene keeps its current frame. Initial reduced-motion visits get a useful still.
  const frameTime = time || (motion ? 0 : 3.5);
  return (
    <div
      ref={ref}
      className={`question-visual question-visual-${kind}`}
      data-question={variant}
      data-clock={time.toFixed(2)}
      data-motion={motion ? 'playing' : 'paused'}
    >
      <svg
        viewBox="0 0 600 320"
        role="img"
        aria-label={`${description(kind, variant)} Conceptual illustration, not a computed physical prediction.`}
        style={{ display: 'block', width: '100%', height: 'auto' }}
      >
        <defs>
          <radialGradient id={`${id}-halo`}>
            <stop stopColor="#342345" stopOpacity=".5" />
            <stop offset="1" stopColor="#08070d" stopOpacity="0" />
          </radialGradient>
        </defs>
        <rect width="600" height="320" fill="#09080e" rx="18" />
        <ellipse
          cx="300"
          cy="160"
          rx="284"
          ry="148"
          fill={`url(#${id}-halo)`}
        />
        <path
          d="M30 30H48M30 30V48M570 30H552M570 30V48M30 290H48M30 290V272M570 290H552M570 290V272"
          fill="none"
          stroke={FAINT}
          opacity=".65"
        />
        {scene(kind, frameTime, variant)}
      </svg>
    </div>
  );
}
