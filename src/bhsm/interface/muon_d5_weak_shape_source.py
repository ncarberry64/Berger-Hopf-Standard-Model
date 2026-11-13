"""Density and principal contacts of a direct D5 coefficient source."""
import numpy as np


def fixed_radial_d5_weak_source(point_source,volume,volume_first,weights,
        radial_values,radial_first,*,time_Clifford):
    """Integrate delta(mu D), with every original fixed radial test retained.

    The declared coordinate basis B(rho)I has V_t=0 identically and does
    not vary with the source. This is a computational test basis, not a
    physical normal inclusion or a claim its first derivative is zero.
    """
    mu,dm,w=np.asarray(volume,complex),np.asarray(volume_first,complex),np.asarray(weights,float)
    B,Br=np.asarray(radial_values,complex),np.asarray(radial_first,complex);G0=np.asarray(time_Clifford,complex)
    D,dD,R,dR=(np.asarray(point_source[k],complex)for k in('original_D5_zero_order','direct_source_D5_zero_order','original_D5_radial_principal','direct_source_D5_radial_principal'))
    q,d,_=D.shape
    if D.shape!=(q,d,d)or dD.shape!=D.shape or R.shape!=D.shape or dR.shape!=D.shape or mu.shape!=(q,)or dm.shape!=mu.shape or w.shape!=mu.shape or B.shape[0]!=q or Br.shape!=B.shape or G0.shape!=(d,d):
        raise ValueError('same full original point coefficients, density and every fixed radial test required')
    nr=B.shape[1];K=np.zeros((nr*d,nr*d),complex);dK=np.zeros_like(K)
    for i in range(q):
        for m in range(nr):
            for n in range(nr):
                acted=D[i]*B[i,n]+R[i]*Br[i,n]
                first=dD[i]*B[i,n]+dR[i]*Br[i,n]
                rows=slice(m*d,(m+1)*d);cols=slice(n*d,(n+1)*d)
                K[rows,cols]+=w[i]*mu[i]*B[i,m]*(G0@acted)
                dK[rows,cols]+=w[i]*B[i,m]*(G0@(dm[i]*acted+mu[i]*first))
    return dict(original_fixed_radial_weak_action=K,direct_shape_fixed_radial_weak_action=dK,
        volume_density_coefficient_source=dm,all_fixed_radial_and_opposite_Spin_rows_retained=True,
        fixed_coordinate_trial_time_derivative_exactly_zero=True,
        physical_normal_inclusion_and_trace_source_not_selected=True)
