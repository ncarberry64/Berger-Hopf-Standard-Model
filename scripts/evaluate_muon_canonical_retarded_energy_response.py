"""Execute canonical Lorentz energy/current jets on both corrected arms."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_canonical_retarded_energy_response import corrected_phase_retarded_energy_response,static_normal_frame_energy_identity
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase,profile_preserving_lepton_sample
from bhsm.interface.muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
from evaluate_muon_reached_trace_action import deterministic_archive
from evaluate_muon_intrinsic_scalar_regulator_correction import source_record


def materialize(output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve previous retarded energy applications')
    refs={};arrays={};rows=[]
    for folder in ('artifacts/muon_finite_normal_phase_20261011/incoming_run_1','artifacts/muon_inherited_finite_normal_phase_20261011/run_1'):
        phase=load_profile_preserving_phase(folder,repository=ROOT);refs.update(phase['input_hashes'])
        side=phase['receipt']['side'];span=float(phase['receipt']['span']);L=abs(span)
        if phase['receipt']['steps']!=1:raise ValueError('bind the same one-cell corrected field and Green scope')
        midpoint=profile_preserving_lepton_sample(phase,span/2)['operator']
        mass=float(lepton_current_hilbert_representation()['family_Y'][1,1].real*np.linalg.norm(midpoint['H']))
        for resolution in (4,8):
            r=corrected_phase_retarded_energy_response(phase,mass,max_step=L/resolution)
            p=side+'_resolution_'+str(resolution)+'_'
            for k,v in r.items():
                if isinstance(v,np.ndarray):arrays[p+k]=v
            rows.append(dict(side=side,max_step_divisor=resolution,proper_time_span=r['proper_time_span'],energy=r['energy'],
                energy_scope='actual local fixed-Y muon rest-symbol mass probe; no momentum eigenstate/covariance selected',
                retarded_response_norm=float(np.linalg.norm(r['retarded_energy_response'])),
                energy_first_jet_norm=float(np.linalg.norm(r['retarded_energy_first_jet'])),
                canonical_current_unitarity_defect=r['canonical_current_unitarity_defect'],
                temporal_frame_unitarity_defect=r['temporal_frame_unitarity_defect'],integration=r['integration']))
            print(json.dumps(rows[-1],sort_keys=True),flush=True)
        refine={k:float(np.linalg.norm(arrays[side+'_resolution_4_'+k]-arrays[side+'_resolution_8_'+k]))for k in
            ('canonical_propagator','retarded_energy_response','retarded_energy_first_jet','temporal_unitary_frame')}
        for row in rows:
            if row['side']==side:row['same_action_step_refinement_difference']=refine
        # This diagnostic tests the actual consumed numerator, rather
        # than assigning the discrete tent kinetic constant an energy.
        A=midpoint['W']+midpoint['Omega_tau'];kinetic=12/(midpoint['N']**2*L**2)
        P=kinetic*np.eye(18)+A.conj().T@A;G=np.linalg.solve(P,A.conj().T)
        Lor=mass*np.eye(18)-midpoint['H_can']
        arrays[side+'_midpoint_spatial_W']=midpoint['W'];arrays[side+'_midpoint_temporal_Omega_tau']=midpoint['Omega_tau']
        arrays[side+'_midpoint_canonical_Hcan']=midpoint['H_can'];arrays[side+'_retained_tent_factor_Green']=G
        arrays[side+'_Lorentz_inverse_times_retained_tent_Green_difference']=Lor@G-np.eye(18)
        static=static_normal_frame_energy_identity(midpoint['W'],mass,L*midpoint['N'])
        for k,v in static.items():
            if isinstance(v,np.ndarray):arrays[side+'_static_temporal_normal_frame_'+k]=v
        rows.append(dict(side=side,diagnostic='actual operator identity test at midpoint',
            discrete_tent_temporal_kinetic=kinetic,
            Lorentz_inverse_times_native_tent_Green_identity_defect=float(np.linalg.norm(Lor@G-np.eye(18))),
            native_vs_required_temporal_Wick_coefficient_difference=float(np.linalg.norm(midpoint['Omega_tau']+1j*midpoint['Omega_tau'])),
            static_normal_frame_numerator_residual=float(np.linalg.norm(static['numerator_product_difference'])),
            finite_endpoint_remainder_norm=float(np.linalg.norm(static['finite_endpoint_term'])),
            static_normal_frame_identity_not_identification_of_changing_cell=True))
    sources=[source_record(p,s)for p,s in (
        ('src/bhsm/interface/muon_canonical_retarded_energy_response.py',['canonical_retarded_energy_response','corrected_phase_retarded_energy_response','static_normal_frame_energy_identity']),
        ('src/bhsm/interface/muon_profile_preserving_phase_sample.py',['profile_preserving_lepton_sample']),
        ('src/bhsm/interface/muon_primal_intrinsic_lepton_operator.py',['primal_intrinsic_lepton_operator']))]
    for r in sources:refs[r['path']]=r['sha256']
    for p in (Path(__file__).relative_to(ROOT).as_posix(),'tests/test_muon_canonical_retarded_energy_response.py'):refs[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('reached canonical action changed during energy application')
    out.mkdir(parents=True);a=out/'application.npz';deterministic_archive(a,arrays)
    info=dict(path=a.name,bytes=a.stat().st_size,sha256=sha256(a.read_bytes()).hexdigest())
    result=dict(classification='EVALUATED_CORRECTED_CANONICAL_LORENTZ_RETARDED_ENERGY_CURRENT_JETS',input_hashes=refs,source_records=sources,archive=info,records=rows,
        complete18_current_retarded_equation_and_energy_jet_executed=True,
        endpoint_holonomy_and_finite_energy_source_remainder_retained=True,
        state_or_positive_band_or_physical_incoming_mode_selected=False,
        native_tent_factor_not_identified_by_an_energy_substitution=True,
        Lorentz_normal_frame_equation='D_L=i d_tau-Hcan; temporal unitary frame dotT=-Omega_tau T produces W_T=Tdagger W T',
        exact_static_local_symbol_Wick_equation='A_E=i omega+W_T; P_E=omega²+W_T²; G_L=-P_E^-1 A_Edagger at omega=i(E+i0)',
        changing_body_remaining_application='the actual W_T(tau) and source jets/endpoint graph must be analytically transported to the same positive/native contour or retained as two-time loop Green; finite retarded endpoint kernel is not a Feynman/current covariance',
        overlap='local intrinsic-Higgs exchange matches only its fixed-Y scalar continuum sector, photon-induced exchange only its current/VP sector; neither subtraction performed by this energy/current application',
        physical_native_Sigma_or_normalized_soft_Pauli_completed=False,physical_a_mu=None,physical_g_mu=None,
        error_scope='binary DOP853 actual action coefficients, finite-step refinement and algebraic midpoint identity residuals only; no outward time/producer/eigen/domain or physical observable error bound')
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(classification=result['classification'],archive=info),sort_keys=True))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    materialize(p.parse_args().output)
