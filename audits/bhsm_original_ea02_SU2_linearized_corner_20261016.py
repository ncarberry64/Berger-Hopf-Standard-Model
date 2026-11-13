"""Actual SU2 deltaV(A,H) corner on all27x7 retained ea02 source columns.

Literal momentum/gauge-image functionals consume exact coefficient jets.
The Gauss H_R comparison is independently evaluated. Mixed-clock rows are
separately labeled polynomial Noether-identity controls, not a new Hessian.
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
RADIAL='artifacts/muon_baton_zoo_radial_convergence_20261014'


def run(repository,coefficient_folder,SU2_folder,central_seven_folder,gauss_folder,output):
    root,cdir,sdir,ldir,gdir,out=map(lambda p:Path(p).resolve(),(repository,coefficient_folder,SU2_folder,central_seven_folder,gauss_folder,output))
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
    def meta(folder,expected):
        m=read(folder/'result.json')
        if m['source_sha256']!=expected or sha256(pin(folder/'executed_producer.py').read_bytes()).hexdigest()!=expected:raise ValueError('Exact frozen reviewed input source required')
        return m
    def archive(folder,meta,name=None):
        name=meta['archive']['name']if name is None else name;p=folder/name
        receipt=meta['archives'][name]if 'archives'in meta else meta['archive']
        if sha256(pin(p).read_bytes()).hexdigest()!=receipt['sha256']:raise ValueError('Actual source operand bytes changed')
        return read(p)
    cm=meta(cdir,'c744590f986e47c946f128641b071808f527d230ba60fc2fa70adf87d351c851')
    sm=meta(sdir,'792af62bc8bc9257beeafd57894644b22272a820edfed3ff67e2ccdf33c129b2')
    lm=meta(ldir,'a4127316f999d03a67f8307d12258d4aaed809f292d8234d05d494b85381d425')
    gm=meta(gdir,'519371278ad0884047147d7b97364d2af7f5f7ae145d15cda1549b56cce35902')
    a=archive(cdir,cm,'actual_same_ea02_D4_seven_point_density_R_hR.npz')
    ad=archive(cdir,cm,'actual_same_ea02_D4_seven_point_density_Rdot.npz')
    s,l,g=archive(sdir,sm),archive(ldir,lm),archive(gdir,gm)
    for z in(ad,s,l,g):
        if not np.array_equal(z['master368'],a['master368'])or z['coordinate_time'].item()!=a['coordinate_time'].item():raise ValueError('No field/source/clock/branch splice')
    if sm['degree']!=4 or gm['Gauss_rows']!=60:raise ValueError('Full D4 SU2/gauge carrier required')
    R=exact(a,'actual_complete_right')
    if _upper(R-exact(l,'actual_retained_seven_fields'))>1e-30 or _upper(R-exact(g,'actual_same_seven_field'))>1e-30:raise ValueError('Identical complete seven R in every application required')
    prof=read(RADIAL+'/literal_MP_radial_complex192_run_2/degree_04_literal_MP_radial_profiles_and_derivative_complex.npz')
    ph,phr,wp=[_matrix(prof[k+'_high'])+_matrix(prof[k+'_low'])for k in('values','first','wall_values')]
    # Independent two-direction polynomial arithmetic, without any J axis.
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
                z=C(o);return P(self.v*z,self.h*z,self.r*z,self.hr*z)
            return P(self.v*o.v,self.h*o.v+self.v*o.h,self.r*o.v+self.v*o.r,self.hr*o.v+self.r*o.h+self.h*o.r+self.v*o.hr)
        __rmul__=__mul__
        def __truediv__(self,o):return self*(1/C(o))
    def add(x,y):return[a+b for a,b in zip(x,y)]
    def sub(x,y):return[a-b for a,b in zip(x,y)]
    def scale(z,x):return[z*a for a in x]
    def dot(x,y):return sum((a*b for a,b in zip(x,y)),P())
    factor=C(float(1/np.sqrt(2)))
    def comm(x,y):return[factor*(x[1]*y[2]-x[2]*y[1]),factor*(x[2]*y[0]-x[0]*y[2]),factor*(x[0]*y[1]-x[1]*y[0]),P()]
    def table(z,key):
        v,h,r,hr=[exact(z,key+suffix)for suffix in('','_h','_R','_hR')]
        return[[P(v[i,k],h[i,k],acb_mat([[r[i*v.ncols()+k,j]for j in range(7)]]),acb_mat([[hr[i*v.ncols()+k,j]for j in range(7)]]))for k in range(v.ncols())]for i in range(v.nrows())]
    gen=higgs_u2_real_representation()['real_generators']
    def O(conn,h):return[sum((conn[k]*sum((C(gen[k][i,j])*h[j]for j in range(4)),P())for k in range(4)),P())for i in range(4)]
    def fields(row,k):return[row[20*k+4*f:20*k+4*f+4]for f in range(5)]
    def functional(z):
        point,metric,wall,raw,weights=[table(z,k)for k in('point','density','wall','raw_child','boundary_weights')]
        Q=[P()for _ in range(27)];G=[P()for _ in range(27)];contactA=acb_mat(27,7);contactH=acb_mat(27,7)
        for ir in range(len(point)):
            A,At,Ar=(fields(point[ir],k)for k in range(3));e,_,_,k,beta=metric[ir]
            X=add(sub(At[1],Ar[0]),comm(A[0],A[1]));Rs=[add(Ar[f],comm(A[1],A[f]))for f in range(2,5)]
            Y=[sub(add(At[f],comm(A[0],A[f])),scale(beta,r))for f,r in zip(range(2,5),Rs)]
            momentum=[scale(k,X)]+[scale(e,y)for y in Y]
            weight=C(float(MAXWELL_TO_CAP)*float(z['radial_quadrature'][ir]))
            for j,(p,b)in enumerate((p,b)for p in range(9)for b in range(3)):
                parameter=[P(C(int(c==b))*ph[ir,p])for c in range(4)];drparameter=[P(C(int(c==b))*phr[ir,p])for c in range(4)]
                K=[add(drparameter,comm(A[1],parameter))]+[comm(A[f],parameter)for f in range(2,5)]
                charge=weight*sum((dot(pi,ki)for pi,ki in zip(momentum,K)),P());Q[j]+=charge
                dx=add(scale(C(-1),drparameter),comm(parameter,A[1]));dy=[comm(parameter,A[f])for f in range(2,5)]
                G[j]+=weight*(k*dot(X,dx)+e*sum((dot(y,d)for y,d in zip(Y,dy)),P()))
                for f in range(4):
                    for c in range(4):
                        for r in range(7):contactA[j,r]+=weight*momentum[f][c].v*K[f][c].r[0,r]
        H,Hdot=raw[0][260:264],raw[0][264:268];DtH=add(Hdot,O(wall[0][:4],H))
        PiH=scale(C(2)/C(VOLUME),[weights[0][0]*x for x in DtH])
        for j,(p,b)in enumerate((p,b)for p in range(9)for b in range(3)):
            parameter=[P(C(int(c==b))*wp[0,p])for c in range(4)];VH=scale(C(-1),O(parameter,H))
            Q[j]+=dot(PiH,VH);G[j]+=dot(PiH,O(parameter,H))
            for c in range(4):
                for r in range(7):contactH[j,r]+=PiH[c].v*VH[c].r[0,r]
        return Q,G,contactA,contactH
    print(json.dumps(dict(stage='actual_SU2_full27x7_deltaV_corner')),flush=True)
    Q,G,contactA,contactH=functional(a);Qd,Gd,_,_=functional(ad)
    def scalar_slot(vec,key):return acb_mat([[getattr(x,key)]for x in vec])
    def right_slot(vec,key):return acb_mat([[getattr(x,key)[0,j]for j in range(7)]for x in vec])
    q,qh,dq,qhr=[scalar_slot(Q,'v'),scalar_slot(Q,'h'),right_slot(Q,'r'),right_slot(Q,'hr')]
    gg,ggh,dg,gghr=[scalar_slot(G,'v'),scalar_slot(G,'h'),right_slot(G,'r'),right_slot(G,'hr')]
    dqt=qhr+right_slot(Qd,'r');dgt=gghr+right_slot(Gd,'r')
    V,Cg=exact(s,'SU2_gauge_position_map'),exact(s,'SU2_Gauss_map')
    held=V.transpose()*exact(l,'actual_full_momentum_variation');contacts=contactA+contactH
    independently_projected=Cg.transpose()*exact(g,'actual_native_Gauss_Kz_trial')
    independent_rows=dq+independently_projected
    values=dict(actual_full_seven_fields=R,actual_SU2_initial_charge=q,actual_SU2_initial_charge_clock=qh,
        actual_SU2_initial_charge_variation=dq,actual_SU2_initial_charge_variation_total_clock=dqt,
        actual_SU2_future_arm_outward_flux_variation=-dq,actual_SU2_fixed_chart_V_deltaPi=held,
        actual_SU2_unprojected_deltaK_A_corner_contact=contactA,actual_SU2_deltaV_H_corner_contact=contactH,
        actual_SU2_full_deltaV_A_H_corner_contact=contacts,
        full_charge_variation_minus_fixed_chart_and_deltaV=dq-held-contacts,
        actual_independent_native_Gauss_H_R_projection=independently_projected,
        actual_independent_linearized_SU2_primary_rows=independent_rows,
        literal_temporal_Gauss_parameter_variation=dg,literal_Gauss_variation_minus_independent_projection=dg-independently_projected,
        literal_temporal_Gauss_parameter_variation_total_clock=dgt,
        clock_linearized_primary_polynomial_identity_control=dqt+dgt,
        literal_primal_charge_minus_saved_SU2=q-exact(s,'actual_SU2_initial_corner_charge'),
        literal_primal_charge_clock_minus_saved_SU2=qh-exact(s,'actual_SU2_initial_corner_charge_total_clock'))
    required=acb_mat(27,7);r=exact(s,'actual_SU2_Gauss_charge_projection');affineq=acb_mat(dq);affineg=acb_mat(independently_projected)
    for i in range(27):required[i,0]=r[i,0];affineq[i,0]+=q[i,0];affineg[i,0]+=r[i,0]
    values.update(required_affine_SU2_charge_variation=required,actual_SU2_charge_variation_minus_affine_required=dq-required,
        actual_affine_seven_SU2_charge=affineq,actual_affine_seven_SU2_Gauss_projection=affineg,
        actual_affine_seven_SU2_primary_rows=affineq+affineg)
    def four(m):
        z=acb_mat(m.nrows(),4)
        for i in range(m.nrows()):
            z[i,0]=m[i,0]
            for j in range(3):z[i,1+j]=m[i,1+j]+m[i,4+j]
        return z
    values['actual_combined_four_affine_SU2_Gauss_projection']=four(affineg)
    arrays=dict(master368=a['master368'],coordinate_time=a['coordinate_time'],profile_internal_labels=s['profile_internal_labels'])
    for key,m in values.items():arrays[key+'_high'],arrays[key+'_low']=_split(m);arrays.update(ex.export_acb_exact_dyadic(m,key+'_exact'))
    path=out/'actual_SU2_all27x7_deltaV_corner_and_independent_Gauss.npz';_compressed_npz(path,arrays)
    pin(Path(__file__))
    result=dict(classification='ACTUAL_SAME_EA02_FULL27_BY7_SU2_DELTA_V_SOURCE_CORNER',source_sha256=sha256(producer).hexdigest(),input_and_source_hashes=dict(sorted(pins.items())),
        archive=dict(name=path.name,sha256=sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size),arithmetic_precision_bits=256,
        independent_all27x7_linearized_primary_upper=_upper(independent_rows),fixed_chart_plus_full_deltaV_decomposition_upper=_upper(dq-held-contacts),
        literal_Gauss_variation_vs_independent_all60_projection_upper=_upper(dg-independently_projected),
        literal_primal_charge_vs_saved_SU2_upper=_upper(q-exact(s,'actual_SU2_initial_corner_charge')),
        literal_primal_charge_clock_vs_saved_SU2_upper=_upper(qh-exact(s,'actual_SU2_initial_corner_charge_total_clock')),
        actual_deltaK_A_contact_upper=_upper(contactA),actual_deltaV_H_contact_upper=_upper(contactH),
        actual_SU2_charge_variation_upper=_upper(dq),actual_SU2_charge_variation_total_clock_upper=_upper(dqt),
        clock_linearized_primary_polynomial_identity_upper=_upper(dqt+dgt),clock_control_independent_mixed_Gauss_Hessian_evaluated=False,
        actual_affine_seven_SU2_constraint_projection_upper=_upper(affineg),actual_combined_four_SU2_constraint_projection_upper=_upper(four(affineg)),
        deltaV_A_contact_unprojected_not_admitted_state_coordinate=True,deltaV_H_and_metric_density_contacts_retained_once=True,
        all_independent_native_Gauss_H_R_rows_consumed=True,actual_hR_and_Rdot_include_sourceDot=True,
        original_seven_to_four_combination_retained=True,no_action_Hessian_history_or_source_solve_replayed=True,
        full_SU2_retarded_reset_domain_or_exterior_evaluated=False,physical_full_outgoing_derivative_pass=False,
        physical_radial_solution_convergence=False,physical_Maxwell226_after_pass=False,
        physical_normalized_two_spin_state=False,physical_muon_magnetic_moment=None,original_coupled_corrections=0)
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({k:result[k]for k in('independent_all27x7_linearized_primary_upper','fixed_chart_plus_full_deltaV_decomposition_upper','actual_deltaK_A_contact_upper','actual_affine_seven_SU2_constraint_projection_upper','clock_linearized_primary_polynomial_identity_upper')}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',type=Path,default=ROOT)
    for key in('coefficient-folder','SU2-folder','central-seven-folder','gauss-folder','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();run(a.repository,a.coefficient_folder,a.SU2_folder,a.central_seven_folder,a.gauss_folder,a.output)
