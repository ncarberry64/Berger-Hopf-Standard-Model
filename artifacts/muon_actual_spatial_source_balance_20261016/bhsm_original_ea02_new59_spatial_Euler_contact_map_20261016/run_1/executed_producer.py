"""Open36 by59 physical spatial-q to deltaV.E map at the original ea02.

Only frozen coefficient/Euler germs and exact source-owned weak-functional
blocks are consumed. No action, Hxx, source/history sampling or q-value solve
occurs. Proper normal/flux/domain constraints stay separate and unselected.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
import textwrap
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
POSITION='audits/bhsm_original_ea02_d4_position_operator_20261016.py'
POSITION_SHA='70670f411a2a11d301677359500be28fb9769f1557000b3262eb5939816ae389'
OWNER='audits/bhsm_original_ea02_physical_deltaV_Euler_clock_20261016.py'
OWNER_SHA='979045f0e0869905d7e66c926e0cb28ba4d38c0df6d3c6873eaca7d9581839ac'
DECOMP_ARCHIVE_SHA='7c8f3b515139473a664c94a394a3cf1afd09078a0be57795793ec296f390fe87'
CLOCK_SHA='8d4a7fe4fe24501c6d2e00681ed9ca4f1e2b5eb9d0793b3e775bab4c92b58574'
CLOCK_ARCHIVE_SHA='2e0b2140004e37699f80ed25d14c8d988f657598f6b7d4b1269bce292cf7039d'
COEFF_SHA='c744590f986e47c946f128641b071808f527d230ba60fc2fa70adf87d351c851'
COEFF_ARCHIVE_SHA='6cf8979c6d81fb427a23a93848f13a87400a615daae0e1496698d042f85755a2'
RADIAL='artifacts/muon_baton_zoo_radial_convergence_20261014'


def execute(clock_folder,coefficient_folder,decomposition_folder,output):
    out=Path(output).resolve();out.mkdir(parents=True,exist_ok=False)
    source=Path(__file__).read_bytes();(out/'executed_producer.py').write_bytes(source)
    p=ROOT/POSITION
    if sha256(p.read_bytes()).hexdigest()!=POSITION_SHA:raise ValueError('Reviewed full217 metadata backend changed')
    spec=importlib.util.spec_from_file_location('position_metadata_for_q_contact_map',p)
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    position=module.ActualEa02D4PositionOperator();op=position.phase;op.pin(p,POSITION_SHA)
    from flint import acb,acb_mat
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    from bhsm.interface.muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
    from bhsm.interface.muon_parent_mean_causal_action import MAXWELL_TO_CAP
    from bhsm.interface.muon_literal_euclidean_wall_action import VOLUME
    def packet(folder,expected_source,expected_archive,name=None):
        folder=Path(folder).resolve();meta=op.read(folder/'result.json');op.pin(folder/'executed_producer.py',expected_source)
        if meta['source_sha256']!=expected_source:raise ValueError('Frozen reviewed operand producer changed')
        z=op.read(folder/(meta['archive']['name']if name is None else name),expected_archive)
        if not np.array_equal(z['master368'],op.target['master368'])or z['coordinate_time'].item()!=op.target['coordinate_time'].item():raise ValueError('No different-state/source/cut composition')
        return z
    clock=packet(clock_folder,CLOCK_SHA,CLOCK_ARCHIVE_SHA)
    a=packet(coefficient_folder,COEFF_SHA,COEFF_ARCHIVE_SHA,'actual_same_ea02_D4_seven_point_density_R_hR.npz')
    decomp=packet(decomposition_folder,OWNER_SHA,DECOMP_ARCHIVE_SHA)
    owner_bytes=op.pin(OWNER,OWNER_SHA).read_bytes();owner_source=owner_bytes.decode('utf8')
    # Reuse the exact already-reviewed source blocks, with an explicit
    # namespace. No dynamic frame inspection, patches or hidden caller state.
    def block(start,end):
        if owner_source.count(start)!=1 or owner_source.count(end)!=1:raise ValueError('Frozen owner block boundaries changed')
        return textwrap.dedent(owner_source[owner_source.index(start):owner_source.index(end)])
    functional_block=block('    def C(v):','    # Build the literal fixed-chart physical q test maps.')
    map_block=block('    n=217;original=','    selected=[')
    context=dict(op=op,position=position,clock=clock,a=a,value=op.value,rows=op.rows,upper=op.upper,
        acb=acb,acb_mat=acb_mat,np=np,RADIAL=RADIAL,
        higgs_u2_real_representation=higgs_u2_real_representation,MAXWELL_TO_CAP=MAXWELL_TO_CAP,VOLUME=VOLUME)
    exec(compile(functional_block,OWNER+':exact_weak_E_block','exec'),context)
    exec(compile(map_block,OWNER+':exact_fixed_q_maps_block','exec'),context)
    Qpoint,Qr,Qwall,rawQ=(context[k]for k in('Qpoint','Qr','Qwall','rawQ'))
    phi,phir,phiw,weak_E,comm,add,scale,O,C=(context[k]for k in('phi','phir','phiw','weak_E','comm','add','scale','O','C'))
    newq=np.asarray(position.newq,int);nr=len(Qpoint)
    if len(newq)!=59 or nr!=48:raise ValueError('Actual full59 new q labels and original48 nodes required')
    # These are direct supplied-map statements, not inferred flux/port BC.
    raw_geometry=op.rows(rawQ,np.arange(100));rawH=op.rows(rawQ,np.arange(260,264))
    geometry_new=acb_mat([[raw_geometry[i,int(j)]for j in newq]for i in range(100)])
    H_new=acb_mat([[rawH[i,int(j)]for j in newq]for i in range(4)])
    wall_new=acb_mat([[Qwall[i,int(j)]for j in newq]for i in range(20)])
    if op.upper(geometry_new)!=0 or op.upper(H_new)!=0:raise ValueError('This map is only the owned new59 pure gauge spatial complement')
    # Revalidate all59 represented physical Euler tests with this exact
    # namespace and data, independently of the new unrepresented contacts.
    Euler=op.value(clock,'actual_bare_primal217_Euler');control=acb_mat(59,1)
    for k,j in enumerate(newq):
        j=int(j)
        if any(not Qpoint[ir][c,j].is_zero()for ir in range(nr)for c in range(4))or any(not rawQ[i,j].is_zero()for i in range(264,268)):raise ValueError('Unaccounted temporal or Higgs-clock test')
        test=[[[Qpoint[ir][4*f+c,j]for c in range(4)]for f in range(1,5)]for ir in range(nr)]
        testr=[[[Qr[ir][4*f+c,j]for c in range(4)]for f in range(1,5)]for ir in range(nr)]
        wt=[[Qwall[4*f+c,j]for c in range(4)]for f in range(1,5)]
        control[k,0]=weak_E(test,testr,wt,[C(0)]*4)[0]-Euler[j,0]
    if op.upper(control)>2e-10:raise ArithmeticError('New59 physical Eulerfunctional reproduction failed')
    M=acb_mat(36,59);parts=[acb_mat(36,59)for _ in range(4)]
    for param in range(9):
        print(json.dumps(dict(stage='actual_open_new59_spatial_contact_map',profile=param,SU2_channels=3,columns=59)),flush=True)
        for channel in range(3):
            row=4*param+channel
            for k,j in enumerate(newq):
                j=int(j);test=[];testr=[]
                for ir in range(nr):
                    par=[C(int(c==channel))*phi[ir,param]for c in range(4)]
                    parr=[C(int(c==channel))*phir[ir,param]for c in range(4)]
                    aa=[[Qpoint[ir][4*f+c,j]for c in range(4)]for f in range(1,5)]
                    ar=[[Qr[ir][4*f+c,j]for c in range(4)]for f in range(1,5)]
                    test.append([comm(x,par)for x in aa])
                    testr.append([add(comm(x,par),comm(y,parr))for x,y in zip(ar,aa)])
                parw=[C(int(c==channel))*phiw[0,param]for c in range(4)]
                wt=[comm([Qwall[4*f+c,j]for c in range(4)],parw)for f in range(1,5)]
                result=weak_E(test,testr,wt,[C(0)]*4);M[row,k]=result[0]
                for l in range(4):parts[l][row,k]=result[l+1]
    # The nine central rows vanish by the exact Lie commutator and H_new=0,
    # not by deleting small entries. Explicitly check the generator identity.
    central_generator_check=comm([C(1),C(2),C(3),C(4)],[C(0),C(0),C(0),C(1)])
    if any(not x.is_zero()for x in central_generator_check):raise ValueError('Owned central Lie algebra convention changed')
    central_rows=np.arange(9)*4+3;active_rows=np.array([4*p+c for p in range(9)for c in range(3)])
    central=op.rows(M,central_rows)
    # Independent order of contraction: combine the literal physical field
    # tests first, then apply commutator/weak_E, versus the completed matrix.
    directions=acb_mat(59,2)
    for k in range(59):directions[k,0]=C(1)/(k+1);directions[k,1]=C(1j if k%2 else -1j)/(k+2)
    Qnd=[acb_mat([[Qpoint[ir][r,int(j)]for j in newq]for r in range(20)])*directions for ir in range(nr)]
    Qrd=[acb_mat([[Qr[ir][r,int(j)]for j in newq]for r in range(20)])*directions for ir in range(nr)]
    Qwd=wall_new*directions;direct=acb_mat(36,2)
    for param in range(9):
        for channel in range(3):
            for col in range(2):
                test=[];testr=[]
                for ir in range(nr):
                    par=[C(int(c==channel))*phi[ir,param]for c in range(4)];parr=[C(int(c==channel))*phir[ir,param]for c in range(4)]
                    aa=[[Qnd[ir][4*f+c,col]for c in range(4)]for f in range(1,5)]
                    ar=[[Qrd[ir][4*f+c,col]for c in range(4)]for f in range(1,5)]
                    test.append([comm(x,par)for x in aa]);testr.append([add(comm(x,par),comm(y,parr))for x,y in zip(ar,aa)])
                parw=[C(int(c==channel))*phiw[0,param]for c in range(4)]
                wt=[comm([Qwd[4*f+c,col]for c in range(4)],parw)for f in range(1,5)]
                direct[4*param+channel,col]=weak_E(test,testr,wt,[C(0)]*4)[0]
    direction_controls=M*directions-direct
    if op.upper(direction_controls)>2e-10:raise ArithmeticError('New contact-map direction-before/after contraction controls failed')
    # Certified elimination yields a lower-rank minor; the independent exact
    # central-row identity supplies upper27. No SVD threshold sets the rank.
    W=op.rows(M,active_rows);row_labels=list(active_rows);col_labels=list(range(59));pivots=[]
    for stage in range(27):
        choices=[(float(abs(W[i,j]).lower()),i,j)for i in range(stage,27)for j in range(stage,59)]
        lower,i,j=max(choices)
        if lower<=0:break
        if i!=stage:
            for d in range(59):W[stage,d],W[i,d]=W[i,d],W[stage,d]
            row_labels[stage],row_labels[i]=row_labels[i],row_labels[stage]
        if j!=stage:
            for d in range(27):W[d,stage],W[d,j]=W[d,j],W[d,stage]
            col_labels[stage],col_labels[j]=col_labels[j],col_labels[stage]
        pivot=W[stage,stage];pivots.append(lower)
        for d in range(stage+1,27):
            factor=W[d,stage]/pivot
            for e in range(stage+1,59):W[d,e]-=factor*W[stage,e]
            W[d,stage]=0
    attempted_rank=len(pivots);rank_lower=attempted_rank
    while True:
        minor=acb_mat([[M[int(i),int(j)]for j in col_labels[:rank_lower]]for i in row_labels[:rank_lower]])if rank_lower else acb_mat(0,0)
        determinant=minor.det()if rank_lower else C(1)
        if float(abs(determinant).lower())>0:break
        rank_lower-=1
    arrays=dict(master368=op.target['master368'],coordinate_time=op.target['coordinate_time'],
        new59_position_indices=newq,temporal_profile_internal_labels=np.array([(p,c)for p in range(9)for c in range(4)]),
        central9_temporal_rows=central_rows,SU2_27_temporal_rows=active_rows,
        certified_minor_temporal_rows=np.array(row_labels[:rank_lower]),certified_minor_new59_columns=np.array(col_labels[:rank_lower]))
    values=dict(actual_open36_by_new59_physical_deltaV_Euler_map=M,
        bulk_Lq_contact_map=parts[0],bulk_momentum_clock_contact_map=parts[1],
        wall_scalar_Lq_contact_map=parts[2],wall_scalar_momentum_clock_contact_map=parts[3],
        new59_physical_Euler_reproduction_controls=control,exact_central9_contact_rows=central,
        actual_new59_raw_geometry_position_map=geometry_new,actual_new59_raw_Higgs_position_map=H_new,
        actual_new59_wall_gauge_value_map=wall_new,certified_original_map_minor=minor,
        certified_original_map_minor_determinant=acb_mat([[determinant]]),
        external_new59_direction_controls_only=directions,direction_before_after_contraction_rows=direction_controls,
        direct_physical_tests_before_map_contraction=direct,
        actual_current_seven_deltaV_Euler_separate=op.value(decomp,'actual_unprojected_physical_deltaV_Euler'))
    for key,v in values.items():arrays[key+'_high'],arrays[key+'_low']=op.split(v);arrays.update(op.exact.export_acb_exact_dyadic(v,key+'_exact'))
    path=out/'actual_new59_spatial_to_physical_Euler_contact_map.npz';_compressed_npz(path,arrays)
    for name,mod in list(sys.modules.items()):
        p=getattr(mod,'__file__',None)
        if p and(name=='bhsm'or name.startswith('bhsm.'))and Path(p).resolve().is_relative_to(ROOT):op.pin(Path(p).resolve())
    op.pin(Path(__file__))
    report=dict(classification='ACTUAL_OPEN_NEW59_SPATIAL_Q_TO_PHYSICAL_DELTA_V_EULER_MAP',source_sha256=sha256(source).hexdigest(),
        input_and_source_sha256=dict(sorted(op.pins.items())),archive=dict(name=path.name,bytes=path.stat().st_size,sha256=sha256(path.read_bytes()).hexdigest()),
        frozen_weak_Euler_owner_sha256=OWNER_SHA,exact_functional_block_sha256=sha256(functional_block.encode()).hexdigest(),
        exact_fixed_q_maps_block_sha256=sha256(map_block.encode()).hexdigest(),
        actual_map_rows=36,actual_new_spatial_columns=59,central9_rows_exact_zero=op.upper(central)==0,
        certified_rank_lower=rank_lower,rank_upper_from_exact_central_rows=27,
        certified_elimination_pivots_before_original_minor_check=attempted_rank,
        certified_exact_rank=rank_lower if rank_lower==27 else None,
        certified_original_minor_abs_lower=float(abs(determinant).lower()),
        actual_contact_map_upper=op.upper(M),new59_physical_Euler_reproduction_upper=op.upper(control),
        independent_direction_before_after_contraction_upper=op.upper(direction_controls),
        actual_new59_geometry_map_upper=op.upper(geometry_new),actual_new59_Higgs_map_upper=op.upper(H_new),
        actual_new59_wall_value_map_upper=op.upper(wall_new),
        exact_support_no_small_entry_cutoff_or_SVD_rank_threshold=True,
        arbitrary_new_q_values_or_cancellation_solution_selected=False,
        external_direction_controls_are_not_selected_physical_q_values=True,
        fixed_old158_momenta_promoted_to_physical_domain=False,
        full_proper_mechanical_momentum_flux_or_normal_domain_ports_proven_unchanged=False,
        proper_source_and_domain_constraints_remain_separate=True,
        action_Hxx_coefficient_or_history_sampling_calls=0,
        new_kinetic_operator_or_physical_boundary_model_invented=False,
        chi_zero_or_exact_leftnull_required=False,original_coupled_corrections=0,
        physical_outgoing_full_derivative_Maxwell226_spin_moment=False)
    (out/'result.json').write_text(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({k:report[k]for k in('actual_contact_map_upper','new59_physical_Euler_reproduction_upper','certified_rank_lower','rank_upper_from_exact_central_rows','actual_new59_wall_value_map_upper')}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for key in('clock-folder','coefficient-folder','decomposition-folder','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args()
    try:execute(a.clock_folder,a.coefficient_folder,a.decomposition_folder,a.output)
    except Exception as error:
        import traceback
        if a.output.exists():(a.output/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc(),source_sha256=sha256(Path(__file__).read_bytes()).hexdigest()),sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
        raise
