'use client';
/* oxlint-disable jsx-a11y/prefer-tag-over-role -- SVG describes a mathematical phase diagram. */
import { useState } from 'react';
import { useSceneClock } from './science-console';
import { hopfPoint, projectFiber } from '../lib/berger-hopf';
import { SCIENCE } from './exhibits';

// Frozen charged-lepton ledger, not the three core/wall/depth modes.
const families = [
  {
    name: 'First family',
    particles: ['e⁻', 'νe', 'u', 'd'],
    k: 9,
    j: 3,
    copy: 'The electron and up and down quarks build ordinary atoms.',
  },
  {
    name: 'Second family',
    particles: ['μ⁻', 'νμ', 'c', 's'],
    k: 5,
    j: 2,
    copy: 'Muon, charm and strange repeat the charge pattern with heavier charged particles.',
  },
  {
    name: 'Third family',
    particles: ['τ⁻', 'ντ', 't', 'b'],
    k: 0,
    j: 0,
    copy: 'Tau, top and bottom complete the three-family pattern. The historical heavy lepton slot is the uniform mode.',
  },
];
const labels = [
  'Charged lepton',
  'Neutrino',
  'Up-type quark',
  'Down-type quark',
];

export function FamilyStudy({ motion }: { motion: boolean }) {
  const [tour, setTour] = useState(true);
  const [playing, setPlaying] = useState(true);
  const [selected, setSelected] = useState(0);
  const [start, setStart] = useState(0);
  const { ref, time } = useSceneClock(motion && playing);
  const active = tour
    ? (selected + Math.floor((time - start) / 4)) % 3
    : selected;
  const family = families[active];
  const q = family.k - 2 * family.j;
  const project = (theta: number) => {
    const [x, y] = projectFiber(hopfPoint(0.58, 0.8, theta), time * 0.22 + 0.5);
    return [260 + (x - 260) * 1.2, 172 + (y - 228) * 0.85];
  };
  const line = Array.from({ length: 129 }, (_, i) => {
    const [x, y] = project((i * Math.PI) / 64);
    return `${i ? 'L' : 'M'}${x.toFixed(2)},${y.toFixed(2)}`;
  }).join(' ');
  return (
    <div className="family-study" ref={ref}>
      <div className="matter-scene">
        <svg
          viewBox="0 0 520 350"
          role="img"
          aria-label={`${family.name}: Hopf phase winding q=${q} from historical charged-lepton mode (${family.k},${family.j}); rotating mathematical view`}
        >
          <text x="24" y="30" fill="#bda7f5" fontSize="15">
            {family.name.toUpperCase()} · HOPF PHASE
          </text>
          <path d={line} fill="none" stroke="#555066" strokeWidth="2" />
          {Array.from({ length: 72 }, (_, i) => {
            const theta = (i * Math.PI) / 36;
            const [x, y] = project(theta);
            return (
              <circle
                key={i}
                cx={x}
                cy={y}
                r="4.5"
                fill={`hsl(${42 + (240 * (1 - Math.cos(q * theta))) / 2} 85% 70%)`}
              />
            );
          })}
          <text
            x="260"
            y="312"
            textAnchor="middle"
            fill="#ffcf99"
            fontSize="19"
          >
            (k, j) = ({family.k}, {family.j}) · q = {q}
          </text>
          <text
            x="260"
            y="340"
            textAnchor="middle"
            fill="#d9cfe3"
            fontSize="14"
          >
            {q === 0
              ? 'Uniform phase · the zero-mode slot'
              : `${q} phase windings around one fiber`}
          </text>
        </svg>
        <div className="matter-family">
          <p className="eyebrow">{family.name} · reference particle content</p>
          <div className="particle-quartet">
            {family.particles.map((symbol, i) => (
              <div key={labels[i]}>
                <strong>{symbol}</strong>
                <span>{labels[i]}</span>
              </div>
            ))}
          </div>
          <p>{family.copy}</p>
        </div>
      </div>
      <div className="console-selector" aria-label="Particle family">
        {families.map((f, i) => (
          <button
            key={f.name}
            aria-pressed={active === i}
            onClick={() => {
              setSelected(i);
              setTour(false);
            }}
          >
            {f.name}
          </button>
        ))}
        <button
          onClick={() => {
            setSelected(active);
            setStart(time);
            setTour(!tour);
          }}
        >
          {tour ? 'Pause family cycle' : 'Cycle all families'}
        </button>
        <button onClick={() => setPlaying(!playing)}>
          {playing ? 'Pause family motion' : 'Animate family view'}
        </button>
      </div>
      <details className="console-details family-context">
        <summary>What the family animation shows · modes and sources</summary>
        <p className="console-caption">
          The tour changes family every four seconds. Color shows Re(eⁱqθ) on a
          Hopf fiber, with q = k − 2j from the frozen charged-lepton ledger. The
          camera rotates; these are phase patterns, not particle orbits or the
          full eigenfunctions. Hopf charge is not electric charge. The quark and
          neutrino labels identify reference family members; this lepton diagram
          does not assign them modes.{' '}
          <a
            href={`${SCIENCE}/theory/ae3_family_mass_ontology_recovery_audit.md`}
          >
            Mode and mass context ↗
          </a>
        </p>
      </details>
    </div>
  );
}
