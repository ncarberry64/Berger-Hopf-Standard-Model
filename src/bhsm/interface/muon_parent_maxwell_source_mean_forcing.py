"""Reached mean cotangents of the evaluated odd Maxwell/H responses.

These are third variations of the same scalar action, not a mean inverse.
Two odd factors pair by the exact unit-Haar Gram matrix.  The numerical
outgoing local core and its compact source remain explicitly conditional.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import numpy as np

from .muon_parent_maxwell_corrected_retarded import _ad, constant_angular_curvatures, load_corrected_iterate
from .muon_parent_maxwell_full_weak import M
from .muon_matched_mechanical_source import epsilon
from .muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation


def _real(x, name):
    if not np.isrealobj(x): raise ValueError(name+' requires explicit real coefficients')
    x=np.asarray(x,float)
    if not np.isfinite(x).all(): raise ValueError(name+' must be finite')
    return x


def _mean_bracket(u,v):
    result=np.zeros((len(u),len(v),4))
    result[:,:,:3]=np.einsum('ijk,ain,bjn->abk',epsilon()/np.sqrt(2),u[:,:3],v[:,:3])
    return result


def _first(A,u,ut,ur,E):
    angular=np.einsum('ihk,afck->aifch',E,u)
    act=lambda a,x:np.einsum('ij,ajn->ain',_ad(a),x)
    X=ut[:,1]-ur[:,0]+act(A[0],u[:,1])-act(A[1],u[:,0])
    T=np.array([ut[:,2+i]-angular[:,i,0]+act(A[0],u[:,2+i])-act(A[2+i],u[:,0]) for i in range(3)]).transpose(1,0,2,3)
    R=np.array([ur[:,2+i]-angular[:,i,1]+act(A[1],u[:,2+i])-act(A[2+i],u[:,1]) for i in range(3)]).transpose(1,0,2,3)
    B=2*u[:,2:].copy()
    for i,j,k in np.argwhere(epsilon()):
        B[:,i]+=epsilon()[i,j,k]*(angular[:,j,2+k]+act(A[2+j],u[:,2+k]))
    return X,T,R,B


def _second_mean(u,v):
    X=_mean_bracket(u[:,0],v[:,1])+_mean_bracket(v[:,0],u[:,1]).transpose(1,0,2)
    T=np.array([_mean_bracket(u[:,0],v[:,2+i])+_mean_bracket(v[:,0],u[:,2+i]).transpose(1,0,2) for i in range(3)]).transpose(1,2,0,3)
    R=np.array([_mean_bracket(u[:,1],v[:,2+i])+_mean_bracket(v[:,1],u[:,2+i]).transpose(1,0,2) for i in range(3)]).transpose(1,2,0,3)
    B=np.zeros_like(T)
    for i,j,k in np.argwhere(epsilon()):
        B[:,:,i]+=.5*epsilon()[i,j,k]*(_mean_bracket(u[:,2+j],v[:,2+k])+_mean_bracket(v[:,2+j],u[:,2+k]).transpose(1,0,2))
    return X,T,R,B


def _second_w(w,u):
    left=lambda a,x:np.einsum('ij,ajn->ain',_ad(a),x)
    X=left(w[0],u[:,1])-left(w[1],u[:,0])
    T=np.array([left(w[0],u[:,2+i])-left(w[2+i],u[:,0]) for i in range(3)]).transpose(1,0,2,3)
    R=np.array([left(w[1],u[:,2+i])-left(w[2+i],u[:,1]) for i in range(3)]).transpose(1,0,2,3)
    B=np.zeros_like(T)
    for i,j,k in np.argwhere(epsilon()):
        B[:,i]+=.5*epsilon()[i,j,k]*(left(w[2+j],u[:,2+k])-left(w[2+k],u[:,2+j]))
    return X,T,R,B


def _dot(u,v):
    return np.einsum('ain,bin->ab',u.reshape(len(u),-1,u.shape[-1]),v.reshape(len(v),-1,v.shape[-1]))


def _mdot(w,uv):
    return np.einsum('i,abi->ab',w.ravel(),uv.reshape(*uv.shape[:2],-1))


def _paired(u,v,d):
    e,r,bmag,k,beta=d
    return k*_dot(u[0],v[0])+e*_dot(u[1]-beta*u[2],v[1]-beta*v[2])-r*_dot(u[2],v[2])-bmag*_dot(u[3],v[3])


def _mean_paired(w,uv,d):
    e,r,bmag,k,beta=d
    return k*_mdot(w[0],uv[0])+e*_mdot(w[1]-beta*w[2],uv[1]-beta*uv[2])-r*_mdot(w[2],uv[2])-bmag*_mdot(w[3],uv[3])


def maxwell_mean_cotangents(A,At,Ar,u,ut,ur,E,densities):
    """All mean value/time/radial weak rows, D^3 S[w,u_A,u_B]."""
    A,At,Ar=(_real(x,'base connection') for x in (A,At,Ar))
    u,ut,ur=(_real(x,'odd connection response') for x in (u,ut,ur))
    E=_real(E,'right derivative matrices');d=_real(densities,'metric densities')
    if A.shape!=(5,4) or At.shape!=A.shape or Ar.shape!=A.shape or u.ndim!=4 or u.shape[1:3]!=(5,4) or ut.shape!=u.shape or ur.shape!=u.shape:
        raise ValueError('complete connection value/first jets and response axes required')
    n=u.shape[-1]
    if E.shape!=(3,n,n) or d.shape!=(5,) or np.any(d[:4]<=0): raise ValueError('same angular derivatives and positive metric densities required')
    F=_first(A,u,ut,ur,E);UV=_second_mean(u,u)
    shape=(20,len(u),len(u));out={key:np.zeros(shape) for key in ('value','time','radial')}
    for row in range(20):
        w=np.eye(20)[row].reshape(5,4)
        for key in out:
            value=w if key=='value' else np.zeros_like(w)
            dt=w if key=='time' else np.zeros_like(w)
            dr=w if key=='radial' else np.zeros_like(w)
            fw=tuple(x[0,...,0] for x in _first(A,value[None,...,None],dt[None,...,None],dr[None,...,None],np.zeros((3,1,1))))
            cross=_second_w(value,u)
            pair=_paired(F,cross,d)
            out[key][row]=_mean_paired(fw,UV,d)+pair+pair.T
    base=constant_angular_curvatures(A,At,Ar)
    F0=tuple(base[key] for key in ('Ftr','Ft','Fr','B'))
    eu,ev=F[1]-d[4]*F[2],F[1]-d[4]*F[2]
    e0,euv=F0[1]-d[4]*F0[2],UV[1]-d[4]*UV[2]
    factors=np.array([
        _dot(eu,ev)+_mdot(e0,euv),
        -_dot(F[2],F[2])-_mdot(F0[2],UV[2]),
        -_dot(F[3],F[3])-_mdot(F0[3],UV[3]),
        _dot(F[0],F[0])+_mdot(F0[0],UV[0]),
        -d[0]*(_dot(F[2],ev)+_dot(eu,F[2])+_mdot(F0[2],euv)+_mdot(e0,UV[2]))])
    out['metric_density_cotangent']=factors
    out['mechanical_lambda_cotangents']=np.array([np.einsum('fc,fcab->ab',M,out[key].reshape(5,4,len(u),len(u))[2:]) for key in ('value','time','radial')])
    out['paired_hessian']=_paired(F,F,d)+_mean_paired(F0,UV,d)
    return out


def higgs_mean_cotangents(H,Ht,A,h,ht,a,E,weights,*,lambda_H,nu_squared_action):
    """Real-2Re intrinsic scalar mean rows and geometry weight cotangents.

    h/ht are unknown-field responses, not independent fitted DH.  a is the
    material one-form response; Ar does not advect At a second time.
    """
    H,Ht,A,h,ht,a,E,weights=(_real(x,'same-coordinate scalar/gauge coefficients') for x in (H,Ht,A,h,ht,a,E,weights))
    if h.ndim!=3 or h.shape[1]!=4 or ht.shape!=h.shape or a.shape!=(len(h),5,4,h.shape[-1]) or H.shape!=(4,) or Ht.shape!=(4,) or A.shape!=(5,4) or E.shape!=(3,h.shape[-1],h.shape[-1]) or weights.shape!=(3,):
        raise ValueError('full intrinsic scalar and connection axes required')
    if np.any(weights<=0):raise ValueError('positive intrinsic metric weights required')
    if lambda_H is None or nu_squared_action is None or not np.isfinite([lambda_H,nu_squared_action]).all() or lambda_H<=0 or nu_squared_action<0:
        raise ValueError('explicit positive lambda_H and nonnegative nu_squared_action required')
    G=higgs_u2_real_representation()['real_generators'];fields=np.array([0,2,3,4])
    O=np.einsum('fc,cij->fij',A[fields],G)
    U=np.einsum('afcn,cij->afijn',a[:,fields],G)
    D0=np.einsum('fij,j->fi',O,H);D0[0]+=Ht
    D=np.einsum('fij,ajn->afin',O,h)+np.einsum('afijn,j->afin',U,H)
    D[:,0]+=ht;D[:,1:]+=np.einsum('fhk,aik->afih',E,h)
    mixed=np.einsum('afijn,bjn->abfi',U,h)
    mixed+=mixed.transpose(1,0,2,3)
    metric=np.array([weights[0],-weights[1],-weights[1],-weights[1]])
    hu=np.einsum('i,ain->an',H,h);hpair=_dot(h,h)
    potential=-lambda_H*(8*hu@hu.T+4*(H@H-nu_squared_action)*hpair)
    def contraction(w,wt,wa):
        Ow=np.einsum('fc,cij->fij',wa[fields],G)
        Dw=np.einsum('fij,j->fi',O,w)+np.einsum('fij,j->fi',Ow,H);Dw[0]+=wt
        cross=np.einsum('fij,ajn->afin',Ow,h)+np.einsum('afijn,j->afin',U,w)
        pair=np.array([_dot(D[:,f],cross[:,f]) for f in range(4)])
        result=2*np.einsum('f,fab->ab',metric,np.einsum('fi,abfi->fab',Dw,mixed)+pair+pair.transpose(0,2,1))
        wp=np.einsum('i,ain->an',w,h)
        result-=8*weights[2]*lambda_H*((H@w)*hpair+hu@wp.T+wp@hu.T)
        return result
    scalar_value=np.array([contraction(w,np.zeros(4),np.zeros((5,4))) for w in np.eye(4)])
    scalar_time=np.array([contraction(np.zeros(4),w,np.zeros((5,4))) for w in np.eye(4)])
    gauge_value=np.array([contraction(np.zeros(4),np.zeros(4),w.reshape(5,4)) for w in np.eye(20)])
    terms=np.array([2*(_dot(D[:,f],D[:,f])+_mdot(D0[f],mixed[:,:,f])) for f in range(4)])
    factors=np.array([terms[0],-terms[1:].sum(axis=0),potential])
    mech=np.einsum('fc,fcab->ab',M,gauge_value.reshape(5,4,len(h),len(h))[2:])
    volume=2*np.pi**2
    return dict(scalar_value=volume*scalar_value,scalar_time=volume*scalar_time,gauge_value=volume*gauge_value,
        metric_weight_cotangent=volume*factors,mechanical_lambda_cotangent=volume*mech,
        paired_hessian=volume*np.einsum('k,kab->ab',weights,factors),
        pairing='real_2Re; unit-Haar Gram; physical volume2pi² once',material_At_advection_count=1)


def materialize(output,repository=None,*,response_application='artifacts/muon_parent_maxwell_corrected_retarded_20261010/run_3'):
    from .muon_birth_candidate_geometry_action import ROOT
    from .muon_moving_geometric_action import retained_state
    from .muon_parent_gauge_geometry_correction import finite_common_iterate_at_time,compact_temporal_basis
    from .muon_parent_maxwell_geometry_weak import geometric_connection_coefficient_jets
    from .muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
    from .muon_parent_maxwell_full_q_application import retained_full_q_angular_space
    from .muon_parent_retarded_hypercharge import regular_radial_basis,WALL,compact_trace_pulse,_deterministic_npz
    repository=Path(ROOT if repository is None else repository);output=Path(output)
    if output.exists():raise FileExistsError('preserve prior receipts; use a new output')
    parentdir=repository/response_application
    receipt=json.loads((parentdir/'result.json').read_text())
    for name in ('application.npz','operator.npz'):
        if sha256((parentdir/name).read_bytes()).hexdigest()!=receipt['array_archives'][name]['sha256']:
            raise ValueError('response archive disagrees with its receipt')
    for name,digest in receipt['input_hashes'].items():
        if sha256((repository/name).read_bytes()).hexdigest()!=digest:raise ValueError('response input changed')
    source='src/bhsm/interface/muon_parent_maxwell_source_mean_forcing.py'
    inputs={**receipt['input_hashes'],**{response_application+'/'+k:sha256((parentdir/k).read_bytes()).hexdigest() for k in ('result.json','application.npz','operator.npz')}}
    inputs[source]=sha256((repository/source).read_bytes()).hexdigest()
    c,rep,own=load_corrected_iterate(repository);reference=retained_state(repository);angular=retained_full_q_angular_space(repository)
    with np.load(parentdir/'application.npz') as a:response={k:a[k].copy() for k in a.files}
    with np.load(parentdir/'operator.npz') as a:operator={k:a[k].copy() for k in a.files}
    E=angular['derivative_matrices'];Q=angular['source_coefficients'][160:].T.reshape(8,3,4,20)
    rho,quad=operator['rho'],operator['quadrature'];basis,radial=regular_radial_basis(rho,1)
    meanbasis,meanradial=regular_radial_basis(rho,rep['radial_order'])
    targetcount=rep['radial_count'];meanbasis,meanradial=meanbasis[:,:targetcount],meanradial[:,:targetcount]
    keys=('Maxwell_geometry_100','scalar_geometry_100','combined_geometry_100','Maxwell_mean_gauge_value','Maxwell_mean_gauge_time',
          'scalar_mean_gauge_value','scalar_mean_H_value','scalar_mean_H_time','combined_mean_gauge_value','combined_mean_gauge_time')
    arrays={key:[] for key in keys};indices=[];sampletimes=[]
    for requested in operator['time_nodes']:
        idx=int(np.argmin(abs(response['times']-requested)));u=float(response['times'][idx]);indices.append(idx);sampletimes.append(u)
        if abs(u-requested)>1e-14*rep['length']:raise ValueError('source response time does not bind the action nodes')
        t=u-rep['length'];data=finite_common_iterate_at_time(t,c,rep,reference,rho=rho)
        geo=geometric_connection_coefficient_jets(12,data['q'],data['qdot'],data['m'],rho,source_value=data['normal'],source_rate=data['normal_rate'])
        x=response['state'][idx,:320].T.reshape(8,4,4,20);xd=response['velocity'][idx,:320].T.reshape(8,4,4,20)
        at=response['A_tau'][idx].T.reshape(8,4,20);g,gd,_=compact_trace_pulse(u,receipt['duration'])
        mg=np.zeros((100,8,8));gv=np.zeros((targetcount,20,8,8));gt=np.zeros_like(gv)
        for r,row in enumerate(geo['rows']):
            field=np.zeros((8,5,4,20));field[:,0]=basis[r,0]*at;field[:,1:]=basis[r,0]*x;field[:,2:]+=basis[r,-1]*g*Q
            dt=np.zeros_like(field);dt[:,1:]=basis[r,0]*xd;dt[:,2:]+=basis[r,-1]*gd*Q
            dr=np.zeros_like(field);dr[:,0]=radial[r,0]*at;dr[:,1:]=radial[r,0]*x;dr[:,2:]+=radial[r,-1]*g*Q
            A,At,Ar=(data['fields'][k][r,0].copy() for k in ('gauge','gauge_tau','gauge_rho'))
            A[2:]+=M*(row['connection_lambda'].value-1);At[2:]+=M*row['lambda_tau'].value;Ar[2:]+=M*row['lambda_rho'].value
            densitynames=('electric','radial','angular','electric_radial','shift')
            result=maxwell_mean_cotangents(A,At,Ar,field,dt,dr,E,np.array([row[k].value for k in densitynames]))
            mg+=quad[r]*(np.einsum('kc,kab->cab',np.array([row[k].gradient for k in densitynames]),result['metric_density_cotangent'])
                +np.einsum('kc,kab->cab',np.array([row[k].gradient for k in ('connection_lambda','lambda_tau','lambda_rho')]),result['mechanical_lambda_cotangents']))
            for j in range(targetcount):
                gv[j]+=quad[r]*(meanbasis[r,j]*result['value']+meanradial[r,j]*result['radial'])
                gt[j]+=quad[r]*meanbasis[r,j]*result['time']
        wall=finite_common_iterate_at_time(t,c,rep,reference,rho=np.array([WALL]))
        weights=intrinsic_m4_weight_jet(12,wall['q'],wall['qdot'],wall['m'],source_value=wall['normal'],source_rate=wall['normal_rate'])
        b,bt=compact_temporal_basis(np.array([t]),rep['length']);sc=c[rep['scalar_start']:]
        H=b[0]*sc[:4]+sc[4:];Ht=bt[0]*sc[:4]
        A=wall['fields']['gauge'][0,0].copy();A[2:]+=M*(weights['mechanical_connection_lambda'].value-1)
        h=response['intrinsic_H_response'][idx].T.reshape(8,4,20);ht=response['velocity'][idx,320:400].T.reshape(8,4,20)
        a=np.zeros((8,5,4,20));a[:,2:]=g*Q
        sr=higgs_mean_cotangents(H,Ht,A,h,ht,a,E,np.array([weights[k].value for k in ('wT','wS','wV')]),
            lambda_H=rep['scalar_matching']['lambda_H'],nu_squared_action=receipt['nu_squared_action_member'])
        sg=8*(np.einsum('kc,kab->cab',np.array([weights[k].gradient for k in ('wT','wS','wV')]),sr['metric_weight_cotangent'])
            +weights['mechanical_connection_lambda'].gradient[:,None,None]*sr['mechanical_lambda_cotangent'])
        # Use the SAME radial basis at the actual reference wall, not the
        # last Gauss point and not a second connection advection.
        wallbasis,_=regular_radial_basis(np.array([WALL]),rep['radial_order'])
        scalar_gauge=np.array([8*wallbasis[0,j]*sr['gauge_value'] for j in range(targetcount)])
        values=(mg,sg,mg+sg,gv,gt,scalar_gauge,8*sr['scalar_value'],8*sr['scalar_time'],gv+scalar_gauge,gt)
        for key,value in zip(keys,values):arrays[key].append(value)
    arrays={key:np.array(value) for key,value in arrays.items()};arrays.update(times=np.array(sampletimes),response_indices=np.array(indices),
        mean_radial_basis=meanbasis,mean_radial_basis_derivative=meanradial,rho=rho,quadrature=quad)
    output.mkdir(parents=True);_deterministic_npz(output/'application.npz',arrays)
    if inputs!={name:sha256((repository/name).read_bytes()).hexdigest() for name in inputs}:
        raise RuntimeError('consumed input/source changed; replay with frozen operands')
    report=dict(scope='EVALUATED_SOURCE_PAIRED_MEAN_ACTION_COTANGENTS_ONLY',input_hashes=inputs,
        application_sha256=sha256((output/'application.npz').read_bytes()).hexdigest(),
        equation='H_mean x_AB=-D^3S[mean_test,x_A,x_B]; exported cotangents are D^3S before the minus sign',
        source_pair_order='A,B=raw betaPhoton0..7; symmetric bilinear mixed derivative, not divided by2',
        angular_pairing='exact unit-Haar Gram of complete real n1+n3 shells; no extra angular state selected',
        mean_gauge_target='radial2 plus independent wall lift, all At/Ar/A1/A2/A3 and all4 unitTr16 components',
        geometry_coordinate_order='q37,qdot37,m24,normal,normal_rate',
        scalar_Maxwell_relative_normalization=8.,scalar_volume='2pi² once; real_2Re',
        cap_normalization='multiply all combined cotangents by1/[8*(2pi²)²] when entering the common cap action',
        material_At_advection_count=1,At_coordinate_time_derivative_enters_Maxwell_action=False,
        scalar_Ar_direct_row_zero_reason='intrinsic material action depends At_ref and Ai; no repeated wall_rate Ar advection',
        scalar_H_time_load_zero_scope='this prescribed spatial trace has delta_At_wall=0, so the genuine mixed temporal DH contact is zero; not a full physical Gauss/domain identity',
        source_profile_scope=receipt['source_scope'],retained_geometry_side=receipt['retained_geometry_side'],
        incoming23_or_outgoing24_forward_physical_history_evaluated=False,
        nu_squared_action_member=receipt['nu_squared_action_member'],stationary_background=False,
        mean_second_response=None,causal_mean_descriptor_solved=False,physical_native_source_paired_contact=None,
        compact130_inverse_substituted=False,full_native_heat_or_Pauli_evaluated=False,
        error_scope='finite radial quadrature and17 stored-response action samples; no continuum or physical two-arm enclosure',
        array_norms={key:float(np.linalg.norm(arrays[key])) for key in keys},
        symmetry_maximum=max(float(np.max(abs(arrays[key]-arrays[key].swapaxes(-1,-2)))) for key in keys),
        symmetry_relative_maximum=max(float(np.max(abs(arrays[key]-arrays[key].swapaxes(-1,-2)))/(1+np.max(abs(arrays[key])))) for key in keys))
    (output/'result.json').write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return report


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();print(json.dumps(materialize(args.output),sort_keys=True))
