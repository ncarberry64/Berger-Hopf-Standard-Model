"""Verify exact saved application reuse and explicitly unresolved physical data."""
from pathlib import Path
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from scripts.evaluate_muon_causal_data_prerequisites import pin,verified_inputs


def verify(first,second):
    first,second=Path(first),Path(second);verified_inputs()
    names=sorted(p.name for p in first.iterdir() if p.is_file())
    if names!=sorted(p.name for p in second.iterdir() if p.is_file()):raise ValueError('different output sets')
    for name in names:
        if (first/name).read_bytes()!=(second/name).read_bytes():raise ValueError('nonidentical materializations')
    r=json.loads((first/'result.json').read_bytes())
    for rel,h in r['input_sha256'].items():
        if pin(ROOT/rel)!=h:raise ValueError('input changed '+rel)
    if pin(first/'application.npz')!=r['arrays']['sha256']:raise ValueError('arrays changed')
    with np.load(first/'application.npz',allow_pickle=False) as z:
        if sorted(z.files)!=r['arrays']['keys']:raise ValueError('array set changed')
        if any(z[k].dtype.hasobject or not np.isfinite(z[k]).all() for k in z.files):raise ValueError('invalid array')
        if not np.max(abs(z['charge_exchange']))>1:raise ValueError('nonzero exchange removed')
        if not np.max(abs(z['electron_pair_charge_exchange']))>.5:raise ValueError('current consumption removed')
        for k in ('original_charge_balance_rows','original_charge_balance_source_rows'):
            if np.max(abs(z[k]))>2e-10:raise ValueError('original coefficient identity failed')
        if not np.array_equal(z['prepared_physical_required_K0_K1_fm'],[0,2000]):
            raise ValueError('preparation target changed')
        C=z['original_integrability_matrix'];Cx=z['original_integrability_matrix_source']
        lam=z['pointwise_gauge_compensator'];lamx=z['pointwise_gauge_compensator_source']
        if C.shape!=(52,4) or np.linalg.matrix_rank(C,tol=1e-12)!=4:
            raise ValueError('pointwise curvature/Higgs rank proof lost')
        if np.max(abs(C@lam))>2e-10 or np.max(abs(Cx@lam+np.einsum('ai,ki->ka',C,lamx)))>2e-10:
            raise ValueError('original integrability/source rows failed')
    if r['comparison']['pointwise_time_gauge_rank']!=4:raise ValueError('pointwise proof changed')
    if (r['retained_parent_h'],r['free_incoming_data'],r['remaining_h_after_coordinate_pivot'])!=(3660,40,3620):
        raise ValueError('free physical data lost')
    for k in ('physical_d_in','physical_initial_Cauchy_data','physical_packet_sections',
        'collider_to_parent_incidence','physical_pair_conversion','physical_occupation',
        'physical_state_combination_child_check','physical_Gauss_residual','physical_Cauchy_norm_residual',
        'full_formation_residual'):
        if r[k] is not None:raise ValueError('unevaluated physical quantity promoted '+k)
    if r['physical_inputs_newly_instantiated'] or r['physical_h_selected_rank']!=0:
        raise ValueError('prerequisite promoted to a physical state')
    if r['physical_guard']!=2e-10 or r['physical_admission'] or r['complete_physical_derivative']:
        raise ValueError('physical guard/scope changed')
    d=r['radial17_consumed_example'];rows=d['original6time_nodal_partitions']
    if rows['held_incoming_evolution']['max_abs']<1e8 or rows['held_birth_original_D5']['max_abs']<1e8:
        raise ValueError('held compatibility failures removed')
    probe=d['independent9'][0]
    if probe['terms']['original_D5']['max_abs']<1e7 or probe['terms']['original_D5_source']['max_abs']<1e9:
        raise ValueError('independent original nonpasses removed')
    if d['physical_norm'] is not None or d['physical_state_amplitudes'] is not None:
        raise ValueError('coordinate diagnostics promoted to physical norms')
    if r['radial17_extra_birth_ports_per_target_branch']!=112 or r['orientation_families']!=[2,3]:
        raise ValueError('unresolved representation ports/families lost')
    return dict(schema='bhsm.causal-data-prerequisite-verification.v1',byte_identical=True,
        arrays_sha256=r['arrays']['sha256'],result_sha256=pin(first/'result.json'),
        original_operator_checks=True,physical_data_instantiated=False,physical_admission=False)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('first',type=Path);p.add_argument('second',type=Path);a=p.parse_args()
    print(json.dumps(verify(a.first,a.second),sort_keys=True,indent=2))
