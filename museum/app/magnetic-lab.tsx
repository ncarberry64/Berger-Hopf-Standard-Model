'use client';
/* oxlint-disable jsx-a11y/prefer-tag-over-role -- Inline SVG needs image semantics; an HTML img cannot contain this interactive drawing. */
import { useState } from 'react';
import references from './reference-data.json';
import { larmorHz } from '../lib/science-media';
import { useSceneClock } from './science-console';

export function MagneticLab({ motion }: { motion: boolean }) {
  const [paused, setPaused] = useState(false);
  const { ref, time } = useSceneClock(motion && !paused);
  return (
    <div ref={ref} className="magnetic-lab">
      <div className="media-toolbar">
        <span className="data-label">
          CODATA 2022 measured references · animated magnetic moments
        </span>
        <button disabled={!motion} onClick={() => setPaused(!paused)}>
          {paused || !motion ? '▶ Animate moments' : 'Ⅱ Freeze moments'}
        </button>
      </div>
      <div className="magnetic-particles">
        {references.magnetic.map((row) => {
          const frequency = larmorHz(row.moment, 0.1);
          // Fixed field for a common physical comparison; logarithmic time scaling makes all four visible.
          const phase =
            -Math.sign(row.moment) * time * Math.log10(1 + frequency) * 0.5;
          const sx = 150 + 57 * Math.cos(phase),
            sy = 108 + 20 * Math.sin(phase);
          const sign = Math.sign(row.moment);
          const mx = 150 + sign * (sx - 150),
            my = 200 + sign * (sy - 200);
          return (
            <article className="magnetic-particle" key={row.id}>
              <header>
                <span>{row.symbol}</span>
                <h4>{row.name}</h4>
              </header>
              <svg
                viewBox="0 0 300 370"
                role="img"
                aria-label={`${row.name}: signed magnetic moment ${row.moment} joules per tesla, ${sign < 0 ? 'opposite to' : 'along'} the spin`}
              >
                <defs>
                  <radialGradient id={`moment-${row.id}`}>
                    <stop stopColor={row.color} stopOpacity=".6" />
                    <stop offset="1" stopColor={row.color} stopOpacity="0" />
                  </radialGradient>
                </defs>
                <circle
                  cx="150"
                  cy="200"
                  r="100"
                  fill={`url(#moment-${row.id})`}
                />
                <line
                  x1="150"
                  x2="150"
                  y1="45"
                  y2="330"
                  stroke="#6a5879"
                  strokeDasharray="3 5"
                />
                <text x="165" y="52" fill="#a999b6" fontSize="12">
                  B = 0.1 T
                </text>
                <ellipse
                  cx="150"
                  cy="108"
                  rx="57"
                  ry="20"
                  fill="none"
                  stroke="#9a8ca6"
                  strokeDasharray="3 6"
                  opacity=".4"
                />
                {sign < 0 && (
                  <ellipse
                    cx="150"
                    cy="292"
                    rx="57"
                    ry="20"
                    fill="none"
                    stroke={row.color}
                    strokeDasharray="3 6"
                    opacity=".4"
                  />
                )}
                <line
                  x1="150"
                  y1="200"
                  x2={sx.toFixed(2)}
                  y2={sy.toFixed(2)}
                  stroke="#ded5e8"
                  strokeWidth="2"
                  strokeDasharray="5 4"
                />
                <line
                  x1="150"
                  y1="200"
                  x2={mx.toFixed(2)}
                  y2={my.toFixed(2)}
                  stroke={row.color}
                  strokeWidth="5"
                />
                <circle
                  cx={mx.toFixed(2)}
                  cy={my.toFixed(2)}
                  r="6"
                  fill={row.color}
                />
                <text
                  x={(sx + 10).toFixed(2)}
                  y={(sy - 10).toFixed(2)}
                  fill="#ded5e8"
                  fontSize="13"
                >
                  S
                </text>
                <text
                  x={(mx - 18).toFixed(2)}
                  y={(my + (sign < 0 ? 24 : -24)).toFixed(2)}
                  fill={row.color}
                  fontSize="21"
                >
                  μ
                </text>
                <circle cx="150" cy="200" r="7" fill="#fff" />
                <text
                  x="150"
                  y="353"
                  textAnchor="middle"
                  fill={row.color}
                  fontSize="12"
                >
                  {sign < 0 ? 'Moment opposite to spin' : 'Moment along spin'}
                </text>
              </svg>
              <div className="moment-value">
                <small>Magnetic moment · J/T</small>
                <strong style={{ color: row.color }}>
                  {row.moment.toExponential()}
                </strong>
                <small>±{row.uncertainty.toExponential(2)} J/T</small>
              </div>
              <div className="moment-frequency">
                <span>Precession at 0.1 T</span>
                <strong>{frequency.toExponential(5)} Hz</strong>
              </div>
            </article>
          );
        })}
      </div>
      <p className="console-caption">
        <b>Measured magnetic moments · explanatory animation</b> · Colored
        vector: magnetic moment μ. Dashed vector: spin S. A common 0.1 T field
        illustrates precession; motion is slowed separately for visibility and
        vector lengths are normalized.
      </p>
      <details className="console-details">
        <summary>Explore the science · four magnetic fingerprints</summary>
        <p>
          Magnetic moment measures how strongly a particle responds to a
          magnetic field. Its sign tells us whether it points along or opposite
          to the spin. The neutral neutron still has a magnetic moment because
          its internal constituents carry charge.
        </p>
        <p>
          For these spin-½ particles, the displayed physical frequency is f =
          2|μ|B/h. The animation uses logarithmic time compression; visual
          wobble ratios and arrow lengths are not physical frequency or moment
          ratios. Quantum spin is represented by a vector illustration, not a
          rotating material surface.
        </p>
        {references.magnetic.map((r) => (
          <p key={r.id}>
            <strong>{r.name}.</strong> {r.note}
          </p>
        ))}
        <a href={references.nist_source}>
          CODATA 2022 values and uncertainties ↗
        </a>
      </details>
    </div>
  );
}
