'use client';
/* oxlint-disable jsx-a11y/prefer-tag-over-role -- Named inline SVG illustrations. */
import { useSceneClock } from './science-console';
import {
  curve,
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
const structures = [
  {
    name: 'Hadrons',
    kind: 'hadrons',
    caption: 'Quarks bound by the strong interaction.',
    examples: ['Proton · uud', 'Neutron · udd'],
    detail:
      'A proton’s valence content; its full state also includes gluons and sea quarks.',
  },
  {
    name: 'Nuclei',
    kind: 'nuclei',
    caption: 'Protons and neutrons build atomic nuclei.',
    examples: ['Helium-4 · 2p + 2n', 'Carbon-12 · 6p + 6n'],
    detail: 'Shown: a helium-4 nucleus.',
  },
  {
    name: 'Atoms',
    kind: 'atoms',
    caption: 'An electron cloud surrounds a nucleus.',
    examples: ['Hydrogen', 'Helium', 'Carbon'],
    detail:
      'Shown: hydrogen. Moving marks suggest a cloud, not classical electron orbits.',
  },
  {
    name: 'Molecules',
    kind: 'molecules',
    caption: 'Chemical bonds connect atoms into new structures.',
    examples: ['Water · H₂O', 'Carbon dioxide · CO₂', 'DNA'],
    detail: 'Shown: water’s bent shape, with a schematic molecular vibration.',
  },
  {
    name: 'Matter',
    kind: 'matter',
    caption: 'Many particles produce collective states.',
    examples: [
      'Ice · solid',
      'Water · liquid',
      'Air · gas',
      'Ionized gas · plasma',
    ],
    detail: 'Order, rearrangement, free motion and charged constituents.',
  },
  {
    name: 'Astronomical structures',
    kind: 'cosmos',
    caption: 'Gravity assembles matter across cosmic scales.',
    examples: ['Earth', 'Sun', 'Milky Way', 'Cosmic web'],
    detail:
      'Shown: a schematic spiral galaxy, with stars moving around its center.',
  },
];

function Showcase({ kind, time }: { kind: string; time: number }) {
  const orbit = (angle: number, rx: number, ry: number) => [
    110 + Math.cos(angle) * rx,
    58 + Math.sin(angle) * ry,
  ];
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
          hadrons: 'Three labeled valence quarks in a schematic proton',
          nuclei: 'Two protons and two neutrons in helium-4',
          atoms: 'Schematic hydrogen electron cloud surrounding a proton',
          molecules:
            'A bent water molecule with two hydrogen atoms and one oxygen',
          matter: 'Particle arrangements in solid, liquid, gas and plasma',
          cosmos: 'A rotating spiral galaxy with stars and a central bulge',
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
      {kind === 'hadrons' && (
        <g>
          <ellipse
            cx="110"
            cy="58"
            rx="62"
            ry="43"
            fill="#bda7f50c"
            stroke="#bda7f550"
          />
          {[0, 1, 2].map((i) => {
            const [x, y] = orbit(time * 0.4 + (i * Math.PI * 2) / 3, 38, 28);
            return (
              <g key={i}>
                <path
                  d={`M110 58Q${x + 12} 58 ${x} ${y}`}
                  stroke="#ffbc77"
                  fill="none"
                />
                <circle cx={x} cy={y} r="11" fill="#292038" stroke="#bda7f5" />
                <text x={x} y={y + 4} textAnchor="middle">
                  {i === 2 ? 'd' : 'u'}
                </text>
              </g>
            );
          })}
        </g>
      )}
      {kind === 'nuclei' && (
        <g>
          {[
            [-13, -12],
            [13, -12],
            [-13, 12],
            [13, 12],
          ].map(([x, y], i) => (
            <g
              key={i}
              transform={`translate(${110 + x + Math.sin(time + i) * 1.2} ${58 + y})`}
            >
              <circle
                r="18"
                fill={i % 2 ? '#2f244a' : '#573728'}
                stroke={i % 2 ? '#bda7f5' : '#ffbc77'}
              />
              <text y="4" textAnchor="middle">
                {i % 2 ? 'n' : 'p'}
              </text>
            </g>
          ))}
        </g>
      )}
      {kind === 'atoms' && (
        <g>
          {[42, 35, 28, 21].map((r) => (
            <circle
              key={r}
              cx="110"
              cy="58"
              r={r}
              fill="#71e5eb08"
              stroke="#71e5eb16"
            />
          ))}
          {Array.from({ length: 55 }, (_, i) => {
            const radius = 13 + 29 * Math.sqrt((i + 0.5) / 55);
            const [x, y] = orbit(
              i * 2.39996 + time * (0.15 + (i % 3) * 0.03),
              radius,
              radius,
            );
            return (
              <circle
                key={i}
                cx={x}
                cy={y}
                r="1"
                fill="#71e5eb"
                opacity=".35"
              />
            );
          })}
          <circle cx="110" cy="58" r="7" fill="#ffbc77" />
          <text x="124" y="62">
            p
          </text>
        </g>
      )}
      {kind === 'molecules' && (
        <g>
          {[-1, 1].map((side) => {
            const x = 110 + side * (36 + 2 * Math.sin(time * 2));
            const y = 76 + 2 * Math.sin(time * 2);
            return (
              <g key={side}>
                <path
                  d={`M110 48L${x} ${y}`}
                  stroke="#bda7f5"
                  strokeWidth="4"
                />
                <circle cx={x} cy={y} r="12" fill="#173640" stroke="#71e5eb" />
                <text x={x} y={y + 4} textAnchor="middle">
                  H
                </text>
              </g>
            );
          })}
          <circle cx="110" cy="48" r="20" fill="#573728" stroke="#ffbc77" />
          <text x="110" y="52" textAnchor="middle">
            O
          </text>
        </g>
      )}
      {kind === 'matter' && (
        <g>
          {['Solid', 'Liquid', 'Gas', 'Plasma'].map((label, state) => (
            <g key={label}>
              <rect
                x={3 + state * 55}
                y="14"
                width="49"
                height="74"
                rx="5"
                fill="#ffffff03"
                stroke="#494257"
              />
              {Array.from({ length: 9 }, (_, i) => {
                const phase = time * 0.6 + i * 2.4;
                const x =
                  state > 1
                    ? 27 + state * 55 + 18 * Math.sin(phase * (1 + i * 0.07))
                    : 13 +
                      state * 55 +
                      (i % 3) * 12 +
                      Math.sin(phase) * (state ? 4 : 0.4);
                const y =
                  state > 1
                    ? 51 + 29 * Math.cos(phase * 0.83 + i)
                    : state === 1
                      ? 55 + Math.floor(i / 3) * 10 + 4 * Math.cos(phase)
                      : 28 + Math.floor(i / 3) * 22 + 0.4 * Math.cos(phase);
                return (
                  <g key={i}>
                    <circle
                      cx={x}
                      cy={y}
                      r={state === 3 && i % 2 ? 1.5 : 3}
                      fill={state === 3 && i % 2 ? '#bda7f5' : '#71e5eb'}
                    />
                    {state === 3 && (
                      <text x={x + 3} y={y - 3} fontSize="7">
                        {i % 2 ? '−' : '+'}
                      </text>
                    )}
                  </g>
                );
              })}
              <text x={27 + state * 55} y="104" textAnchor="middle">
                {label}
              </text>
            </g>
          ))}
        </g>
      )}
      {kind === 'cosmos' && (
        <g>
          <ellipse cx="110" cy="58" rx="76" ry="40" fill="#bda7f508" />
          {[0, 1, 2].map((arm) => (
            <g key={arm}>
              <path
                d={curve(
                  Array.from({ length: 70 }, (_, i) =>
                    orbit(
                      (arm * Math.PI * 2) / 3 + i * 0.05 + time * 0.12,
                      5 + i,
                      2 + i * 0.45,
                    ),
                  ),
                )}
                fill="none"
                stroke="#bda7f5"
                opacity=".4"
              />
              {Array.from({ length: 35 }, (_, i) => {
                const [x, y] = orbit(
                  (arm * Math.PI * 2) / 3 + i * 0.1 + time * 0.12,
                  6 + i * 2,
                  3 + i * 0.9,
                );
                return (
                  <circle
                    key={i}
                    cx={x}
                    cy={y}
                    r={i % 4 ? 1 : 1.7}
                    fill={i % 3 ? '#bda7f5' : '#ffbc77'}
                  />
                );
              })}
            </g>
          ))}
          {[14, 9, 5].map((r) => (
            <ellipse
              key={r}
              cx="110"
              cy="58"
              rx={r}
              ry={r * 0.6}
              fill="#ffbc7740"
            />
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
        <div className="children-foundations">
          <h3>
            01 <span>Proposed foundations</span>
          </h3>
          <ol>
            {foundations.map((item) => (
              <ExampleCard key={item.kind} item={item} time={time} />
            ))}
          </ol>
        </div>
        <span className="children-bridge" aria-hidden="true">
          →
        </span>
        <div className="children-particles">
          <h3>
            02 <span>Standard Model particle table</span>
          </h3>
          <p>One layer in the proposed BHSM child graph</p>
          <div className="children-families">
            {families.map(({ name, particles, tone, detail }) => (
              <div className={`children-family children-${tone}`} key={name}>
                <h4>{name}</h4>
                <div>
                  {particles.map((p) => (
                    <span key={p}>{p}</span>
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
        </div>
        <span className="children-bridge" aria-hidden="true">
          →
        </span>
        <div className="children-structures">
          <h3>
            03 <span>Structures across scales</span>
          </h3>
          <ol>
            {structures.map((item) => (
              <ExampleCard key={item.kind} item={item} time={time} />
            ))}
          </ol>
        </div>
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
