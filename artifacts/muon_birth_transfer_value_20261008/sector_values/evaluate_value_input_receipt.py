"""Read retained E1 operands and reconstruct their finite geometric snapshot.

This performs no action solve, event search, trajectory, selector construction,
or field-state choice.  The fermion operator cache is inventoried as operators,
never converted into a physical event trace.
"""
from __future__ import annotations

import argparse
import ast
from hashlib import sha256
import json
import math
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
RESET_REPORT = 'artifacts/muon_birth_transfer_value_20261008/retained_reset/run_1/result.json'
STATE_SOURCE = 'artifacts/flagship_integration/BHSM_N12_C2_REFINED_RESET_ROOT_CENTER.npz'
FERMION_BODY = Path('C:/Users/carbe/OneDrive/Documents/CODEX/outputs/bhsm_muon_20260930/fermion_body_20261001')
STARTING_HEAD = '64b51a2cedb7be410251b3fb3c4f942cc148bcc4'
SCIENTIFIC_REFERENCE = '524ed90689bd5923c249bba2e699abf627e703cd'


def file_identity(path):
    path = Path(path)
    content = path.read_bytes()
    return dict(path=str(path.relative_to(ROOT)).replace('\\', '/')
                if path.is_relative_to(ROOT) else str(path).replace('\\', '/'),
                bytes=len(content), sha256=sha256(content).hexdigest())


def producer(path, symbols):
    absolute = ROOT / path if not Path(path).is_absolute() else Path(path)
    syntax = ast.parse(absolute.read_text(encoding='utf-8'))
    functions = {node.name: node for node in ast.walk(syntax)
                 if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    return dict(**file_identity(absolute), symbols={name: dict(
        start_line=functions[name].lineno, end_line=functions[name].end_lineno,
        bounds_verified_by='PYTHON_AST') for name in symbols})


def array_value(array):
    array = np.asarray(array)
    return dict(values=array.tolist(), shape=list(array.shape), dtype=str(array.dtype),
                array_sha256_C_order=sha256(np.ascontiguousarray(array).tobytes()).hexdigest(),
                binary64_hex=[float(value).hex() for value in array.flat])


def array_metadata(array):
    array = np.asarray(array)
    result = dict(shape=list(array.shape), dtype=str(array.dtype),
                  all_finite=bool(np.isfinite(array).all()),
                  array_sha256_C_order=sha256(np.ascontiguousarray(array).tobytes()).hexdigest())
    if np.iscomplexobj(array):
        result['nonzero_entry_count'] = int(np.count_nonzero(array))
        result['frobenius_norm'] = float(np.linalg.norm(array))
    return result


def reconstruct_fields(state, chi):
    """Literal finite evaluation of the retained exact reconstruction equations."""
    state = np.asarray(state, dtype=float)
    q, velocity, multipliers = state[:37], state[37:74], state[74:98]
    ks, js = np.arange(1, 13, dtype=float), np.arange(12, dtype=float)
    ck = np.cos(4 * np.outer(ks, chi))
    sk = np.sin(4 * np.outer(ks, chi))
    cj = np.cos(4 * np.outer(js, chi))
    sj = np.sin(4 * np.outer(js, chi))
    window, window_prime = np.sin(2 * chi)**2, 2 * np.sin(4 * chi)
    u = q[1:13] @ ck
    up = (-4 * ks * q[1:13]) @ sk
    w = window * (q[13:25] @ cj)
    b = window * (q[25:37] @ cj)
    wp = window_prime * (q[13:25] @ cj) + window * ((-4 * js * q[13:25]) @ sj)
    bp_shape = window_prime * (q[25:37] @ cj) + window * ((-4 * js * q[25:37]) @ sj)
    radius0 = (343.0 / 5.0)**(1.0 / 6.0)
    radius = radius0 * math.exp(float(q[0]))
    C = radius * np.exp(u + w)
    A = radius * np.exp(u + b) * np.cos(chi)
    B = radius * np.exp(u - b) * np.sin(chi)
    N = np.exp(multipliers[:12] @ ck)
    beta = np.sin(4 * chi) * (multipliers[12:] @ cj)
    beta_prime = 4 * np.cos(4 * chi) * (multipliers[12:] @ cj) + np.sin(4 * chi) * ((-4 * js * multipliers[12:]) @ sj)
    cp, ap, bp = up + wp, up + bp_shape - np.tan(chi), up - bp_shape + 1 / np.tan(chi)
    lc = velocity[0] + velocity[1:13] @ ck + window * (velocity[13:25] @ cj)
    la = velocity[0] + velocity[1:13] @ ck + window * (velocity[25:37] @ cj)
    lb = velocity[0] + velocity[1:13] @ ck - window * (velocity[25:37] @ cj)
    f_normal = -beta / N
    x_spatial = 1 / C**2 + 3 * np.cos(chi)**2 / A**2 + 3 * np.sin(chi)**2 / B**2
    sigma = -.5 + 2 * chi / np.pi - np.sin(4 * chi) / (2 * np.pi)
    S = A*A + B*B
    return dict(radius_scale=np.full_like(chi, radius), C=C, A=A, B=B,
                lapse_N=N, shift_beta_chi=beta, shift_beta_prime_chi=beta_prime,
                eta_f=chi.copy(), eta_f_prime=np.ones_like(chi), eta_f_normal=f_normal,
                eta_X=x_spatial-f_normal*f_normal, response_sigma=sigma,
                localization_L_sigma=1-4*sigma*sigma,
                adm_Hc=(lc-beta*cp-beta_prime)/N,
                adm_Ha=(la-beta*ap)/N, adm_Hb=(lb-beta*bp)/N,
                mechanical_connection_lambda=A*A/S,
                diagonal_quotient_fiber_radius=np.sqrt(S),
                diagonal_quotient_base_radius=A*B/np.sqrt(S))


def receipt():
    report = json.loads((ROOT / RESET_REPORT).read_text(encoding='utf-8'))
    if report['starting_head'] != STARTING_HEAD or report['scientific_reference'] != SCIENTIFIC_REFERENCE:
        raise ValueError('reset receipt has a different scientific identity')
    if report['selected_incoming_event_index'] != 23:
        raise ValueError('incoming E1 branch23 is not bound')
    with np.load(ROOT / STATE_SOURCE, allow_pickle=False) as source:
        retained = np.array(source['state'], copy=True)
        state_arrays = {name: array_metadata(source[name]) for name in source.files}
    states = dict(incoming_C1_E1=retained[98:196].copy(), outgoing_C2=retained[:98].copy())
    for side, key in [('incoming_C1_E1', 'Phi_P_minus_geometry'), ('outgoing_C2', 'Phi_mu_plus_geometry')]:
        if not np.array_equal(states[side], np.asarray(report['retained_state_values'][key]['values'])):
            raise ValueError('retained state differs from reset report at ' + side)
    nodes, weights = np.polynomial.legendre.leggauss(96)
    chi, quadrature = (nodes+1)*np.pi/8, weights*np.pi/8
    fields = {side: {name: array_value(value) for name, value in reconstruct_fields(state, chi).items()}
              for side, state in states.items()}
    boundary = {side: {name: float(value[0]) for name, value in reconstruct_fields(state, np.array([np.pi/4])).items()}
                for side, state in states.items()}
    with np.load(FERMION_BODY / 'fermion_body.npz', allow_pickle=False) as body:
        body_arrays = {name: array_metadata(body[name]) for name in body.files}
        currents = np.array(body['B_H_photon_source_unit_generators_Q_minus_one'], copy=True)
        operator_dependency = dict(
            derivative_operator='B_H,a=-H_a=diag(-Q*J_a,+Q*J_a)',
            per_operator_frobenius_norm=[float(np.linalg.norm(matrix)) for matrix in currents],
            per_operator_nonzero_entry_count=[int(np.count_nonzero(matrix)) for matrix in currents],
            all_eight_current_derivatives_nonzero=bool(all(np.count_nonzero(matrix) for matrix in currents)),
            meaning='Retained nonzero quadratic-current operators depend on fermion coefficient values. Operator nonzero is not a claim that a particular unprovided physical trace is nonzero.',
            hypothetical_state_selected=False)
    source_refs = [
        producer('src/bhsm/interface/aether_sobolev_galerkin_pencil_lift_v15_81.py', ['dimensions', 'generalized_lagrangian']),
        producer('src/bhsm/interface/aether_n3_exact_full_local_action_jet_v17_60.py', ['exact_full_action_jet_at_state']),
        producer('src/bhsm/interface/aether_exact_radial_schur_lift_v15_83.py', ['identity_response_localization']),
        producer('src/bhsm/interface/aether_diagonal_sp1_m4_attachment_v15_50.py', ['diagonal_quotient_geometry', 'attachment_states', 'action_ownership_ledger']),
        producer('src/bhsm/interface/action_extension_global_spin_reset_ae2.py', ['transmit_trace', 'opposite_normal_green_residual', 'action_definition']),
        producer('src/bhsm/interface/ae4_current_c2_physical_enclosure_state_integration.py', ['transport_composition_contract', 'reconciled_identification_rows']),
        producer('src/bhsm/interface/ae4_c2_stratified_event_flux_assembly.py', ['assemble_stratified_direct_sum', 'solve_retarded_event_kkt', 'canonical_noether_flux_balance']),
        producer('src/bhsm/interface/completion/foundational_dirac_spin_glue_v14_45.py', ['foundational_action_payload', 'zero_mode_pullback_payload']),
        producer('src/bhsm/interface/aether_n3_zero_background_calderon_closure_v17_97.py', ['zero_background_calderon_closure']),
        producer('src/bhsm/interface/aether_hybrid_standard_model_bundle_v15_53.py', ['hybrid_bundle_gluing']),
        producer('src/bhsm/interface/ae4_current_c2_factorized_hs_calderon.py', ['factorized_product_dirac_hs_weyl_jet', 'direct_composition_hs_weyl_value']),
        producer(FERMION_BODY / 'fermion_body.py', ['fermion_body_data', 'photon_source_generators', 'prefix_propagators', 'feynman_kernel']),
    ]
    return dict(
        classification='EVALUATED_RETAINED_E1_GEOMETRIC_FIELD_VALUES_WITH_CONCRETE_FERMION_TRACE_INPUT_STOP',
        starting_head=STARTING_HEAD, scientific_reference=SCIENTIFIC_REFERENCE,
        event_binding=dict(common_event='E1', incoming='C1 branch23 at E1^-', outgoing='C2 branch24 at E1^+',
                           original_state_incoming_slice=[98,196], original_state_outgoing_slice=[0,98],
                           finite_time_displacement=0, current_parent_step1222_extrapolated=False),
        input_identities=[file_identity(ROOT/STATE_SOURCE), file_identity(ROOT/RESET_REPORT),
                          file_identity(FERMION_BODY/'fermion_body.npz'), file_identity(FERMION_BODY/'actual_data_checks.json')],
        source_refs=source_refs, retained_state_array_metadata=state_arrays,
        retained_state_layout=dict(
            state_dimension=98, q=dict(indices_zero_based_half_open=[0,37], scale_q0=[0,1],
                                      mean_warp_u1_to_u12=[1,13], radial_warp_w0_to_w11=[13,25], anisotropy_b0_to_b11=[25,37]),
            velocity=dict(indices_zero_based_half_open=[37,74], corresponding_time_derivatives_of_q=True),
            lapse_shift_multipliers=dict(indices_zero_based_half_open=[74,98], log_lapse_n1_to_n12=[74,86], shift_b0_to_b11=[86,98]),
            independent_eta_coefficients_in_q=False, eta_is_fixed_monotone_quotient_gauge='f=chi',
            gauge_fermion_ghost_HS_amplitudes_encoded_in_98_vector=False),
        retained_state_values={side:array_value(state) for side,state in states.items()},
        reconstruction_equations=dict(
            radial_coordinate='0<=chi<=pi/4; rho=2chi; no time offset',
            R='R0 exp(q0), R0=(343/5)^(1/6), retained geometric action units',
            u='sum_(k=1..12) q[k] cos(4k chi)',
            w='sin^2(2chi) sum_(j=0..11) q[13+j] cos(4j chi)',
            b='sin^2(2chi) sum_(j=0..11) q[25+j] cos(4j chi)',
            geometry='C=R exp(u+w); A=R exp(u+b) cos(chi); B=R exp(u-b) sin(chi)',
            lapse='N=exp(sum_(k=1..12) m[k-1] cos(4k chi))',
            shift='beta=sin(4chi) sum_(j=0..11) m[12+j] cos(4j chi)',
            eta='f=chi; f_prime=1; f_normal=-beta/N; eta=(cos(chi)u_S3,sin(chi)v_S3)',
            eta_invariant='X_eta=C^-2+3cos^2(chi)/A^2+3sin^2(chi)/B^2-(beta/N)^2',
            response='sigma=-1/2+2chi/pi-sin(4chi)/(2pi); L_sigma=1-4sigma^2',
            mechanical_connection='omega=lambda theta_u+(1-lambda)theta_v; lambda=A^2/(A^2+B^2)',
            physical_independent_SM_gauge_connection='Not supplied by mechanical coframe coefficients alone'),
        fresh_geometric_snapshot=dict(
            status='EVALUATED_RETAINED_QUOTIENT_GEOMETRY_AT_BINARY64_PROOF_CENTER',
            chi=array_value(chi), quadrature_weights=array_value(quadrature), fields=fields,
            boundary_chi_pi_over_four=boundary,
            positive_geometry_and_lapse=all(np.all(np.asarray(record[name]['values'])>0)
                                            for record in fields.values() for name in ['A','B','C','lapse_N']),
            eta_profile_is_gauge_fixed_not_new_shape_solve=True,
            physical_full_field_stationary_background_claimed=False,
            error_scope='Binary64 evaluation of unchanged finite reconstruction formulas at the retained center and Gauss96 nodes. No new residual enclosure, continuum error bound, or physical field-state inference.'),
        geometric_reset_values=dict(
            status='EVALUATED_SAME_EVENT_RETAINED_57_ROW_PRODUCER',
            reset_report=RESET_REPORT, selected_incoming_event_index=report['selected_incoming_event_index'],
            residual_l2_norm=report['residual_l2_norm'], residual_max_abs=report['residual_max_abs'],
            residual_groups=report['residual_groups'], raw_geometric_traces=report['raw_geometric_traces'],
            raw_attachment_trace=report['raw_attachment_trace'], raw_canonical_momentum=report['raw_canonical_momentum'],
            full_field_matching_claimed=False),
        sector_value_inventory=[
            dict(sector='geometry_eta_sigma', status='EVALUATED_RETAINED_GEOMETRIC_STATE_AND_RESET',
                 field_values='q37,v37,m24, reconstructed C,A,B,N,beta,f=chi,sigma and geometric canonical momentum',
                 complete_interacting_conormal_dynamicflux_Noether_contact_values=False),
            dict(sector='gauge_transverse', status='UNEVALUATED_ACTUAL_E1_FIELD_AMPLITUDES',
                 known='EH-owned mechanical connection coefficient lambda and retained current/Weyl operator matrices',
                 inactive=False, zero_background_at_actual_E1_proved=False),
            dict(sector='gauge_constraint', status='UNEVALUATED_ACTUAL_E1_FIELD_AMPLITUDES',
                 known='Assembled AE4 relative domain and constrained operator prescription',
                 inactive=False, zero_background_at_actual_E1_proved=False),
            dict(sector='BRST_ghost', status='UNEVALUATED_ACTUAL_E1_FIELD_VALUES',
                 known='Domain gluing, quotient and matched-operator cancellation identity',
                 inactive=False, physical_inactivity_at_actual_E1_proved=False),
            dict(sector='fermion_family', status='UNEVALUATED_INCOMING_EVENT_TRACE_VALUE',
                 known='Muon slot1 mode(5,2), frozen rank1 projector, U_R, eta normal pullback, finite-body Dirac/current operators',
                 required_value='g_F^-=Gamma0_E1^-(Psi_C1)', inactive=False,
                 local_operator_nonzero_dependency=operator_dependency),
            dict(sector='HS_scalar', status='UNEVALUATED_ACTUAL_E1_SOURCE_AND_FIELD_VALUES',
                 known='Assembled scalar graph and factorized HS consumer with explicit source_profile input',
                 inactive=False, physical_inactivity_at_actual_E1_proved=False)],
        fermion_body_inventory=dict(
            status='EVALUATED_RETAINED_OPERATOR_ARRAY_METADATA_ONLY', arrays=body_arrays,
            contains_fermion_state_coefficients=False, contains_incoming_E1_fermion_trace=False,
            source_scope='47 midpoint finite-core geometry segments and parameterized 20x20 LR body, not one-sided E1 matter data',
            saved_operator_checks=json.loads((FERMION_BODY/'actual_data_checks.json').read_text(encoding='utf-8')),
            saved_checks_reexecuted=False, physical_matching_residual_inferred=False),
        concrete_first_missing_input=dict(
            label='UNEVALUATED', operand='g_F^-=Gamma0_E1^-(Psi_C1)',
            value=None, one_first_stop_in_dependency_order=True,
            producer='No attached current C1/E1 numerical producer emits fermion trace coefficients in the reviewed retained state or fermion body arrays.',
            immediate_consumer='action_extension_global_spin_reset_ae2.transmit_trace(event_trace,reset_lift)',
            next_consumer='ae4_current_c2_physical_enclosure_state_integration.transport_composition_contract: Psi_mu^+=T_enc,mu Psi_P^-',
            nonzero_dependency='Fermion normal Green pairing needs psi_event and phi_event; retained B_H,a current matrices are nonzero, so operator geometry cannot determine their quadratic contractions without state coefficients.',
            normalization_does_not_supply_value='u0=N_eta J^-1/2 sin(f_eta) and integral J|u0|^2=1 fix the radial pullback. Psi5=u0 psi4 still requires tangential psi4/C1 event coefficients.',
            common_frame_does_not_supply_value='U_R=I up to common spin/gauge frame is an operator identity, not a fermion trace.',
            domain_semantics_or_family_selector_gap=False,
            downstream_conditional_dependencies='Other active field values and their mixed blocks must share this actual event/domain before full canonical, conormal, dynamic-flux, Noether and contact contractions can be evaluated. They are not presented as separate first stops.'),
        downstream_value_consumers=dict(
            green_form='psi_event^dagger J_e phi_event + (U_R psi_event)^dagger[-U_R J_e U_R^dagger](U_R phi_event)',
            event_canonical='H_pp q+H_pc c+C^dagger lambda+J=0; H_cp q+H_cc^R c=0; Cq=d',
            event_Noether='2 Re <Tq,Pi_parent+Pi_child_return+J+C^dagger lambda>',
            actual_event_trace_and_sector_tractions_supplied=False,
            full_physical_conormal_value=None, full_physical_canonical_value=None,
            full_physical_dynamicflux_value=None, full_physical_Noether_value=None,
            full_physical_contact_value=None,
            independent_fermion_surface_action='S_Sigma,F,AE2=0 is owned internal-glue density; it does not set bulk fermion trace/current or all contact jets to zero.'),
        prior_zero_background_scope=dict(
            status='DERIVED_SELECTED_CLASSICAL_BACKGROUND_HOMOGENEOUS_MATCH',
            producer='aether_n3_zero_background_calderon_closure_v17_97.zero_background_calderon_closure',
            exact_scope='It constructs four zero classical trace/flux arrays for the selected reconstructed background. Its provenance uses static v15.50 action_ownership_ledger and v15.53 hybrid_bundle_gluing; neither binds that zero-field choice to the retained current branch23/E1 pair.',
            event_identity_binding_to_current_branch23_E1_and_branch24_muon=False,
            proves_inactivity_of_current_interacting_muon_birth_field=False,
            zero_classical_background_does_not_erase_determinant_or_current_operator=True),
        execution=dict(fresh_geometric_snapshots=2, action_evaluations=0, trajectories=0,
                       root_solves=0, eigenvector_selections=0, numerical_controls=0,
                       campaigns=0, external_body_metadata_reads=1,
                       physical_fermion_trace_chosen=False, zero_field_assumption_inserted=False),
        runtime=dict(python=sys.version.split()[0], numpy=np.__version__),
        physical_transfer_conjunction_passed=False, physical_mode_psi=None, physical_xi=None,
        physical_seven_port_source=None, physical_stationary_KKT_base=None)


def evaluate(output):
    value = receipt()
    content = (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)+'\n').encode('utf-8')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(content)
    print(json.dumps(dict(path=str(output), bytes=len(content), sha256=sha256(content).hexdigest(),
                         first_missing=value['concrete_first_missing_input']['operand'],
                         reset_residual_l2_norm=value['geometric_reset_values']['residual_l2_norm'],
                         boundary=value['fresh_geometric_snapshot']['boundary_chi_pi_over_four']), sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    evaluate(parser.parse_args().out)
