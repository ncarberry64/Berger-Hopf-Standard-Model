"""Evaluate the retained 57-row producer at the forward-swapped E1/C2 pair.

No state, trajectory, root, normalization, or boundary law is solved here.
The stored refined proof center is reused bit for bit.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

import numpy as np
import scipy


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'src'))

from bhsm.interface.aether_full_reset_action_jacobian import (
    full_reset_residual,
    _attachment_coordinates_at_order,
    _attachment_jacobian_at_order,
    _symmetric_power,
    _trace_jacobian_at_order,
)
from bhsm.interface.aether_high_precision_velocity_jet import (
    high_precision_canonical_momentum_from_blocks,
    high_precision_ordered_eigenpair_from_blocks,
    high_precision_velocity_jet_blocks,
)


STATE_SOURCE = 'artifacts/flagship_integration/BHSM_N12_C2_REFINED_RESET_ROOT_CENTER.npz'
NORMALIZATION_SOURCE = 'artifacts/flagship_integration/BHSM_N12_FULL_RESET_ACTION_JACOBIAN.npz'
SCALE_SOURCE = 'artifacts/n12_direct_checkpoint/BHSM_N12_EXACT_ROOT_RESIDUAL.json'
ROOT_CERTIFICATE = 'artifacts/flagship_integration/BHSM_N12_C2_REFINED_RESET_ROOT_CENTER.json'
ORIENTATION_SOURCE = 'artifacts/flagship_integration/BHSM_N12_FINITE_TERMINAL_TWO_SIDED_FORWARD_INTERFACE.json'
INCOMING_ORIENTATION_SOURCE = 'artifacts/flagship_integration/BHSM_N12_FINITE_TERMINAL_ORIENTATION_CERTIFICATE.json'


def _identity(path, repository=ROOT):
    file = Path(repository) / path
    return dict(path=path, sha256=sha256(file.read_bytes()).hexdigest())


def _values(array):
    array = np.asarray(array, dtype=float)
    return dict(values=array.tolist(), binary64_hex=[float(x).hex() for x in array.flat],
                shape=list(array.shape), dtype='float64')


def _group(rows, start, stop):
    values = np.asarray(rows[start:stop], dtype=float)
    return dict(row_indices_zero_based=list(range(start, stop)), values=values.tolist(),
                l2_norm=float(np.linalg.norm(values)), max_abs=float(np.max(np.abs(values))))


def evaluate_reset_values(repository: Path | str = ROOT):
    """Return actual retained reset values; execute no trajectory or root solve."""
    repository = Path(repository)
    with np.load(repository / STATE_SOURCE, allow_pickle=False) as data:
        original = np.array(data['state'], copy=True)
        weights = np.array(data['state_weights'], copy=True)
        reference = np.array(data['branch_reference'], copy=True)
    with np.load(repository / NORMALIZATION_SOURCE, allow_pickle=False) as data:
        normalization = np.array(data['normalization_coordinates'], copy=True)
        if not np.array_equal(weights, data['state_weights']):
            raise ValueError('retained state weights differ between input owners')
    scale_record = json.loads((repository / SCALE_SOURCE).read_text())
    certificate = json.loads((repository / ROOT_CERTIFICATE).read_text())
    orientation = json.loads((repository / ORIENTATION_SOURCE).read_text())
    incoming_certificate = json.loads((repository / INCOMING_ORIENTATION_SOURCE).read_text())
    if not (certificate['validation_passed'] and orientation['validation_passed']
            and incoming_certificate['validation_passed']):
        raise ValueError('retained certificates must be validated')
    expected_state_sha256 = certificate['proof_coordinate_Newton_step']['data_SHA256'].lower()
    actual_state_sha256 = _identity(STATE_SOURCE, repository)['sha256']
    if actual_state_sha256 != expected_state_sha256:
        raise ValueError('retained state NPZ no longer matches its original root certificate')
    incoming = original[98:196].copy()
    outgoing = original[0:98].copy()
    forward_pair = np.concatenate((incoming, outgoing))
    scale = float(scale_record['ordered_scale'])
    common = dict(order=12, joint_state=forward_pair, state_weights=weights,
                  branch_reference=reference, ordered_scale=scale,
                  normalization_coordinates=normalization, points=96)
    rows, selected = full_reset_residual(**common, high_precision_action=True)
    if selected != 23:
        raise ValueError('forward-swapped incoming reference did not select branch23: ' + str(selected))
    # The 4-vector produced at rows26:30 is whitened and can mix the three
    # geometric trace coordinates with the attachment coordinate. Keep the
    # original raw trace split as well as the unchanged producer output.
    trace = _trace_jacobian_at_order(12)
    raw_trace = trace @ (outgoing[:37] - incoming[:37])
    raw_attachment = (_attachment_coordinates_at_order(12, outgoing[:37])[1]
                      - _attachment_coordinates_at_order(12, incoming[:37])[1])
    attachment = _attachment_jacobian_at_order(12, normalization)
    boundary = np.vstack((trace, attachment[1]))
    whitening = _symmetric_power(boundary @ np.diag(1 / weights[:37]**2) @ boundary.T, -.5)
    raw_boundary = np.concatenate((raw_trace, [raw_attachment]))
    whitened_crosscheck = whitening @ raw_boundary
    if not np.array_equal(whitened_crosscheck, rows[26:30]):
        raise ValueError('retained trace output does not match producer whitening')
    momenta = []
    ordered_lines = []
    for state in (incoming, outgoing):
        blocks = high_precision_velocity_jet_blocks(
            12, state[:37], state[37:74], state[74:], points=96, precision=60)
        momenta.append(high_precision_canonical_momentum_from_blocks(
            12, state[:37], blocks, precision=60))
        line = high_precision_ordered_eigenpair_from_blocks(blocks, reference, precision=60)
        ordered_lines.append(dict(index=int(line['index']),
                                  eigenvalue=str(line['eigenvalue']),
                                  spectral_gap=str(line['spectral_gap'])))
    if [line['index'] for line in ordered_lines] != [23, 24]:
        raise ValueError('retained reference did not select incoming23/outgoing24')
    raw_momentum_difference = momenta[1] - momenta[0]
    momentum_normalization = _symmetric_power(attachment @ attachment.T, .5)
    if not np.array_equal(momentum_normalization @ raw_momentum_difference, rows[55:57]):
        raise ValueError('retained canonical output does not match producer normalization')
    # An independent arithmetic path on exactly the same retained states is
    # a precision crosscheck, not a residual tolerance or continuum enclosure.
    float_rows, float_selected = full_reset_residual(**common, high_precision_action=False)
    groups = {
        'event_multiplier_constraints': _group(rows, 0, 24),
        'event_canonical_energy_constraint': _group(rows, 24, 25),
        'selected_event_row': _group(rows, 25, 26),
        'normalized_trace_attachment_4': _group(rows, 26, 30),
        'child_multiplier_constraints': _group(rows, 30, 54),
        'child_canonical_energy_constraint': _group(rows, 54, 55),
        'canonical_momentum_child_minus_event_2': _group(rows, 55, 57),
    }
    inputs = [STATE_SOURCE, NORMALIZATION_SOURCE, SCALE_SOURCE, ROOT_CERTIFICATE,
              ORIENTATION_SOURCE, INCOMING_ORIENTATION_SOURCE]
    producer_paths = [
        'src/bhsm/interface/aether_full_reset_action_jacobian.py',
        'src/bhsm/interface/aether_high_precision_velocity_jet.py',
        'src/bhsm/interface/aether_cross_resolution_reconnaissance_v21_35.py',
        'src/bhsm/interface/aether_constraint_consistent_sobolev_lift_v15_84.py',
        'src/bhsm/interface/aether_canonical_momentum_action_jacobian.py',
        'src/bhsm/interface/aether_n3_exact_full_local_action_jet_v17_60.py',
        'src/bhsm/interface/aether_sobolev_galerkin_pencil_lift_v15_81.py',
        'src/bhsm/interface/aether_m4_standard_model_zeta_backreaction_v15_51.py',
        'src/bhsm/interface/aether_post_cut_nonround_lorentzian_cap_v15_48.py',
        'src/bhsm/interface/muon_birth_reset_evaluation.py',
    ]
    report = dict(
        classification='EVALUATED_RETAINED_N12_GEOMETRIC_RESET_AT_FORWARD_SWAPPED_E1_C2_CENTER',
        starting_head='64b51a2cedb7be410251b3fb3c4f942cc148bcc4',
        scientific_reference='524ed90689bd5923c249bba2e699abf627e703cd',
        input_identities=[_identity(p, repository) for p in inputs],
        producer_identities=[_identity(p, repository) for p in producer_paths],
        producer_call=dict(symbol='aether_full_reset_action_jacobian.full_reset_residual',
                           order=12, points=96, high_precision_action=True,
                           internal_decimal_precision=60,
                           binary64_return_and_trace_normalization=True,
                           ordered_scale=scale,
                           ordered_scale_binary64_hex=scale.hex()),
        runtime=dict(python=sys.version.split()[0], numpy=np.__version__, scipy=scipy.__version__),
        state_binding=dict(
            original_state_npz_hash_matches_root_certificate=True,
            original_state_npz_expected_sha256=expected_state_sha256,
            incoming_C1_E1=dict(source_key='state', source_indices_zero_based=[98, 196],
                               selected_branch=23, role='original child C_* becomes incoming event E1'),
            outgoing_C2=dict(source_key='state', source_indices_zero_based=[0, 98],
                             selected_branch=24, role='original event E_* becomes outgoing child C2'),
            state_layout=dict(q=[0, 37], velocity=[37, 74], lapse_shift_multipliers=[74, 98]),
            source_reference_key='branch_reference', source_weights_key='state_weights',
            normalization_key='normalization_coordinates',
            one_common_event=True, finite_time_displacement=0,
            state_is_retained_binary64_proof_center=True,
            exact_root_distance_action_norm_upper=certificate['refined_radii_theorem']['a_posteriori_root_distance_upper']),
        retained_state_values=dict(Phi_P_minus_geometry=_values(incoming),
                                   Phi_mu_plus_geometry=_values(outgoing),
                                   state_weights=_values(weights), branch_reference=_values(reference),
                                   normalization_coordinates=_values(normalization)),
        geometry_field_blocks={side:dict(q=_values(state[:37]),
            velocity=_values(state[37:74]),
            lapse_shift_multipliers=_values(state[74:98]),
            lapse_coefficients_n1_to_n12=_values(state[74:86]),
            shift_coefficients_b0_to_b11=_values(state[86:98]))
            for side,state in [('incoming_C1_E1', incoming), ('outgoing_C2', outgoing)]},
        selected_incoming_event_index=int(selected), expected_incoming_event_index=23,
        actual_ordered_lines=dict(incoming_C1_E1=ordered_lines[0], outgoing_C2=ordered_lines[1]),
        residual_vector=rows.tolist(), residual_groups=groups,
        residual_l2_norm=float(np.linalg.norm(rows)), residual_max_abs=float(np.max(np.abs(rows))),
        raw_geometric_traces=dict(values=raw_trace.tolist(), max_abs=float(np.max(np.abs(raw_trace)))),
        raw_attachment_trace=dict(value=float(raw_attachment)),
        boundary_whitening_matrix=whitening.tolist(),
        normalized_geometric_trace_coordinates=_group(rows,26,29),
        normalized_attachment_coordinate=_group(rows,29,30),
        normalized_boundary_coordinate_scope='Whitened4coordinates can mix raw geometric3trace and attachment1; raw maps given separately.',
        raw_canonical_momentum=dict(incoming_event=momenta[0].tolist(),
            outgoing_child=momenta[1].tolist(),
            child_minus_event=raw_momentum_difference.tolist(),
            momentum_normalization_matrix=momentum_normalization.tolist(),
            normalized_child_minus_event=rows[55:57].tolist(),
            decimal_precision=60),
        precision_crosscheck=dict(binary64_selected_index=int(float_selected),
                                 binary64_residual_l2_norm=float(np.linalg.norm(float_rows)),
                                 full_binary64_residual_vector=float_rows.tolist(),
                                 binary64_minus_decimal60_return_max_abs=float(np.max(np.abs(float_rows - rows)))),
        orientation=dict(chronology='E0 -> C1(branch23) -> E1=C_* -> C2=E_*(branch24)',
                         trace_difference='outgoing child minus incoming event',
                         canonical_difference='outgoing child momentum minus incoming event momentum',
                         constraints='old child and old event constraints exchange under forward swap',
                         eigenline='same retained reference-overlap-selected line; returned incoming index23 verified',
                         physical_full_field_matching_claimed=False),
        error_scope='Direct evaluation of the unchanged quadrature96 geometric 57-row producer at exact retained binary64 center inputs. Internal action/eigenpair/momentum calculations use Decimal60; constraints, normalization and returned rows remain binary64. The arithmetic-path difference is a crosscheck, not a rigorous error bound. The existing action-norm root-distance certificate is retained but not converted into residual component enclosures here. No continuum quadrature error or complete interacting full-field residual is inferred from these numbers.',
        execution=dict(producer_calls=2, high_precision_action_calls=1, binary64_crosscheck_calls=1,
                       additional_high_precision_sector_blocks_for_raw_momentum=2,
                       trajectories=0, new_root_solves=0, campaigns=0, old_controls=0),
    )
    return report


def evaluate(output):
    report = evaluate_reset_values()
    groups = report['residual_groups']
    selected = report['selected_incoming_event_index']
    raw_attachment = report['raw_attachment_trace']['value']
    output.mkdir(parents=True, exist_ok=True)
    (output / 'result.json').write_text(json.dumps(report, sort_keys=True, indent=2) + '\n', newline='\n')
    print(json.dumps(dict(output=str(output), selected=selected,
                         residual_l2_norm=report['residual_l2_norm'],
                         residual_max_abs=report['residual_max_abs'],
                         groups={k:v['max_abs'] for k,v in groups.items()},
                         raw_trace_max_abs=report['raw_geometric_traces']['max_abs'],
                         raw_attachment=raw_attachment,
                         precision_max_difference=report['precision_crosscheck']['binary64_minus_decimal60_return_max_abs'])))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    evaluate(parser.parse_args().out)
