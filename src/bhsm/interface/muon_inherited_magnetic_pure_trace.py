"""Unsquared magnetic transfer operand on the inherited source-on stages.

The represented n0+n1 coordinate transfer is distinct from a current
bilinear and from an exterior pole relation. Every original18 fiber stays.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import expm,expm_frechet
from .muon_holomorphic_n1_magnetic_action import magnetic_angular_trace
from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation


def bind_inherited_magnetic_trace_points(bindings,points):
    """Rebuild actual Xi and its source-first germ before a propagator acts."""
    E=magnetic_angular_trace()['derivative_matrices'];alpha=lepton_current_hilbert_representation()['alpha']
    d=90;k=points['total_field_first'].shape[1];generators=[];first=[];bodies=[]
    for b in bindings:
        s=b['stage'];R=s['R4'].item();N=s['induced_lapse'].item()
        H=np.zeros((d,d),complex);H[:18,:18]=s['Hcan']
        angular=sum(np.kron(a,e)for a,e in zip(alpha,E))
        H[18:,18:]=np.kron(s['Hcan'],np.eye(4))-1j*angular/R
        dH=np.zeros((k,d,d),complex);dH[:,:18,:18]=s['Hcan_first']
        for c in range(k):dH[c,18:,18:]=np.kron(s['Hcan_first'][c],np.eye(4))+1j*angular*s['R4_first'][c]/R**2
        generators.append(-1j*N*H);first.append(-1j*s['induced_lapse_first'][:,None,None]*H-1j*N*dH);bodies.append(H)
    Xi=[];dXi=[];insertions=[];dinsertions=[]
    for i,j in enumerate(points['cell']):
        j=int(j);b=bindings[j];s=b['stage'];N=s['induced_lapse'].item();W=np.r_[b['lifts']['W'],b['lifts']['hv']]
        wall=np.einsum('ca,ahb->chb',W,points['total_field'][i].reshape(84,4,3),optimize=True)
        dwall=np.einsum('ca,kahb->kchb',W,points['total_field_first'][i].reshape(k,84,4,3),optimize=True)
        coeff=np.einsum('chb,cij->bhij',wall,s['canonical_wall_current_vertices'],optimize=True)
        dcoeff=np.einsum('kchb,cij->kbhij',dwall,s['canonical_wall_current_vertices'],optimize=True)
        dcoeff+=np.einsum('chb,kcij->kbhij',wall,s['canonical_wall_current_vertices_first'],optimize=True)
        X=np.zeros((3,d,d),complex);dX=np.zeros((k,3,d,d),complex)
        for a in range(3):
            X[a,18:,:18]=coeff[a].transpose(1,0,2).reshape(72,18)
            X[a,:18,18:]=coeff[a].transpose(1,2,0).reshape(18,72)
            dX[:,a,18:,:18]=dcoeff[:,a].transpose(0,2,1,3).reshape(k,72,18)
            dX[:,a,:18,18:]=dcoeff[:,a].transpose(0,2,3,1).reshape(k,18,72)
        Xi.append(X);dXi.append(dX);insertions.append(-1j*N*X)
        dinsertions.append(-1j*s['induced_lapse_first'][:,None,None,None]*X-1j*N*dX)
    return dict(generators=np.array(generators),generator_first=np.array(first),bodies=np.array(bodies),
        actual_Xi=np.array(Xi),actual_Xi_first=np.array(dXi),insertion=np.array(insertions),insertion_first=np.array(dinsertions),
        cell=np.asarray(points['cell'],int),sigma=np.asarray(points['sigma']),coordinate_weight=1j*np.asarray(points['scale']),
        complete_n0_n1_all18_fibers=True,n1_input_to_n2_image_included=False,
        full_unprojected_n1_fermion_source_image_closed=False)


def pure_unsquared_magnetic_trace_jets(generators,generator_first,coordinate_steps,point_data):
    """U_B=∫U(f,t) deltaB(t) U(t,i)dt and its three source slots.

    No right current or literal left-current moment occurs. The coordinate
    steps and supplied quadrature weights are held; no physical endpoint
    motion, pole or exterior source contacts are assigned zero by this API.
    """
    G,dG,h=map(np.asarray,(generators,generator_first,coordinate_steps))
    cell,sigma,weight=(np.asarray(point_data[n])for n in('cell','sigma','coordinate_weight'))
    I,dI=(np.asarray(point_data[n],complex)for n in('insertion','insertion_first'))
    n,d,_=G.shape;k=dG.shape[1];q=len(cell);axes=I.shape[1]
    if n!=2 or G.shape!=(n,d,d)or dG.shape!=(n,k,d,d)or h.shape!=(2,)or I.shape!=(q,axes,d,d)or dI.shape!=(q,k,axes,d,d):
        raise ValueError('same complete two-stage generators and independent source-first point maps required')
    if sigma.shape!=(q,)or weight.shape!=(q,)or any(not np.isfinite(a).all()for a in(G,dG,h,sigma,weight,I,dI)):
        raise ValueError('finite original stage/source/time maps required')
    if any(int(j)!=j or j<0 or j>=n or 2*s-j < -1e-13 or 2*s-j>1+1e-13 for j,s in zip(cell,sigma)):
        raise ValueError('every point belongs to its actual complete stage interval')
    def segment(j,dt):
        out=[];U=None
        for c in range(k):
            value,derivative=expm_frechet(dt*G[j],dt*dG[j,c])
            if U is None:U=value
            out.append(derivative)
        if U is None:U=expm(dt*G[j])
        return U,np.array(out).reshape(k,d,d)
    full=[segment(j,h[j])for j in range(n)]
    U=full[1][0]@full[0][0]
    dU=full[1][1]@full[0][0]+full[1][0]@full[0][1]
    UB=np.zeros((axes,d,d),complex);slots={name:np.zeros((k,axes,d,d),complex)for name in('left_propagator','insertion','right_propagator')}
    transpose=np.zeros_like(UB)
    for i,j in enumerate(cell):
        j=int(j);local=2*sigma[i]-j
        right,dr=segment(j,local*h[j]);left,dl=segment(j,(1-local)*h[j])
        for earlier in range(j-1,-1,-1):
            dr=dr@full[earlier][0]+right@full[earlier][1];right=right@full[earlier][0]
        for later in range(j+1,n):
            dl=full[later][1]@left+full[later][0]@dl;left=full[later][0]@left
        UB+=weight[i]*(left@I[i]@right)
        transpose+=weight[i]*(right.T@I[i].transpose(0,2,1)@left.T)
        for c in range(k):
            slots['left_propagator'][c]+=weight[i]*(dl[c]@I[i]@right)
            slots['insertion'][c]+=weight[i]*(left@dI[i,c]@right)
            slots['right_propagator'][c]+=weight[i]*(left@I[i]@dr[c])
    mixed=sum(slots.values())
    return dict(full_unsquared_transfer=U,full_unsquared_transfer_first=dU,magnetic_transfer=UB,magnetic_transfer_first=mixed,
        **{'magnetic_transfer_first_'+name:v for name,v in slots.items()},
        independent_literal_transpose_magnetic_transfer=transpose,
        literal_transpose_identity_defect=transpose-UB.transpose(0,2,1),
        physical_boundary_or_pole_or_source_current_normalization_selected=False,
        current_Jtranspose_inverse_J_not_substituted=True,
        coordinate_interval_and_point_weights_held=True)
