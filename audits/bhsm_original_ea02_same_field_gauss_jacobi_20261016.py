"""Actual native-material D4 Gauss H*R on the retained seven ea02 fields.

No third derivative, time/field history, retraction or correction is run.
The primal Gauss gradient and H_G R are distinct. The primal gradient is
added exactly once to affine column0. Native means material precision here.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import sys
import numpy as np
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
ROOT=Path(__file__).resolve().parents[1]
FAMILY='artifacts/muon_baton_zoo_maximal_current_realization_20261013'
RUNTIME=FAMILY+'/actual_new620_fresh_native_MP_new_exact_R7_clock_control_run_1'
TARGET=FAMILY+'/actual_linear_cut_compatible368_MP_full_operator_blocked_run_2/actual_precise_direct_CHILD620_and_full368_canonical_source_operands.npz'


def run(repository,position_folder,jacobi_folder,output):
    root,pdir,jdir,out=map(lambda p:Path(p).resolve(),(repository,position_folder,jacobi_folder,output));out.mkdir(parents=True,exist_ok=False)
    producer=Path(__file__).read_bytes();(out/'executed_producer.py').write_bytes(producer);pins={}
    def pin(p):
        p=Path(p);p=p if p.is_absolute()else root/p;k=p.relative_to(root).as_posix()if p.is_relative_to(root)else str(p);pins[k]=sha256(p.read_bytes()).hexdigest();return p
    def read(p):
        p=pin(p)
        if p.suffix=='.json':return json.loads(p.read_bytes())
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    def module(name,path):
        p=pin(path);s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
    sys.path[:0]=[str(root/'src'),str(root/'scripts')]
    from flint import ctx,acb_mat
    from bhsm.interface.muon_stored_admission_correction import _upper
    from bhsm.interface.muon_stored_fiber_canonical_tangent import _split
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
    ctx.prec=256
    module('bhsm_baton_zoo_exact_acb_packets',RUNTIME+'/bhsm_baton_zoo_exact_acb_packets_imported_runtime.py')
    ex=module('bhsm_exact_action_balls',RUNTIME+'/bhsm_exact_action_balls_imported_runtime.py')
    packed=module('same_field_gauss_jacobi_scalar',RUNTIME+'/new620_fresh_actual_native_MP_scalar_imported_runtime.py')
    chart=module('same_field_gauss_jacobi_chart4',RUNTIME+'/new620_fresh_same_material_equations_chart4_imported_runtime.py')
    def exact(z,k):return ex.parse_acb_exact_dyadic(z,k+'_exact')
    a=read(TARGET);pm,jm=read(pdir/'result.json'),read(jdir/'result.json')
    if pins[TARGET]!='ea02ed6aee45310c5651fef5c8f103e868007d4f125582ab2b64ff7651f76b2b':raise ValueError('Exact original target required')
    for folder,meta,h in [(pdir,pm,'d6b0dbb2e34185011f243f7f571da2f536ebc58c6138fab380f856a2f5db96b9'),(jdir,jm,'a761a939cffb6b426ac254f59a8263feeb644ebdfc3843f69b061ee607b4ba3f')]:
        if meta['source_sha256']!=h or sha256(pin(folder/'executed_producer.py').read_bytes()).hexdigest()!=h:raise ValueError('Exact reviewed position/Jacobi source required')
        if sha256(pin(folder/meta['archive']['name']).read_bytes()).hexdigest()!=meta['archive']['sha256']:raise ValueError('Position/Jacobi archive bytes changed')
    p,j=read(pdir/pm['archive']['name']),read(jdir/jm['archive']['name']);newmaps=read(pdir/pm['native_epoch_map_archive']['name'])
    if sha256((pdir/pm['native_epoch_map_archive']['name']).read_bytes()).hexdigest()!=pm['native_epoch_map_archive']['sha256']:raise ValueError('Corrected epoch-map bytes changed')
    for z in (p,j):
        if not np.array_equal(z['master368'],a['master368'])or z['coordinate_time'].item()!=a['coordinate_time'].item():raise ValueError('No state/time splice')
    maps=read('artifacts/muon_baton_zoo_radial_convergence_20261014/actual_linear_cut_degree4_complete_clock_epoch_maps_run_1/actual_degree_04_complete_clock_covariant_product_epoch_maps.npz')
    for k in ('extra_point_lift','extra_wall_lift'):
        for part in ('high','low'):maps[k+'_'+part]=newmaps[k+'_'+part]
    phase=load_profile_preserving_phase('artifacts/muon_inherited_finite_normal_phase_20261011/run_1',repository=root);pins.update(phase['input_hashes']);rep=dict(phase['representation']);P=phase['coordinates']['lift']
    for k,rk in [('original_gauge_basis','gauge_basis'),('original_gauge_radial_basis','gauge_radial_basis'),('original_wall_trace_map','wall_trace_map')]:
        v=maps[k+'_high']+maps[k+'_low'];rep[rk]=v.real.reshape(len(rep['rho']),80,1,5,4)if rk!='wall_trace_map'else v.real
    n=int(p['enlarged_dynamic_count']);full=int(maps['full_dimension']);tests=252+np.arange(2*n,full-252);R=exact(j,'actual_enlarged_seven_field');rh,rl=_split(R)
    if R.nrows()!=full or R.ncols()!=7:raise ValueError('Complete same seven fields required')
    params=read('artifacts/muon_coupled_birth_full_application_20261012/run_1/result.json')['action_parameters'];extra=np.asarray(maps['extra_coordinates_to_full'],int);zero=np.zeros(full,complex)
    print(json.dumps(dict(stage='actual_ea02_D4_Gauss_H_R_started',Gauss_tests=len(tests),rights=7)),flush=True)
    app=packed.phase_action_contractions(a['raw_pair'],a['reference_pair'],rep,P,maps,tests,zero,zero,rh,rl,
        extra_base=p['same_field_child_coefficients'][extra-252],include_directional_first=False,include_parent_action=False,precision_bits=256,
        material_chart_precision='independent_mp_same_material_equations',material_chart_owner=chart.anchored_material_chart4,
        nu_squared_action=params['nu_squared_action'],surface_gamma=params['surface_gamma'],export_exact_action_balls=True,right_exact=R)
    _compressed_npz(out/'actual_D4_Gauss_H_R_seven_action.npz',app)
    r,Kz=exact(app,'phase_gradient'),exact(app,'phase_Hessian_on_actual_right');same=_upper(r-exact(p,'enlarged_primal_Gauss_r'))
    if same>2e-10:raise ValueError('Fresh Gauss application changed the fixed primal row')
    affine=acb_mat(Kz)
    for i in range(r.nrows()):affine[i,0]+=r[i,0]
    combined=acb_mat(r.nrows(),4)
    for i in range(r.nrows()):
        combined[i,0]=affine[i,0]
        for k in range(3):combined[i,1+k]=affine[i,1+k]+affine[i,4+k]
    arrays=dict(coordinate_time=a['coordinate_time'],master368=a['master368'],full_Gauss_action_indices=tests)
    for k,value in dict(actual_primal_Gauss_r=r,actual_native_Gauss_Kz_trial=Kz,actual_affine_seven_Gauss_trial_residual=affine,actual_combined_four_Gauss_trial_residual=combined,actual_same_seven_field=R).items():
        arrays[k+'_high'],arrays[k+'_low']=_split(value);arrays.update(ex.export_acb_exact_dyadic(value,k+'_exact'))
    archive=out/'actual_D4_native_Gauss_Jacobi_and_affine_residual.npz';_compressed_npz(archive,arrays)
    for name,m in list(sys.modules.items()):
        f=getattr(m,'__file__',None)
        if f and(name=='bhsm'or name.startswith('bhsm.'))and Path(f).resolve().is_relative_to(root):pin(Path(f).resolve())
    pin(Path(__file__))
    report=dict(classification='ACTUAL_ORIGINAL_EA02_SAME_FIELD_D4_GAUSS_JACOBI_APPLICATION',source_sha256=sha256(producer).hexdigest(),input_and_source_hashes=dict(sorted(pins.items())),
        archive=dict(name=archive.name,sha256=sha256(archive.read_bytes()).hexdigest(),bytes=archive.stat().st_size),Gauss_rows=len(tests),rights=7,
        actual_primal_Gauss_upper=_upper(r),actual_native_Gauss_Kz_upper=_upper(Kz),actual_affine_seven_Gauss_residual_upper=_upper(affine),actual_combined_four_Gauss_residual_upper=_upper(combined),same_primal_Gauss_reproduction_upper=same,
        native_means_material_precision_not_graded_operator=True,primal_r_added_once_only_in_affine_column0=True,
        higher_radial_field_or_response_solved=False,Gauss_retraction_or_correction_applied=False,physical_outgoing_or_derivative_or_moment=False,original_coupled_corrections_applied=0)
    (out/'result.json').write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n');print(json.dumps({k:report[k]for k in ('actual_native_Gauss_Kz_upper','actual_affine_seven_Gauss_residual_upper','same_primal_Gauss_reproduction_upper')}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',type=Path,default=ROOT);p.add_argument('--position-folder',required=True,type=Path);p.add_argument('--jacobi-folder',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
    a=p.parse_args();run(a.repository,a.position_folder,a.jacobi_folder,a.output)
