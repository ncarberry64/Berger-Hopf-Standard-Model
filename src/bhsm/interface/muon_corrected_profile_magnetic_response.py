"""Magnetic Euler/Gauss applications on the corrected normal/profile phase.

The radial/time/spatial inherited connection image is applied before the
literal Lorentz weak Hessian.  This finite retarded application is distinct
from the positive ADM field reference, quantum covariance, and soft LSZ.
"""
from __future__ import annotations
import numpy as np
from scipy.interpolate import CubicHermiteSpline

from .muon_parent_positive_coupled_field import corrected_positive_parent_reference
from .muon_parent_maxwell_corrected_retarded import full_constant_angular_hessian,intrinsic_scalar_trace_hessian
from .muon_reached_trace_action import moving_trace_time_forms,moving_trace_gauge_rows,sampled_reached_form
from .muon_parent_maxwell_full_retarded import constrained_gauss_schur
from .muon_parent_retarded_hypercharge import regular_radial_basis,WALL
from .muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from .muon_electromagnetic_soft_magnetic_source import uniform_magnetic_source_first_jets,magnetic_point_jet
from .muon_profile_preserving_phase_sample import profile_preserving_raw_sample


def corrected_wall_reference(raw,representation,*,coordinate_time,initial_pair=None,reference_pair=None):
    """Exact wall value/time/radial image in the same material chart."""
    rep=dict(representation);rep['rho']=np.array([WALL]);rep['radial_quadrature']=np.ones(1)
    rep['gauge_basis']=np.moveaxis(rep['wall_trace_map'],-1,0)[None,:,None]
    rep['gauge_radial_basis']=np.moveaxis(rep['wall_radial_derivative_map'],-1,0)[None,:,None]
    return corrected_positive_parent_reference(raw,rep,coordinate_time=coordinate_time,
        initial_pair=initial_pair,reference_pair=reference_pair)


def corrected_profile_reached_sample(raw,representation,angular,trace,trace_rate,*,
        coordinate_time,nu_squared_action,initial_pair=None,reference_pair=None):
    """Literal full488 Lorentz action, with its full inherited first germ.

    All80 algebraic At rows are kept until the actual joint Gauss Schur.
    The source400 map and rate act before reduction; scalar relative8 is
    the retained common cap normalization.  No positive form is substituted.
    """
    x=np.asarray(raw);Q=np.asarray(trace);Qt=np.asarray(trace_rate);nu=float(nu_squared_action)
    if (x.shape!=(268,) or any(not np.isrealobj(a) or not np.isfinite(a).all() for a in (x,Q,Qt))
            or Q.shape!=(400,8) or Qt.shape!=Q.shape or np.any(Q[:160]) or np.any(Qt[:160])
            or not np.isfinite(nu) or nu<0):
        raise ValueError('complete real raw268/spatial400 source and explicit Higgs parameter required')
    kw=dict(coordinate_time=coordinate_time,initial_pair=initial_pair,reference_pair=reference_pair)
    ref=corrected_positive_parent_reference(x,representation,**kw)
    A=ref['background_values'];At=ref['background_time_derivatives'];Ar=ref['background_radial_derivatives']
    local=[full_constant_angular_hessian(a,at,ar,d) for a,at,ar,d in
        zip(A,At,Ar,ref['positive_two_form_densities'])]
    radial,radial_rate=regular_radial_basis(ref['rho'],1)
    E=np.concatenate((np.eye(20)[None],np.asarray(angular['derivative_matrices'])))
    products=np.array([[a.T@b for b in E] for a in E])
    forms=moving_trace_time_forms(np.array([a['tensor'] for a in local]),ref['radial_weights'],radial,radial_rate,Q,Qt,products)
    idx=np.r_[np.arange(400),np.arange(480,488)];matrices=[]
    for old in forms:
        new=np.zeros((488,488));new[np.ix_(idx,idx)]=old;matrices.append(new)
    wall=corrected_wall_reference(x,representation,**kw)
    weights=intrinsic_m4_weight_jet(12,x[:37],x[37:74],x[74:98],source_value=x[98],source_rate=x[99])
    coeff=np.array([weights[k].value for k in ('wT','wS','wV')])
    scalar=intrinsic_scalar_trace_hessian(x[-8:-4],x[-4:],wall['background_values'][0],coeff,
        lambda_H=representation['scalar_matching']['lambda_H'],nu_squared_action=nu,angular=angular)['matrix']
    value=np.zeros((560,488));velocity=np.zeros_like(value)
    value[:80,400:480]=np.eye(80);value[80:480,480:]=Q;velocity[480:,400:480]=np.eye(80)
    scalar_forms=(8*velocity.T@scalar@velocity,8*value.T@scalar@velocity,8*value.T@scalar@value)
    matrices=[a+b for a,b in zip(matrices,scalar_forms)]
    rows=moving_trace_gauge_rows(local,A,ref['radial_weights'],radial,radial_rate,Q,Qt,E)
    expanded=np.zeros((4,80,488));expanded[:,:,:400]=rows[:,:,:400];expanded[:,:,480:]=rows[:,:,400:]
    return dict(raw_forms=tuple(matrices),reduced=constrained_gauss_schur(*matrices,80),
        scalar_forms=scalar_forms,gauge_weak_rows=expanded,source=Q,source_rate=Qt,raw_fields=x.copy(),
        full_background_values=np.array([A,At,Ar]),wall_background_values=wall['background_values'][0],
        inherited_profile_value_time_radial=ref['inherited_profile_value_time_radial'],
        scalar_Maxwell_relative_normalization=8.,all_moving_trace_contacts_retained=True,
        inherited_connection_count=1,extra_connection_Ar_advection_count=0,
        exact_normal_geometry_applied=True,physical_free_wall_inverse=False,physical_Pauli_value=False)


def corrected_magnetic_source_sample(phase,coordinate_time,angular,*,electric_charge):
    """Bind analytic physical local-B jets to one actual corrected phase."""
    sample=profile_preserving_raw_sample(phase,coordinate_time);raw=sample['raw_fields']
    kwargs={}
    if phase['receipt']['side']=='outgoing':
        kwargs=dict(initial_pair=phase['arrays']['initial_pair'],reference_pair=phase['arrays']['reference_pair'])
    source=uniform_magnetic_source_first_jets(raw,angular,electric_charge=electric_charge)
    wall=corrected_wall_reference(raw,phase['representation'],coordinate_time=coordinate_time,**kwargs)
    weights=intrinsic_m4_weight_jet(12,raw[:37],raw[37:74],raw[74:98],source_value=raw[98],source_rate=raw[99])
    if abs(source['R4']-weights['R4'].value)>2e-14*source['R4']:
        raise ArithmeticError('magnetic source and corrected intrinsic wall radius differ')
    source['local_point_jet']=magnetic_point_jet(source,angular,wall['background_values'][0,2:])
    action=corrected_profile_reached_sample(raw,phase['representation'],angular,
        source['connection_source'],source['connection_source_rate'],coordinate_time=coordinate_time,
        nu_squared_action=phase['receipt']['action_parameters']['nu_squared_action'],**kwargs)
    return dict(source=source,action=action,raw_sample=sample)


def corrected_magnetic_sampled_form(times,samples,*,duration):
    """One numerical unreduced action interpolation and consistent Q/Qdot.

    Matrix samples are cubic interpolated before Gauss, as in the retained
    action core.  Q uses its analytic node rates in one Hermite polynomial;
    exported Qdot is its derivative.  The between-node action-production
    interpolation error is explicitly outside this numerical solve.
    """
    form=sampled_reached_form(times,samples,duration=duration)
    q=CubicHermiteSpline(np.asarray(times),np.array([s['source'] for s in samples]),
        np.array([s['source_rate'] for s in samples]))
    form['source_map']=q;form['source_rate_map']=q.derivative()
    form['source_rate_is_derivative_of_supplied_source_interpolation']=True
    form['inherited_profile_retained_before_action_and_Gauss']=True
    return form
