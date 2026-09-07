'use client';
import { useEffect, useState } from 'react';
import references from './reference-data.json';
import { larmorHz } from '../lib/science-media';

export function MagneticLab({ motion }: { motion: boolean }) {
  const rows = references.magnetic;
  const [selected, setSelected] = useState(0),
    [magnet, setMagnet] = useState({ x: 135, y: 165, active: true }),
    [field, setField] = useState(0.1),
    [time, setTime] = useState(0),
    [paused, setPaused] = useState(false);
  useEffect(() => {
    if (!motion || paused) return;
    const t = setInterval(() => setTime((v) => v + 0.04), 40);
    return () => clearInterval(t);
  }, [motion, paused]);
  const fieldAt = (i: number) =>
    magnet.active
      ? field /
        (1 +
          (Math.hypot(magnet.x - (135 + i * 210), magnet.y - 270) / 120) ** 2)
      : 0;
  const row = rows[selected],
    b = fieldAt(selected),
    frequency = larmorHz(row.moment, b);
  return (
    <div className="magnetic-lab">
      <p className="data-label">
        CODATA REFERENCE VALUES · simulated spin precession
      </p>
      <p>
        Move your magnet over a particle. Its spin direction precesses around
        the field, like the axis of a wobbling top. Select a particle to compare
        its response below.
      </p>
      <div
        className="magnet-stage"
        onPointerMove={(e) => {
          const box = e.currentTarget
            .querySelector('svg')!
            .getBoundingClientRect();
          const x = ((e.clientX - box.left) * 900) / box.width,
            y = ((e.clientY - box.top) * 440) / box.height;
          setMagnet({ x, y, active: true });
          setSelected(Math.max(0, Math.min(3, Math.round((x - 135) / 210))));
        }}
        onPointerLeave={() => setMagnet((m) => ({ ...m, active: false }))}
      >
        <svg
          viewBox="0 0 900 440"
          role="img"
          aria-label="Four spin-precession diagrams respond to the cursor magnet; use the particle buttons and field slider for keyboard control"
        >
          <defs>
            <radialGradient id="magnet-space">
              <stop stopColor="#153244" />
              <stop offset="1" stopColor="#030c18" />
            </radialGradient>
            <marker
              id="spin-arrow"
              markerWidth="6"
              markerHeight="6"
              refX="3"
              refY="3"
              orient="auto"
            >
              <path d="M0 0L6 3L0 6Z" fill="#fff" />
            </marker>
          </defs>
          <rect width="900" height="440" fill="url(#magnet-space)" />
          {rows.map((p, i) => {
            const x = 135 + i * 210,
              localB = fieldAt(i);
            const f = larmorHz(p.moment, localB);
            const a = time * Math.sign(p.moment) * Math.log10(1 + f) * 0.65;
            const dx = 38 * Math.cos(a),
              dy = 15 * Math.sin(a);
            return (
              <g key={p.id}>
                <circle
                  cx={x}
                  cy="270"
                  r="73"
                  fill={p.color}
                  opacity={i === selected ? 0.08 : 0.025}
                />
                <ellipse
                  cx={x}
                  cy="191"
                  rx="38"
                  ry="15"
                  fill="none"
                  stroke={p.color}
                  opacity=".55"
                  strokeDasharray="3 5"
                />
                <path
                  d={`M${x} 285 L${x - 38} 191 M${x} 285 L${x + 38} 191`}
                  stroke={p.color}
                  opacity=".15"
                />
                <line
                  x1={x}
                  y1="307"
                  x2={x}
                  y2="145"
                  stroke="#567487"
                  strokeDasharray="5 7"
                />
                <line
                  x1={x}
                  y1="285"
                  x2={(x + dx).toFixed(2)}
                  y2={(191 + dy).toFixed(2)}
                  stroke={p.color}
                  strokeWidth="4"
                  markerEnd="url(#spin-arrow)"
                />
                <circle cx={x} cy="285" r="17" fill={p.color} />
                <text
                  x={x}
                  y="292"
                  textAnchor="middle"
                  fill="#06101a"
                  fontSize="20"
                >
                  {p.symbol}
                </text>
                <text
                  x={x}
                  y="365"
                  textAnchor="middle"
                  fill="#e5f0f5"
                  fontSize="21"
                >
                  {p.name}
                </text>
                <text
                  x={x}
                  y="392"
                  textAnchor="middle"
                  fill="#9fb6c8"
                  fontSize="15"
                >
                  {(f / 1e6).toFixed(3)} MHz
                </text>
              </g>
            );
          })}
          {magnet.active && (
            <g
              transform={`translate(${magnet.x.toFixed(2)} ${magnet.y.toFixed(2)})`}
              pointerEvents="none"
            >
              <circle
                r="58"
                fill="none"
                stroke="#82bcc7"
                strokeDasharray="3 6"
                opacity=".4"
              />
              <rect
                x="-30"
                y="-14"
                width="30"
                height="28"
                rx="3"
                fill="#f58ba9"
              />
              <rect y="-14" width="30" height="28" rx="3" fill="#67e8ef" />
              <text
                x="-15"
                y="6"
                textAnchor="middle"
                fill="#06101a"
                fontSize="17"
              >
                N
              </text>
              <text
                x="15"
                y="6"
                textAnchor="middle"
                fill="#06101a"
                fontSize="17"
              >
                S
              </text>
            </g>
          )}
        </svg>
      </div>
      <div className="media-toolbar">
        {rows.map((r, i) => (
          <button
            key={r.id}
            aria-pressed={selected === i}
            onClick={() => {
              setSelected(i);
              setMagnet({ x: 135 + i * 210, y: 165, active: true });
            }}
          >
            {r.name}
          </button>
        ))}
        <button disabled={!motion} onClick={() => setPaused((p) => !p)}>
          {paused || !motion ? 'Play precession' : 'Pause precession'}
        </button>
      </div>
      <label className="media-slider">
        Magnet strength · {field.toFixed(2)} T
        <input
          aria-label="Magnet strength in tesla"
          type="range"
          min="0"
          max="1"
          step=".01"
          value={field}
          onChange={(e) => {
            setField(+e.target.value);
            setMagnet({ x: 135 + selected * 210, y: 165, active: true });
          }}
        />
      </label>
      <div className="event-story">
        <h4>{row.name}: magnetic response</h4>
        <p>{row.note}</p>
        <div className="science-readout">
          <div>
            <small>CODATA 2022 magnetic moment</small>
            <strong>{row.moment.toExponential(9)} J/T</strong>
            <small>
              Standard uncertainty ±{row.uncertainty.toExponential(1)} J/T
            </small>
          </div>
          <div>
            <small>Local model field</small>
            <strong>{b.toFixed(4)} T</strong>
            <small>Illustrative distance profile</small>
          </div>
          <div>
            <small>Calculated Larmor frequency</small>
            <strong>{(frequency / 1e6).toFixed(6)} MHz</strong>
            <small>f = 2|μ|B/h for spin ½</small>
          </div>
          <div>
            <small>BHSM comparison</small>
            <strong>Derivation open</strong>
            <small>No reviewed magnetic value yet</small>
          </div>
        </div>
        <p className="media-note">
          The numerical frequency follows the reference moment and selected
          field. Visual speed is logarithmically compressed; the cone is a
          spin-direction schematic, not a particle’s physical shape. Field
          geometry and initial tilt are illustrative.{' '}
          <a href={references.nist_source}>NIST / CODATA 2022 values ↗</a>
        </p>
      </div>
    </div>
  );
}
