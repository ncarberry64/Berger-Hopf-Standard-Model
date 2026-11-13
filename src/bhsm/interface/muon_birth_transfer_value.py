"""Value-level E1 reset packet with one explicit unavailable matter trace.

The geometric reset producer is evaluated, not replaced by an audit of its
dimensions. Physical full-field promotion remains separate from that result.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path

import numpy as np

from .muon_birth_reset_evaluation import ROOT, evaluate_reset_values

STARTING_HEAD = '64b51a2cedb7be410251b3fb3c4f942cc148bcc4'
SCIENTIFIC_REFERENCE = '524ed90689bd5923c249bba2e699abf627e703cd'
ARTIFACT_DIRECTORY = 'artifacts/muon_birth_transfer_value_20261008'
FIRST_UNAVAILABLE_VALUE = 'INCOMING_C1_E1_FERMION_TRACE'


def _check_identity(record):
    if (record.get('starting_head') != STARTING_HEAD
            or record.get('scientific_reference') != SCIENTIFIC_REFERENCE):
        raise ValueError('value evidence has a different scientific starting identity')


@dataclass(frozen=True)
class MuonBirthTransferValue:
    """Actual geometric values and incomplete physical transfer operands."""
    reset_values: dict
    transport_inputs: dict
    sector_values: dict

    def __post_init__(self):
        for name in ('reset_values', 'transport_inputs', 'sector_values'):
            object.__setattr__(self, name, deepcopy(getattr(self, name)))
        self._validate()

    def _validate(self):
        for name in ('reset_values', 'transport_inputs', 'sector_values'):
            _check_identity(getattr(self, name))
        reset = self.reset_values
        rows = np.asarray(reset['residual_vector'], dtype=float)
        if rows.shape != (57,) or not np.all(np.isfinite(rows)):
            raise ValueError('all actual finite 57 reset rows are required')
        lines = reset['actual_ordered_lines']
        if (lines['incoming_C1_E1']['index'], lines['outgoing_C2']['index']) != (23, 24):
            raise ValueError('the retained forward incoming23/outgoing24 pair is required')
        missing = self.transport_inputs['first_unavailable_numerical_operand']
        if missing['id'] != FIRST_UNAVAILABLE_VALUE or missing['incoming_value'] is not None:
            raise ValueError('this evaluated partial packet records the unavailable incoming fermion trace')

    def report(self):
        self._validate()
        reset = self.reset_values
        transport = self.transport_inputs
        sector = self.sector_values
        states = reset['retained_state_values']
        binding = dict(event='E1', incoming_branch=23, outgoing_branch=24,
                       incoming_binary64_hex=states['Phi_P_minus_geometry']['binary64_hex'],
                       outgoing_binary64_hex=states['Phi_mu_plus_geometry']['binary64_hex'],
                       normalization=states['normalization_coordinates']['binary64_hex'],
                       weights=states['state_weights']['binary64_hex'],
                       quadrature_points=96, order=12)
        identity = sha256(json.dumps(binding, sort_keys=True).encode()).hexdigest()
        unknown = dict(status='UNEVALUATED__FIRST_INCOMING_FERMION_TRACE_NOT_SUPPLIED', value=None)
        return deepcopy(dict(
            classification='RETAINED_GEOMETRIC_BIRTH_RESET_VALUES_EVALUATED__INCOMING_C1_FERMION_TRACE_UNAVAILABLE',
            starting_head=STARTING_HEAD, scientific_reference=SCIENTIFIC_REFERENCE,
            target='I_PHYS_MUON_BIRTH_TRANSFER_VALUE',
            physical_muon_birth_transfer_identified=False,
            support_definition='BRANCH_REALIZATION_TRANSFER_EVENT__FROZEN',
            cutoff_rule='Sigma_star^mu=Sigma_(P->mu)__MUON_CHILD_PLUS_SIDE__FROZEN',
            Phi_P_minus=dict(geometry=states['Phi_P_minus_geometry'],
                             field_blocks=reset['geometry_field_blocks']['incoming_C1_E1'],
                             incoming_fermion_trace=None,
                             complete_interacting_full_field_state=False),
            Phi_mu_plus=dict(geometry=states['Phi_mu_plus_geometry'],
                             field_blocks=reset['geometry_field_blocks']['outgoing_C2'],
                             muon_label=dict(sector='charged_lepton', slot=1, mode=[5,2]),
                             transported_fermion_trace=None,
                             complete_interacting_full_field_state=False),
            Sigma_P_to_mu=dict(retained_event='E1=C_*', outgoing_child='C2=E_*',
                               numerical_geometric_incidence_evaluated=True,
                               physical_full_field_identification_evaluated=False,
                               one_sided_values_same_event=True, finite_time_offset_used=False),
            common_domain_identity=dict(value=identity, scope='RETAINED_N12_RESET_POINT_AND_CHART_ONLY',
                                        physical_full_field_domain_identity=None),
            common_domain=dict(
                quadrature='order12/96-point retained chi rule on [0,pi/4]',
                clock='One algebraic E1 event incidence; no absolute physical birth time/lifetime inferred',
                orientation=reset['orientation'],
                geometric_trace_pullback='Retained T q and attachment maps, with their fixed normalization coordinates',
                fermionic_transmission_graph='Gamma0_child=U_R Gamma0_event; Gamma1_child=-U_R Gamma1_event',
                fermionic_graph_value_at_E1=None, full_field_pairing=None,
                arbitrary_right_inverse_used=False),
            active_strata=None,
            reset_residual=reset['residual_vector'],
            reset_residual_norm_or_component_enclosures=dict(
                l2_norm=reset['residual_l2_norm'], max_abs=reset['residual_max_abs'],
                component_enclosures=None, scope=reset['error_scope']),
            reset_groups=reset['residual_groups'],
            trace_matching=dict(raw_geometry=reset['raw_geometric_traces'],
                                raw_attachment=reset['raw_attachment_trace'],
                                normalized_4=reset['residual_groups']['normalized_trace_attachment_4'],
                                whitening=reset['boundary_whitening_matrix'],
                                full_field_trace_matching=None),
            canonical_matching=dict(geometry=reset['raw_canonical_momentum'],
                                    full_field_canonical_matching=None),
            conormal_interface_matching=unknown,
            dynamic_flux_matching=unknown,
            noether_hamiltonian_balance=dict(
                geometric_energy_rows=dict(event=reset['residual_groups']['event_canonical_energy_constraint'],
                                           child=reset['residual_groups']['child_canonical_energy_constraint']),
                full_parent_event_child_balance=None,
                source_and_contacts=None, omitted_sectors_set_zero=False),
            muon_projector=transport['muon_projector_numerical_value'],
            transported_muon_state=None,
            full_field_active_sector_ledger=sector,
            branch23_noncontinuation_evidence=dict(
                retained_orientation_source='artifacts/flagship_integration/BHSM_N12_FINITE_TERMINAL_ORIENTATION_CERTIFICATE.json',
                selected_line_evaluated=reset['actual_ordered_lines']['incoming_C1_E1'],
                retained_local_regular_noncontinuation=True,
                complete_interacting_transfer_claimed=False),
            branch24_child_realization_evidence=dict(
                selected_line_evaluated=reset['actual_ordered_lines']['outgoing_C2'],
                geometric_reset_values=reset['classification'],
                muon_full_field_realization_evaluated=False),
            positive_duration_child_certificate=dict(
                source='artifacts/flagship_integration/BHSM_N12_FINITE_TERMINAL_TWO_SIDED_FORWARD_INTERFACE.json',
                scope='Retained local positive-duration outgoing branch24 C2 existence at the two-sided forward event; not a full interacting muon-value continuation certificate',
                historical_direct_checkpoint='artifacts/n12_direct_checkpoint/BHSM_N12_COMPLETE_PERSISTENT_CHILD_CERTIFICATE.json',
                direct_checkpoint_is_current_outgoing_C2_certificate=False,
                retained_component_certificate=True, new_continuation_solve=False),
            first_unavailable_numerical_operand=transport['first_unavailable_numerical_operand'],
            energy_matching=dict(F_E_mu=None, Delta_imp_bulk=None,
                same_event_preserved=True, surface_moved=False,
                equation='<psi_mu^+,(R_mu^+-H_event,drive)psi_mu^+>',
                discrepancy='<psi_mu^+,(H_impedance-H_bulk,constrained)psi_mu^+>',
                geometric_E_can_substituted=False,
                tangential_matter_trace_is_mechanical_formation_mode=False),
            downstream={name:deepcopy(unknown) for name in (
                'psi_star','full_inertia_normalization','xi_psi','b_psi_seven','physical_KKT_base',
                'L_etaeta','R_eta','S_eta_s','R_eta_s','R_s','L_ss','h_psi','delta_psi','z_psi',
                'r','i','total_v_J_jets','c','AE4_heat','relative_zeta_eta','R_ind',
                'native_photon_response','paired_e_mu_heat','signed_Pauli','a_mu','g_mu')},
            retained_geometric_evaluation=reset,
            retained_transport_inputs=transport,
            claim_statuses=dict(
                ADOPTED_OWNER_DEFINITION='Previously adopted branch transfer and child-birth cutoff remain frozen',
                EVALUATED='Actual retained E1/C2 vectors, all57geometric reset rows, raw traces/momenta, supplied existing projector idempotence and same-event geometry samples',
                DERIVED='Existing action/transport laws are reused; no new semantics or family theorem',
                RETAINED_CERTIFIED='Existing local branch orientation, reset root and positive-duration certificates',
                CONTROL_ONLY='Prior numerical controls are not rerun or used as states',
                UNEVALUATED='Actual incoming C1 fermion trace, nonzero muon transport, full-field balance, mechanical birth energy/KKT/native values',
                OWNER_DEFINITION_GAP='None reopened; the first stop is a concrete unavailable numerical trace'),
            error_scope=reset['error_scope'],
        ))


def evaluate_muon_birth_transfer_value(repository: Path | str = ROOT):
    """Evaluate the actual reset; attach the reviewed numerical input receipts."""
    repository = Path(repository)
    folder = repository / ARTIFACT_DIRECTORY
    transport = json.loads((folder/'muon_transport/numerical_input_receipt.json').read_text(encoding='utf8'))
    sector = json.loads((folder/'sector_values/value_input_receipt.json').read_text(encoding='utf8'))
    return MuonBirthTransferValue(evaluate_reset_values(repository), transport, sector)
