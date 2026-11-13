"""Actual H-selected unit EM source on changing full18 coefficients.

The source is the retained material At current -Q_H/N, with its separate
literal transpose target. This is a supplied-domain current component,
not charge/LSZ normalization or a physical photon/pole selection.
"""
from __future__ import annotations
import numpy as np
from .muon_source_directed_em_normal_current import holomorphic_charge_projection
from .muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
from .muon_continued_action_reality import _higgs_mass_realified
from .muon_holomorphic_current_source import (
    source_varied_unsquared_current_chain,compose_current_components,
    attach_current_chain_first,two_term_complex_sum,
)


def holomorphic_unit_em_moments(H_realified,H_first,lapse,lapse_first):
    """Differentiate both analytic Higgs branches, never conjugating a jet."""
    h=np.asarray(H_realified,complex);dh=np.asarray(H_first,complex)
    N=complex(lapse);dN=np.asarray(lapse_first,complex)
    if h.shape!=(4,)or dh.ndim!=2 or dh.shape[0]!=4 or dN.shape!=(dh.shape[1],)or N==0:
        raise ValueError('same actual realified H, all source tangents and nonzero induced lapse required')
    if not all(np.isfinite(x).all()for x in (h,dh,dN))or not np.isfinite(N):raise ValueError('finite original source coordinates required')
    own=holomorphic_charge_projection(h);s=own['unit_Tr16_charge_coefficients'];n=h@h;dn=2*h@dh
    hp,hm=h[:2]+1j*h[2:],h[:2]-1j*h[2:]
    dp,dm=dh[:2]+1j*dh[2:],dh[:2]-1j*dh[2:]
    P=np.outer(hp,hm)/n
    dP=np.array([(np.outer(a,hm)+np.outer(hp,b))/n-P*c/n for a,b,c in zip(dp.T,dm.T,dn)])
    Q=np.zeros((18,18),complex);Q[:12,:12]=-np.kron(P,np.eye(6));Q[12:,12:]=-np.eye(6)
    dQ=np.zeros((dh.shape[1],18,18),complex);dQ[:,:12,:12]=-np.array([np.kron(a,np.eye(6))for a in dP])
    numer=np.array([2*(h[0]*h[1]+h[2]*h[3]),2*(h[0]*h[3]-h[2]*h[1]),h[0]**2+h[2]**2-h[1]**2-h[3]**2])
    dnumer=np.array([2*(dh[0]*h[1]+h[0]*dh[1]+dh[2]*h[3]+h[2]*dh[3]),
        2*(dh[0]*h[3]+h[0]*dh[3]-dh[2]*h[1]-h[2]*dh[1]),
        2*(h[0]*dh[0]+h[2]*dh[2]-h[1]*dh[1]-h[3]*dh[3])])
    ds=np.zeros((dh.shape[1],4),complex);ds[:,:3]=(-np.sqrt(2)*(dnumer/n-numer[:,None]*dn[None]/n**2)).T
    G=lepton_unit_trace_gauge_representation()['generators']
    J=-Q/N;dJ=-dQ/N+Q[None]*dN[:,None,None]/N**2
    mass=_higgs_mass_realified(h);dmass=np.array([_higgs_mass_realified(a)for a in dh.T])
    return dict(charge=Q,charge_first=dQ,unit_Tr16_coefficients=s,unit_Tr16_coefficients_first=ds,
        literal_right=J,literal_right_first=dJ,literal_left=J.T.copy(),literal_left_first=dJ.swapaxes(-1,-2).copy(),
        charge_idempotence_rows=Q@Q+Q,charge_idempotence_first_rows=dQ@Q+Q@dQ+dQ,
        charge_generator_rows=1j*np.einsum('c,cij->ij',s,G)-Q,
        charge_generator_first_rows=1j*np.einsum('kc,cij->kij',ds,G)-dQ,
        canonical_current_coframe_rows=N*J+Q,
        canonical_current_coframe_first_rows=dN[:,None,None]*J+N*dJ+dQ,
        fixed_Y_mass_charge_rows=Q@mass-mass@Q,
        fixed_Y_mass_charge_first_rows=dQ@mass+Q@dmass-dmass@Q-mass@dQ,
        analytic_Higgs_branches_independent=True,source_direction_conjugated=False,
        physical_charge_or_LSZ_normalized=False)


def independent_current_transpose(components):
    """Independent reverse literal dual of every exact source/target stage."""
    last=components[-1];d=last['trace'].shape[0];nl=last['initial_target'].shape[0]
    k=len(last['trace_first']);nr=last['source_return'].shape[1]
    p=np.zeros((d,nl),complex);dp=np.zeros((k,d,nl),complex)
    current=np.zeros((nl,nr),complex);first=np.zeros((k,nl,nr),complex)
    for a in components[::-1]:
        U,r,L,c=(a[n]for n in ('trace','source_return','initial_target','direct_current'))
        dU,dr,dL,dc=(a[n+'_first']for n in ('trace','source_return','initial_target','direct_current'))
        current+=c+p.T@r
        first+=dc+dp.swapaxes(-1,-2)@r+p.T@dr
        dp=dL.swapaxes(-1,-2)+dU.swapaxes(-1,-2)@p+U.T@dp
        p=L.T+U.T@p
    return dict(current=current,current_first=first,initial_literal_adjoint=p,initial_literal_adjoint_first=dp)


def changing_unit_em_current(steps,stages,H_coordinates,H_coordinate_first):
    """Apply all18 current columns with both source motions and clock/kernel.

    These are unit, constant temporal coordinate tests of the actual
    current. They are not old FE2 coefficients, chosen spin states, or a
    zero transfer physical photon. The defined current J.T A^-1 J has no
    standalone direct density; its changing J/left source is retained.
    """
    q=len(stages);h=np.asarray(steps,complex);hc=np.asarray(H_coordinates,complex);dhc=np.asarray(H_coordinate_first,complex)
    if h.shape!=(q,)or hc.shape!=(q,4)or dhc.shape!=(q,4,2):raise ValueError('same complete two-term changing stages required')
    moments=[holomorphic_unit_em_moments(x,dx,a['induced_lapse'],a['induced_lapse_first'])for x,dx,a in zip(hc,dhc,stages)]
    N=np.array([a['induced_lapse']for a in stages]);dN=np.array([a['induced_lapse_first']for a in stages])
    H=np.array([a['Hcan']for a in stages]);dH=np.array([a['Hcan_first']for a in stages])
    J,L=np.array([a['literal_right']for a in moments]),np.array([a['literal_left']for a in moments])
    dJ,dL=np.array([a['literal_right_first']for a in moments]),np.array([a['literal_left_first']for a in moments])
    z=np.zeros_like(dH);zero=np.zeros_like(H);zclock=np.zeros((q,2),complex)
    args=dict(coordinate_steps=h,lapse=N,body=H,right_source=J,literal_left=L,direct_density=zero,
        coordinate_steps_first=zclock,lapse_first=dN,body_first=dH,right_source_first=dJ,literal_left_first=dL,
        direct_density_first=z,energy=0j,energy_first=np.zeros(2,complex))
    whole=source_varied_unsquared_current_chain(**args)
    pieces={}
    for name,change in (
        ('operator_and_clock',dict(right_source_first=z,literal_left_first=z)),
        ('right_current_motion',dict(lapse_first=zclock,body_first=z,literal_left_first=z)),
        ('left_current_motion',dict(lapse_first=zclock,body_first=z,right_source_first=z))):
        a=source_varied_unsquared_current_chain(**(args|change));pieces[name]=a['direct_current_first']
    components=[]
    for j in range(q):
        own={n:(v[j:j+1]if isinstance(v,np.ndarray)and n not in ('energy_first',)else v)for n,v in args.items()}
        components.append(source_varied_unsquared_current_chain(**own))
    dual=independent_current_transpose(components)
    boundary=dict(initial_boundary=np.eye(18),final_boundary=np.zeros((18,18)),boundary_source=np.zeros((18,18)),
        initial_target=np.zeros((18,18)),final_target=np.zeros((18,18)),direct_current=np.zeros((18,18)))
    attached=attach_current_chain_first(whole,boundary,{n:np.zeros((2,18,18))for n in boundary})
    result={n:np.array([a[n]for a in moments])for n in moments[0]if isinstance(moments[0][n],np.ndarray)}
    result.update(whole_current=attached['current'],whole_current_first=attached['current_first'],
        independent_transpose_current=dual['current'],independent_transpose_current_first=dual['current_first'],
        initial_literal_adjoint=dual['initial_literal_adjoint'],initial_literal_adjoint_first=dual['initial_literal_adjoint_first'],
        boundary_matrix=attached['boundary_matrix'],forced_boundary_source=attached['forced_boundary_source'],
        effective_literal_left=attached['effective_literal_left'],direct_source_return_current=attached['direct_source_return_current'],
        first_placement_sum_rows=sum(pieces.values())-attached['current_first'],
        original_boundary_rows=attached['original_boundary_rows'],original_transpose_rows=attached['original_transpose_rows'])
    result.update({n+'_first':v for n,v in pieces.items()})
    result['current_source_return']=whole['source_return'];result['current_source_return_first']=whole['source_return_first']
    result['current_trace']=whole['trace'];result['current_trace_first']=whole['trace_first']
    for n in ('whole_current_first','operator_and_clock_first','right_current_motion_first','left_current_motion_first'):
        hi,lo=two_term_complex_sum(result[n][0],result[n][1]);result[n+'_combined_high']=hi;result[n+'_combined_low']=lo
    result.update(analytic_left_not_Hilbert_conjugated=True,source_axis_fitted=False,
        standalone_density_zero_only_for_defined_bilinear_current=True,
        all_three_families_and_neutral_fibers_retained=True,
        physical_charge_F1_residue_soft_Pauli_or_external_pole_selected=False)
    return result
