import test from 'node:test';
import assert from 'node:assert/strict';
import { collisionDemo } from '../lib/collision-demo.ts';
import { demos } from '../lib/collision-scenarios.ts';
import { buildTransitionRecord } from '../lib/bhsm-transition.ts';

function record(scenario) {
  return buildTransitionRecord(
    {
      kind: 'demo',
      scenario,
      kinematics: collisionDemo(
        scenario.energy,
        scenario.masses,
        scenario.angle,
        scenario.charges,
      ),
    },
    demos,
  );
}
test('demo transition screens only charge and threshold and keeps BHSM quantities unresolved', () => {
  const r = record(demos[0]);
  assert.equal(r.incoming.cm_energy_GeV, 10);
  assert.deepEqual(
    r.branches.map((b) => b.screen),
    ['kinematic-pass', 'kinematic-pass', 'charge-blocked'],
  );
  assert.equal(r.branches.filter((b) => b.displayed).length, 1);
  assert.ok(r.observables.conservation_residual_GeV < 1e-12);
  assert.equal(r.observables.particles[0].four_vector.E, 5);
  assert.equal(r.boundary.imbalance, null);
  assert.equal(r.boundary.amplitude, null);
  assert.equal(r.incoming.envelope_fields, null);
  assert.ok(
    r.branches.every(
      (b) => b.probability === null && b.bhsm_admissibility === null,
    ),
  );
  assert.equal(r.observables.bhsm_predictions, null);
  assert.equal(r.physical_prediction, false);
  assert.equal(
    JSON.stringify(r),
    JSON.stringify(record(demos[0])),
    'same scientific inputs produce byte-identical records',
  );
});
test('threshold and charge blocks survive without invented outgoing observables', () => {
  const r = record({ ...demos[0], energy: 0.1 });
  assert.equal(r.branches[0].screen, 'threshold-closed');
  assert.equal(r.branches[1].screen, 'kinematic-pass');
  assert.equal(r.observables.invariant_mass_GeV, null);
  assert.equal(r.observables.conservation_residual_GeV, null);
  assert.deepEqual(r.observables.particles, []);
  assert.deepEqual(
    record(demos[2]).branches.map((b) => b.screen),
    ['charge-blocked', 'charge-blocked', 'kinematic-pass'],
  );
});
test('CMS muons never supply an invented incoming state, full-event balance or predicted branch', () => {
  const tracks = [
    { label: 'μ⁻', charge: -1, E: 5, px: 3, py: 0, pz: 3.9986 },
    { label: 'μ⁺', charge: 1, E: 5, px: -3, py: 0, pz: -3.9986 },
  ];
  const r = buildTransitionRecord(
    { kind: 'cms', tracks, run: 12, event: 34, subsystemMass: 10 },
    demos,
  );
  assert.equal(r.classification, 'RECONSTRUCTED_CMS_SUBSYSTEM');
  assert.equal(r.incoming.cm_energy_GeV, null);
  assert.equal(r.incoming.total_charge_e, null);
  assert.equal(r.incoming.four_vectors, null);
  assert.equal(r.observables.conservation_residual_GeV, null);
  assert.equal(r.observables.selected_angle_degrees, null);
  assert.equal(r.observables.mass_scope, 'reconstructed dimuon subsystem only');
  assert.equal(r.observables.particles[0].pt_GeV, 3);
  assert.ok(
    r.branches.every(
      (b) =>
        b.screen === 'not-evaluated' &&
        b.charge_pass === null &&
        b.threshold_pass === null &&
        !b.displayed,
    ),
  );
  assert.equal(r.physical_prediction, false);
});
