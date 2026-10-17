"""Actual signed D3S field operands on the original natural84 n1 layout.

The field source is already the TOTAL response, including its prescribed
wall lift and induced Higgs. All geometry/metric coefficients are supplied
by the same stage binding and held in this field-direction derivative.
"""
from __future__ import annotations
import numpy as np
from .muon_literal_wall_magnetic_action import (
    maxwell_magnetic_coefficient_tensors, intrinsic_magnetic_hessian_block,
)
from .muon_parent_mean_causal_action import MAXWELL_TO_CAP


def signed_n1_magnetic_point_operands(binding,total_field,coordinate_rate,
        even_derivatives,odd_derivatives,source_derivatives,gaunt):
    """D3S[actual source, even trial, odd trial] in value/rate placements.

    Field order is the binding's At-first84, harmonic-minor. Inputs are
    (336,3), outputs (3,840,336), for even n0+n2 and odd/source n1. Source
    value/time/radial germs are formed with P/Pt/Pr, and wall H/Hdot with
    W/hv. The source-only transpose adapter below repairs the old API's
    E.T contraction without changing even/odd operator placements or old
    source bytes. These are Lorentz-coordinate action coefficients; any
    temporal/proper-clock pullback and boundary source are caller operations.
    """
    row=binding['row'];lifts=binding['lifts']
    f,ft=np.asarray(total_field,complex),np.asarray(coordinate_rate,complex)
    Ee,Eo,Es,G=[np.asarray(x) for x in(even_derivatives,odd_derivatives,source_derivatives,gaunt)]
    if (f.shape!=(336,3)or ft.shape!=f.shape or Ee.shape!=(3,10,10)
            or Eo.shape!=(3,4,4)or Es.shape!=(3,4,4)or G.shape!=(10,4,4)
            or any(not np.isrealobj(x)for x in(Ee,Eo,Es,G))
            or any(not np.isfinite(x).all()for x in(f,ft,Ee,Eo,Es,G))):
        raise ValueError('complete source3×n1 and real even0/2, odd/source1 Gaunt action maps required')
    P,Pr,Pt,W,hv=[np.asarray(lifts[k],complex)for k in('P','Pr','Pt','W','hv')]
    nr=len(P);quad=np.asarray(lifts['radial_weights'],float)
    if (P.shape!=(nr,20,84)or Pr.shape!=P.shape or Pt.shape!=P.shape
            or W.shape!=(20,84)or hv.shape!=(4,84)or quad.shape!=(nr,)
            or row['A'].shape!=(nr,5,4)or row['densities'].shape!=(nr,5)
            or not np.isfinite(quad).all()):
        raise ValueError('same full four-radial84 lift and signed stage density required')
    coefficients=f.reshape(84,4,3);rates=ft.reshape(84,4,3)
    source=np.einsum('ram,mhb->rahb',P,coefficients,optimize=True).reshape(nr,5,4,4,3)
    source_time=np.einsum('ram,mhb->rahb',Pt,rates,optimize=True).reshape(nr,5,4,4,3)
    source_radial=np.einsum('ram,mhb->rahb',Pr,coefficients,optimize=True).reshape(nr,5,4,4,3)
    source_wall=np.einsum('am,mhb->ahb',W,coefficients,optimize=True).reshape(5,4,4,3)
    source_H=np.einsum('am,mhb->ahb',hv,coefficients,optimize=True)
    source_Hdot=np.einsum('am,mhb->ahb',hv,rates,optimize=True)
    ep=np.r_[np.eye(10)[None],Ee];op=np.r_[np.eye(4)[None],Eo]
    left_angular=np.array([[ep[p].T@G[:,:,h]for h in range(4)]for p in range(4)])
    right_angular=np.array([[G[:,:,h]@op[p]for h in range(4)]for p in range(4)])
    maxwell=[];intrinsic=[];off_shell=[]
    # Old source-coefficient APIs index Es[k,h] rather than Es[h,k].
    # ONLY their source input is adapted; trials keep owned E operators.
    source_api_E=Es.transpose(0,2,1)
    def scalar_lifts(n):
        v=np.zeros((28*n,84*n),complex);t=v.copy();I=np.eye(n)
        v[:4*n]=np.kron(hv,I);v[4*n:24*n]=np.kron(W,I)
        t[24*n:]=np.kron(hv,I)
        return v,t
    Se=scalar_lifts(10);So=scalar_lifts(4)
    for axis in range(3):
        L=np.zeros((2,2,4,84,84,4),complex);R=L.copy()
        for r in range(nr):
            maps=np.zeros((2,3,20,84),complex)
            maps[0,0]=P[r];maps[0,2]=Pr[r];maps[1,1]=Pt[r]
            tensor=maxwell_magnetic_coefficient_tensors(row['A'][r],source[r,:,:,:,axis],
                source_time[r,:,:,:,axis],source_radial[r,:,:,:,axis],row['densities'][r],source_api_E)
            factor=MAXWELL_TO_CAP*quad[r]
            L+=factor*np.einsum('uiam,ijpabh,vjbn->uvpmnh',maps,tensor['left'],maps,optimize=True)
            R+=factor*np.einsum('uiam,ijpabh,vjbn->uvpmnh',maps,tensor['right'],maps,optimize=True)
            # Curvature-contact derivative has only value/value trial slots.
            L[0,0,0]+=factor*np.einsum('am,abh,bn->mnh',P[r],tensor['contact'],P[r],optimize=True)
        gauge=(np.einsum('uvpmnh,pheo->uvmeno',L,right_angular,optimize=True)
            +np.einsum('uvpmnh,pheo->uvmeno',R,left_angular,optimize=True)).reshape(2,2,840,336)
        h=intrinsic_magnetic_hessian_block(row['wall_A'],row['H'],row['Hdot'],
            source_wall[:,:,:,axis],source_H[:,:,axis],source_Hdot[:,:,axis],row['weights'],
            Ee,Eo,source_api_E,G,lambda_H=row['lambda_H'],nu_squared_action=row['nu_squared_action'])
        scalar=np.array([[Se[i].T@h['hessian']@So[j]for j in range(2)]for i in range(2)])
        contact=np.array([[Se[i].T@h['off_shell_DH_contact']@So[j]for j in range(2)]for i in range(2)])
        maxwell.append(gauge);intrinsic.append(scalar);off_shell.append(contact)
    maxwell=np.asarray(maxwell);intrinsic=np.asarray(intrinsic);allblocks=maxwell+intrinsic
    names=('K','B_forward','B_reverse','M');places=((0,0),(0,1),(1,0),(1,1))
    result={}
    for name,(i,j)in zip(names,places):
        result['delta_'+name]=allblocks[:,i,j]
        result['Maxwell_delta_'+name]=maxwell[:,i,j]
        result['intrinsic_delta_'+name]=intrinsic[:,i,j]
        result['intrinsic_off_shell_DH_delta_'+name]=np.asarray(off_shell)[:,i,j]
    result.update(total_source_field=f,total_source_coordinate_rate=ft,
        source_gauge=source,source_gauge_coordinate_time=source_time,source_gauge_radial=source_radial,
        source_wall_gauge=source_wall,source_H=source_H,source_H_coordinate_time=source_Hdot,
        even_derivatives=Ee,odd_derivatives=Eo,source_derivatives=Es,gaunt_even_odd_source=G,
        value_permutation=np.asarray(binding['value_permutation']),
        source_only_derivative_orientation_adapter=True,
        both_signed_angular_placements_retained=True,
        full_Maxwell_curvature_and_intrinsic_DH_Hdot_potential_contacts_retained=True,
        prescribed_wall_not_added_twice=True,source_coefficients_conjugated=False,
        temporal_clock_or_weak_boundary_not_chosen=True,
        field_derivative_holds_supplied_geometry_and_parameters=True,
        whole_metric_or_exterior_or_physical_P_strat_variation_not_assigned_zero=True,
        physical_pole_LSZ_or_Pauli_identified=False)
    return result
