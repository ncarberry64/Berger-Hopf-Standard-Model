'use client';
/* oxlint-disable jsx-a11y/prefer-tag-over-role -- Inline SVG carries the accessible scene description. */
import { useState } from 'react';
import { useSceneClock } from './science-console';

// Presentation coordinates and timing only; no fitted mass or QCD dynamics.
const sea = Array.from({ length: 360 }, (_, i) => ({
  x: 22 + ((i * 173) % 636),
  y: 72 + ((i * 97) % 238),
  phase: i * 2.39996,
}));
const colors = ['#ff806e', '#83e6ac', '#78baff'];
const births = [
  [188, 122],
  [486, 116],
  [418, 280],
];
const clamp = (v: number) => Math.max(0, Math.min(1, v));
const smooth = (v: number) => {
  const x = clamp(v);
  return x * x * (3 - 2 * x);
};
const mix = (a: number, b: number, t: number) => a + (b - a) * t;

// Bounded illustrative paths in the proton's fixed center frame.
function boundQuarks(t: number) {
  const raw = [0, 1, 2].map((i) => {
    const phase = (i * Math.PI * 2) / 3;
    return [
      26 * Math.cos(t * 2.1 + phase) + 7 * Math.sin(t * 3.7 + phase),
      21 * Math.sin(t * 2.5 + phase) + 5 * Math.cos(t * 4.1 + phase),
    ];
  });
  const cx = raw.reduce((sum, p) => sum + p[0], 0) / 3;
  const cy = raw.reduce((sum, p) => sum + p[1], 0) / 3;
  return raw.map(([x, y]) => [340 + x - cx, 196 + y - cy]);
}

export function MassVisual({ motion }: { motion: boolean }) {
  const [playing, setPlaying] = useState(true);
  const [view, setView] = useState<'formation' | 'internal' | 'atom'>(
    'formation',
  );
  const [startedAt, setStartedAt] = useState(0);
  const { ref, time } = useSceneClock(motion && playing);
  // Hold the completed atom. Replay explicitly returns to the field-only start.
  const elapsed = Math.min(22, Math.max(0, time - startedAt));
  const t =
    view === 'internal' ? 8.8 : view === 'atom' || !motion ? 22 : elapsed;
  const emergence = colors.map((_, i) => smooth((t - 2.5 - i * 0.55) / 0.7));
  const gathering = smooth((t - 4.8) / 3.1);
  const bonds = smooth((t - 5.2) / 2.5);
  const merged = smooth((t - 6.8) / 2.2);
  const proton = smooth((t - 9.2) / 1.4);
  const electron = smooth((t - 12) / 0.8);
  const attraction = smooth((t - 13) / 3.5);
  const atom = smooth((t - 16.5) / 1.5);
  const target = boundQuarks(time);
  const quarks = target.map(([x, y], i) => [
    mix(births[i][0], x, gathering),
    mix(births[i][1], y, gathering),
  ]);
  const rx = mix(82, 152, atom) * merged;
  const ry = mix(64, 105, atom) * merged;
  const localRadii = emergence.map((e) => 26 * e * (1 - merged));
  const stage =
    t < 2.5
      ? 'field'
      : t < 4.8
        ? 'quarks'
        : t < 9.2
          ? 'binding'
          : t < 12
            ? 'proton'
            : t < 13
              ? 'electron'
              : t < 18
                ? 'capture'
                : 'atom';
  const caption = {
    field: '01 · The virtual particle field alone',
    quarks: '02 · Quarks emerge and clear space',
    binding: '03 · Quarks bind into a shared bubble',
    proton: '04 · The bound system is a proton',
    electron: '05 · An electron emerges from the field',
    capture: '06 · Attraction brings the electron inward',
    atom: '07 · Hydrogen: the bubble holds the field back',
  }[stage];
  const electronX = mix(558, 440, attraction);
  const electronY =
    mix(106, 215, attraction) - 40 * Math.sin(attraction * Math.PI);

  function replay() {
    setStartedAt(time);
    setView('formation');
    setPlaying(true);
  }

  return (
    <div
      className="mass-visual"
      ref={ref}
      data-stage={stage}
      data-formation-time={t.toFixed(2)}
    >
      <svg
        viewBox="0 0 680 390"
        role="img"
        aria-label="BHSM conceptual mass sequence: virtual particle field alone; quarks emerge, clear space and bind into a proton; one electron emerges from the field, is attracted and binds into a hydrogen atom. The mass bubble holds back the surrounding field."
      >
        <defs>
          <radialGradient id="mass-cloud">
            <stop stopColor="#83dcff" stopOpacity=".05" />
            <stop offset=".45" stopColor="#8cbaff" stopOpacity=".26" />
            <stop offset=".8" stopColor="#72dcff" stopOpacity=".12" />
            <stop offset="1" stopColor="#72dcff" stopOpacity="0" />
          </radialGradient>
          <radialGradient id="mass-boundary">
            <stop stopColor="#100d1b" />
            <stop offset=".88" stopColor="#141223" />
            <stop offset="1" stopColor="#ffc77e" stopOpacity=".25" />
          </radialGradient>
          <radialGradient id="mass-nucleus">
            <stop stopColor="#ffe5bb" />
            <stop offset=".45" stopColor="#d7a1a1" />
            <stop offset=".8" stopColor="#6779b6" />
            <stop offset="1" stopColor="#20263f" />
          </radialGradient>
        </defs>
        <rect width="680" height="390" rx="12" fill="#05080f" />
        <text x="24" y="30" fill="#ffcf99" fontSize="15">
          BHSM · MASS HOLDS BACK THE FIELD
        </text>
        <text x="24" y="54" fill="#d0cbdf" fontSize="14">
          {caption}
        </text>
        {merged > 0 && (
          <ellipse
            className="mass-bubble"
            cx="340"
            cy="196"
            rx={rx}
            ry={ry}
            fill="url(#mass-boundary)"
            stroke="#fbc884"
            strokeWidth="2"
            strokeOpacity=".8"
          />
        )}
        {quarks.map(
          ([x, y], i) =>
            localRadii[i] > 0 && (
              <circle
                key={i}
                className="mass-quark-bubble"
                cx={x}
                cy={y}
                r={localRadii[i]}
                fill="#141223"
                stroke={colors[i]}
                strokeOpacity={emergence[i] * (1 - merged) * 0.65}
              />
            ),
        )}
        {sea.map((p, i) => {
          let x = p.x + 5 * Math.sin(time * 0.8 + p.phase);
          let y = p.y + 4 * Math.cos(time * 0.7 + p.phase);
          // Growing bubbles push nearby field marks toward the boundary.
          for (let j = 0; j < 3; j++) {
            const [qx, qy] = quarks[j];
            const r = localRadii[j];
            const dx = x - qx,
              dy = y - qy;
            const distance = Math.hypot(dx, dy);
            if (r > 0 && distance < r + 3) {
              const angle = distance > 0.01 ? Math.atan2(dy, dx) : p.phase;
              x = qx + (r + 3) * Math.cos(angle);
              y = qy + (r + 3) * Math.sin(angle);
            }
          }
          if (rx > 0 && ry > 0) {
            const dx = (x - 340) / rx,
              dy = (y - 196) / ry;
            const distance = Math.hypot(dx, dy);
            if (distance < 1.05) {
              const angle = distance > 0.01 ? Math.atan2(dy, dx) : p.phase;
              x = 340 + rx * 1.05 * Math.cos(angle);
              y = 196 + ry * 1.05 * Math.sin(angle);
            }
          }
          const lifetime = 2.4 + (i % 7) * 0.29;
          const age = (time + p.phase) % lifetime;
          const alpha = smooth(age / 0.18) * (1 - smooth((age - 0.65) / 0.22));
          if (alpha <= 0) return null;
          return (
            <circle
              className="mass-vacuum-mark"
              key={i}
              cx={x}
              cy={y}
              r={i % 3 === 0 ? 1.9 : 1.1}
              fill="#dfc896"
              opacity={alpha * 0.8}
            />
          );
        })}
        <g className="mass-internal-motion" opacity={1 - proton}>
          {bonds > 0 &&
            quarks.map(([x, y], i) => {
              const [xx, yy] = quarks[(i + 1) % 3];
              const dx = xx - x,
                dy = yy - y;
              const length = Math.max(1, Math.hypot(dx, dy));
              const d = Array.from({ length: 45 }, (_, n) => {
                const u = n / 44;
                const wiggle =
                  4 *
                  Math.sin(u * Math.PI * 12 - time * 4) *
                  Math.sin(u * Math.PI);
                return `${n ? 'L' : 'M'}${x + u * dx - (wiggle * dy) / length},${y + u * dy + (wiggle * dx) / length}`;
              }).join(' ');
              return (
                <path
                  className="mass-color-bond"
                  key={i}
                  d={d}
                  fill="none"
                  stroke={colors[i]}
                  strokeWidth="2.5"
                  opacity={bonds}
                />
              );
            })}
          {quarks.map(
            ([x, y], i) =>
              emergence[i] > 0 && (
                <g
                  className="mass-quark"
                  key={i}
                  opacity={emergence[i]}
                  transform={`translate(${x} ${y})`}
                >
                  <circle r="18" fill={colors[i]} fillOpacity=".15" />
                  <circle r="10" fill={colors[i]} />
                  <text
                    y="4"
                    textAnchor="middle"
                    fill="#07101c"
                    fontSize="13"
                    fontWeight="bold"
                  >
                    {i === 2 ? 'd' : 'u'}
                  </text>
                </g>
              ),
          )}
        </g>
        <g className="mass-stable-nucleus" opacity={proton}>
          <circle
            cx="340"
            cy="196"
            r="47"
            fill="url(#mass-nucleus)"
            stroke="#ddd5eb"
            strokeWidth="1.5"
          />
          <text
            x="340"
            y="193"
            textAnchor="middle"
            fill="#101323"
            fontSize="16"
            fontWeight="bold"
          >
            PROTON
          </text>
          <text
            x="340"
            y="213"
            textAnchor="middle"
            fill="#101323"
            fontSize="14"
          >
            uud · +1
          </text>
        </g>
        <g className="mass-electron-arrival" opacity={electron * (1 - atom)}>
          <circle
            cx="558"
            cy="106"
            r={12 + 15 * electron}
            fill="none"
            stroke="#95cfff"
            strokeDasharray="2 4"
            opacity={1 - attraction}
          />
          <path
            d="M558 106 Q459 41 440 215"
            fill="none"
            stroke="#95cfff"
            strokeDasharray="3 7"
            opacity={0.5 * attraction * (1 - attraction)}
          />
          <circle
            cx={electronX}
            cy={electronY}
            r="16"
            fill="#95cfff"
            fillOpacity=".15"
          />
          <circle cx={electronX} cy={electronY} r="7" fill="#95cfff" />
          <text
            x={electronX + 14}
            y={electronY + 5}
            fill="#b5e3ff"
            fontSize="16"
          >
            e⁻
          </text>
        </g>
        <g className="mass-electron-cloud" opacity={atom}>
          <ellipse cx="340" cy="196" rx="143" ry="96" fill="url(#mass-cloud)" />
          <ellipse
            cx="340"
            cy="196"
            rx="117"
            ry="78"
            fill="none"
            stroke="#95cfff"
            strokeDasharray="2 5"
            opacity=".25"
          />
          <text
            x="340"
            y="281"
            textAnchor="middle"
            fill="#b5e3ff"
            fontSize="14"
          >
            Bound electron · 1s probability cloud
          </text>
        </g>
        <text
          x="340"
          y="335"
          textAnchor="middle"
          fill="#ffcf99"
          fontSize="16"
          opacity={atom}
        >
          HYDROGEN ATOM · 1 proton + 1 electron
        </text>
        <text x="24" y="364" fill="#dfc896" fontSize="14">
          Virtual particle field · conceptual view
        </text>
        <text
          x="655"
          y="364"
          textAnchor="end"
          fill="#ffcf99"
          fontSize="14"
          opacity={merged}
        >
          Bubble = field held back
        </text>
      </svg>
      <div className="mass-visual-key">
        <span>● Quarks + color bonds</span>
        <span>◌ Bound electron probability cloud</span>
        <span>○ Mass bubble holding back the field</span>
      </div>
      <div
        className="console-selector"
        aria-label="Mass formation and viewing frame"
      >
        <button aria-pressed={view === 'formation'} onClick={replay}>
          Replay formation
        </button>
        <button
          aria-pressed={view === 'internal'}
          onClick={() => setView('internal')}
        >
          Inside the proton
        </button>
        <button aria-pressed={view === 'atom'} onClick={() => setView('atom')}>
          Hydrogen atom
        </button>
      </div>
      <button
        className="evidence-play"
        onClick={() => setPlaying(!playing)}
        disabled={!motion}
      >
        {!motion
          ? 'Still view · animation off'
          : playing
            ? 'Pause mass animation'
            : 'Play mass animation'}
      </button>
    </div>
  );
}
