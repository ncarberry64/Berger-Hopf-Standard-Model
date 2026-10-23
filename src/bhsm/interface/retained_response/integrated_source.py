"""Radially integrated original Maxwell quadratic action on exported histories.

All outputs are on the retained PROVISIONAL real histories. They are not a
physical collider solution, native quantum propagator, or magnetic moment.
The source is the existing local magnetic trace, per unit canonical charge,
continued into the supplied frozen radial wall lift. No ramp is selected.
"""
from __future__ import annotations
from pathlib import Path
import sys, json, hashlib, io, zipfile
import numpy as np
from scipy.linalg import solve, eigvalsh
from .action_magnetic_kernel import (FieldJet, zero_field, curvature,
    curvature_first, curvature_second, pairing, local_hessian, local_action)
from .retained_magnetic_application import wall_data, FRAME, epsilon

FIELDS=('value','time','radial','angular')
NANG=4
NF=20
NCURV=40

def real_exact(x):
    a=np.asarray(x)
    if not np.isfinite(a).all() or (np.iscomplexobj(a) and np.any(a.imag != 0)):
        raise ValueError('Finite real source coefficients required; no clipping')
    return a.real

def flatten_curvature(c):
    return np.concatenate([c[0], *(v.reshape(v.shape[:-2]+(-1,)) for v in c[1:])],axis=-1)

def weighted_curvature(f,d):
    e,r,b,k,shift=np.moveaxis(d,-1,0)
    x,t,z,m=f[...,:4],f[...,4:16],f[...,16:28],f[...,28:40]
    y=t-shift[...,None]*z
    return np.concatenate([k[...,None]*x,e[...,None]*y,
        -e[...,None]*shift[...,None]*y-r[...,None]*z,-b[...,None]*m],axis=-1)

def pair_maps(a,b,d):
    # a,b have (radial,curvature,coefficient). Contractions keep signed action.
    def dot(x,y): return np.matmul(x.swapaxes(-1,-2),y)
    e,r,da,k,sh=np.moveaxis(d,-1,0)
    X,T,Z,B=a[:,:16],a[:,16:64],a[:,64:112],a[:,112:160]
    xx,tt,zz,bb=b[:,:16],b[:,16:64],b[:,64:112],b[:,112:160]
    y=T-sh[:,None,None]*Z;yy=tt-sh[:,None,None]*zz
    return k[:,None,None]*dot(X,xx)+e[:,None,None]*dot(y,yy)-r[:,None,None]*dot(Z,zz)-da[:,None,None]*dot(B,bb)

def _basis_jet(kind='value',angular_axis=0):
    I=np.eye(20).reshape(20,5,4)
    z=np.zeros_like(I);ea=np.zeros((20,3,5,4))
    if kind=='angular': ea[:,angular_axis]=I
    return FieldJet(I if kind=='value' else z,
        I if kind=='time' else z,I if kind=='radial' else z,ea)

def _kron_harmonic(a,b):
    # point... out20/in20 tensor harmonic4, in both output/input positions.
    return np.einsum('...ij,ab->...iajb',a,b).reshape(a.shape[:-2]+(a.shape[-2]*4,a.shape[-1]*4))

def point_linear_maps(connection):
    nr=len(connection);z=np.zeros_like(connection)
    base=FieldJet(connection[:,None],z[:,None],z[:,None],np.zeros((nr,1,3,5,4)))
    unit=_basis_jet()
    u=FieldJet(*(np.broadcast_to(getattr(unit,k),(nr,)+getattr(unit,k).shape) for k in FIELDS))
    Lvalue=real_exact(flatten_curvature(curvature_first(base,u))).swapaxes(-1,-2)
    L=_kron_harmonic(Lvalue,np.eye(4))
    zero=zero_field()
    # E_i Y_h = FRAME[i,h,k] Y_k; coefficient action is FRAME[i].T.
    for i in range(3):
        La=real_exact(flatten_curvature(curvature_first(zero,_basis_jet('angular',i)))).T
        L+=_kron_harmonic(La,FRAME[i].T)[None]
    Lr0=real_exact(flatten_curvature(curvature_first(zero,_basis_jet('radial')))).T
    Lt0=real_exact(flatten_curvature(curvature_first(zero,_basis_jet('time')))).T
    Lr=np.broadcast_to(_kron_harmonic(Lr0,np.eye(4)),L.shape)
    Lt=np.broadcast_to(_kron_harmonic(Lt0,np.eye(4)),L.shape)
    return L,Lr,Lt

def contact_matrix(sample):
    I=np.eye(20).reshape(20,5,4);z=np.zeros_like(I)
    u=FieldJet(I[:,None],z[:,None],z[:,None],np.zeros((20,1,3,5,4)))
    v=FieldJet(I[None],z[None],z[None],np.zeros((1,20,3,5,4)))
    C=real_exact(flatten_curvature(curvature_second(u,v)))
    base=FieldJet(sample['connection_value'],sample['connection_coordinate_time'],
        sample['connection_radial'],sample['connection_angular'])
    Fb=real_exact(flatten_curvature(curvature(base)))
    H=np.einsum('ri,abi->rab',weighted_curvature(Fb,sample['metric_densities']),C,optimize=True)
    return _kron_harmonic(H,np.eye(4))

def integrate_form(sample,normalization):
    V,R,T=point_linear_maps(sample['connection_value'])
    d=sample['metric_densities'];b=sample['radial_basis'];br=sample['radial_derivative_basis']
    w=normalization*sample['radial_quadrature']
    blocks={'vv':pair_maps(V,V,d)+contact_matrix(sample),
        'vr':pair_maps(V,R,d),'rr':pair_maps(R,R,d),
        'vt':pair_maps(V,T,d),'rt':pair_maps(R,T,d),'tt':pair_maps(T,T,d)}
    def integral(aa,bb,x):
        return np.einsum('r,rj,rk,rab->jakb',w,aa,bb,x,optimize=True).reshape(4*80,4*80)
    vr=integral(b,br,blocks['vr'])
    K=integral(b,b,blocks['vv'])+vr+vr.T+integral(br,br,blocks['rr'])
    B=integral(b,b,blocks['vt'])+integral(br,b,blocks['rt'])
    M=integral(b,b,blocks['tt'])
    return {'K':K,'B':B,'M':M}

def probe_coefficients(sample):
    raw=sample['raw_fields'];rate=sample['raw_coordinate_time_derivative'];wall=wall_data(raw)
    # Exact holomorphic directional evaluation of analytic source geometry.
    wd=wall_data(raw.astype(complex)+1j*1e-20*rate)
    R=float(wall['R4']);Rd=float(wd['R4'].imag/1e-20)
    s=sample['H_selected_charge_coefficients'];sd=sample['H_selected_charge_coordinate_rate']
    wave=np.zeros((5,4,3));ep=epsilon()
    # Y=(2x0,2x1,2x2,2x3), q_j=-x_(3-j), A_i=-R4^2 eps_ijk q_j s/2.
    for i,j,k in np.ndindex(3,3,3):wave[2+i,3-j,k]+=ep[i,j,k]/4
    q=np.einsum('fhk,c->fchk',wave,s)*R**2
    qd=np.einsum('fhk,c->fchk',wave,2*R*Rd*s+R**2*sd)
    W=np.zeros((4,5,4,4,3));Wt=np.zeros_like(W)
    W[3]=q;Wt[3]=qd
    return {'W':W.reshape(320,3),'Wdot':Wt.reshape(320,3),
        'R4_wall':R,'R4_wall_rate':Rd,'charge_rate_check':float(np.max(abs(wd['charge'].imag/1e-20-sd)))}

def source_columns(form,probe):
    K,B,M=(form[k] for k in ('K','B','M'));W,Wd=probe['W'],probe['Wdot']
    return {'F_b':K@W+B@Wd,'F_bdot':B@W,
        'H_b':B.T@W+M@Wd,'H_bdot':M@W}

def gauss_eliminate(form,source):
    ids=np.arange(320).reshape(4,5,4,4)
    y=ids[:,0].ravel();z=ids[:,1:].ravel()
    K,B,M=(form[k] for k in ('K','B','M'))
    if np.any(M[y]) or np.any(M[:,y]) or np.any(B[:,y]):
        raise ArithmeticError('At kinetic/rate columns must vanish exactly')
    A=K[np.ix_(y,y)];C=K[np.ix_(y,z)];D=B[np.ix_(y,z)]
    loads=np.c_[source['F_b'][y],source['F_bdot'][y]]
    rhs=np.c_[C,D,loads]
    sol=solve(A,rhs,assume_a='sym')
    Y,Z,a=sol[:,:256],sol[:,256:512],sol[:,512:]
    f=np.c_[source['F_b'][z],source['F_bdot'][z]]-C.T@a
    h=np.c_[source['H_b'][z],source['H_bdot'][z]]-D.T@a
    Mr=M[np.ix_(z,z)]-D.T@Z
    Br=B[np.ix_(z,z)]-C.T@Z
    Kr=K[np.ix_(z,z)]-C.T@Y
    solve_res=A@sol-rhs
    eig=eigvalsh(A);m_eig=eigvalsh((Mr+Mr.T)/2)
    # This finite Gauss operation is algebra only. No physical quotient inferred.
    return {'gauss_ids':y,'dynamic_ids':z,'A':A,'C':C,'D':D,'Y':Y,'Z':Z,
        'At_source':-a,'Mred':Mr,'Bred':Br,'Kred':Kr,'fred':f,'hred':h,
        'gauss_source_constant_matrix':-.5*loads.T@a,
        'force_shift':-C.T@a,'momentum_shift':-D.T@a,
        'solve_error':float(np.max(abs(solve_res))),
        'solve_backward_error':float(np.linalg.norm(solve_res,np.inf)/(np.linalg.norm(A,np.inf)*np.linalg.norm(sol,np.inf)+np.linalg.norm(rhs,np.inf))),
        'A_eigenvalues':eig,'Mred_eigenvalues':m_eig}

def verify_input(root):
    root=Path(root);manifest=json.loads((root/'SHA256SUMS.json').read_text())
    for name,h in manifest.items():
        path=(root/name).resolve()
        if not path.is_relative_to(root.resolve()) or hashlib.sha256(path.read_bytes()).hexdigest()!=h:
            raise ValueError('Input integrity failure: '+name)
    met=json.loads((root/'MANIFEST.json').read_text())
    if met['configuration']['radial_order']!=192 or met['configuration']['time_order']!=4:
        raise ValueError('this execution preserves the exported quadratures')
    return met, {'file_hashes_verified':len(manifest),'input_manifest_sha256':hashlib.sha256((root/'SHA256SUMS.json').read_bytes()).hexdigest(),
        'export_revision':met['configuration']['head'],'original_source_texts_verified':len(met['configuration']['source_hashes']),
        'inherited_full_archives_rehashed_here':False,'quantum_or_physical_completion_implied':False}

def save_npz(path,arrays):
    tmp=Path(str(path)+'.tmp')
    with zipfile.ZipFile(tmp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for n,a in sorted(arrays.items()):
            buff=io.BytesIO();np.lib.format.write_array(buff,np.asarray(a),allow_pickle=False)
            info=zipfile.ZipInfo(n+'.npy',(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,buff.getvalue(),compresslevel=6)
    tmp.replace(path)

def evaluate(root,output):
    root=Path(root);out=Path(output)
    out.mkdir(parents=True,exist_ok=False)
    md,validation=verify_input(root);results=[]
    for side in ('incoming','outgoing'):
        for label in ('lo','q000','q001','q002','q003','hi'):
            sample=dict(np.load(root/side/(label+'.npz'),allow_pickle=False))
            sm=json.loads((root/side/(label+'.json')).read_text())
            form=integrate_form(sample,md['MAXWELL_TO_CAP']);probe=probe_coefficients(sample)
            source=source_columns(form,probe);reduced=gauss_eliminate(form,source)
            arrays={**form,**{k:v for k,v in probe.items() if isinstance(v,np.ndarray)},**source,
                **{k:v for k,v in reduced.items() if isinstance(v,np.ndarray)}}
            save_npz(out/(side+'_'+label+'.npz'),arrays)
            eig=reduced['Mred_eigenvalues']
            rec={'side':side,'label':label,'time':sm['coordinate_time'],'time_weight':sm['positive_time_quadrature'],
                'source_max':{k:float(np.max(abs(v))) for k,v in source.items()},
                'Gauss_value_source_max':float(np.max(abs(source['F_b'][reduced['gauss_ids']]))),
                'Gauss_rate_source_max':float(np.max(abs(source['F_bdot'][reduced['gauss_ids']]))),
                'source_force_shift_max':float(np.max(abs(reduced['force_shift']))),
                'source_momentum_shift_max':float(np.max(abs(reduced['momentum_shift']))),
                'gauss_matrix_min_eigenvalue':float(reduced['A_eigenvalues'][0]),
                'gauss_matrix_max_eigenvalue':float(reduced['A_eigenvalues'][-1]),
                'gauss_solve_absolute_residual':reduced['solve_error'],
                'gauss_solve_scaled_backward_error':reduced['solve_backward_error'],
                'reduced_M_min_eigenvalue':float(eig[0]),'reduced_M_max_eigenvalue':float(eig[-1]),
                'reduced_M_below_relative_1e-10':int(np.sum(abs(eig)<1e-10*max(abs(eig)))),
                'raw_form_symmetry':max(float(np.max(abs(form[k]-form[k].T))) for k in ('K','M')),
                'R4_wall':probe['R4_wall'],'R4_wall_rate':probe['R4_wall_rate'],
                'H_axis_rate_vs_original':probe['charge_rate_check']}
            results.append(rec)
            (out/'progress.json').write_text(json.dumps(results,indent=2,sort_keys=True)+'\n')
            print(side,label,'Gauss solve',rec['gauss_solve_absolute_residual'],'source',rec['source_max'],flush=True)
    result={'classification':'EVALUATED_RADIAL_ORIGINAL_MAXWELL_MAGNETIC_DRIVE_AND_FINITE_GAUSS_SOURCE',
        'validation':validation,'normalization':md['MAXWELL_TO_CAP'],'records':results,
        'angular_space':'n1, real Cartesian Y=2*x; (radial4,field5,internal4,harmonic4)',
        'radial_basis':'unaltered exported four-function frame, including the independent wall lift',
        'scope':'held actual provisional background, direct local magnetic wall trace per e_can; original Maxwell action only',
        'magnetic_amplitude_or_turnon_time_selected':False,'retarded_evolution_executed':False,
        'complete_physical_outgoing_derivative_admitted':False,'coupled_corrections':0,
        'physical_Maxwell_all226_after_state':None,'a_mu':None,'g_mu':None,'total_uncertainty':None,
        'radial_or_time_convergence_certified':False,'finite_algebraic_Gauss_elimination_is_physical_quotient':False}
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    return result

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--inputs',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();evaluate(a.inputs,a.output)
