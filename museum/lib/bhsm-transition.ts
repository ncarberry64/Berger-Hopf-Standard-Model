import type { collisionDemo, FourVector } from './collision-demo';
import type { demos } from './collision-scenarios';

type Scenario = (typeof demos)[number];
type Track = FourVector & { label: string; charge: number };
type Input =
  | {
      kind: 'demo';
      scenario: Scenario;
      kinematics: ReturnType<typeof collisionDemo>;
    }
  | {
      kind: 'cms';
      tracks: Track[];
      run: number | null;
      event: number | null;
      subsystemMass: number;
    };

// An auditable transition record. Missing BHSM dynamics remain null, not zero.
// Branch checks are necessary kinematic screens, never a complete admissibility proof.
export function buildTransitionRecord(input: Input, candidates: Scenario[]) {
  const demo = input.kind === 'demo' ? input : null;
  const energy = demo?.scenario.energy ?? null;
  const incomingCharge = demo
    ? demo.scenario.charges[0] + demo.scenario.charges[1]
    : null;
  const tracks: Track[] = demo
    ? demo.kinematics.outgoing.map((v, i) => ({
        ...v,
        label: demo.scenario.labels[i],
        charge: demo.scenario.charges[i + 2],
      }))
    : input.kind === 'cms'
      ? input.tracks
      : [];
  const branches = candidates.map((candidate) => {
    const threshold = candidate.masses[2] + candidate.masses[3];
    const finalCharge = candidate.charges[2] + candidate.charges[3];
    const chargePass =
      incomingCharge === null
        ? null
        : Math.abs(incomingCharge - finalCharge) < 1e-9;
    // Strictly above threshold follows collisionDemo's nonzero phase-space convention.
    const thresholdPass = energy === null ? null : energy > threshold;
    return {
      id: candidate.id,
      label: candidate.labels.join(' + '),
      threshold_GeV: threshold,
      final_charge_e: finalCharge,
      charge_pass: chargePass,
      threshold_pass: thresholdPass,
      screen:
        chargePass === null
          ? 'not-evaluated'
          : !chargePass
            ? 'charge-blocked'
            : !thresholdPass
              ? 'threshold-closed'
              : 'kinematic-pass',
      displayed: demo?.scenario.id === candidate.id,
      bhsm_admissibility: null,
      probability: null,
    };
  });
  return {
    schema: 'bhsm-museum-transition/v1',
    classification: demo
      ? 'CONDITIONAL_TWO_BODY_KINEMATICS'
      : 'RECONSTRUCTED_CMS_SUBSYSTEM',
    physical_prediction: false,
    event: demo
      ? { id: demo.scenario.id, title: demo.scenario.title }
      : {
          id: `cms-${input.kind === 'cms' ? input.run : null}-${input.kind === 'cms' ? input.event : null}`,
          title: 'Recorded CMS dimuon subsystem',
        },
    units: {
      energy: 'GeV',
      momentum: 'GeV (c = 1)',
      charge: 'elementary charge',
    },
    incoming: {
      labels: demo
        ? demo.scenario.incomingLabels
        : ['proton beams (context only)'],
      four_vectors: demo ? demo.kinematics.incoming : null,
      rest_masses_GeV: demo ? demo.scenario.masses.slice(0, 2) : null,
      cm_energy_GeV: energy,
      total_charge_e: incomingCharge,
      envelope_fields: null,
      environment_fields: null,
      classification: demo
        ? 'CHOSEN_DEMONSTRATION_INPUTS'
        : 'INITIAL_SUBPROCESS_NOT_RECONSTRUCTED',
    },
    boundary: {
      classification: 'UNEVALUATED_BHSM_BOUNDARY',
      imbalance: null,
      action_owned_transition_map: null,
      amplitude: null,
      note: 'Encounter animation is schematic. No event-specific BHSM boundary field, imbalance or transition amplitude is evaluated.',
    },
    branches,
    branch_scope:
      'Three displayed candidate channels, not exhaustive. Charge and threshold checks do not establish BHSM dynamics or full quantum-number admissibility. CMS subsystem data cannot select the complete collision branch.',
    observables: {
      classification: demo
        ? 'CALCULATED_FOR_CHOSEN_CHANNEL'
        : 'DERIVED_FROM_RECONSTRUCTED_SUBSYSTEM',
      selected_angle_degrees: demo ? demo.scenario.angle : null,
      invariant_mass_GeV: demo
        ? demo.kinematics.outgoing.length
          ? demo.scenario.energy
          : null
        : input.kind === 'cms'
          ? input.subsystemMass
          : null,
      mass_scope: demo
        ? 'complete selected two-body final state'
        : 'reconstructed dimuon subsystem only',
      conservation_residual_GeV: demo ? demo.kinematics.residual : null,
      particles: tracks.map((v) => ({
        label: v.label,
        charge_e: v.charge,
        four_vector: { E: v.E, px: v.px, py: v.py, pz: v.pz },
        pt_GeV: Math.hypot(v.px, v.py),
      })),
      cross_section: null,
      branching_fraction: null,
      bhsm_predictions: null,
    },
    sources: {
      theory_revision: '92763ef226a65d8b7ddea4c9c7e8054cc1a611c5',
      kinematics: 'museum/lib/collision-demo.ts',
      reference_masses:
        'https://physics.nist.gov/cuu/Constants/Table/allascii.txt',
      cms: demo ? null : 'https://opendata.cern.ch/record/303',
      envelopment:
        'docs/bhsm_machian_geometric_envelopment_foundation_v10_0.md',
      boundary:
        'theory/bhsm_boundary_improved_event_mode_envelopment_charge_map_adjudication.md',
      transition: 'docs/bhsm_quantum_core_transition_v11_0.md',
    },
  };
}
export type TransitionRecord = ReturnType<typeof buildTransitionRecord>;
