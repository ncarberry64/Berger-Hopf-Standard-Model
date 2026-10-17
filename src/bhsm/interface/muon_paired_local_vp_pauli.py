"""Certified on-shell Pauli overlap of the two local lepton current copies.

This evaluates a physical continuum overlap, with the muon external mass
in BOTH graphs. It does not subtract a local graph from an unmatched
finite boundary-source heat matrix. The own-muon VP graph is part of
the frozen mass-independent two-loop coefficient.
"""
from __future__ import annotations
import math
import numpy as np
from flint import acb, arb, ctx


def _outward(value):
    return [float(np.nextafter(float(value.lower()),-math.inf)),
            float(np.nextafter(float(value.upper()),math.inf))]


def certified_vp_coefficient(mass_ratio_decimal,*,precision_bits=192,
                             collar_bits=40,quadrature_bits=70):
    """Enclose 2 int dx(1-x) int dy y(1-y) log(1+r²x²y(1-y)/(1-x)).

    The y integral is exact. Acb integrates its analytic closed expression
    on a finite x collar; explicit positive bounds enclose both omitted
    endpoints. Log and square-root branch cuts are checked by the actual
    integration callback. All supplied decimals are exact central inputs.
    """
    if precision_bits<128 or not 20<=collar_bits<=60 or not 40<=quadrature_bits<precision_bits-40:
        raise ValueError('resolved certified arithmetic and endpoint collars required')
    with ctx.workprec(precision_bits):
        r=arb(str(mass_ratio_decimal))
        if not r>0:raise ValueError('positive exact decimal mass ratio required')
        eps=arb(2)**(-collar_bits);r2=r*r
        def integrand(x,analytic,derivative=False):
            k=acb(r2)*x*x/(1-x)
            v=(1+4/k).sqrt(analytic=analytic)
            root=k.sqrt(analytic=analytic)/2
            L=2*(root+(1+k/4).sqrt(analytic=analytic)).log(analytic=analytic)
            inner=(acb(2)/3-4/k+8*L/(k*k*v)) if derivative else (
                acb(4)/(3*k)-acb(5)/9+(1-2/k)*v*L/3)
            return (1-x)*inner
        options=dict(abs_tol=arb(2)**(-quadrature_bits),rel_tol=arb(2)**(-quadrature_bits),
                     eval_limit=200000,depth_limit=60)
        # Geometric endpoint partitions keep the known logarithmic layer
        # away from a single unnecessarily broad complex integration ball.
        breaks=[eps,arb('0.001'),arb('0.1'),arb('0.5'),arb('0.9'),1-eps]
        totals=[]
        for derivative in (False,True):
            total=acb(0)
            for a,b in zip(breaks,breaks[1:]):
                total+=acb.integral(lambda x,analytic:integrand(x,analytic,derivative),a,b,**options)
            if not total.is_finite() or not total.imag.contains(0):
                raise ArithmeticError('physical real continuum integral not enclosed')
            # log(1+z)<=z at the lower endpoint. At the upper endpoint,
            # integrate u log(1+r²/(4u))/3 and use u<=eps. The mass-ratio
            # derivative of the inner integral is <=2/3 everywhere.
            low=(2 if derivative else 1)*r2*eps**3/45
            high=eps**2/3 if derivative else eps**2*(
                (1+r2/(4*eps)).log()/6+arb(1)/12)
            tail=low+high
            radius=float(np.nextafter(float(tail.upper()),math.inf))
            enclosure=total.real+arb(0,str(radius))
            totals.append((enclosure,tail))
        coefficient,tail=totals[0];derivative,dtail=totals[1]
        return dict(coefficient_interval=_outward(coefficient),
            derivative_log_mass_ratio_interval=_outward(derivative),
            coefficient_ball=str(coefficient),derivative_ball=str(derivative),
            endpoint_tail_upper=float(np.nextafter(float(tail.upper()),math.inf)),
            derivative_endpoint_tail_upper=float(np.nextafter(float(dtail.upper()),math.inf)),
            precision_bits=precision_bits,collar_bits=collar_bits,quadrature_bits=quadrature_bits,
            mass_ratio_decimal=str(mass_ratio_decimal),
            error_scope='rigorous exact-central-decimal continuum quadrature and endpoint tails; measurement, higher-order and native matching errors excluded')


def paired_local_vp_pauli(*,alpha_inverse_decimal,mass_ratio_decimal,
                          precision_bits=192,collar_bits=40,quadrature_bits=70):
    """Actual normalized muon-shell overlap of muon minus electron VP.

    The delta Pi graphs have their Thomson value removed before the
    Pauli integral. On-shell charge/LSZ counterterms of this local sector
    multiply the Dirac tensor annihilated by the existing Pauli covector.
    This assertion does not extend to an uncomputed interacting native
    residue or mixed external-fermion block.
    """
    electron=certified_vp_coefficient(mass_ratio_decimal,precision_bits=precision_bits,
        collar_bits=collar_bits,quadrature_bits=quadrature_bits)
    own_check=certified_vp_coefficient('1',precision_bits=precision_bits,
        collar_bits=collar_bits,quadrature_bits=quadrature_bits)
    with ctx.workprec(precision_bits):
        a=1/arb(str(alpha_inverse_decimal));x2=(a/arb.pi())**2
        own=arb(119)/36-arb.pi()**2/3
        ei=electron['coefficient_interval'];E=arb((ei[0]+ei[1])/2, str((ei[1]-ei[0])/2))
        # Input bounds are outward binary endpoints; constructing the
        # midpoint with binary arithmetic could narrow them, so retain an
        # extra endpoint rounding allowance explicitly.
        E+=arb(0,str(np.finfo(float).eps*max(abs(ei[0]),abs(ei[1]))))
        mu=x2*own;el=x2*E;paired=mu-el
        di=electron['derivative_log_mass_ratio_interval'];D=arb((di[0]+di[1])/2,
            str((di[1]-di[0])/2+np.finfo(float).eps*max(abs(di[0]),abs(di[1]))))
        pair_bounds=_outward(paired)
        checks=own_check['coefficient_interval']
        if not checks[0]<=float(own.mid())<=checks[1]:
            raise ArithmeticError('independent continuum own-loop integral disagrees with exact coefficient')
        return dict(classification='EVALUATED_NORMALIZED_CONTINUUM_PAIRED_LOCAL_VP_PAULI_OVERLAP',
            muon_VP_interval=_outward(mu),electron_VP_interval=_outward(el),
            paired_muon_minus_electron_interval=pair_bounds,
            paired_center=float(paired.mid()),
            derivative_alpha_interval=_outward(2*paired/a),
            derivative_log_muon_electron_ratio_interval=_outward(-x2*D),
            common_positive_VP_sum_upper=float(np.nextafter(float((mu+el).upper()),math.inf)),
            own_muon_exact_coefficient='119/36-pi^2/3',
            independent_own_muon_integral=own_check,electron_integral=electron,
            same_external_mass_shell='muon in both terms; no subtraction of two different external amplitudes',
            pairing='unit charge divided once; calibrated local simple spin-sector pole LSZ',
            regulator='finite Thomson-subtracted local one-loop VP graphs',
            explicit_source_term_forced_into_commutator=False,
            frozen_own_VP_already_in_A1=True,
            native_boundary_form_overlap_subtracted=False,
            complete_disjoint_native_remainder=False,complete_observable=False,
            error_scope='continuum quadrature, exact own coefficient and central-decimal arithmetic; binary export padding included; independent measurement covariance, native completion and higher orders excluded')


def signed_soft_overlap_enclosure(application,t,*,direction_norm_squared=1.):
    """Enclose the normalized signed Pauli derivative, including soft bias.

    Each positive VP spectral measure obeys |F2(rho)-F2(0)|<=rho F2(0)/6.
    Taking the common paired difference before bounding retains its
    zero-transfer correlation; the finite-transfer remainder uses the sum.
    This is a bound, not a fabricated finite-transfer point value.
    """
    t=float(t);d=float(direction_norm_squared)
    if not np.isfinite([t,d]).all() or t==0 or d<=0:
        raise ValueError('signed nonzero transfer and positive direction norm required')
    rho=t*t*d;bias=np.nextafter(rho*application['common_positive_VP_sum_upper']/6,math.inf)
    a,b=application['paired_muon_minus_electron_interval']
    return dict(t=t,rho=rho,normalized_signed_derivative_interval=[
        float(np.nextafter(a-bias,-math.inf)),float(np.nextafter(b+bias,math.inf))],
        paired_soft_bias_upper=float(bias),
        Pauli_normalization='L_u^dagger D=0; L_u^dagger P_u=1; q=t*m_mu*(0,u)',
        finite_transfer_point_evaluated=False,
        error_scope='certified central local paired VP integral plus spectral soft-bias bound only')
