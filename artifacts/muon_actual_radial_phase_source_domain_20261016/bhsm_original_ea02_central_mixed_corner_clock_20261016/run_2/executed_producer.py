"""Independent central9x7 mixed corner clock from complete217 momenta.

Differentiates Q=V(H)^T Pi explicitly, with all four mixed product terms.
The independent literal36 temporal Gauss clock is read only AFTER that
contraction. No Noether identity, new AD, source/history/action replay or
zero response-rate assignment supplies the evaluated corner clock.
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
CURRENT='artifacts/muon_baton_zoo_maximal_current_realization_20261013'
RUNTIME=CURRENT+'/actual_new620_fresh_native_MP_new_exact_R7_clock_control_run_1'
TARGET=CURRENT+'/actual_linear_cut_compatible368_MP_full_operator_blocked_run_2/actual_precise_direct_CHILD620_and_full368_canonical_source_operands.npz'
RADIAL='artifacts/muon_baton_zoo_radial_convergence_20261014'


def run(repository,cauchy_folder,coefficient_folder,central_folder,temporal_folder,output):
    root,qdir,cdir,pdir,tdir,out=map(lambda p:Path(p).resolve(),(repository,cauchy_folder,coefficient_folder,central_folder,temporal_folder,output))
    out.mkdir(parents=True,exist_ok=False);producer=Path(__file__).read_bytes();(out/'executed_producer.py').write_bytes(producer);pins={}
    def pin(path,expected=None):
        p=Path(path);p=p if p.is_absolute()else root/p
        key=p.relative_to(root).as_posix()if p.is_relative_to(root)else str(p);h=sha256(p.read_bytes()).hexdigest()
        if expected is not None and h!=expected:raise ValueError('Frozen source/epoch changed '+key)
        pins[key]=h;return p
    def read(path,expected=None):
        p=pin(path,expected)
        if p.suffix=='.json':return json.loads(p.read_bytes())
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    def module(name,path):
        p=pin(path);s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
    sys.path[:0]=[str(root/'src'),str(root/'scripts')]
    from flint import ctx,acb_mat
    from bhsm.interface.muon_stored_admission_correction import _matrix,_upper
    from bhsm.interface.muon_stored_fiber_canonical_tangent import _split
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
    from bhsm.interface.muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
    ctx.prec=288
    module('bhsm_baton_zoo_exact_acb_packets',RUNTIME+'/bhsm_baton_zoo_exact_acb_packets_imported_runtime.py')
    ex=module('bhsm_exact_action_balls',RUNTIME+'/bhsm_exact_action_balls_imported_runtime.py')
    def exact(z,k):return ex.parse_acb_exact_dyadic(z,k+'_exact')
    def rows(a,indices):return acb_mat([[a[int(i),j]for j in range(a.ncols())]for i in indices])
    def metadata(folder,expected):
        m=read(folder/'result.json')
        if m['source_sha256']!=expected:raise ValueError('Exact reviewed producer required')
        pin(folder/'executed_producer.py',expected);return m
    def archive(folder,meta,name=None):
        name=meta['archive']['name']if name is None else name;receipt=meta['archives'][name]if'archives'in meta else meta['archive']
        return read(folder/name,receipt['sha256'])
    qm=metadata(qdir,'63d04359f42673671169f61bcfa395b04fe5008c05912b65c95090c0a4458942')
    cm=metadata(cdir,'c744590f986e47c946f128641b071808f527d230ba60fc2fa70adf87d351c851')
    pm=metadata(pdir,'56c5dc1d082e01e2903d544f327ebf16e64155125e01af0601c2c7038c55aa47')
    tm=metadata(tdir,'a0634e1b7d31568bf2485ce26cbd961bb2bf63475f972a43bc6e63bda7f07efd')
    if max(tm['independent_H_R_vs_native_all60_projection_upper'],tm['independent_SU2_Gauss_clock_plus_direct_charge_clock_upper'])>2e-10:
        raise ValueError('Previously independent literal36/central-first and SU2 mixed-clock controls must pass')
    q=archive(qdir,qm);a=archive(cdir,cm,'actual_same_ea02_D4_seven_point_density_R_hR.npz')
    ad=archive(cdir,cm,'actual_same_ea02_D4_seven_point_density_Rdot.npz');p=archive(pdir,pm)
    target=read(TARGET,'ea02ed6aee45310c5651fef5c8f103e868007d4f125582ab2b64ff7651f76b2b')
    for z in(q,a,ad,p):
        if not np.array_equal(z['master368'],target['master368'])or z['coordinate_time'].item()!=target['coordinate_time'].item():raise ValueError('No source/field/clock epoch splice')
    guards={}
    guards['complete_R_same_coefficient_germ']=_upper(exact(q,'exact_carried_full_D4_field_seven')-exact(a,'actual_complete_right'))
    guards['complete_Rdot_same_coefficient_germ']=_upper(exact(q,'exact_carried_full_D4_field_seven_clock')-exact(ad,'actual_complete_right'))
    if max(guards.values())>1e-25:raise ValueError('Actual full source and response-rate operands must match')
    if int(q['enlarged_dynamic_count'])!=217 or pm['degree']!=4 or pm['central_parameter_count']!=9:raise ValueError('Actual full217/central9 chart required')
    phase=load_profile_preserving_phase('artifacts/muon_inherited_finite_normal_phase_20261011/run_1',repository=root);pins.update(phase['input_hashes'])
    lift=np.asarray(phase['coordinates']['lift'])
    for i in range(4):
        if not np.array_equal(np.flatnonzero(lift[260+i]),[102+i])or lift[260+i,102+i]!=1:raise ValueError('Literal original Higgs coordinate inclusion required')
    embedding=np.asarray(q['old368_to_complete_D4_child'],int)
    hpos=embedding[np.asarray(target['original252_to_augmented368'],int)[102:106]]
    if len(np.unique(hpos))!=4 or np.any(hpos>=217):raise ValueError('Exact old/new Higgs position incidence required')
    raw=exact(a,'raw_child');rawh=exact(a,'raw_child_h');rawR=exact(a,'raw_child_R');rawhR=exact(a,'raw_child_hR');rawRd=exact(ad,'raw_child_R')
    H=acb_mat([[raw[0,260+i]]for i in range(4)]);Hh=acb_mat([[rawh[0,260+i]]for i in range(4)])
    HR=rows(rawR,np.arange(260,264));HhR=rows(rawhR,np.arange(260,264));HRd=rows(rawRd,np.arange(260,264));HRtotal=HhR+HRd
    guards['raw_H_R_same_canonical_Higgs_rows']=_upper(HR-rows(exact(q,'exact_carried_full_D4_field_seven'),252+hpos))
    # Keep the actually supplied mixed coefficient and response-rate pieces
    # separately; neither is inferred from a conservation identity.
    guards['raw_H_Rdot_same_canonical_Higgs_clock_rows']=_upper(HRd-rows(exact(q,'exact_carried_full_D4_field_seven_clock'),252+hpos))
    HY=_matrix(higgs_u2_real_representation()['real_generators'][3])
    prof=read(RADIAL+'/literal_MP_radial_complex192_run_2/degree_04_literal_MP_radial_profiles_and_derivative_complex.npz')
    phi=_matrix(prof['wall_values_high'])+_matrix(prof['wall_values_low'])
    if phi.ncols()!=9:raise ValueError('Fixed original radial parameter profiles required')
    oldV=exact(p,'central_gauge_position_map');oldVh=exact(p,'central_gauge_position_map_total_clock');C=exact(p,'central_gauge_Gauss_map')
    if oldV.nrows()!=217 or oldV.ncols()!=9 or C.nrows()!=60 or C.ncols()!=9:raise ValueError('Original full gauge-generator chart required')
    expectedC=acb_mat(60,9)
    for j in range(9):expectedC[24+4*j+3,j]=1
    guards['fixed_central_parameter_to_Gauss_incidence']=_upper(C-expectedC)
    V,Vh=acb_mat(oldV),acb_mat(217,9)
    for j in range(9):
        v=-HY*H*phi[0,j];vh=-HY*Hh*phi[0,j]
        for i,row in enumerate(hpos):V[int(row),j],Vh[int(row),j]=v[i,0],vh[i,0]
    guards['explicit_H_generator_same_original_V']=_upper(V-oldV)
    guards['explicit_Hdot_generator_same_original_Vdot']=_upper(Vh-oldVh)
    if max(guards.values())>2e-10:raise ValueError('The exact original fixed profile/Higgs chart must match')
    Pi,Pih,dPi,dPih=(exact(q,k)for k in('complete_D4_primal_momentum','complete_D4_primal_momentum_clock','complete_D4_momentum_seven','complete_D4_momentum_seven_clock'))
    if Pi.nrows()!=217 or dPi.nrows()!=217 or dPi.ncols()!=7:raise ValueError('Every old/new canonical momentum is required')
    Q,Qh=V.transpose()*Pi,Vh.transpose()*Pi+V.transpose()*Pih
    dQ,dQh=V.transpose()*dPi,Vh.transpose()*dPi+V.transpose()*dPih
    dV_Pi,dV_Pih,dVh_Pi=acb_mat(9,7),acb_mat(9,7),acb_mat(9,7)
    dVhR_Pi,dVRd_Pi=acb_mat(9,7),acb_mat(9,7)
    for j in range(9):
        dV=-HY*HR*phi[0,j];dVhR=-HY*HhR*phi[0,j];dVRd=-HY*HRd*phi[0,j]
        for k in range(7):
            for i,row in enumerate(hpos):
                dV_Pi[j,k]+=dV[i,k]*Pi[int(row),0]
                dV_Pih[j,k]+=dV[i,k]*Pih[int(row),0]
                dVhR_Pi[j,k]+=dVhR[i,k]*Pi[int(row),0]
                dVRd_Pi[j,k]+=dVRd[i,k]*Pi[int(row),0]
    dVh_Pi=dVhR_Pi+dVRd_Pi;dQ+=dV_Pi;dQh+=dV_Pih+dVh_Pi
    # No Gauss/charge identity has been used to construct dQ or dQh above.
    t=archive(tdir,tm)
    if not np.array_equal(t['master368'],target['master368'])or t['coordinate_time'].item()!=target['coordinate_time'].item():raise ValueError('Independent temporal clock must be same epoch')
    if not np.array_equal(t['temporal_profile_internal_labels'],np.asarray([(j,c)for j in range(9)for c in range(4)])):raise ValueError('Exact literal36 named parameter order required')
    central=np.arange(9)*4+3;Gfirst=rows(exact(t,'independent_literal_temporal_Gauss_H_R'),central)
    Gh=rows(exact(t,'independent_literal_temporal_Gauss_variation_total_clock'),central)
    primary=dQ+Gfirst;mixed=dQh+Gh
    guards['primal_charge_same_original_corner']=_upper(Q-exact(p,'actual_primal_initial_corner_charge'))
    guards['primal_charge_clock_same_original_corner']=_upper(Qh-exact(p,'actual_initial_corner_charge_total_clock'))
    Gprimal=exact(p,'actual_Gauss_charge_total_clock');affineqh,affineGh=acb_mat(dQh),acb_mat(Gh)
    required=acb_mat(9,7)
    for j in range(9):affineqh[j,0]+=Qh[j,0];affineGh[j,0]+=Gprimal[j,0];required[j,0]=Gprimal[j,0]
    def four(m):
        z=acb_mat(9,4)
        for i in range(9):
            z[i,0]=m[i,0]
            for j in range(3):z[i,1+j]=m[i,1+j]+m[i,4+j]
        return z
    values=dict(complete_central9_V=V,complete_central9_Vdot=Vh,fixed_central9_Gauss_map=C,
        actual_raw_H=H,actual_raw_H_clock=Hh,actual_raw_H_R=HR,actual_raw_H_hR=HhR,actual_raw_H_Rdot=HRd,actual_raw_H_R_total_clock=HRtotal,
        actual_central9_primal_Q=Q,actual_central9_primal_Qdot=Qh,actual_central9_delta_Q=dQ,actual_central9_delta_Qdot=dQh,
        actual_central9_delta_Qdot_Vdot_deltaPi=Vh.transpose()*dPi,actual_central9_delta_Qdot_V_deltaPidot=V.transpose()*dPih,
        actual_central9_delta_Q_deltaV_Pi=dV_Pi,actual_central9_delta_Qdot_deltaV_Pidot=dV_Pih,
        actual_central9_delta_Qdot_deltaVdot_Pi=dVh_Pi,actual_central9_delta_Qdot_deltaV_hR_Pi=dVhR_Pi,
        actual_central9_delta_Qdot_deltaV_Rdot_Pi=dVRd_Pi,
        independent_literal_central9_Gauss_H_R=Gfirst,independent_literal_central9_Gauss_clock=Gh,
        independent_central9_linearized_primary=primary,independent_central9_mixed_primary=mixed,
        future_arm_initial_outward_delta_Qdot=-dQh,required_affine_central9_delta_Qdot=required,
        actual_affine_seven_central9_corner_clock=affineqh,actual_affine_seven_central9_Gauss_clock=affineGh,
        actual_combined_four_affine_central9_Gauss_clock=four(affineGh),actual_affine_central9_clock_balance=affineqh+affineGh)
    arrays=dict(master368=target['master368'],coordinate_time=target['coordinate_time'],central9_rows_in_temporal36=central,
        central_Higgs_position_rows=hpos,fixed_wall_phi_high=prof['wall_values_high'],fixed_wall_phi_low=prof['wall_values_low'])
    for k,m in values.items():arrays[k+'_high'],arrays[k+'_low']=_split(m);arrays.update(ex.export_acb_exact_dyadic(m,k+'_exact'))
    path=out/'independent_central9x7_mixed_source_corner_clock.npz';_compressed_npz(path,arrays)
    for k,m in list(sys.modules.items()):
        f=getattr(m,'__file__',None)
        if f and k.startswith('bhsm.')and Path(f).resolve().is_relative_to(root):pin(Path(f).resolve())
    pin(Path(__file__))
    report=dict(classification='INDEPENDENT_CENTRAL9_BY7_MIXED_CORNER_CLOCK_FROM_COMPLETE217_MOMENTA',source_sha256=sha256(producer).hexdigest(),
        input_and_source_hashes=dict(sorted(pins.items())),archive=dict(name=path.name,sha256=sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size),
        arithmetic_precision_bits=288,central_parameters=9,rights=7,complete_momentum_rows=217,exact_source_and_chart_guards=guards,
        independent_central9_first_primary_upper=_upper(primary),independent_central9_mixed_primary_upper=_upper(mixed),
        independent_central9_first_and_mixed_check_pass=bool(max(_upper(primary),_upper(mixed))<=2e-10),
        actual_delta_Qdot_upper=_upper(dQh),actual_independent_central_Gauss_clock_upper=_upper(Gh),
        actual_deltaVdot_Pi_contact_upper=_upper(dVh_Pi),actual_deltaV_Pidot_contact_upper=_upper(dV_Pih),
        actual_deltaV_hR_Pi_contact_upper=_upper(dVhR_Pi),actual_deltaV_Rdot_Pi_contact_upper=_upper(dVRd_Pi),
        actual_affine_seven_central_Gauss_clock_upper=_upper(affineGh),actual_affine_column0_central_Gauss_clock_upper=_upper(rows(affineGh.transpose(),[0])),
        actual_combined_four_central_Gauss_clock_upper=_upper(four(affineGh)),
        original_fixed_phi_and_Higgs_coordinate_map_derived_not_new_native_chart=True,
        central_gauge_part_constant_from_original_fixed_parameter_owner=True,
        complete217_primal_variation_and_clock_momenta_used=True,all_four_mixed_Q_product_contacts_retained=True,
        actual_hR_and_Rdot_Higgs_contacts_supplied_separately=True,
        no_Noether_identity_or_Gauss_result_used_to_construct_corner_clock=True,
        independent_literal_Gauss_clock_compared_only_after_momentum_contraction=True,
        all36_independent_corner_clock_checks_completed_with_previous_SU2_27=True,
        no_AD_action_source_history_or_field_solve_replayed=True,affine_primal_clock_added_once_column0=True,
        actual_affine_central_Gauss_clock_satisfied=bool(_upper(affineGh)<=2e-10),
        microscopic_native_graded_current_or_physical_charge_units_evaluated=False,
        physical_full_outgoing_energy_field_source_domain_derivative_pass=False,physical_radial_solution_convergence=False,
        original_coupled_corrections=0,physical_Maxwell_all226_after_pass=False,physical_normalized_two_spin_state=None,physical_muon_magnetic_moment=None)
    (out/'result.json').write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({k:report[k]for k in('independent_central9_first_primary_upper','independent_central9_mixed_primary_upper','actual_deltaVdot_Pi_contact_upper','actual_affine_seven_central_Gauss_clock_upper')}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',type=Path,default=ROOT)
    for k in('cauchy-folder','coefficient-folder','central-folder','temporal-folder','output'):p.add_argument('--'+k,type=Path,required=True)
    a=p.parse_args();run(a.repository,a.cauchy_folder,a.coefficient_folder,a.central_folder,a.temporal_folder,a.output)
