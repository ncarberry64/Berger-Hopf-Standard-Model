"""Actual magnetic variation of the intrinsic-Higgs positive cell form.

The odd n1+n3 scalar block is not closed under the external source.
This module keeps its complete even product image and both derivative
placements.  The existing tent, midpoint coefficients and action Gram
are retained.  No full quantum domain, statistics or pole is assigned.
"""
from __future__ import annotations
from functools import lru_cache
import numpy as np
from .muon_intrinsic_scalar_discretization import scalar_s3_discretization
from .muon_intrinsic_higgs_positive_green import intrinsic_higgs_cell_jacobi
from .muon_parent_maxwell_corrected_retarded import higgs_u2_real_representation


@lru_cache(maxsize=2)
def _product_space(source_maximum):
    if source_maximum not in (1,3):
        raise ValueError('complete retained source shell n1 or n1+n3 required')
    maximum=3+source_maximum
    s=scalar_s3_discretization(maximum)
    labels=s['real_basis_labels']
    oi=np.array([i for i,l in enumerate(labels) if l[0] in (1,3)])
    ei=np.array([i for i,l in enumerate(labels) if l[0]%2==0])
    si=np.array([i for i,l in enumerate(labels) if l[0] in (1,3) and l[0]<=source_maximum])
    O,E,S=(s['real_basis_values'][:,i] for i in (oi,ei,si))
    w=s['haar_weights']
    # Haar normalized Gaunt coefficients; no physical S3 volume here.
    products=(O[:,:,None]*S[:,None,:]).reshape(len(w),-1)
    G=(E.T@(w[:,None]*products)).reshape(len(ei),len(oi),len(si))
    remainder=products-E@G.reshape(len(ei),-1)
    residual=np.sqrt(np.sum(w[:,None]*remainder**2,axis=0)).reshape(len(oi),len(si))
    derivatives=s['real_angular_derivative_matrices']
    return dict(gaunt_even_odd_source=G,
        odd_harmonic_labels=[labels[i] for i in oi],
        even_harmonic_labels=[labels[i] for i in ei],
        source_harmonic_labels=[labels[i] for i in si],
        odd_derivative_matrices=derivatives[:,oi][:,:,oi],
        even_derivative_matrices=derivatives[:,ei][:,:,ei],
        source_derivative_matrices=derivatives[:,si][:,:,si],
        odd_basis_values=O,even_basis_values=E,source_basis_values=S,
        Haar_weights=w,su2_points=s['su2_points'],
        scalar_product_image_residual=residual,
        quadrature_polynomial_degree=s['quadrature_polynomial_degree'],
        exact_representation_image='Peter-Weyl n_source*n_odd contains |n_source-n_odd|,...,n_source+n_odd in steps2',
        image_residual_scope='evaluated quadrature/representation rounding; not outward enclosure')


def higgs_magnetic_source_image_space(angular,wall_gauge,H_source):
    """Choose the exact product image from supplied retained source support.

    Exact all-zero n3 coordinates permit n0/n2/n4; any nonzero n3
    coordinate retains n6 too.  No numerical threshold deletes a mode.
    Source directions and maps are real coefficient fields, not states.
    """
    a,h=np.asarray(wall_gauge),np.asarray(H_source)
    if (not np.isrealobj(a) or not np.isrealobj(h) or a.ndim!=4 or
        a.shape[1:]!=(5,4,20) or h.shape!=(len(a),4,20) or
        not np.isfinite(a).all() or not np.isfinite(h).all() or len(a)==0):
        raise ValueError('complete real magnetic wall gauge and H80 directions required')
    labels=angular['harmonic_labels']
    n3=np.array([i for i,l in enumerate(labels) if l[0]==3])
    if len(labels)!=20 or len(n3)!=16:
        raise ValueError('retained complete real n1+n3 angular frame required')
    pure=not (np.any(a[:,:,:,n3]) or np.any(h[:,:,n3]))
    space={k:(v.copy() if isinstance(v,np.ndarray) else
              list(v) if isinstance(v,list) else v)
           for k,v in _product_space(1 if pure else 3).items()}
    if space['odd_harmonic_labels']!=labels:
        raise ValueError('product map and retained angular frames differ')
    source_ids=np.array([i for i,l in enumerate(labels) if l[0]<= (1 if pure else 3)])
    return dict(space,source_wall_gauge=a[:,:,:,source_ids].copy(),
        source_H=h[:,:,source_ids].copy(),
        source_n3_exactly_zero=bool(pure),source_maximum_level=1 if pure else 3,
        source_support_reduction_rule='bit-exact zero coordinates only; no norm/eigenvalue deletion')


def intrinsic_higgs_positive_source_application(raw_fields,representation,angular,*,
                                               length,first_wall_gauge,first_H):
    """Differentiate the literal real-linear Jacobi on its full source image.

    For each covariant derivative D, delta(D^T D)_eo is
    D_e^T deltaD_eo + deltaD_oe^T D_o, with deltaD_oe^T=-deltaD_eo.
    The potential derivative is lambda[4(deltaH H^T+H deltaH^T)
    +4(H dot deltaH)I].  The unchanged constant-coefficient tent has
    no temporal derivative of these frozen midpoint coefficient fields.
    """
    base=intrinsic_higgs_cell_jacobi(raw_fields,representation,angular,length=length)
    image=higgs_magnetic_source_image_space(angular,first_wall_gauge,first_H)
    E=image['even_derivative_matrices'];no=20;ne=len(image['even_harmonic_labels'])
    G=image['gaunt_even_odd_source'];T=higgs_u2_real_representation()['real_generators']
    dt=base['material_temporal_connection'][::no,::no]
    omega=np.array([base['covariant_angular_derivative'][i,::no,::no]
        -np.eye(4)*angular['derivative_matrices'][i,0,0] for i in range(3)])
    Dte=np.kron(dt,np.eye(ne))
    Dse=np.array([np.kron(np.eye(4),E[i])+np.kron(omega[i],np.eye(ne)) for i in range(3)])
    from .muon_current_source_motion_cubic import current_face_source_jets
    weights=current_face_source_jets(np.asarray(raw_fields)[:100])['intrinsic_weights']
    wt,ws,wv=(weights[k].value for k in ('wT','wS','wV'))
    potential_internal=base['potential'][::no,::no]
    Pe=(12*wt/(wv*float(length)**2))*np.eye(4*ne)
    Pe+=(wt/wv)*(Dte.T@Dte)+(ws/wv)*sum(D.T@D for D in Dse)+np.kron(potential_internal,np.eye(ne))
    dtime=[];dspace=[];dpotential=[]
    H=np.asarray(raw_fields)[-8:-4];lam=base['scalar_matching']['lambda_H']
    for a,h in zip(image['source_wall_gauge'],image['source_H']):
        multiplication=np.einsum('fcq,ijq->fcij',a,G)
        dD=np.einsum('fcij,cuv->fuivj',multiplication,T).reshape(5,4*ne,4*no)
        dtime.append((wt/wv)*(Dte.T@dD[0]-dD[0]@base['material_temporal_connection']))
        dspace.append((ws/wv)*sum(Dse[i].T@dD[2+i]-dD[2+i]@base['covariant_angular_derivative'][i] for i in range(3)))
        dU=np.array([lam*(4*(np.outer(h[:,q],H)+np.outer(H,h[:,q]))+4*(H@h[:,q])*np.eye(4)) for q in range(h.shape[1])])
        dpotential.append(np.einsum('quv,ijq->uivj',dU,G).reshape(4*ne,4*no))
    dtime,dspace,dpotential=map(np.asarray,(dtime,dspace,dpotential))
    derivative=dtime+dspace+dpotential
    return dict(image,positive_H_odd=base['operator'],positive_H_even=Pe,
        delta_positive_H_even_odd=derivative,
        delta_temporal_connection_even_odd=dtime,delta_spatial_even_odd=dspace,
        delta_potential_even_odd=dpotential,
        action_Gram_scalar=base['action_Gram_scalar'],
        delta_action_Hessian_even_odd=base['action_Gram_scalar']*derivative,
        background_real_H=H.copy(),scalar_matching=base['scalar_matching'],
        same_action_real_pairing='real2Re; raw intrinsic S4/V², unit Haar timesV once',
        source_temporal_scope='actual sampled source fields held as cell coefficients; no full source-history differential complement claim',
        temporal_derivative_projection_scope='int b² bprime=0 for this projected source moment only',
        both_covariant_derivative_placements_retained=True,
        source_odd_geometry_component_included=False,
        complete_graded_quantum_Sigma_or_Pauli_assigned=False,
        physical_a_mu=None,physical_g_mu=None)
