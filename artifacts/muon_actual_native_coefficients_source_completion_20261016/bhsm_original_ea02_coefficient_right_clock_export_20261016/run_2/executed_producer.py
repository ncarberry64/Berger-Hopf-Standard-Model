"""Coefficient-only R/hR and Rdot operands at the exact ea02/D4 cut.

The separately copied runtime returns before any action density assembly.
No original runtime, history, field, response, Hessian or primal solve changes.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
FAMILY='artifacts/muon_baton_zoo_maximal_current_realization_20261013'
RUNTIME=FAMILY+'/actual_new620_fresh_native_MP_new_exact_R7_clock_control_run_1'
TARGET=FAMILY+'/actual_linear_cut_compatible368_MP_full_operator_blocked_run_2/actual_precise_direct_CHILD620_and_full368_canonical_source_operands.npz'
CLOCK=FAMILY+'/actual_same_cut_native_MP_matrixfree_continuous_clock_run_1/actual_continuous_phase210_clock_and_same_owner_point_density_rate.npz'


def run(repository,position_folder,jacobi_folder,output):
    root,pdir,jdir,out=map(lambda p:Path(p).resolve(),(repository,position_folder,jacobi_folder,output))
    out.mkdir(parents=True,exist_ok=False);pins={};producer=Path(__file__).read_bytes();(out/'executed_producer.py').write_bytes(producer)
    def pin(path):
        p=Path(path);p=p if p.is_absolute()else root/p
        key=p.relative_to(root).as_posix()if p.is_relative_to(root)else str(p);pins[key]=sha256(p.read_bytes()).hexdigest();return p
    def read(path):
        p=pin(path)
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
    original=pin(RUNTIME+'/new620_fresh_actual_native_MP_scalar_imported_runtime.py')
    if sha256(original.read_bytes()).hexdigest()!='8fcc5e3a5c0e2724cf24789c8326fb9725601f5a991e4f5e0b3189a27c0ca5fe':raise ValueError('Original frozen scalar runtime changed')
    copy=pin('audits/retained_muon_ea02_coefficient_export_runtime_20261016.py')
    patch=pin('audits/retained_muon_ea02_coefficient_export_runtime_20261016.patch')
    if sha256(copy.read_bytes()).hexdigest()!='bc84be9f173d05d2c1f9aaefd05469cbe6f49a911f414c9b5e5d75d5a4bc3ac2'or sha256(patch.read_bytes()).hexdigest()!='676676c3107c634999f0460d3bc5a55238cc59927da2b3c4fc77443a43040a40':raise ValueError('Explicit coefficient-only source/diff changed')
    import difflib
    diff=''.join(difflib.unified_diff(original.read_text().splitlines(True),copy.read_text().splitlines(True),fromfile=original.name,tofile=copy.name))
    if diff.encode()!=patch.read_bytes():raise ValueError('Disclosed early-return patch does not reconstruct the copied source')
    (out/'frozen_coefficient_export_runtime.py').write_bytes(copy.read_bytes());(out/'disclosed_coefficient_export.patch').write_bytes(patch.read_bytes())
    packed=module('ea02_coefficient_export_copy',copy);chart=module('ea02_coefficient_export_chart4',RUNTIME+'/new620_fresh_same_material_equations_chart4_imported_runtime.py')
    def exact(z,k):return ex.parse_acb_exact_dyadic(z,k+'_exact')
    target,clock=read(TARGET),read(CLOCK);pm,jm=read(pdir/'result.json'),read(jdir/'result.json')
    if pins[TARGET]!='ea02ed6aee45310c5651fef5c8f103e868007d4f125582ab2b64ff7651f76b2b'or pins[CLOCK]!='18fcc0d4fa588c4fcd7aaa8822be76c132b660e0a2f223f7be55fcb9d8d41290':raise ValueError('Exact ea02/native CUT clock required')
    for folder,meta,h in((pdir,pm,'d6b0dbb2e34185011f243f7f571da2f536ebc58c6138fab380f856a2f5db96b9'),(jdir,jm,'a761a939cffb6b426ac254f59a8263feeb644ebdfc3843f69b061ee607b4ba3f')):
        if meta['source_sha256']!=h or sha256(pin(folder/'executed_producer.py').read_bytes()).hexdigest()!=h:raise ValueError('Frozen same-cut source required')
        if sha256(pin(folder/meta['archive']['name']).read_bytes()).hexdigest()!=meta['archive']['sha256']:raise ValueError('Frozen same-cut source archive required')
    p,j=read(pdir/pm['archive']['name']),read(jdir/jm['archive']['name']);native=read(pdir/pm['native_epoch_map_archive']['name'])
    if sha256((pdir/pm['native_epoch_map_archive']['name']).read_bytes()).hexdigest()!=pm['native_epoch_map_archive']['sha256']:raise ValueError('Native basis value/clock archive changed')
    for z in(p,j,clock):
        if not np.array_equal(z['master368'],target['master368'])or z['coordinate_time'].item()!=target['coordinate_time'].item():raise ValueError('No field/source/response epoch splice')
    if pm['degree']!=4 or jm['new_positions']!=59 or not pm['epoch_basis_value_and_clock_reconstructed_from_native_point_germs']:raise ValueError('Exact corrected native D4 source application required')
    phase=load_profile_preserving_phase('artifacts/muon_inherited_finite_normal_phase_20261011/run_1',repository=root);pins.update(phase['input_hashes']);rep=dict(phase['representation']);P=phase['coordinates']['lift']
    maps=read('artifacts/muon_baton_zoo_radial_convergence_20261014/actual_linear_cut_degree4_complete_clock_epoch_maps_run_1/actual_degree_04_complete_clock_covariant_product_epoch_maps.npz')
    for k in('extra_point_lift','extra_wall_lift'):
        for part in('high','low'):maps[k+'_'+part]=native[k+'_'+part]
    Th=packed._coefficient_array(None,native['extra_point_lift_total_clock_high'],native['extra_point_lift_total_clock_low'])
    Wh=packed._coefficient_array(None,native['extra_wall_lift_total_clock_high'],native['extra_wall_lift_total_clock_low'])
    for k,rk in(('original_gauge_basis','gauge_basis'),('original_gauge_radial_basis','gauge_radial_basis'),('original_wall_trace_map','wall_trace_map')):
        v=maps[k+'_high']+maps[k+'_low'];rep[rk]=v.real.reshape(len(rep['rho']),80,1,5,4)if rk!='wall_trace_map'else v.real
    full=int(maps['full_dimension']);oldmap=np.asarray(p['old368_to_enlarged_child'],int)
    h0=exact(clock,'actual_total_master_clock_direction');h=acb_mat(full,1)
    for i in range(252):h[i,0]=h0[i,0]
    for i,dest in enumerate(oldmap):h[252+int(dest),0]=h0[252+i,0]
    R,Rdot=exact(j,'actual_enlarged_seven_field'),exact(j,'actual_enlarged_seven_field_clock')
    if R.nrows()!=full or R.ncols()!=7 or Rdot.nrows()!=full or Rdot.ncols()!=7:raise ValueError('Complete exact same seven fields and clocks required')
    extra=np.asarray(maps['extra_coordinates_to_full'],int);base=p['same_field_child_coefficients'];zero=np.zeros(full,complex)
    def coefficient_call(right,clocked):
        rh,rl=_split(right);hh,hl=_split(h)
        return packed.phase_action_contractions(target['raw_pair'],target['reference_pair'],rep,P,maps,np.asarray([],int),
            hh[:,0]if clocked else zero,hl[:,0]if clocked else zero,rh,rl,extra_base=base[extra-252],
            reference_direction=clock['reference_affine_clock_once']if clocked else None,include_directional_first=clocked,
            include_parent_action=False,precision_bits=256,material_chart_precision='independent_mp_same_material_equations',material_chart_owner=chart.anchored_material_chart4,
            extra_point_lift_first=Th if clocked else None,extra_wall_lift_first=Wh if clocked else None,
            right_exact=right,direction_exact=h if clocked else None,coefficient_export_only=True)
    print(json.dumps(dict(stage='coefficient_only_R_hR',rights=7,J_tests=0,radial_nodes=len(rep['rho']))),flush=True)
    a=coefficient_call(R,True)
    print(json.dumps(dict(stage='coefficient_only_Rdot',rights=7,J_tests=0)),flush=True)
    b=coefficient_call(Rdot,False)
    for z in(a,b):
        if bool(z['action_density_or_gradient_or_Hessian_assembled'])or not bool(z['coefficient_export_only']):raise ValueError('Coefficient-only early return required')
        z.update(coordinate_time=target['coordinate_time'],master368=target['master368'],rho=np.asarray(rep['rho']),radial_quadrature=np.asarray(rep['radial_quadrature']),
            old368_to_enlarged_child=oldmap,new_position_indices=p['new_position_indices'])
    reproduction={}
    for key,oldkey in(('point','child_point_coefficients'),('density','child_metric_density'),('wall','child_wall_connection')):
        reproduction[key]=_upper(exact(a,key)-exact(p,oldkey));reproduction[key+'_h']=_upper(exact(a,key+'_h')-exact(p,oldkey+'_directional_first'))
        reproduction[key+'_Rdot_base']=_upper(exact(b,key)-exact(p,oldkey))
    if max(reproduction.values())>2e-10:raise ValueError('Coefficient-only early return changed actual coefficient/clock operands')
    archives={}
    for name,z in(('actual_same_ea02_D4_seven_point_density_R_hR.npz',a),('actual_same_ea02_D4_seven_point_density_Rdot.npz',b)):
        path=out/name;_compressed_npz(path,z);archives[name]=dict(sha256=sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size)
    for name,m in list(sys.modules.items()):
        f=getattr(m,'__file__',None)
        if f and(name=='bhsm'or name.startswith('bhsm.'))and Path(f).resolve().is_relative_to(root):pin(Path(f).resolve())
    pin(Path(__file__))
    result=dict(classification='EXACT_SAME_EA02_D4_SEVEN_COEFFICIENT_RIGHT_AND_CLOCK_EXPORT',source_sha256=sha256(producer).hexdigest(),input_and_source_hashes=dict(sorted(pins.items())),
        archives=archives,actual_original_field_and_clock_reproduction_upper=reproduction,radial_nodes=len(rep['rho']),rights=7,J_tests=0,arithmetic_precision_bits=256,
        original_scalar_runtime_unchanged_sha256=sha256(original.read_bytes()).hexdigest(),copied_runtime_sha256=sha256(copy.read_bytes()).hexdigest(),disclosed_patch_sha256=sha256(patch.read_bytes()).hexdigest(),
        original_regular_action_mode_equations_unchanged=True,coefficient_only_early_return_before_action_density=True,
        no_action_gradient_Hessian_or_field_or_response_solve=True,source_and_reference_total_clock_retained_once=True,
        actual_Rdot_and_sourceDot_supplied_not_zeroed=True,pure_boundary_weights_without_geometric_cap_action_loop=True,
        same_fixed_chart_T_Th_W_Wh_reused=True,exact_dyadic_coefficient_exports=True,implicit_material_chart_coefficients_and_derivatives_exported=True,
        independent_full59x7_Jacobi_control_pass=False,physical_outgoing_or_full_derivative_or_Moment=False,original_coupled_corrections=0)
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(archives=archives,reproduction=reproduction)),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',type=Path,default=ROOT)
    for key in('position-folder','jacobi-folder','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();run(a.repository,a.position_folder,a.jacobi_folder,a.output)
