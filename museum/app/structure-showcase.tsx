'use client';
/* oxlint-disable jsx-a11y/prefer-tag-over-role -- Named inline SVG illustrations. */
import { useId, useState } from 'react';
import { curve } from '../lib/children-geometry';
import { OrbitalStudy } from './orbital-study';
import { matterCycle } from '../lib/orbital-density';

const catalog = [
  {
    name: 'Hadrons',
    kind: 'hadrons',
    caption: 'Quarks interact through the gluon field.',
    choices: [
      [
        'Proton · uud',
        'Two up quarks and one down quark, with animated gluon exchanges.',
      ],
      [
        'Neutron · udd',
        'One up quark and two down quarks, with animated gluon exchanges.',
      ],
    ],
    note: 'Exchange paths and color-charge changes are schematic. The full hadron also contains sea quarks and gluons.',
    source: [
      'Quarks and gluons',
      'https://www.energy.gov/science/doe-explainsquarks-and-gluons',
    ],
  },
  {
    name: 'Nuclei',
    kind: 'nuclei',
    caption: 'Protons and neutrons form a bound nucleus.',
    choices: [
      ['Helium-4 · 2p + 2n', 'Four nucleons: two protons and two neutrons.'],
      ['Carbon-12 · 6p + 6n', 'Twelve nucleons: six protons and six neutrons.'],
    ],
    note: 'A static constituent-count illustration; positions are schematic.',
    source: [
      'Nuclear structure',
      'https://openstax.org/books/university-physics-volume-3/pages/10-1-properties-of-nuclei',
    ],
  },
  {
    name: 'Atoms',
    kind: 'atoms',
    caption:
      'Glowing probability densities reveal orbital shapes and dark nodes.',
    choices: [
      [
        'Hydrogen',
        'Hydrogen-1 · 1 proton · 1 electron. Explore the ground-state 1s orbital and selected excited states.',
      ],
      [
        'Carbon',
        'Carbon-12 · 6 protons + 6 neutrons · 6 electrons · 1s² 2s² 2p². Inspect illustrative s and p orbital sections.',
      ],
    ],
    note: 'Brightness represents relative probability density. Dark nodes are places where the displayed wavefunction vanishes; electrons do not follow the outlines as paths.',
    source: [
      'Quantum model of the atom',
      'https://openstax.org/books/chemistry-atoms-first-2e/pages/3-3-development-of-quantum-theory',
    ],
  },
  {
    name: 'Molecules',
    kind: 'molecules',
    caption: 'Bond geometry gives molecules their structure.',
    choices: [
      [
        'Water · H₂O',
        'Water’s equilibrium H–O–H angle is about 104.5°. A small bending oscillation illustrates the vibrational mode; amplitude and speed are illustrative.',
      ],
      [
        'Carbon dioxide · CO₂',
        'O=C=O: a linear molecule with two double bonds. Shown with a schematic stretching vibration.',
      ],
      [
        'DNA',
        'Two helical backbones joined by complementary base pairs: A–T and G–C.',
      ],
    ],
    note: 'Illustrative shapes and motion; sizes and vibration rates are not calibrated.',
    source: [
      'Molecular structure and bond angles',
      'https://openstax.org/books/chemistry-atoms-first-2e/pages/4-6-molecular-structure-and-polarity',
    ],
  },
  {
    name: 'Matter',
    kind: 'matter',
    caption: 'Collective behavior changes with the state of matter.',
    choices: [
      [
        'Ice · solid',
        'An ordered solid: constituents vibrate near fixed positions.',
      ],
      [
        'Water · liquid',
        'A liquid: closely packed constituents rearrange while occupying the bottom of the container.',
      ],
      [
        'Air · gas',
        'A gas: separated constituents move throughout the container.',
      ],
      [
        'Ionized gas · plasma',
        'A plasma: mobile ions and electrons form a charged collective system.',
      ],
    ],
    note: 'Reference-science diagrams: particles vibrate, rearrange or move freely according to the selected state. This is not a molecular-dynamics solver or a time-resolved phase transition.',
    source: [
      'States of matter',
      'https://openstax.org/books/chemistry-2e/pages/1-2-phases-and-classification-of-matter',
    ],
  },
  {
    name: 'Astronomical structures',
    kind: 'cosmos',
    caption: 'Galaxies, clustering patterns and immense flows of matter.',
    choices: [
      [
        'Milky Way',
        'A schematic spiral galaxy with a central bulge and star-filled arms.',
      ],
      [
        'Cosmic web',
        'Filaments and dense galaxy clusters surround broad voids.',
      ],
      [
        'BAO',
        'Baryon acoustic oscillations leave a preferred separation in galaxy clustering. The ring marks a statistical excess of pairs, not a physical shell around every galaxy.',
      ],
      [
        'Laniakea',
        'A supercluster mapped as a basin of galaxy flows, including our Milky Way. Streamlines illustrate the flow toward its interior.',
      ],
      [
        'Great Attractor',
        'A large concentration of matter associated with coherent galaxy motions in the local Universe. It is a gravitational region, not a single object.',
      ],
      [
        'Shapley',
        'The Shapley Supercluster is a rich concentration of galaxy clusters on still larger scales.',
      ],
    ],
    note: 'Qualitative views, not survey reconstructions. Flow-basin boundaries depend on the velocity data and analysis.',
  },
];

const tones = ['#ffbc77', '#71e5eb', '#bda7f5'];
const point = (a: number, r: number, squash = 1) => [
  110 + Math.cos(a) * r,
  59 + Math.sin(a) * r * squash,
];

function Nucleus({
  count,
  small = false,
  time,
}: {
  count: number;
  small?: boolean;
  time: number;
}) {
  const radius = small ? 2.7 : count === 4 ? 15 : 9;
  return (
    <g>
      <circle
        cx="110"
        cy="59"
        r={
          small
            ? Math.max(6, Math.sqrt(count) * radius * 1.45 + radius + 2)
            : 51
        }
        fill="none"
        stroke="#ffdcaa"
        strokeWidth={small ? 0.7 : 1.2}
        opacity=".7"
      />
      {Array.from({ length: count }, (_, i) => {
        const angle = i * 2.39996;
        const spread = count === 1 ? 0 : Math.sqrt(i + 0.5) * radius * 1.45;
        return (
          <g
            key={i}
            transform={`translate(${110 + Math.cos(angle) * spread + (small ? 0 : 0.6 * Math.sin(time + i))} ${59 + Math.sin(angle) * spread})`}
          >
            <circle
              r={radius}
              fill={i % 2 ? '#352749' : '#604028'}
              stroke={i % 2 ? tones[2] : tones[0]}
              strokeWidth=".8"
            />
            {!small && (
              <text y="3.5" textAnchor="middle">
                {i % 2 ? 'n' : 'p'}
              </text>
            )}
          </g>
        );
      })}
    </g>
  );
}

function Hadron({ selected, time }: { selected: number; time: number }) {
  const quarks = Array.from({ length: 3 }, (_, i) =>
    point(-Math.PI / 2 + (i * Math.PI * 2) / 3 + 0.08 * Math.sin(time + i), 35),
  );
  return (
    <g>
      <ellipse
        cx="110"
        cy="59"
        rx="66"
        ry="45"
        fill="#bda7f50a"
        stroke="#bda7f535"
      />
      {quarks.map(([x, y], i) => {
        const [tx, ty] = quarks[(i + 1) % 3];
        const dx = tx - x,
          dy = ty - y,
          length = Math.hypot(dx, dy);
        const at = (s: number) => {
          const wave =
            4 * Math.sin(s * Math.PI * 12 - time * 3) * Math.sin(Math.PI * s);
          return [
            x + s * dx - (wave * dy) / length,
            y + s * dy + (wave * dx) / length,
          ];
        };
        const [gx, gy] = at((time * 0.35 + i / 3) % 1);
        return (
          <g key={i}>
            <path
              d={curve(Array.from({ length: 65 }, (_, k) => at(k / 64)))}
              fill="none"
              stroke={tones[i]}
              strokeWidth="1.6"
              opacity=".8"
            />
            <circle cx={gx} cy={gy} r="6" fill="#0a101c" stroke={tones[i]} />
            <text
              x={gx}
              y={gy + 3}
              textAnchor="middle"
              className="children-gluon-label"
            >
              g
            </text>
          </g>
        );
      })}
      {quarks.map(([x, y], i) => (
        <g key={i}>
          <circle
            cx={x}
            cy={y}
            r="11"
            fill="#191827"
            stroke={tones[(i + Math.floor(time * 0.35)) % 3]}
            strokeWidth="2"
          />
          <text x={x} y={y + 4} textAnchor="middle">
            {i === 0 || (i === 1 && selected === 0) ? 'u' : 'd'}
          </text>
        </g>
      ))}
      <text x="110" y="113" textAnchor="middle">
        g · gluon exchange
      </text>
    </g>
  );
}

function Molecule({ selected, time }: { selected: number; time: number }) {
  if (selected === 2)
    return (
      <g>
        {[0, Math.PI].map((phase, j) => (
          <path
            key={j}
            d={curve(
              Array.from({ length: 90 }, (_, i) => [
                110 +
                  30 * Math.sin((i / 89) * Math.PI * 4 + time * 0.35 + phase),
                8 + (i / 89) * 99,
              ]),
            )}
            stroke={tones[j + 1]}
            strokeWidth="3"
            fill="none"
          />
        ))}
        {Array.from({ length: 10 }, (_, i) => {
          const x = 30 * Math.sin((i / 9) * Math.PI * 4 + time * 0.35);
          return (
            <g key={i}>
              <path
                d={`M${110 - x} ${9 + i * 10.6}H${110 + x}`}
                stroke={tones[0]}
                opacity=".6"
              />
              <text x="156" y={12 + i * 10.6}>
                {i % 2 ? 'G–C' : 'A–T'}
              </text>
            </g>
          );
        })}
      </g>
    );
  const co2 = selected === 1;
  return (
    <g>
      {[-1, 1].map((side) => {
        const x =
          110 +
          side *
            (co2
              ? 56 + 4 * Math.sin(time * 2)
              : 44 *
                Math.sin(((52.25 + 1.5 * Math.sin(time * 2)) * Math.PI) / 180));
        const y = co2
          ? 59
          : 48 +
            44 * Math.cos(((52.25 + 1.5 * Math.sin(time * 2)) * Math.PI) / 180);
        return (
          <g key={side}>
            {(co2 ? [-3, 3] : [0]).map((offset) => (
              <path
                key={offset}
                d={`M110 ${(co2 ? 59 : 48) + offset}L${x} ${y + offset}`}
                stroke={tones[2]}
                strokeWidth="2.5"
              />
            ))}
            <circle
              cx={x}
              cy={y}
              r={co2 ? 17 : 12}
              fill={co2 ? '#573728' : '#173640'}
              stroke={co2 ? tones[0] : tones[1]}
            />
            <text x={x} y={y + 4} textAnchor="middle">
              {co2 ? 'O' : 'H'}
            </text>
          </g>
        );
      })}
      <circle
        cx="110"
        cy={co2 ? 59 : 48}
        r="19"
        fill={co2 ? '#352749' : '#573728'}
        stroke={co2 ? tones[2] : tones[0]}
      />
      <text x="110" y={co2 ? 63 : 52} textAnchor="middle">
        {co2 ? 'C' : 'O'}
      </text>
    </g>
  );
}

function Matter({ selected, time }: { selected: number; time: number }) {
  return (
    <g>
      <rect
        x="21"
        y="8"
        width="178"
        height="94"
        rx="8"
        fill="#71e5eb04"
        stroke="#575067"
      />
      {selected === 1 && (
        <path
          d={`M23 47Q65 ${45 + 2 * Math.sin(time)} 110 47T197 47V99H23Z`}
          fill="#71e5eb0c"
        />
      )}
      {Array.from({ length: 24 }, (_, i) => {
        const phase = time * 0.65 + i * 2.4;
        const x =
          selected > 1
            ? 110 + 77 * Math.sin(phase * (1 + i * 0.02))
            : 39 + (i % 6) * 28 + Math.sin(phase) * (selected ? 6 : 1);
        const y =
          selected > 1
            ? 55 + 38 * Math.cos(phase * 0.83 + i)
            : selected === 1
              ? 57 + Math.floor(i / 6) * 11 + 4 * Math.cos(phase)
              : 24 + Math.floor(i / 6) * 21 + Math.cos(phase);
        return (
          <g key={i}>
            <circle
              cx={x}
              cy={y}
              r={selected === 3 && i % 2 ? 2 : 4}
              fill={selected === 3 && i % 2 ? tones[2] : tones[1]}
            />
            {selected === 3 && (
              <text x={x + 4} y={y - 4}>
                {i % 2 ? '−' : '+'}
              </text>
            )}
          </g>
        );
      })}
    </g>
  );
}

function Cosmos({ selected, time }: { selected: number; time: number }) {
  if (selected === 2)
    return (
      <g>
        <ellipse
          cx="110"
          cy="57"
          rx="70"
          ry="40"
          fill="none"
          stroke="#ffbc7755"
          strokeWidth="7"
        />
        {Array.from({ length: 110 }, (_, i) => {
          const a = i * 2.39996,
            radius = i < 62 ? 39 + 4 * Math.sin(i * 3.2) : 8 + (i % 43);
          return (
            <circle
              key={i}
              cx={110 + Math.cos(a) * radius * 1.75}
              cy={57 + Math.sin(a) * radius}
              r={i < 62 ? 1.2 : 0.8}
              fill={tones[i % 3]}
              opacity=".7"
            />
          );
        })}
        <circle cx="110" cy="57" r="3" fill="#fff3da" />
        <path d="M110 57H180" stroke="#ffe2b7" strokeDasharray="3 3" />
        <text x="110" y="115" textAnchor="middle">
          Preferred galaxy separation
        </text>
      </g>
    );
  if (selected === 3 || selected === 4) {
    const target = selected === 3 ? [132, 57] : [110, 57];
    const at = (i: number, s: number) => {
      const a = (i * Math.PI * 2) / 12;
      const bend = (selected === 3 ? 22 : 8) * Math.sin(Math.PI * s);
      return [
        (110 + Math.cos(a) * 95) * (1 - s) + target[0] * s + Math.sin(a) * bend,
        (57 + Math.sin(a) * 44) * (1 - s) + target[1] * s + Math.cos(a) * bend,
      ];
    };
    return (
      <g>
        {selected === 3 && (
          <path
            d="M12 42Q30 0 99 15T204 43Q214 81 161 100T64 96Q5 85 12 42Z"
            fill="#bda7f508"
            stroke="#bda7f5"
            strokeDasharray="3 4"
            opacity=".6"
          />
        )}
        {Array.from({ length: 12 }, (_, i) => {
          const [x, y] = at(i, (time * 0.1 + i / 12) % 1);
          return (
            <g key={i}>
              <path
                d={curve(Array.from({ length: 40 }, (_, j) => at(i, j / 39)))}
                stroke={tones[i % 3]}
                fill="none"
                opacity=".4"
              />
              <circle cx={x} cy={y} r="1.8" fill={tones[i % 3]} />
            </g>
          );
        })}
        {Array.from({ length: selected === 3 ? 20 : 65 }, (_, i) => (
          <circle
            key={i}
            cx={target[0] + Math.cos(i * 2.4) * Math.sqrt(i + 1) * 2.4}
            cy={target[1] + Math.sin(i * 2.4) * Math.sqrt(i + 1) * 1.8}
            r={i % 4 ? 1 : 2}
            fill={i % 3 ? '#ffbc77' : '#fff3da'}
          />
        ))}
        <text x="110" y="115" textAnchor="middle">
          {selected === 3
            ? 'Flow basin · Laniakea'
            : 'Matter concentration · local flows'}
        </text>
      </g>
    );
  }
  if (selected === 5)
    return (
      <g>
        <path
          d="M28 75Q62 22 111 56T194 31"
          stroke="#bda7f5"
          strokeWidth="15"
          opacity=".12"
          fill="none"
        />
        {[
          [52, 60],
          [110, 51],
          [171, 41],
        ].map(([cx, cy], cluster) => (
          <g key={cluster}>
            <ellipse cx={cx} cy={cy} rx="28" ry="22" fill="#ffbc7708" />
            {Array.from({ length: 42 }, (_, i) => (
              <circle
                key={i}
                cx={cx + Math.cos(i * 2.399) * Math.sqrt(i + 1) * 3.5}
                cy={cy + Math.sin(i * 2.399) * Math.sqrt(i + 1) * 2.6}
                r={i % 7 ? 1 : 2}
                fill={tones[(i + cluster) % 3]}
                opacity=".7"
              />
            ))}
          </g>
        ))}
        <text x="110" y="115" textAnchor="middle">
          Clusters within a supercluster
        </text>
      </g>
    );
  if (selected === 1) {
    const nodes = [
      [18, 32],
      [48, 19],
      [70, 48],
      [112, 20],
      [150, 39],
      [197, 18],
      [205, 79],
      [158, 95],
      [118, 68],
      [68, 100],
      [28, 81],
    ];
    const edges = [
      [0, 1],
      [0, 2],
      [0, 10],
      [1, 3],
      [2, 3],
      [2, 8],
      [2, 9],
      [3, 4],
      [4, 5],
      [4, 6],
      [4, 8],
      [6, 7],
      [7, 8],
      [8, 9],
      [9, 10],
    ];
    return (
      <g>
        {edges.map(([a, b], i) => (
          <g key={i}>
            <path
              d={curve([nodes[a], nodes[b]])}
              stroke={tones[2]}
              opacity=".28"
              strokeWidth="3"
            />
            {Array.from({ length: 8 }, (_, j) => (
              <circle
                key={j}
                cx={nodes[a][0] + ((nodes[b][0] - nodes[a][0]) * j) / 8}
                cy={
                  nodes[a][1] +
                  ((nodes[b][1] - nodes[a][1]) * j) / 8 +
                  2 * Math.sin(i + j)
                }
                r="1"
                fill={tones[1]}
                opacity=".5"
              />
            ))}
          </g>
        ))}
        {nodes.map(([x, y], i) => (
          <g key={i}>
            <circle cx={x} cy={y} r="7" fill="#ffbc7715" />
            <circle cx={x} cy={y} r="2.5" fill={tones[0]} />
          </g>
        ))}
      </g>
    );
  }
  return (
    <g>
      {[0, 1, 2].map((arm) => (
        <g key={arm}>
          <path
            d={curve(
              Array.from({ length: 70 }, (_, i) =>
                point(
                  (arm * Math.PI * 2) / 3 + i * 0.05 + time * 0.12,
                  5 + i,
                  0.45,
                ),
              ),
            )}
            fill="none"
            stroke={tones[2]}
            opacity=".4"
          />
          {Array.from({ length: 35 }, (_, i) => {
            const [x, y] = point(
              (arm * Math.PI * 2) / 3 + i * 0.1 + time * 0.12,
              6 + i * 2,
              0.45,
            );
            return (
              <circle
                key={i}
                cx={x}
                cy={y}
                r={i % 4 ? 1 : 1.7}
                fill={tones[i % 3]}
              />
            );
          })}
        </g>
      ))}
      {[14, 9, 5].map((r) => (
        <ellipse
          key={r}
          cx="110"
          cy="59"
          rx={r}
          ry={r * 0.6}
          fill="#ffbc7740"
        />
      ))}
    </g>
  );
}

function StructureCard({
  item,
  time,
}: {
  item: (typeof catalog)[number];
  time: number;
}) {
  const [choice, setChoice] = useState({ index: 0, at: time });
  const [cycling, setCycling] = useState(true);
  const selected =
    item.kind === 'matter'
      ? matterCycle(choice.index, choice.at, time, cycling)
      : choice.index;
  const id = useId();
  const [label, detail] = item.choices[selected];
  return (
    <li className={`children-example children-example-${item.kind}`}>
      <strong>{item.name}</strong>
      {item.kind === 'atoms' ? (
        <OrbitalStudy
          key={selected}
          atom={label === 'Hydrogen' ? 'hydrogen' : 'carbon'}
          time={time}
          id={`${id}-scene`}
        />
      ) : (
        <svg
          className="children-scene children-interactive-scene"
          viewBox="0 0 220 120"
          role="img"
          aria-label={`${label}: ${detail}`}
          id={`${id}-scene`}
        >
          {item.kind === 'hadrons' && (
            <Hadron selected={selected} time={time} />
          )}
          {item.kind === 'nuclei' && (
            <Nucleus count={selected ? 12 : 4} time={0} />
          )}
          {item.kind === 'molecules' && (
            <Molecule selected={selected} time={time} />
          )}
          {item.kind === 'matter' && <Matter selected={selected} time={time} />}
          {item.kind === 'cosmos' && <Cosmos selected={selected} time={time} />}
        </svg>
      )}
      <p>{item.caption}</p>
      <div
        className="children-choices"
        role="group"
        aria-label={`${item.name} examples`}
      >
        {item.choices.map(([name], i) => (
          <button
            type="button"
            key={name}
            aria-pressed={selected === i}
            aria-controls={`${id}-scene ${id}-detail`}
            onClick={() => {
              setChoice({ index: i, at: time });
              if (item.kind === 'matter') setCycling(false);
            }}
          >
            {name}
          </button>
        ))}
      </div>
      {item.kind === 'matter' && (
        <div className="matter-cycle-control">
          <button
            type="button"
            aria-pressed={cycling}
            onClick={() => {
              setChoice({ index: selected, at: time });
              setCycling(!cycling);
            }}
          >
            {cycling ? 'Pause state cycle' : 'Cycle states'}
          </button>
          <small>
            {cycling
              ? 'Solid → liquid → gas → plasma · 6 s each'
              : 'Selected state held for inspection'}
          </small>
          <div className="matter-cycle-progress" aria-hidden="true">
            <span
              style={{
                transform: `scaleX(${cycling ? (Math.max(0, time - choice.at) % 6) / 6 : 0})`,
              }}
            />
          </div>
        </div>
      )}
      <p
        className="children-selection"
        id={`${id}-detail`}
        aria-live={item.kind === 'matter' && cycling ? 'off' : 'polite'}
        aria-atomic="true"
      >
        {detail}
      </p>
      <small>{item.note}</small>
      {item.kind === 'cosmos' && selected >= 2 && (
        <a
          className="children-source"
          target="_blank"
          rel="noreferrer"
          href={
            [
              'https://www.esa.int/ESA_Multimedia/Images/2023/05/What_Euclid_will_measure_baryonic_acoustic_oscillations',
              'https://www.nature.com/articles/nature13674',
              'https://www.eso.org/sci/publications/messenger/archive/no.84-jun96/messenger-no84-17-18.pdf',
              'https://www.esa.int/ESA_Multimedia/Images/2013/10/Shapley_Supercluster',
            ][selected - 2]
          }
        >
          Explore {label} ↗
        </a>
      )}
      {item.source && (
        <a
          className="children-source"
          href={item.source[1]}
          target="_blank"
          rel="noreferrer"
        >
          {item.source[0]} ↗
        </a>
      )}
    </li>
  );
}

export function StructureShowcase({ time }: { time: number }) {
  return (
    <ol>
      {catalog.map((item) => (
        <StructureCard key={item.kind} item={item} time={time} />
      ))}
    </ol>
  );
}
