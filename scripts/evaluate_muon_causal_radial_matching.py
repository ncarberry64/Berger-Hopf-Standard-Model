"""Apply the retained causal convention to the actual scalar matching path."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_causal_radial_matching import (causal_radial_boundary_application,
    causal_radial_soft_path_application,finite_causal_radial_covector)
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve all earlier causal applications')
    out.mkdir(parents=True);pins={};archives={};records=[]
    def read(folder):
        p=ROOT/folder;r=json.loads((p/'result.json').read_bytes());pins.update(r['input_hashes'])
        pins[(p/'result.json').relative_to(ROOT).as_posix()]=sha256((p/'result.json').read_bytes()).hexdigest();return p,r
    def array(folder,name,receipt):
        p=folder/name;h=sha256(p.read_bytes()).hexdigest()
        if h!=receipt['archives'][name]['sha256']:raise RuntimeError('frozen original action changed')
        pins[p.relative_to(ROOT).as_posix()]=h
        return np.load(p,allow_pickle=False)
    tp,tm=read('artifacts/muon_native_radial_overlap_tail_20261011/run_1')
    mp,mm=read('artifacts/muon_native_local_overlap_matching_20261011/run_3')
    pp,pm=read('artifacts/muon_piecewise_euclidean_action_20261011/run_2')
    def save(name,obj):
        arrays={}
        def pack(v,key):
            if isinstance(v,np.ndarray):arrays[key]=v;return dict(array_key=key,shape=list(v.shape))
            if isinstance(v,dict):return{k:pack(a,key+'_'+k)for k,a in v.items()}
            if isinstance(v,(list,tuple)):return[pack(a,key+'_'+str(j))for j,a in enumerate(v)]
            if isinstance(v,np.generic):return pack(v.item(),key)
            if isinstance(v,complex):return dict(real=v.real,imag=v.imag)
            return v
        r=pack(obj,'data');p=out/name;deterministic_archive(p,arrays)
        if p.stat().st_size>10*1024**2:raise ArithmeticError('split all complete arrays')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest());return r
    for side in('incoming','outgoing'):
        a=array(tp,f'{side}_exact_schur_and_tail.npz',tm)
        pencil={k.removeprefix('data_pencil_'):a[k]for k in a.files if k.startswith('data_pencil_')};pencil['At_count']=64
        p=array(tp,f'{side}_poles_and_bypasses.npz',tm);circles=p['data_cluster_circles']
        mrec=next(r for r in mm['records']if r['kind']=='coupled_radial_matching'and r['side']==side)['record']
        br=mrec['calibrated_external_covector_probes'][1]
        args=dict(matched_mass_action=br['matched_internal_and_external_fermion_mass_action'],fixed_Y=br['fixed_Y'],
            kinetic_residue=mrec['coupled_matching']['actual_scalar_kinetic_residue'])
        # The recorded proper cell length is only the finite causal prefix
        # consumed here. It is not declared to be the maximal child history.
        T=next(r['total_proper_clock']for r in pm['records']if r['side']==side and r['temporal_cells']==8)
        ma=array(mp,f'{side}_coupled_scalar_matching.npz',mm)
        ref=ma['data_coupled_matching_same_coordinate_reference_coefficients'];mu2=float(-ref[0,0,0].real/ref[2,0,0].real)
        rates=np.r_[args['matched_mass_action']*np.array([.1,1.,10.]),next(r for r in tm['records']if r['side']==side)['certificate']['omega_start_lower']]
        boundary=causal_radial_boundary_application(pencil,proper_length=T,laplace_rates=rates)
        branches=causal_radial_soft_path_application(pencil,circles,**args,reference_mass_squared=mu2,order=24)
        finite=[finite_causal_radial_covector(pencil,proper_length=T,**args,quadrature_order=q)for q in(6,8)]
        comparisons=[]
        for row in boundary['applications']:
            s=complex(row['laplace_rate']);D=pencil['K']+s*pencil['J']-s*s*pencil['M']
            opposite=pencil['source'].T@np.linalg.solve(D,pencil['source'])
            comparisons.append(dict(laplace_rate=np.array(s),opposite_advanced_radial_pairing=opposite,
                retarded_minus_advanced_trace=np.array(np.trace(row['meromorphic_radial_inverse_action_pairing']-opposite)/4)))
        rec=save(f'{side}_causal_application.npz',dict(causal_boundary=boundary,applied_causal_path=branches,
            finite_causal_covector_applications=finite,opposite_orientation_checks=comparisons))
        norms=dict(proper_numerical_prefix=T,growth_abscissa_numerical=boundary['numerical_growth_abscissa'],
            applied_causal_meromorphic_covector_real=float(branches['applied_retarded_rotation_covector'].real),
            applied_causal_meromorphic_covector_imag=float(branches['applied_retarded_rotation_covector'].imag),
            finite_causal_covector_real=float(finite[-1]['finite_causal_covector'].real),
            finite_causal_order_difference=float(abs(finite[1]['finite_causal_covector']-finite[0]['finite_causal_covector'])),
            original_finite_Gauss_residual_max=float(max(np.max(abs(r['original_Gauss_equation_residual']))for r in boundary['applications'])),
            original_finite_dynamic_residual_max=float(max(np.max(abs(r['original_dynamic_equation_residual']))for r in boundary['applications'])))
        records.append(dict(side=side,archive=f'{side}_causal_application.npz',record=rec,norms=norms))
        print(json.dumps(dict(stage='causal_scalar_matching',side=side,**norms),sort_keys=True),flush=True)
    for p in(Path(__file__),'src/bhsm/interface/muon_causal_radial_matching.py','tests/test_muon_causal_radial_matching.py',
        'src/bhsm/interface/muon_local_normal_action_symbol.py','src/bhsm/interface/muon_parent_maxwell_full_retarded.py',
        'src/bhsm/interface/muon_wick_canonical_inverse.py','scripts/evaluate_muon_reached_trace_action.py'):
        p=Path(p);p=p if p.is_absolute()else ROOT/p;pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in pins.items()):raise RuntimeError('consumed causal owner changed')
    result=dict(classification='EVALUATED_ACTION_OWNED_CAUSAL_RADIAL_MATCHING_PATH_AND_FINITE_ENDPOINT_RETURN',input_hashes=pins,archives=archives,records=records,
        exact_frequency_owner='muon_local_normal_action_symbol.chronological_frequency_polynomial: right variation exp(+i z tau), velocity+i z x',
        causal_owner='muon_parent_maxwell_full_retarded constrained action/Hamilton equations and muon_wick_canonical_inverse zero-before-source/common birth continuation',
        proper_causal_transfer='positive action source -> -C(-i s)^-1; inverse-action Green is its negative; finite canonical endpoint retained',
        causal_rotation='clockwise positive-Lorentz-frequency meromorphic rotation to z=-i s from retarded lower half-plane; Im(s)>0 bypass on actual source-paired roots',
        earlier_positive_imaginary_z_scalar_application_is_advanced_orientation=True,
        trace_orientation_equality_from_action_transpose_is_tested_not_forced=True,
        finite_boundary_application_equals_the_meromorphic_loop=False,
        absolute_Laplace_convergence_below_growth_abscissa_claimed=False,
        physical_native_Feynman_covariance_or_Pauli_identified=False,physical_a_mu=None,physical_g_mu=None,
        error_scope='binary64 frozen action causal semigroup, original Gauss/endpoints and numerical scalar source application. The causal sign is derived from retained equations; matrix production, quadrature/semigroup and maximal-history/quantum-domain errors are not enclosed. No principal value or new Feynman state is selected.')
    p=out/'result.json';p.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256(p.read_bytes()).hexdigest(),archives=len(archives)),sort_keys=True),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    materialize(p.parse_args().output)
