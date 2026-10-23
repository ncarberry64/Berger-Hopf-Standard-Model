"""Execute the actual full18 contour operator/source first germs."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_intrinsic_fermion_wick_application import fermion_wick_application,temporal_contour_gauge_covariance
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
from bhsm.interface.muon_coupled_magnetic_field_variation import corrected_magnetic_first_field_interpolation
from bhsm.interface.muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
from evaluate_muon_reached_trace_action import deterministic_archive
from evaluate_muon_intrinsic_scalar_regulator_correction import source_record


def materialize(output):
    out=Path(output);out=out if out.is_absolute()else ROOT/out
    if out.exists():raise FileExistsError('preserve every earlier contour application')
    source=ROOT/'artifacts/muon_corrected_profile_magnetic_response_20261011/run_1'
    raw=(source/'result.json').read_bytes();receipt=json.loads(raw);refs=dict(receipt['input_hashes'])
    refs[(source/'result.json').relative_to(ROOT).as_posix()]=sha256(raw).hexdigest()
    if receipt['classification']!='EVALUATED_CORRECTED_PROFILE_SAME_BIRTH_LOCAL_MAGNETIC_FULL488_RETARDED_RESPONSE':
        raise ValueError('actual corrected same-birth source required')
    def load(name):
        p=source/name;b=p.read_bytes();r=receipt['array_archives'][name]
        if sha256(b).hexdigest()!=r['sha256']or len(b)!=r['bytes']:raise ValueError('source arrays changed: '+name)
        refs[p.relative_to(ROOT).as_posix()]=r['sha256']
        with np.load(p,allow_pickle=False)as f:return{k:f[k]for k in f.files}
    rows=[];files={};out.mkdir(parents=True)
    for side,folder in (
        ('incoming','artifacts/muon_finite_normal_phase_20261011/incoming_run_1'),
        ('outgoing','artifacts/muon_inherited_finite_normal_phase_20261011/run_1')):
        phase=load_profile_preserving_phase(folder,repository=ROOT);refs.update(phase['input_hashes'])
        primal,phase_arrays,velocity,contacts=[load(side+'_'+x+'.npz')for x in ('primal_and_source','phase','velocity','contacts')]
        sampler=corrected_magnetic_first_field_interpolation(primal,phase_arrays,velocity,contacts)
        L=abs(float(phase['receipt']['span']));x,w=np.polynomial.legendre.leggauss(6)
        times=np.r_[(x+1)*L/4,(x+3)*L/4];weights=np.r_[w,w]*L/4
        for j,u in enumerate(times):
            a=fermion_wick_application(phase,float(u),first_field_sampler=sampler)
            arrays={k:v for k,v in a.items()if isinstance(v,np.ndarray)}
            p=out/(side+'_sample_'+str(j)+'.npz');deterministic_archive(p,arrays)
            if p.stat().st_size>10*1024**2:raise ValueError('complete first germ exceeds public archive cap')
            files[p.name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest(),arrays=sorted(arrays))
            rows.append(dict(side=side,sample=j,response_time=float(u),coordinate_time=a['coordinate_time'],
                quadrature_weight=float(weights[j]),body_identity_residual=a['body_Lorentz_contour_identity_residual'],
                reference_body_difference_norm=float(np.linalg.norm(a['positive_reference_body_difference'])),
                body_tau_first_norm=float(np.linalg.norm(a['continued_body_tau_first'])),
                source_value_norm=float(np.linalg.norm(a['continued_source_coefficients'])),
                source_tau_first_norm=float(np.linalg.norm(a['continued_source_tau_first']))))
    gauge=lepton_unit_trace_gauge_representation()['generators'][3];Q=-1j*gauge
    # Exact Hermiticity follows the retained diagonal hypercharge matrix;
    # no approximate matrix projection is inserted by this diagnostic.
    frame=temporal_contour_gauge_covariance(Q,1.)
    p=out/'temporal_frame.npz';deterministic_archive(p,{k:v for k,v in frame.items()if isinstance(v,np.ndarray)})
    files[p.name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    sources=[source_record(p,s)for p,s in (
        ('src/bhsm/interface/muon_intrinsic_fermion_wick_application.py',['fermion_wick_application','continued_fermion_source_vertices','temporal_contour_gauge_covariance']),
        ('src/bhsm/interface/muon_profile_preserving_phase_sample.py',['profile_preserving_lepton_sample']),
        ('src/bhsm/interface/muon_magnetic_open_lepton_vertex.py',['canonical_open_field_vertices']),
        ('src/bhsm/interface/muon_coupled_magnetic_field_variation.py',['corrected_magnetic_first_field_interpolation']))]
    for r in sources:refs[r['path']]=r['sha256']
    for p in (Path(__file__).relative_to(ROOT).as_posix(),'tests/test_muon_intrinsic_fermion_wick_application.py'):
        refs[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('actual continuation inputs changed')
    result=dict(classification='EVALUATED_ACTUAL_FULL18_FERMION_CONTOUR_OPERATOR_AND_MAGNETIC_SOURCE_FIRST_GERMS',
        input_hashes=refs,array_archives=files,source_records=sources,records=rows,
        operator_identity='D_L=i(derivative_t+Omega_L,t)/N-W; D_L|contour=-A_E, A_E=(derivative_tau-i Omega_L,t)/N+W',
        source_identity='delta A_E=delta Hcan_L at the real anchor; derivative_tau source=-i derivative_t source, including N/R and inherited wall clock',
        angular_domain='full18 body and differential principal coefficients; actual source harmonics1/3 and all8 paired coordinates retained, no source-coordinate heat',
        gauge_covariance='analytic U_E(tau)=U_L(t0-i tau) and inverse; real-time Udot cannot be reused in the contour derivative',
        endpoint_domain='same oriented canonical traces, duals and source moments must be continued; no finite far-face replacement or exterior graph application performed',
        actual_source_charge_inserted_again=False,real_positive_reference_relabelled_as_continued_operator=False,
        statistics_or_P_strat_or_LSZ_or_F2_assigned=False,physical_a_mu=None,physical_g_mu=None,
        error_scope='binary64 exact local chain-rule applications on saved finite coefficient/source interpolants; no analytic-contour radius, domain continuation or physical uncertainty enclosure')
    (out/'result.json').write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return dict(classification=result['classification'],files=len(files),records=rows)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    print(json.dumps(materialize(p.parse_args().output),sort_keys=True))
