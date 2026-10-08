"""Scientific ownership and event-definition gates; no numerical controls."""
from copy import deepcopy
from dataclasses import replace

import pytest

from bhsm.interface.ae4_support_loss_classical_realization import (
    CLASSICAL_OWNER, HEAT_OWNER, FIRST_MISSING_DEFINITION, PORT_ORDER,
    REQUIRED_OUTPUTS, inspected_support_loss_realization,
)
from bhsm.interface.master_action.terms import term_rows


@pytest.fixture
def realization():
    return inspected_support_loss_realization()


def test_classical_KKT_owner_and_consuming_heat_owner_remain_separate(realization):
    report = realization.report()
    owners = report['owner_separation']
    assert owners['support_loss_classical_owner'] == CLASSICAL_OWNER
    assert owners['downstream_heat_owner'] == HEAT_OWNER
    assert CLASSICAL_OWNER != HEAT_OWNER
    assert owners['quantum_heat_in_classical_restoring_action'] is False
    assert owners['interface_between_owners'] == 'c=ell_star^2=i/r'
    assert report['owner_base_domain_pairing']['common_physical_identity_instantiated'] is False


def test_all_required_outputs_bind_one_pending_action_base_domain(realization):
    report = realization.report()
    assert tuple(report['required_outputs']) == REQUIRED_OUTPUTS
    assert {x['binding_identity'] for x in report['required_outputs'].values()} == {realization.binding_identity}
    assert report['required_outputs']['b_psi']['value'] == [None] * 7
    assert all(x['blocked_by'] == FIRST_MISSING_DEFINITION for x in report['required_outputs'].values())
    assert report['physical_solution'] is False


def test_energy_equality_without_cessation_condition_cannot_select_event(realization):
    event = realization.report()['event_conditions']
    assert event['energy_equality']['equation'] == '<psi_star,(R_total-H_event,drive)psi_star>=0'
    assert event['conjunction_required'] and event['first_future_selection']
    assert event['outward_support_cessation']['value'] is None
    assert event['event_surface'] is None and not event['root_search_performed']
    assert realization.report()['first_missing_definition']['name'] == FIRST_MISSING_DEFINITION


@pytest.mark.parametrize('replacement', [0, 'descriptor=0', 'canonical_stop', 'sum Pi=0'])
def test_known_boundary_balance_or_artificial_zero_cannot_fill_cessation_slot(realization, replacement):
    audit = deepcopy(realization.outward_audit)
    audit['first_missing_definition']['value'] = replacement
    with pytest.raises(ValueError, match='operational outward-support'):
        replace(realization, outward_audit=audit)


def test_mixed_requirement_identity_is_rejected(realization):
    different = replace(realization.outputs[0], binding_identity='another owner/base/domain')
    with pytest.raises(ValueError, match='mixed owner/base/domain'):
        replace(realization, outputs=(different,) + realization.outputs[1:])


def test_report_nested_mutation_cannot_publish_arbitrary_cessation(realization):
    detached = realization.report()
    detached['event_conditions']['outward_support_cessation']['value'] = 0
    detached['classical_owner_provenance']['classical_owner']['quantum_heat_in_classical_action'] = True
    report = realization.report()
    assert report['event_conditions']['outward_support_cessation']['value'] is None
    assert report['classical_owner_provenance']['classical_owner']['quantum_heat_in_classical_action'] is False


def test_direct_provenance_mutation_fails_closed_on_publication(realization):
    realization.outward_audit['first_missing_definition']['value'] = 'arbitrary flux=0'
    with pytest.raises(ValueError, match='operational outward-support'):
        realization.report()


def test_quantum_determinant_cannot_be_registered_as_extra_classical_resistance(realization):
    audit = deepcopy(realization.classical_audit)
    audit['classical_owner']['quantum_heat_in_classical_action'] = True
    with pytest.raises(ValueError, match='downstream'):
        replace(realization, classical_audit=audit)


def test_registered_strata_and_derived_boundary_outputs_are_not_duplicate_scalars(realization):
    audit = realization.classical_audit
    rows = audit['scalar_composition']['registered_13_terms']
    assert [x['term_id'] for x in rows] == [x['term_id'] for x in term_rows()]
    assert len({x['term_id'] for x in rows}) == 13
    matcher = next(x for x in rows if x['term_id'] == 'T4_matcher')
    assert 'lambda^dagger R' in matcher['counting_rule']
    sectors = {x['sector']: x for x in audit['sector_accounting']}
    assert sectors['trace_momentum_conormal_dynamic_flux']['kind'] == 'derived_boundary_or_Legendre_output'
    assert sectors['contacts']['kind'] == 'directional_derivative_of_originating_scalar_or_constraint'
    assert sectors['AE4_finite_E1_and_relative_zeta_eta']['kind'] == 'downstream_quantum_owner'
    assert audit['scalar_composition']['stratification_guard']['reduction_arrows_sourced'] is False


def test_complete_normal_section_and_kinetic_normalization_are_retained(realization):
    report = realization.report()
    normal = report['normal_section']
    assert normal['full_active_section_required']
    assert normal['registered_regular_strata'] == ['M8', 'M5+', 'M5-', 'M4']
    assert normal['active_regular_strata'] is None
    assert tuple(normal['canonical_seven_port_order']) == PORT_ORDER
    assert 'psi_star^(s) n_star^(s)' in normal['equation']
    assert report['normalization']['preferred_condition'] == '<psi_star,I_star psi_star>=1'
    assert all(report['normalization'][key] is None for key in ('base_i', 'i_v', 'i_J', 'i_vJ'))
    assert not report['normalization']['zero_total_inertia_jets_inferred']
    assert not report['branch_identity']['selected_mode_is_N12_ordered_stop_eigenline']


def test_existing_later_support_evolution_is_not_misreported_as_absent(realization):
    # Later reciprocal attachment is actual retained progress, not a newly
    # invented cessation law. The source audit must retain that distinction.
    audit = realization.outward_audit
    records = audit['inspected_equations']
    text = str(records)
    assert 'reciprocal_attachment_action_v11_3.py' in text
    assert 'I_W=upsilon I_C' in text
    assert 'J_attach' in text
    assert audit['no_valid_event_replacement'] is True


def test_no_physical_or_generic_control_execution_after_exact_definition_stop(realization):
    report = realization.report()
    assert all(x['value'] is None for x in report['downstream_status'].values())
    assert all(x['blocked_by'] == FIRST_MISSING_DEFINITION for x in report['downstream_status'].values())
    assert report['execution']['new_generic_KKT_algebra'] == 0
    assert report['execution']['new_finite_control_runs'] == 0
    assert report['execution']['new_physical_KKT_solves'] == 0
    assert set(report['claim_statuses']) == {'DERIVED', 'EVALUATED', 'CONTROL_ONLY', 'UNEVALUATED', 'OWNER_DEFINITION_GAP'}
