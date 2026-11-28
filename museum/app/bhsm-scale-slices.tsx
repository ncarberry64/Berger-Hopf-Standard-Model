'use client';

import { useId, useState, type CSSProperties } from 'react';

const layers = [
  {
    name: 'Hypersphere core',
    short: 'Core → fields',
    color: '#ffbc77',
    category: 'BHSM proposal',
    description:
      'The proposed common core underlies the possibility of excitations on spacetime fields. It is the foundation of this conceptual map, not a tiny object assigned a physical diameter.',
    detail:
      'BHSM does not assign ordinary distance, elapsed time or a particle trajectory inside the core. The field excitations belong to the spacetime side of the proposed correspondence.',
  },
  {
    name: 'Excitations & modes',
    short: 'Moiré organization',
    color: '#ff968a',
    category: 'BHSM interpretation',
    description:
      'Overlapping excitations make a moiré-like pattern: a visual way to introduce the proposed organization of modes.',
    detail:
      'The interference drawing is an analogy for mode structure. A pattern alone does not determine a particle identity, mass or decay probability.',
  },
  {
    name: 'Standard Model',
    short: 'Fundamental particles',
    color: '#71e5eb',
    category: 'Established particle framework · BHSM connection conditional',
    description:
      'Quarks, leptons, interaction bosons and the Higgs occupy one slice of the larger BHSM picture. Explore their conventional organization in the chart below.',
    detail:
      'BHSM conditionally reproduces the Standard Model matter and gauge ledger under stated assumptions. This scale map is not a first-principles derivation of the Standard Model.',
  },
  {
    name: 'Periodic table',
    short: 'Atoms & elements',
    color: '#bda7f5',
    category: 'Established organization of matter',
    description:
      'Quarks bind into nucleons; nuclei and electrons form atoms. Elements are organized by atomic number in the periodic table.',
    detail:
      'This slice moves from fundamental constituents to composite systems. Atomic structure and the Standard Model particle ledger describe different levels of organization.',
  },
  {
    name: 'Molecules',
    short: 'Bonds & chemistry',
    color: '#96dfb1',
    category: 'Established organization of matter',
    description:
      'Atoms join through chemical bonds. Their arrangements create molecules, with properties that depend on structure and environment.',
    detail:
      'Chemistry brings collective organization into view: the same atomic ingredients can form very different molecular structures.',
  },
  {
    name: 'Planets & stars',
    short: 'Worlds & stellar systems',
    color: '#f4ce77',
    category: 'Observed astrophysical systems',
    description:
      'Matter gathers into worlds and stars. Gravity, pressure, radiation and environment shape their histories.',
    detail:
      'These are larger-scale systems with their own physical mechanisms. Their place in the BHSM map does not replace the need to test stellar and planetary predictions.',
  },
  {
    name: 'Cosmic scale',
    short: 'Galaxies & the cosmic web',
    color: '#a7baff',
    category: 'Observed structures · BHSM cosmology proposed',
    description:
      'Galaxies, clusters and the cosmic web form the widest view in this museum: a connected universe of structure and change.',
    detail:
      'The observed cosmic structures and the proposed BHSM cosmic cycle have different evidence status. Use the cosmology exhibits to follow that distinction.',
  },
];

const quarks = [
  ['u', 'up'],
  ['c', 'charm'],
  ['t', 'top'],
  ['d', 'down'],
  ['s', 'strange'],
  ['b', 'bottom'],
];
const leptons = [
  ['e', 'electron'],
  ['μ', 'muon'],
  ['τ', 'tau'],
  ['νe', 'electron neutrino'],
  ['νμ', 'muon neutrino'],
  ['ντ', 'tau neutrino'],
];
const bosons = [
  ['γ', 'photon', 'Electromagnetic'],
  ['g', 'gluon', 'Strong'],
  ['W±', 'W bosons', 'Weak'],
  ['Z', 'Z boson', 'Weak'],
];

function SliceContents({ level, y }: { level: number; y: number }) {
  if (level === 0) {
    return (
      <g fill="none" stroke="currentColor" strokeWidth="1.1">
        {[0, 1, 2, 3, 4].map((i) => (
          <ellipse key={i} cx="240" cy={y} rx={27 + i * 17} ry={10 + i * 5} />
        ))}
        <ellipse cx="240" cy={y} rx="23" ry="31" />
        <path d={`M145 ${y} H335 M240 ${y - 31} V${y + 31}`} />
        <circle cx="240" cy={y} r="6" fill="currentColor" stroke="none" />
      </g>
    );
  }
  if (level === 1) {
    return (
      <g fill="none" stroke="currentColor" strokeWidth="1" opacity=".8">
        {Array.from({ length: 13 }, (_, i) => (
          <g key={i}>
            <ellipse cx="216" cy={y} rx={12 + i * 10} ry={4 + i * 2.7} />
            <ellipse cx="264" cy={y} rx={12 + i * 10} ry={4 + i * 2.7} />
          </g>
        ))}
      </g>
    );
  }
  if (level === 2) {
    return (
      <g
        textAnchor="middle"
        fontSize="18"
        fill="currentColor"
        fontFamily="monospace"
      >
        {['u', 'd', 'e', 'ν', 'γ', 'H'].map((symbol, i) => (
          <g key={symbol}>
            <circle
              cx={130 + i * 44}
              cy={y}
              r="17"
              fill="currentColor"
              fillOpacity=".1"
              stroke="currentColor"
              strokeWidth="1"
            />
            <text x={130 + i * 44} y={y + 6}>
              {symbol}
            </text>
          </g>
        ))}
      </g>
    );
  }
  if (level === 3) {
    return (
      <g fill="currentColor">
        {Array.from({ length: 18 * 5 }, (_, i) => {
          const col = i % 18;
          const row = Math.floor(i / 18);
          if (row === 0 && col > 0 && col < 17) return null;
          if ((row === 1 || row === 2) && col > 1 && col < 12) return null;
          return (
            <rect
              key={i}
              x={115 + col * 14}
              y={y - 25 + row * 11}
              width="10"
              height="8"
              rx="1"
              opacity={0.35 + (col % 3) * 0.2}
            />
          );
        })}
      </g>
    );
  }
  if (level === 4) {
    const atoms = [
      [145, -7],
      [195, 15],
      [245, -10],
      [290, 14],
      [334, -10],
    ];
    return (
      <g stroke="currentColor" strokeWidth="3" fill="currentColor">
        <path
          d={`M145 ${y - 7} L195 ${y + 15} L245 ${y - 10} L290 ${y + 14} L334 ${y - 10}`}
          fill="none"
          opacity=".65"
        />
        {atoms.map(([x, dy], i) => (
          <circle
            key={i}
            cx={x}
            cy={y + dy}
            r={i % 2 ? 8 : 12}
            fillOpacity=".3"
          />
        ))}
      </g>
    );
  }
  if (level === 5) {
    return (
      <g stroke="currentColor" fill="none">
        <ellipse cx="240" cy={y} rx="115" ry="27" opacity=".4" />
        <ellipse cx="240" cy={y} rx="73" ry="18" opacity=".6" />
        <circle cx="240" cy={y} r="16" fill="currentColor" stroke="none" />
        <circle cx="176" cy={y + 8} r="6" fill="#96dfb1" stroke="none" />
        <circle cx="338" cy={y - 14} r="9" fill="#a7baff" stroke="none" />
        <ellipse cx="338" cy={y - 14} rx="16" ry="4" />
      </g>
    );
  }
  return (
    <g stroke="currentColor" fill="currentColor">
      <path
        d={`M155 ${y + 3} L194 ${y - 16} L239 ${y + 10} L280 ${y - 19} L321 ${y + 4} M194 ${y - 16} L222 ${y - 28} L280 ${y - 19} M239 ${y + 10} L281 ${y + 23} L321 ${y + 4} M155 ${y + 3} L199 ${y + 25} L239 ${y + 10}`}
        fill="none"
        strokeOpacity=".7"
      />
      {[
        [155, 3],
        [194, -16],
        [239, 10],
        [280, -19],
        [321, 4],
        [222, -28],
        [281, 23],
        [199, 25],
      ].map(([x, dy], i) => (
        <circle key={i} cx={x} cy={y + dy} r={i % 3 === 0 ? 4 : 2.5} />
      ))}
    </g>
  );
}

function ScaleSculpture({ selected }: { selected: number }) {
  const uid = useId().replace(/:/g, '');
  return (
    <svg className="scale-sculpture" viewBox="0 0 480 690" aria-hidden="true">
      <defs>
        {layers.map((layer, i) => (
          <linearGradient
            key={i}
            id={`${uid}-slice-${i}`}
            x1="0"
            y1="0"
            x2="1"
            y2="1"
          >
            <stop offset="0" stopColor={layer.color} stopOpacity=".2" />
            <stop offset="1" stopColor={layer.color} stopOpacity=".025" />
          </linearGradient>
        ))}
      </defs>
      <path
        d="M240 54 V647"
        stroke="#8ea2b7"
        strokeDasharray="2 8"
        opacity=".35"
      />
      <path
        d="M32 632 V61 l-5 9 m5-9 5 9"
        fill="none"
        stroke="#8ea2b7"
        opacity=".65"
      />
      <text
        transform="translate(20 394) rotate(-90)"
        className="scale-axis-label"
      >
        INCREASING SCALE OF ORGANIZATION
      </text>
      {[...layers].reverse().map((layer, visualIndex) => {
        const level = 6 - visualIndex;
        const y = 94 + visualIndex * 85;
        const radius = [112, 158, 190, 206, 190, 158, 112][visualIndex];
        const active = selected === level;
        return (
          <g
            key={layer.name}
            style={{ color: layer.color }}
            opacity={active ? 1 : 0.76}
          >
            <path
              d={`M${240 - radius} ${y} a${radius} 39 0 0 0 ${radius * 2} 0 v13 a${radius} 39 0 0 1 ${-radius * 2} 0 Z`}
              fill="currentColor"
              fillOpacity={active ? 0.2 : 0.08}
              stroke="currentColor"
              strokeOpacity=".35"
            />
            <ellipse
              cx="240"
              cy={y}
              rx={radius}
              ry="39"
              fill={`url(#${uid}-slice-${level})`}
              stroke="currentColor"
              strokeWidth={active ? 2.5 : 1}
            />
            <SliceContents level={level} y={y} />
            <path
              d={`M${240 + radius + 6} ${y + 3} H443`}
              stroke="currentColor"
              strokeOpacity=".5"
            />
            <text
              x="450"
              y={y + 8}
              fill="currentColor"
              className="scale-slice-number"
            >
              {String(level + 1).padStart(2, '0')}
            </text>
          </g>
        );
      })}
      <text x="240" y="670" textAnchor="middle" className="scale-diagram-note">
        Conceptual slices · not to physical scale
      </text>
    </svg>
  );
}

function ParticleChart() {
  return (
    <div
      className="scale-particle-chart"
      id="standard-model-chart"
      aria-labelledby="scale-particle-title"
    >
      <div className="scale-chart-heading">
        <div>
          <p className="eyebrow">A closer look at slice 03</p>
          <h3 id="scale-particle-title">
            The Standard Model of fundamental particles
          </h3>
        </div>
        <span className="scale-evidence-tag">Conventional reference</span>
      </div>
      <div className="scale-particle-families">
        <div className="scale-matter-particles">
          <div className="scale-generations">
            <span>Generation I</span>
            <span>Generation II</span>
            <span>Generation III</span>
          </div>
          {[
            { name: 'Quarks', className: 'quarks', particles: quarks },
            { name: 'Leptons', className: 'leptons', particles: leptons },
          ].map((family) => (
            <div
              className={`scale-particle-family ${family.className}`}
              key={family.name}
            >
              <h4>
                {family.name} <small>Matter particles · spin ½</small>
              </h4>
              <ul>
                {family.particles.map(([symbol, name]) => (
                  <li key={name}>
                    <b aria-hidden="true">{symbol}</b>
                    <span>{name}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
        <div className="scale-interaction-particles">
          <div className="scale-particle-family bosons">
            <h4>
              Gauge bosons <small>Interaction carriers · spin 1</small>
            </h4>
            <ul>
              {bosons.map(([symbol, name, force]) => (
                <li key={name}>
                  <b aria-hidden="true">{symbol}</b>
                  <span>{name}</span>
                  <small>{force}</small>
                </li>
              ))}
            </ul>
          </div>
          <div className="scale-higgs">
            <b aria-hidden="true">H</b>
            <div>
              <h4>Higgs boson</h4>
              <p>
                Scalar particle · spin 0<br />
                Excitation of the Higgs field
              </p>
            </div>
          </div>
        </div>
      </div>
      <p className="scale-chart-note">
        Particle families are grouped for readability; antiparticles and gluon
        color states are not separately tiled. Gravity is outside the Standard
        Model, and neutrino masses require an extension of its minimal form.{' '}
        <a href="https://home.cern/science/physics/standard-model/">
          Explore the conventional framework at CERN ↗
        </a>
      </p>
    </div>
  );
}

export function BHSMScaleSlices() {
  const [selected, setSelected] = useState(2);
  const layer = layers[selected];
  return (
    <section
      id="bhsm-scale-map"
      className="bhsm-scale-map"
      aria-labelledby="bhsm-scale-title"
    >
      <div className="scale-section-heading">
        <p className="eyebrow">The BHSM scale atlas</p>
        <h2 id="bhsm-scale-title">One picture, from the core to the cosmos.</h2>
        <p>
          Read upward from the proposed hypersphere core through fields,
          particles and matter to cosmic structure. The Standard Model is one
          slice in this larger BHSM conceptual map.
        </p>
      </div>
      <div className="scale-atlas-layout">
        <figure className="scale-sculpture-frame">
          <ScaleSculpture selected={selected} />
          <figcaption>
            Seven separated slices show levels of organization. Their spacing is
            illustrative; the stack is neither a timeline nor a set of measured
            nested shells.
          </figcaption>
        </figure>
        <div className="scale-atlas-reader">
          <p className="scale-selector-label">
            Choose a slice to explore <span>↑ Read from the foundation</span>
          </p>
          <ol className="scale-layer-list" reversed>
            {[...layers].reverse().map((item, i) => {
              const index = 6 - i;
              return (
                <li
                  key={item.name}
                  style={{ '--slice-color': item.color } as CSSProperties}
                >
                  <button
                    type="button"
                    aria-pressed={selected === index}
                    aria-controls="scale-layer-detail"
                    onClick={() => setSelected(index)}
                  >
                    <span className="scale-layer-number">
                      {String(index + 1).padStart(2, '0')}
                    </span>
                    <span>
                      <strong>{item.name}</strong>
                      <small>{item.short}</small>
                    </span>
                    <span className="scale-layer-marker" aria-hidden="true">
                      {selected === index ? '●' : '○'}
                    </span>
                  </button>
                </li>
              );
            })}
          </ol>
          <div
            id="scale-layer-detail"
            className="scale-layer-detail"
            style={{ '--slice-color': layer.color } as CSSProperties}
            aria-live="polite"
            aria-atomic="true"
          >
            <p className="scale-layer-status">{layer.category}</p>
            <h3>{layer.name}</h3>
            <p>{layer.description}</p>
            <p className="scale-detail-context">{layer.detail}</p>
          </div>
        </div>
      </div>
      <ParticleChart />
      <p className="scale-source-note">
        The lower two slices present the BHSM proposal. The higher slices
        organize familiar physical systems; placing them in one diagram does not
        establish a derivation connecting every scale.{' '}
        <a href="./research/lifecycle-core-surface-amendment-20261022.md">
          Read the BHSM core and surface interpretation ↗
        </a>
      </p>
      <a className="scale-tour-link" href="#bhsm-lifecycle">
        Follow formation, persistence and change across the scales →
      </a>
    </section>
  );
}
