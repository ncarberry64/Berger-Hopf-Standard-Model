'use client';
/* oxlint-disable next/no-html-link-for-pages -- This link opens a static Markdown source note. */
import { useState } from 'react';
import { useSceneClock } from './science-console';
import { SCIENCE } from './exhibits';
import { MassVisual } from './mass-visual';

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
      <p className="eyebrow">BHSM mass · the physical picture</p>
      <h4>Holding back the surrounding field.</h4>
      <MassVisual motion={motion} />
      <p>
        BHSM proposes that a localized configuration displaces the surrounding
        energy–geometry response. Here three quarks, connected by color threads,
        move within an electron cloud as a region clears in the surrounding
        virtual-particle sea. In this picture, mass expresses the energy
        involved in maintaining that displacement: how much of the surrounding
        response is held back.
      </p>
      <p className="console-caption">
        Author’s conceptual illustration, using a proton’s uud content and an
        enlarged electron probability cloud. Threads depict color interaction;
        the cloud’s rotating view is not an electron orbit. The sea represents
        vacuum response, not a measured gas of virtual particles. Sizes, motion
        and the cleared area are explanatory, not a QCD solution or a mass
        scale.
      </p>
      <h4>From that picture to the mass calculation.</h4>
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
        The equation tour follows the documented mass contract, m = Erel / c². A
        cleared area or a count of dots alone is not that energy. Numerical
        masses require each normalized configuration, matched parent and
        physical energy readout. Those existing obligations remain open.
      </p>
      <a href={`${SCIENCE}/theory/ae3_family_mass_ontology_recovery_audit.md`}>
        Mass definition, recovered calculation and exact remaining bridge ↗
      </a>
      {' · '}
      <a href="./research/mass-and-hypersphere-context.md">
        Curvature papers and displaced-energy context ↗
      </a>
    </section>
  );
}
