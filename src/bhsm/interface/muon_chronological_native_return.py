"""Apply the birth-composed mean and magnetic direct form to the same action.

This is an interval boundary response on the reached three-axis source
space. It supplies no quantum photon covariance or Pauli promotion.
"""
from __future__ import annotations
import numpy as np
from flint import arb,ctx
from .muon_magnetic_native_return_enclosure import enclosed_magnetic_return


def enclosed_chronological_magnetic_return(bare,direct,mean_lower,mean_upper,*,precision_bits=192):
    """Keep the chronological mean intervals and insert fermion +1/2 once."""
    d=np.asarray(direct);lo=np.asarray(mean_lower);hi=np.asarray(mean_upper)
    if d.shape not in ((3,3),(8,8)) or lo.shape!=d.shape or hi.shape!=d.shape or not np.isrealobj(lo) or not np.isrealobj(hi):
        raise ValueError('actual three-axis or complete padded-eight direct and real chronological mean intervals required')
    if not all(np.isfinite(a).all() for a in (d,lo,hi)) or np.any(lo>hi):
        raise ValueError('finite point direct and ordered real mean bounds required')
    if d.shape==(8,8) and any(np.any(a[3:]) or np.any(a[:,3:]) for a in (d,lo,hi)):
        raise ValueError('five inactive magnetic source axes must remain exact zeros')
    lower=np.zeros((8,8));upper=lower.copy()
    with ctx.workprec(precision_bits):
        for i in range(3):
            for j in range(3):
                a,b=arb(float(lo[i,j])),arb(float(hi[i,j]))
                m=(a+b)/2+arb(0,(b-a)/2)
                value=(arb(float(d[i,j].real))+m)/2
                if not value.is_zero():
                    lower[i,j]=np.nextafter(float(value.lower()),-np.inf)
                    upper[i,j]=np.nextafter(float(value.upper()),np.inf)
    # Exact binary power-of-two scaling of the retained direct rounding;
    # the chronological target and mean are real action coefficients.
    imaginary=np.zeros((8,8));imaginary[:3,:3]=d[:3,:3].imag/2
    a=enclosed_magnetic_return(bare,lower,upper,imaginary,precision_bits=precision_bits)
    a.update(applied_native_real_lower=lower,applied_native_real_upper=upper,
        applied_native_imaginary=imaginary,complex_fermion_statistics_factor=.5,
        statistics_applied_once=True,true_birth_chronological_mean_used=True,
        actual_source_dimension=3,source_inclusion='three physical magnetic axes into padded-eight coefficient representation',
        local_overlap_subtraction_applied=False,
        error_scope='exact stored bare/direct coefficients and certified discrete chronological real mean intervals; direct/target/source formation, continuum, native domain and Pauli matching excluded')
    return a
