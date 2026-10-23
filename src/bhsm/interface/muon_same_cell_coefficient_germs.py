"""Owned coefficient time germs for source-directed weak-action enrichment.

These are derivatives of the declared affine saved cell, including the
inherited parent/reference clock. They are not a continuous Euler solution.
The algebraic temporal potential is held at its solved midpoint, rather
than importing the distinct physical first-germ At into this interpolation.
"""
from __future__ import annotations
import numpy as np
from .muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from .muon_birth_inherited_finite_normal_phase import affine_geometry_germ
from .muon_birth_finite_normal_trace_graph import affine_connection_profile_two_jet
from .muon_inherited_lepton_temporal_weak_action import inherited_cell_raw_at_time
from .muon_birth_trace_enriched_action import generic_coordinate_lift
from .muon_parent_retarded_hypercharge import WALL


def _affine_rate(raw):
    out=np.zeros_like(raw);out[:37]=raw[37:74];out[98]=raw[99]
    return out


def _product(a,b):
    return np.array([a[0]*b[0],a[1]*b[0]+a[0]*b[1],
        a[2]*b[0]+2*a[1]*b[1]+a[0]*b[2]])


def _inverse(a):
    if a[0]<=0:raise ValueError('positive owned metric coefficient required')
    return np.array([1/a[0],-a[1]/a[0]**2,2*a[1]**2/a[0]**3-a[2]/a[0]**2])


def coefficient_germs(raw,raw_coordinate_rate,time,*,initial_pair=None,reference_pair=None):
    """Values, future-coordinate first/second derivatives on one affine cell.

    ``kappa_wall=lambda-1+inherited_profile0`` is the complete mechanical
    spatial connection coefficient, counted once. Independent Ai/H motion
    remains a separate source placement; At has zero interpolation rate
    because its algebraic slot is held, not because the physical At_t is zero.
    """
    raw=np.asarray(raw,float);rate=np.asarray(raw_coordinate_rate,float);t=float(time)
    if (raw.ndim!=1 or len(raw)<108 or rate.shape!=raw.shape or
            not np.isfinite(raw).all() or not np.isfinite(rate).all() or not np.isfinite(t)):
        raise ValueError('same finite raw cell and its affine coefficient rate required')
    w=intrinsic_m4_weight_jet(12,raw[:37],raw[37:74],raw[74:98],
        source_value=raw[98],source_rate=raw[99])
    def apply(jet):return np.array([float(jet.value),float(jet.gradient@rate[:100]),
        float(rate[:100]@jet.hessian@rate[:100])])
    R=apply(w['R4']);N=apply(w['induced_lapse']);lam=apply(w['mechanical_connection_lambda'])
    profile=np.zeros(3);explicit=np.zeros(3)
    if (initial_pair is None)!=(reference_pair is None):raise ValueError('both inherited pairs required')
    if initial_pair is not None:
        initial=np.asarray(initial_pair,float);reference=np.asarray(reference_pair,float)
        if initial.shape!=(2,len(raw)) or reference.shape!=initial.shape:
            raise ValueError('same full inherited initial and reference pairs required')
        parent=affine_geometry_germ(initial[0],t)
        refs=np.array([affine_geometry_germ(a,t)for a in reference])
        p=affine_connection_profile_two_jet(np.array([parent,raw]),np.array([WALL]))
        r=affine_connection_profile_two_jet(refs,np.array([WALL]))
        dp=np.r_[_affine_rate(initial[0])[:100],rate[:100]]
        dr=np.concatenate([_affine_rate(a)[:100]for a in reference])
        dc=np.r_[_affine_rate(initial[0])[:100],np.zeros(100)]
        profile=np.array([p['value'][0,0]-r['value'][0,0],
            p['first'][0,0]@dp-r['first'][0,0]@dr,
            dp@p['second'][0,0]@dp-dr@r['second'][0,0]@dr])
        explicit=np.array([0.,p['first'][0,0]@dc-r['first'][0,0]@dr,
            dp@p['second'][0,0]@dc-dr@r['second'][0,0]@dr])
    k=lam+profile;k[0]-=1
    invR=_inverse(R);invN=_inverse(N)
    germs=dict(R4=R,N=N,mechanical_lambda=lam,inherited_profile=profile,kappa_wall=k,
        inverse_R4=invR,inverse_N=invN,kappa_over_R4=_product(k,invR))
    return dict(germs=germs,explicit_inherited_clock=explicit,
        explicit_inherited_clock_order=('no separate value','fixed-child clock first',
            'along-cell derivative of fixed-child clock first'),
        raw_fields=raw,raw_coordinate_time_derivative=rate,
        coordinate_time=t,inherited_connection_count=1,
        derivative_order=('value','future_coordinate_first','future_coordinate_second'),
        proper_time_first={name:float(a[1]/N[0])for name,a in germs.items()},
        interpolation='same x-linear/vy-midpoint cell and affine parent/reference first germs',
        algebraic_At_interpolation_rate_zero_provenance='the owned cell holds v/y; this is not a claim about the physical first-germ At_t',
        physical_history_or_cutoff_or_Pauli_selected=False)


def same_cell_coefficient_germs(stage_raw,stage_time,time,representation,*,
        initial_pair=None,reference_pair=None):
    """Use exactly the existing phase lift before applying coefficient jets."""
    raw=inherited_cell_raw_at_time(stage_raw,stage_time,time,representation)
    c=generic_coordinate_lift(representation['gauge_labels']);P=c['lift'];n=c['x_count']
    eta=P.T@np.asarray(stage_raw);rate=P[:,:n]@eta[n:2*n]
    return coefficient_germs(raw,rate,time,initial_pair=initial_pair,reference_pair=reference_pair)


def divided_coefficient_germs(evaluate,time,anchor,*,quadrature_order=12):
    """Integrate f' to represent (f(t)-f(anchor))/(t-anchor) stably.

    This retains tiny analytic directions without subtracting close values
    or declaring sampled singular vectors exact nulls. The integral is a
    Gauss evaluation of the owned derivative, not an outward enclosure.
    The continuous t=anchor value is the actual first derivative.
    """
    t,a=float(time),float(anchor)
    if not np.isfinite([t,a]).all() or type(quadrature_order)is not int or quadrature_order<2:
        raise ValueError('finite same-cell times and explicit Gauss order required')
    if t==a:return {name:float(g[1])for name,g in evaluate(a)['germs'].items()}
    z,w=np.polynomial.legendre.leggauss(quadrature_order)
    samples=[evaluate(a+(t-a)*(x+1)/2)['germs']for x in z]
    return {name:float(sum(weight*s[name][1]for weight,s in zip(w,samples))/2)
        for name in samples[0]}
