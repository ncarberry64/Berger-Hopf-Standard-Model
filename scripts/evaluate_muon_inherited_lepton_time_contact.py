"""Apply corrected inherited wall and proper-time Dirac first-order contact."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_birth_finite_normal_phase import load_finite_normal_endpoint
from bhsm.interface.muon_inherited_intrinsic_lepton_operator import inherited_intrinsic_lepton_operator
from bhsm.interface.muon_native_dirac_hamiltonian import lepton_current_hilbert_representation,fixed_y_higgs_hamiltonian
from bhsm.interface.muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(output,source):
    out=Path(output);out=out if out.is_absolute() else ROOT/out
    src=Path(source);src=src if src.is_absolute() else ROOT/src
    if out.exists():raise FileExistsError('preserve evaluated prior applications')
    r=json.loads((src/'result.json').read_bytes())
    if r['classification']!='EVALUATED_INHERITED_PROFILE_CHILD_CANONICAL_ACTION' or r['completed_steps']!=r['steps']:
        raise ValueError('completed same-action inherited child phase required')
    refs=dict(r['input_hashes'])
    for p,h in refs.items():
        if sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('consumed action changed: '+p)
    b=(src/'application.npz').read_bytes()
    if sha256(b).hexdigest()!=r['numerical_sha256']:raise ValueError('actual phase changed')
    refs[(src/'application.npz').relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
    refs[(src/'result.json').relative_to(ROOT).as_posix()]=sha256((src/'result.json').read_bytes()).hexdigest()
    base=load_finite_normal_endpoint('artifacts/muon_parent_gauge_geometry_correction_20261010/finite_moving_trace_run_1',side='outgoing')
    with np.load(src/'application.npz',allow_pickle=False) as f:saved={k:f[k].copy() for k in f.files}
    angular=retained_full_q_angular_space(ROOT);E=np.asarray(angular['derivative_matrices'])
    alpha=lepton_current_hilbert_representation()['alpha'];generators=lepton_unit_trace_gauge_representation()['generators']
    arrays={};records=[]
    for stage,(raw,t) in enumerate(zip(saved['stage_independent_raw'],saved['stage_coordinate_time'])):
        op=inherited_intrinsic_lepton_operator(raw,float(t),saved['initial_pair'],saved['reference_pair'],base['representation'])
        if not np.allclose(op['wall_independent_plus_inherited_image'],saved['stage_wall_gauge'][stage],rtol=0,atol=4e-16):
            raise ValueError('action and intrinsic wall images differ')
        R,N=op['R4'],op['N'];rate=np.zeros_like(raw);rate[:37]=raw[37:74];rate[98]=raw[99]
        Rdot=op['geometry']['R4']['raw_first_jet']@rate
        # D_spatial is expressed in the fixed unit-S3 frame. The coordinate
        # derivative of its complete wall connection is supplied by the
        # material action, including parent/reference and child motion once.
        Odot=np.einsum('ac,cij->aij',op['total_wall_spatial_connection_coordinate_rate'],generators)
        Hdot=(raw[-4:-2]+1j*raw[-2:])[None]
        M=fixed_y_higgs_hamiltonian(op['H'][None])[0];Mdot=fixed_y_higgs_hamiltonian(Hdot)[0]
        Wdot=-1j*np.einsum('aij,ajk->ik',alpha,Odot)/R-(Rdot/R)*(op['W']-M)+Mdot
        Wtau=Wdot/N
        n0A=op['W']+op['Omega_tau'];kappa=12/(N*N*(r['span']/r['steps'])**2)
        matrices={
            'n0_spatial_factor':op['W'],'n0_temporal_connection':op['Omega_tau'],
            'n0_spatial_proper_time_derivative':Wtau,
            'n0_frozen_weak_square':kappa*np.eye(18)+n0A.conj().T@n0A,
            'n0_reached_time_contact_square':kappa*np.eye(18)+n0A.conj().T@n0A-Wtau,
        }
        odd=-1j*sum(np.kron(E[a],alpha[a]) for a in range(3))/R+np.kron(np.eye(20),op['W'])
        oddtau=1j*sum(np.kron(E[a],alpha[a]) for a in range(3))*Rdot/(N*R*R)+np.kron(np.eye(20),Wtau)
        A=odd+np.kron(np.eye(20),op['Omega_tau'])
        frozen=kappa*np.eye(360)+A.conj().T@A
        matrices.update(odd_n1_n3_spatial_factor=odd,odd_n1_n3_spatial_proper_time_derivative=oddtau,
            odd_n1_n3_frozen_weak_square=frozen,odd_n1_n3_reached_time_contact_square=frozen-oddtau)
        prefix='stage_'+str(stage)
        for name,value in matrices.items():arrays[prefix+'_'+name]=value
        for name in ('W','Omega_tau','H_can','W_raw_first_jet','Omega_tau_raw_first_jet','H_can_raw_first_jet',
                     'wall_independent_plus_inherited_image','total_wall_connection','total_wall_spatial_connection_coordinate_rate'):
            arrays[prefix+'_'+name]=op[name]
        for name,geo in op['geometry'].items():arrays[prefix+'_geometry_'+name+'_raw_first_jet']=geo['raw_first_jet']
        z=dict(stage=stage,coordinate_time=float(t),R4=R,induced_lapse=N,
            R4_coordinate_time_rate=float(Rdot),inherited_wall_profile=op['inherited_wall_profile'].tolist(),
            full18_inherited_W_contact_norm=float(np.linalg.norm(op['W_profile_contact'])),
            full18_W_proper_time_derivative_norm=float(np.linalg.norm(Wtau)),
            full18_W_proper_time_derivative_Hermiticity_defect=float(np.linalg.norm(Wtau-Wtau.conj().T)),
            odd360_spatial_proper_time_derivative_norm=float(np.linalg.norm(oddtau)),
            n0_contact_square_gap=float(np.linalg.eigvalsh(matrices['n0_reached_time_contact_square'])[0]),
            odd360_contact_square_gap=float(np.linalg.eigvalsh(frozen-oddtau)[0]),
            full18_H_can_Hermiticity_defect=float(np.linalg.norm(op['H_can']-op['H_can'].conj().T)),
            intrinsic_wall_reconstruction_defect=op['inherited_trace_residual'])
        records.append(z);print(json.dumps(z,sort_keys=True),flush=True)
    for name in ('muon_inherited_intrinsic_lepton_operator','muon_inherited_wall_lepton_application','muon_native_dirac_hamiltonian',
                 'muon_intrinsic_m4_normal_pullback','muon_birth_inherited_finite_normal_phase'):
        p='src/bhsm/interface/'+name+'.py';refs[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    refs[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    out.mkdir(parents=True);deterministic_archive(out/'application.npz',arrays)
    receipt=dict(classification='EVALUATED_INHERITED_WALL_AND_DIRAC_PROPER_TIME_FIRST_ORDER_CONTACT',
        input_hashes=refs,archive=dict(path='application.npz',bytes=(out/'application.npz').stat().st_size,
            sha256=sha256((out/'application.npz').read_bytes()).hexdigest()),records=records,
        action_identity='D=(partial_tau+Omega_tau)+D_spatial; DdaggerD=−(partial_tau+Omega_tau)^2+D_spatial^2−(partial_tau D_spatial+[Omega_tau,D_spatial])',
        weak_square_contact='A_daggerA already retains−[Omega_tau,D_spatial] and−Omega_tau^2; add only−partial_tau D_spatial, not the commutator a second time',
        current_Gram='unit canonical point fiber I18; orthonormal Haar angular modes Y/sqrt(2pi²)',
        material_connection_embedding_count=1,
        algebraic_At_time_derivative_required_for_reached_contact=False,
        full_coefficient_time_integration_or_error_enclosure_performed=False,
        native_full_domain_relative_completion_external_LSZ_or_Pauli_completed=False,
        error_scope='binary64 actual same-action stage value and complete child raw firstjets; affine parent/reference finite chart and reached time contact only, not a full temporal weak-form error bound or physical formation/cutoff')
    (out/'result.json').write_text(json.dumps(receipt,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return dict(classification=receipt['classification'],archive=receipt['archive'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--source',type=Path,default='artifacts/muon_inherited_finite_normal_phase_20261011/run_1')
    a=p.parse_args();print(json.dumps(materialize(a.output,a.source),sort_keys=True))
