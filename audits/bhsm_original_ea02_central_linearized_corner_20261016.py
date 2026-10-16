"""Actual seven-column central source-corner linearization at the ea02 cut.

Consumes independently evaluated momentum and Gauss Hessian applications.
No field, source history, action contraction, retraction or correction is run.
The central parameter profiles are the same retained coefficient chart.
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
RADIAL='artifacts/muon_baton_zoo_radial_convergence_20261014'
RUNTIME=FAMILY+'/actual_new620_fresh_native_MP_new_exact_R7_clock_control_run_1'
TARGET=FAMILY+'/actual_linear_cut_compatible368_MP_full_operator_blocked_run_2/actual_precise_direct_CHILD620_and_full368_canonical_source_operands.npz'


def run(repository,central_folder,jacobi_folder,seven_clock_folder,gauss_folder,output):
    root,centraldir,jdir,sdir,gdir,out=map(lambda p:Path(p).resolve(),(repository,central_folder,jacobi_folder,seven_clock_folder,gauss_folder,output))
    out.mkdir(parents=True,exist_ok=False);pins={};producer=Path(__file__).read_bytes()
    (out/'executed_producer.py').write_bytes(producer)
    def pin(path):
        p=Path(path);p=p if p.is_absolute()else root/p
        key=p.relative_to(root).as_posix()if p.is_relative_to(root)else str(p)
        pins[key]=sha256(p.read_bytes()).hexdigest();return p
    def read(path):
        p=pin(path)
        if p.suffix=='.json':return json.loads(p.read_bytes())
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    def module(name,path):
        p=pin(path);spec=importlib.util.spec_from_file_location(name,p)
        m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
    sys.path[:0]=[str(root/'src'),str(root/'scripts')]
    from flint import ctx,acb_mat
    from bhsm.interface.muon_stored_admission_correction import _matrix,_upper
    from bhsm.interface.muon_stored_fiber_canonical_tangent import _split
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
    from bhsm.interface.muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
    ctx.prec=256
    module('bhsm_baton_zoo_exact_acb_packets',RUNTIME+'/bhsm_baton_zoo_exact_acb_packets_imported_runtime.py')
    ex=module('bhsm_exact_action_balls',RUNTIME+'/bhsm_exact_action_balls_imported_runtime.py')
    def exact(z,k):return ex.parse_acb_exact_dyadic(z,k+'_exact')
    def rows(a,ids):return acb_mat([[a[int(i),j]for j in range(a.ncols())]for i in ids])
    def metadata(folder,expected):
        m=read(folder/'result.json')
        if m['source_sha256']!=expected or sha256(pin(folder/'executed_producer.py').read_bytes()).hexdigest()!=expected:raise ValueError('Frozen reviewed input producer required')
        return m
    def archive(folder,meta):
        p=folder/meta['archive']['name']
        if sha256(pin(p).read_bytes()).hexdigest()!=meta['archive']['sha256']:raise ValueError('Actual application archive bytes changed')
        return read(p)
    def auxiliary(folder,meta,name):
        p=folder/name
        # Older producers pin auxiliary output bytes in the paired inventory;
        # where available use their native per-archive record as well.
        if 'archives'in meta and sha256(pin(p).read_bytes()).hexdigest()!=meta['archives'][name]['sha256']:raise ValueError('Auxiliary application bytes changed')
        return read(p)
    cm=metadata(centraldir,'56c5dc1d082e01e2903d544f327ebf16e64155125e01af0601c2c7038c55aa47')
    jm=metadata(jdir,'a761a939cffb6b426ac254f59a8263feeb644ebdfc3843f69b061ee607b4ba3f')
    sm=metadata(sdir,'95a64f63e2a541abf698ce7e65afc75a3f4eddb5932f239b74458a171e5be1be')
    if not sm['admitted_original210_and_frame7_clock']or max(sm['records'][-1]['original210_linearized_clock_upper'],sm['records'][-1]['frame7_upper'])>2e-10:raise ValueError('Actual original seven clock must pass')
    if sha256(pin(sdir/'executed_producer.py').read_bytes()).hexdigest()!=sm['source_sha256']:raise ValueError('Seven-clock source bytes changed')
    gm=metadata(gdir,'519371278ad0884047147d7b97364d2af7f5f7ae145d15cda1549b56cce35902')
    central,jacobi,gauss=archive(centraldir,cm),archive(jdir,jm),archive(gdir,gm)
    seven=auxiliary(sdir,sm,'actual_same_cut_seven_continuous_response_clock.npz')
    oldapp=auxiliary(sdir,sm,'actual_same_cut_phase_h_R_seven.npz')
    newapp=read(jdir/'actual_D4_position_velocity_h_R_seven.npz')
    for p,h in((sdir/'actual_same_cut_phase_h_R_seven.npz','e15ff54e2294222594782e6a329da34605b264fa20d750e4d987e27198e00e59'),
                (jdir/'actual_D4_position_velocity_h_R_seven.npz','e233ca63a7c9dd611d27162b4cb8e3bde08fb33d01f5b35b56274186ace6e744')):
        if sha256(pin(p).read_bytes()).hexdigest()!=h:raise ValueError('Frozen actual velocity Hessian application required')
    target=read(TARGET)
    if pins[TARGET]!='ea02ed6aee45310c5651fef5c8f103e868007d4f125582ab2b64ff7651f76b2b':raise ValueError('Exact original ea02 target required')
    for z in(central,jacobi,gauss,seven):
        if not np.array_equal(z['master368'],target['master368'])or z['coordinate_time'].item()!=target['coordinate_time'].item():raise ValueError('No field/source/clock epoch splice')
    if cm['degree']!=4 or jm['new_positions']!=59 or gm['Gauss_rows']!=60:raise ValueError('Complete reviewed D4 test carrier required')
    oldmap=np.asarray(jacobi['old368_to_enlarged_child'],int);newq=np.asarray(jacobi['new_position_indices'],int)
    if not np.array_equal(oldmap,central['old368_to_enlarged_child'])or not np.array_equal(newq,central['new_position_indices']):raise ValueError('Position and corner chart changed')
    n=len(central['all_original_and_new_position_indices']);Pi=exact(central,'full_canonical_momentum')
    V,C=exact(central,'central_gauge_position_map'),exact(central,'central_gauge_Gauss_map')
    R=exact(jacobi,'actual_enlarged_seven_field');oldR=exact(seven,'actual_complete_seven_response')
    if R.nrows()!=746 or R.ncols()!=7 or n!=217 or V.ncols()!=9:raise ValueError('Full retained D4 and seven rights required')
    embed=acb_mat(746,7)
    for i in range(252):
        for j in range(7):embed[i,j]=oldR[i,j]
    for i,dest in enumerate(oldmap):
        for j in range(7):embed[252+int(dest),j]=oldR[252+i,j]
    Rdefect=_upper(R-embed);GaussRdefect=_upper(R-exact(gauss,'actual_same_seven_field'))
    if max(Rdefect,GaussRdefect)>1e-30:raise ValueError('Momentum and Gauss applications must use the identical retained seven rights')
    oldHR=exact(oldapp,'phase_Hessian_on_actual_right');newHR=exact(newapp,'phase_Hessian_on_actual_right')
    if oldHR.nrows()!=210 or newHR.nrows()!=118 or oldHR.ncols()!=7 or newHR.ncols()!=7:raise ValueError('All old and new velocity Hessian rows required')
    dPi=acb_mat(n,7)
    for i,dest in enumerate(oldmap[:158]):
        for j in range(7):dPi[int(dest),j]=oldHR[i,j]
    for i,dest in enumerate(newq):
        for j in range(7):dPi[int(dest),j]=newHR[59+i,j]
    phase=load_profile_preserving_phase('artifacts/muon_inherited_finite_normal_phase_20261011/run_1',repository=root);pins.update(phase['input_hashes'])
    original=np.asarray(target['original252_to_augmented368'],int)
    rawR=_matrix(phase['coordinates']['lift'])*rows(R,252+oldmap[original]);dH=rows(rawR,np.arange(260,264))
    TY=_matrix(higgs_u2_real_representation()['real_generators'][3])
    profiles=read(f'{RADIAL}/literal_MP_radial_complex192_run_2/degree_04_literal_MP_radial_profiles_and_derivative_complex.npz')
    wall=_matrix(profiles['wall_values_high'])+_matrix(profiles['wall_values_low'])
    Hindices=oldmap[original[102:106]]
    dVcontact=acb_mat(9,7);dV_H=acb_mat(36,7)
    for p in range(9):
        variation=-TY*dH*wall[0,p]
        for a,dest in enumerate(Hindices):
            for j in range(7):
                dV_H[4*p+a,j]=variation[a,j];dVcontact[p,j]+=variation[a,j]*Pi[int(dest),0]
    dQmomentum=V.transpose()*dPi;dQ=dQmomentum+dVcontact
    KG=exact(gauss,'actual_native_Gauss_Kz_trial');rG=exact(gauss,'actual_primal_Gauss_r')
    rGdefect=_upper(rG-exact(central,'full_primal_Gauss_r'))
    projected=C.transpose()*KG;linearized=dQ+projected
    r=C.transpose()*rG;primalQ=exact(central,'actual_primal_initial_corner_charge')
    affineQ=acb_mat(dQ);affineG=acb_mat(projected)
    for i in range(9):affineQ[i,0]+=primalQ[i,0];affineG[i,0]+=r[i,0]
    required=dQ*0
    for i in range(9):required[i,0]=r[i,0]
    chargeDefect=dQ-required;outwardDefect=-dQ+required
    oldbinary=exact(central,'saved_original_binary_Gauss_Kz_central_projection')
    def four(a):
        if a.ncols()!=7:raise ValueError('All original seven split columns required')
        z=acb_mat(a.nrows(),4)
        for i in range(a.nrows()):
            z[i,0]=a[i,0]
            for j in range(3):z[i,1+j]=a[i,1+j]+a[i,4+j]
        return z
    values=dict(actual_retained_seven_fields=R,actual_full_momentum_variation=dPi,actual_raw_Higgs_variation=dH,
        actual_central_gauge_map_Higgs_variation=dV_H,actual_momentum_corner_variation=dQmomentum,
        actual_gauge_map_contact_corner_variation=dVcontact,actual_total_initial_corner_charge_variation=dQ,
        actual_future_arm_initial_outward_flux_variation=-dQ,actual_native_full_Gauss_Kz=KG,
        actual_native_central_Gauss_Kz_projection=projected,linearized_primary_Noether_rows=linearized,
        actual_primal_initial_corner_charge=primalQ,actual_primal_central_Gauss_projection=r,
        actual_affine_seven_initial_corner_charge=affineQ,actual_affine_seven_Gauss_charge=affineG,
        actual_affine_seven_primary_Noether_rows=affineQ+affineG,
        actual_combined_four_initial_corner_charge_variation=four(dQ),
        actual_combined_four_native_central_Gauss_Kz_projection=four(projected),
        actual_combined_four_affine_initial_corner_charge=four(affineQ),
        actual_combined_four_affine_Gauss_charge=four(affineG),
        actual_combined_four_affine_primary_Noether_rows=four(affineQ+affineG),
        required_affine_defect_initial_corner_charge_variation=required,
        actual_charge_variation_minus_affine_required=chargeDefect,
        actual_future_arm_outward_variation_minus_affine_required=outwardDefect,
        saved_original_binary_Gauss_Kz_central_projection=oldbinary,
        native_minus_saved_original_binary_Gauss_Kz_central_projection=projected-oldbinary,
        native_primal_Gauss_minus_central_primal_archive=rG-exact(central,'full_primal_Gauss_r'))
    arrays=dict(coordinate_time=target['coordinate_time'],master368=target['master368'],central_profile_indices=np.arange(9),
        old368_to_enlarged_child=oldmap,new_position_indices=newq,Higgs_position_indices=Hindices)
    for k,a in values.items():arrays[k+'_high'],arrays[k+'_low']=_split(a);arrays.update(ex.export_acb_exact_dyadic(a,k+'_exact'))
    path=out/'actual_native_seven_central_linearized_corner_and_Gauss.npz';_compressed_npz(path,arrays)
    pin(Path(__file__));pin('src/bhsm/interface/muon_intrinsic_higgs_gauge_action.py')
    report=dict(classification='ACTUAL_ORIGINAL_EA02_NATIVE_SEVEN_CENTRAL_LINEARIZED_SOURCE_CORNER',degree=4,
        source_sha256=sha256(producer).hexdigest(),input_and_source_hashes=dict(sorted(pins.items())),
        archive=dict(name=path.name,sha256=sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size),arithmetic_precision_bits=256,
        same_seven_embedding_upper=Rdefect,independent_Gauss_seven_identity_upper=GaussRdefect,same_primal_Gauss_reproduction_upper=rGdefect,
        independent_linearized_primary_Noether_upper=_upper(linearized),independent_affine_primary_Noether_upper=_upper(affineQ+affineG),
        actual_momentum_corner_variation_upper=_upper(dQmomentum),actual_gauge_map_contact_corner_variation_upper=_upper(dVcontact),
        actual_total_initial_corner_charge_variation_upper=_upper(dQ),actual_native_central_Gauss_Kz_upper=_upper(projected),
        actual_affine_seven_Gauss_charge_upper=_upper(affineG),actual_charge_variation_minus_affine_required_upper=_upper(chargeDefect),
        actual_combined_four_affine_Gauss_charge_upper=_upper(four(affineG)),
        independent_combined_four_affine_primary_Noether_upper=_upper(four(affineQ+affineG)),
        native_minus_saved_original_binary_Gauss_Kz_central_projection_upper=_upper(projected-oldbinary),
        every_old_and_new_velocity_Hessian_row_retained=True,independent_all60_Gauss_Hessian_rows_consumed=True,
        deltaV_Higgs_contact_retained_once=True,central_Gauss_map_field_independent=True,
        profiles_are_fixed_retained_parameter_chart_not_unknown_physical_domain=True,
        primal_rG_and_linearized_KG_R_and_affine_sum_kept_separate=True,primal_added_once_to_affine_column0=True,
        original_seven_to_four_retarded_plus_homogeneous_combination_retained=True,
        canonical_charge_is_Pi_pairing=True,future_arm_initial_outward_conormal_sign=-1,
        no_action_or_field_or_source_history_sampling_replayed=True,no_Rdot_needed_for_primary_charge=True,
        original_prefix_cell7_complete_density_time_derivative_admitted=False,
        full_SU2_source_corner_evaluated=False,native_means_material_precision_not_graded_operator=True,
        full_retarded_domain_and_exterior_evaluated=False,physical_outgoing_Y_R=None,physical_affine_s_R=None,physical_C0_Cj=None,
        physical_full_derivative_pass=False,physical_radial_convergence=False,physical_Maxwell226_after_pass=False,
        normalized_two_spin_state=False,physical_muon_magnetic_moment=None,Gauss_retraction_applied=False,original_coupled_corrections=0)
    (out/'result.json').write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({k:report[k]for k in('independent_linearized_primary_Noether_upper','actual_total_initial_corner_charge_variation_upper','actual_affine_seven_Gauss_charge_upper','native_minus_saved_original_binary_Gauss_Kz_central_projection_upper')}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',type=Path,default=ROOT)
    for key in('central-folder','jacobi-folder','seven-clock-folder','gauss-folder','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();run(a.repository,a.central_folder,a.jacobi_folder,a.seven_clock_folder,a.gauss_folder,a.output)
