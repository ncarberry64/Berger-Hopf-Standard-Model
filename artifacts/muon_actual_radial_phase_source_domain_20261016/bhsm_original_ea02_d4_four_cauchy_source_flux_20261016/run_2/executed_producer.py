"""Exact original7-to4 D4 Cauchy/source/initial-flux composition.

The original affine/retarded/homogeneous columns retain their provenance;
no birth section, field solve, projection or outgoing graph is introduced.
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
OLD=CURRENT+'/actual_linear_cut_enlarged_Gauss_Legendre_prolongation_run_2/actual_original_Gauss_and_old_Legendre_complete_current_Cauchy_prolongation.npz'


def run(cauchy_folder,output):
    folder,out=Path(cauchy_folder).resolve(),Path(output).resolve();out.mkdir(parents=True,exist_ok=False)
    producer=Path(__file__).read_bytes();(out/'executed_producer.py').write_bytes(producer);pins={}
    def pin(p,expected=None):
        p=Path(p);p=p if p.is_absolute()else ROOT/p;h=sha256(p.read_bytes()).hexdigest()
        if expected is not None and h!=expected:raise ValueError('Frozen original Cauchy operand changed')
        pins[p.relative_to(ROOT).as_posix()if p.is_relative_to(ROOT)else str(p)]=h;return p
    def load(p,expected=None):
        p=pin(p,expected)
        if p.suffix=='.json':return json.loads(p.read_bytes())
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    sys.path.insert(0,str(ROOT/'src'))
    from flint import ctx,acb_mat
    from bhsm.interface.muon_stored_admission_correction import _matrix,_upper
    from bhsm.interface.muon_stored_fiber_canonical_tangent import _split
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    ctx.prec=288
    def imported(name,path):
        spec=importlib.util.spec_from_file_location(name,pin(path));m=importlib.util.module_from_spec(spec)
        sys.modules[name]=m;spec.loader.exec_module(m);return m
    imported('bhsm_baton_zoo_exact_acb_packets',RUNTIME+'/bhsm_baton_zoo_exact_acb_packets_imported_runtime.py')
    exact=imported('bhsm_exact_action_balls',RUNTIME+'/bhsm_exact_action_balls_imported_runtime.py')
    def val(z,k):return exact.parse_acb_exact_dyadic(z,k+'_exact')if k+'_exact_real_mid_mantissa'in z else _matrix(z[k+'_high'])+_matrix(z[k+'_low'])
    rows=lambda a,ids:acb_mat([[a[int(i),j]for j in range(a.ncols())]for i in ids])
    meta=load(folder/'result.json','f10d2140d0b5a24fe684c28d520a838ed04ca583828182b13d3043c7a25d2f94')
    data=load(folder/meta['archive']['name'],'7e11ceedc78de309d8944797982ed35aded42056f5b3fd9bccd871455591d5b3')
    pin(folder/'executed_producer.py','63d04359f42673671169f61bcfa395b04fe5008c05912b65c95090c0a4458942')
    old=load(OLD,'553494b91c4ec85e9cca5791e4a5c506a48701bd8a41d4fff24c83c3f2d2ea33')
    if old['authoritative_node_time'].item()!=data['coordinate_time'].item():raise ValueError('Original canonical epoch differs')
    C=np.zeros((7,4),int);C[0,0]=1
    for j in range(3):C[1+j,1+j]=C[4+j,1+j]=1
    mat=_matrix(C);n=217
    Q=val(data,'complete_D4_source_complete_canonical_seven')*mat
    Qdot=val(data,'complete_D4_source_complete_canonical_seven_clock')*mat
    source=rows(val(data,'exact_carried_full_D4_field_seven'),np.arange(252))*mat
    sourcedot=val(data,'actual_parent_sourceDot')*mat
    Pi,Pidot=rows(Q,np.arange(n,2*n)),rows(Qdot,np.arange(n,2*n))
    e=np.asarray(data['old368_to_complete_D4_child'],int)[:158]
    retained=val(old,'combined_four_Cauchy316');nativeold=rows(Q,np.r_[e,n+e]);olddefect=nativeold-retained
    # Old positions must match. Momentum formation is explicitly diagnosed,
    # not changed to force equality with a prior retained canonical packet.
    qdefect=_upper(rows(olddefect,np.arange(158)))
    if qdefect>2e-10:raise ValueError('Different original field/column combination')
    arrays=dict(coordinate_time=data['coordinate_time'],master368=data['master368'],
        original7_to4_incidence=C,old158_positions_in_D4=e,new59_position_indices=data['new59_position_indices'])
    values=dict(complete_D4_canonical_four=Q,complete_D4_canonical_four_clock=Qdot,
        actual_parent_source_four=source,actual_parent_source_four_clock=sourcedot,
        fixed_cut_initial_outward_source_complete_flux_four=-Pi,
        fixed_cut_initial_outward_source_complete_flux_four_clock=-Pidot,
        native_old316_four_minus_retained_original=olddefect,
        primal_D4_momentum_separate=val(data,'complete_D4_primal_momentum'),
        primal_D4_momentum_clock_separate=val(data,'complete_D4_primal_momentum_clock'),
        full60_primal_algebraic_r_separate=val(data,'complete_D4_primal_algebraic_r'))
    for k in data:
        if k.endswith('_high')and k.startswith('all60_saved_')and'combined_four'in k:values[k[:-5]]=val(data,k[:-5])
    for k,a in values.items():
        arrays[k+'_high'],arrays[k+'_low']=_split(a);arrays.update(exact.export_acb_exact_dyadic(a,k+'_exact'))
    arc=out/'actual_original_four_D4_cauchy_source_and_initial_flux.npz';_compressed_npz(arc,arrays)
    for name,m in list(sys.modules.items()):
        p=getattr(m,'__file__',None)
        if p and(name=='bhsm'or name.startswith('bhsm.'))and Path(p).resolve().is_relative_to(ROOT):pin(Path(p).resolve())
    pin(Path(__file__))
    report=dict(classification='EXACT_ORIGINAL7_TO4_D4_CAUCHY_SOURCE_FIXED_INITIAL_FLUX_COMPOSITION',
        source_sha256=sha256(producer).hexdigest(),input_and_source_sha256=dict(sorted(pins.items())),
        archive=dict(name=arc.name,sha256=sha256(arc.read_bytes()).hexdigest(),bytes=arc.stat().st_size),
        original_old158_position_identity_upper=qdefect,
        native_old158_four_momentum_minus_retained_upper=_upper(rows(olddefect,np.arange(158,316))),
        full217_four_source_complete_momentum_upper=_upper(Pi),full217_four_momentum_clock_upper=_upper(Pidot),
        exact_same_seven_column_combination=True,initial_face_is_fixed_cut=True,
        parent_gv_added_twice=False,primal_momentum_added_to_affine_column=False,
        field_or_action_or_history_or_birth_solve_repeated=False,new_Cauchy_projection_or_correction=False,
        all60_Gauss_compatibility_or_new_retarded_solution_admitted=False,
        moving_cut_energy_domain_jet_supplied=False,physical_outgoing_derivative_or_normalized_spin_moment=False,
        original_coupled_corrections_applied=0)
    (out/'result.json').write_text(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({k:v for k,v in report.items()if k not in('input_and_source_sha256','archive')}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cauchy-folder',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args()
    run(a.cauchy_folder,a.output)
