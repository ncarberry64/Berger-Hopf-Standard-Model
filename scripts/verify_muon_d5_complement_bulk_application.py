"""Check sewn eta traces of the returned finite bulk coefficient family.

This verifies the two collars of EACH incoming history instance. It does
not identify them with the two time histories or impose physical outer data.
"""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT)]


def pin(p):return sha256(p.read_bytes()).hexdigest()


def load_manifest(folder,record):
    arrays={}
    for name,md in record['archives'].items():
        p=folder/name
        if pin(p)!=md['sha256']:raise ValueError('saved application changed: '+str(p))
        with np.load(p,allow_pickle=False) as z:arrays.update({k:z[k] for k in z.files})
    return arrays


def verify(folder,output):
    folder=Path(folder);output=Path(output)
    if output.exists():raise FileExistsError('preserve earlier checks')
    core=json.loads((folder/'core_result.json').read_bytes())
    result=json.loads((folder/'result.json').read_bytes())
    if pin(folder/'core_result.json')!=result['core_record_sha256']:
        raise ValueError('core/result identity mismatch')
    a=load_manifest(folder,core);returned=load_manifest(folder,result)
    U=a['wall_geometric_right'];Ux=a['wall_geometric_right_source']
    Ui=np.linalg.inv(U);Uix=-Ui@Ux@Ui
    B=a['wall_selected_Bhat'];Bx=a['wall_selected_Bhat_source']
    maximum=lambda x:float(np.max(abs(x)))
    common=lambda V,Vx:(Ui@V,Uix@V+Ui@Vx)
    checks={}
    for label in ('plus_seed','minus_seed','minus_LR','minus_RL'):
        V=a[label+'_chi_value'][0];Vx=a[label+'_chi_source'][0]
        if label.startswith('minus'):V,Vx=common(V,Vx)
        checks[label]=dict(selected_collar_equation_max=maximum(B@V),
            differentiated_selected_collar_equation_max=maximum(Bx@V+B@Vx))
    Q,Qx=a['wall_plus_complement_basis'],a['wall_plus_complement_basis_source']
    Z,Zx=a['wall_minus_complement_basis'],a['wall_minus_complement_basis_source']
    z,zx=common(Z,Zx)
    homogeneous=dict(coordinates_per_time_node=366,time_nodes=6,
        plus_selected_max=maximum(B@Q),minus_selected_max=maximum(B@z),
        plus_selected_source_max=maximum(Bx@Q+B@Qx),
        minus_selected_source_max=maximum(Bx@z+B@zx),
        jump_max=maximum(z-Q),jump_source_max=maximum(zx-Qx),
        data_or_data_source_assigned=False)
    prior=ROOT/'artifacts/muon_formed_event_domain_application_20261019/run_2/formed_event_domain_application.npz'
    with np.load(prior,allow_pickle=False) as old:
        for channel in ('LR','RL'):
            label='minus_'+channel
            v,vx=common(a[label+'_chi_value'][0],a[label+'_chi_source'][0])
            target=np.zeros_like(v[-1]);source_target=np.zeros_like(vx[-1])
            target[:,-18:]=old['incoming_'+channel+'_image']
            source_target[:,-18:]=old['incoming_'+channel+'_image_coordinate_time']
            checks[label]['E1_original_jump_max']=maximum(v[-1]-target)
            checks[label]['E1_original_jump_source_max']=maximum(vx[-1]-source_target)
    bulk=result['event_consumption']['original_bulk_checks']
    finite_residuals={name:max(row[name] for row in bulk.values()) for name in (
        'original_full_D5_collocation_max','original_full_D5_offnode_max',
        'original_full_D5_source_collocation_max','original_full_D5_source_offnode_max',
        'original_complement_plus_extension_collocation_max',
        'original_complement_plus_extension_source_collocation_max')}
    event=result['event_consumption']['actual_event_operand_applications']
    # All rows below are independent of the unassigned physical normal factors.
    bound=max([x for row in checks.values() for x in row.values()]
              +[v for k,v in homogeneous.items() if k.endswith('_max')])
    if bound>2e-10:raise ArithmeticError('finite sewn collar equations failed')
    record=dict(schema='bhsm.d5-bulk-collar-original-check.v1',
        application_input_sha256={name:pin(folder/name)
            for name in ('core_result.json','result.json')},
        owner_input_sha256={p.relative_to(ROOT).as_posix():pin(p)
            for p in (prior,Path(__file__))},
        both_original_collar_equations=checks,
        complete_homogeneous_trace_family=homogeneous,
        reconstructed_original_finite_D5=finite_residuals,
        nonnull_bulk_event_operands=event,
        normal_profile_normalization_equations={
            'right':'integral_actual_full_normal_domain J |u_R|^2 ds=1',
            'independent_left':'corresponding independent left normalization and analytic pairing',
            'right_integral':None,'left_integral':None,
            'partial_material_strip_norm_substituted':False},
        held_outer_event_conditions={
            'regular_center':'original H1 closure of smooth Cartesian spinors; no new origin trace',
            'future_outer':'original retarded regular/outgoing support; no finite strip annihilator supplied',
            'event':'Gamma0_child-U_R Gamma0_parent=0 with actual corner incidence',
            'outer_residual':None,'event_residual':None,
            'originating_square_conormal_residual':None,
            'finite_Green_currents_are_not_native_temporal_conormals':True},
        physical_guard=2e-10,finite_collar_arithmetic_checked=True,
        physical_full_D5_normalization_outer_event_admitted=False)
    output.write_text(json.dumps(record,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps(dict(checkpoint=str(output),finite_collar_max=bound,
        reconstructed_original_finite_D5=finite_residuals)))
    return record


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--application-dir',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();verify(args.application_dir,args.output)
