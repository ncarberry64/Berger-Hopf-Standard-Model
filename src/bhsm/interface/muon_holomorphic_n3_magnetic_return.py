"""Source-directed n3→n2/n4 action on original24 wall/current test images.

The complete84×n1 causal magnetic field is kept as the source. Trials are
explicit supplied original wall-gauge/H coordinate tests, before angular
assembly. They are not a selected physical current, Green, or native loop.
"""
from __future__ import annotations
import numpy as np
from functools import lru_cache
from .muon_literal_wall_magnetic_action import maxwell_magnetic_coefficient_tensors,intrinsic_magnetic_hessian_block
from .muon_parent_mean_causal_action import MAXWELL_TO_CAP
from .muon_intrinsic_scalar_discretization import scalar_s3_discretization


@lru_cache(maxsize=1)
def source_n3_return_angular_images():
    a=scalar_s3_discretization(4);labels=a['real_basis_labels'];E=a['real_angular_derivative_matrices']
    ids={n:np.flatnonzero([l[0]==n for l in labels])for n in(1,2,3,4)}
    Y={n:a['real_basis_values'][:,i]for n,i in ids.items()};w=a['haar_weights']
    G={n:np.einsum('pe,p,po,ps->eos',Y[n],w,Y[3],Y[1],optimize=True)for n in(2,4)}
    product=(Y[3][:,:,None]*Y[1][:,None,:]).reshape(len(w),64)
    reconstructed=sum(Y[n]@G[n].reshape(len(ids[n]),64)for n in(2,4))
    return dict(gaunts=G,derivatives={n:E[:,i][:,:,i]for n,i in ids.items()},
        labels={n:np.array([labels[j]for j in i])for n,i in ids.items()},
        complete_n3_times_n1_image_residual=float(np.sqrt(np.max(np.sum(w[:,None]*abs(product-reconstructed)**2,axis=0)))),
        source_degree=1,starting_degree=3,complete_return_degrees=(2,4))


def projected_magnetic_return_action(binding,total_field,coordinate_rate,test_lift,
        target_derivatives,trial_derivatives,source_derivatives,gaunt):
    """All K/BF/BR/M and independent angular sides on a named test lift.

    Each output acts on 24*ntarget by 24*ntrial, rather than constructing
    the full84-harmonic action tensor. The source still uses EVERY P/Pt/Pr
    and W/hv row, including induced H/Hdot and all interior At coefficients.
    """
    row,lifts=binding['row'],binding['lifts'];f,ft=np.asarray(total_field,complex),np.asarray(coordinate_rate,complex)
    T=np.asarray(test_lift,complex);Ee,Eo,Es,G=[np.asarray(x)for x in(target_derivatives,trial_derivatives,source_derivatives,gaunt)]
    ne,no,ns=G.shape
    if f.shape!=(336,3)or ft.shape!=f.shape or T.shape!=(84,24)or ns!=4 or Ee.shape!=(3,ne,ne)or Eo.shape!=(3,no,no)or Es.shape!=(3,4,4):
        raise ValueError('complete84×source1 plus explicit original24 test lift/complete angular maps required')
    if any(not np.isrealobj(x)for x in(Ee,Eo,Es,G))or any(not np.isfinite(x).all()for x in(f,ft,T,Ee,Eo,Es,G)):
        raise ValueError('real harmonic basis, analytic complex field/source coefficients required')
    P,Pr,Pt,W,hv=(np.asarray(lifts[n],complex)for n in('P','Pr','Pt','W','hv'));nr=len(P)
    if np.max(abs(np.r_[W,hv]@T-np.eye(24)))>2e-13:raise ValueError('tests must be the supplied exact gauge-wall/H image, not a fitted projection')
    field=f.reshape(84,4,3);rate=ft.reshape(84,4,3)
    source=np.einsum('ram,mhb->rahb',P,field).reshape(nr,5,4,4,3)
    st=np.einsum('ram,mhb->rahb',Pt,rate).reshape(source.shape)
    sr=np.einsum('ram,mhb->rahb',Pr,field).reshape(source.shape)
    sw=np.einsum('am,mhb->ahb',W,field).reshape(5,4,4,3)
    sh=np.einsum('am,mhb->ahb',hv,field);sht=np.einsum('am,mhb->ahb',hv,rate)
    ep=np.r_[np.eye(ne)[None],Ee];op=np.r_[np.eye(no)[None],Eo]
    right_ang=np.array([[G[:,:,h]@op[p]for h in range(4)]for p in range(4)])
    left_ang=np.array([[ep[p].T@G[:,:,h]for h in range(4)]for p in range(4)])
    source_API_E=Es.transpose(0,2,1)
    def scalar_maps(n):
        v=np.zeros((28*n,24*n),complex);t=v.copy();I=np.eye(n)
        v[:4*n]=np.kron(hv@T,I);v[4*n:24*n]=np.kron(W@T,I);t[24*n:]=np.kron(hv@T,I)
        return v,t
    Se=scalar_maps(ne);So=scalar_maps(no);left=[];right=[];curvature=[];scalar=[]
    for axis in range(3):
        L=np.zeros((2,2,4,24,24,4),complex);R=L.copy();C=np.zeros((24,24,4),complex)
        for r,weight in enumerate(lifts['radial_weights']):
            maps=np.zeros((2,3,20,24),complex);maps[0,0]=P[r]@T;maps[0,2]=Pr[r]@T;maps[1,1]=Pt[r]@T
            a=maxwell_magnetic_coefficient_tensors(row['A'][r],source[r,:,:,:,axis],st[r,:,:,:,axis],
                sr[r,:,:,:,axis],row['densities'][r],source_API_E)
            factor=MAXWELL_TO_CAP*weight
            L+=factor*np.einsum('uiam,ijpabh,vjbn->uvpmnh',maps,a['left'],maps,optimize=True)
            R+=factor*np.einsum('uiam,ijpabh,vjbn->uvpmnh',maps,a['right'],maps,optimize=True)
            C+=factor*np.einsum('am,abh,bn->mnh',maps[0,0],a['contact'],maps[0,0],optimize=True)
        left.append(np.einsum('uvpmnh,pheo->uvmeno',L,right_ang,optimize=True).reshape(2,2,24*ne,24*no))
        right.append(np.einsum('uvpmnh,pheo->uvmeno',R,left_ang,optimize=True).reshape(2,2,24*ne,24*no))
        curvature.append(np.einsum('mnh,eoh->meno',C,G,optimize=True).reshape(24*ne,24*no))
        h=intrinsic_magnetic_hessian_block(row['wall_A'],row['H'],row['Hdot'],sw[:,:,:,axis],
            sh[:,:,axis],sht[:,:,axis],row['weights'],Ee,Eo,source_API_E,G,
            lambda_H=row['lambda_H'],nu_squared_action=row['nu_squared_action'])
        scalar.append(np.array([[Se[i].T@h['hessian']@So[j]for j in range(2)]for i in range(2)]))
    left,right,scalar,curvature=map(np.asarray,(left,right,scalar,curvature))
    total=left+right+scalar;total[:,0,0]+=curvature
    result={}
    for name,(i,j)in zip(('K','B_forward','B_reverse','M'),((0,0),(0,1),(1,0),(1,1))):
        result['delta_'+name]=total[:,i,j];result['Maxwell_left_'+name]=left[:,i,j]
        result['Maxwell_right_'+name]=right[:,i,j];result['intrinsic_'+name]=scalar[:,i,j]
    result.update(Maxwell_curvature_contact=curvature,test_lift=T,
        source_gauge=source,source_gauge_coordinate_time=st,source_gauge_radial=sr,source_wall=sw,source_H=sh,source_Hdot=sht,
        target_derivatives=Ee,trial_derivatives=Eo,source_derivatives=Es,gaunt=G,
        source_derivative_orientation_adapter=True,coefficient_direction_conjugated=False,
        physical_current_or_Green_or_loop_or_pole_selected=False)
    return result
