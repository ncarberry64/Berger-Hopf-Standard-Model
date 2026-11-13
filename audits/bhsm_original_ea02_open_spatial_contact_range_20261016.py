"""Open rank27 spatial contact family with its FULL frozen wall trace.

Only exact saved coefficient maps are used. Numerical coordinate origins do
not select physical q values. The32 free coordinates, all boundary/flux/domain
constraints and response momentum/phase complements remain unknowns to solve.
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
PHASE='audits/bhsm_original_ea02_d4_phase_operator_20261016.py'
PHASE_SHA='c2f11bd4890631c03afee8b0db1fe8a93e505a12071da9cd2b9923744e8a5c6d'
MAP_SHA='ee70fbcc2938236e70ef5f8be03d44e3d94e8a2f153972f532c57f9a68cebfb0'
MAP_ARCHIVE_SHA='d9c443287206aef8a3596b72d4778a27c3d49ffdaa1f6e882da3e18e2960512b'
DECOMP_SHA='979045f0e0869905d7e66c926e0cb28ba4d38c0df6d3c6873eaca7d9581839ac'
DECOMP_ARCHIVE_SHA='7c8f3b515139473a664c94a394a3cf1afd09078a0be57795793ec296f390fe87'


def execute(map_folder,decomposition_folder,output):
    out=Path(output).resolve();out.mkdir(parents=True,exist_ok=False)
    source=Path(__file__).read_bytes();(out/'executed_producer.py').write_bytes(source)
    p=ROOT/PHASE
    if sha256(p.read_bytes()).hexdigest()!=PHASE_SHA:raise ValueError('Frozen action metadata backend changed')
    spec=importlib.util.spec_from_file_location('ea02_metadata_for_open_q_range',p)
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    op=module.ActualEa02D4PhaseOperator();op.pin(p,PHASE_SHA)
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    def packet(folder,source_sha,archive_sha):
        folder=Path(folder).resolve();meta=op.read(folder/'result.json');op.pin(folder/'executed_producer.py',source_sha)
        if meta['source_sha256']!=source_sha or meta['archive']['sha256']!=archive_sha:raise ValueError('Frozen reviewed map producer changed')
        z=op.read(folder/meta['archive']['name'],archive_sha)
        if not np.array_equal(z['master368'],op.target['master368'])or z['coordinate_time'].item()!=op.target['coordinate_time'].item():raise ValueError('No source/field/cut splice')
        return z
    z=packet(map_folder,MAP_SHA,MAP_ARCHIVE_SHA);d=packet(decomposition_folder,DECOMP_SHA,DECOMP_ARCHIVE_SHA)
    M=op.value(z,'actual_open36_by_new59_physical_deltaV_Euler_map')
    W=op.value(z,'actual_new59_wall_gauge_value_map')
    temporal=np.asarray(z['certified_minor_temporal_rows'],int);pivots=np.asarray(z['certified_minor_new59_columns'],int)
    free=np.setdiff1d(np.arange(59),pivots);central=np.asarray(z['central9_temporal_rows'],int);newq=np.asarray(z['new59_position_indices'],int)
    if len(temporal)!=27 or len(pivots)!=27 or len(free)!=32 or op.upper(op.rows(M,central))!=0:raise ValueError('Certified27 SU2 rows and central9zero required')
    A=op.acb_mat([[M[int(i),int(j)]for j in pivots]for i in temporal])
    determinant=A.det()
    if float(abs(determinant).lower())<=0:raise ValueError('Original-map nonzero minor certificate required')
    Ainv=A.solve(op.matrix(np.eye(27)))
    P=op.acb_mat(59,36);N=op.acb_mat(59,32)
    for i,j in enumerate(pivots):
        for k,row in enumerate(temporal):P[int(j),int(row)]=Ainv[i,k]
    freeblock=op.acb_mat([[M[int(i),int(j)]for j in free]for i in temporal]);pivotfree=-A.solve(freeblock)
    for k,j in enumerate(free):
        N[int(j),k]=1
        for i,pivot in enumerate(pivots):N[int(pivot),k]=pivotfree[i,k]
    range_projector=op.acb_mat(36,36)
    for i in temporal:range_projector[int(i),int(i)]=1
    identities=dict(right_inverse_range_rows=M*P-range_projector,open32_kernel_rows=M*N)
    if any(not v[i,j].contains(0)for v in identities.values()for i in range(v.nrows())for j in range(v.ncols())):raise ArithmeticError('Exact open-range algebra is not enclosed')
    current=op.value(d,'actual_unprojected_physical_deltaV_Euler')
    particular=-P*current;remaining=current+M*particular
    WP,WN,Wpart=W*P,W*N,W*particular
    # Keep the actual frozen coefficients, including nonzero midpoint crumbs.
    support=[]
    for j,q in enumerate(newq):
        nonzero=[i for i in range(20)if float(abs(W[i,j]).lower())>0]
        support.append(dict(local_column=j,child_q_index=int(q),
            proven_nonzero_rows=nonzero,all_entries_enclose_zero=all(W[i,j].contains(0)for i in range(20)),
            maximum_absolute_lower=max((float(abs(W[i,j]).lower())for i in range(20)),default=0),
            maximum_absolute_upper=max((float(abs(W[i,j]).upper())for i in range(20)),default=0)))
    small=[s for s in support if 154<=s['child_q_index']<=185 or 202<=s['child_q_index']<=216]
    # E_qnew acts on unknown RESPONSE coordinates, not on the primal.
    E=op.acb_mat(746,59)
    for j,q in enumerate(newq):E[252+int(q),j]=1
    values=dict(actual_physical_contact_map=M,full_frozen_wall_trace_map=W,
        certified_original_minor=A,certified_original_minor_determinant=op.acb_mat([[determinant]]),
        open_spatial_contact_right_inverse_P=P,open_spatial_contact_kernel_N=N,
        SU2_contact_range_projector=range_projector,
        known_current_seven_physical_deltaV_Euler=current,
        known_seven_particular_response_q_coordinate_coefficients=particular,
        remaining_central_and_interval_contact_rows=remaining,
        full_wall_trace_times_P=WP,full_wall_trace_times_N=WN,
        full_wall_trace_known_particular_coefficients=Wpart,
        response_full746_new59_q_incidence=E,
        known_particular_full746_response_direction=E*particular,
        open32_full746_response_q_incidence=E*N,**identities)
    arrays=dict(master368=op.target['master368'],coordinate_time=op.target['coordinate_time'],new59_position_indices=newq,
        pivot_new59_coordinate_labels=pivots,open32_free_new59_coordinate_labels=free,
        certified_SU2_temporal_rows=temporal,central9_temporal_rows=central)
    for key,v in values.items():arrays[key+'_high'],arrays[key+'_low']=op.split(v);arrays.update(op.exact.export_acb_exact_dyadic(v,key+'_exact'))
    path=out/'actual_open_spatial_contact_family_and_full_wall_trace.npz';_compressed_npz(path,arrays)
    for name,mod in list(sys.modules.items()):
        p=getattr(mod,'__file__',None)
        if p and(name=='bhsm'or name.startswith('bhsm.'))and Path(p).resolve().is_relative_to(ROOT):op.pin(Path(p).resolve())
    op.pin(Path(__file__))
    report=dict(classification='ACTUAL_OPEN_RANK27_SPATIAL_CONTACT_FAMILY_WITH_FULL_FROZEN_TRACE',source_sha256=sha256(source).hexdigest(),
        input_and_source_sha256=dict(sorted(op.pins.items())),archive=dict(name=path.name,bytes=path.stat().st_size,sha256=sha256(path.read_bytes()).hexdigest()),
        family='deltaq_new=-P*current_deltaV_Euler+N*a32; no physical a32 values selected',
        wall_relation='deltaA_wall=W*(-P*current_deltaV_Euler)+W*N*a32; no boundary value prescribed',
        coupled_phase_relation='Hv*(Rbase+Eq*deltaq+Ephase*eta)-Pi_response=0; HG*(Rbase+Eq*deltaq+Ephase*eta)+rG*b=0',
        proper_source_and_outgoing_trace_normal_flux_constraints='retained separate coupled equations; Pi_response complement not fixed by old numerical section',
        exact_contact_rank=27,open_response_q_coordinates=32,
        right_inverse_range_residual_upper=op.upper(identities['right_inverse_range_rows']),
        kernel_residual_upper=op.upper(identities['open32_kernel_rows']),
        q_particular_coordinate_upper=op.upper(particular),remaining_contact_upper=op.upper(remaining),
        full_wall_times_P_upper=op.upper(WP),full_wall_times_N_upper=op.upper(WN),
        full_wall_known_particular_upper=op.upper(Wpart),
        all_frozen_wall_coefficients_retained_without_thresholding=True,
        frozen_wall_support_bounds=support,
        small47_column_count=len(small),small47_proven_nonzero_column_count=sum(bool(s['proven_nonzero_rows'])for s in small),
        small47_universal_zero_enclosure_claim=False,ideal_profile_zero_identified_with_frozen_map=False,
        original_primal_or_physical_source_changed=False,physical_q_or_free32_values_selected=False,
        coordinate_origin_not_a_physical_zero_assignment=True,minnorm_or_empirical_fitting_used=False,
        full_old158_momenta_selected_as_physical_boundary_data=False,
        wall_normal_flux_or_full_proper_ports_assumed_preserved=False,
        phase_constitutive_or_clock_closure_evaluated_for_this_new_family=False,
        exact_full36_clock_null_certificate_or_required_chi_zero_claimed=False,
        action_Hxx_history_or_coefficient_sampling_calls=0,original_coupled_corrections=0,
        physical_outgoing_full_derivative_Maxwell226_spin_moment=False)
    (out/'result.json').write_text(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({k:report[k]for k in('right_inverse_range_residual_upper','kernel_residual_upper','q_particular_coordinate_upper','remaining_contact_upper','full_wall_known_particular_upper','small47_proven_nonzero_column_count')}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for key in('map-folder','decomposition-folder','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args()
    try:execute(a.map_folder,a.decomposition_folder,a.output)
    except Exception as error:
        import traceback
        if a.output.exists():(a.output/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc(),source_sha256=sha256(Path(__file__).read_bytes()).hexdigest()),sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
        raise
