"""Finite causal Maxwell trace-to-response map on the exported histories.

Uses only the previously assembled original M/B/K matrices. Wall traces stay
as independent inputs. This is not a completed physical exterior or muon solve.
Time action rescaling and kinetic whitening are explicit coordinate changes.
"""
from __future__ import annotations
from pathlib import Path
import json, io, zipfile, hashlib
import numpy as np
from scipy.linalg import solve, cholesky, lu_factor, lu_solve, eigvalsh
from numpy.polynomial import Polynomial


def save_npz(path, data):
    path=Path(path);tmp=path.with_suffix(path.suffix+'.tmp')
    with zipfile.ZipFile(tmp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for name,value in sorted(data.items()):
            b=io.BytesIO();np.lib.format.write_array(b,np.asarray(value),allow_pickle=False)
            info=zipfile.ZipInfo(name+'.npy',(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,b.getvalue(),compresslevel=6)
    tmp.replace(path)


def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def maxabs(a):return float(np.max(np.abs(a))) if np.size(a) else 0.
def sl(mat,a,b):return mat[np.ix_(a,b)]


def gauss_table(n=4):
    t,w=np.polynomial.legendre.leggauss(n);c=(t+1)/2;b=w/2
    A=np.empty((n,n))
    for j in range(n):
        ell=Polynomial.fromroots(np.delete(c,j));ell=ell/ell(c[j]);integ=ell.integ()
        A[:,j]=integ(c)-integ(0.)
    return c,b,A


def layout(gauge='interior'):
    ids=np.arange(320).reshape(4,5,4,4)
    y=ids[:3,0].ravel() # Only zero-wall-trace At coordinates are eliminated.
    g=ids[3,[0,2,3,4]].ravel() # Tangential material trace: At and Ai, not Ar.
    free=np.setdiff1d(np.arange(320),np.r_[y,g])
    fixed=ids[0 if gauge=='interior' else 3,1,3,:].ravel()
    x=np.setdiff1d(free,fixed)
    if (len(y),len(g),len(free),len(x))!=(48,64,208,204):raise AssertionError('layout changed')
    return y,x,g,fixed


def partial_gauss(M,B,K,ny):
    A=K[:ny,:ny];C=K[:ny,ny:];D=B[:ny,ny:]
    if maxabs(M[:ny])>1e-16 or maxabs(M[:,:ny])>1e-16 or maxabs(B[:,:ny])>1e-16:
        raise ValueError('At-rate terms incompatible with declared algebraic form')
    sol=solve(A,np.c_[C,D],assume_a='sym')
    n=len(C.T);Y,Z=sol[:,:n],sol[:,n:]
    return dict(M=M[ny:,ny:]-D.T@Z,B=B[ny:,ny:]-C.T@Z,
                K=K[ny:,ny:]-C.T@Y,Y=Y,Z=Z,A=A,
                solve_absolute=maxabs(A@sol-np.c_[C,D]))


def raw_reorder(sample,T,y,x,g):
    # q_phys = J qhat; qhat_At = T At. S_hat = T S_phys.
    order=np.r_[y,x,g];J=np.eye(320)[:,order]
    J[:,np.isin(order,np.arange(320).reshape(4,5,4,4)[:,0].ravel())]/=T
    M=J.T@sample['M']@J;B=T*(J.T@sample['B']@J);K=T*T*(J.T@sample['K']@J)
    return J,M,B,K


def prepare(side,inputs,gauge='interior'):
    folder=Path(inputs);meta=json.loads((folder/'metadata.json').read_text())
    T=meta['sides'][side]['duration'];y,x,g,fixed=layout(gauge);ny,nx,ng=len(y),len(x),len(g)
    labels=['lo','q000','q001','q002','q003','hi']
    samples={lab:dict(np.load(folder/(side+'_'+lab+'.npz'),allow_pickle=False)) for lab in labels}
    J,M,B,K=raw_reorder(samples['lo'],T,y,x,g)
    red=partial_gauss(M,B,K,ny);M0=red['M'][:nx,:nx]
    # Exact gauge-slice kinetic pairing, not geometric pseudo-inversion.
    R=cholesky((M0+M0.T)/2,lower=False)
    Ri=solve(R,np.eye(nx),assume_a='gen')
    H=np.eye(ny+nx+ng);H[ny:ny+nx,ny:ny+nx]=Ri
    J=J@H
    records={};ngeneral=2*ng;nmag=6;nd=ngeneral+nmag
    for lab in labels:
        s=samples[lab];tau=meta['sides'][side]['samples'][lab]['tau']
        M=J.T@s['M']@J;B=T*(J.T@s['B']@J);K=T*T*(J.T@s['K']@J)
        red=partial_gauss(M,B,K,ny)
        # Source traces are still prescribed INPUT coefficients. No exterior law.
        G=np.zeros((ng,nd));Gd=np.zeros_like(G)
        G[:,:ng]=np.eye(ng);G[:,ng:2*ng]=tau*np.eye(ng);Gd[:,ng:2*ng]=np.eye(ng)
        # y physical rescaling affects wall At; W has only spatial entries here.
        inv_port_scale=np.ones(ng);inv_port_scale[:16]=T
        W=inv_port_scale[:,None]*s['W'][g]
        Wd=T*inv_port_scale[:,None]*s['Wdot'][g]
        G[:,ngeneral:ngeneral+3]=W;G[:,ngeneral+3:]=tau*W
        Gd[:,ngeneral:ngeneral+3]=Wd;Gd[:,ngeneral+3:]=W+tau*Wd
        mr,br,kr=[red[z] for z in ('M','B','K')]
        mx,bx,kx=mr[:nx,:nx],br[:nx,:nx],kr[:nx,:nx]
        h=br[nx:,:nx].T@G+mr[:nx,nx:]@Gd
        f=kr[:nx,nx:]@G+br[:nx,nx:]@Gd
        sol=solve(mx,np.c_[bx.T,np.eye(nx),h],assume_a='pos')
        neg=-sol[:,:nx];inv=sol[:,nx:2*nx];lh=-sol[:,2*nx:]
        F=np.block([[neg,inv],[kx+bx@neg,bx@inv]])
        force=np.vstack((lh,f+bx@lh))
        records[lab]=dict(M=M,B=B,K=K,red=red,G=G,Gd=Gd,F=F,force=force,h=h,f=f,
                         tau=tau,physical_time=meta['sides'][side]['samples'][lab]['time'])
    N=np.load(folder/'gauge_maps.npz')['relative_spatial_gauge']
    Nt=np.load(folder/'gauge_maps.npz')['relative_temporal_gauge']
    return dict(side=side,duration=T,ny=ny,nx=nx,ng=ng,nd=nd,records=records,J=J,
                y=y,x=x,g=g,fixed=fixed,whitening=R,gauge=gauge,gaugeN=N,gaugeNt=Nt,
                kinetic_min_unwhitened=float(eigvalsh(M0)[0]),kinetic_max_unwhitened=float(eigvalsh(M0)[-1]))


def causal_solve(data):
    nx,nd=data['nx'],data['nd'];n=2*nx;c,b,A=gauss_table();ns=4
    points=[data['records'][f'q{i:03d}'] for i in range(ns)]
    if max(abs(c-np.array([r['tau'] for r in points])))>2e-14:raise ValueError('export time nodes changed')
    mat=np.zeros((ns*n,ns*n));rhs=np.zeros((ns*n,n+nd))
    for i in range(ns):
        rhs[i*n:(i+1)*n,:n]=np.eye(n)
        for j in range(ns):
            mat[i*n:(i+1)*n,j*n:(j+1)*n]=-A[i,j]*points[j]['F']
            rhs[i*n:(i+1)*n,n:]+=A[i,j]*points[j]['force']
        mat[i*n:(i+1)*n,i*n:(i+1)*n]+=np.eye(n)
    factor=lu_factor(mat);z=lu_solve(factor,rhs)
    res=mat@z-rhs
    Z=z.reshape(ns,n,n+nd)
    Zd=np.array([p['F']@zz+np.c_[np.zeros((n,n)),p['force']] for p,zz in zip(points,Z)])
    initial=np.c_[np.eye(n),np.zeros((n,nd))]
    final=initial+np.einsum('i,ijk->jk',b,Zd)
    symp=np.block([[np.zeros((nx,nx)),np.eye(nx)],[-np.eye(nx),np.zeros((nx,nx))]])
    transfer=final[:,:n]
    backward=float(np.linalg.norm(res,np.inf)/(np.linalg.norm(mat,np.inf)*np.linalg.norm(z,np.inf)+np.linalg.norm(rhs,np.inf)))
    return dict(stages=Z,stage_rates=Zd,initial=initial,final=final,
        stage_equation_absolute=maxabs(res),stage_backward_error=backward,
        homogeneous_symplectic_error=maxabs(transfer.T@symp@transfer-symp),
        homogeneous_hamiltonian_identity=max(maxabs(p['F'].T@symp+symp@p['F']) for p in points))


def reconstruct(data,label,Z):
    nx,ny,ng,nd=data['nx'],data['ny'],data['ng'],data['nd'];n=2*nx
    r=data['records'][label];fulln=Z.shape[1]
    G=np.c_[np.zeros((ng,n)),r['G']];Gd=np.c_[np.zeros((ng,n)),r['Gd']]
    Zd=r['F']@Z+np.c_[np.zeros((n,n)),r['force']]
    X,V=Z[:nx],Zd[:nx]
    remaining=np.vstack((X,G));rates=np.vstack((V,Gd))
    Y=-r['red']['Y']@remaining-r['red']['Z']@rates
    Q=np.vstack((Y,remaining));Qd=np.vstack((np.zeros_like(Y),rates))
    # At derivative is absent from original scalar action; its unused rate slot
    # is a placeholder in these action maps, NOT an assertion about physical d_tAt.
    grad=r['K']@Q+r['B']@Qd
    mom=r['B'].T@Q+r['M']@Qd
    qphys=data['J']@Q;vphys=data['J']@Qd/data['duration']
    forceg=grad[ny+nx:];momg=mom[ny+nx:]
    return dict(Q=Q,Qd=Qd,qphys=qphys,vphys=vphys,grad=grad,mom=mom,forceg=forceg,momg=momg,
                gauss=maxabs(grad[:ny]),momentum=maxabs(mom[ny:ny+nx]-Z[nx:]),
                euler=maxabs(grad[ny:ny+nx]-Zd[nx:]),X=X,V=V,Y=Y)


def boundary_maps(data,solution):
    nx,nd=data['nx'],data['nd'];n=2*nx;c,b,A=gauss_table();ng=data['ng']
    W=np.zeros((nd,n+nd));responses={}
    for k,lab in enumerate(['q000','q001','q002','q003']):
        rec=reconstruct(data,lab,solution['stages'][k]);responses[lab]=rec;r=data['records'][lab]
        W+=b[k]*(r['G'].T@rec['forceg']+r['Gd'].T@rec['momg'])
    for lab,key in [('lo','initial'),('hi','final')]:responses[lab]=reconstruct(data,lab,solution[key])
    endpoint=data['records']['hi']['G'].T@responses['hi']['momg']-data['records']['lo']['G'].T@responses['lo']['momg']
    final=solution['final'][:,n:];initial=solution['initial'][:,n:]
    green=W[:,n:]-W[:,n:].T + final[:nx].T@final[nx:]-final[nx:].T@final[:nx] - initial[:nx].T@initial[nx:]+initial[nx:].T@initial[:nx]
    return dict(weak_wall=W,wall_euler_weak=W-endpoint,wall_temporal_endpoint=endpoint,responses=responses,
                discrete_boundary_green_error=maxabs(green),
                wall_antisymmetry_without_temporal_term=maxabs(W[:,n:]-W[:,n:].T))


def independent_original_dae(data):
    """Direct Gauss-Legendre solve of original momentum, Euler, and Gauss rows.
    Does not call partial_gauss, use the reduced coefficients, or invert mass.
    Returns maps for all initial and boundary columns.
    """
    nx,ny,ng,nd=data['nx'],data['ny'],data['ng'],data['nd'];n=2*nx;block=2*nx+ny
    c,b,A=gauss_table();mat=np.zeros((4*block,4*block));rhs=np.zeros((4*block,n+nd))
    sx=np.arange(ny,ny+nx);sg=np.arange(ny+nx,ny+nx+ng);sy=np.arange(ny)
    pp=[data['records'][f'q{i:03d}'] for i in range(4)]
    for i,ri in enumerate(pp):
        ix=slice(i*block,i*block+nx);ip=slice(i*block+nx,i*block+2*nx);iy=slice(i*block+2*nx,(i+1)*block)
        ci=slice(i*block,i*block+nx);cv=slice(i*block+nx,i*block+2*nx);cy=slice(i*block+2*nx,(i+1)*block)
        M,B,K=ri['M'],ri['B'],ri['K'];G,Gd=ri['G'],ri['Gd']
        mat[ix,ci]=np.eye(nx);rhs[ix,:nx]=np.eye(nx)
        mat[ip,ci]=sl(B,sx,sx).T;mat[ip,cv]=sl(M,sx,sx);mat[ip,cy]=sl(B,sy,sx).T
        rhs[ip,nx:n]=np.eye(nx)
        rhs[ip,n:]=-sl(M,sx,sg)@Gd-sl(B,sg,sx).T@G
        mat[iy,ci]=sl(K,sy,sx);mat[iy,cv]=sl(B,sy,sx);mat[iy,cy]=sl(K,sy,sy)
        rhs[iy,n:]=-sl(K,sy,sg)@G-sl(B,sy,sg)@Gd
        for j,rj in enumerate(pp):
            jx=slice(j*block,j*block+nx);jv=slice(j*block+nx,j*block+2*nx);jy=slice(j*block+2*nx,(j+1)*block)
            mat[ix,jv]-=A[i,j]*np.eye(nx)
            mat[ip,jx]-=A[i,j]*sl(rj['K'],sx,sx)
            mat[ip,jv]-=A[i,j]*sl(rj['B'],sx,sx)
            mat[ip,jy]-=A[i,j]*sl(rj['K'],sx,sy)
            rhs[ip,n:]+=A[i,j]*(sl(rj['K'],sx,sg)@rj['G']+sl(rj['B'],sx,sg)@rj['Gd'])
    z=lu_solve(lu_factor(mat),rhs);res=mat@z-rhs;stage=z.reshape(4,block,n+nd)
    Z=[];rates=[];Qs=[]
    for i,(zz,r) in enumerate(zip(stage,pp)):
        X,V,Y=zz[:nx],zz[nx:2*nx],zz[2*nx:]
        G=np.c_[np.zeros((ng,n)),r['G']];Gd=np.c_[np.zeros((ng,n)),r['Gd']]
        Q=np.vstack((Y,X,G));Qd=np.vstack((np.zeros_like(Y),V,Gd))
        mom=r['M']@Qd+r['B'].T@Q;grad=r['K']@Q+r['B']@Qd
        Z.append(np.vstack((X,mom[ny:ny+nx])));rates.append(np.vstack((V,grad[ny:ny+nx])));Qs.append(Q)
    final=np.c_[np.eye(n),np.zeros((n,nd))]+np.einsum('i,ijk->jk',b,np.array(rates))
    return dict(stages=np.array(Z),final=final,original_stages=np.array(Qs),
                equation_absolute=maxabs(res),backward_error=float(np.linalg.norm(res,np.inf)/(np.linalg.norm(mat,np.inf)*np.linalg.norm(z,np.inf)+np.linalg.norm(rhs,np.inf))))
