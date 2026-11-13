"""Exact finite new59 momentum/Gauss rank and fixed-old-Pi range diagnostic.

Fresh owned gauge velocity maps and native physical Dphi checks are used.
No pseudoinverse, solution, zero free momenta or physical domain is chosen.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import importlib.util
import itertools
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
CURRENT='artifacts/muon_baton_zoo_maximal_current_realization_20261013'
RUNTIME=CURRENT+'/actual_new620_fresh_native_MP_new_exact_R7_clock_control_run_1'
TARGET=CURRENT+'/actual_linear_cut_compatible368_MP_full_operator_blocked_run_2/actual_precise_direct_CHILD620_and_full368_canonical_source_operands.npz'
SEED=CURRENT+'/actual_linear_cut_enlarged_Gauss_Legendre_prolongation_run_2/actual_original_Gauss_and_old_Legendre_complete_current_Cauchy_prolongation.npz'
RADIAL='artifacts/muon_baton_zoo_radial_convergence_20261014'


def run(repository,position_folder,central_folder,coefficient_folder,gauss_folder,output):
    root,pdir,cdir,fdir,gdir,out=map(lambda p:Path(p).resolve(),(repository,position_folder,central_folder,coefficient_folder,gauss_folder,output))
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
    from flint import ctx,acb,acb_mat
    from bhsm.interface.muon_stored_admission_correction import _matrix,_upper
    from bhsm.interface.muon_stored_fiber_canonical_tangent import _split
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
    from bhsm.interface.muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
    ctx.prec=256
    module('bhsm_baton_zoo_exact_acb_packets',RUNTIME+'/bhsm_baton_zoo_exact_acb_packets_imported_runtime.py')
    ex=module('bhsm_exact_action_balls',RUNTIME+'/bhsm_exact_action_balls_imported_runtime.py')
    def exact(z,k):return ex.parse_acb_exact_dyadic(z,k+'_exact')
    def hl(z,k):return _matrix(z[k+'_high'])+_matrix(z[k+'_low'])
    def rows(a,ids):return acb_mat([[a[int(i),j]for j in range(a.ncols())]for i in ids])
    def cols(a,ids):return rows(a.transpose(),ids).transpose()
    def C(v):return v if isinstance(v,acb)else acb(complex(v))
    def metadata(folder,expected):
        m=read(folder/'result.json')
        if m['source_sha256']!=expected or sha256(pin(folder/'executed_producer.py').read_bytes()).hexdigest()!=expected:raise ValueError('Frozen reviewed same-source producer required')
        return m
    def archive(folder,m,name=None):
        name=m['archive']['name']if name is None else name;p=folder/name;r=m['archives'][name]if 'archives'in m else m['archive']
        if sha256(pin(p).read_bytes()).hexdigest()!=r['sha256']:raise ValueError('Actual operand archive changed')
        return read(p)
    pm=metadata(pdir,'d6b0dbb2e34185011f243f7f571da2f536ebc58c6138fab380f856a2f5db96b9')
    cm=metadata(cdir,'56c5dc1d082e01e2903d544f327ebf16e64155125e01af0601c2c7038c55aa47')
    fm=metadata(fdir,'c744590f986e47c946f128641b071808f527d230ba60fc2fa70adf87d351c851')
    gm=metadata(gdir,'519371278ad0884047147d7b97364d2af7f5f7ae145d15cda1549b56cce35902')
    p,c=archive(pdir,pm),archive(cdir,cm);f=archive(fdir,fm,'actual_same_ea02_D4_seven_point_density_R_hR.npz');g=archive(gdir,gm)
    target,seed=read(TARGET),read(SEED)
    if pins[TARGET]!='ea02ed6aee45310c5651fef5c8f103e868007d4f125582ab2b64ff7651f76b2b'or pins[SEED]!='553494b91c4ec85e9cca5791e4a5c506a48701bd8a41d4fff24c83c3f2d2ea33':raise ValueError('Exact original canonical state and seven-source seed required')
    for z in(p,c,f,g):
        if not np.array_equal(z['master368'],target['master368'])or z['coordinate_time'].item()!=target['coordinate_time'].item():raise ValueError('No field/source/epoch splice')
    if seed['authoritative_node_time'].item()!=target['coordinate_time'].item():raise ValueError('Canonical source seed belongs to another cut')
    if pm['degree']!=4 or cm['degree']!=4:raise ValueError('Full actual D4 carrier required')
    maps=read(RADIAL+'/actual_linear_cut_degree4_complete_clock_epoch_maps_run_1/actual_degree_04_complete_clock_covariant_product_epoch_maps.npz')
    native=read(pdir/pm['native_epoch_map_archive']['name'])
    if sha256((pdir/pm['native_epoch_map_archive']['name']).read_bytes()).hexdigest()!=pm['native_epoch_map_archive']['sha256']:raise ValueError('Actual native product maps changed')
    phase=load_profile_preserving_phase('artifacts/muon_inherited_finite_normal_phase_20261011/run_1',repository=root);pins.update(phase['input_hashes']);rep=phase['representation'];P=phase['coordinates']['lift']
    # Reevaluate the actual owned coefficient map. None of its cached binary
    # columns is taken as the rank certificate without this fresh comparison.
    module('bhsm_baton_zoo_compatible_radial_complex',RADIAL+'/compatible_central_all_epochs_run_2/executed_bhsm_baton_zoo_compatible_radial_complex.py')
    literal=module('bhsm_baton_zoo_literal_radial_profile_precision',RADIAL+'/literal_MP_radial_complex192_run_2/executed_bhsm_baton_zoo_literal_radial_profile_precision.py')
    owner=module('actual_ea02_temporal_velocity_owner',RADIAL+'/actual_common_cut_degree4_complete_phase_blocks_run_1/executed_bhsm_baton_zoo_current_covariant_phase_blocks.py')
    freshZ,_=owner.temporal_generators(rep,P,maps,target['raw_pair'],4)
    profiles=literal.literal_profiles(rep,rep['rho'],4,precision=256);wallprofiles=literal.literal_profiles(rep,[float(np.pi/2)],4,precision=256)
    ctx.prec=256
    cached=read(RADIAL+'/actual_common_cut_degree4_complete_phase_blocks_run_1/actual_same_current_complete_phase_and_literal_temporal_generator_operands.npz')
    fresh_vs_cached=_upper(freshZ-hl(cached,'actual_literal_temporal_generators'))
    n=217;V=rows(freshZ,np.arange(n));Cg=rows(freshZ,np.arange(n,freshZ.nrows()))
    if _upper(Cg- acb_mat([[0]*36 for _ in range(24)]+np.eye(36).astype(int).tolist()))!=0:raise ValueError('Exact named fixed temporal coordinate map required')
    oldmap=np.asarray(c['old368_to_enlarged_child'],int);newq=np.asarray(c['new_position_indices'],int);oldq=oldmap[:158]
    B=rows(V,newq).transpose();Bold=rows(B,np.arange(28));Bnew=rows(B,np.arange(28,36))
    # Exact sparse support certifies BOTH an upper rank and nonzero minors.
    # Overlap with zero is NOT exact zero for an acb ball.  Certify all
    # sparse zeros literally, so a zero-containing remainder cannot lower rank.
    if any(not B[i,j].is_zero() and not B[i,j]!=0 for i in range(36)for j in range(59)):
        raise ValueError('Unresolved zero-containing entry cannot certify sparse rank')
    supports=[[j for j in range(59)if not B[i,j].is_zero()]for i in range(36)]
    active=[i for i,support in enumerate(supports)if support]
    if any(len(supports[i])!=1 for i in active):raise ValueError('Actual map is not the evaluated sparse rank-certificate form')
    pivot=[supports[i][0]for i in active]
    if len(set(pivot))!=len(pivot):raise ValueError('Independent sparse pivot certificate is unavailable')
    lower=[float(abs(B[i,j]).lower())for i,j in zip(active,pivot)]
    if not lower or min(lower)<=0:raise ValueError('Every rank pivot must exclude zero as an interval')
    minor=cols(rows(B,active),pivot);det=minor.det();rank=len(active)
    oldactive=[i for i in active if i<28];oldpivot=[supports[i][0]for i in oldactive]
    newactive=[i for i in active if i>=28];newpivot=[supports[i][0]for i in newactive]
    if set(oldpivot)&set(newpivot):raise ValueError('Restricted-new rank needs an explicit coupled-column treatment')
    zero_rows=np.setdiff1d(np.arange(36),active);free=np.setdiff1d(np.arange(59),pivot)
    L=acb_mat(len(zero_rows),36)
    for j,i in enumerate(zero_rows):L[j,int(i)]=1
    if _upper(L*B)!=0 or float(abs(det).lower())<=0:raise ValueError('Exact left-annihilator/nonzero-minor rank certificate failed')
    # Verify that these fresh velocity labels really realize native Dphi at
    # the actual field; a convenient identity coordinate is not substituted.
    full=746;right=acb_mat(full,36)
    for i in range(n):
        for j in range(36):right[252+n+i,j]=V[i,j]
    orig=np.asarray(target['original252_to_augmented368'],int);rawV=_matrix(P)*rows(right,252+oldmap[orig]);extra=np.asarray(maps['extra_coordinates_to_full'],int);extraV=rows(right,extra)
    def mat3(key):
        h,l=native[key+'_high'],native[key+'_low'];return _matrix(h.reshape(-1,len(extra)))+_matrix(l.reshape(-1,len(extra)))
    T=mat3('extra_point_lift');induced=T*extraV;nr=len(rep['rho'])
    gbh,gbl=maps['original_gauge_basis_high'].reshape(nr,80,20),maps['original_gauge_basis_low'].reshape(nr,80,20)
    grh,grl=maps['original_gauge_radial_basis_high'].reshape(nr,80,20),maps['original_gauge_radial_basis_low'].reshape(nr,80,20)
    for ir in range(nr):
        gb=_matrix(gbh[ir])+_matrix(gbl[ir]);gr=_matrix(grh[ir])+_matrix(grl[ir])
        blocks=[gb.transpose()*rows(rawV,np.arange(100,180)),gb.transpose()*rows(rawV,np.arange(180,260)),gr.transpose()*rows(rawV,np.arange(100,180))]
        for block,a0 in enumerate(blocks):
            for i in range(20):
                for j in range(36):induced[60*ir+20*block+i,j]+=a0[i,j]
    point=exact(f,'point');expected=acb_mat(nr*60,36);factor=1/acb(2).sqrt();actionfactor=C(float(1/np.sqrt(2)));factor_difference=abs(factor-actionfactor)
    def comm(a,b,factor):return[factor*(a[1]*b[2]-a[2]*b[1]),factor*(a[2]*b[0]-a[0]*b[2]),factor*(a[0]*b[1]-a[1]*b[0]),C(0)]
    for ir in range(nr):
        for p0 in range(9):
            for a0 in range(4):
                param=[C(int(i==a0))*profiles['values'][ir,p0]for i in range(4)]
                for spatial in range(1,5):
                    image=comm([point[ir,4*spatial+i]for i in range(4)],param,factor)
                    if spatial==1:image[a0]+=profiles['first'][ir,p0]
                    for i in range(4):expected[60*ir+20+4*spatial+i,4*p0+a0]=image[i]
    image_defect=_upper(induced-expected);raw_geo_defect=_upper(rows(rawV,np.arange(100)))
    gens=[_matrix(v)for v in higgs_u2_real_representation()['real_generators']];H=_matrix(target['raw_pair'][1,260:264]);expectedHt=acb_mat(4,36)
    for p0 in range(9):
        for a0 in range(4):
            v=-gens[a0]*H*wallprofiles['values'][0,p0]
            for i in range(4):expectedHt[i,4*p0+a0]=v[i,0]
    Higgs_defect=_upper(rows(rawV,np.arange(264,268))-expectedHt)
    if max(fresh_vs_cached,image_defect,raw_geo_defect,Higgs_defect)>2e-10:raise ValueError('Fresh native gauge velocity image failed its actual physical coefficient checks')
    # Two distinct questions: fixed original canonical Pi, and a change to
    # the actual supplied seven affine Gauss trials at the retained base.
    PioldCanonical=hl(target,'Pi158');PiNative=exact(c,'full_canonical_momentum');Vo=rows(V,oldq)
    PioldNative=rows(PiNative,oldq);PinewNative=rows(PiNative,newq)
    bcanonical=-Vo.transpose()*PioldCanonical;bnative=-Vo.transpose()*PioldNative
    native_primal_check=B*PinewNative-bnative+rows(exact(g,'actual_primal_Gauss_r'),np.arange(24,60))
    btrial=rows(exact(g,'actual_affine_seven_Gauss_trial_residual'),np.arange(24,60))
    obstructionCanonical=L*bcanonical;obstructionTrial=L*btrial
    def obstruction_status(z):
        nonzero=[(i,j)for i in range(z.nrows())for j in range(z.ncols())if float(abs(z[i,j]).lower())>0]
        return dict(upper=_upper(z),certified_nonzero_entries=nonzero,interval_certified_out_of_exact_range=bool(nonzero),within_2e10_range_tolerance=bool(_upper(z)<=2e-10))
    # Existing seven-to-four canonical source span is recorded, not fitted.
    sourcePiOld=rows(hl(seed,'retarded_and_homogeneous_separate316'),np.arange(158,316))
    sourceCokernel=L*Vo.transpose()*sourcePiOld
    sourceField=acb_mat(746,7);parent=hl(seed,'actual_parent_source252');child=hl(seed,'actual_solved_child_field368')
    for i in range(252):
        for j in range(7):sourceField[i,j]=parent[i,j]
    for i,dest in enumerate(oldmap):
        for j in range(7):sourceField[252+int(dest),j]=child[i,j]
    sourceR_defect=_upper(sourceField-exact(f,'actual_complete_right'))
    if sourceR_defect>1e-30:raise ValueError('Canonical source component must belong to the same exact retained seven field columns')
    def four(a0):
        z=acb_mat(a0.nrows(),4)
        for i in range(a0.nrows()):
            z[i,0]=a0[i,0]
            for j in range(3):z[i,1+j]=a0[i,1+j]+a0[i,4+j]
        return z
    missing=31 # profile phi P3, central c3: index is verified from labels.
    if missing not in zero_rows or 4*7+3!=missing:raise ValueError('Evaluated missing new central compatibility label changed')
    old_missing=rows(Vo.transpose(),[missing]);missing_source=old_missing*sourcePiOld
    missing_support=[i for i in range(158)if old_missing[0,i]!=0]
    extra_old=np.asarray(target['extra116_to_full'],int)-252
    named_old=[int(extra_old[i])for i in(3,75,111)]
    if sorted(missing_support)!=sorted(named_old):raise ValueError('Missing phiP3-central row must use the actual old phiP0/phiP2/derivative-phiP1 momenta')
    # Independent rational derivative identity for phi P3.  At the wall
    # phi=(1-y^2)^2=0 exactly, hence its Higgs endpoint image vanishes.
    # The evaluated owner has tiny zero-containing Higgs balls; retain them
    # rather than silently replacing them in V or in any source contraction.
    from bhsm.interface.muon_parent_retarded_hypercharge import WALL
    literal_missing=acb_mat(1,158)
    for i,value in zip(named_old,(C(20)/(3*C(WALL)),C(70)/(3*C(WALL)),C(1))):literal_missing[0,i]=value
    missing_row_difference=old_missing-literal_missing
    if any(not missing_row_difference[0,j].contains(0)for j in range(158)):
        raise ValueError('Literal rational phiP3 derivative identity disagrees with the owned row')
    uncertain_old=[j for j in range(158)if not old_missing[0,j].is_zero()and not old_missing[0,j]!=0]
    # A finite source-component range check, never a choice of source weights.
    # The affine column0 is recorded with the tangent columns, not promoted to
    # a freely adjustable physical port.  q/field/domain contacts are absent
    # from this deliberately fixed-q momentum-component question.
    source4=four(sourceCokernel)
    def certified_minor(a0,size):
        candidates=[]
        for ids in itertools.combinations(range(a0.nrows()),size):
            q=rows(a0,ids);d=q.det();lb=float(abs(d).lower())
            if lb>0:candidates.append((lb,ids,q,d))
        if not candidates:raise ValueError('Requested source component rank has no certified nonzero minor')
        return max(candidates,key=lambda z:z[0])
    source_minor_lower,source_minor_rows,source_minor,source_det=certified_minor(source4,4)
    augmented=acb_mat([[source4[i,j]for j in range(4)]+[obstructionCanonical[i,0]]for i in range(len(zero_rows))])
    augmented_minor_lower,augmented_minor_rows,augmented_minor,augmented_det=certified_minor(augmented,5)
    values=dict(fresh_full_velocity_gauge_map=V,fresh_new59_momentum_to_temporal_Gauss_map=B,
        old28_parameter_rows_on_new59=Bold,new8_parameter_rows_on_new59=Bnew,
        certified_full_rank_pivot_minor=minor,certified_full_rank_pivot_determinant=acb_mat([[det]]),
        exact_left_cokernel_selector=L,fixed_original_old158_canonical_momentum=PioldCanonical,
        native_action_old158_momentum=PioldNative,native_minus_original_old158_momentum=PioldNative-PioldCanonical,
        required_new59_primal_charge_load_fixed_original_oldPi=bcanonical,required_load_fixed_native_oldPi=bnative,
        fixed_original_oldPi_primal_cokernel_obstruction=obstructionCanonical,
        actual_seven_affine_Gauss_load_for_new_momentum_change=btrial,actual_seven_load_cokernel_obstruction=obstructionTrial,
        actual_old28_affine_Gauss_load=rows(btrial,np.arange(28)),actual_new8_affine_Gauss_load=rows(btrial,np.arange(28,36)),
        native_primal_charge_vs_action_Gauss_control=native_primal_check,
        original_seven_old_canonical_momentum_components=sourcePiOld,old_canonical_source_seven_cokernel_image=sourceCokernel,
        old_canonical_source_combined_four_cokernel_image=four(sourceCokernel),
        missing_new_phiP3_central_old_momentum_row=old_missing,missing_new_phiP3_central_canonical_source_seven=missing_source,
        literal_phiP3_central_old_momentum_row=literal_missing,owned_minus_literal_phiP3_central_row=missing_row_difference,
        missing_new_phiP3_central_canonical_source_combined_four=four(missing_source),
        source_four_cokernel_rank_minor=source_minor,source_four_cokernel_rank_determinant=acb_mat([[source_det]]),
        fixed_oldPi_load_augmented_source_four_minor=augmented_minor,fixed_oldPi_load_augmented_source_four_determinant=acb_mat([[augmented_det]]),
        actual_native_point_gauge_velocity_image=induced,actual_direct_native_Dphi_velocity_image=expected)
    arrays=dict(master368=target['master368'],coordinate_time=target['coordinate_time'],new59_position_indices=newq,old158_position_indices=oldq,
        full_pivot_temporal_rows=np.asarray(active),full_pivot_new59_columns=np.asarray(pivot),old28_pivot_new59_columns=np.asarray(oldpivot),
        restricted_new8_pivot_new59_columns=np.asarray(newpivot),unresolved_new59_free_coordinate_labels=free,
        exact_zero_temporal_rows=zero_rows,missing_central_old158_momentum_indices=np.asarray(named_old),
        missing_central_zero_containing_old158_entries=np.asarray(uncertain_old),
        source_four_cokernel_minor_rows=np.asarray(source_minor_rows),fixed_oldPi_augmented_source_four_minor_rows=np.asarray(augmented_minor_rows),
        missing_central_momentum_function_labels=np.asarray(['Ar central phiP0','Ar central phiP2','Ar central d_rho(phiP1)']))
    for key,a0 in values.items():arrays[key+'_high'],arrays[key+'_low']=_split(a0);arrays.update(ex.export_acb_exact_dyadic(a0,key+'_exact'))
    path=out/'actual_new59_momentum_Gauss_rank_range_and_source_span.npz';_compressed_npz(path,arrays);pin(Path(__file__))
    report=dict(classification='ACTUAL_FIXED_CURRENT_SOURCE_NEW59_MOMENTUM_GAUSS_RANK_AND_RANGE',source_sha256=sha256(producer).hexdigest(),input_and_source_hashes=dict(sorted(pins.items())),
        archive=dict(name=path.name,sha256=sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size),arithmetic_precision_bits=256,
        actual_full_rank=rank,actual_old28_rank=len(oldactive),actual_new8_rank_while_preserving_old28=len(newactive),
        free_new_momentum_directions_preserving_all_temporal_rows=len(free),new_directions_after_preserving_old28=59-len(oldactive),
        pivot_determinant_absolute_lower=float(abs(det).lower()),exact_zero_temporal_rows=zero_rows.tolist(),
        fresh_vs_cached_velocity_generator_upper=fresh_vs_cached,native_point_Dphi_image_upper=image_defect,
        native_raw_geometry_velocity_image_upper=raw_geo_defect,native_Higgs_gauge_velocity_image_upper=Higgs_defect,
        native_vs_literal_action_commutator_factor_difference_upper=float(factor_difference.upper()),
        native_old158_vs_original_canonical_momentum_upper=_upper(PioldNative-PioldCanonical),
        native_primal_charge_vs_action_Gauss_upper=_upper(native_primal_check),
        fixed_original_oldPi_primal_range=obstruction_status(obstructionCanonical),actual_seven_affine_load_range=obstruction_status(obstructionTrial),
        missing_new_central_old_momentum_support=missing_support,missing_new_central_source_seven_nonzero_columns=[j for j in range(7)if float(abs(missing_source[0,j]).lower())>0],
        missing_new_central_literal_formula='Pi[d_rho(phiP1)]+20/(3*WALL)*Pi[phiP0]+70/(3*WALL)*Pi[phiP2]',
        missing_new_central_owned_minus_literal_row_upper=_upper(missing_row_difference),
        missing_new_central_retained_zero_containing_entries=uncertain_old,
        combined_four_old_momentum_cokernel_image_rank=4,combined_four_rank_minor_abs_lower=source_minor_lower,
        fixed_oldPi_load_augmented_source_four_rank=5,fixed_oldPi_augmented_minor_abs_lower=augmented_minor_lower,
        isolated_fixed_q_four_momentum_component_span_cannot_cancel_all_eight_exact_loads=True,
        affine_source_column0_is_not_promoted_to_a_free_physical_parameter=True,
        missing_new_central_source_combined_four_nonzero_columns=[j for j in range(4)if float(abs(four(missing_source)[0,j]).lower())>0],
        missing_new_central_source_seven_upper=_upper(missing_source),missing_new_central_source_combined_four_upper=_upper(four(missing_source)),
        canonical_source_fields_match_current_seven_upper=sourceR_defect,
        rank_certified_by_exact_support_and_nonzero_minor_not_SVD=True,no_pseudoinverse_minimum_norm_or_free_coordinate_values_chosen=True,
        range_obstruction_only_under_fixed_old_canonical_momentum_hypothesis=True,
        existing_old_source_momentum_components_can_carry_missing_central_row=True,
        source_span_component_diagnostic_not_full_coupled_source_domain_solution=True,
        actual_old28_residuals_not_discarded=True,full_BHSM_solution_nonexistence_claim=False,
        full_outgoing_domain_or_31_free_momenta_selected=False,physical_full_derivative_or_radial_convergence_or_Maxwell226=False,
        normalized_physical_two_spin_state=False,physical_muon_magnetic_moment=None,original_coupled_corrections=0)
    (out/'result.json').write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({k:report[k]for k in('actual_full_rank','actual_old28_rank','actual_new8_rank_while_preserving_old28','free_new_momentum_directions_preserving_all_temporal_rows','fixed_original_oldPi_primal_range','actual_seven_affine_load_range','missing_new_central_source_combined_four_nonzero_columns')}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',type=Path,default=ROOT)
    for key in('position-folder','central-folder','coefficient-folder','gauss-folder','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();run(a.repository,a.position_folder,a.central_folder,a.coefficient_folder,a.gauss_folder,a.output)
