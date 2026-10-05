"""Node3 normalized-input kinetic actions and native attachment obstruction.

These are actions of the saved canonical M4 geometric/common-A reference
on the actual radial projection. They are not Pi4 D_strat iota_j. No
unprovided Higgs/normal/domain row is set to zero or added to the parent.
"""
from __future__ import annotations
import numpy as np


def normalized_input_maps(point, receipt, radial_weights, radius):
    """Use cached functions and their owned action jets, not a new profile."""
    mu4=2*np.pi**2*radius**3
    w=radial_weights;u=point['u'];p=point['p']
    moments=lambda measure:np.array([w@(measure*u*u),w@(measure*u*p),w@(measure*p*p)])
    volume=moments(point['volume']);cauchy=moments(point['Cauchy'])
    I=float(np.mean(receipt['I']['interval']));Idot=float(np.mean(receipt['I_tau']['interval']))
    kappa=1/np.sqrt(2*I)
    return dict(M4=mu4,volume_moments=volume,Cauchy_moments=cauchy,
        B_volume=np.array([1.,receipt['bulk_B']]),
        B_volume_tau=np.array([0.,receipt['bulk_B_tau']]),
        B_Cauchy=np.array([1.,receipt['Cauchy_B']]),
        B_Cauchy_tau=np.array([0.,receipt['Cauchy_B_tau']]),
        material_trace=np.array([kappa,0.]),
        material_trace_tau=np.array([-kappa*Idot/(2*I),0.]),
        volume_adjoint_residual=volume[1]-mu4*receipt['bulk_B'],
        volume_isometry_quadrature_residual=volume[0]-mu4,
        Cauchy_adjoint_residual=cauchy[1]-cauchy[0]*receipt['Cauchy_B'])


def intrinsic_reference_rows(basis,carrier,radius,H,shape_v,B,B_tau):
    """Actual n1/n3 actions, including the derivative of the B input map.

    The saved common-frame wall symbol is iGamma0(d_tau+3H/2)
    + angular/r + S_S3/r + b_g GaugeUnit. Boundary proper lapse is
    exactly one by its clock convention. No normal boost is inserted.
    All64 spin/carrier output rows and both source angular levels survive.
    """
    G=carrier['common_parent_Gamma']
    bg=-1/(radius*(1+np.exp(4*shape_v)))
    zero=1.5*H*1j*G[0]+carrier['angular_spin']/radius+bg*carrier['commonA_gauge_unit']
    rows={};F0=[];F1=[];inputs=[]
    for n,xi in basis.items():
        E=carrier[f'angular_E_n{n}']
        angular=sum(np.einsum('oi,imkj,vm->ovkj',1j*G[a+1],xi,E[a]) for a in range(3))
        r0=np.einsum('oi,imkj->omkj',zero,xi)+angular/radius
        rt=np.einsum('oi,imkj->omkj',1j*G[0],xi)
        w0=B[0]*r0+B_tau[0]*rt;wt=B[0]*rt
        p0=B[1]*r0+B_tau[1]*rt;pt=B[1]*rt
        rows.update({f'kinetic_reference_W_0_n{n}':w0,f'kinetic_reference_W_tau_n{n}':wt,
            f'kinetic_reference_p_0_n{n}':p0,f'kinetic_reference_p_tau_n{n}':pt,
            f'normalized_wall_W_input_n{n}':B[0]*xi,f'normalized_wall_p_input_n{n}':B[1]*xi,
            f'normalized_wall_p_input_tau_n{n}':B_tau[1]*xi})
        flat=lambda a:a.reshape(-1,a.shape[-1])
        F0.append(np.concatenate((flat(w0),flat(p0)),axis=1))
        F1.append(np.concatenate((flat(wt),flat(pt)),axis=1))
        inputs.append(np.concatenate((flat(B[0]*xi),flat(B[1]*xi)),axis=1))
    return dict(**rows,F0=np.concatenate(F0),F1=np.concatenate(F1),
        normalized_inputs=np.concatenate(inputs),wall_bg_reference=bg,
        radius=np.array(radius),H=np.array(H),shape_v=np.array(shape_v))


def intrinsic_reference_gram(rows,M4):
    """Only the known kinetic-reference Gram; NOT an additive native Gram."""
    F0,F1,E=rows['F0'],rows['F1'],rows['normalized_inputs']
    return dict(kinetic_reference_A=M4*(F0.conj().T@F0),
        kinetic_reference_B=M4*(F0.conj().T@F1),
        kinetic_reference_C=M4*(F1.conj().T@F1),
        normalized_input_mass=M4*(E.conj().T@E))


def graph_complement(B,M5,M4,wall_vector):
    """Weighted obstruction to using a bounded projection as full domain.

    In canonical independent H5 plus H4, (-B^sharp z,z) is orthogonal
    to every (x,Bx). This is an actual-input check of the general identity,
    not a substitute finite operator or a heat calculation.
    """
    Bsharp=np.linalg.solve(M5,B.conj().T@M4)
    left=-Bsharp@wall_vector
    annihilator=left.conj().T@M5+wall_vector.conj().T@M4@B
    return dict(B_sharp=Bsharp,graph_orthogonal_bulk=left,
        graph_orthogonal_wall=wall_vector,graph_annihilator=annihilator,
        graph_orthogonal_norm_squared=np.real(np.vdot(left,M5@left)+np.vdot(wall_vector,M4@wall_vector)))
