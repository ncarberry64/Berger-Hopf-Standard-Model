'use client';
/* oxlint-disable jsx-a11y/prefer-tag-over-role -- Inline SVG carries the accessible scene description. */
import { useState } from 'react';
import { useSceneClock } from './science-console';

// Fixed sampling and presentation coordinates; no fitted mass or QCD dynamics.
const sea = Array.from({ length: 360 }, (_, i) => ({
  x: 22 + ((i * 173) % 636),
  y: 48 + ((i * 97) % 290),
  phase: i * 2.39996,
}));
const colors = ['#ff806e', '#83e6ac', '#78baff'];
const clamp = (v: number) => Math.max(0, Math.min(1, v));
const smooth = (v: number) => {
  const x = clamp(v);
  return x * x * (3 - 2 * x);
};

// Bounded illustrative paths in a fixed center-of-configuration frame.
function quarkPositions(t: number) {
  const raw = [0, 1, 2].map((i) => {
    const phase = (i * Math.PI * 2) / 3;
    return [
      30 * Math.cos(t * 2.1 + phase) + 9 * Math.sin(t * 3.7 + phase),
      25 * Math.sin(t * 2.5 + phase) + 7 * Math.cos(t * 4.1 + phase),
    ];
  });
  const cx = raw.reduce((sum, p) => sum + p[0], 0) / 3;
  const cy = raw.reduce((sum, p) => sum + p[1], 0) / 3;
  return raw.map(([x, y]) => [340 + x - cx, 196 + y - cy]);
}

export function MassVisual({ motion }: { motion: boolean }) {
  const [playing, setPlaying] = useState(true);
  const [view, setView] = useState<'cycle' | 'internal' | 'stable'>('cycle');
  const { ref, time } = useSceneClock(motion && playing);
  const cycle = time % 14;
  const stable =
    view === 'stable' || !motion
      ? 1
      : view === 'internal'
        ? 0
        : smooth((cycle - 4) / 2) * smooth((14 - cycle) / 2);
  // Clear once, then retain the stable envelope instead of repeatedly dissolving it.
  const cleared = motion ? smooth(time / 2) : 1;
  const rx = 148 * cleared;
  const ry = 104 * cleared;
  const quarks = quarkPositions(time);
  return (
    <div className="mass-visual" ref={ref}>
      <svg
        viewBox="0 0 680 390"
        role="img"
        aria-label="BHSM displaced-energy illustration: quarks move inside a fixed nucleus frame, then the view resolves into a stationary proton. Virtual-particle marks appear and disappear outside the cleared region and electron cloud. Conceptual, not a calculated mass."
      >
        <defs>
          <radialGradient id="mass-cloud">
            <stop stopColor="#83dcff" stopOpacity=".06" />
            <stop offset=".62" stopColor="#8cbaff" stopOpacity=".24" />
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
          BHSM · MASS AS DISPLACED ENERGY
        </text>
        <ellipse
          cx="340"
          cy="196"
          rx={rx}
          ry={ry}
          fill="url(#mass-boundary)"
          stroke="#fbc884"
          strokeOpacity=".65"
        />
        {sea.map((p, i) => {
          const x = p.x + 5 * Math.sin(time * 0.8 + p.phase);
          const y = p.y + 4 * Math.cos(time * 0.7 + p.phase);
          const distance = Math.hypot(
            (x - 340) / Math.max(1, rx),
            (y - 196) / Math.max(1, ry),
          );
          if (distance < 1.04) return null;
          const lifetime = 2.4 + (i % 7) * 0.29;
          const age = (time + p.phase) % lifetime;
          // Separate short births/deaths, with fully absent intervals between.
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
        <g transform={`rotate(${12 * Math.sin(time * 0.3)} 340 196)`}>
          <ellipse cx="278" cy="196" rx="72" ry="66" fill="url(#mass-cloud)" />
          <ellipse cx="402" cy="196" rx="72" ry="66" fill="url(#mass-cloud)" />
          {[0, 1, 2].map((i) => (
            <ellipse
              key={i}
              cx="340"
              cy="196"
              rx={119 + i * 6}
              ry={48 + i * 10}
              fill="none"
              stroke="#95cfff"
              strokeWidth="1"
              opacity={0.16 - i * 0.03}
              transform={`rotate(${i * 55 + time * 8} 340 196)`}
            />
          ))}
        </g>
        <circle
          cx="340"
          cy="196"
          r="57"
          fill="#101421"
          fillOpacity=".3"
          stroke="#c7b8f3"
          strokeOpacity=".55"
          strokeDasharray="3 5"
        />
        <g className="mass-internal-motion" opacity={1 - stable}>
          {colors.map((color, i) => (
            <path
              key={color}
              d={Array.from({ length: 22 }, (_, n) => {
                const [x, y] = quarkPositions(time - (21 - n) * 0.025)[i];
                return `${n ? 'L' : 'M'}${x},${y}`;
              }).join(' ')}
              fill="none"
              stroke={color}
              strokeWidth="5"
              opacity=".17"
            />
          ))}
          {quarks.map(([x, y], i) => {
            const [xx, yy] = quarks[(i + 1) % 3];
            const dx = xx - x,
              dy = yy - y,
              length = Math.hypot(dx, dy);
            const d = Array.from({ length: 45 }, (_, n) => {
              const u = n / 44,
                wiggle =
                  5 *
                  Math.sin(u * Math.PI * 12 - time * 4) *
                  Math.sin(u * Math.PI);
              return `${n ? 'L' : 'M'}${x + u * dx - (wiggle * dy) / length},${y + u * dy + (wiggle * dx) / length}`;
            }).join(' ');
            return (
              <path
                key={i}
                d={d}
                fill="none"
                stroke={colors[i]}
                strokeWidth="2.5"
              />
            );
          })}
          {quarks.map(([x, y], i) => (
            <g key={i} transform={`translate(${x} ${y})`}>
              <circle r="16" fill={colors[i]} fillOpacity=".15" />
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
          ))}
        </g>
        <g className="mass-stable-nucleus" opacity={stable}>
          <circle
            cx="340"
            cy="196"
            r="53"
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
            y="214"
            textAnchor="middle"
            fill="#101323"
            fontSize="14"
          >
            uud
          </text>
        </g>
        <text x="24" y="362" fill="#dfc896" fontSize="14">
          Virtual-particle sea · visual metaphor
        </text>
        <text x="655" y="362" textAnchor="end" fill="#95cfff" fontSize="14">
          Electron cloud · enlarged
        </text>
        <text x="340" y="320" textAnchor="middle" fill="#ffcf99" fontSize="15">
          {stable > 0.5
            ? 'Stable nucleus · the same bound system'
            : 'Internal motion · the nucleus stays centered'}
        </text>
      </svg>
      <div className="mass-visual-key">
        <span>● Quarks + color threads</span>
        <span>◌ Electron probability cloud</span>
        <span>○ Fixed nucleus frame + displaced region</span>
      </div>
      <div className="console-selector" aria-label="Mass viewing frame">
        <button
          aria-pressed={view === 'cycle'}
          onClick={() => setView('cycle')}
        >
          Cycle both views
        </button>
        <button
          aria-pressed={view === 'internal'}
          onClick={() => setView('internal')}
        >
          Inside the nucleus
        </button>
        <button
          aria-pressed={view === 'stable'}
          onClick={() => setView('stable')}
        >
          Stable nucleus
        </button>
      </div>
      <button className="evidence-play" onClick={() => setPlaying(!playing)}>
        {playing ? 'Pause mass animation' : 'Play mass animation'}
      </button>
    </div>
  );
}
