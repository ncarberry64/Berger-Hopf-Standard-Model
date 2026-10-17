"""Complete same-ea0260x7 Gauss clock from independent36 and cached24.

Mechanical rawm labels select exact cached direct-action hH_R/H_Rdot
operands. The temporal36 are independently differentiated polynomials.
No action, history, response or cap calculation is repeated.
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
CLOCK=CURRENT+'/actual_same_cut_native_MP_matrixfree_continuous_clock_run_1/actual_continuous_phase210_clock_and_same_owner_point_density_rate.npz'
RADIAL='artifacts/muon_baton_zoo_radial_convergence_20261014'


def run(repository,seven_clock_folder,coefficient_folder,central_folder,gauss_folder,temporal_folder,output):
    root,sdir,cdir,pdir,gdir,tdir,out=map(lambda p:Path(p).resolve(),(repository,seven_clock_folder,coefficient_folder,central_folder,gauss_folder,temporal_folder,output))
    out.mkdir(parents=True,exist_ok=False);producer=Path(__file__).read_bytes();(out/'executed_producer.py').write_bytes(producer);pins={}
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
    from bhsm.interface.muon_stored_admission_correction import _matrix,_upper
    from bhsm.interface.muon_stored_fiber_canonical_tangent import _split
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
    ctx.prec=256
    module('bhsm_baton_zoo_exact_acb_packets',RUNTIME+'/bhsm_baton_zoo_exact_acb_packets_imported_runtime.py')
    ex=module('bhsm_exact_action_balls',RUNTIME+'/bhsm_exact_action_balls_imported_runtime.py')
    def exact(z,k):return ex.parse_acb_exact_dyadic(z,k+'_exact')
    def rows(a,ids):return acb_mat([[a[int(i),j]for j in range(a.ncols())]for i in ids])
    def metadata(folder,sha):
        m=read(folder/'result.json')
        if m['source_sha256']!=sha or sha256(pin(folder/'executed_producer.py').read_bytes()).hexdigest()!=sha:raise ValueError('Frozen reviewed producer required')
        return m
    def archive(folder,meta,name=None):
        name=meta['archive']['name']if name is None else name;p=folder/name;receipt=meta['archives'][name]if 'archives'in meta else meta['archive']
        if sha256(pin(p).read_bytes()).hexdigest()!=receipt['sha256']:raise ValueError('Exact frozen archive bytes required')
        return read(p)
    sm=metadata(sdir,'95a64f63e2a541abf698ce7e65afc75a3f4eddb5932f239b74458a171e5be1be')
    cm=metadata(cdir,'c744590f986e47c946f128641b071808f527d230ba60fc2fa70adf87d351c851')
    pm=metadata(pdir,'56c5dc1d082e01e2903d544f327ebf16e64155125e01af0601c2c7038c55aa47')
    gm=metadata(gdir,'519371278ad0884047147d7b97364d2af7f5f7ae145d15cda1549b56cce35902')
    tm=metadata(tdir,'a0634e1b7d31568bf2485ce26cbd961bb2bf63475f972a43bc6e63bda7f07efd')
    if not sm['admitted_original210_and_frame7_clock']:raise ValueError('Actual old210 response clock must pass its unchanged original equations')
    last=sm['records'][-1]
    if max(last['original210_linearized_clock_upper'],last['frame7_upper'])>2e-10:raise ValueError('Actual old210 response clock failed')
    clock=read(CLOCK);target=read(TARGET)
    if pins[CLOCK]!='18fcc0d4fa588c4fcd7aaa8822be76c132b660e0a2f223f7be55fcb9d8d41290'or pins[TARGET]!='ea02ed6aee45310c5651fef5c8f103e868007d4f125582ab2b64ff7651f76b2b':raise ValueError('Exact native originalCUT required')
    s=archive(sdir,sm,'actual_same_cut_seven_continuous_response_clock.npz')
    oldhR=archive(sdir,sm,'actual_same_cut_phase_h_R_seven.npz')
    final=archive(sdir,sm,f'iteration_{int(last["iteration"]):02d}_fresh_original210_seven_clock.npz')
    a=archive(cdir,cm,'actual_same_ea02_D4_seven_point_density_R_hR.npz');ad=archive(cdir,cm,'actual_same_ea02_D4_seven_point_density_Rdot.npz')
    p,g,t=archive(pdir,pm),archive(gdir,gm),archive(tdir,tm)
    for z in(s,a,ad,p,g,t):
        if not np.array_equal(z['master368'],target['master368'])or z['coordinate_time'].item()!=target['coordinate_time'].item():raise ValueError('No field/source/time epoch splice')
    oldmap=np.asarray(p['old368_to_enlarged_child'],int);n=len(p['all_original_and_new_position_indices'])
    if n!=217 or gm['Gauss_rows']!=60 or tm['temporal_Gauss_rows']!=36:raise ValueError('Full D4 carrier required')
    def embed(z):
        v=acb_mat(746,z.ncols())
        for i in range(252):
            for j in range(z.ncols()):v[i,j]=z[i,j]
        for i,dest in enumerate(oldmap):
            for j in range(z.ncols()):v[252+int(dest),j]=z[252+i,j]
        return v
    guards={}
    guards['R_exact_same_cut_embedding']=_upper(embed(exact(s,'actual_complete_seven_response'))-exact(a,'actual_complete_right'))
    guards['Rdot_exact_same_cut_embedding']=_upper(embed(exact(s,'actual_complete_seven_response_clock'))-exact(ad,'actual_complete_right'))
    guards['h_exact_native_embedding']=_upper(embed(exact(clock,'actual_total_master_clock_direction'))-exact(a,'actual_total_clock'))
    guards['old_hR_actual_R_identity']=_upper(exact(oldhR,'actual_right')-exact(s,'actual_complete_seven_response'))
    guards['old_hR_native_h_identity']=_upper(exact(oldhR,'complete_augmented_direction')-exact(clock,'actual_total_master_clock_direction'))
    guards['old_hR_reference_clock_identity']=_upper(exact(oldhR,'reference_direction')-exact(a,'reference_clock_once'))
    guards['final_H_Rdot_actual_Rdot_identity']=_upper(exact(final,'actual_right')-exact(s,'actual_complete_seven_response_clock'))
    if max(guards.values())>1e-30:raise ValueError('Actual full source/R/h/Rdot/ref clock identities required')
    tests=np.asarray(oldhR['test_full_action_indices'],int)
    if not np.array_equal(tests,252+np.arange(158,368))or not np.array_equal(final['test_full_action_indices'],tests):raise ValueError('All original210 phase rows/order required')
    phase=load_profile_preserving_phase('artifacts/muon_inherited_finite_normal_phase_20261011/run_1',repository=root);pins.update(phase['input_hashes']);P=np.asarray(phase['coordinates']['lift'])
    originals=[];raw_scales=[]
    for rawrow in range(74,98):
        indices=np.flatnonzero(P[rawrow]!=0)
        if len(indices)!=1:raise ValueError('Each original lapse/shift coefficient must have one owned literal coordinate label')
        originals.append(int(indices[0]));raw_scales.append(P[rawrow,indices[0]])
    original=np.asarray(originals,int);oldchild=np.asarray(target['original252_to_augmented368'],int)[original]
    test_lookup={int(v):i for i,v in enumerate(tests)};oldrows=np.asarray([test_lookup[252+int(v)]for v in oldchild],int)
    mech=oldmap[oldchild]-2*n;temporal=np.setdiff1d(np.arange(60),mech)
    if len(np.unique(mech))!=24 or np.any(mech<0)or np.any(mech>=60)or len(temporal)!=36:raise ValueError('Exact24 mechanical and36 temporal Gauss coordinate partition required')
    phasepacket=read(RADIAL+'/actual_common_cut_degree4_complete_phase_blocks_run_1/actual_same_current_complete_phase_and_literal_temporal_generator_operands.npz')
    Z=_matrix(phasepacket['actual_literal_temporal_generators_high'])+_matrix(phasepacket['actual_literal_temporal_generators_low']);Cg=rows(Z,np.arange(n,Z.nrows()))
    if Cg.nrows()!=60 or Cg.ncols()!=36 or _upper(rows(Cg,mech))!=0:raise ValueError('Mechanical constraints must not be confused with temporal gauge parameters')
    Ctemp=rows(Cg,temporal)
    if any(sum(Ctemp[i,j]!=0 for i in range(36))!=1 for j in range(36))or any(sum(Ctemp[i,j]!=0 for j in range(36))!=1 for i in range(36)):raise ValueError('Actual temporal parameter/coordinate incidence must be an invertible named diagonal/permutation scaling')
    # Coordinate-covector conversion only: no field/equation is solved.
    Mtemp=Ctemp.transpose().solve(exact(t,'independent_literal_temporal_Gauss_h_H_R'))
    Dtemp=Ctemp.transpose().solve(exact(t,'independent_literal_temporal_Gauss_H_Rdot'))
    Mmechanical=rows(exact(oldhR,'phase_Hessian_first_on_actual_right'),oldrows)
    Dmechanical=rows(exact(final,'phase_Hessian_on_actual_right'),oldrows)
    M,D=acb_mat(60,7),acb_mat(60,7)
    for k,row in enumerate(mech):
        for j in range(7):M[int(row),j],D[int(row),j]=Mmechanical[k,j],Dmechanical[k,j]
    for k,row in enumerate(temporal):
        for j in range(7):M[int(row),j],D[int(row),j]=Mtemp[k,j],Dtemp[k,j]
    total=M+D;Gt=exact(p,'full_primal_Gauss_total_clock');rG=exact(g,'actual_primal_Gauss_r');KG=exact(g,'actual_native_Gauss_Kz_trial')
    affine=acb_mat(total)
    for i in range(60):affine[i,0]+=Gt[i,0]
    oldGauss=np.arange(316,368);oldGaussRows=oldGauss-158;d4OldGauss=oldmap[oldGauss]-2*n
    oldtotal=rows(exact(oldhR,'phase_Hessian_first_on_actual_right')+exact(final,'phase_Hessian_on_actual_right'),oldGaussRows)
    oldGt=rows(exact(clock,'phase_gradient_first'),oldGaussRows)
    oldr=rows(exact(clock,'phase_gradient'),oldGaussRows)
    guards['old52_primal_r_preservation']=_upper(rows(rG,d4OldGauss)-oldr)
    guards['old52_primal_clock_preservation']=_upper(rows(Gt,d4OldGauss)-oldGt)
    guards['old52_H_R_preservation']=_upper(rows(KG,d4OldGauss)-rows(exact(oldhR,'phase_Hessian_on_actual_right'),oldGaussRows))
    guards['old52_mixed_total_clock_preservation']=_upper(rows(total,d4OldGauss)-oldtotal)
    mechanical_control=rows(exact(final,'original210_clock_rows'),oldrows)
    guards['mechanical_affine_rows_vs_cached_fresh_control']=_upper(rows(affine,mech)-mechanical_control)
    guards['temporal_parameter_covector_conversion']=_upper(Cg.transpose()*total-exact(t,'independent_literal_temporal_Gauss_variation_total_clock'))
    first_native=rows(exact(oldhR,'phase_Hessian_on_actual_right'),oldrows)
    values=dict(actual_complete_seven_fields=exact(a,'actual_complete_right'),actual_complete_seven_field_clock=exact(ad,'actual_complete_right'),
        full60_primal_Gauss_r=rG,full60_primal_Gauss_total_clock=Gt,full60_Gauss_H_R=KG,
        cached_direct_action_mechanical24_h_H_R=Mmechanical,cached_direct_action_mechanical24_H_Rdot=Dmechanical,
        mechanical24_direct_action_first_H_R=first_native,
        complete60_Gauss_h_H_R=M,complete60_Gauss_H_Rdot=D,complete60_Gauss_variation_total_clock=total,
        complete60_affine_seven_Gauss_clock_rows=affine,cached_old52_direct_action_Gauss_variation_total_clock=oldtotal,
        old52_completed_minus_cached_mixed_clock=rows(total,d4OldGauss)-oldtotal,
        mechanical24_affine_clock_rows=rows(affine,mech),temporal36_affine_clock_rows=rows(affine,temporal),
        actual_temporal36_parameter_to_coordinate_covector=Ctemp)
    combined=acb_mat(60,4)
    for i in range(60):
        combined[i,0]=affine[i,0]
        for j in range(3):combined[i,1+j]=affine[i,1+j]+affine[i,4+j]
    values['complete60_combined_four_affine_Gauss_clock_rows']=combined
    arrays=dict(master368=target['master368'],coordinate_time=target['coordinate_time'],raw_mechanical_rows=np.arange(74,98),
        original252_mechanical_coordinate_labels=original,raw_to_original_mechanical_scales=np.asarray(raw_scales),old368_mechanical_coordinate_labels=oldchild,
        old210_mechanical_test_rows=oldrows,complete60_mechanical_rows=mech,complete60_temporal_rows=temporal,old52_rows_in_complete60=d4OldGauss,
        original_prefix_cell7_complete_density_time_derivative_admitted=np.asarray(False))
    for key,m in values.items():arrays[key+'_high'],arrays[key+'_low']=_split(m);arrays.update(ex.export_acb_exact_dyadic(m,key+'_exact'))
    path=out/'actual_complete60_Gauss_mixed_source_clock_operands.npz';_compressed_npz(path,arrays);pin(Path(__file__))
    report=dict(classification='ACTUAL_COMPLETE60_SAME_EA02_GAUSS_MIXED_SOURCE_CLOCK',source_sha256=sha256(producer).hexdigest(),input_and_source_hashes=dict(sorted(pins.items())),
        archive=dict(name=path.name,sha256=sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size),arithmetic_precision_bits=256,exact_operand_guards_and_crosschecks_upper=guards,
        old210_mechanical_row_labels=oldrows.tolist(),complete60_mechanical_row_labels=mech.tolist(),
        actual_full60_Gauss_variation_clock_upper=_upper(total),actual_mechanical24_Gauss_variation_clock_upper=_upper(Mmechanical+Dmechanical),
        actual_complete60_affine_clock_rows_upper=_upper(affine),actual_mechanical24_affine_clock_rows_upper=_upper(rows(affine,mech)),
        actual_temporal36_affine_clock_rows_upper=_upper(rows(affine,temporal)),actual_combined_four_affine_clock_rows_upper=_upper(combined),
        temporal36_independently_differentiated_polynomial=True,mechanical24_extracted_from_cached_direct_action_mixed_and_Rdot_operands=True,
        mechanical24_only_equation_controls_used=False,mechanical24_independent_literal_polynomial_check=False,
        all60_actual_mixed_source_clock_operands_evaluated=True,all60_independent_literal_derivative_check=False,
        exact_raw_m_labels_not_assumed_row_ranges=True,coordinate_covector_conversion_not_equation_solve=True,
        actual_sourceDot_and_reference_clock_retained_once=True,primal_Gt_added_once_only_affine_column0=True,
        old52_and_new8_clock_rows_kept_separate=True,no_cap_action_Hessian_or_history_or_response_replay=True,
        actual_complete60_affine_clock_satisfied=bool(_upper(affine)<=2e-10),original_prefix_cell7_protocol_retroactively_admitted=False,
        full_physical_outgoing_derivative_pass=False,physical_radial_solution_convergence=False,physical_Maxwell226_after_pass=False,
        physical_normalized_two_spin_state=False,physical_muon_magnetic_moment=None,original_coupled_corrections=0)
    (out/'result.json').write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({k:report[k]for k in('actual_full60_Gauss_variation_clock_upper','actual_complete60_affine_clock_rows_upper','actual_mechanical24_affine_clock_rows_upper','actual_temporal36_affine_clock_rows_upper')}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',type=Path,default=ROOT)
    for key in('seven-clock-folder','coefficient-folder','central-folder','gauss-folder','temporal-folder','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();run(a.repository,a.seven_clock_folder,a.coefficient_folder,a.central_folder,a.gauss_folder,a.temporal_folder,a.output)
