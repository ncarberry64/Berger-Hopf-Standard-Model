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

export function MassVisual({ motion }: { motion: boolean }) {
  const [playing, setPlaying] = useState(true);
  const { ref, time } = useSceneClock(motion && playing);
  const cycle = motion ? time % 12 : 6;
  const cleared = Math.min(1, cycle / 3);
  const rx = 148 * cleared;
  const ry = 104 * cleared;
  const quarks = [0, 1, 2].map((i) => {
    const a = time * 0.5 + (i * Math.PI * 2) / 3;
    return [340 + 42 * Math.cos(a), 196 + 29 * Math.sin(a)];
  });
  return (
    <div className="mass-visual" ref={ref}>
      <svg
        viewBox="0 0 680 390"
        role="img"
        aria-label="BHSM displaced-energy illustration: three uud quarks joined by color threads, an electron cloud, and a surrounding virtual-particle sea held outside a cleared region. Conceptual, not a calculated mass."
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
          return (
            <circle
              key={i}
              cx={x}
              cy={y}
              r={i % 3 === 0 ? 1.9 : 1.1}
              fill="#dfc896"
              opacity={0.3 + 0.35 * Math.sin(time + p.phase) ** 2}
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
        <text x="24" y="362" fill="#dfc896" fontSize="14">
          Virtual-particle sea · visual metaphor
        </text>
        <text x="655" y="362" textAnchor="end" fill="#95cfff" fontSize="14">
          Electron cloud · enlarged
        </text>
        <text x="340" y="320" textAnchor="middle" fill="#ffcf99" fontSize="15">
          {cycle < 3
            ? 'A localized configuration clears a region'
            : 'The surrounding response is held back'}
        </text>
      </svg>
      <div className="mass-visual-key">
        <span>● Quarks + color threads</span>
        <span>◌ Electron probability cloud</span>
        <span>○ Displaced region</span>
      </div>
      <button className="evidence-play" onClick={() => setPlaying(!playing)}>
        {playing ? 'Pause mass animation' : 'Play mass animation'}
      </button>
    </div>
  );
}
