"""Incoming OWN-parent forced shape response and complete birth/source return.

Saved negative proof cells are traversed in positive chronology.  The
initial ORIGINAL canonical variation is zero; this is the declared inverse
domain for a response, not independently given physical environment data.
"""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
from flint import acb_mat,ctx
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from evaluate_muon_per_arm_canonical_source import clean
from bhsm.interface.muon_normal_shape_induced_canonical_response import forced_original_canonical_jacobi,source_complete_true_face
from bhsm.interface.muon_complex_canonical_compatibility import canonical_central_frame
from bhsm.interface.muon_stored_admission_correction import _matrix
from bhsm.interface.muon_stored_fiber_canonical_tangent import _split
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(source,history,output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve incoming response applications')
    pins={};archives={}
    def read(folder,name):
        p=ROOT/folder/name;b=p.read_bytes();pins[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
        if p.suffix=='.json':return json.loads(b)
        with np.load(p)as z:return{k:z[k].copy()for k in z.files}
    md=read(source,'result.json');hm=read(history,'result.json')
    phase,_=retained_input('incoming',pins);P=phase['coordinates']['lift'];rep=phase['representation']
    names=('far','cell_0001','corner','cell_0000','birth')
    points={n:read(source,n+'_own_shape_drive.npz')for n in names}
    F=canonical_central_frame(points['birth']['raw'],rep)['named_frame_covectors']
    if np.any(F[:,:106]):raise ValueError('the named frames must not alter velocity momentum')
    out.mkdir(parents=True)
    def save(name,a):
        p=out/name;_compressed_npz(p,{k:v for k,v in a.items()if isinstance(v,np.ndarray)})
        if p.stat().st_size>=10*1024**2:raise ValueError('split complete source/action arrays')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    def split_sum(*pairs):
        old=ctx.prec;ctx.prec=192
        try:
            q=acb_mat(pairs[0][0].shape[0],pairs[0][0].shape[1])
            for h,l in pairs:q+=_matrix(h)+_matrix(l)
            return _split(q)
        finally:ctx.prec=old
    def product(A,h,l):
        old=ctx.prec;ctx.prec=192
        try:return _split(_matrix(A)*(_matrix(h)+_matrix(l)))
        finally:ctx.prec=old
    records=[];work_records=[]
    for sector in('base','area'):
        sourcekey='integrated_weak_bulk_source'if sector=='base'else'area_integrated_weak_bulk_source'
        ratekey='source_rate'if sector=='base'else'area_source_rate'
        g=lambda n:points[n][sourcekey]
        B=lambda n:points[n][ratekey]
        qh=np.r_[np.zeros(106),g('far')[106:212]][:,None];ql=np.zeros_like(qh)
        outputs={}
        for name in names:
            p=points[name];H=p['original_own_Hessian'];time=p['coordinate_time'].item()
            if name.startswith('cell_'):
                k=int(name[5:]);stage=read(history,f'incoming_{k:04d}_actual_base.npz')
                if not np.array_equal(H,stage['stage_Hessian']):raise ValueError('OWN stage action changed')
                h=-stage['step'].item()
                if complex(h).real<=0:raise ValueError('incoming traversal must be chronologically positive')
                a=forced_original_canonical_jacobi(H,h,F,qh,ql,g(name))
                ih,il=a['induced_stage_direction_high'],a['induced_stage_direction_low']
                qh,ql=a['effective_canonical_final_high'],a['effective_canonical_final_low']
                rec=dict(sector=sector,point=name,time=time,positive_step=h,
                    original358_upper=a['original_forced_rows_upper'],frame_reaction_upper=a['frame_reaction_rows_upper'],
                    framed360_upper=a['framed_rows_upper'],literal_transpose_upper=a['literal_transpose_rows_upper'])
            else:
                a=source_complete_true_face(H,F,qh,ql,g(name),B(name))
                ih,il=a['induced_phase_high'],a['induced_phase_low']
                rec=dict(sector=sector,point=name,time=time,original146_upper=a['original_forced_rows_upper'],
                    frame_reaction_upper=a['frame_reaction_rows_upper'],framed148_upper=a['framed_rows_upper'],
                    full_rate_work_decomposition_upper=a['full_rate_work_decomposition_upper'],
                    full_rate_work=a['complete_rate_work'].item(),source_offset_work=a['rate_source_offset_contact'])
            bh=p['normal_shape_direction'][:,None];bl=np.zeros_like(bh)
            th,tl=split_sum((ih,il),(bh,bl))if sector=='base'else(ih.copy(),il.copy())
            original_pi_h,original_pi_l=product(H[106:212],ih,il)
            total_pi_h,total_pi_l=product(H[106:212],th,tl)
            direct_pi_h,direct_pi_l=product(H[106:212],bh,bl)
            raw_i=product(P,ih,il);raw_b=product(P,bh,bl);raw_t=product(P,th,tl)
            ch,cl=split_sum((ih[:106],il[:106]),) # preserve the complete x part
            original_canonical_h=np.vstack((ch,original_pi_h));original_canonical_l=np.vstack((cl,original_pi_l))
            total_canonical_h=np.vstack((th[:106],total_pi_h));total_canonical_l=np.vstack((tl[:106],total_pi_l))
            rec.update(induced_phase_norm=float(np.linalg.norm(ih+il)),total_phase_norm=float(np.linalg.norm(th+tl)),
                source_norm=float(np.linalg.norm(g(name))),full_rate_conormal_norm=float(np.linalg.norm(B(name))))
            arrays={k:v for k,v in a.items()if isinstance(v,np.ndarray)}
            arrays.update(actual_raw=p['raw'],actual_master=p['master'],actual_coordinate_time=np.array(time),
                original_own_Hessian=H,original_own_gradient=p['original_own_gradient'],
                effective_source=g(name),effective_source_g_v=g(name)[106:212],full_rate_conormal=B(name),
                direct_phase_high=bh,direct_phase_low=bl,induced_phase_high=ih,induced_phase_low=il,
                total_phase_high=th,total_phase_low=tl,
                direct_raw_high=raw_b[0],direct_raw_low=raw_b[1],induced_raw_high=raw_i[0],induced_raw_low=raw_i[1],
                total_raw_high=raw_t[0],total_raw_low=raw_t[1],
                original_induced_canonical_high=original_canonical_h,original_induced_canonical_low=original_canonical_l,
                total_original_canonical_high=total_canonical_h,total_original_canonical_low=total_canonical_l,
                direct_original_Pi_high=direct_pi_h,direct_original_Pi_low=direct_pi_l,
                effective_canonical_high=qh,effective_canonical_low=ql,named_frame_covectors=F,
                original_base_rows=p['original_base_rows'])
            save(f'{sector}_{name}_induced_and_total.npz',arrays);outputs[name]=(ih,il,a)
            records.append(rec);print(json.dumps(clean(rec),sort_keys=True),flush=True)
        bulk=sum((-read(history,f'incoming_{k:04d}_actual_base.npz')['step'].item())*
            (g(f'cell_{k:04d}')@(outputs[f'cell_{k:04d}'][0]+outputs[f'cell_{k:04d}'][1])[:,0])for k in(1,0))
        initial=outputs['far'][2]['complete_rate_work'].item();final=outputs['birth'][2]['complete_rate_work'].item()
        corner=B('corner')@(outputs['corner'][0]+outputs['corner'][1])[:,0]
        total=bulk+final-initial+corner-corner
        save(f'{sector}_complete_incoming_work.npz',dict(bulk_work=np.array(bulk),far_rate_work=np.array(initial),
            birth_rate_work=np.array(final),same_germ_corner_left_minus_right=np.array(corner-corner),complete_incoming_source_work=np.array(total)))
        work_records.append(dict(sector=sector,bulk_work=bulk,far_rate_work=initial,birth_rate_work=final,
            complete_incoming_source_work=total))
    for name,module in sorted(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and p and Path(p).is_relative_to(ROOT):
            p=Path(p);pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    pins[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=v for p,v in pins.items()):raise ValueError('same OWN source/action changed')
    result=dict(classification='EXECUTED_INCOMING_OWN_PARENT_FORCED_NORMAL_SHAPE_RESPONSE_AND_BIRTH_RETURN',
        input_hashes=pins,archives=archives,records=records,work=work_records,action_parameters=hm['action_parameters'],
        chronological_order=[1,0],own_parent_Hessian_not_joint_parent_block=True,
        initial_condition='original induced dx=0,dPi=0 at the computational far face; effective dp=g_v',
        full_x_v_y_rate_conormal_and_source_offset_retained=True,base_direct_shape_included_once=True,
        area_channel='common M8 gamma coefficient of normal shape source; no second direct b and no gamma assigned',
        internally_generated_gammaNone_history_not_independent_environment=True,
        physical_matching_admitted=False,physical_mode_or_pole_selected=False,
        scope='Original same OWN action fixed stored Jacobi source solve; action coefficients and finite midpoint/face domain remain their recorded approximation. No action or physical error enclosure.')
    p=out/'result.json';p.write_text(json.dumps(clean(result),sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='incoming_induced_complete',result_sha256=sha256(p.read_bytes()).hexdigest(),work=clean(work_records)),sort_keys=True),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,default=Path('artifacts/muon_incoming_own_normal_shape_20261013/run_1'))
    p.add_argument('--history',type=Path,default=Path('artifacts/muon_changing_canonical_source_20261012/run_3'))
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();materialize(a.source,a.history,a.output)
