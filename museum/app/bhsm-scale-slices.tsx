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
      'The interference drawing and three family tracks are conceptual. They follow the conditional family interpretation into the Standard Model without deriving particle masses or decay probabilities.',
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
      'The first-generation constituent route continues here: electrons and up/down quarks build ordinary atoms. The heavier-family routes stop before this slice; muonic and other exotic atoms are outside this ordinary-matter view.',
  },
  {
    name: 'Molecules',
    short: 'Bonds & chemistry',
    color: '#96dfb1',
    category: 'Established organization of matter',
    description:
      'Atoms join through chemical bonds. Their arrangements create molecules, with properties that depend on structure and environment.',
    detail:
      'The white fork illustrates possible left/right mirror arrangements of the same ingredients. Some molecules are chiral; many are not. This is a new level of organization, not particle generations or particle chirality turning into molecular handedness.',
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
    return null; // Family ports are drawn above the connecting paths.
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
    return null; // The molecular slice carries the mirror pair.
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

const familyLanes = [
  { roman: 'I', x: 150, color: '#71e5eb', quarks: 'u · d', leptons: 'e · νe' },
  { roman: 'II', x: 240, color: '#ffbc77', quarks: 'c · s', leptons: 'μ · νμ' },
  {
    roman: 'III',
    x: 330,
    color: '#d1b8ff',
    quarks: 't · b',
    leptons: 'τ · ντ',
  },
];

function MolecularMirrorPair() {
  return (
    <g className="scale-mirror-pair">
      <path
        d="M240 231 V296"
        stroke="#aac1cf"
        strokeDasharray="2 4"
        opacity=".6"
      />
      {[
        { x: 165, side: 1, label: 'left' },
        { x: 315, side: -1, label: 'right' },
      ].map(({ x, side, label }) => (
        <g key={label}>
          <g transform={`translate(${x} 264) scale(${side} 1)`}>
            <path
              d="M0 0 V-27 M0 0 L-34 7"
              fill="none"
              stroke="#d8efe2"
              strokeWidth="1.8"
            />
            <path d="M0 0 L18 10 L26 20 Z" fill="#96dfb1" />
            {[1, 2, 3, 4].map((i) => (
              <path
                key={i}
                d={`M${i * 5 - i * 0.6} ${-i * 4 - i * 0.7} l${i * 1.2} ${i * 1.4}`}
                stroke="#bda7f5"
                strokeWidth="1.6"
              />
            ))}
            <circle r="5" fill="#eef8f2" />
            <circle cy="-27" r="6" fill="#f4ce77" />
            <circle cx="-34" cy="7" r="6" fill="#71e5eb" />
            <circle cx="22" cy="15" r="6" fill="#ff968a" />
            <circle cx="23" cy="-19" r="6" fill="#bda7f5" />
          </g>
          <text
            x={x}
            y="305"
            textAnchor="middle"
            className="scale-mirror-label"
          >
            {label} · + &amp; −
          </text>
        </g>
      ))}
    </g>
  );
}

function FamilyConnections({ showLines }: { showLines: boolean }) {
  return (
    <g className="scale-family-connections">
      <g opacity={showLines ? 1 : 0}>
        {familyLanes.map((family) => {
          const path = `M240 604 C240 568 ${family.x} 565 ${family.x} 519 V461`;
          return (
            <g key={family.roman}>
              <path d={path} fill="none" stroke="#0b1720" strokeWidth="6" />
              <path
                d={path}
                fill="none"
                stroke={family.color}
                strokeWidth="2.5"
                strokeDasharray="5 4"
              />
              <circle
                cx={family.x}
                cy="519"
                r="10"
                fill="#10212c"
                stroke={family.color}
                strokeWidth="1.3"
              />
              <text
                x={family.x}
                y="523"
                textAnchor="middle"
                fill={family.color}
                className="scale-family-number"
              >
                {family.roman}
              </text>
            </g>
          );
        })}
        <path
          d="M150 405 C150 376 240 385 240 349"
          className="scale-matter-route-back"
        />
        <path
          d="M150 405 C150 376 240 385 240 349"
          className="scale-matter-route"
        />
        <g strokeWidth="2" fill="none">
          <path d="M240 405 V393 M234 393 H246" stroke="#ffbc77" opacity=".6" />
          <path
            d="M330 405 L346 393 M341 389 L351 397"
            stroke="#d1b8ff"
            opacity=".6"
          />
        </g>
        <path
          d="M240 335 C240 310 165 315 165 286 M240 335 C240 310 315 315 315 286"
          fill="none"
          stroke="#0b1720"
          strokeWidth="6"
        />
        <path
          d="M240 335 C240 310 165 315 165 286 M240 335 C240 310 315 315 315 286"
          fill="none"
          stroke="#d9e6e8"
          strokeWidth="2"
        />
        <circle
          cx="240"
          cy="349"
          r="14"
          fill="#10212c"
          stroke="#d9e6e8"
          strokeWidth="1.5"
        />
        <ellipse
          cx="240"
          cy="349"
          rx="10"
          ry="4"
          fill="none"
          stroke="#71e5eb"
        />
        <circle cx="240" cy="349" r="3" fill="#71e5eb" />
        <text x="178" y="373" className="scale-ordinary-constituents">
          u, d, e
        </text>
      </g>
      {familyLanes.map((family) => (
        <g key={family.roman}>
          <rect
            x={family.x - 37}
            y="405"
            width="74"
            height="56"
            rx="6"
            fill="#10212c"
            stroke={family.color}
            strokeWidth="1.5"
          />
          <text
            x={family.x}
            y="420"
            textAnchor="middle"
            fill={family.color}
            className="scale-family-port-number"
          >
            {family.roman}
          </text>
          <text
            x={family.x - 17}
            y="437"
            textAnchor="middle"
            fill="#eef3f6"
            className="scale-family-particles"
          >
            {family.quarks.split(' · ')[0]}
          </text>
          <text
            x={family.x + 17}
            y="437"
            textAnchor="middle"
            fill="#eef3f6"
            className="scale-family-particles"
          >
            {family.quarks.split(' · ')[1]}
          </text>
          <text
            x={family.x - 17}
            y="451"
            textAnchor="middle"
            fill="#d5e4ec"
            className="scale-family-particles"
          >
            {family.leptons.split(' · ')[0]}
          </text>
          <text
            x={family.x + 17}
            y="451"
            textAnchor="middle"
            fill="#a9becb"
            className="scale-family-particles"
          >
            {family.leptons.split(' · ')[1]}
          </text>
        </g>
      ))}
      <MolecularMirrorPair />
    </g>
  );
}

function ChargeConnections() {
  return (
    <g className="scale-charge-connections">
      <g
        fill="none"
        stroke="#ff998a"
        strokeWidth="1.4"
        strokeDasharray="1 3"
        strokeLinecap="round"
      >
        <path d="M85 94 V470 H290" />
        {familyLanes.map(({ x }) => (
          <path key={x} d={`M${x - 40} 470 V433 H${x - 25}`} />
        ))}
        {[
          [94, 150],
          [179, 130],
          [264, 105],
          [349, 105],
        ].map(([y, x]) => (
          <path key={y} d={`M85 ${y} H${x - 9}`} />
        ))}
      </g>
      <g
        fill="none"
        stroke="#79bfff"
        strokeWidth="1.4"
        strokeDasharray="1 3"
        strokeLinecap="round"
      >
        <path d="M397 94 V477 H133" />
        {familyLanes.map(({ x }) => (
          <path
            key={x}
            d={`M${x + 41} 477 V433 H${x + 25} M${x - 17} 477 V455`}
          />
        ))}
        {[
          [94, 330],
          [179, 350],
          [264, 375],
          [349, 375],
        ].map(([y, x]) => (
          <path key={y} d={`M397 ${y} H${x + 9}`} />
        ))}
      </g>
      {familyLanes.map(({ x }) => (
        <g key={x} fill="none" strokeWidth="1">
          <circle cx={x - 17} cy="433" r="8" stroke="#ff998a" />
          <circle cx={x + 17} cy="433" r="8" stroke="#79bfff" />
          <circle cx={x - 17} cy="448" r="7" stroke="#79bfff" />
        </g>
      ))}
      {[
        {
          sign: '+',
          color: '#ff998a',
          positions: [
            [94, 150],
            [179, 130],
            [264, 105],
            [349, 105],
            [470, 85],
          ],
        },
        {
          sign: '−',
          color: '#79bfff',
          positions: [
            [94, 330],
            [179, 350],
            [264, 375],
            [349, 375],
            [477, 397],
          ],
        },
      ].map(({ sign, color, positions }) => (
        <g key={sign} fill={color}>
          {positions.map(([y, x]) => (
            <g key={y}>
              <circle
                cx={x}
                cy={y}
                r="9"
                fill="#10212c"
                stroke={color}
                strokeWidth="1.5"
              />
              <text
                x={x}
                y={y + 4}
                textAnchor="middle"
                className="scale-charge-sign"
              >
                {sign}
              </text>
            </g>
          ))}
        </g>
      ))}
    </g>
  );
}

function ScaleSculpture({
  selected,
  threads,
}: {
  selected: number;
  threads: string;
}) {
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
      <FamilyConnections showLines={threads !== 'charge'} />
      {threads !== 'families' && <ChargeConnections />}
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
  const [threads, setThreads] = useState('both');
  const [shareStatus, setShareStatus] = useState('');
  const [fallbackLink, setFallbackLink] = useState('');
  const layer = layers[selected];

  async function copyAtlasLink() {
    const url = new URL(window.location.href);
    url.hash = 'bhsm-scale-map';
    const link = url.toString();
    try {
      if (!navigator.clipboard?.writeText)
        throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(link);
      setFallbackLink('');
      setShareStatus('Atlas link copied. Share it with someone curious.');
    } catch {
      setFallbackLink(link);
      setShareStatus('Select and copy the atlas link below.');
    }
  }

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
        <div
          className="scale-share-actions"
          aria-label="Take the scale atlas with you"
        >
          <a
            href="./learn/bhsm-scale-atlas.svg"
            download="BHSM-scale-atlas.svg"
          >
            Download the atlas poster <span>SVG · printable at any size ↓</span>
          </a>
          <button type="button" onClick={copyAtlasLink}>
            Copy a link to the atlas ↗
          </button>
        </div>
        <p className="scale-share-status" role="status">
          {shareStatus}
        </p>
        {fallbackLink && (
          <label className="scale-share-fallback">
            Atlas link
            <input
              type="url"
              value={fallbackLink}
              readOnly
              onFocus={(event) => event.currentTarget.select()}
              onClick={(event) => event.currentTarget.select()}
            />
          </label>
        )}
      </div>
      <div className="scale-atlas-layout">
        <figure className="scale-sculpture-frame">
          <div className="scale-thread-controls" aria-label="Atlas thread view">
            {[
              ['both', 'Both threads'],
              ['families', 'Family paths'],
              ['charge', 'Electric charge'],
            ].map(([value, label]) => (
              <button
                key={value}
                type="button"
                aria-pressed={threads === value}
                onClick={() => setThreads(value)}
              >
                {label}
              </button>
            ))}
          </div>
          <ScaleSculpture selected={selected} threads={threads} />
          <figcaption>
            Follow three family paths from the proposed core and modes to their
            Standard Model slots. The ordinary-matter route continues through
            atoms to two mirror-image molecular arrangements. Slice spacing is
            illustrative, not a timeline or measured nested shells. The dotted
            +/− threads follow charged constituents and carriers, not spin or
            the net charge of whole neutral objects.
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
      <div
        className="scale-family-key"
        aria-labelledby="scale-family-key-title"
      >
        <h3 id="scale-family-key-title">
          Three families. Ordinary matter. Molecular handedness.
        </h3>
        <ul className="scale-family-legend">
          {familyLanes.map((family) => (
            <li
              key={family.roman}
              style={{ '--family-color': family.color } as CSSProperties}
            >
              <span>{family.roman}</span> {family.quarks} · {family.leptons}
            </li>
          ))}
        </ul>
        <p>
          Dashed lower paths show the conditional BHSM family interpretation,
          not computed trajectories or a derivation of the family masses. At the
          particle slice, I, II and III mark the three conventional fermion
          generations; gauge bosons and the Higgs are shared across them.
        </p>
        <p>
          The electron and up/down quarks supply the constituents of ordinary
          atoms. The II and III routes end before that slice because their
          heavier charged relatives do not build ordinary stable atoms. This
          does not erase their neutrinos, depict a decay chain, or cover muonic
          and other exotic atoms.
        </p>
        <div className="scale-charge-key">
          <h4>Electric charge through the scales</h4>
          <p>
            <span className="scale-charge-positive">+ positive:</span> up, charm
            and top quarks (+⅔e).{' '}
            <span className="scale-charge-negative">− negative:</span> down,
            strange and bottom quarks (−⅓e), and electron, muon and tau (−1e).
            Neutrinos have zero electric charge and no charge-thread connection.
          </p>
          <p>
            W+ and W− also carry ±1e; they sit in the shared boson group below.
            Photon, gluon, Z and Higgs have zero electric charge, so the
            electric threads skip them. Gluon color charge is a different
            property.
          </p>
          <p>
            At atomic and molecular scales, +/− mark nuclei and electrons. At
            planetary, stellar and cosmic scales, they mark charged constituents
            or plasma carriers. A neutral atom, molecule or larger system can
            contain both; the diagram does not assign it a net charge. The
            charge paths begin at the Standard Model slice, with no electric
            charge assigned to the proposed core or modes. Molecular handedness
            is independent of the +/− sign.
          </p>
        </div>
        <p>
          Above atoms, the neutral fork changes the level of description: some
          molecular arrangements come in non-superposable mirror pairs. The two
          labels mean visual left and right, not assigned R/S or D/L
          configurations. Not all molecules are chiral, and molecular handedness
          is not a conversion of particle generation or particle chirality.{' '}
          <a href="https://goldbook.iupac.org/terms/view/C01058">
            IUPAC: chirality ↗
          </a>{' '}
          ·{' '}
          <a href="https://goldbook.iupac.org/terms/view/E02069">
            enantiomers ↗
          </a>
        </p>
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
