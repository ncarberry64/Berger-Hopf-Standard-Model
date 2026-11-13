"""Independent literal polynomial/product-rule check of all59x7 Jacobi rows.

Reads coefficient-only actual R/hR/Rdot exports, never the packed action
as an evaluator. The two-direction arithmetic differentiates the explicit
weak first variation and canonical momentum polynomial, not a J*h*R AD.
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
FAMILY='artifacts/muon_baton_zoo_maximal_current_realization_20261013'
RUNTIME=FAMILY+'/actual_new620_fresh_native_MP_new_exact_R7_clock_control_run_1'


def run(repository,coefficient_folder,position_folder,jacobi_folder,output):
    root,cdir,pdir,jdir,out=map(lambda p:Path(p).resolve(),(repository,coefficient_folder,position_folder,jacobi_folder,output))
    out.mkdir(parents=True,exist_ok=False);producer=Path(__file__).read_bytes();(out/'executed_producer.py').write_bytes(producer);pins={}
    def pin(path):
        p=Path(path);p=p if p.is_absolute()else root/p
        key=p.relative_to(root).as_posix()if p.is_relative_to(root)else str(p);pins[key]=sha256(p.read_bytes()).hexdigest();return p
    def read(path):
        p=pin(path)
        if p.suffix=='.json':return json.loads(p.read_bytes())
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    def module(name,path):
        p=pin(path);s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
    sys.path[:0]=[str(root/'src'),str(root/'scripts')]
    from flint import ctx,acb,acb_mat
    from bhsm.interface.muon_stored_admission_correction import _matrix,_upper
    from bhsm.interface.muon_stored_fiber_canonical_tangent import _split
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    from bhsm.interface.muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
    from bhsm.interface.muon_parent_mean_causal_action import MAXWELL_TO_CAP
    from bhsm.interface.muon_literal_euclidean_wall_action import VOLUME
    ctx.prec=256
    module('bhsm_baton_zoo_exact_acb_packets',RUNTIME+'/bhsm_baton_zoo_exact_acb_packets_imported_runtime.py')
    ex=module('bhsm_exact_action_balls',RUNTIME+'/bhsm_exact_action_balls_imported_runtime.py')
    def exact(z,k):return ex.parse_acb_exact_dyadic(z,k+'_exact')
    def C(v):return v if isinstance(v,acb)else acb(complex(v))
    cm,pm,jm=read(cdir/'result.json'),read(pdir/'result.json'),read(jdir/'result.json')
    if not cm['coefficient_only_early_return_before_action_density']or not cm['no_action_gradient_Hessian_or_field_or_response_solve']:raise ValueError('Actual disclosed coefficient-only export required')
    for folder,meta in((cdir,cm),(pdir,pm),(jdir,jm)):
        if sha256(pin(folder/'executed_producer.py').read_bytes()).hexdigest()!=meta['source_sha256']:raise ValueError('Input producer bytes changed')
    if pm['source_sha256']!='d6b0dbb2e34185011f243f7f571da2f536ebc58c6138fab380f856a2f5db96b9'or jm['source_sha256']!='a761a939cffb6b426ac254f59a8263feeb644ebdfc3843f69b061ee607b4ba3f':raise ValueError('Reviewed native position/Jacobi sources required')
    def checked_archive(folder,meta,name=None):
        name=meta['archive']['name']if name is None else name;p=folder/name
        receipt=meta['archives'][name]if 'archives'in meta else meta['archive']
        if sha256(pin(p).read_bytes()).hexdigest()!=receipt['sha256']:raise ValueError('Frozen actual operand bytes changed')
        return read(p)
    a=checked_archive(cdir,cm,'actual_same_ea02_D4_seven_point_density_R_hR.npz')
    ad=checked_archive(cdir,cm,'actual_same_ea02_D4_seven_point_density_Rdot.npz')
    p,j=checked_archive(pdir,pm),checked_archive(jdir,jm)
    maps=read(pdir/pm['native_epoch_map_archive']['name'])
    if sha256((pdir/pm['native_epoch_map_archive']['name']).read_bytes()).hexdigest()!=pm['native_epoch_map_archive']['sha256']:raise ValueError('Fixed native T/Th/W/Wh bytes changed')
    for z in(ad,p,j):
        if not np.array_equal(z['master368'],a['master368'])or z['coordinate_time'].item()!=a['coordinate_time'].item():raise ValueError('No field/source/right epoch splice')
    if pm['degree']!=4 or jm['new_positions']!=59 or int(a['right_count'])!=7:raise ValueError('Actual complete D4 59x7 problem required')
    if _upper(exact(a,'actual_complete_right')-exact(j,'actual_enlarged_seven_field'))>1e-30 or _upper(exact(ad,'actual_complete_right')-exact(j,'actual_enlarged_seven_field_clock'))>1e-30:raise ValueError('Exact same R and actual Rdot required')
    # Independent two-direction polynomial arithmetic: scalar v,h and all
    # seven independent analytic R,hR axes. No J axis or packed source call.
    Z=acb_mat(1,7)
    class P:
        __slots__=('v','h','r','hr')
        def __init__(self,v=0,h=0,r=None,hr=None):self.v,self.h,self.r,self.hr=C(v),C(h),Z if r is None else r,Z if hr is None else hr
        def __add__(self,o):
            if not isinstance(o,P):o=P(o)
            return P(self.v+o.v,self.h+o.h,self.r+o.r,self.hr+o.hr)
        __radd__=__add__
        def __neg__(self):return P(-self.v,-self.h,-self.r,-self.hr)
        def __sub__(self,o):return self+-o if isinstance(o,P)else self+(-C(o))
        def __rsub__(self,o):return -self+o
        def __mul__(self,o):
            if not isinstance(o,P):
                s=C(o);return P(self.v*s,self.h*s,self.r*s,self.hr*s)
            return P(self.v*o.v,self.h*o.v+self.v*o.h,self.r*o.v+self.v*o.r,
                self.hr*o.v+self.r*o.h+self.h*o.r+self.v*o.hr)
        __rmul__=__mul__
        def __truediv__(self,o):return self*(1/C(o))
    def add(x,y):return[a+b for a,b in zip(x,y)]
    def sub(x,y):return[a-b for a,b in zip(x,y)]
    def scale(s,x):return[s*a for a in x]
    def dot(x,y):return sum((a*b for a,b in zip(x,y)),P())
    factor=C(float(1/np.sqrt(2)))
    def comm(x,y):return[factor*(x[1]*y[2]-x[2]*y[1]),factor*(x[2]*y[0]-x[0]*y[2]),factor*(x[0]*y[1]-x[1]*y[0]),P()]
    def jet_table(z,key):
        v,h,r,hr=[exact(z,key+s)for s in('','_h','_R','_hR')]
        return[[P(v[i,k],h[i,k],acb_mat([[r[i*v.ncols()+k,c]for c in range(7)]]),acb_mat([[hr[i*v.ncols()+k,c]for c in range(7)]]))for k in range(v.ncols())]for i in range(v.nrows())]
    point,metric,wall,raw,weights=[jet_table(a,k)for k in('point','density','wall','raw_child','boundary_weights')]
    pointd,metricd=[jet_table(ad,k)for k in('point','density')]
    extra=np.asarray(maps['extra_coordinates_to_full'],int);n=int(p['enlarged_dynamic_count']);newq=np.asarray(p['new_position_indices'],int)
    def map_matrix(key):
        h,l=maps[key+'_high'],maps[key+'_low']
        return _matrix(h.reshape(-1,len(extra)))+_matrix(l.reshape(-1,len(extra)))
    T,Th,W,Wh=[map_matrix(k)for k in('extra_point_lift','extra_point_lift_total_clock','extra_wall_lift','extra_wall_lift_total_clock')]
    iq=[int(np.flatnonzero(extra==252+q).item())for q in newq];iv=[int(np.flatnonzero(extra==252+n+q).item())for q in newq]
    Q,V,Vh,Vd=[acb_mat(59,7)for _ in range(4)];qprimal,vprimal,vclock=[acb_mat(59,1)for _ in range(3)]
    def fields(row,k):return[row[20*k+4*f:20*k+4*f+4]for f in range(5)]
    def invariants(row,g):
        A,At,Ar=(fields(row,k)for k in range(3));e,r,d,k,beta=g
        X=add(sub(At[1],Ar[0]),comm(A[0],A[1]))
        R=[add(Ar[f],comm(A[1],A[f]))for f in range(2,5)]
        Y=[sub(add(At[f],comm(A[0],A[f])),scale(beta,s))for f,s in zip(range(2,5),R)]
        B=[add(scale(C(2),A[i+2]),comm(A[j+2],A[k+2]))for i,j,k in((0,1,2),(1,2,0),(2,0,1))]
        mom=[scale(C(0),X),scale(k,X)]+[scale(e,y)for y in Y]
        return A,X,R,Y,B,mom
    print(json.dumps(dict(stage='independent_literal_59_by_7_bulk',nodes=len(point))),flush=True)
    for ir in range(len(point)):
        e,r,d,k,beta=metric[ir];A,X,R,Y,B,mom=invariants(point[ir],metric[ir]);_,_,_,_,_,momd=invariants(pointd[ir],metricd[ir])
        weight=C(float(MAXWELL_TO_CAP)*float(a['radial_quadrature'][ir]))
        for row,(jq,jv)in enumerate(zip(iq,iv)):
            da,dat,dar=([[P(T[60*ir+20*b+4*f+c,jq])for c in range(4)]for f in range(5)]for b in range(3))
            dx=add(sub(dat[1],dar[0]),add(comm(da[0],A[1]),comm(A[0],da[1])))
            dr=[add(dar[f],add(comm(da[1],A[f]),comm(A[1],da[f])))for f in range(2,5)]
            dy=[sub(add(dat[f],add(comm(da[0],A[f]),comm(A[0],da[f]))),scale(beta,s))for f,s in zip(range(2,5),dr)]
            db=[add(scale(C(2),da[i+2]),add(comm(da[j+2],A[l+2]),comm(A[j+2],da[l+2])))for i,j,l in((0,1,2),(1,2,0),(2,0,1))]
            first=weight*(k*dot(X,dx)+e*sum((dot(u,v)for u,v in zip(Y,dy)),P())-r*sum((dot(u,v)for u,v in zip(R,dr)),P())-d*sum((dot(u,v)for u,v in zip(B,db)),P()))
            qprimal[row,0]+=first.v
            for c in range(7):Q[row,c]+=first.r[0,c]
            if any(T[60*ir+s,jv]!=0 for s in list(range(20))+list(range(40,60))):raise ValueError('Velocity weak test has an unaccounted field/radial placement')
            velocity=P();velocityd=P()
            for f in range(5):
                b=[P(T[60*ir+20+4*f+c,jv],Th[60*ir+20+4*f+c,jv])for c in range(4)]
                velocity+=weight*dot(mom[f],b);velocityd+=weight*dot(momd[f],b)
            vprimal[row,0]+=velocity.v;vclock[row,0]+=velocity.h
            for c in range(7):V[row,c]+=velocity.r[0,c];Vh[row,c]+=velocity.hr[0,c];Vd[row,c]+=velocityd.r[0,c]
    gens=higgs_u2_real_representation()['real_generators'];H=raw[0][260:264];wS=weights[0][1]
    def O(conn,h):return[sum((conn[k]*sum((C(gens[k][i,j])*h[j]for j in range(4)),P())for k in range(4)),P())for i in range(4)]
    print(json.dumps(dict(stage='independent_literal_59_by_7_scalar_wall')),flush=True)
    for row,(jq,jv)in enumerate(zip(iq,iv)):
        if any(W[s,jv]!=0 for s in range(20))or any(W[s,jq]!=0 for s in range(4)):raise ValueError('Unaccounted scalar-wall velocity/temporal weak-test placement')
        first=-C(2)*wS*sum((dot(O(wall[0][4*f:4*f+4],H),O([P(W[4*f+c,jq])for c in range(4)],H))for f in range(2,5)),P())/C(VOLUME)
        qprimal[row,0]+=first.v
        for c in range(7):Q[row,c]+=first.r[0,c]
    K=Q-Vh-Vd
    reference={k:exact(j,k)for k in('actual_new_position_H_R','actual_new_velocity_h_H_R','actual_new_velocity_H_Rdot','actual_new_position_Kz_trial')}
    defects={k:_upper(a-reference[k])for k,a in(('actual_new_position_H_R',Q),('actual_new_velocity_h_H_R',Vh),('actual_new_velocity_H_Rdot',Vd),('actual_new_position_Kz_trial',K))}
    primal_defects={k:_upper(a-exact(p,k))for k,a in(('new_position_Lq',qprimal),('new_position_Lv',vprimal),('new_position_total_clock_Lv',vclock),('new_position_primal_Euler_r',qprimal-vclock))}
    affine=acb_mat(K);primal=exact(p,'new_position_primal_Euler_r')
    for i in range(59):affine[i,0]+=primal[i,0]
    combined=acb_mat(59,4)
    for i in range(59):
        combined[i,0]=affine[i,0]
        for c in range(3):combined[i,1+c]=affine[i,1+c]+affine[i,4+c]
    values=dict(independent_literal_position_H_R=Q,independent_literal_velocity_H_R=V,
        independent_literal_velocity_h_H_R=Vh,independent_literal_velocity_H_Rdot=Vd,independent_literal_position_Kz_trial=K,
        independent_literal_affine_seven_position_rows=affine,independent_literal_combined_four_position_rows=combined,
        independent_literal_primal_Lq=qprimal,independent_literal_primal_Lv=vprimal,independent_literal_primal_d_t_Lv=vclock)
    arrays=dict(coordinate_time=a['coordinate_time'],master368=a['master368'],new_position_indices=newq)
    for key,m in values.items():arrays[key+'_high'],arrays[key+'_low']=_split(m);arrays.update(ex.export_acb_exact_dyadic(m,key+'_exact'))
    path=out/'independent_literal_full59x7_Jacobi_and_source_operands.npz';_compressed_npz(path,arrays)
    pin(Path(__file__))
    passed=max(list(defects.values())+list(primal_defects.values()))<=2e-10
    result=dict(classification='INDEPENDENT_LITERAL_ACTUAL_FULL59_BY7_POSITION_JACOBI_CONTROL',source_sha256=sha256(producer).hexdigest(),input_and_source_hashes=dict(sorted(pins.items())),
        archive=dict(name=path.name,sha256=sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size),arithmetic_precision_bits=256,
        independent_all59x7_Jacobi_control_pass=passed,individual_literal_vs_packed_derivative_defect_upper=defects,
        independent_primal_reproduction_upper=primal_defects,actual_position_Kz_upper=_upper(K),actual_affine_seven_position_rows_upper=_upper(affine),actual_combined_four_position_rows_upper=_upper(combined),
        no_packed_action_Hessian_or_gradient_called=True,actual_point_density_R_hR_Rdot_used=True,
        no_J_axis_AD_used=True,literal_weak_first_variation_and_canonical_momentum_product_rule=True,
        all59_positions_and_seven_source_retarded_homogeneous_columns_retained=True,
        actual_fixed_chart_T_Th_W_Wh_counted_once=True,scalar_wall_H_and_wS_contacts_retained_once=True,
        full_Hessian_or_mean_or_response_solve=False,original_history_and_source_unchanged=True,
        physical_full_outgoing_derivative_pass=False,physical_radial_solution_convergence=False,
        physical_Maxwell226_after_pass=False,physical_normalized_two_spin_state=False,physical_muon_magnetic_moment=None,original_coupled_corrections=0)
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(passed=passed,derivative_defects=defects,primal_defects=primal_defects)),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',type=Path,default=ROOT)
    for key in('coefficient-folder','position-folder','jacobi-folder','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();run(a.repository,a.coefficient_folder,a.position_folder,a.jacobi_folder,a.output)
