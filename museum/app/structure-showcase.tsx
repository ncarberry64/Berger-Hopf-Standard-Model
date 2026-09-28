'use client';
/* oxlint-disable jsx-a11y/prefer-tag-over-role -- Named inline SVG illustrations. */
import { useId, useState } from 'react';
import { curve } from '../lib/children-geometry';

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
    note: 'A constituent-count illustration; positions and motion are schematic.',
  },
  {
    name: 'Atoms',
    kind: 'atoms',
    caption: 'Electron wavefunctions extend around the nucleus.',
    choices: [
      [
        'Hydrogen',
        'Hydrogen-1 · 1 proton · 1 electron · 1s¹. A spherical s-state probability envelope.',
      ],
      [
        'Helium',
        'Helium-4 · 2 protons + 2 neutrons · 2 electrons · 1s². Paired electrons occupy the 1s orbital.',
      ],
      [
        'Carbon',
        'Carbon-12 · 6 protons + 6 neutrons · 6 electrons · 1s² 2s² 2p². Inner s states and directional p lobes.',
      ],
    ],
    note: 'Shading suggests probability density; waveform packets illustrate phase. Ground-state density is stationary. These are orbital sketches, not electron trajectories or a computed atomic solution.',
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
        'Two hydrogen atoms bond to oxygen in a bent geometry. Shown with a schematic bending vibration.',
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
    note: 'Particle arrangements are simplified; ice’s crystal lattice and molecular detail are not resolved.',
  },
  {
    name: 'Astronomical structures',
    kind: 'cosmos',
    caption: 'Explore the forms of matter on larger scales.',
    choices: [
      [
        'Earth',
        'A rotating rocky planet, with an ocean, continents and atmosphere.',
      ],
      [
        'Sun',
        'A star: a luminous plasma sphere with schematic surface activity and coronal loops.',
      ],
      [
        'Milky Way',
        'A schematic spiral galaxy with a central bulge and star-filled arms.',
      ],
      [
        'Cosmic web',
        'A network of filaments and dense galaxy clusters surrounding broad voids.',
      ],
    ],
    note: 'These scenes illustrate structure, not measured maps, orbits or evolution rates.',
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

function Packet({
  x,
  y,
  rx,
  ry,
  time,
  tone,
  angle = 0,
  gradient,
}: {
  x: number;
  y: number;
  rx: number;
  ry: number;
  time: number;
  tone: string;
  angle?: number;
  gradient: string;
}) {
  return (
    <g transform={`translate(${x} ${y}) rotate(${angle})`}>
      <ellipse rx={rx} ry={ry} fill={`url(#${gradient})`} />
      {[-0.45, 0, 0.45].map((offset, i) => (
        <path
          key={i}
          d={curve(
            Array.from({ length: 65 }, (_, k) => {
              const u = (k / 64) * 2 - 1;
              const envelope = Math.exp(-4 * u * u) * (1 - u * u);
              return [
                u * rx,
                offset * ry +
                  Math.sin(u * Math.PI * 3 - time * 1.6 + i) *
                    ry *
                    0.23 *
                    envelope,
              ];
            }),
          )}
          stroke={tone}
          fill="none"
          strokeWidth=".9"
          opacity={0.45 + 0.15 * Math.cos(time + i)}
        />
      ))}
    </g>
  );
}

function Atom({
  selected,
  time,
  id,
}: {
  selected: number;
  time: number;
  id: string;
}) {
  return (
    <g>
      <defs>
        {tones.slice(1).map((tone, i) => (
          <radialGradient id={`${id}-orbital-${i}`} key={tone}>
            <stop stopColor={tone} stopOpacity=".42" />
            <stop offset=".65" stopColor={tone} stopOpacity=".16" />
            <stop offset="1" stopColor={tone} stopOpacity="0" />
          </radialGradient>
        ))}
      </defs>
      {selected < 2 ? (
        <Packet
          x={110}
          y={59}
          rx={selected ? 43 : 50}
          ry={selected ? 43 : 50}
          time={time}
          tone={tones[1]}
          gradient={`${id}-orbital-0`}
        />
      ) : (
        <g>
          {[0, 90].map((angle) => (
            <g key={angle} transform={`rotate(${angle} 110 59)`}>
              {[-1, 1].map((side) => (
                <Packet
                  key={side}
                  x={110 + side * 32}
                  y={59}
                  rx={27}
                  ry={15}
                  time={time + (side < 0 ? Math.PI : 0)}
                  tone={tones[side < 0 ? 1 : 2]}
                  gradient={`${id}-orbital-${side < 0 ? 0 : 1}`}
                />
              ))}
            </g>
          ))}
          <Packet
            x={110}
            y={59}
            rx={22}
            ry={22}
            time={time}
            tone={tones[1]}
            gradient={`${id}-orbital-0`}
          />
          <circle
            cx="110"
            cy="59"
            r="15"
            fill="none"
            stroke="#0a101c"
            strokeWidth="2"
            opacity=".65"
          />
        </g>
      )}
      <Nucleus small count={[1, 4, 12][selected]} time={0} />
      <text x="8" y="14">
        {['1s¹', '1s²', '1s² 2s² 2p²'][selected]}
      </text>
      <text x="110" y="113" textAnchor="middle">
        wave phase · probability envelope
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
            (co2 ? 56 + 4 * Math.sin(time * 2) : 35 + 2 * Math.sin(time * 2));
        const y = co2 ? 59 : 76 + 3 * Math.sin(time * 2);
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

function Cosmos({
  selected,
  time,
  id,
}: {
  selected: number;
  time: number;
  id: string;
}) {
  if (selected === 0)
    return (
      <g>
        <defs>
          <clipPath id={`${id}-planet`}>
            <circle cx="110" cy="59" r="40" />
          </clipPath>
        </defs>
        <circle cx="110" cy="59" r="44" fill="#71e5eb10" stroke="#71e5eb40" />
        <circle cx="110" cy="59" r="40" fill="#163e61" />
        <g clipPath={`url(#${id}-planet)`}>
          {[0, 1, 2].map((i) => (
            <g
              key={i}
              transform={`translate(${((time * 7) % 125) + i * 125 - 170} 0)`}
            >
              <path
                d="M71 28L86 19L102 27L97 41L110 49L99 63L85 56L81 41ZM103 68L121 62L130 73L119 95L110 99Z"
                fill="#72bda2"
              />
            </g>
          ))}
          {[-20, 0, 20].map((y) => (
            <ellipse
              key={y}
              cx="110"
              cy={59 + y}
              rx={Math.sqrt(1600 - y * y)}
              ry="6"
              fill="none"
              stroke="#71e5eb30"
            />
          ))}
        </g>
      </g>
    );
  if (selected === 1)
    return (
      <g>
        {[48, 43, 37].map((r, i) => (
          <circle
            key={r}
            cx="110"
            cy="59"
            r={r}
            fill={i === 2 ? '#d98940' : '#ffbc7710'}
          />
        ))}
        {Array.from({ length: 14 }, (_, i) => {
          const a = (i * Math.PI * 2) / 14 + time * 0.08;
          const [x, y] = point(a, 36);
          return (
            <ellipse
              key={i}
              cx={x}
              cy={y}
              rx={7 + 2 * Math.sin(time + i)}
              ry="3"
              fill="none"
              stroke="#ffe2b7"
              transform={`rotate(${(a * 180) / Math.PI} ${x} ${y})`}
              opacity=".7"
            />
          );
        })}
        <circle cx="101" cy="48" r="22" fill="#ffc46a40" />
      </g>
    );
  if (selected === 3) {
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
                opacity={0.35 + 0.15 * Math.sin(time + j)}
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
  const [selected, setSelected] = useState(item.kind === 'cosmos' ? 2 : 0);
  const id = useId();
  const [label, detail] = item.choices[selected];
  return (
    <li className={`children-example children-example-${item.kind}`}>
      <strong>{item.name}</strong>
      <svg
        className="children-scene children-interactive-scene"
        viewBox="0 0 220 120"
        role="img"
        aria-label={`${label}: ${detail}`}
        id={`${id}-scene`}
      >
        {item.kind === 'hadrons' && <Hadron selected={selected} time={time} />}
        {item.kind === 'nuclei' && (
          <Nucleus count={selected ? 12 : 4} time={time} />
        )}
        {item.kind === 'atoms' && (
          <Atom selected={selected} time={time} id={id} />
        )}
        {item.kind === 'molecules' && (
          <Molecule selected={selected} time={time} />
        )}
        {item.kind === 'matter' && <Matter selected={selected} time={time} />}
        {item.kind === 'cosmos' && (
          <Cosmos selected={selected} time={time} id={id} />
        )}
      </svg>
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
            onClick={() => setSelected(i)}
          >
            {name}
          </button>
        ))}
      </div>
      <p
        className="children-selection"
        id={`${id}-detail`}
        aria-live="polite"
        aria-atomic="true"
      >
        {detail}
      </p>
      <small>{item.note}</small>
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
