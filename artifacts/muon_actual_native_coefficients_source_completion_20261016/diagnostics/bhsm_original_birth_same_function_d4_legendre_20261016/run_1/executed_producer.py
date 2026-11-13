"""Same-function original3 birth ports in the complete native D4 phase action.

Only cached action applications and exact labelled coordinate embeddings
are used. No birth saddle, field equation, Cauchy retraction, action/D5/
profile history or exterior solve is repeated. New momenta are computed,
not prescribed. The numerical proper3-port section is not a full226 event
selector or a physical outgoing domain.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
RADIAL='artifacts/muon_baton_zoo_radial_convergence_20261014'
D4=RADIAL+'/covariant_degree4_normalized_MP_birth_run_1'
D2B=RADIAL+'/compatible_degree2_birth_run_1/enlarged_birth_proper_three_columns_and_canonical_seeds.npz'
EXPECTED={D2B:'caef5647df5da771b07af293921206902f38cc31a1255091e955faa9552946d0',
    D4+'/actual_complete_MP_phase_action_on_normalized_rights.npz':'104aaa6f91a423750a637332bede6f5dc81705eda39c9e48e6ba44b3e1eb521a',
    D4+'/actual_product_domain_lifts_and_normalization.npz':'be8f43a9035df6ef432be4602e657480005efb4101b3f5a1c5cba0245815463a'}


def run(output,precision=224):
    out=Path(output).resolve();out.mkdir(parents=True,exist_ok=False)
    source=Path(__file__).read_bytes();(out/'executed_producer.py').write_bytes(source);pins={}
    def pin(p):
        p=Path(p);p=p if p.is_absolute()else ROOT/p;k=p.relative_to(ROOT).as_posix();h=sha256(p.read_bytes()).hexdigest()
        if k in EXPECTED and h!=EXPECTED[k]:raise ValueError('Exact cached action/birth operand required: '+k)
        pins[k]=h;return p
    def load(p):
        p=pin(p)
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    sys.path.insert(0,str(ROOT/'src'))
    from flint import ctx,acb_mat
    from bhsm.interface.muon_stored_admission_correction import _matrix,_upper
    from bhsm.interface.muon_stored_fiber_canonical_tangent import _split
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    ctx.prec=int(precision)
    hl=lambda z,k:_matrix(z[k+'_high'])+_matrix(z[k+'_low'])
    rows=lambda a,ix:acb_mat([[a[int(i),j]for j in range(a.ncols())]for i in ix])
    b=load(D2B)
    a={d:load(f'{RADIAL}/compatible_explicit_maps_all_epochs_run_1/birth_degree_{d:02d}_compatible_connected_radial_action.npz')for d in(2,4)}
    products={d:load(f'{RADIAL}/covariant_product_functions_and_contacts_run_1/birth_degree_{d:02d}_covariant_product_functions_and_moving_contacts.npz')for d in(2,4)}
    tables={d:load(f'{RADIAL}/literal_MP_point_wall_tables_run_1/degree_{d:02d}_literal_MP_original_and_extra_point_wall_tables.npz')for d in(2,4)}
    maps=load(D4+'/actual_product_domain_lifts_and_normalization.npz')
    native=load(D4+'/actual_complete_MP_phase_action_on_normalized_rights.npz')
    other=load(D4+'/actual_covariant_product_MP_proper_birth_columns_and_nonzero_seeds.npz')
    n0,n=int(b['dynamic_count']),int(maps['dynamic_count']);full=int(maps['full_dimension'])
    if (n0,n,full)!=(158,217,746):raise ValueError('Exact old316 and completeD4 chart required')
    for z in(*a.values(),*products.values(),other):
        if not np.array_equal(z['raw_pair'],b['raw_pair'])or not np.array_equal(z['reference_pair'],b['reference_pair']):raise ValueError('Changed base field/reference germ')
    if any(z['coordinate_time'].item()!=0 for z in(*a.values(),*products.values()))or b['birth_coordinate_time'].item()!=0:raise ValueError('Exact original birth0 clock required')
    if any(not np.array_equal(a[2][k],a[4][k])for k in('rho','quadrature')):raise ValueError('No point/quadrature-rule change in this source application')
    # Literal function labels, not a minimum-norm fit or a phase retraction.
    comp=np.full(368,-1,int)
    for old,new in zip(a[2]['current288_to_augmented'],a[4]['current288_to_augmented']):comp[int(old)]=int(new)
    for key,count in(('added_position_indices',32),('added_rate_indices',32),('added_Gauss_indices',8),
            ('derivative_compatible_position_indices',4),('derivative_compatible_rate_indices',4)):
        for old,new in zip(a[2][key],a[4][key][:count]):
            if comp[int(old)] not in(-1,int(new)):raise ValueError('Overlapping function labels disagree')
            comp[int(old)]=int(new)
    if np.any(comp<0)or len(np.unique(comp))!=368:raise ValueError('Every old field/velocity/Gauss coordinate needs an injective function label')
    cov=np.asarray(maps['previous_radial_to_augmented'],int);embedding=cov[comp]
    if not np.array_equal(embedding[n0:2*n0],n+embedding[:n0]):raise ValueError('Paired q/v incidence must survive')
    globalmap=np.r_[np.arange(252),252+embedding]
    Uold=hl(b,'full_two_arm_fixed_position_phase');U=acb_mat(full,3)
    for old,new in enumerate(globalmap):
        for j in range(3):U[int(new),j]=Uold[old,j]
    phaseids=np.asarray(maps['phase_to_full_action_indices'],int)
    if not np.array_equal(phaseids,native['test_full_action_indices']):raise ValueError('Complete same-native phase test incidence required')
    if _upper(rows(U,np.r_[np.arange(106),252+np.arange(n)]))!=0:raise ValueError('Original fixed birth positions must remain EXACTLY fixed')
    if not np.array_equal(maps['normalized_phase_right_high'],native['actual_right_high'])or not np.array_equal(maps['normalized_phase_right_low'],native['actual_right_low']):raise ValueError('Action rights and normalized basis changed')
    R=hl(maps,'normalized_phase_right');M=rows(R,phaseids)
    # Solve coordinate conversion ONLY: no action equation/saddle is solved.
    coeff=M.solve(rows(U,phaseids));representation=R*coeff-U
    if _upper(representation)>1e-25:raise ValueError('Complete same-function phase representation failed')
    HR=hl(native,'phase_Hessian_on_actual_right')*coeff
    parentHR=hl(native,'parent_own_phase_Hessian_on_actual_right')*coeff
    childHR=hl(native,'child_inherited_phase_Hessian_on_actual_right')*coeff
    if _upper(HR-parentHR-childHR)>1e-25:raise ValueError('Parent+inherited child/source action must be counted once')
    # All source/point/density columns are preserved, not only old canonical data.
    Ucompat=acb_mat(692,3)
    for i in range(252):
        for j in range(3):Ucompat[i,j]=Uold[i,j]
    for i,new in enumerate(comp):
        for j in range(3):Ucompat[252+int(new),j]=Uold[252+i,j]
    direction_checks={};direction_arrays={}
    for key in('saved_old_full_point_lift','saved_old_full_density_lift'):
        f2,f4=(products[d][key]for d in(2,4));left=_matrix(f2.reshape(-1,f2.shape[-1]))*Uold
        right=_matrix(f4.reshape(-1,f4.shape[-1]))*Ucompat
        direction_checks[key+'_same_direction_upper']=_upper(left-right)
        direction_arrays[key+'_old3_direction']=left;direction_arrays[key+'_D4_embedded3_direction']=right
    # Native MP point/wall coefficient tables are checked on every old extra
    # slot. Identical parent/raw incidences retain the remaining original part.
    oldextra=np.asarray(a[2]['extra_coordinates_to_full'],int)
    d4extra={int(v):j for j,v in enumerate(maps['extra_coordinates_to_full'])}
    keep=np.array([d4extra[int(globalmap[int(k)])]for k in oldextra])
    for name in('original_gauge_basis','original_gauge_radial_basis','original_wall_trace_map'):
        if not np.array_equal(tables[2][name+'_high'],tables[4][name+'_high'])or not np.array_equal(tables[2][name+'_low'],tables[4][name+'_low']):raise ValueError('Original native point/wall tables changed')
    def column_matrix(z,k,selected=None):
        h,l=z[k+'_high'],z[k+'_low']
        if selected is not None:h,l=h[...,selected],l[...,selected]
        return _matrix(h.reshape(-1,h.shape[-1]))+_matrix(l.reshape(-1,l.shape[-1]))
    for kind in('point','wall'):
        left=column_matrix(tables[2],'compatible_extra_'+kind+'_lift')
        right=column_matrix(maps,'extra_'+kind+'_lift',keep)
        difference=left-right;direction_checks['native_MP_extra_'+kind+'_table_upper']=_upper(difference)
        direction_checks['native_MP_extra_'+kind+'_direction_upper']=_upper(difference*rows(Uold,oldextra))
    if max(direction_checks.values())>2e-10:raise ValueError('Same field/source/point/wall/density direction was not preserved')
    # E and F remain the original supplied section. The independently solved
    # enlargedD4 saddle has a different phase section and is NOT substituted.
    oldphase=np.asarray(b['phase_to_full_action_indices'],int);newinverse={int(v):i for i,v in enumerate(phaseids)}
    selected=np.array([newinverse[int(globalmap[int(v)])]for v in oldphase])
    E=np.zeros((6,len(phaseids)),complex);F=np.zeros((len(b['named_frames']),len(phaseids)),complex)
    E[:,selected]=b['proper_trace'];F[:,selected]=b['named_frames']
    qphase=rows(U,phaseids);ports=_matrix(E)*qphase-_matrix(b['common_port_map']);frames=_matrix(F)*qphase
    if max(_upper(ports),_upper(frames))>2e-10:raise ValueError('Original proper3 ports/named frames changed')
    if _upper(_matrix(other['proper_trace'])*qphase-_matrix(b['common_port_map']))>2e-10:raise ValueError('Actual completeD4 proper traces do not reproduce original ports')
    Pi=rows(HR,np.arange(106,106+n));Gauss=rows(HR,np.arange(106+n+40,len(phaseids)))
    pg=hl(native,'phase_gradient');primalPi=rows(pg,np.arange(106,106+n));primalGauss=rows(pg,np.arange(106+n+40,len(phaseids)))
    Q=acb_mat(2*n,3)
    for i in range(n):
        for j in range(3):Q[n+i,j]=Pi[i,j]
    newq=np.setdiff1d(np.arange(n),embedding[:n0]);newPi=rows(Pi,newq)
    oldPi=hl(b,'child_source_complete_canonical_pair');retained_oldPi=rows(oldPi,np.arange(n0,2*n0))
    arrays=dict(old368_to_complete_D4_child=embedding,old620_to_complete_D4_full=globalmap,
        coordinate_time=b['birth_coordinate_time'],raw_pair=b['raw_pair'],reference_pair=b['reference_pair'],
        dynamic_count=np.asarray(n),phase_test_full_indices=phaseids,new_position_indices=newq,
        original_proper_trace_on_complete_D4=E,original_named_frames_on_complete_D4=F,original_common_port_map=b['common_port_map'])
    values=dict(original_three_full_birth_phase=Uold,same_function_three_full_D4_birth_phase=U,
        normalized_phase_coordinates=coeff,complete_phase_action_on_same_function_three_ports=HR,
        independent_parent_own_phase_action=parentHR,independent_inherited_child_source_phase_action=childHR,
        full_D4_child_canonical_three_port=Q,full_D4_child_momentum_three_port=Pi,
        new59_D4_child_momentum_three_port=newPi,full_D4_child_Gauss_three_port=Gauss,
        primal_full_D4_child_momentum=primalPi,primal_full_D4_child_Gauss_r=primalGauss,
        native_old158_momentum_minus_saved_original_binary=rows(Pi,embedding[:n0])-retained_oldPi,
        original_proper_port_identity_rows=ports,original_named_frame_identity_rows=frames,
        same_function_normalized_representation_rows=representation,**direction_arrays)
    for name,value in values.items():arrays[name+'_high'],arrays[name+'_low']=_split(value)
    archive=out/'actual_same_function_original3_birth_D4_canonical_and_source_block.npz';_compressed_npz(archive,arrays)
    for name,module in list(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if p and(name=='bhsm'or name.startswith('bhsm.'))and Path(p).resolve().is_relative_to(ROOT):pin(Path(p).resolve())
    pin(Path(__file__));pin('src/bhsm/interface/muon_birth_full_proper_port_saddle.py')
    report=dict(classification='SAME_FUNCTION_ORIGINAL3_BIRTH_PORTS_COMPLETE_D4_CACHED_NATIVE_LEGENDRE_SOURCE_BLOCK',
        source_sha256=sha256(source).hexdigest(),input_and_source_sha256=dict(sorted(pins.items())),
        archive=dict(name=archive.name,bytes=archive.stat().st_size,sha256=sha256(archive.read_bytes()).hexdigest()),
        direction_identity_checks=direction_checks,normalized_coordinate_identity_upper=_upper(representation),
        original_proper_port_identity_upper=_upper(ports),original_named_frame_identity_upper=_upper(frames),
        new59_momentum_on_same_original3_ports_upper=_upper(newPi),full217_momentum_upper=_upper(Pi),
        full60_Gauss_on_same_original3_ports_upper=_upper(Gauss),primal_full60_Gauss_r_upper=_upper(primalGauss),
        native_old158_momentum_minus_saved_original_binary_upper=_upper(values['native_old158_momentum_minus_saved_original_binary']),
        same_raw_reference_time_point_wall_density_functions=True,new_zero_field_coefficients_are_representation_only=True,
        new_canonical_momenta_prescribed_zero=False,original_three_parent_source_directions_unchanged=True,
        enlarged_birth_saddle_or_action_or_D5_or_history_recomputed=False,coordinate_conversion_solve_not_equation_solve=True,
        primal_Gauss_r_and_linear_Gauss_Kports_separate=True,
        numerical_proper3_port_section_is_full226_event_selector=False,
        new_full_retarded_response_or_physical_outgoing_domain_solved=False,physical_radial_convergence=False,
        physical_energy_field_derivative_or_normalized_spin_or_moment=False,original_coupled_corrections_applied=0,
        arithmetic_scope='224-bit applications of saved MP high+low coefficients; cached coefficient/normalization/quadrature and physical-domain errors are not enclosed')
    (out/'result.json').write_text(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({k:v for k,v in report.items()if k not in('input_and_source_sha256','archive')}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path);p.add_argument('--precision',default=224,type=int);a=p.parse_args()
    try:run(a.output,a.precision)
    except Exception as e:
        import traceback
        if a.output.exists():(a.output/'failure.json').write_text(json.dumps(dict(error=repr(e),traceback=traceback.format_exc(),source_sha256=sha256(Path(__file__).read_bytes()).hexdigest()),indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
        raise
