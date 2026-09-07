'use client';
/* oxlint-disable jsx-a11y/prefer-tag-over-role -- Inline SVG needs image semantics; an HTML img cannot contain this interactive drawing. */
import { useState } from 'react';
import { useSceneClock } from './science-console';
import references from './reference-data.json';

const nodes = [
  { x: 95, y: 360 },
  { x: 275, y: 290 },
  { x: 450, y: 205 },
  { x: 615, y: 150 },
  { x: 805, y: 150 },
];
const names = ['Gravity', 'Electromagnetic', 'Weak', 'Strong', 'Aether'];
function position(segment: number, t: number) {
  const a = nodes[segment],
    b = nodes[segment + 1];
  return [
    (1 - t) ** 3 * a.x +
      3 * (1 - t) ** 2 * t * (a.x + 85) +
      3 * (1 - t) * t * t * (b.x - 85) +
      t ** 3 * b.x,
    a.y + (b.y - a.y) * (t * t * (3 - 2 * t)),
  ];
}

export function ForceTree({ motion }: { motion: boolean }) {
  const [pausedFrame, setFrame] = useState(0),
    [playing, setPlaying] = useState(true);
  const { ref: sceneRef, time } = useSceneClock(motion && playing);
  const [start, setStart] = useState(0);
  const frame = playing ? ((time - start) * 5) % 101 : pausedFrame;
  const chosen = Math.min(4, Math.floor(frame / 20)),
    reference = references.energy_scales[Math.min(3, chosen)];
  return (
    <div className="force-tree" ref={sceneRef}>
      <p className="data-label">
        PROPOSED BHSM CONNECTIONS · sourced reference scales
      </p>
      <button
        className="event-stage"
        aria-label={
          playing && motion
            ? 'Pause force animation and inspect energy scales'
            : 'Resume force animation'
        }
        aria-pressed={!playing}
        onClick={() => {
          if (!playing) setStart(time - frame / 5);
          else setFrame(frame);
          setPlaying((p) => !p);
        }}
      >
        <svg
          viewBox="0 0 950 480"
          role="img"
          aria-label="Gravity branches from electromagnetism, electromagnetism from the weak interaction, weak joins strong, and strong connects to a luminous aether core"
        >
          <defs>
            <radialGradient id="aether-glow">
              <stop stopColor="#fff" />
              <stop offset=".18" stopColor="#fff5bf" />
              <stop offset=".4" stopColor="#f4c870" stopOpacity=".6" />
              <stop offset="1" stopColor="#cb7cff" stopOpacity="0" />
            </radialGradient>
            <filter id="force-glow">
              <feGaussianBlur stdDeviation="5" />
            </filter>
          </defs>
          <rect width="950" height="480" fill="#050509" />
          <path
            d="M70 65 C310 65 385 150 615 150"
            fill="none"
            stroke="#fc9171"
            strokeWidth="3"
            opacity=".65"
          />
          <path
            d="M90 185 C245 185 300 205 450 205"
            fill="none"
            stroke="#67e8ef"
            strokeWidth="3"
            opacity=".65"
          />
          <path
            d="M55 280 C140 280 180 290 275 290"
            fill="none"
            stroke="#f2c774"
            strokeWidth="3"
            opacity=".65"
          />
          {nodes.slice(0, 4).map((n, i) => {
            const b = nodes[i + 1],
              color = references.energy_scales[i].color;
            const d = `M${n.x} ${n.y} C${n.x + 85} ${n.y} ${b.x - 85} ${b.y} ${b.x} ${b.y}`;
            return (
              <g key={i}>
                {Array.from({ length: 11 }, (_, j) => {
                  const offset = (j - 5) * 3.2;
                  const points = Array.from({ length: 41 }, (_, k) => {
                    const t = k / 40,
                      [x, y] = position(i, t);
                    const wave =
                      Math.sin(t * Math.PI) *
                      (offset + 8 * Math.sin(t * 8 - frame * 0.14 + j * 0.35));
                    return `${k ? 'L' : 'M'}${x.toFixed(2)},${(y + wave).toFixed(2)}`;
                  });
                  return (
                    <path
                      key={`ribbon-${j}`}
                      d={points.join(' ')}
                      fill="none"
                      stroke={color}
                      strokeWidth=".8"
                      opacity=".26"
                    />
                  );
                })}
                <circle
                  cx={n.x}
                  cy={n.y}
                  r={chosen === i ? 28 : 20}
                  fill="none"
                  stroke={color}
                  strokeWidth="1"
                  opacity=".4"
                />
                <path
                  d={d}
                  fill="none"
                  stroke={color}
                  strokeWidth="16"
                  opacity=".18"
                  filter="url(#force-glow)"
                />
                <path d={d} fill="none" stroke={color} strokeWidth="3" />
                {Array.from({ length: 6 }, (_, j) => {
                  const t = (frame / 25 + j / 6) % 1,
                    p = position(i, t);
                  return (
                    <circle
                      key={j}
                      cx={p[0].toFixed(2)}
                      cy={p[1].toFixed(2)}
                      r="3.5"
                      fill={color}
                      opacity={0.3 + 0.7 * t}
                    />
                  );
                })}
                <circle
                  cx={n.x}
                  cy={n.y}
                  r={chosen === i ? 11 : 7}
                  fill={color}
                />
                <text
                  x={n.x}
                  y={n.y + 43}
                  textAnchor={i === 0 ? 'start' : 'middle'}
                  fill={color}
                  fontSize="20"
                >
                  {names[i]}
                </text>
              </g>
            );
          })}
          <circle
            cx="805"
            cy="150"
            r={(112 + 12 * Math.sin(frame * 0.1)).toFixed(2)}
            fill="url(#aether-glow)"
          />
          {Array.from({ length: 8 }, (_, i) => (
            <ellipse
              key={`core-${i}`}
              cx="805"
              cy="150"
              rx={34 + i * 4}
              ry={12 + i * 5}
              fill="none"
              stroke="#fff3cb"
              opacity=".2"
              transform={`rotate(${frame * 1.2 + i * 22} 805 150)`}
            />
          ))}
          <circle cx="805" cy="150" r="27" fill="#fffde8" />
          <text
            x="805"
            y="161"
            textAnchor="middle"
            fill="#6e4c35"
            fontSize="35"
          >
            ∞
          </text>
          <text
            x="805"
            y="263"
            textAnchor="middle"
            fill="#fff4c7"
            fontSize="25"
          >
            Aether · the core
          </text>
          <text
            x="805"
            y="290"
            textAnchor="middle"
            fill="#b6c5d6"
            fontSize="15"
          >
            Conceptual infinite limit
          </text>
          <text
            x="475"
            y="445"
            textAnchor="middle"
            fill="#c4d9e6"
            fontSize="17"
          >
            {playing && motion
              ? 'Follow the connections · click to pause'
              : 'Paused · inspect the reference scales below'}
          </text>
        </svg>
      </button>
      <div className="media-toolbar">
        {names.map((name, i) => (
          <button
            key={name}
            aria-pressed={chosen === i}
            onClick={() => {
              setFrame(i * 20);
              setPlaying(false);
            }}
          >
            {name}
          </button>
        ))}
        <button
          disabled={!motion}
          onClick={() => {
            if (!playing) setStart(time - frame / 5);
            else setFrame(frame);
            setPlaying((p) => !p);
          }}
        >
          {playing && motion ? 'Pause' : 'Play'}
        </button>
      </div>
      <label className="media-slider">
        Journey toward the core
        <input
          type="range"
          min="0"
          max="100"
          step=".1"
          value={frame}
          onChange={(e) => {
            setFrame(+e.target.value);
            setPlaying(false);
          }}
        />
      </label>
      <div
        className="event-story"
        aria-live={playing && motion ? 'off' : 'polite'}
      >
        <h4>
          {chosen === 4 ? 'Aether: the proposed common core' : reference.label}
        </h4>
        <div className="science-readout">
          <div>
            <small>
              {chosen === 4 ? 'Conceptual limit' : 'Reference energy scale'}
            </small>
            <strong>{chosen === 4 ? '∞' : reference.scale}</strong>
            <small>
              {chosen === 4
                ? 'No finite or infinite physical transition energy has been derived.'
                : reference.meaning}
            </small>
          </div>
          <div>
            <small>BHSM connection</small>
            <strong>
              {chosen === 4
                ? 'Shared origin proposed'
                : `${names[chosen]} → ${names[chosen + 1]}`}
            </strong>
            <small>Author-specified conceptual topology</small>
          </div>
        </div>
        {chosen < 4 && (
          <a href={reference.source}>Reference scale and conventions ↗</a>
        )}
      </div>
      <details className="console-details">
        <summary>Explore the science · physical reference scales</summary>
        <p>
          These branches express Norman’s proposed organization. The benchmarks
          use different physical definitions and are not an increasing energy
          axis or a calculated coupling-merger curve. The luminous ∞ is a
          conceptual endpoint, not evidence of divergent energy.
        </p>

        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Interaction</th>
                <th>Reference scale</th>
                <th>Meaning</th>
              </tr>
            </thead>
            <tbody>
              {references.energy_scales.map((r) => (
                <tr key={r.id}>
                  <th>{r.label}</th>
                  <td>{r.scale}</td>
                  <td>
                    {r.meaning} <a href={r.source}>Source ↗</a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>
    </div>
  );
}
