'use client';
import { useState } from 'react';
import { useSceneClock } from './science-console';
import { SCIENCE } from './exhibits';

const steps = [
  [
    'Parent + child',
    'Qξ[ΦP+C]',
    'Evaluate the conserved energy of the complete configuration, including the child.',
  ],
  [
    'Matched parent',
    '− Qξ[ΦP matched]',
    'Subtract the parent in the same boundary conditions and energy convention.',
  ],
  [
    'Relative energy',
    'ΔHξ = Erel',
    'The difference isolates the energy associated with the child.',
  ],
  [
    'Rest mass',
    'm = Erel / c²',
    'In a stable rest frame, identify this relative energy with mass; check agreement with the physical pole or stable-cycle readout.',
  ],
];

export function MassStudy({ motion }: { motion: boolean }) {
  const { ref, time } = useSceneClock(motion);
  const [selected, setSelected] = useState<number | null>(null);
  const active = selected ?? Math.floor(time / 4) % steps.length;
  return (
    <section
      className="mass-study evidence-feature"
      ref={ref}
      aria-label="BHSM mass: the relative-energy definition"
    >
      <p className="eyebrow">BHSM mass contract · v14.54, recovered in AE3</p>
      <h4>Mass is the energy difference a child brings.</h4>
      <p>
        BHSM defines a particle’s mass through the energy of the whole
        parent-and-child configuration minus a matched parent. Divide that
        relative rest energy by c². A harmonic label organizes a candidate; its
        raw geometric eigenvalue is not automatically a particle’s mass.
      </p>
      <div className="mass-steps" aria-label="Follow the mass calculation">
        {steps.map(([name, formula], i) => (
          <button
            key={name}
            onClick={() => setSelected(i)}
            aria-pressed={active === i}
          >
            <small>
              0{i + 1} · {name}
            </small>
            <strong>{formula}</strong>
          </button>
        ))}
      </div>
      <p className="mass-step-copy">{steps[active][2]}</p>
      <button
        className="evidence-play"
        onClick={() => setSelected(selected === null ? active : null)}
      >
        {selected === null ? 'Pause explanation' : 'Follow the calculation'}
      </button>
      <p className="console-caption">
        The animation follows the documented equation; it does not assign
        invented energies or evolve a particle. Numerical masses require each
        normalized configuration, matched parent and physical energy readout.
        Those existing obligations remain open.
      </p>
      <a href={`${SCIENCE}/theory/ae3_family_mass_ontology_recovery_audit.md`}>
        Mass definition, recovered calculation and exact remaining bridge ↗
      </a>
    </section>
  );
}
