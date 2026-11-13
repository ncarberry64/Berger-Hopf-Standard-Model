"""Bind the real positive-coframe eta covector on saved full1920 trial germs.

No D5/action/profile/history computation is repeated. The exact local
contact is applied to saved formal A0 and its owned time first, followed
by the geometric density isometry on both input and output. The real
positive-coframe/same-covector premise is explicit; full AE4 grade/domain
and physical energy conversion remain unclaimed.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
PRIMARY='artifacts/muon_real_coupled_open_operator_20261016/source_first_run_1'


def run(repository,insertion_folder,output):
    root,folder,out=map(lambda p:Path(p).resolve(),(repository,insertion_folder,output));out.mkdir(parents=True,exist_ok=False)
    producer=Path(__file__).read_bytes();(out/'executed_producer.py').write_bytes(producer);pins={}
    def pin(p):
        p=Path(p);p=p if p.is_absolute()else root/p;k=p.relative_to(root).as_posix()if p.is_relative_to(root)else str(p);pins[k]=sha256(p.read_bytes()).hexdigest();return p
    def read(p):
        p=pin(p)
        if p.suffix=='.json':return json.loads(p.read_bytes())
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    def scaled(a,b):return float(np.max(abs(a-b)/np.maximum(1,np.maximum(abs(a),abs(b))),initial=0))
    sys.path.insert(0,str(root/'src'))
    from bhsm.interface.muon_real_positive_d5_covector_binding import real_positive_d5_covector_binding
    from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    primary_meta=read(PRIMARY+'/result.json');source=read(PRIMARY+'/application.npz')
    if pins[PRIMARY+'/result.json']!='d15def102e329c38f35b62c137d8398aa72eeda626924498a426246d66c88df1'or pins[PRIMARY+'/application.npz']!='7da8ddd5fa4bda397aa6a2d50e845338a3ef92fb3f0e837a5a6d0d166915e177':raise ValueError('Exact saved real source-first germs required')
    im=read(folder/'result.json')
    if sha256(pin(folder/'executed_producer.py').read_bytes()).hexdigest()!='4a9ea459bb95a3f470562098c9d82509c982677997542f86ed3626f968e9ded3':raise ValueError('Exact reviewed full1920 recovery source required')
    if '7da8ddd5fa4bda397aa6a2d50e845338a3ef92fb3f0e837a5a6d0d166915e177'not in im['input_and_source_sha256'].values():raise ValueError('The saved A0 recovery must consume the identical source-first archive')
    full=full_d5_localized_lepton_trace();arrays={};records=[]
    for side in ('incoming','outgoing'):
        c={k[len(side+'_input_'):]:v for k,v in source.items()if k.startswith(side+'_input_')};c.pop('raw');c.pop('rawtime')
        geo=read(folder/(side+'_saved_geometry.npz'))
        for k,v in c.items():
            if side+'_c_'+k in geo and not np.array_equal(v,geo[side+'_c_'+k]):raise ValueError('No source/clock coefficient splice: '+k)
        branches={b:real_positive_d5_covector_binding(c,gamma=full['gamma5D_'+b],sheet_orientation=1)for b in ('particle','conjugate')}
        a=branches['particle'];delta,dx=a['delta_scalar_body'],a['delta_scalar_body_first'][0]
        mu,mux=a['fermion_geometric_density'],a['fermion_geometric_density_first'][0];s,sx=a['input_output_density_isometry'],a['input_output_density_isometry_first'][0]
        for name in ('delta_scalar_body','delta_scalar_body_first','f_timelike_derivative','fermion_geometric_density','fermion_geometric_density_first','input_output_density_isometry','input_output_density_isometry_first'):
            arrays[side+'_'+name]=a[name]
        N,C,R,z=(c[k]for k in ('lapse','radial_coframe','radius','coordinate_shift'))
        Nrad,Crad,Rrad=(c[k]for k in ('lapse_log_radial','radial_coframe_log_radial','radius_log_radial'))
        h4_expected=(Nrad+3*Rrad)/(2*C)
        density_log_time=(c['radial_coframe_first'][0]/C+3*c['radius_first'][0]/R-z*(Crad+3*Rrad))/(2*N)
        h0_after=c['geometric_time_contact']-density_log_time
        h0_expected=-c['coordinate_shift_radial']/(2*N)
        arrays[side+'_reduced_time_halfdiv']=h0_after
        arrays[side+'_reduced_radial_halfdiv']=(Nrad-Crad)/(2*C)
        geo_checks=dict(radial_halfdiv_scaled=scaled(c['geometric_radial_contact'],h4_expected),time_density_isometry_halfdiv_scaled=scaled(h0_after,h0_expected))
        for eps in (-1,1):
            tag=f'{side}_eta{eps}';name=tag+'_compact_application.npz';saved=read(folder/name)
            receipt=im['archives'][name];expected=receipt['sha256']if isinstance(receipt,dict)else receipt
            if sha256((folder/name).read_bytes()).hexdigest()!=expected:raise ValueError('Saved full1920 recovery changed')
            key=tag+'_recovered_';v,vx=saved[key+'value'],saved[key+'value_time'];A,Ax=saved[key+'A0'],saved[key+'A0_time']
            if v.shape!=(4,3,2,4,16,5,3)or A.shape!=v.shape or vx.shape!=v.shape or Ax.shape!=v.shape:raise ValueError('All3 families, both branches, Spin4,SM16,h5 and3 declared trials required')
            timescale=lambda b:b[:4].reshape((4,)+(1,)*(v.ndim-1))
            patched=A+timescale(delta)*v;patchedx=Ax+timescale(dx)*v+timescale(delta)*vx
            chi=timescale(s)*v;chix=timescale(sx)*v+timescale(s)*vx
            acted=timescale(s)*patched;actedx=timescale(sx)*patched+timescale(s)*patchedx
            # Exact input/output isometry from mu=N*C*R^3 to the N-weighted
            # proper-clock measure. sin(f) is NOT absorbed in this map.
            norm=lambda b:np.sum(abs(b)**2,axis=tuple(range(1,b.ndim)))
            ip=lambda b,d:np.sum(b.conj()*d,axis=tuple(range(1,b.ndim))).real
            left=mu[:4]*norm(patched);right=N[:4]*norm(acted)
            leftx=mux[:4]*norm(patched)+2*mu[:4]*ip(patched,patchedx)
            rightx=c['lapse_first'][0,:4]*norm(acted)+2*N[:4]*ip(acted,actedx)
            norm_check=scaled(left,right);normx_check=scaled(leftx,rightx)
            if max(norm_check,normx_check)>2e-10:raise ArithmeticError('Actual input/output density isometry failed')
            arrays[tag+'_covector_native_A_on_original_trial']=patched
            arrays[tag+'_covector_native_A_on_original_trial_time']=patchedx
            arrays[tag+'_density_isometric_input_trial']=chi
            arrays[tag+'_density_isometric_input_trial_time']=chix
            arrays[tag+'_density_isometric_native_A_trial']=acted
            arrays[tag+'_density_isometric_native_A_trial_time']=actedx
            arrays[tag+'_temporal_conormal_contact_delta']=timescale(mu/N*delta)*v
            records.append(dict(side=side,sheet_orientation=eps,full_fibre_width=1920,declared_trial_columns=3,
                delta_operator_norms=abs(delta).tolist(),delta_full1920_Frobenius_norms=(np.sqrt(1920)*abs(delta)).tolist(),
                full1920_action_contact_norm=float(np.linalg.norm(timescale(delta)*v)),full1920_action_contact_time_norm=float(np.linalg.norm(timescale(dx)*v+timescale(delta)*vx)),
                input_output_density_isometry_scaled=norm_check,input_output_density_isometry_first_scaled=normx_check,
                Clifford_contact_defect=max(branches[b]['Clifford_output_contact_identity_defect']for b in branches),
                fermion_density_scaled=a['supplied_fermion_density_scaled_defect'],fermion_density_first_scaled=a['supplied_fermion_density_first_scaled_defect'],geometry_checks=geo_checks))
    archive=out/'actual_full1920_positive_covector_binding.npz';_compressed_npz(archive,arrays)
    for name,m in list(sys.modules.items()):
        p=getattr(m,'__file__',None)
        if p and(name=='bhsm'or name.startswith('bhsm.'))and Path(p).resolve().is_relative_to(root):pin(Path(p).resolve())
    for path in ('src/bhsm/interface/ae4_stratified_dirac_zeta_induced_owner.py','src/bhsm/interface/muon_owned_native_product_connection.py','src/bhsm/interface/muon_combined_f_eta_contact.py','src/bhsm/interface/muon_original_m8_geometric_expression.py','src/bhsm/interface/muon_m8_original_hopf_spin_lift.py','src/bhsm/interface/muon_full_d5_common_gauge_insertion.py'):pin(path)
    pin(Path(__file__))
    report=dict(classification='REAL_POSITIVE_COFRAME_FULL_D5_COVECTOR_COMPATIBILITY_BINDING',source_sha256=sha256(producer).hexdigest(),input_and_source_hashes=dict(sorted(pins.items())),
        archive=dict(name=archive.name,sha256=sha256(archive.read_bytes()).hexdigest(),bytes=archive.stat().st_size),records=records,
        real_positive_coframe_same_covector_connection_premise=True,input_output_fermion_geometric_pairing_bound=True,
        sin_f_absorbed_in_Riesz_or_eta_deleted=False,analytic_time_contour_or_new_Wick_phase_chosen=False,
        full_existing_SM_Spin_families_retained=True,M8_Spin16_identified_as_SM_copy=False,
        no_D5_action_history_or_profile_replay=True,assigned_formal_energy_point_promoted=False,
        full_AE4_native_grading_or_global_domain_identified=False,physical_E_dictionary=False,
        physical_outgoing_or_energy_field_derivative_or_moment=False,original_coupled_corrections_applied=0)
    (out/'result.json').write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(records=records)),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',default=ROOT,type=Path);p.add_argument('--insertion-folder',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
    a=p.parse_args()
    try:run(a.repository,a.insertion_folder,a.output)
    except Exception as e:
        import traceback
        if a.output.exists():(a.output/'failure.json').write_text(json.dumps(dict(error=repr(e),traceback=traceback.format_exc(),source_sha256=sha256(Path(__file__).read_bytes()).hexdigest()),indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
        raise
