"""New outgoing-subspace sensitivity readout of a saved real Dirac transfer.

The completed canonical transfer is consumed without rerunning it. No tail
row, physical pole, missing magnetic jet or new exterior is selected.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import numpy as np


def evaluate(repository, output):
    root,out=Path(repository).resolve(),Path(output).resolve()
    if out.exists():
        raise FileExistsError('preserve previous readouts')
    folder='artifacts/muon_canonical_retarded_energy_response_20261011/run_1'
    receipt_rel=folder+'/result.json'; archive_rel=folder+'/application.npz'
    receipt=json.loads((root/receipt_rel).read_bytes())
    if sha256((root/archive_rel).read_bytes()).hexdigest()!=receipt['archive']['sha256']:
        raise ValueError('saved canonical transfer changed')
    for p,h in receipt['input_hashes'].items():
        if sha256((root/p).read_bytes()).hexdigest()!=h:
            raise ValueError('retained canonical-transfer owner changed: '+p)
    prefix='outgoing_resolution_8_'
    with np.load(root/archive_rel,allow_pickle=False) as saved:
        U=saved[prefix+'canonical_propagator'].copy()
        U4=saved['outgoing_resolution_4_canonical_propagator'].copy()
        R=saved[prefix+'retarded_energy_response'].copy()
        RE=saved[prefix+'retarded_energy_first_jet'].copy()
        frame=saved[prefix+'temporal_unitary_frame'].copy()
        H=saved['outgoing_midpoint_canonical_Hcan'].copy()
        W=saved['outgoing_midpoint_spatial_W'].copy()
        O=saved['outgoing_midpoint_temporal_Omega_tau'].copy()
    rows=[r for r in receipt['records'] if r.get('side')=='outgoing'
          and r.get('max_step_divisor')==8]
    if len(rows)!=1 or U.shape!=(18,18):
        raise ValueError('the complete saved real all-family18 outgoing application is required')
    old=rows[0];tau=old['proper_time_span'];energy=old['energy']
    phase=np.exp(1j*energy*tau)
    V=phase*U;VE=1j*tau*V;VEE=-tau*tau*V
    sv=np.linalg.svd(V,compute_uv=False)
    # This checks a known finite phase derivative only. It is not Gamma_E
    # of the unevaluated full exterior; C_T,E remains an independent jet.
    theta=energy*tau;h=1e-3
    literal=lambda theta:np.exp(1j*theta)*U
    fd=tau*(-literal(theta+2*h)+8*literal(theta+h)
            -8*literal(theta-h)+literal(theta-2*h))/(12*h)
    sigma=np.array([[[0,1],[1,0]],[[0,-1j],[1j,0]],[[1,0],[0,-1]]],complex)/2
    spin=[np.kron(np.eye(9),s) for s in sigma]
    actual_spin_commutators=[float(np.linalg.norm(H@s-s@H)) for s in spin]
    transfer_spin_commutators=[float(np.linalg.norm(U@s-s@U)) for s in spin]
    inverse_norm=float(1/min(sv))
    boundary_gain=dict(min=float(min(sv)),max=float(max(sv)),
        condition=float(max(sv)/min(sv)),inverse_norm=inverse_norm)
    result=dict(
        classification='NEW_ACTUAL_FINITE_OUTGOING_SUBSPACE_SENSITIVITY_FROM_SAVED_REAL_TRANSFER',
        producer_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        input_hashes={receipt_rel:sha256((root/receipt_rel).read_bytes()).hexdigest(),
                      archive_rel:sha256((root/archive_rel).read_bytes()).hexdigest()},
        retained_operator_input_hashes=receipt['input_hashes'],
        actual_fiber_dimension=18,actual_proper_time_span=tau,
        reference_energy_probe=energy,
        energy_scope=old['energy_scope'],
        per_terminal_row_singular_values=sv.tolist(),
        missing_terminal_value_or_E_B_EB_row_gain=boundary_gain,
        row_gain_is_coordinate_sensitivity_not_physical_moment_uncertainty=True,
        invariant_terminal_projector_tangent_gain_bounds=dict(
            Frobenius_lower=float(min(sv)**2),Frobenius_upper=float(max(sv)**2),
            operator_lower=float(min(sv)**2),operator_upper=float(max(sv)**2)),
        invariant_subspace_statement='At fixed real energy with unitary V, the orthogonal projector of the allowed initial trace space is P0=V^dagger P_T V. A transverse terminal tangent dP_T is carried to V^dagger dP_T V with identical Frobenius and operator norms. Stored singular values bound deviations from exact isometry; no P_T or tangent is chosen.',
        projector_tangent_scope='dP_T is Hermitian with P_T dP_T P_T=0 and (I-P_T)dP_T(I-P_T)=0. These real-parameter Grassmann directions omit pure changes of the terminal row/frame basis. Further physical domain constraints are not selected.',
        row_basis_cancellation='For C_T -> S C_T, the parallel derivative S_a C_T contributes S_a C_T V r=0 on a genuine pole. Invertible equation-row scaling cancels from normalized pole slopes. Unit row gain alone therefore proves no physical magnetic sensitivity.',
        physical_projector_or_tangent_produced=False,
        orthogonal_projector_used_as_holomorphic_energy_jet=False,
        nonzero_physical_magnetic_domain_motion_proved=False,
        missing_terminal_B_row_to_known_EB_phase_contact_gain=tau*float(max(sv)),
        missing_terminal_row_to_forced_source_gain=float(np.linalg.norm(R,2)),
        missing_terminal_row_to_forced_source_E_contact_gain=float(np.linalg.norm(RE,2)),
        finite_phase_E_derivative_norm=float(np.linalg.norm(VE,2)),
        finite_phase_EE_derivative_norm=float(np.linalg.norm(VEE,2)),
        finite_phase_E_derivative_five_point_relative_discrepancy=float(np.linalg.norm(fd-VE)/np.linalg.norm(VE)),
        same_saved_transfer_refinement_difference=float(np.linalg.norm(U-U4)),
        canonical_unitarity_defect=float(np.linalg.norm(U.conj().T@U-np.eye(18))),
        temporal_frame_unitarity_defect=float(np.linalg.norm(frame.conj().T@frame-np.eye(18))),
        temporal_connection_norm=float(np.linalg.norm(O)),
        canonical_vs_spatial_connection_identity_defect=float(np.linalg.norm(H-W+1j*O)),
        full_canonical_H_norm=float(np.linalg.norm(H)),
        midpoint_spin_commutator_norms=actual_spin_commutators,
        saved_transfer_spin_commutator_norms=transfer_spin_commutators,
        derivation='Coordinate-level identity only: for V(E)=exp(i E tau)U and Gamma_tail=C_T(E,B)V(E,B), a missing terminal derivative row D contributes D V with the same singular-value gains. Gamma_EB also retains C_T,B V_E; V_B/V_EB and C_T jets are not set to zero.',
        source_derivation='In Gamma=C_i+C_f V, f=b-C_f R, source rows require C_f derivatives too. The saved R_E is the literal finite forcing jet, not a complete outgoing-domain jet.',
        field_specific_boundary_B_or_EB_jet_computed=False,
        actual_terminal_annihilator_or_allowed_subspace_selected=False,
        finite_prefix_is_physical_outgoing_endpoint=False,
        full_angular_or_radial_exterior_convergence_claimed=False,
        unknown_terminal_row_is_free_physical_parameter=False,
        future_tail_scope='The action-owned continuation must produce the future row and its jets after the real coefficients/domain are constructed. Their absence here is an unevaluated application, not permission to choose them.',
        old_empirical_references_reused_as_new_prediction_input=False,
        full_physical_outgoing_derivative_passed=False,
        physical_two_spin_normalization=None,physical_muon_magnetic_moment=None,
        original_Maxwell_or_226_pass_claimed=False,coupled_matching_corrections=0,
        source_profile_transfer_pairing_or_history_campaign_replayed=False,
        uncertainty_scope='Binary64 algebra on saved canonical transfer and its previously recorded finite-step error; no new outward time/exterior or physical-state error bound.')
    out.mkdir(parents=True)
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({k:result[k] for k in ('missing_terminal_value_or_E_B_EB_row_gain',
        'invariant_terminal_projector_tangent_gain_bounds',
        'missing_terminal_row_to_forced_source_gain',
        'missing_terminal_row_to_forced_source_E_contact_gain',
        'finite_phase_E_derivative_five_point_relative_discrepancy',
        'midpoint_spin_commutator_norms','saved_transfer_spin_commutator_norms',
        'temporal_connection_norm')},sort_keys=True))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repository',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();evaluate(a.repository,a.output)
