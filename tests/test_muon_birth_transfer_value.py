"""Validate actual retained E1 receipts without rerunning their HP producer."""
from hashlib import sha256
import json
from pathlib import Path

import numpy as np
import pytest

from bhsm.interface.muon_birth_transfer_value import (
    ARTIFACT_DIRECTORY,
    FIRST_UNAVAILABLE_VALUE,
    MuonBirthTransferValue,
    SCIENTIFIC_REFERENCE,
    STARTING_HEAD,
)


ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / ARTIFACT_DIRECTORY
STATE_SOURCE = ROOT / 'artifacts/flagship_integration/BHSM_N12_C2_REFINED_RESET_ROOT_CENTER.npz'


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


@pytest.fixture
def owned_receipts():
    return dict(
        reset_values=read_json(FOLDER / 'retained_reset/run_1/result.json'),
        transport_inputs=read_json(FOLDER / 'muon_transport/numerical_input_receipt.json'),
        sector_values=read_json(FOLDER / 'sector_values/value_input_receipt.json'),
    )


@pytest.fixture
def packet(owned_receipts, monkeypatch):
    # The actual reset was evaluated twice by its separate replay. Any attempt
    # to rerun it in these receipt/guard tests is an unintended operation.
    def producer_must_not_run(*args, **kwargs):
        raise AssertionError('receipt tests must not execute the reset producer')

    monkeypatch.setattr(
        'bhsm.interface.muon_birth_transfer_value.evaluate_reset_values',
        producer_must_not_run,
    )
    return MuonBirthTransferValue(**owned_receipts)


@pytest.fixture
def original_state_arrays():
    with np.load(STATE_SOURCE, allow_pickle=False) as source:
        return {key: np.array(source[key], copy=True) for key in source.files}


def assert_binary64_identical(receipt, expected):
    actual = np.asarray(receipt['values'], dtype=np.float64)
    expected = np.asarray(expected, dtype=np.float64)
    assert actual.shape == expected.shape
    assert actual.tobytes() == expected.tobytes()
    assert receipt['binary64_hex'] == [float(value).hex() for value in expected.flat]


def test_actual_same_event_vectors_are_original_npz_swapped_bit_for_bit(packet, original_state_arrays):
    values = packet.reset_values['retained_state_values']
    original = original_state_arrays['state']
    assert original.shape == (196,)
    assert_binary64_identical(values['Phi_P_minus_geometry'], original[98:196])
    assert_binary64_identical(values['Phi_mu_plus_geometry'], original[:98])
    binding = packet.reset_values['state_binding']
    assert binding['incoming_C1_E1']['source_indices_zero_based'] == [98, 196]
    assert binding['outgoing_C2']['source_indices_zero_based'] == [0, 98]
    assert binding['one_common_event']
    assert binding['finite_time_displacement'] == 0
    assert not packet.report()['Sigma_P_to_mu']['finite_time_offset_used']


def test_reset_weight_reference_and_normalization_arrays_keep_their_owners(packet, original_state_arrays):
    values = packet.reset_values['retained_state_values']
    assert_binary64_identical(values['state_weights'], original_state_arrays['state_weights'])
    assert_binary64_identical(values['branch_reference'], original_state_arrays['branch_reference'])
    path = ROOT / 'artifacts/flagship_integration/BHSM_N12_FULL_RESET_ACTION_JACOBIAN.npz'
    with np.load(path, allow_pickle=False) as source:
        assert_binary64_identical(values['normalization_coordinates'], source['normalization_coordinates'])
        assert_binary64_identical(values['state_weights'], source['state_weights'])
    identity = next(row for row in packet.reset_values['input_identities']
                    if row['path'].endswith('BHSM_N12_C2_REFINED_RESET_ROOT_CENTER.npz'))
    assert identity['sha256'] == sha256(STATE_SOURCE.read_bytes()).hexdigest()
    assert identity['sha256'] == '59dd88661b15cbeec96bc19294f9d9c64f754cccbfbc385c32329fa9c864a8fe'


def test_q_velocity_and_lapse_shift_values_are_actual_state_slices(packet):
    reset = packet.reset_values
    for side, key in [('incoming_C1_E1', 'Phi_P_minus_geometry'), ('outgoing_C2', 'Phi_mu_plus_geometry')]:
        state = np.asarray(reset['retained_state_values'][key]['values'])
        fields = reset['geometry_field_blocks'][side]
        assert_binary64_identical(fields['q'], state[:37])
        assert_binary64_identical(fields['velocity'], state[37:74])
        assert_binary64_identical(fields['lapse_shift_multipliers'], state[74:98])
        assert_binary64_identical(fields['lapse_coefficients_n1_to_n12'], state[74:86])
        assert_binary64_identical(fields['shift_coefficients_b0_to_b11'], state[86:98])
        assert_binary64_identical(packet.sector_values['retained_state_values'][side], state)


def test_all_57_actual_rows_are_finite_and_report_their_retained_magnitude(packet):
    reset = packet.reset_values
    rows = np.asarray(reset['residual_vector'])
    assert rows.shape == (57,)
    assert np.isfinite(rows).all()
    norm, maximum = float(np.linalg.norm(rows)), float(np.max(np.abs(rows)))
    assert norm == pytest.approx(7.64107108345298e-15, rel=2e-15, abs=0)
    assert maximum == pytest.approx(5.628594097932515e-15, rel=2e-15, abs=0)
    assert reset['residual_l2_norm'] == pytest.approx(norm, rel=2e-15, abs=0)
    assert reset['residual_max_abs'] == maximum
    assert packet.report()['reset_residual_norm_or_component_enclosures']['component_enclosures'] is None


def test_all_seven_reset_groups_partition_the_actual_rows(packet):
    reset = packet.reset_values
    rows = np.asarray(reset['residual_vector'])
    ranges = {
        'event_multiplier_constraints': (0, 24),
        'event_canonical_energy_constraint': (24, 25),
        'selected_event_row': (25, 26),
        'normalized_trace_attachment_4': (26, 30),
        'child_multiplier_constraints': (30, 54),
        'child_canonical_energy_constraint': (54, 55),
        'canonical_momentum_child_minus_event_2': (55, 57),
    }
    assert set(reset['residual_groups']) == set(ranges)
    covered = []
    for name, (start, stop) in ranges.items():
        group = reset['residual_groups'][name]
        assert group['row_indices_zero_based'] == list(range(start, stop))
        np.testing.assert_array_equal(group['values'], rows[start:stop])
        assert group['l2_norm'] == pytest.approx(np.linalg.norm(rows[start:stop]), rel=2e-15, abs=0)
        assert group['max_abs'] == np.max(np.abs(rows[start:stop]))
        covered.extend(group['row_indices_zero_based'])
    assert covered == list(range(57))


def test_actual_raw_trace_and_momentum_normalizations_reproduce_returned_rows(packet):
    reset = packet.reset_values
    rows = np.asarray(reset['residual_vector'])
    raw_boundary = np.r_[reset['raw_geometric_traces']['values'], reset['raw_attachment_trace']['value']]
    whitening = np.asarray(reset['boundary_whitening_matrix'])
    np.testing.assert_array_equal(whitening @ raw_boundary, rows[26:30])
    canonical = reset['raw_canonical_momentum']
    difference = np.asarray(canonical['outgoing_child']) - np.asarray(canonical['incoming_event'])
    np.testing.assert_array_equal(difference, canonical['child_minus_event'])
    normalized = np.asarray(canonical['momentum_normalization_matrix']) @ difference
    np.testing.assert_array_equal(normalized, rows[55:57])
    np.testing.assert_array_equal(normalized, canonical['normalized_child_minus_event'])
    assert canonical['decimal_precision'] == 60


def test_incoming23_outgoing24_are_evaluated_ordered_lines_on_the_same_event(packet):
    reset = packet.reset_values
    assert reset['selected_incoming_event_index'] == 23
    assert reset['actual_ordered_lines']['incoming_C1_E1']['index'] == 23
    assert reset['actual_ordered_lines']['outgoing_C2']['index'] == 24
    for line in reset['actual_ordered_lines'].values():
        assert np.isfinite(float(line['eigenvalue']))
        assert float(line['spectral_gap']) > 0
    report = packet.report()
    assert report['common_domain_identity']['scope'] == 'RETAINED_N12_RESET_POINT_AND_CHART_ONLY'
    assert report['common_domain_identity']['physical_full_field_domain_identity'] is None
    assert report['Phi_mu_plus']['muon_label'] == dict(sector='charged_lepton', slot=1, mode=[5, 2])


def test_muon_projector_reuses_original_slot_and_is_exactly_idempotent(packet):
    receipt = packet.transport_inputs['muon_projector_numerical_value']
    original = read_json(ROOT / receipt['retained_row_source'])
    rows = original['family_mode_C2_instantiation']['rows']
    lepton_rows = [row for row in rows if row['sector'] == 'charged_lepton']
    assert [(row['slot'], row['mode_label']) for row in lepton_rows] == [
        (0, [0, 0]), (1, [5, 2]), (2, [9, 3]),
    ]
    assert receipt['retained_row'] == lepton_rows[1]
    projector = np.asarray(receipt['real']) + 1j*np.asarray(receipt['imag'])
    assert projector.shape == (3, 3)
    np.testing.assert_array_equal(projector, np.diag([0, 1, 0]))
    assert np.max(np.abs(projector @ projector - projector)) == 0.0
    assert receipt['evaluated_idempotence_max_abs_residual'] == 0.0
    assert np.linalg.matrix_rank(projector) == receipt['evaluated_projector_rank'] == 1
    assert not receipt['new_family_selector_defined']
    assert not receipt['actual_nonzero_matter_section_projected']
    assert receipt['actual_E1_reset_projector_compatibility_value'] is None


def test_first_missing_fermion_trace_cannot_be_promoted_by_geometric_reset_or_projector(packet):
    report = packet.report()
    missing = report['first_unavailable_numerical_operand']
    assert missing['id'] == FIRST_UNAVAILABLE_VALUE == 'INCOMING_C1_E1_FERMION_TRACE'
    assert missing['incoming_value'] is None
    assert 'NOT_ZERO' in missing['status']
    assert not report['physical_muon_birth_transfer_identified']
    assert report['Phi_P_minus']['incoming_fermion_trace'] is None
    assert report['Phi_mu_plus']['transported_fermion_trace'] is None
    assert report['transported_muon_state'] is None
    assert report['common_domain']['fermionic_graph_value_at_E1'] is None
    assert report['common_domain']['full_field_pairing'] is None
    assert report['active_strata'] is None
    assert not report['noether_hamiltonian_balance']['omitted_sectors_set_zero']
    assert all(value['value'] is None for value in report['downstream'].values())
    assert report['energy_matching']['F_E_mu'] is None
    assert report['energy_matching']['Delta_imp_bulk'] is None
    assert not report['energy_matching']['geometric_E_can_substituted']
    assert not report['energy_matching']['tangential_matter_trace_is_mechanical_formation_mode']


def test_geometric_eta_and_nonzero_current_operators_do_not_supply_matter_state(packet):
    sector = packet.sector_values
    layout = sector['retained_state_layout']
    assert layout['eta_is_fixed_monotone_quotient_gauge'] == 'f=chi'
    assert not layout['independent_eta_coefficients_in_q']
    assert not layout['gauge_fermion_ghost_HS_amplitudes_encoded_in_98_vector']
    assert sector['fresh_geometric_snapshot']['positive_geometry_and_lapse']
    assert not sector['fresh_geometric_snapshot']['physical_full_field_stationary_background_claimed']
    fermion = next(row for row in sector['sector_value_inventory'] if row['sector'] == 'fermion_family')
    assert not fermion['inactive']
    assert fermion['local_operator_nonzero_dependency']['all_eight_current_derivatives_nonzero']
    assert all(value > 0 for value in fermion['local_operator_nonzero_dependency']['per_operator_frobenius_norm'])
    assert not sector['fermion_body_inventory']['contains_fermion_state_coefficients']
    assert not sector['prior_zero_background_scope']['proves_inactivity_of_current_interacting_muon_birth_field']


@pytest.mark.parametrize('side,bad_index', [
    ('incoming_C1_E1', 24), ('outgoing_C2', 23),
    ('incoming_C1_E1', -1), ('outgoing_C2', 25),
])
def test_constructor_rejects_a_different_ordered_branch_pair(owned_receipts, side, bad_index):
    owned_receipts['reset_values']['actual_ordered_lines'][side]['index'] = bad_index
    with pytest.raises(ValueError, match='incoming23/outgoing24'):
        MuonBirthTransferValue(**owned_receipts)


@pytest.mark.parametrize('record', ['reset_values', 'transport_inputs', 'sector_values'])
@pytest.mark.parametrize('identity', ['starting_head', 'scientific_reference'])
def test_constructor_rejects_mixed_scientific_receipt_identities(owned_receipts, record, identity):
    assert owned_receipts[record]['starting_head'] == STARTING_HEAD
    assert owned_receipts[record]['scientific_reference'] == SCIENTIFIC_REFERENCE
    owned_receipts[record][identity] = 'unrelated-scientific-identity'
    with pytest.raises(ValueError, match='different scientific starting identity'):
        MuonBirthTransferValue(**owned_receipts)


@pytest.mark.parametrize('bad_rows', [
    [0.0]*56, [0.0]*58, [[0.0]]*57,
    [float('nan')]+[0.0]*56, [float('inf')]+[0.0]*56,
    [-float('inf')]+[0.0]*56,
])
def test_constructor_rejects_incomplete_or_nonfinite_reset_rows(owned_receipts, bad_rows):
    owned_receipts['reset_values']['residual_vector'] = bad_rows
    with pytest.raises(ValueError, match='finite 57 reset rows'):
        MuonBirthTransferValue(**owned_receipts)


@pytest.mark.parametrize('claimed_value', [0.0, [], [0.0], {'value': 0.0}])
def test_zero_or_placeholder_cannot_fill_the_unavailable_trace(owned_receipts, claimed_value):
    owned_receipts['transport_inputs']['first_unavailable_numerical_operand']['incoming_value'] = claimed_value
    with pytest.raises(ValueError, match='unavailable incoming fermion trace'):
        MuonBirthTransferValue(**owned_receipts)


def test_constructor_rejects_a_different_missing_operand(owned_receipts):
    owned_receipts['transport_inputs']['first_unavailable_numerical_operand']['id'] = 'GENERIC_KKT_GAP'
    with pytest.raises(ValueError, match='unavailable incoming fermion trace'):
        MuonBirthTransferValue(**owned_receipts)


def test_constructor_detaches_input_receipts_before_the_caller_mutates_them(owned_receipts):
    packet = MuonBirthTransferValue(**owned_receipts)
    baseline = packet.report()
    owned_receipts['reset_values']['residual_vector'][0] = float('nan')
    owned_receipts['transport_inputs']['muon_projector_numerical_value']['real'][1][1] = 0.0
    owned_receipts['sector_values']['retained_state_values']['incoming_C1_E1']['values'][0] = 999.0
    assert packet.report() == baseline


def test_report_mutation_is_detached_from_packet_and_future_reports(packet):
    baseline = packet.report()
    edited = packet.report()
    edited['Phi_P_minus']['geometry']['values'][0] = 999.0
    edited['muon_projector']['real'][1][1] = 0.0
    edited['first_unavailable_numerical_operand']['incoming_value'] = [0.0]
    edited['full_field_active_sector_ledger']['sector_value_inventory'][4]['inactive'] = True
    edited['downstream']['a_mu']['value'] = 1.0
    assert packet.report() == baseline
