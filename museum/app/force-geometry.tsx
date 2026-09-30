'use client';

/* oxlint-disable jsx-a11y/prefer-tag-over-role -- Inline scientific SVG diagrams. */
import { useState } from 'react';
import { useSceneClock } from './science-console';
import { hypersphereCurves } from '../lib/children-geometry';

const studies = [
  {
    name: 'Strong force',
    motif: 'Binding & cohesion',
    color: '#72d9ff',
    text: 'A proton’s three valence quarks exchange gluons.',
    meaning:
      'BHSM pictures strong interaction as cohesion in the underlying Aether geometry. The reference diagram shows quark–gluon interaction; its exchange markers are schematic, not calculated QCD trajectories.',
    boundary:
      'Established strong interactions are described by QCD. This display does not calculate confinement or a binding energy.',
  },
  {
    name: 'Electromagnetic',
    motif: 'Limited surface availability',
    color: '#f2c774',
    text: 'The classical field of a point charge decreases as 1/r².',
    meaning:
      'In this BHSM interpretation, only a limited electromagnetic component is freely available on the surface, corresponding to the fine-structure constant (FSC, α). The animation instead samples the established Coulomb inverse-square law; it does not assign a numerical surface fraction.',
    boundary:
      'The fine-structure constant measures electromagnetic coupling. The proposed surface interpretation is qualitative here; the curve is normalized at r₀, in the classical static point-charge regime; it does not calculate α.',
  },
  {
    name: 'Weak force',
    motif: 'Decay & transformation',
    color: '#fc9171',
    text: 'An unstable configuration transforms into decay products.',
    meaning:
      'The weak-force study illustrates decay: an unstable configuration transforms and releases daughter products. The reference channel shown is neutron beta decay into a proton, electron and electron antineutrino. Highlighting identifies products; it does not assign trajectories or a lifetime.',
    boundary:
      'Weak interactions mediate particle transformations. This geometric analogy does not compute a decay channel, lifetime or interaction range.',
  },
  {
    name: 'Gravity',
    motif: 'Large-scale geometry',
    color: '#b99bff',
    text: 'In the Newtonian limit, a point mass produces an inverse-square field.',
    meaning:
      'BHSM proposes a geometric account of gravity. The displayed reference curve samples the established Newtonian inverse-square law, normalized at r₀; it applies in the weak-field, nonrelativistic limit.',
    boundary:
      'Gravity is distinct from electromagnetism. No electromagnetic frequency, metric solution or gravitational-wave prediction is assigned here.',
  },
  {
    name: 'One geometric origin',
    motif: 'The hypersphere',
    color: '#67e8ef',
    text: 'Rotate a mathematical projection of S³ from four-dimensional space.',
    meaning:
      'BHSM proposes a common hyperspherical origin. This view rotates an exact S³ parameterization in four dimensions and projects it for display; it does not invent surface collisions or daughter particles.',
    boundary:
      'A common picture is not a completed unification. Physical mode identification, normalized couplings and quantitative predictions remain open.',
  },
];

// Established reference mechanisms and an exact mathematical projection.
// Time advances explanatory markers; it is never a calibrated particle trajectory.
function ForceField({ kind, phase }: { kind: number; phase: number }) {
  const step = Math.floor(phase * 3) % 3;
  const radius = 1 + 2 * phase;
  const quarks = [
    [150, 65],
    [65, 205],
    [235, 205],
  ];
  const colors = ['#fc9171', '#71e5eb', '#bda7f5'];
  return (
    <svg
      viewBox="0 0 300 280"
      role="img"
      aria-label={`${studies[kind].name}: ${studies[kind].text}`}
    >
      <rect width="300" height="280" fill="#050c14" />
      {kind === 0 && (
        <g>
          {quarks.map(([x, y], i) => {
            const [tx, ty] = quarks[(i + 1) % 3];
            const u = (phase * 3) % 1;
            return (
              <g key={i}>
                <path
                  d={`M${x} ${y} L${tx} ${ty}`}
                  stroke={colors[i]}
                  strokeWidth="2"
                  fill="none"
                />
                <circle
                  cx={x + (tx - x) * u}
                  cy={y + (ty - y) * u}
                  r="8"
                  fill="#0a101c"
                  stroke={colors[i]}
                />
                <text
                  x={x + (tx - x) * u}
                  y={y + (ty - y) * u + 4}
                  fill={colors[i]}
                  fontSize="12"
                  textAnchor="middle"
                >
                  g
                </text>
                <circle
                  cx={x}
                  cy={y}
                  r="20"
                  stroke={colors[(i + step) % 3]}
                  strokeWidth="3"
                  fill="#101522"
                />
                <text x={x} y={y + 5} fill="#fff" textAnchor="middle">
                  {i < 2 ? 'u' : 'd'}
                </text>
              </g>
            );
          })}
          <text
            x="150"
            y="258"
            textAnchor="middle"
            fill="#cfc6db"
            fontSize="12"
          >
            Proton · quarks exchange gluons
          </text>
        </g>
      )}
      {(kind === 1 || kind === 3) && (
        <g>
          <path d="M40 40V230H270" fill="none" stroke="#91859f" />
          <path
            d={Array.from({ length: 101 }, (_, i) => {
              const r = 1 + i / 50;
              return `${i ? 'L' : 'M'}${40 + (r - 1) * 110},${230 - 170 / (r * r)}`;
            }).join(' ')}
            fill="none"
            stroke={kind === 1 ? '#f2c774' : '#b99bff'}
            strokeWidth="3"
          />
          <circle
            cx={40 + (radius - 1) * 110}
            cy={230 - 170 / (radius * radius)}
            r="6"
            fill="#fff"
          />
          <text x="150" y="25" textAnchor="middle" fill="#e8d8fb" fontSize="15">
            {kind === 1 ? 'Coulomb field' : 'Newtonian gravity'}
          </text>
          <text
            x="150"
            y="255"
            textAnchor="middle"
            fill="#cfc6db"
            fontSize="12"
          >
            r/r₀ = {radius.toFixed(2)} · field ∝ 1/r²
          </text>
          <text
            x="150"
            y="275"
            textAnchor="middle"
            fill="#a99abc"
            fontSize="11"
          >
            Sampling a law, not a moving particle
          </text>
        </g>
      )}
      {kind === 2 && (
        <g>
          <circle
            cx="68"
            cy="128"
            r="30"
            fill="#152031"
            stroke="#71e5eb"
            strokeWidth="2"
          />
          <text x="68" y="135" fill="#fff" textAnchor="middle" fontSize="25">
            n
          </text>
          <path
            d="M104 128H163M156 120L166 128L156 136"
            stroke="#fc9171"
            strokeWidth="2"
            fill="none"
          />
          {['p', 'e⁻', 'ν̄e'].map((label, i) => (
            <g key={label}>
              <circle
                cx="223"
                cy={63 + i * 66}
                r="24"
                fill="#15101b"
                stroke={step === i ? '#ffbc77' : '#665374'}
                strokeWidth={step === i ? 3 : 1}
              />
              <text
                x="223"
                y={70 + i * 66}
                textAnchor="middle"
                fill="#fff"
                fontSize="19"
              >
                {label}
              </text>
            </g>
          ))}
          <text
            x="150"
            y="259"
            textAnchor="middle"
            fill="#cfc6db"
            fontSize="12"
          >
            Neutron β decay · n → p + e⁻ + ν̄e
          </text>
        </g>
      )}
      {kind === 4 && (
        <g>
          <g transform="translate(0 45) scale(1.36)" fill="none">
            {hypersphereCurves(phase * 12).map((d, i) => (
              <path key={i} d={d} stroke={colors[i % 3]} strokeWidth=".8" />
            ))}
          </g>
          <text
            x="150"
            y="249"
            textAnchor="middle"
            fill="#cfc6db"
            fontSize="14"
          >
            S³ ⊂ R⁴ · projected hypersphere
          </text>
          <text
            x="150"
            y="270"
            textAnchor="middle"
            fill="#a99abc"
            fontSize="11"
          >
            Mathematical rotation, not cosmic evolution
          </text>
        </g>
      )}
    </svg>
  );
}

export function ForceGeometry({
  motion,
  setMotion,
}: {
  motion: boolean;
  setMotion: (value: boolean) => void;
}) {
  const [playing, setPlaying] = useState(true);
  const [offset, setOffset] = useState(0);
  const [chosen, setChosen] = useState(0);
  const { ref, time } = useSceneClock(motion && playing);
  const phase = (((time / 12 + offset) % 1) + 1) % 1;
  const study = studies[chosen];
  return (
    <div ref={ref} className="force-atlas">
      <div className="force-atlas-heading">
        <span className="data-label">
          Reference science & geometry · BHSM interpretation below
        </span>
        <span className="force-atlas-key">
          Laws, decay products and mathematical geometry
        </span>
      </div>
      <div className="force-studies" aria-label="Five geometric studies">
        {studies.map((item, i) => (
          <button
            key={item.name}
            type="button"
            className="force-study"
            aria-pressed={chosen === i}
            aria-controls="force-study-reading"
            onClick={() => setChosen(i)}
            style={{ '--study-color': item.color } as React.CSSProperties}
          >
            <span className="force-study-number">0{i + 1}</span>
            <h4>{item.name}</h4>
            <span className="force-study-motif">{item.motif}</span>
            <ForceField kind={i} phase={phase} />
            <span className="force-study-caption">{item.text}</span>
            <span className="force-study-explore">
              {chosen === i ? 'Selected study' : 'Explore study'}{' '}
              <span aria-hidden="true">↗</span>
            </span>
          </button>
        ))}
      </div>
      <div className="force-atlas-controls">
        <button
          type="button"
          onClick={() => {
            if (!motion) {
              setMotion(true);
              setPlaying(true);
            } else setPlaying(!playing);
          }}
        >
          {!motion
            ? 'Enable animation'
            : playing
              ? 'Pause animation'
              : 'Play animation'}
        </button>
        <button type="button" onClick={() => setOffset(-time / 12)}>
          Restart
        </button>
        <label>
          Animation phase
          <input
            type="range"
            min="0"
            max="100"
            step="0.1"
            value={phase * 100}
            aria-valuetext={`${Math.round(phase * 100)} percent of illustrative cycle`}
            onChange={(e) => {
              setPlaying(false);
              setOffset(Number(e.target.value) / 100 - time / 12);
            }}
          />
        </label>
        <span>12-second explanatory replay</span>
      </div>
      <div
        className="force-study-reading"
        id="force-study-reading"
        aria-live="polite"
        style={{ '--study-color': study.color } as React.CSSProperties}
      >
        <div>
          <p className="eyebrow">
            Study 0{chosen + 1} · {study.motif}
          </p>
          <h4>{study.name}</h4>
          <p>{study.meaning}</p>
        </div>
        <div>
          <p className="eyebrow">What this shows</p>
          <p>{study.boundary}</p>
        </div>
      </div>
      <p className="console-caption">
        Scientific basis:{' '}
        <a href="https://www.energy.gov/science/doe-explainsquarks-and-gluons">
          QCD quarks and gluons
        </a>{' '}
        ·{' '}
        <a href="https://openstax.org/books/university-physics-volume-2/pages/5-3-coulombs-law">
          Coulomb’s law
        </a>{' '}
        ·{' '}
        <a href="https://openstax.org/books/university-physics-volume-3/pages/10-4-nuclear-reactions">
          Beta decay
        </a>{' '}
        ·{' '}
        <a href="https://openstax.org/books/university-physics-volume-1/pages/13-1-newtons-law-of-universal-gravitation">
          Newtonian limit
        </a>
        . The common-origin interpretation is BHSM’s proposal; the reference
        laws do not establish it.
      </p>
      <p className="force-atlas-closing">
        One proposed geometric origin. Four interaction stories.
      </p>
    </div>
  );
}
