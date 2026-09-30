'use client';
/* oxlint-disable jsx-a11y/prefer-tag-over-role -- Named inline SVG illustrations. */
/* oxlint-disable jsx-a11y/no-noninteractive-tabindex -- Independent scroll regions need keyboard focus for arrow/PageDown scrolling. */
import { useState } from 'react';
import { useSceneClock } from './science-console';
import { StructureShowcase } from './structure-showcase';
import {
  harmonicCurve,
  hexagon,
  hypersphereCurves,
} from '../lib/children-geometry';

const foundations = [
  {
    name: 'Core / topology',
    kind: 'core',
    caption:
      'BHSM proposition: only a hypersphere can supply the foundations of this reality.',
    examples: ['Hypersphere S³', 'Closed manifold', 'Linked Hopf fibers'],
    detail: 'A rotating projection of the three-sphere in four dimensions.',
  },
  {
    name: 'Modes',
    kind: 'modes',
    caption: 'Harmonic vibrational patterns: one structure, different modes.',
    examples: ['Fundamental', 'Second harmonic', 'Third harmonic'],
    detail: 'Standing-wave examples reveal nodes and antinodes.',
  },
  {
    name: 'Geometry',
    kind: 'geometry',
    caption:
      'Two hexagonal patterns overlap to reveal a changing moiré structure.',
    examples: ['Symmetry', 'Relative rotation', 'Interference pattern'],
    detail: 'A geometric analogy for how relationships create larger patterns.',
  },
];
const families = [
  {
    name: 'Quarks',
    particles: ['u', 'c', 't', 'd', 's', 'b'],
    tone: 'quarks',
    detail: 'Up and down quarks form protons and neutrons.',
  },
  {
    name: 'Leptons',
    particles: ['e', 'μ', 'τ', 'νₑ', 'νμ', 'ντ'],
    tone: 'leptons',
    detail:
      'Electrons, their heavier relatives and the three neutrino flavors.',
  },
  {
    name: 'Gauge bosons',
    particles: ['g', 'γ', 'Z', 'W⁺', 'W⁻'],
    tone: 'bosons',
    detail: 'Gluons, photons and the W and Z bosons mediate interactions.',
  },
  {
    name: 'Scalar',
    particles: ['H'],
    tone: 'scalar',
    detail: 'The Higgs boson is an excitation of the Higgs field.',
  },
];
function Showcase({ kind, time }: { kind: string; time: number }) {
  return (
    <svg
      className="children-scene"
      viewBox="0 0 220 116"
      role="img"
      aria-label={
        {
          core: 'Rotating four-dimensional hypersphere projection',
          modes: 'Three standing-wave harmonic modes with fixed nodes',
          geometry:
            'Two overlapping hexagonal grids create a moving moiré pattern',
        }[kind]
      }
    >
      {kind === 'core' && (
        <g fill="none">
          {hypersphereCurves(time).map((d, i) => (
            <path
              key={i}
              d={d}
              stroke={i % 3 === 0 ? '#ffbc77' : '#bda7f5'}
              strokeWidth=".8"
              opacity=".65"
            />
          ))}
          <text x="12" y="18">
            S³ ⊂ R⁴
          </text>
        </g>
      )}
      {kind === 'modes' && (
        <g fill="none">
          {[1, 2, 3].map((n) => (
            <g key={n}>
              <path d={`M28 ${20 + (n - 1) * 35}H198`} stroke="#393449" />
              <path
                d={harmonicCurve(n, time)}
                stroke={['#ffbc77', '#bda7f5', '#71e5eb'][n - 1]}
                strokeWidth="2"
              />
              {Array.from({ length: n + 1 }, (_, i) => (
                <circle
                  key={i}
                  cx={28 + (i * 170) / n}
                  cy={20 + (n - 1) * 35}
                  r="2"
                  fill="#ede4ff"
                />
              ))}
              <text x="9" y={23 + (n - 1) * 35}>
                {n}
              </text>
            </g>
          ))}
        </g>
      )}
      {kind === 'geometry' && (
        <g fill="none" strokeWidth=".65">
          {[0, 1].map((layer) => (
            <g
              key={layer}
              stroke={layer ? '#ffbc77' : '#71e5eb'}
              opacity=".65"
              transform={`rotate(${layer ? 8 + 7 * Math.sin(time * 0.3) : 0} 110 58)`}
            >
              {Array.from({ length: 23 }, (_, i) => (
                <path key={i} d={hexagon(4 + i * 2.25)} />
              ))}
            </g>
          ))}
        </g>
      )}
    </svg>
  );
}

function ExampleCard({
  item,
  time,
}: {
  item: (typeof foundations)[number];
  time: number;
}) {
  return (
    <li className={`children-example children-example-${item.kind}`}>
      <strong>{item.name}</strong>
      <Showcase kind={item.kind} time={time} />
      <p>{item.caption}</p>
      <ul className="children-examples" aria-label={`${item.name} examples`}>
        {item.examples.map((example) => (
          <li key={example}>{example}</li>
        ))}
      </ul>
      <small>{item.detail}</small>
    </li>
  );
}

export function ChildrenOfBHSM({ motion }: { motion: boolean }) {
  const { ref, time } = useSceneClock(motion);
  const [property, setProperty] = useState('charge');
  return (
    <section className="bhsm-children" aria-labelledby="children-title">
      <header className="children-heading">
        <div>
          <p className="eyebrow">Different scales · one connected story</p>
          <h2 id="children-title">
            Children <em>of</em> BHSM
          </h2>
        </div>
        <p>From deep structure to a universe of structure.</p>
      </header>
      <div className="children-map" ref={ref}>
        <section
          className="children-foundations children-panel"
          tabIndex={0}
          aria-label="01 Proposed foundations — scroll to explore"
        >
          <h3>
            01 <span>Proposed foundations</span>
          </h3>
          <ol>
            {foundations.map((item) => (
              <ExampleCard key={item.kind} item={item} time={time} />
            ))}
          </ol>
        </section>
        <span className="children-bridge" aria-hidden="true">
          →
        </span>
        <section
          className="children-particles children-panel"
          tabIndex={0}
          aria-label="02 Standard Model particle table — scroll to explore"
        >
          <h3>
            02 <span>Standard Model particle table</span>
          </h3>
          <p>One layer in the proposed BHSM child graph</p>
          <div className="particle-properties" aria-label="Particle property">
            {['charge', 'spin'].map((name) => (
              <button
                key={name}
                aria-pressed={property === name}
                onClick={() => setProperty(name)}
              >
                {name === 'charge' ? 'Electric charge' : 'Quantum spin'}
              </button>
            ))}
          </div>
          <div className="children-families">
            {families.map(({ name, particles, tone, detail }) => (
              <div className={`children-family children-${tone}`} key={name}>
                <h4>{name}</h4>
                <div className="children-particle-grid">
                  {particles.map((p, index) => (
                    <div className="children-particle-cell" key={p}>
                      <span>{p}</span>
                      <small>
                        {property === 'spin'
                          ? tone === 'scalar'
                            ? 's = 0'
                            : tone === 'bosons'
                              ? 's = 1'
                              : 's = ½'
                          : `Q = ${tone === 'quarks' ? (index < 3 ? '+⅔' : '−⅓') : tone === 'leptons' ? (index < 3 ? '−1' : '0') : p === 'W⁺' ? '+1' : p === 'W⁻' ? '−1' : '0'}`}
                      </small>
                    </div>
                  ))}
                </div>
                <p>{detail}</p>
              </div>
            ))}
          </div>
          <p className="children-particle-bridge">
            Particle families provide the ingredients. Binding and collective
            behavior build the structures in the next panel.
          </p>
          <small>
            Charge is in units of e. Spin is in units of ℏ: an intrinsic quantum
            property, not a rotating surface.
          </small>
          <a href="https://home.cern/science/physics/standard-model">
            Standard Model reference ↗
          </a>
        </section>
        <span className="children-bridge" aria-hidden="true">
          →
        </span>
        <section
          className="children-structures children-panel"
          tabIndex={0}
          aria-label="03 Structures across scales — scroll to explore"
        >
          <h3>
            03 <span>Structures across scales</span>
          </h3>
          <StructureShowcase time={time} />
        </section>
      </div>
      <p className="children-scope">
        The hypersphere foundation and core–modes–geometry connections are BHSM
        propositions; their physical derivation remains open. The projected
        hypersphere, harmonic and moiré studies illustrate mathematical ideas.
        Particle families and larger structures are established categories.
        Animations are schematic, with no physical scale or rate calibration.
      </p>
    </section>
  );
}
