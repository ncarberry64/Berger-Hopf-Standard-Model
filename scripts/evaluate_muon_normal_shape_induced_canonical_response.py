"""Actual forced child canonical response to corrected moving-normal source.

Original initial x/Pi are held; effective p=Pi+g_v carries the source
offset. All x/v/y rate-conormal and born-parameter contacts are retained.
The represented two-cell IVP is a computational response, not a physical
birth/formation/exterior selector or a selection of the normal amplitude.
"""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
from flint import ctx,acb_mat
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_normal_shape_induced_canonical_response import forced_original_canonical_jacobi,source_complete_true_face
from bhsm.interface.muon_actual_normal_shape_source import proper_normal_shape_coefficient
from bhsm.interface.muon_stored_admission_correction import _matrix,_mid
from bhsm.interface.muon_stored_fiber_canonical_tangent import _split
from bhsm.interface.muon_complex_canonical_compatibility import canonical_central_frame
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
from evaluate_muon_d5_finite_trace_pole_match import clean


def materialize(rate_source,weak_source,history,output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve every canonical response')
    pins={};archives={}
    def read(folder,name):
        p=ROOT/folder/name;pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
        if p.suffix=='.json':return json.loads(p.read_bytes())
        with np.load(p)as z:return{k:z[k].copy()for k in z.files}
    rm=read(rate_source,'result.json');wm=read(weak_source,'result.json');hm=read(history,'result.json')
    if not hm['all_steps_and_endpoints_passed']:raise ValueError('same admitted original complex canonical cells required')
    phase=load_profile_preserving_phase('artifacts/muon_inherited_finite_normal_phase_20261011/run_1',repository=ROOT)
    pins.update(phase['input_hashes']);rep=phase['representation'];P=phase['coordinates']['lift']
    names=['initial','cell_0000','corner_0000','cell_0001','final'];points={}
    if hm['steps']!=2:raise ValueError('the supplied actual bounded source history has two cells')
    ctx_old=ctx.prec;ctx.prec=192
    try:
        for name in names:
            rate=read(rate_source,name+'_bounded_rate_and_shape.npz');weak=read(weak_source,name+'_shape_weak_application.npz')
            af=proper_normal_shape_coefficient(weak['raw_pair'][1],P);b=acb_mat(252,1)
            b[37,0]=complex(af['value']);da=_matrix(np.r_[np.zeros(252),af['gradient']])
            actual_rate=_matrix(rate['literal_two_term_rhs_rate_high'])+_matrix(rate['literal_two_term_rhs_rate_low'])
            b[143,0]=(da.transpose()*actual_rate)[0,0]
            bh,bl=_split(b)
            points[name]=dict(rate=rate,weak=weak,direct_high=bh,direct_low=bl,time=weak['coordinate_time'].item())
    finally:ctx.prec=ctx_old
    F=canonical_central_frame(points['initial']['weak']['raw_pair'][1],rep)['named_frame_covectors']
    if np.any(F[:,:106]!=0):raise ValueError('named frame is the owned algebraic At selector, not a velocity constraint')
    out.mkdir(parents=True)
    def save(name,a):
        p=out/name;_compressed_npz(p,{k:v for k,v in a.items()if isinstance(v,np.ndarray)})
        if p.stat().st_size>=10*1024**2:raise ValueError('split compact canonical/source arrays')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    def raw_split(high,low):
        old=ctx.prec;ctx.prec=192
        try:return _split(_matrix(P)*(_matrix(high)+_matrix(low)))
        finally:ctx.prec=old
    def sum_split(*pairs):
        old=ctx.prec;ctx.prec=192
        try:
            total=acb_mat(len(pairs[0][0]),1)
            for hi,lo in pairs:total+=_matrix(hi)+_matrix(lo)
            return _split(total)
        finally:ctx.prec=old
    records=[];sector_results={};metadata=[]
    for sector in('base','area'):
        g=lambda p:points[p]['rate']['literal_two_term_rhs_'+sector+'_bulk_source']
        B=lambda p:points[p]['rate']['literal_two_term_rhs_'+sector+'_boundary_source']
        source0=g('initial')[252:];canonical_hi=np.r_[np.zeros(106),source0[106:212]][:,None];canonical_lo=np.zeros_like(canonical_hi)
        output_points={}
        def face(name):
            point=points[name];H=point['rate']['literal_child_Hessian'];src=g(name)[252:]
            r=source_complete_true_face(H,F,canonical_hi,canonical_lo,src,B(name)[252:])
            return r
        for index,name in enumerate(names):
            point=points[name];H=point['rate']['literal_child_Hessian'];src=g(name)[252:]
            if name.startswith('cell_'):
                j=int(name[5:]);stage=read(history,f'step_{j:04d}_stage.npz');step=stage['coordinate_step'].item()
                reproduction=float(np.max(abs(H-stage['stage_Hessian'])))
                a=forced_original_canonical_jacobi(H,step,F,canonical_hi,canonical_lo,src)
                ih,il=a['induced_stage_direction_high'],a['induced_stage_direction_low']
                canonical_hi,canonical_lo=a['effective_canonical_final_high'],a['effective_canonical_final_low']
                record=dict(sector=sector,point=name,actual_time=point['time'],step=step,
                    source_complete_original358_upper=a['original_forced_rows_upper'],frame_reaction_upper=a['frame_reaction_rows_upper'],
                    framed360_upper=a['framed_rows_upper'],literal_transpose_upper=a['literal_transpose_rows_upper'],
                    original_source_assembly_upper=a['original_plus_reaction_assembly_upper'],
                    original_saved_action_Hessian_difference_max=reproduction)
            else:
                a=face(name);ih,il=a['induced_phase_high'],a['induced_phase_low']
                record=dict(sector=sector,point=name,actual_time=point['time'],
                    source_complete_original146_upper=a['original_forced_rows_upper'],frame_reaction_upper=a['frame_reaction_rows_upper'],
                    framed148_upper=a['framed_rows_upper'],full_rate_work_decomposition_upper=a['full_rate_work_decomposition_upper'],
                    complete_rate_source_work=a['complete_rate_work'].item(),source_offset_contact=a['rate_source_offset_contact'])
            bh,bl=point['direct_high'],point['direct_low']
            # Direct normal shape is included ONCE in the base channel.
            # Area is a mixed common-gamma coefficient source, not another
            # independently repeated normal shape or physical gamma value.
            th,tl=sum_split((ih,il),(bh,bl))if sector=='base'else(ih.copy(),il.copy())
            ri_h,ri_l=raw_split(ih,il);rb_h,rb_l=raw_split(bh,bl);rt_h,rt_l=raw_split(th,tl)
            record.update(induced_phase_norm=float(np.linalg.norm(ih+il)),direct_phase_norm=float(np.linalg.norm(bh+bl)),
                total_phase_norm=float(np.linalg.norm(th+tl)),induced_raw_norm=float(np.linalg.norm(ri_h+ri_l)),
                total_raw_norm=float(np.linalg.norm(rt_h+rt_l)),actual_direct_birth_position_not_zero=bool(np.max(abs(bh[:106]+bl[:106]))>0))
            # Independent stored-H source-vs-Hb comparison, no replacement
            # of the supplied rounded source by a theoretically zero EL.
            defect=H@(bh+bl)[:,0]-src
            record['provided_source_minus_Hb_norm']=float(np.linalg.norm(defect))
            arrays={k:v for k,v in a.items()if isinstance(v,np.ndarray)}
            arrays.update(actual_raw_pair=point['weak']['raw_pair'],actual_reference_pair=point['weak']['reference_pair'],
                actual_coordinate_time=np.array(point['time']),literal_child_Hessian=H,original_child_gradient=point['rate']['literal_child_gradient'],
                full504_effective_source=g(name),full504_rate_conormal=B(name),
                direct_phase_high=bh,direct_phase_low=bl,induced_phase_high=ih,induced_phase_low=il,
                total_phase_high=th,total_phase_low=tl,direct_raw_high=rb_h,direct_raw_low=rb_l,
                induced_raw_high=ri_h,induced_raw_low=ri_l,total_raw_high=rt_h,total_raw_low=rt_l,
                effective_canonical_high=canonical_hi,effective_canonical_low=canonical_lo,
                provided_source_minus_Hb=defect,named_frame_covectors=F)
            save(f'{sector}_{name}_induced_and_total.npz',arrays);output_points[name]=(ih,il,th,tl,a)
            records.append(record);print(json.dumps(clean(record),sort_keys=True),flush=True)
        # Complete work retains rate_v/rate_y and the source offset at all
        # true faces. The internal face is provided in the SAME chart on
        # both sides, so its left-minus-right equality is verified here.
        work=sum(read(history,f'step_{j:04d}_stage.npz')['coordinate_step'].item()*
            (g(f'cell_{j:04d}')[252:]@(output_points[f'cell_{j:04d}'][0]+output_points[f'cell_{j:04d}'][1])[:,0])for j in range(2))
        initial=output_points['initial'][4]['complete_rate_work'].item();final=output_points['final'][4]['complete_rate_work'].item()
        corner_left=B('corner_0000')[252:]@(output_points['corner_0000'][0]+output_points['corner_0000'][1])[:,0]
        corner_right=B('corner_0000')[252:]@(output_points['corner_0000'][0]+output_points['corner_0000'][1])[:,0]
        born=np.zeros(252,complex)
        for j in range(2):
            name=f'cell_{j:04d}';t=points[name]['time'];J=np.eye(252,dtype=complex)
            J[np.arange(37),106+np.arange(37)]+=t;J[37,143]+=t
            born+=read(history,f'step_{j:04d}_stage.npz')['coordinate_step'].item()*(J.T@g(name)[:252])
        for name,sign in(('initial',-1),('final',1)):
            t=points[name]['time'];J=np.eye(252,dtype=complex);J[np.arange(37),106+np.arange(37)]+=t;J[37,143]+=t
            born+=sign*(J.T@B(name)[:252])
        save(f'{sector}_complete_temporal_and_born_work.npz',dict(bulk_work=np.array(work),initial_full_rate_work=np.array(initial),
            final_full_rate_work=np.array(final),corner_left_minus_right=np.array(corner_left-corner_right),
            complete_child_source_work=np.array(work+final-initial+corner_left-corner_right),born_parameter_source_cotangent=born))
        metadata.append(dict(sector=sector,complete_child_source_work=work+final-initial+corner_left-corner_right,
            initial_full_rate_work=initial,final_full_rate_work=final,coefficient_corner_work=corner_left-corner_right,
            born_parameter_source_cotangent_norm=float(np.linalg.norm(born)),parent_born_not_bulk_forcing=True))
        sector_results[sector]=output_points
    for name,module in sorted(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and p and Path(p).is_relative_to(ROOT):
            p=Path(p);pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    for p in(Path(__file__),ROOT/'tests/test_muon_normal_shape_induced_canonical_response.py'):
        pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    if any(sha256((ROOT/k).read_bytes()).hexdigest()!=v for k,v in pins.items()):raise ValueError('same original action/source/domain required')
    result=dict(classification='EVALUATED_INDUCED_MOVING_NORMAL_CANONICAL_RESPONSE_AND_FULL_SOURCE_CONTACTS',input_hashes=pins,archives=archives,
        records=records,temporal_and_born_work=metadata,action_parameters=hm['action_parameters'],
        initial_condition='original induced dx=0,dPi=0; effective dp=g_eff_v(initial), with source-complete v/y and all named reactions',
        final_condition='canonical output and full g_rate true-face work; no physical terminal/retarded selector',
        bulk_equation='J358 dz+[0,-h*g_eff_x,g_eff_v,g_eff_y]+named frame reaction=0',
        source_rate_conormal='full child x/v/y pulled back by literal true-face adjoint plus source-offset contact; not first106 only',
        direct_plus_induced_combined_before_projection=True,total_birth_normal_shape_not_silently_zero=True,
        area_channel='mixed common-gamma coefficient source on same base; no second direct normal shape or independent child-gamma family',
        parent_profile_and_reference_explicit_clock_once=True,parent_born_source_parameter_held_not_future_parent_dynamics=True,
        internal_trueface_rate_chart_supplied_on_both_sides=True,reset73_not_added_as_bulk_constraint=True,
        source_rounding_and_exact_stored_matrix_representation_not_action_accuracy=True,
        original_birth226_max=wm['original_birth226_max'],original_all67_work=wm['original_all67_clock_scaled_mechanical_work'],
        physical_mode_matched_base_retarded_tail_Gamma2_LSZ_Pauli_or_native_observable_admitted=False,
        physical_a_mu=None,physical_g_mu=None,error_enclosure=None)
    p=out/'result.json';p.write_text(json.dumps(clean(result),sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256(p.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rate-source',type=Path,default=Path('artifacts/muon_normal_shape_rate_attribution_20261012/run_1'))
    p.add_argument('--weak-source',type=Path,default=Path('artifacts/muon_normal_shape_weak_consumption_20261012/run_1'))
    p.add_argument('--history',type=Path,default=Path('artifacts/muon_reached_complex_normal_history_20261012/trial_0000_run_1'));p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();materialize(a.rate_source,a.weak_source,a.history,a.output)
