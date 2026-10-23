"""Read-only exact saved-state/response provenance, no action re-evaluation."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import mpmath as mp
import numpy as np


ROOT=Path(__file__).resolve().parents[1]
FAMILY='artifacts/muon_baton_zoo_maximal_current_realization_20261013'
PACKET='actual_new_only_compatible316_response_and_full252_source_return.npz'
TARGET='actual_linear_cut_compatible368_MP_full_operator_blocked_run_2/actual_precise_direct_CHILD620_and_full368_canonical_source_operands.npz'
SEED='actual_linear_cut_enlarged_Gauss_Legendre_prolongation_run_2/actual_original_Gauss_and_old_Legendre_complete_current_Cauchy_prolongation.npz'
EXPECTED='ea02ed6aee45310c5651fef5c8f103e868007d4f125582ab2b64ff7651f76b2b'


def run(root,output):
    root,out=Path(root).resolve(),Path(output)
    if out.exists():raise FileExistsError('Preserve every provenance receipt')
    pins={}
    def read(path):
        p=Path(path);p=p if p.is_absolute()else root/p;b=p.read_bytes();pins[p.relative_to(root).as_posix()]=sha256(b).hexdigest()
        if p.suffix=='.json':return json.loads(b)
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    def eq(a,b,label):
        if not np.array_equal(a,b):raise ValueError(label+': exact operand identity failed')
        return True
    def clock(a):
        z=complex(a.item());return[z.real,z.imag]
    def absolute(a):return float(np.max(abs(a)))
    def exact(z,key):
        a,b=z[key+'_high'],z[key+'_low']
        return np.array([mp.mpc(complex(x))+mp.mpc(complex(y))for x,y in zip(a.flat,b.flat)],object).reshape(a.shape)
    def mpmax(a):return mp.nstr(max(abs(v)for v in a.flat),45)
    family=root/FAMILY;target=read(family/TARGET)
    if pins[(family/TARGET).relative_to(root).as_posix()]!=EXPECTED:raise ValueError('Different original ea02 target')
    flow=family/'actual_response_cut_compatible368_refinement_flow_run_1'
    initial=read(flow/'actual_precise_compatible_cut_constitutive_rows.npz')
    seed=read(family/SEED)
    initial_equal={k:eq(target[k],initial[k],k)for k in('master368','Pi158_high','Pi158_low','coordinate_time')}
    eq(seed['authoritative_node_time'],target['coordinate_time'],'initial response target clock')
    eq(seed['completed_frames'],target['completed_frames'],'initial response target frame')
    previous,previous_response=initial,seed
    previous_response_path=family/SEED;records=[]
    with mp.workdps(80):
        for i in range(8):
            middle_path=flow/f'cell_{i:04d}_retry_00_precise_original526_midpoint.npz'
            end_path=flow/f'cell_{i:04d}_retry_00_precise_original210_endpoint.npz'
            middle,end=read(middle_path),read(end_path)
            response_folder=family/(f'actual_new_only_compatible316_matrixfree_retarded_cell{i}'+('_warm_run_2'if i==7 else'_run_1'))
            response_path=response_folder/PACKET;response=read(response_path);meta=read(response_folder/'result.json')
            if not meta['admitted_finite_cell']or meta['original526_rows_upper']>2e-10:raise ValueError('Unadmitted saved response cell')
            eq(response['actual_midpoint_master368'],middle['midpoint_master368'],'complete368 midpoint')
            eq(response['coordinate_time'],middle['coordinate_time'],'response midpoint clock')
            eq(response['step'],middle['step'],'response step')
            eq(response['completed_frames'],target['completed_frames'],'full frame')
            eq(response['original252_to_augmented368'],target['original252_to_augmented368'],'field incidence')
            for part in('high','low'):eq(middle['final_Pi158_'+part],end['Pi158_'+part],'full endpoint momentum '+part)
            if Path(response['actual_midpoint_packet'].item()).resolve()!=middle_path.resolve():raise ValueError('Midpoint pointer mismatch')
            consumed={}
            for path,h in meta['inputs'].items():
                p=Path(path);p=p.resolve()if p.is_absolute()else(root/p).resolve();consumed[p]=h
            for p in(middle_path,previous_response_path,family/TARGET):
                h=sha256(p.read_bytes()).hexdigest()
                if consumed.get(p.resolve())!=h:raise ValueError('Required actual previous-response/midpoint/ea02 byte link absent: '+str(p))
            clocks=[p for p in consumed if p.name=='actual_continuous_phase210_clock_and_same_owner_point_density_rate.npz']
            if len(clocks)!=1:raise ValueError('Unique actual same-midpoint source-clock packet required')
            clock_path=clocks[0];source_clock=read(clock_path)
            if consumed[clock_path]!=sha256(clock_path.read_bytes()).hexdigest():raise ValueError('Source clock bytes changed')
            eq(source_clock['master368'],middle['midpoint_master368'],'source clock complete368 field')
            eq(source_clock['coordinate_time'],middle['coordinate_time'],'source clock exact midpoint tag')
            eq(source_clock['literal_completed_frames'],target['completed_frames'],'source clock frame')
            for pname in('executed_producer.py','initial_producer.py'):
                p=response_folder/pname;pins[p.relative_to(root).as_posix()]=sha256(p.read_bytes()).hexdigest()
            producer=response_folder/'executed_producer.py'
            if sha256(producer.read_bytes()).hexdigest()!=meta['producer_sha256']:raise ValueError('Saved executed response producer differs')
            if sha256(response_path.read_bytes()).hexdigest()!=meta['packet_sha256']:raise ValueError('Saved response packet differs')
            Q=exact(response,'retarded_and_homogeneous_separate316');C=exact(response,'combined_four_Cauchy316')
            combined=np.empty((316,4),object);combined[:,0]=Q[:,0]
            for j in range(3):combined[:,1+j]=Q[:,1+j]+Q[:,4+j]
            carry=exact(response,'existing_full252_source_return')-exact(previous_response,'existing_full252_source_return')-exact(response,'full252_inherited_source_return_increment')
            position_defect=absolute(middle['midpoint_master368'][:158]-(previous['master368'][:158]+end['master368'][:158])/2)
            if position_defect>2e-10:raise ValueError('Saved primal chronological midpoint identity fails')
            tag_delta=response['authoritative_node_time'].item()-end['coordinate_time'].item()
            records.append(dict(cell=i,midpoint=middle_path.relative_to(root).as_posix(),endpoint=end_path.relative_to(root).as_posix(),response=response_path.relative_to(root).as_posix(),
                previous_response=previous_response_path.relative_to(root).as_posix(),source_clock=clock_path.relative_to(root).as_posix(),
                midpoint_time=clock(middle['coordinate_time']),endpoint_time=clock(end['coordinate_time']),step=float(middle['step']),
                position_midpoint_identity_absolute=position_defect,endpoint_tag_addition_order_delta=[tag_delta.real,tag_delta.imag],
                exact_complete368_midpoint_and_clock_and_frame=True,previous_response_consumed_byte_sha_verified=True,
                full_Pi158_endpoint_high_low_bit_identity=True,combined_four_from_separate_seven_MP80_representation_residual=mpmax(C-combined),
                full252_cumulative_source_return_MP80_representation_residual=mpmax(carry),
                admitted_saved_response_original526_upper=meta['original526_rows_upper'],
                full_density_time_derivative_admitted=meta.get('complete_density_time_derivative_admitted',None)))
            previous,previous_response,previous_response_path=end,response,response_path
    final=read(flow/'last_actual_compatible_primal_with_unclosed_future.npz')
    for k in('master368','Pi158_high','Pi158_low','coordinate_time'):eq(final[k],previous[k],'final '+k)
    principal=read(family/'actual_compatible368_MP_gradient_run_1/actual_precise_compatible_cut_constitutive_rows.npz')
    first=read(flow/'cell_0000_retry_00_precise_original210_endpoint.npz')
    eq(principal['coordinate_time'],first['coordinate_time'],'explicit equal-time branch comparison')
    branch=dict(same_coordinate_time=clock(first['coordinate_time']),same_full368_field=np.array_equal(principal['master368'],first['master368']),
        max_full368_field_difference=absolute(principal['master368']-first['master368']),max_position158_difference=absolute(principal['master368'][:158]-first['master368'][:158]),
        max_Pi158_high_low_sum_difference=absolute((principal['Pi158_high']+principal['Pi158_low'])-(first['Pi158_high']+first['Pi158_low'])),
        splicing_authorized_by_equal_clock=False)
    result=dict(classification='INDEPENDENT_ORIGINAL_EA02_SAVED_PRIMAL_RESPONSE_EPOCH_PROVENANCE',
        original_target_sha256=EXPECTED,original_target_time=clock(target['coordinate_time']),initial_original_target_bit_identities=initial_equal,
        records=records,final_original_response_primal_time=clock(final['coordinate_time']),final_master368_and_Pi158_high_low_bit_identical=True,
        equal_time_principal_branch_exclusion=branch,input_sha256=dict(sorted(pins.items())),
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),saved_accepted_chronology_only=True,action_or_history_recomputed=False,
        physical_time_tag_repair_performed=False,physical_derivative_or_Maxwell226_pass=False,coupled_corrections=0,physical_muon_moment=None)
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(records=len(records),result_sha256=sha256(out.read_bytes()).hexdigest(),principal_branch=branch)))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repository',default=str(ROOT));p.add_argument('--output',required=True);a=p.parse_args();run(a.repository,a.output)
