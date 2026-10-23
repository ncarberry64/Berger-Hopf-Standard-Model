"""Same-history MP Yang--Mills values on the full1120 one-form test space.

The existing positive-reference curvature square AND off-shell contact are
retained. Four angular operator coefficients are contracted before the Haar
lift; this is a finite EW4 constituent, not the microscopic graded operator.
"""
from __future__ import annotations
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
import mpmath as mp

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'audits')]
import bhsm_changing_lorenz_mp_coefficient_values_20261016 as owner
from bhsm.interface.muon_parent_positive_coupled_temporal import one_form_point_row
from bhsm.interface.muon_matched_mechanical_source import epsilon

OWNER_SHA='1b0a9713749feb062fecdb664598a7a5b3528bd72ec5aa18176ae88eb5b88eff'
N=224                         # four angular coefficients x14 blocks x4 adjoints
EPS=[tuple(map(int,p))for p in np.argwhere(epsilon())]


def lambda_jet(raw,rho,c,rate=None):
    """Actual geometric lambda, its material time and rho derivatives.

    This is not the separately anchored response f/probability. The common
    owned chart has qdot=v,sdot=raw99; no extra radial advection is inserted.
    """
    g=owner.geometry(raw,rho,c);chi=g['chi'];q=raw[:37]
    rate=np.r_[raw[37:74],owner.tensor.zeros((61,)),raw[99],mp.mpf(0)] if rate is None else rate
    if any(rate[k]!=raw[37+k]for k in range(37))or rate[98]!=raw[99]:
        raise ValueError('Same owned qdot=v and sdot=raw99 source chart required')
    window=mp.sin(2*chi)**2
    series=mp.fsum(q[25+j]*mp.cos(4*j*chi)for j in range(12))
    db=4*mp.sin(2*chi)*mp.cos(2*chi)*series-window*mp.fsum(4*j*q[25+j]*mp.sin(4*j*chi)for j in range(12))
    difference=2*db-mp.tan(chi)-1/mp.tan(chi)
    partial=2*window*mp.fsum(rate[25+j]*mp.cos(4*j*chi)for j in range(12))
    factor=2*g['lam']*(1-g['lam'])
    return g['lam'],factor*(partial+rho*g['delta_dot']/c['WALL']*difference),factor*g['wall']/c['WALL']*difference


def basis_with_derivative(rho,reference,c):
    b,radial=owner.radial_basis(rho,reference,c)
    x=rho/c['WALL'];a=c['alpha'];beta=c['jacobi_beta']
    reg=x**a;regd=a*x**(a-1)/c['WALL']
    P=((2-beta)+(beta+4)*(2*x-1))/2
    D1=c['normalization'][1]*((regd*(1-x)-reg/c['WALL'])*P+reg*(1-x)*(beta+4)/c['WALL'])
    l=[lambda_jet(owner.ma(np.r_[raw,0.,0.]),rho,c)[2]for raw in reference['states']]
    enrich=(l[0]-l[1]-radial[0,1]*owner.m(reference['projection'][0])-D1*owner.m(reference['projection'][1])-regd*owner.m(reference['wall']))/owner.m(reference['norm'])
    return b,np.array([radial[0,1],D1,enrich,regd],dtype=object),radial


def coefficient(raw,rate,t,rho,side,parent_reference,reference,c,chart,basis=None):
    b,br,radial=basis_with_derivative(rho,reference,c)if basis is None else basis
    v=owner.coefficient(raw,t,rho,side,parent_reference,reference,c,chart,basis_data=(b,radial))
    jet=lambda_jet(raw,rho,c,rate)
    if side=='outgoing':
        parent,refs=parent_reference
        j=[lambda_jet(owner.profile_raw(a,t),rho,c)for a in(parent,*refs)]
        jet=tuple(j[0][i]-j[1][i]+j[2][i]for i in range(3))
    gauge=raw[100:180].reshape(4,5,4);gaugerate=rate[100:180].reshape(4,5,4)
    At=sum((b[j]*gaugerate[j]for j in range(4)),owner.tensor.zeros((5,4)))
    Ar=sum((br[j]*gauge[j]for j in range(4)),owner.tensor.zeros((5,4)))
    At[2:]+=c['M']*jet[1];Ar[2:]+=c['M']*jet[2]
    mu,gt,gr,gs,beta,R=v['metric'];g=v['geometry'];Ceff=g['C']*g['wall']/c['WALL']
    density=np.array([gt/R**2,gr/R**2,gs/R**2,gt/Ceff**2,beta],dtype=object)
    return dict(v,A_time=At,A_radial=Ar,basis_radial=br,densities=density,profile_jet=jet)


def curvatures(A,At,Ar,c):
    ad=lambda a:owner.ad_native(a,c)
    X=At[1]-Ar[0]+ad(A[0])@A[1]
    T=np.array([At[2+i]+ad(A[0])@A[2+i]for i in range(3)],dtype=object)
    R=np.array([Ar[2+i]+ad(A[1])@A[2+i]for i in range(3)],dtype=object)
    B=2*A[2:].copy()
    for i,j,k in EPS:B[i]+=mp.mpf('.5')*int(epsilon()[i,j,k])*(ad(A[2+j])@A[2+k])
    return np.vstack((X,T,R,B))


def addblock(rows,rowblock,h,p,block):
    for a in range(4):
        row=rows[4*rowblock+a]
        for b in range(4):
            v=block[a,b]
            if v:
                k=p*56+h*4+b;row[k]=row.get(k,mp.mpf(0))+v


def maps(A,F,temporal,radial,tent,tent_rate,c):
    """Original unweighted curvature/value maps, encoded by I,E1,E2,E3."""
    I=owner.tensor.identity(4);ad=[owner.ad_native(a,c)for a in A]
    V=[{}for _ in range(20)];C=[{}for _ in range(40)]
    for i in range(2):
        u,ur=radial[i,:2];v,dv,vr=tent*u,tent_rate*u,tent*ur
        for nu in range(5):
            h=5*i+nu;addblock(V,nu,h,0,v*I)
            if nu==1:addblock(C,0,h,0,dv*I+v*ad[0])
            if nu==0:addblock(C,0,h,0,-vr*I-v*ad[1])
            for a in range(3):
                if nu==2+a:
                    addblock(C,1+a,h,0,dv*I+v*ad[0]);addblock(C,4+a,h,0,vr*I+v*ad[1]);addblock(C,7+a,h,0,2*v*I)
                if nu==0:
                    addblock(C,1+a,h,0,-v*ad[2+a]);addblock(C,1+a,h,1+a,-v*I)
                if nu==1:
                    addblock(C,4+a,h,0,-v*ad[2+a]);addblock(C,4+a,h,1+a,-v*I)
            for a,j,k in EPS:
                if nu==2+k:
                    e=int(epsilon()[a,j,k]);addblock(C,7+a,h,0,e*v*ad[2+j]);addblock(C,7+a,h,1+j,e*v*I)
    for p in range(2):
        tp,dt=temporal[p,:2]
        for j in range(2):
            h=10+2*p+j;u,ur=radial[j,:2]
            for nu in range(5):
                block=tp*u*ad[nu]
                if nu==0:block=block+dt*u*I
                if nu==1:block=block+tp*ur*I
                addblock(V,nu,h,0,block)
                if nu>=2:addblock(V,nu,h,nu-1,tp*u*I)
            for f in range(10):addblock(C,f,h,0,tp*u*owner.ad_native(F[f],c))
    return V,C


def contact(F,density,c):
    e,r,d,k,beta=density;C=owner.tensor.zeros((20,20));ad=lambda a:-owner.ad_native(a,c)
    def block(mu,nu,v):C[4*mu:4*mu+4,4*nu:4*nu+4]+=v
    block(0,1,k*ad(F[0]))
    for i in range(3):
        electric=ad(F[1+i]-beta*F[4+i]);block(0,2+i,e*electric);block(1,2+i,-e*beta*electric+r*ad(F[4+i]))
    C=C+C.T
    for i,j,h in EPS:block(2+j,2+h,d*int(epsilon()[i,j,h])*ad(F[7+i]))
    if any(C[i,j]!=C[j,i]for i in range(20)for j in range(20)):
        raise ArithmeticError('Literal contact lost exact algebraic symmetry')
    return C


def combine(a,b,scale):
    row=dict(a)
    for j,v in b.items():row[j]=row.get(j,mp.mpf(0))+scale*v
    return {j:v for j,v in row.items()if v}


def outer_add(total,row,weight):
    values=sorted((i,v)for i,v in row.items()if v)
    for n,(i,a)in enumerate(values):
        wa=weight*a
        for j,b in values[n:]:total[i*N+j]+=wa*b


def cross_add(total,left,right,weight):
    for i,a in left.items():
        if a:
            wa=weight*a
            for j,b in right.items():
                if b:
                    k=min(i,j)*N+max(i,j);total[k]+=wa*b*(2 if i==j else 1)


def accumulate(square,contacts,V,C,F,density,weight,c):
    e,r,d,k,beta=density
    for a in range(4):outer_add(square,C[a],weight*k)
    for i in range(3):
        for a in range(4):
            outer_add(square,combine(C[4+4*i+a],C[16+4*i+a],-beta),weight*e)
            outer_add(square,C[16+4*i+a],weight*r)
            outer_add(square,C[28+4*i+a],weight*d)
    Q=contact(F,density,c)
    for i in range(20):
        for j in range(i+1,20):
            if Q[i,j]:cross_add(contacts,V[i],V[j],weight*Q[i,j])


def products(E):
    H=[owner.tensor.identity(20),*owner.ma(E)];out={}
    for p in range(4):
        for q in range(p,4):
            z=H[p].T@H[q];out[p,q]=[(i,j,z[i,j])for i in range(20)for j in range(20)if z[i,j]]
            out[q,p]=[(j,i,a)for i,j,a in out[p,q]]
    return out


def lift(upper,angular):
    result=owner.tensor.zeros((1120,1120))
    for idx in np.flatnonzero(upper):
        i,j=divmod(int(idx),N)
        if i>j:raise ArithmeticError('Only exact upper coefficient storage is admitted')
        p,a=divmod(i,56);q,b=divmod(j,56);h,ic=divmod(a,4);g,jc=divmod(b,4);v=upper[idx]
        ri=h*80+ic*20;ci=g*80+jc*20
        for x,y,s in angular[p,q]:result[ri+x,ci+y]+=v*s
        if i!=j:
            for x,y,s in angular[q,p]:result[ci+x,ri+y]+=v*s
    return result


def entry(upper,angular,i,j):
    h,within=divmod(i,80);a,x=divmod(within,20);g,within=divmod(j,80);b,y=divmod(within,20)
    total=mp.mpf(0)
    for p in range(4):
        for q in range(4):
            u=p*56+h*4+a;v=q*56+g*4+b
            coef=upper[min(u,v)*N+max(u,v)]
            if coef:
                total+=coef*next((w for xx,yy,w in angular[p,q]if xx==x and yy==y),mp.mpf(0))
    return total


def exact_tuples(a):
    return np.array([f'{s}:{man:x}:{ex}:{bc}'for s,man,ex,bc in(x._mpf_ for x in a.flat)]).reshape(a.shape)


def gauge_value(phase,t,rho,reference,c):
    """Independent value path for literal derivatives; no new jet routine."""
    raw=owner.raw_at(phase,t);b=owner.radial_basis(rho,reference,c)[0]
    value=sum((b[j]*raw[100:180].reshape(4,5,4)[j]for j in range(4)),owner.tensor.zeros((5,4)))
    if 'parent_reference'in phase:
        parent,refs=phase['parent_reference'];a=[owner.geometry(owner.profile_raw(z,t),rho,c)['lam']for z in(parent,*refs)]
        lam=a[0]-a[1]+a[2]
    else:lam=owner.geometry(raw,rho,c)['lam']
    value[2:]+=c['M']*(lam-1)
    return value


def derivative_controls(phase,side,reference,c,frozen):
    t=owner.m(frozen['temporal_u'][0])+min(owner.m(phase['span']),mp.mpf(0));raw=owner.raw_at(phase,t);rate=owner.ma(phase['rate']);records=[]
    for ri in(0,len(frozen['radial_coordinate_weights'])//2,len(frozen['radial_coordinate_weights'])-1):
        rho=owner.m(frozen['radial_points'][ri]);g=owner.geometry(raw,rho,c);ch=owner.response_chart(g['delta'],c,96,'mp',mp.mp.dps)
        v=coefficient(raw,rate,t,rho,side,phase.get('parent_reference'),reference,c,ch)
        dt=np.array([[mp.diff(lambda tt:gauge_value(phase,tt,rho,reference,c)[i,j],t)for j in range(4)]for i in range(5)],dtype=object)
        dr=np.array([[mp.diff(lambda rr:gauge_value(phase,t,rr,reference,c)[i,j],rho)for j in range(4)]for i in range(5)],dtype=object)
        bd=np.array([mp.diff(lambda rr:owner.radial_basis(rr,reference,c)[0][j],rho)for j in range(4)],dtype=object)
        records.append(dict(radial_index=ri,coordinate_time=mp.nstr(t,65),rho=mp.nstr(rho,65),
            independent_literal_MP_time_derivative=owner.mp_compare(dt,v['A_time']),
            independent_literal_MP_radial_derivative=owner.mp_compare(dr,v['A_radial']),
            independent_literal_MP_fixed_basis_derivative=owner.mp_compare(bd,v['basis_radial']),
            mechanical_time_profile_nonzero=mp.nstr(abs(v['profile_jet'][1]),30),
            mechanical_radial_profile_nonzero=mp.nstr(abs(v['profile_jet'][2]),30)))
    return records


def literal_column(index,A,F,E,radial,temporal,tent,tent_rate,c):
    """A full5x4x20 column and its10x4x20 curvature, independently."""
    v=owner.tensor.zeros((5,4,20));cur=owner.tensor.zeros((10,4,20))
    if index>=800:
        g,k=divmod(index-800,80);p,j=divmod(g,2);a,h=divmod(k,20);tp=temporal[p,0];u=radial[j,0]
        v=owner.native_ghost(index-800,A,E,temporal,radial,c).reshape(5,4,20)
        for f in range(10):cur[f,:,h]=tp*u*owner.ad_native(F[f],c)[:,a]
        return v,cur
    p,k=divmod(index,400);nu,k=divmod(k,80);a,h=divmod(k,20);u,ur=radial[p,:2]
    vt,vr=owner.tensor.zeros(v.shape),owner.tensor.zeros(v.shape);ev=owner.tensor.zeros((3,5,4,20))
    v[nu,a,h]=tent*u;vt[nu,a,h]=tent_rate*u;vr[nu,a,h]=tent*ur
    for j in range(3):ev[j,nu,a]=tent*u*owner.ma(E[j,:,h])
    ad=[owner.ad_native(z,c)for z in A]
    cur[0]=vt[1]-vr[0]+ad[0]@v[1]-ad[1]@v[0]
    for j in range(3):
        cur[1+j]=vt[2+j]-ev[j,0]+ad[0]@v[2+j]-ad[2+j]@v[0]
        cur[4+j]=vr[2+j]-ev[j,1]+ad[1]@v[2+j]-ad[2+j]@v[1]
        cur[7+j]=2*v[2+j]
    for i,j,k in EPS:cur[7+i]+=int(epsilon()[i,j,k])*(ev[j,2+k]+ad[2+j]@v[2+k])
    return v,cur


def bracket_pair(a,b,c):
    out=owner.tensor.zeros((4,))
    for i,j,k in EPS:out[i]+=int(epsilon()[i,j,k])*mp.fsum(a[j,h]*b[k,h]for h in range(20))/c['sqrt2']
    return out


def literal_pair(left,right,F,density,c):
    """Direct Haar curvature and mixed-bracket action, no tensor/contact map."""
    v,a=left;w,b=right;e,r,d,k,beta=density
    dot=lambda x,y:mp.fsum(xx*yy for xx,yy in zip(x.flat,y.flat))
    square=k*dot(a[0],b[0])+e*dot(a[1:4]-beta*a[4:7],b[1:4]-beta*b[4:7])+r*dot(a[4:7],b[4:7])+d*dot(a[7:],b[7:])
    X=bracket_pair(v[0],w[1],c)+bracket_pair(w[0],v[1],c)
    T=np.array([bracket_pair(v[0],w[2+j],c)+bracket_pair(w[0],v[2+j],c)for j in range(3)],dtype=object)
    R=np.array([bracket_pair(v[1],w[2+j],c)+bracket_pair(w[1],v[2+j],c)for j in range(3)],dtype=object)
    B=owner.tensor.zeros((3,4))
    for i,j,h in EPS:B[i]+=int(epsilon()[i,j,h])*bracket_pair(v[2+j],w[2+h],c)
    contact=k*dot(F[0],X)+e*dot(F[1:4]-beta*F[4:7],T-beta*R)+r*dot(F[4:7],R)+d*dot(F[7:],B)
    return square,contact


def shadow_control(v,E,temporal,tent,tent_rate,F,V,C,c,angular):
    square,contacts=owner.tensor.zeros((N*N,)),owner.tensor.zeros((N*N,))
    accumulate(square,contacts,V,C,F,v['densities'],mp.mpf(1),c)
    a=lambda z:owner.tensor.as_float(z)
    tf=np.r_[float(tent),float(tent_rate),a(temporal[0,:2]),a(temporal[1,:2])]
    actual=one_form_point_row(a(v['A']),a(v['A_time']),a(v['A_radial']),E,a(v['radial']),a(v['metric']),a(v['densities']),tf)
    S,Q=lift(square,angular),lift(contacts,angular)
    return dict(one_form_Hessian=owner.tensor.compare(actual['Hessian'],a(S+Q)),
        curvature_contact=owner.tensor.compare(actual['curvature_contact'],a(Q)),
        scope='Complete original binary64 point owner on the SAME rounded MP point operands; adverse near-zero cancellation retained')


def execute(refinement,application,output,cases,dps):
    out=Path(output)
    if out.exists():raise FileExistsError('Preserve every quadrature and arithmetic readout')
    if sha256(Path(owner.__file__).read_bytes()).hexdigest()!=OWNER_SHA:raise ValueError('Frozen MP field owner required')
    phases,reference,frozen,E,pins=owner.load_inputs(refinement,application);out.mkdir(parents=True)
    (out/'executed_producer.py').write_bytes(Path(__file__).read_bytes())
    inputs={'refinement/result.json':sha256((Path(refinement)/'result.json').read_bytes()).hexdigest(),
        'original_TIME6_archive':sha256((Path(application)/'changing_forms.npz').read_bytes()).hexdigest()}
    for side in('incoming','outgoing'):
        for q in(32,64,128):inputs[f'refinement/{side}_radial{q}/forms.npz']=sha256((Path(refinement)/f'{side}_radial{q}'/'forms.npz').read_bytes()).hexdigest()
    records=[]
    with mp.workdps(dps):
        c=owner.constants();angular=products(E)
        derivative_records={side:derivative_controls(phases[side],side,reference,c,frozen[side,128])for side in('incoming','outgoing')}
        for side in('incoming','outgoing'):
            phase=phases[side];rate=owner.ma(phase['rate']);length=abs(owner.m(phase['span']));origin=min(owner.m(phase['span']),mp.mpf(0));previous=None;previous_case=None
            for order,time_order in cases:
                u,tw=owner.time_nodes(phase,frozen[side,128],'mp',time_order,dps)
                snaps=[]
                for uu,ww in zip(u,tw):
                    t=uu+origin;raw=owner.raw_at(phase,t);geo=owner.geometry(raw,c['WALL']/2,c);chart=owner.response_chart(geo['delta'],c,96,'mp',dps)
                    snaps.append(dict(u=uu,t=t,w=ww,raw=raw,chart=chart,temporal=owner.temporal_values(uu,length),tent=2*min(uu/length,1-uu/length),tent_rate=(2 if uu<length/2 else -2)/length))
                x,rw=owner.rule(order,'mp',dps);rho=tuple(c['WALL']*a for a in x);rw=tuple(c['WALL']*a for a in rw)
                square,contacts=owner.tensor.zeros((N*N,)),owner.tensor.zeros((N*N,));controls=[]
                indices=((20,183),(40,823),(284,924),(823,1043));literal=owner.tensor.zeros((len(indices),2))
                for ri,(rr,wr)in enumerate(zip(rho,rw)):
                    basis=basis_with_derivative(rr,reference,c)
                    for ti,s in enumerate(snaps):
                        v=coefficient(s['raw'],rate,s['t'],rr,side,phase.get('parent_reference'),reference,c,s['chart'],basis)
                        F=curvatures(v['A'],v['A_time'],v['A_radial'],c);V,C=maps(v['A'],F,s['temporal'],v['radial'],s['tent'],s['tent_rate'],c)
                        accumulate(square,contacts,V,C,F,v['densities'],wr*s['w'],c)
                        columns={index:literal_column(index,v['A'],F,E,v['radial'],s['temporal'],s['tent'],s['tent_rate'],c)for index in set(a for p in indices for a in p)}
                        for k,(i,j)in enumerate(indices):literal[k]+=wr*s['w']*np.array(literal_pair(columns[i],columns[j],F,v['densities'],c),dtype=object)
                        if ti==0 and ri in(0,order//2,order-1):
                            controls.append(dict(radial_index=ri,time_index=ti,original_full_point_owner_shadow=shadow_control(v,E,s['temporal'],s['tent'],s['tent_rate'],F,V,C,c,angular)))
                    if ri%8==0 or ri==order-1:print(json.dumps(dict(side=side,radial_order=order,time_order=time_order,radial_index=ri+1,radial_count=order,dps=dps)),flush=True)
                matrices=dict(square_curvature=lift(square,angular),curvature_contact=lift(contacts,angular));matrices['one_form_Hessian']=matrices['square_curvature']+matrices['curvature_contact']
                comparison=None if previous is None else {name:owner.mp_compare(previous[name],a)for name,a in matrices.items()}
                integrated=[]
                for k,(i,j)in enumerate(indices):
                    expected=(literal[k,0],literal[k,1],sum(literal[k]))
                    integrated.append(dict(row=i,column=j,forms={name:dict(literal_MP_integral=mp.nstr(wanted,65),tensor_MP_integral=mp.nstr(a[i,j],65),absolute=mp.nstr(abs(a[i,j]-wanted),15))for (name,a),wanted in zip(matrices.items(),expected)}))
                folder=out/f'{side}_radial{order}_time{time_order}';folder.mkdir();arrays=dict(radial_points=np.array(list(map(float,rho))),radial_coordinate_weights=np.array(list(map(float,rw))),temporal_u=np.array(list(map(float,u))),temporal_coordinate_weights=np.array(list(map(float,tw))),source_midpoint=phase['midpoint'],source_rate=phase['rate'],square_coefficient_upper_exact_MP_tuple=exact_tuples(square),contact_coefficient_upper_exact_MP_tuple=exact_tuples(contacts),EW4_real_angular_derivatives=E)
                for name,a in matrices.items():owner.tensor.save_matrix(arrays,name,owner.tensor.as_float(a))
                owner._compressed_npz(folder/'forms.npz',arrays)
                axis=None if previous_case is None else('radial_at_fixed_time_rule'if previous_case[1]==time_order else'temporal_at_fixed_radial_rule'if previous_case[0]==order else'mixed_rule_change_not_separate_axis_control')
                record=dict(side=side,radial_order=order,temporal_order_per_half=time_order,previous_case_radial_and_time=previous_case,comparison_axis=axis,anchored_response_order=96,arithmetic_dps=dps,full_unrounded_MP_adjacent_case_comparisons=comparison,case_component_scaled_pass=None if comparison is None else all(mp.mpf(a['max_entry_scaled'])<=mp.mpf('2e-10')for a in comparison.values()),numerical_sha256=sha256((folder/'forms.npz').read_bytes()).hexdigest(),controls=controls,independent_integrated_full_Haar_MP_controls=integrated,physical_derivative_pass=False,coupled_corrections=0)
                (folder/'result.json').write_text(json.dumps(record,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n');records.append(record);previous=matrices;previous_case=(order,time_order)
    for name,module in list(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if p and(name.startswith('bhsm.')or name.startswith('bhsm_'))and Path(p).is_relative_to(ROOT):pins[Path(p).relative_to(ROOT).as_posix()]=sha256(Path(p).read_bytes()).hexdigest()
    pins[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    for name,h in pins.items():
        if sha256((ROOT/name).read_bytes()).hexdigest()!=h:raise ValueError('Owner changed: '+name)
    result=dict(classification='SAME_AFFINE_REAL_CELL_FULL1120_YANG_MILLS_MP_VALUES',records=records,independent_full_A_time_A_radial_and_reference_basis_derivative_controls=derivative_records,source_and_owner_sha256=dict(sorted(pins.items())),input_archive_sha256=dict(sorted(inputs.items())),cases_radial_and_time=cases,arithmetic_dps=dps,full_EW4_one_form_dimension=1120,SM_color_complement_not_in_this_EW4_constituent=True,original_positive_curvature_contact_retained=True,coefficient_basis_renormalized=False,common_kinetic_Yang_Mills_prefactor_binary_hex=float(owner.MAXWELL_TO_CAP).hex(),common1200_kinetic_with_independent_scalar_blocks_assembled=False,physical_native_outgoing_or_full15_derivative_pass=False,coupled_corrections=0,muon_magnetic_moment=None)
    (out/'result.json').write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--refinement',required=True);p.add_argument('--application',required=True);p.add_argument('--output',required=True);p.add_argument('--cases',nargs='+',default=['64:8','128:8','128:12']);p.add_argument('--dps',type=int,default=80);a=p.parse_args()
    if a.dps<65:raise ValueError('Meaningful declared MP precision required')
    cases=[tuple(map(int,s.split(':')))for s in a.cases]
    execute(a.refinement,a.application,a.output,cases,a.dps)
