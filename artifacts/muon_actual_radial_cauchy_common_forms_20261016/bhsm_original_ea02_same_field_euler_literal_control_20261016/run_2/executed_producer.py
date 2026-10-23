"""Literal polynomial checks of the saved same-field radial Euler operands.

No history, Hessian or field solve is repeated. The independent bulk first
variation and momentum product rule use the saved actual point/density germs.
Only the already-owned scalar-wall coefficient value is evaluated anew.
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
RUNTIME='artifacts/muon_baton_zoo_maximal_current_realization_20261013/actual_new620_fresh_native_MP_new_exact_R7_clock_control_run_1'
TARGET='artifacts/muon_baton_zoo_maximal_current_realization_20261013/actual_linear_cut_compatible368_MP_full_operator_blocked_run_2/actual_precise_direct_CHILD620_and_full368_canonical_source_operands.npz'


def run(repository,application_root,output):
    root,base,out=Path(repository).resolve(),Path(application_root).resolve(),Path(output).resolve();out.mkdir(parents=True,exist_ok=False)
    pins={};source=Path(__file__).read_bytes();(out/'executed_producer.py').write_bytes(source)
    def pin(p):
        p=Path(p);key=p.relative_to(root).as_posix()if p.is_relative_to(root)else'application/'+p.relative_to(base).as_posix()
        pins[key]=sha256(p.read_bytes()).hexdigest();return p
    def load(p):
        p=pin(p)
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    def module(name,path):
        spec=importlib.util.spec_from_file_location(name,pin(root/path));m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
    sys.path[:0]=[str(root/'src'),str(root/'scripts')]
    from flint import acb,acb_mat,ctx
    from bhsm.interface.muon_stored_admission_correction import _matrix,_upper
    from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
    from bhsm.interface.muon_parent_mean_causal_action import MAXWELL_TO_CAP
    from bhsm.interface.muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
    from bhsm.interface.muon_literal_euclidean_wall_action import VOLUME
    ctx.prec=224
    module('bhsm_baton_zoo_exact_acb_packets',RUNTIME+'/bhsm_baton_zoo_exact_acb_packets_imported_runtime.py')
    ex=module('bhsm_exact_action_balls',RUNTIME+'/bhsm_exact_action_balls_imported_runtime.py')
    packed=module('literal_control_scalar',RUNTIME+'/new620_fresh_actual_native_MP_scalar_imported_runtime.py')
    chart=module('literal_control_chart',RUNTIME+'/new620_fresh_same_material_equations_chart4_imported_runtime.py')
    phase=load_profile_preserving_phase('artifacts/muon_inherited_finite_normal_phase_20261011/run_1',repository=root);pins.update(phase['input_hashes']);rep=phase['representation']
    target=load(root/TARGET)
    def C(x):return x if isinstance(x,acb)else acb(complex(x))
    def exact(z,k):return ex.parse_acb_exact_dyadic(z,k+'_exact')
    def hi(z,k):return _matrix(z[k+'_high'])+_matrix(z[k+'_low'])
    def add(a,b):return[x+y for x,y in zip(a,b)]
    def sub(a,b):return[x-y for x,y in zip(a,b)]
    def scale(s,a):return[s*x for x in a]
    def dot(a,b):return sum((x*y for x,y in zip(a,b)),C(0))
    factor=C(float(1/np.sqrt(2)))
    def comm(a,b):return[factor*(a[1]*b[2]-a[2]*b[1]),factor*(a[2]*b[0]-a[0]*b[2]),factor*(a[0]*b[1]-a[1]*b[0]),C(0)]
    def groups(a,r,k):return[[a[r,20*k+4*f+c]for c in range(4)]for f in range(5)]
    generators=higgs_u2_real_representation()['real_generators']
    H=[C(v)for v in target['raw_pair'][1,260:264]]
    def O(a):return[sum((a[k]*sum((C(generators[k][i,j])*H[j]for j in range(4)),C(0))for k in range(4)),C(0))for i in range(4)]
    # Constant geometry coefficient evaluation, without action/gradient/clock
    # seeding, only supplies the original scalar-wall wS value.
    packed.PhaseJet.nj=0;packed.PhaseJet.nr=1;packed.PhaseJet.include_first=False
    with packed.OriginalGeometryPatch('independent_mp_same_material_equations',3,chart.anchored_material_chart4)as G:
        cap=G.holomorphic_cap_and_weights([packed.PhaseJet(C(v))for v in target['raw_pair'][1,:100]],points=rep['cap_points'])
        wS=cap['wS'].value
    records=[];data={};maps={}
    for D in (4,6):
        folder=base/f'native_epoch_D{D}_run_1';other=base/f'native_epoch_D{D}_run_2'
        for name in ('same_field_primal_position_Euler_and_Gauss.npz','native_clock_reconstructed_epoch_point_wall_maps.npz','result.json','executed_producer.py'):
            p,q=pin(folder/name),pin(other/name)
            if p.read_bytes()!=q.read_bytes():raise ValueError('Independent same-input application pair differs')
        z=load(folder/'same_field_primal_position_Euler_and_Gauss.npz');m=load(folder/'native_clock_reconstructed_epoch_point_wall_maps.npz');data[D],maps[D]=z,m
        point,pt=exact(z,'child_point_coefficients'),exact(z,'child_point_coefficients_directional_first')
        density,dt=exact(z,'child_metric_density'),exact(z,'child_metric_density_directional_first')
        wall=exact(z,'child_wall_connection');wall_fields=[[wall[0,4*f+c]for c in range(4)]for f in range(5)]
        nr=point.nrows();n=int(z['enlarged_dynamic_count']);qnew=z['new_position_indices'];extra=m['extra_coordinates_to_full']
        # Saved 3D arrays are flattened only along their two leading point
        # axes; no coordinate/family/angular projection is performed.
        T=_matrix(m['extra_point_lift_high'].reshape(-1,len(extra)))+_matrix(m['extra_point_lift_low'].reshape(-1,len(extra)))
        Tt=_matrix(m['extra_point_lift_total_clock_high'].reshape(-1,len(extra)))+_matrix(m['extra_point_lift_total_clock_low'].reshape(-1,len(extra)))
        W=_matrix(m['extra_wall_lift_high'].reshape(20,len(extra)))+_matrix(m['extra_wall_lift_low'].reshape(20,len(extra)))
        dq,dv,dvt=acb_mat(len(qnew),1),acb_mat(len(qnew),1),acb_mat(len(qnew),1)
        for ir in range(nr):
            A,At,Ar=(groups(point,ir,k)for k in range(3));Ad,Atd,Ard=(groups(pt,ir,k)for k in range(3))
            e,r,d,k,beta=[density[ir,j]for j in range(5)];ed,_,_,kd,betad=[dt[ir,j]for j in range(5)]
            X=add(sub(At[1],Ar[0]),comm(A[0],A[1]));Xd=add(sub(Atd[1],Ard[0]),add(comm(Ad[0],A[1]),comm(A[0],Ad[1])))
            Ts=[add(At[f],comm(A[0],A[f]))for f in range(2,5)]
            Rs=[add(Ar[f],comm(A[1],A[f]))for f in range(2,5)]
            Y=[sub(t,scale(beta,s))for t,s in zip(Ts,Rs)]
            Yd=[sub(add(Atd[f],add(comm(Ad[0],A[f]),comm(A[0],Ad[f]))),add(scale(betad,Rs[f-2]),scale(beta,add(Ard[f],add(comm(Ad[1],A[f]),comm(A[1],Ad[f]))))))for f in range(2,5)]
            Bs=[add(scale(C(2),A[i+2]),comm(A[j+2],A[l+2]))for i,j,l in ((0,1,2),(1,2,0),(2,0,1))]
            P=[scale(C(0),X),scale(k,X)]+[scale(e,y)for y in Y]
            Pd=[scale(C(0),X),add(scale(kd,X),scale(k,Xd))]+[add(scale(ed,y),scale(e,yd))for y,yd in zip(Y,Yd)]
            weight=C(float(MAXWELL_TO_CAP)*float(rep['radial_quadrature'][ir]))
            for j,q in enumerate(qnew):
                iq=np.flatnonzero(extra==252+q).item();iv=np.flatnonzero(extra==252+n+q).item()
                da,dat,dar=([[T[60*ir+20*b+4*f+c,iq]for c in range(4)]for f in range(5)]for b in range(3))
                dx=add(sub(dat[1],dar[0]),add(comm(da[0],A[1]),comm(A[0],da[1])))
                dr=[add(dar[f],add(comm(da[1],A[f]),comm(A[1],da[f])))for f in range(2,5)]
                dy=[sub(add(dat[f],add(comm(da[0],A[f]),comm(A[0],da[f]))),scale(beta,dr[f-2]))for f in range(2,5)]
                db=[add(scale(C(2),da[i+2]),add(comm(da[a+2],A[l+2]),comm(A[a+2],da[l+2])))for i,a,l in ((0,1,2),(1,2,0),(2,0,1))]
                dq[j,0]+=weight*(k*dot(X,dx)+e*sum((dot(a,b)for a,b in zip(Y,dy)),C(0))-r*sum((dot(a,b)for a,b in zip(Rs,dr)),C(0))-d*sum((dot(a,b)for a,b in zip(Bs,db)),C(0)))
                for f in range(5):
                    b=[T[60*ir+20+4*f+c,iv]for c in range(4)];bd=[Tt[60*ir+20+4*f+c,iv]for c in range(4)]
                    dv[j,0]+=weight*dot(P[f],b);dvt[j,0]+=weight*(dot(Pd[f],b)+dot(P[f],bd))
                if any(T[60*ir+s,iv]!=0 for s in list(range(20))+list(range(40,60))):raise ValueError('New velocity test has a non-temporal field contact')
        for j,q in enumerate(qnew):
            iq=np.flatnonzero(extra==252+q).item();iv=np.flatnonzero(extra==252+n+q).item()
            if any(W[s,iv]!=0 for s in range(20))or any(W[s,iq]!=0 for s in range(4)):raise ValueError('Unaccounted scalar-wall velocity or temporal connection variation')
            dq[j,0]-=C(2)*wS*sum((dot(O(wall_fields[f]),O([W[4*f+c,iq]for c in range(4)]))for f in range(2,5)),C(0))/C(VOLUME)
        comparisons={k:_upper(a-exact(z,k))for k,a in [('new_position_Lq',dq),('new_position_Lv',dv),('new_position_total_clock_Lv',dvt),('new_position_primal_Euler_r',dq-dvt)]}
        records.append(dict(degree=D,new_positions=len(qnew),literal_polynomial_defect_upper=comparisons))
        if max(comparisons.values())>2e-10:raise ArithmeticError('Independent literal first-variation/momentum control failed')
    def signature(D,q):
        m=maps[D];j=np.flatnonzero(m['extra_coordinates_to_full']==252+q).item();h=sha256()
        for name in ('extra_point_lift','extra_point_lift_total_clock','extra_wall_lift','extra_wall_lift_total_clock'):
            for part in ('high','low'):h.update(np.ascontiguousarray(m[name+'_'+part][...,j]).tobytes())
        return h.hexdigest()
    lookup={signature(6,q):i for i,q in enumerate(data[6]['new_position_indices'])};pairs=[]
    for i,q in enumerate(data[4]['new_position_indices']):pairs.append((i,lookup[signature(4,q)]))
    common={}
    for key in ('new_position_Lq','new_position_Lv','new_position_total_clock_Lv','new_position_primal_Euler_r'):
        a,b=exact(data[4],key),exact(data[6],key);common[key]=max(float(abs(a[i,0]-b[j,0]).upper())for i,j in pairs)
    for name,m in list(sys.modules.items()):
        p=getattr(m,'__file__',None)
        if p and(name=='bhsm'or name.startswith('bhsm.'))and Path(p).resolve().is_relative_to(root):pin(Path(p).resolve())
    pin(Path(__file__))
    result=dict(classification='INDEPENDENT_LITERAL_FIRST_VARIATION_AND_MOMENTUM_CONTROL_OF_SAME_FIELD_EULER_OPERANDS',
        source_sha256=sha256(source).hexdigest(),input_and_source_hashes=dict(sorted(pins.items())),records=records,
        exact_common_test_value_and_clock_map_matches=len(pairs),common_same_function_row_defect_upper=common,
        arithmetic_precision_bits=224,no_history_or_Hessian_or_state_solve_repeated=True,
        physical_radial_convergence=False,full_outgoing_or_derivative_or_moment=False,original_coupled_corrections_applied=0)
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(records=records,matched_common_rows=len(pairs))),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',type=Path,default=ROOT);p.add_argument('--application-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.repository,a.application_root,a.output)
