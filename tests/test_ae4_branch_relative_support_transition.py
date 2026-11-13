"""Branch-transfer ownership and physical-value guards; no physics controls."""
from dataclasses import replace
import json

import pytest

from bhsm.interface.ae4_branch_relative_support_transition import (
    BranchTransferEvidence,
    ARTIFACT_DIRECTORY,
    EVENT_DEFINITION,
    FIRST_MISSING_OPERAND,
    SUPERSEDED_GAP,
    branch_relative_cutoff_contract,
    branch_transfer_definition,
    current_muon_birth_realization,
)


@pytest.fixture
def complete_evidence():
    # Logical evidence only. This fixture does not supply any physical state,
    # event, action matrix, mode or numerical transition value.
    return BranchTransferEvidence(
        parent_branch='incoming branch',
        child_branch='successor branch',
        event_identity='one common event',
        common_action_domain_identity='one common action/domain',
        parent_noncontinuation=True,
        successor_admissible=True,
        successor_realized=True,
        inherited_matching=True,
    )


@pytest.fixture
def birth_report():
    return current_muon_birth_realization()


def test_transfer_requires_completed_physical_evidence_conjunction(complete_evidence):
    assert complete_evidence.transfer_established


@pytest.mark.parametrize('missing', [
    'parent_noncontinuation', 'successor_admissible',
    'successor_realized', 'inherited_matching',
])
def test_each_physical_transfer_obligation_is_required(complete_evidence, missing):
    assert not replace(complete_evidence, **{missing: False}).transfer_established


@pytest.mark.parametrize('missing', [
    'parent_branch', 'child_branch', 'event_identity',
    'common_action_domain_identity',
])
def test_unbound_evidence_cannot_establish_transfer(complete_evidence, missing):
    assert not replace(complete_evidence, **{missing: ''}).transfer_established


def test_same_branch_relabeling_is_not_a_transfer(complete_evidence):
    assert not replace(
        complete_evidence, child_branch=complete_evidence.parent_branch,
    ).transfer_established


def test_failed_certificate_never_counts_as_physical_noncontinuation(complete_evidence):
    assert not replace(complete_evidence, proof_failure_only=True).transfer_established
    assert not replace(
        complete_evidence, parent_noncontinuation=False,
        proof_failure_only=True,
    ).transfer_established


def test_admissible_successor_without_realization_is_insufficient(complete_evidence):
    compatible_channel = replace(complete_evidence, successor_realized=False)
    assert compatible_channel.successor_admissible
    assert not compatible_channel.transfer_established
    assert not branch_transfer_definition()[
        'successor_admissibility_without_realization_is_sufficient'
    ]


@pytest.mark.parametrize('flag', [
    'parent_noncontinuation', 'successor_admissible', 'successor_realized',
    'inherited_matching', 'proof_failure_only',
])
def test_truthy_string_is_not_physical_boolean_evidence(complete_evidence, flag):
    with pytest.raises(ValueError, match='explicit booleans'):
        replace(complete_evidence, **{flag: 'False'})


@pytest.mark.parametrize('identity', [
    'parent_branch', 'child_branch', 'event_identity',
    'common_action_domain_identity',
])
def test_nonstring_evidence_identity_is_rejected(complete_evidence, identity):
    with pytest.raises(ValueError, match='identities must be strings'):
        replace(complete_evidence, **{identity: 1})
    assert not replace(complete_evidence, **{identity: ' \t '}).transfer_established


def test_whitespace_does_not_make_same_branch_a_distinct_successor(complete_evidence):
    assert not replace(
        complete_evidence, child_branch='  ' + complete_evidence.parent_branch + '  ',
    ).transfer_established


def test_semantic_owner_definition_does_not_promote_a_stop_or_arbitrary_zero():
    definition = branch_transfer_definition()
    assert definition['event'] == EVENT_DEFINITION
    assert definition['status'] == 'ADOPTED_OWNER_DEFINITION'
    assert 'sup I_B' in definition['transition_time']
    assert 'dynamically realized' in definition['transition_time']
    for replacement in (
        'proof_certificate_failure_is_physical_loss',
        'arbitrary_current_zero_is_event', 'upsilon_zero_is_event',
        'descriptor_zero_is_event', 'canonical_stop_alone_is_event',
        'last_cached_point_is_event', 'new_support_scalar',
    ):
        assert definition[replacement] is False


def test_cutoff_uses_child_side_of_birth_and_keeps_decay_separate():
    cutoff = branch_relative_cutoff_contract()
    assert cutoff['surface_rule'] == 'Sigma_star^mu=Sigma_(P->mu)=Sigma_P,out=Sigma_mu,in'
    assert cutoff['evaluation_side'] == 'MUON_CHILD_PLUS_SIDE_AT_BIRTH'
    assert 'no finite temporal offset' in cutoff['plus_side_meaning']
    assert cutoff['cutoff_event'] == 'MUON_BIRTH__P_TO_MU'
    assert 'SEPARATE_LATER_APPLICATION' in cutoff['decay_event']
    assert not cutoff['decay_surface_sets_birth_cutoff']
    assert not cutoff['experimental_lifetime_selects_event']
    assert cutoff['parent_loss_and_child_formation_can_share_event']
    assert not cutoff['same_branch_formation_is_same_branch_cessation_by_default']
    assert cutoff['muon_heat_length_squared_rule'] == 'ell_star,mu^2=c_mu=i_mu^+/r_mu^+'


def test_birth_energy_condition_survives_owner_amendment(birth_report):
    cutoff = birth_report['cutoff_owner_amendment']
    energy = birth_report['energy_birth_test']
    assert not cutoff['energy_equality_automatically_removed_by_transfer']
    assert not cutoff['energy_equality_evaluated']
    assert energy['equation'] == '<psi_mu^+,(R_mu^+-H_event,drive)psi_mu^+>=0'
    assert 'H_impedance-H_bulk,constrained' in energy['conditional_identity']
    assert 'muon formation mode/domain' in energy['identity_premise']
    assert energy['evaluated_value'] is None
    assert not energy['zero_Legendre_energy_is_this_equation']
    assert not energy['surface_moved_or_fitted']


def test_complete_normal_section_full_kinetic_norm_and_seven_ports(birth_report):
    cutoff = birth_report['cutoff_owner_amendment']
    normal = birth_report['normal_source']
    assert cutoff['preferred_normalization'] == '<psi_mu^+,I_mu^+ psi_mu^+>=1'
    assert not cutoff['base_unit_norm_implies_zero_total_inertia_jets']
    assert normal['normalization_requires_full_same_owner_inertia']
    assert not normal['normalization_evaluated']
    assert normal['full_active_section_required']
    assert 'psi_mu^+,(s) n_star^(s)' in normal['definition']
    assert normal['seven_port_order'] == [
        'trace_1', 'trace_2', 'trace_3', 'canonical_momentum_1',
        'canonical_momentum_2', 'dynamic_flux_1', 'dynamic_flux_2',
    ]
    assert 'D2P[X_flow,u_psi]' in normal['seven_port_formula']
    assert 'DP[D_psi X_flow]' in normal['seven_port_formula']
    assert 'opposite outward conormals' in normal['orientation']
    assert not normal['eighth_support_coordinate_added']
    assert not normal['descriptor_or_launch_substitution']


def test_current_report_has_one_value_level_stop_with_no_physical_promotion(birth_report):
    missing = birth_report['first_missing_operand']
    assert missing['name'] == FIRST_MISSING_OPERAND
    assert missing['status'] == 'TRANSITION_OPERAND_UNEVALUATED'
    assert missing['value'] is None
    assert missing['not_a_missing_semantic_definition']
    assert not missing['missing_generic_reset_or_family_selector']
    assert not birth_report['physical_birth_transition_instantiated']
    outputs = birth_report['required_outputs']
    assert outputs['b_psi']['value'] == [None] * 7
    assert all(row['value'] is None for name, row in outputs.items() if name != 'b_psi')
    assert {row['blocked_by'] for row in outputs.values()} == {FIRST_MISSING_OPERAND}
    assert {row['binding_identity'] for row in outputs.values()} == {birth_report['binding_identity']}
    assert all(row['value'] is None for row in birth_report['downstream'].values())
    assert birth_report['stationary_base']['equations'] == ['L_eta=0', 'R=0']
    for operand in ('base', 'multipliers', 'domain', 'pairing', 'chart_pullback'):
        assert birth_report['stationary_base'][operand] is None


def test_old_semantic_gap_is_superseded_without_erasing_receipts(birth_report):
    supersession = birth_report['supersession']
    assert supersession['old_gap'] == SUPERSEDED_GAP
    assert not supersession['old_gap_is_current']
    assert supersession['replacement_definition'] == EVENT_DEFINITION
    assert supersession['old_research_receipts_preserved']
    assert set(birth_report['retained_evidence']) == {
        'parent_transition_audit.json', 'child_birth_audit.json',
        'muon_operand_reuse_audit.json',
    }


def test_retained_reset_continuation_and_family_progress_are_preserved(birth_report):
    audits = birth_report['retained_evidence']
    parent = audits['parent_transition_audit.json']
    child = audits['child_birth_audit.json']
    reuse = audits['muon_operand_reuse_audit.json']
    assert parent['A_actual_parent_branch']['incoming_selected_line'] == 23
    assert parent['A_actual_parent_branch']['outgoing_selected_line'] == 24
    assert 'local component' in parent['B_parent_noncontinuation']['limitations']
    assert parent['CDE_retained_transition_subclosures']['generic_event_child_relation'].startswith('CLOSED')
    certificate = child['answers']['E']['retained_certificate_facts']
    assert certificate['post_event_positive_duration_certified']
    assert certificate['unique_local_continuum_retained_child_flow_exists']
    assert not certificate['single_child_selector_required']
    assert child['answers']['C']['preserved_results']['upstream_family_label_and_projector_transport']
    assert not child['answers']['C']['preserved_results']['new_species_or_family_selector_required']
    assert not reuse['single_missing_transition_operand']['invented_new_selector_or_gate']
    assert 'PEI11 is CLOSED' in reuse['single_missing_transition_operand']['existing_map_reused']


def test_positive_child_ordered_pencil_is_not_the_birth_energy_test(birth_report):
    child = birth_report['retained_evidence']['child_birth_audit.json']
    energy = child['birth_energy_identity']
    assert energy['distinct_retained_equations']['child_ordered_pencil_initial_sign'] == 'POSITIVE'
    assert 'neither evaluates nor disproves F_E_mu' in energy['distinct_retained_equations']['child_ordered_pencil_scope']
    assert all(value is None for value in energy['physical_values'].values())
    assert not energy['distinct_retained_equations']['surface_moved_to_force_equality']


def test_retained_component_certificates_do_not_supply_physical_values(birth_report):
    assert not birth_report['chronology']['temporal_precursor_to_physical_muon_binding_evaluated']
    assert birth_report['chronology']['tau_mu_in'] is None
    assert birth_report['chronology']['tau_mu_out'] is None
    assert not birth_report['chronology']['precursor_new_species_or_action']
    assert all(count == 0 for count in birth_report['execution'].values())
    assert {'RETAINED_CERTIFIED', 'UNEVALUATED'} <= birth_report['claim_statuses'].keys()


def test_detached_report_mutation_cannot_publish_physical_transition_values(birth_report):
    birth_report['first_missing_operand']['value'] = 'guessed transition'
    birth_report['required_outputs']['psi_star']['value'] = 'cached launch'
    birth_report['retained_evidence']['child_birth_audit.json']['answers']['E']['retained_certificate_facts']['single_child_selector_required'] = True
    fresh = current_muon_birth_realization()
    assert fresh['first_missing_operand']['value'] is None
    assert fresh['required_outputs']['psi_star']['value'] is None
    assert not fresh['retained_evidence']['child_birth_audit.json']['answers']['E']['retained_certificate_facts']['single_child_selector_required']


@pytest.mark.parametrize('audit_name', [
    'parent_transition_audit.json', 'child_birth_audit.json',
    'muon_operand_reuse_audit.json',
])
@pytest.mark.parametrize('identity_field', ['starting_head', 'scientific_reference'])
def test_mixed_audit_scientific_identity_is_rejected(
    tmp_path, birth_report, audit_name, identity_field,
):
    folder = tmp_path / ARTIFACT_DIRECTORY
    folder.mkdir(parents=True)
    for name, audit in birth_report['retained_evidence'].items():
        if name == audit_name:
            provenance = audit.get('provenance', audit)
            field = identity_field
            if field == 'starting_head' and 'starting_HEAD' in provenance:
                field = 'starting_HEAD'
            provenance[field] = 'different scientific identity'
        (folder / name).write_text(json.dumps(audit), encoding='utf8')
    with pytest.raises(ValueError, match='different scientific identity'):
        current_muon_birth_realization(tmp_path)


def test_existing_realization_default_report_uses_current_birth_owner():
    from bhsm.interface.ae4_support_loss_classical_realization import (
        inspected_support_loss_realization,
    )

    realization = inspected_support_loss_realization()
    current = realization.report()
    assert current['support_definition']['event'] == EVENT_DEFINITION
    assert current['first_missing_operand']['name'] == FIRST_MISSING_OPERAND
    assert not current['supersession']['old_gap_is_current']
    historical = realization.historical_report()
    assert historical['first_missing_definition']['name'] == SUPERSEDED_GAP
    assert historical['physical_solution'] is False
