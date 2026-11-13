"""Same-background heat contact on the source-driven true-birth mean.

The chronological canonical mean replaces the earlier per-arm held
initial second response on its represented birth chart.  The finite tent
and numerical cutoff probes remain explicit.  This is not a completed
relative determinant, photon covariance or external Pauli vertex.
"""
from __future__ import annotations
import math
import numpy as np
from flint import arb,ctx

from .muon_primal_cell_native_heat import actual_cell_heat_polynomial,actual_cell_even_y_target
from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation


def _real(value,name):
    if value is None:raise ValueError(name+' required')
    a=np.asarray(value)
    if not np.isrealobj(a) or a.dtype.kind not in 'iuf' or not np.isfinite(a).all():
        raise ValueError(name+' requires finite real point coefficients')
    return np.asarray(a,float)


def raw_mean_export_radii(coordinate_lift,midpoint_radius):
    """Exact selector/permutation lift of the certified future-coordinate radius."""
    P=_real(coordinate_lift,'same coordinate lift');r=_real(midpoint_radius,'certified midpoint export radius')
    if P.ndim!=2 or r.ndim!=3 or P.shape[1]!=len(r) or np.any(r<0):
        raise ValueError('same raw/master maps and nonnegative per-entry radius required')
    # No floating combination is asserted exact: this producer uses one
    # signed coordinate identification per raw row, including zero At_dot.
    if np.any((P!=0)&(abs(P)!=1)) or np.any(np.count_nonzero(P,axis=1)>1):
        raise ValueError('nontrivial coordinate combination requires an interval lift')
    return np.einsum('ij,jab->iab',abs(P),r)


def exact_stored_mean_target_pair(target,mean,radius,*,precision_bits=192):
    """Enclose the saved target applied to the certified discrete mean values."""
    k=_real(target,'reached raw target');m=_real(mean,'actual future raw mean');r=_real(radius,'raw export radius')
    if k.ndim!=1 or m.shape!=(len(k),8,8) or r.shape!=m.shape or np.any(r<0):
        raise ValueError('complete raw target and ordered8x8 certified mean required')
    lower=np.empty((8,8));upper=lower.copy()
    with ctx.workprec(precision_bits):
        kk=[arb(float(v)) for v in k]
        for a in range(8):
            for b in range(8):
                z=arb(0)
                for j in range(len(k)):
                    if k[j]!=0:z+=kk[j]*arb(float(m[j,a,b]),float(r[j,a,b]))
                lower[a,b]=np.nextafter(float(z.lower()),-math.inf)
                upper[a,b]=np.nextafter(float(z.upper()),math.inf)
    return dict(lower=lower,upper=upper,center=np.einsum('i,iab->ab',k,m),
        precision_bits=precision_bits,
        error_scope='exact stored binary target coefficients and certified stored discrete mean export only; target formation/upstream source/action/domain excluded')


def directional_even_y4_estimate(polynomial,target,mean,cutoff):
    """Analytic finite-polynomial directional tail, evaluated without outward rounding."""
    m=_real(mean,'actual raw mean direction');c=float(cutoff)
    if not np.isfinite(c) or c<=0:raise ValueError('explicit shared numerical cutoff required')
    z=[np.einsum('iuv,iab->abuv',polynomial[k],m) for k in
        ('P0_raw_first_jet','P1_raw_first_jet','P2_raw_first_jet')]
    radius=target['finite_matrix_even_Y_circle_radius'];gap=target['numerical_P0_gap'];a=gap/2
    norm=sum(radius**j*np.linalg.norm(v,axis=(-2,-1)) for j,v in enumerate(z))
    Y=np.diag(lepton_current_hilbert_representation()['family_Y']).real
    tail=(Y[1]/radius)**4/(1-(Y[1]/radius)**2)-(Y[2]/radius)**4/(1-(Y[2]/radius)**2)
    return dict(estimate=6*np.exp(-c*a)*norm/a*tail,
        analytic_equation='6 exp(-c gap/2)/(gap/2)*(||deltaP0||+r||deltaP1||+r²||deltaP2||)*paired_even_Y4_tail',
        numerical_circle_radius=radius,numerical_circle_gap=a,
        includes_normalized_Gram_derivative=True,outward_norm_or_operator_assembly_certificate=False)


def chronological_mean_heat_application(raw_base,representation,mean,radius,*,length,cutoff,
                                         direct_source_pair,precision_bits=192):
    """Apply the actual raw mean and combine the source contact/insertions once."""
    base=_real(raw_base,'actual same midpoint base');m=_real(mean,'future raw midpoint mean');r=_real(radius,'raw mean radius')
    direct=np.asarray(direct_source_pair)
    if base.shape!=(268,) or m.shape!=(268,8,8) or r.shape!=m.shape or direct.shape!=(8,8) or not np.isfinite(direct).all():
        raise ValueError('actual complete raw268 base/mean and same-source direct pair required')
    p=actual_cell_heat_polynomial(base,representation,length=length)
    target=actual_cell_even_y_target(p,cutoff,divided_difference_order=16)
    refined=actual_cell_even_y_target(p,cutoff,divided_difference_order=32)
    k=target['paired_middle_minus_light_raw_cotangent']
    certified=exact_stored_mean_target_pair(k,m,r,precision_bits=precision_bits)
    numerical_refinement=np.einsum('i,iab->ab',refined['paired_middle_minus_light_raw_cotangent']-k,m)
    combined=.5*(direct+certified['center'])
    if np.any(m[:,:,3:]) or np.any(m[:,3:,:]) or np.any(direct[:,3:]) or np.any(direct[3:,:]):
        raise ValueError('inactive five magnetic axes must be representation zeros')
    return dict(target=target,refined_target=refined,raw_mean=m,raw_mean_export_radius=r,
        mean_contact=certified['center'],mean_contact_lower=certified['lower'],mean_contact_upper=certified['upper'],
        target_refinement_pair=numerical_refinement,exact_stored_pair_precision_bits=precision_bits,
        direct_source_contact_and_both_insertions=direct,
        graded_direct_plus_chronological_mean=combined,
        graded_mean_contact_lower=.5*certified['lower'],graded_mean_contact_upper=.5*certified['upper'],
        mean_Y4_directional_tail_estimate=directional_even_y4_estimate(p,target,m,cutoff),
        fermion_statistics_factor=.5,statistics_factor_applied_once=True,
        current_birth_mean_source_transferred=True,per_arm_second_mean_initial_held_substituted=False,
        parent_fixed_q_normal_mean_scope=True,physical_full_moving_birth_graph_complete=False,
        completed_relative_native_overlap_or_Pauli=False,physical_a_mu=None,physical_g_mu=None)
