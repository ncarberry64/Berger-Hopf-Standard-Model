"""Compose the same-covector real D5 base with all1200 common gauge columns.

Only saved actual coefficient/action germs are contracted. This is a
three-trial form block, not a native spectral trace or an outgoing solve.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np
from scipy.sparse import csr_matrix

ROOT=Path(__file__).resolve().parents[1]
PRIMARY='artifacts/muon_real_coupled_open_operator_20261016/source_first_run_1'


def compare(a,b):
    a,b=np.asarray(a),np.asarray(b)
    return dict(absolute=float(np.max(abs(a-b),initial=0)),
        max_entry_scaled=float(np.max(abs(a-b)/np.maximum(1,np.maximum(abs(a),abs(b))),initial=0)))


def scale(a,v):
    return np.asarray(a).reshape((-1,)+(1,)*(v.ndim-1))*v


def embed(v):
    return np.pad(v,((0,0),(0,0),(0,0),(0,0),(0,0),(0,50),(0,0)))


def run(repository,gauge_folder,covector_folder,output):
    root,gfolder,cfolder,out=map(lambda p:Path(p).resolve(),
        (repository,gauge_folder,covector_folder,output))
    if out.exists():raise FileExistsError('Preserve independent actual contractions')
    pins={}
    def pin(p):
        p=Path(p);p=p if p.is_absolute()else root/p
        key=p.relative_to(root).as_posix()if p.is_relative_to(root)else str(p)
        pins[key]=sha256(p.read_bytes()).hexdigest();return p
    def read(p):
        p=pin(p)
        if p.suffix=='.json':return json.loads(p.read_bytes())
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    sys.path.insert(0,str(root/'src'))
    from bhsm.interface.muon_full_d5_common_gauge_insertion import (
        internal_material_actions,material_pairing,common_form_pullback,apply_material_insertion)
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    from bhsm.interface.muon_parent_retarded_hypercharge import WALL
    gm,cm=read(gfolder/'result.json'),read(cfolder/'result.json')
    if gm['classification']!='ACTUAL_SAME_REAL_PRIMAL_COMMON1200_TO_FULL384_D5_GAUGE_INSERTION':
        raise ValueError('Reviewed complete common gauge incidence required')
    if cm['classification']!='REAL_POSITIVE_COFRAME_FULL_D5_COVECTOR_COMPATIBILITY_BINDING':
        raise ValueError('Same-covector positive real base required')
    if sha256(pin(gfolder/'executed_producer.py').read_bytes()).hexdigest()!='4a9ea459bb95a3f470562098c9d82509c982677997542f86ed3626f968e9ded3':
        raise ValueError('Wrong gauge source epoch')
    if sha256(pin(cfolder/'executed_producer.py').read_bytes()).hexdigest()!='99492ff4d3b12beaa3b5a7f0801020d3859bf151203cbe17ce5c680984fb39d0':
        raise ValueError('Wrong covector source epoch')
    cov=read(cfolder/cm['archive']['name'])
    if sha256((cfolder/cm['archive']['name']).read_bytes()).hexdigest()!=cm['archive']['sha256']:
        raise ValueError('Saved native base changed')
    primary=read(PRIMARY+'/application.npz')
    if pins[PRIMARY+'/application.npz']!='7da8ddd5fa4bda397aa6a2d50e845338a3ef92fb3f0e837a5a6d0d166915e177':
        raise ValueError('Primary actual real coefficient epoch changed')
    angular=read(gfolder/'angular_product_incidence.npz')
    gaunt=angular['gaunt_full55_real20_input5']
    if gaunt.shape!=(55,20,5):raise ValueError('Keep all connected angular outputs')
    _,rw=np.polynomial.legendre.leggauss(4);rw=rw*WALL/2*(2*np.pi**2)
    records=[];arrays={}
    for side in('incoming','outgoing'):
        geo=read(gfolder/(side+'_saved_geometry.npz'))
        c={k[len(side+'_input_'):]:v for k,v in primary.items()if k.startswith(side+'_input_')}
        # The gauge export excludes eta-labelled fields. Read the complete
        # pinned primary c; check every field that was actually exported.
        for k,v in c.items():
            if side+'_c_'+k in geo and not np.array_equal(v,geo[side+'_c_'+k]):
                raise ValueError('Source geometry splice: '+k)
        mu,mux=c['volume_density'][:4],c['volume_density_first'][0,:4]
        N,Nx=c['lapse'][:4],c['lapse_first'][0,:4]
        s,sx=cov[side+'_input_output_density_isometry'][:4],cov[side+'_input_output_density_isometry_first'][0,:4]
        delta,dx=cov[side+'_delta_scalar_body'][:4],cov[side+'_delta_scalar_body_first'][0,:4]
        density_control=compare(mu,N*s*s)
        density_time_control=compare(mux,Nx*s*s+2*N*s*sx)
        for eps in(-1,1):
            tag=f'{side}_eta{eps}';file=tag+'_compact_application.npz';saved=read(gfolder/file)
            if sha256((gfolder/file).read_bytes()).hexdigest()!=gm['archives'][file]['sha256']:
                raise ValueError('Saved common insertion changed')
            key=tag+'_recovered_';v,vx=saved[key+'value'],saved[key+'value_time']
            P=cov[tag+'_covector_native_A_on_original_trial']
            Px=cov[tag+'_covector_native_A_on_original_trial_time']
            chi=cov[tag+'_density_isometric_input_trial'];chix=cov[tag+'_density_isometric_input_trial_time']
            DP=cov[tag+'_density_isometric_native_A_trial'];DPx=cov[tag+'_density_isometric_native_A_trial_time']
            epoch_controls=dict(native=compare(P,saved[key+'A0']+scale(delta,v)),
                native_time=compare(Px,saved[key+'A0_time']+scale(dx,v)+scale(delta,vx)),
                density_input=compare(chi,scale(s,v)),density_input_time=compare(chix,scale(sx,v)+scale(s,vx)),
                density_output=compare(DP,scale(s,P)),density_output_time=compare(DPx,scale(sx,P)+scale(s,Px)))
            if any(t['absolute']!=0 for t in epoch_controls.values()):raise ValueError('Actual saved trial epoch mismatch')
            S,Sx,G=(saved[tag+'_'+k][:4]if k!='carrier_generators'else saved[tag+'_'+k]
                for k in('spin','spin_time','carrier_generators'))
            T=internal_material_actions(S,G,v)
            Tx=internal_material_actions(Sx,G,v)+internal_material_actions(S,G,vx)
            TD=internal_material_actions(S,G,chi)
            TDx=internal_material_actions(Sx,G,chi)+internal_material_actions(S,G,chix)
            phase=saved[key+'formal']-saved[key+'A0']
            phasex=saved[key+'formal_time']-saved[key+'A0_time']
            for tent in(-1,1):
                xtag=tag+f'_tent{tent}';maps=[]
                for j in range(4):
                    m={}
                    for k in('material_value_map','material_value_map_time'):
                        prefix=xtag+f'_r{j}_'+k
                        m[k]=csr_matrix((saved[prefix+'_data'],saved[prefix+'_indices'],saved[prefix+'_indptr']),shape=tuple(saved[prefix+'_shape']))
                    maps.append(m)
                z=(np.cos(np.arange(1,1201)*.173)+.3*np.sin(np.arange(1,1201)*.119))/np.sqrt(1200)
                # Same declared finite gauge direction as the original map;
                # its fixed coefficient vector is not a new field solution.
                length=2*abs(next(r['coordinate_time']for r in gm['records']if r['side']==side))
                z[800:1120]*=length
                material=np.array([(m['material_value_map']@z).reshape(5,4,20)for m in maps])
                materialx=np.array([(m['material_value_map_time']@z).reshape(5,4,20)for m in maps])
                Xi=apply_material_insertion(material,S,G,gaunt,v)
                Xix=apply_material_insertion(materialx,S,G,gaunt,v)+apply_material_insertion(material,Sx,G,gaunt,v)+apply_material_insertion(material,S,G,gaunt,vx)
                XiD=apply_material_insertion(material,S,G,gaunt,chi)
                XiDx=apply_material_insertion(materialx,S,G,gaunt,chi)+apply_material_insertion(material,Sx,G,gaunt,chi)+apply_material_insertion(material,S,G,gaunt,chix)
                square=2*np.einsum('q,qfbsion,qfbsion->',rw*mu,Xi.conj(),Xi).real
                squarex=2*np.einsum('q,qfbsion,qfbsion->',rw*mux,Xi.conj(),Xi).real+4*np.einsum('q,qfbsion,qfbsion->',rw*mu,Xi.conj(),Xix).real
                squareD=2*np.einsum('q,qfbsion,qfbsion->',rw*N,XiD.conj(),XiD).real
                squareDx=2*np.einsum('q,qfbsion,qfbsion->',rw*Nx,XiD.conj(),XiD).real+4*np.einsum('q,qfbsion,qfbsion->',rw*N,XiD.conj(),XiDx).real
                square_checks=dict(value=compare(square,squareD),time=compare(squarex,squareDx),
                    unchanged_contact=compare(square,z@saved[xtag+'_common_source_square_on_declared_direction']),
                    unchanged_contact_time=compare(squarex,z@saved[xtag+'_common_source_square_time_on_declared_direction']))
                placements={}
                for name,base,basex,dense,densex in(
                    ('A0',P,Px,DP,DPx),('formal',P+phase,Px+phasex,DP+scale(s,phase),DPx+scale(sx,phase)+scale(s,phasex))):
                    def form(left,leftx,actions,actionsx,weight,weightx):
                        R=material_pairing(embed(left).conj(),actions,gaunt)
                        Rx=material_pairing(embed(leftx).conj(),actions,gaunt)+material_pairing(embed(left).conj(),actionsx,gaunt)
                        K,Kx=common_form_pullback(R,maps,weight,material_pair_time=Rx,weights_time=weightx)
                        return K+K.conj().transpose(0,2,1),Kx+Kx.conj().transpose(0,2,1)
                    K,Kx=form(base,basex,T,Tx,rw*mu,rw*mux)
                    KD,KDx=form(dense,densex,TD,TDx,rw*N,rw*Nx)
                    DK,DKx=form(scale(delta,v),scale(dx,v)+scale(delta,vx),T,Tx,rw*mu,rw*mux)
                    old=saved[xtag+'_'+name+'_common_K_partial'];oldx=saved[xtag+'_'+name+'_common_K_time_partial']
                    direct=np.einsum('q,qfbsioa,qfbsion->an',rw*mu,embed(base).conj(),Xi)
                    directx=np.einsum('q,qfbsioa,qfbsion->an',rw*mux,embed(base).conj(),Xi)
                    directx+=np.einsum('q,qfbsioa,qfbsion->an',rw*mu,embed(basex).conj(),Xi)+np.einsum('q,qfbsioa,qfbsion->an',rw*mu,embed(base).conj(),Xix)
                    direct=direct+direct.conj().T;directx=directx+directx.conj().T
                    checks=dict(density_isometry=compare(K,KD),density_isometry_time=compare(Kx,KDx),
                        old_plus_covector=compare(K,old+DK),old_plus_covector_time=compare(Kx,oldx+DKx),
                        independent_direction=compare(np.einsum('z,zab->ab',z,K),direct),
                        independent_direction_time=compare(np.einsum('z,zab->ab',z,Kx),directx))
                    arrays[xtag+'_'+name+'_common_K_partial']=K
                    arrays[xtag+'_'+name+'_common_K_time_partial']=Kx
                    arrays[xtag+'_'+name+'_covector_delta_common_K_partial']=DK
                    arrays[xtag+'_'+name+'_covector_delta_common_K_time_partial']=DKx
                    placements[name]=dict(controls=checks,K_norm=float(np.linalg.norm(K)),K_time_norm=float(np.linalg.norm(Kx)),
                        covector_delta_K_norm=float(np.linalg.norm(DK)),covector_delta_K_time_norm=float(np.linalg.norm(DKx)),
                        independent_H80_bulk_norm=float(np.linalg.norm(K[1120:])),
                        Hermitian_defect=float(np.max(abs(K-K.conj().transpose(0,2,1)))))
                controls=[v['max_entry_scaled']for p in placements.values()for v in p['controls'].values()]
                controls += [v['max_entry_scaled']for v in square_checks.values()]
                if max(controls)>2e-10:raise ArithmeticError('Matched covector/common form control failed')
                records.append(dict(side=side,eta_orientation=eps,tent_one_sided_sign=tent,placements=placements,
                    source_square_controls=square_checks,geometric_density=density_control,geometric_density_time=density_time_control,
                    exact_saved_trial_epoch_controls=epoch_controls,complete_product_output_harmonics=55))
    out.mkdir(parents=True)
    _compressed_npz(out/'actual_covector_common_gauge_forms.npz',arrays)
    for name,m in list(sys.modules.items()):
        p=getattr(m,'__file__',None)
        if p and name.startswith('bhsm.')and Path(p).resolve().is_relative_to(root):pin(Path(p).resolve())
    pin(Path(__file__));producer=Path(__file__).read_bytes();(out/'executed_producer.py').write_bytes(producer)
    arc=out/'actual_covector_common_gauge_forms.npz'
    report=dict(classification='ACTUAL_REAL_COVECTOR_COMMON1200_FULL_D5_THREE_TRIAL_FORM_COMPOSITION',
        source_sha256=sha256(producer).hexdigest(),input_and_source_hashes=dict(sorted(pins.items())),
        archive=dict(name=arc.name,sha256=sha256(arc.read_bytes()).hexdigest(),bytes=arc.stat().st_size),records=records,
        full_common1200_and_full384_spin_family_carrier_retained=True,full_connected55_angular_output_retained=True,
        real_positive_coframe_same_covector_premise=True,assigned_formal_energy=float(gm['formal_phase_parameter']),
        A0_and_assigned_formal_phase_kept_separate=True,density_isometry_applied_to_input_and_output=True,
        eta_deleted_or_sin_f_absorbed_in_density=False,gauge_source_coefficients_conjugated=False,
        declared_trial_columns=3,full_native_K_M_or_spectral_trace=False,physical_Higgs_surface_native_map=False,
        physical_native_statistics_grading_and_global_domain_identified=False,physical_native_energy_dictionary=False,
        D5_source_history_profile_campaigns_replayed=0,physical_outgoing_derivative_pass=False,
        original_coupled_corrections=0,physical_Maxwell_all226_after_pass=False,
        normalized_physical_two_spin_muon=None,physical_muon_magnetic_moment=None)
    (out/'result.json').write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(archive=report['archive'],records=len(records))),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repository',default=ROOT,type=Path);p.add_argument('--gauge-folder',required=True,type=Path)
    p.add_argument('--covector-folder',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
    a=p.parse_args();run(a.repository,a.gauge_folder,a.covector_folder,a.output)
