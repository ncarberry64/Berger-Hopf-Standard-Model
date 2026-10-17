"""Actual magnetic factor/current jets on the corrected changing phase.

The open-current vertex is differentiated together with its dependent
gauge-orbit field chart. The factor's temporal gauge vertex is the
anti-Hermitian positive-factor placement, not its Lorentz Hamiltonian
counterpart. Both angular parities and the required n5 return are kept.
"""
from __future__ import annotations
from functools import lru_cache
import numpy as np

from .muon_intrinsic_scalar_discretization import scalar_s3_discretization
from .muon_coupled_higgs_magnetic_source import coupled_intrinsic_wall_images,_multiplication
from .muon_changing_coupled_open_current import positive_factor_open_vertices
from .muon_corrected_profile_magnetic_response import corrected_wall_reference
from .muon_parent_maxwell_corrected_retarded import _ad,higgs_u2_real_representation
from .muon_profile_preserving_phase_sample import profile_preserving_lepton_sample
from .muon_parent_positive_brst_ghost import ghost_radial_values,smooth_ghost_temporal_values
from .muon_parent_retarded_hypercharge import WALL


@lru_cache(maxsize=1)
def magnetic_current_angular_images():
    """Complete even35/odd56 product maps for the represented field loops."""
    s=scalar_s3_discretization(5);labels=s['real_basis_labels']
    ids={key:np.array([i for i,l in enumerate(labels)if l[0]in ns])for key,ns in
        dict(even=(0,2,4),odd=(1,3,5),field_odd=(1,3),source=(1,)).items()}
    v={k:s['real_basis_values'][:,i]for k,i in ids.items()};w=s['haar_weights']
    product=(v['odd'][:,:,None]*v['source'][:,None,:]).reshape(len(w),-1)
    G=(v['even'].T@(w[:,None]*product)).reshape(35,56,4)
    ne=np.array([labels[i][0]for i in ids['even']])[:,None,None]
    no=np.array([labels[i][0]for i in ids['odd']])[None,:,None]
    ns=np.array([labels[i][0]for i in ids['source']])[None,None,:]
    forbidden=(ne<abs(no-ns))|(ne>no+ns)|((ne+no+ns)%2!=0)
    # These entries are forbidden by exact representation degree. No
    # small numerical allowed coefficient is discarded.
    G[forbidden]=0
    reverse=(v['even'][:,:,None]*v['source'][:,None,:]).reshape(len(w),-1)
    remainder=reverse-v['odd']@G.transpose(1,0,2).reshape(56,-1)
    return dict(gaunt_even_odd_source=G,
        even_times_source_to_complete_odd_residual=float(np.sqrt(np.max(np.sum(w[:,None]*remainder**2,axis=0)))),
        derivatives={k:s['real_angular_derivative_matrices'][:,i][:,:,i]for k,i in ids.items()},
        labels={k:[labels[i]for i in a]for k,a in ids.items()},
        odd_field_indices=np.arange(20),full_odd_return_harmonics=56,
        source_image_proof='even n4 times source/external n1 reaches odd n5; odd n5 to even n6 cannot return through the represented n1 external and n1/n3 field loop')


def field_current_direction(base,gaunt,source_gauge,source_H):
    """Literal source motion of D_A eta and -T(eta)H in the current.

    Independent gauge and scalar coefficient columns have zero chart
    variation. The dependent DG columns vary by [a,eta] and -T(eta)h.
    This is chart motion, not an omitted independent physical field.
    """
    G=np.asarray(gaunt);a=np.asarray(source_gauge);h=np.asarray(source_H)
    no=base['harmonic_count'];ne=G.shape[0];mo=base['count']
    if (G.ndim!=3 or G.shape[1]!=no or a.shape!=(5,4,G.shape[2])or h.shape!=(4,G.shape[2])
            or any(not np.isrealobj(x)or not np.isfinite(x).all()for x in(G,a,h))):
        raise ValueError('same complete real field-chart source product required')
    ma=np.array([_multiplication(np.moveaxis(np.array([_ad(x)for x in f.T]),0,-1),G)for f in a])
    T=higgs_u2_real_representation()['real_generators'];mul_h=_multiplication(np.einsum('cij,js->ics',T,h),G)
    dW=np.zeros((5,4*ne,mo));dh=np.zeros((4*ne,mo))
    t,r=base['temporal'],base['radial']
    for p in range(2):
        g=t[2+2*p]
        for k in range(2):
            sl=slice(40*no+(2*p+k)*4*no,40*no+(2*p+k+1)*4*no)
            dW[:,:,sl]=g*r[k,0]*ma
            dh[:,sl]=-g*r[k,0]*mul_h
    return np.concatenate((dW.reshape(20*ne,mo),dh)).reshape(24,ne,mo)


def magnetic_open_current_point(phase,response_time,*,length,first_field_sampler,include_maps=True):
    """Evaluate factor Xi and both current-chart motions on actual fields.

    Geometry is held fixed in this reached angular gauge/H field direction.
    N/R vertex and fermion-Gram derivatives are consequently zero here;
    this is not a claim about the full coupled metric variation.
    """
    L=float(length);u=float(response_time)
    if not np.isfinite([L,u]).all()or L<=0 or u<0 or u>L or abs(phase['receipt']['span'])!=L:
        raise ValueError('same finite chronological source clock required')
    t=u-L if phase['receipt']['side']=='incoming'else u
    a=profile_preserving_lepton_sample(phase,float(t));op=a['operator'];raw=a['sample']['raw_fields']
    kw={}
    if phase['receipt']['side']=='outgoing':kw=dict(initial_pair=phase['arrays']['initial_pair'],reference_pair=phase['arrays']['reference_pair'])
    wall=corrected_wall_reference(raw,phase['representation'],coordinate_time=float(t),**kw)['background_values'][0]
    source=first_field_sampler(u,np.array([WALL]));images=magnetic_current_angular_images()
    if np.any(source['wall_gauge'][...,4:])or np.any(source['H'][...,4:])or np.any(source['Hdot'][...,4:]):
        raise ValueError('nonzero source n3 requires a larger current return image')
    g=smooth_ghost_temporal_values(np.array([u]),L)[0];b=2*min(u/L,1-u/L);bp=2/L if u<L/2 else-2/L
    tf=np.array([b,bp,g[0,0],g[0,1],g[1,0],g[1,1]]);r=ghost_radial_values(np.array([WALL]))[0]
    G=images['gaunt_even_odd_source'];eo=images['derivatives']['field_odd'];ee=images['derivatives']['even']
    vertices=positive_factor_open_vertices(op['R4'],op['N'])
    V=np.concatenate((vertices['gauge'].reshape(20,18,18),vertices['scalar']))
    coefficients=np.concatenate((source['wall_gauge'][:3,:,:,:4].reshape(3,20,4),source['H'][:3,:,:4]),axis=1)
    Xi=np.einsum('Ach,cij->Ahij',coefficients,V)
    # The reverse directed angular source uses the same coefficient vertex;
    # its adjoint must be taken literally (At is anti-Hermitian).
    result=dict(Xi_source_coefficients=Xi,
        Xi_source_coefficient_adjoints=Xi.conj().transpose(0,1,3,2),
        vertices=V,N=op['N'],R4=op['R4'],W=op['W'],Omega_tau=op['Omega_tau'],raw_fields=raw,
        wall_connection=wall,wall_radial_image=r,
        source_wall_gauge=source['wall_gauge'][:3],source_H=source['H'][:3],source_Hdot=source['Hdot'][:3],
        response_time=u,coordinate_time=float(t),temporal_image=tf,
        factor_temporal_vertex='positive At = G/N = i times the Lorentz Hcan At vertex; no second material advection',
        fermion_Gram_source_derivative_exact_zero_in_this_fixed_geometry_direction=True,
        full_metric_response_not_assigned_zero=True,physical_P_strat_LSZ_Pauli_completed=False)
    if include_maps:
        bo=coupled_intrinsic_wall_images(wall,raw[-8:-4],raw[-4:],eo,tf,r)
        be=coupled_intrinsic_wall_images(wall,raw[-8:-4],raw[-4:],ee,tf,r)
        field=lambda base:np.concatenate((base['gauge'].reshape(20*base['harmonic_count'],base['count']),base['scalar'])).reshape(24,base['harmonic_count'],base['count'])
        result.update(odd_field_wall_maps=field(bo),even_field_wall_maps=field(be),
            delta_odd_field_wall_maps=np.array([field_current_direction(bo,G[:,:20],source['wall_gauge'][j,:,:,:4],source['H'][j,:,:4])for j in range(3)]),
            delta_even_field_wall_maps=np.array([field_current_direction(be,G.transpose(1,0,2),source['wall_gauge'][j,:,:,:4],source['H'][j,:,:4])for j in range(3)]))
    return result
