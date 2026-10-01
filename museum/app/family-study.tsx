'use client';
import { useState } from 'react';
import { GeometryField, useSceneClock } from './science-console';
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
    copy: 'Tau, top and bottom complete the three-family pattern that BHSM seeks to explain.',
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
  return (
    <div className="family-study" ref={ref}>
      <div className="matter-scene">
        <GeometryField motion={motion && playing} family={active} />
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
          The tour changes family every four seconds and restores the original
          linked Hopf-fiber views on both desktop and phone. These three views
          vary the mathematical projection for illustration; they are not
          computed family eigenfunctions or particle orbits. The reference
          particle labels and frozen charged-lepton mode ledger are distinct
          from the drawing. The current lepton slot is (k, j) = ({family.k},
          {family.j}).{' '}
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
