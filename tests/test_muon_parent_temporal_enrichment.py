import numpy as np
import pytest

from bhsm.interface.muon_parent_gauge_geometry_correction import (
    ROOT,retained_state,correction_representation,coupled_sector_application,
)
import bhsm.interface.muon_parent_gauge_geometry_correction as original
from bhsm.interface.muon_material_higgs_gauge_action import material_intrinsic_higgs_gauge_action_jet
from bhsm.interface.muon_parent_temporal_enrichment import (
    compact_legendre_time_jet,temporal_representation,include_recorded_coefficients,
    temporal_iterate_at_time,temporal_coupled_application,
)


def test_time_jet_preserves_values_rates_and_has_independent_analytic_derivative():
    length=.001
    v,d=compact_legendre_time_jet(np.array([-length,0.]),length,4)
    np.testing.assert_array_equal(v,0.);np.testing.assert_array_equal(d,0.)
    time=np.array([-.00083,-.00041,-.00017]);step=1e-9
    _,d=compact_legendre_time_jet(time,length,4)
    plus,_=compact_legendre_time_jet(time+step,length,4)
    minus,_=compact_legendre_time_jet(time-step,length,4)
    np.testing.assert_allclose(d,(plus-minus)/(2*step),rtol=2e-9,atol=1e-6)


@pytest.fixture(scope='module')
def finite_application():
    args=dict(time_points=3,radial_points=12,radial_order=1,cap_points=12,
        include_wall_lift=True,include_scalar_mean=True)
    rep=temporal_representation(temporal_order=1,**args);base=rep['base'];ref=retained_state(ROOT)
    c=np.zeros(base['count']);c[:37]=1e-7*np.sin(np.arange(37));c[37:61]=1e-7*np.cos(np.arange(24))
    c[61]=2e-8;c[62:base['scalar_start']]=1e-6*np.sin(np.arange(base['gauge_count']))
    c[base['scalar_start']:]=[1e-6,-2e-6,3e-6,-1e-6,.1,.8,-.2,.05]
    # Apply the exact material one-form chart in this independent local
    # reference call; the preserved historical producer is not edited.
    previous=original.intrinsic_higgs_gauge_action_jet
    try:
        original.intrinsic_higgs_gauge_action_jet=material_intrinsic_higgs_gauge_action_jet
        old=coupled_sector_application(c,base,ref,nu_squared_action=4.,surface_gamma=.002)
    finally:original.intrinsic_higgs_gauge_action_jet=previous
    new=temporal_coupled_application(c,rep,ref,nu_squared_action=4.,surface_gamma=.002)
    return args,ref,c,old,new


def test_single_time_mode_reuses_same_action_normalization_and_all_cross_rows(finite_application):
    _,_,_,old,new=finite_application
    assert new['value']==pytest.approx(old['value'],rel=2e-14,abs=1e-16)
    np.testing.assert_allclose(new['residual'],old['residual'],rtol=2e-14,atol=1e-12)
    np.testing.assert_allclose(new['hessian'],old['hessian'],rtol=2e-14,atol=1e-8)
    assert new['constraint_density_max']>0
    total=np.array([moment['multiplier_constraint_density'] for moment in new['moments']])
    split=np.array([moment['cap_multiplier_constraint_density']+
        moment['independent_Maxwell_multiplier_constraint_density']+
        moment['Higgs_assigned_multiplier_constraint_density']+
        .002*moment['surface_multiplier_constraint_density_per_gamma'] for moment in new['moments']])
    np.testing.assert_array_equal(total,split)


def test_enrichment_contains_old_iterate_but_reaches_new_residual_moments(finite_application):
    args,ref,c,old,_=finite_application
    rep=temporal_representation(temporal_order=2,**args);seed=include_recorded_coefficients(c,rep)
    new=temporal_coupled_application(seed,rep,ref,nu_squared_action=4.,surface_gamma=.002)
    mapping=np.r_[np.arange(62),rep['geometry_count']+np.arange(rep['base']['gauge_count']),
        rep['scalar_start']+np.arange(4),np.arange(rep['count']-4,rep['count'])]
    assert new['value']==pytest.approx(old['value'],rel=2e-14)
    np.testing.assert_allclose(new['residual'][mapping],old['residual'],atol=1e-12,rtol=2e-14)
    np.testing.assert_allclose(new['hessian'][np.ix_(mapping,mapping)],old['hessian'],atol=1e-8,rtol=2e-14)
    # New multiplier moment tests see a defect hidden from the single moment.
    assert np.linalg.norm(new['residual'][62+37:62+61])>1e-7


def test_enriched_fields_rates_and_compact_endpoint_constraints_share_one_vector(finite_application):
    args,ref,c,_,_=finite_application
    rep=temporal_representation(temporal_order=3,**args);seed=include_recorded_coefficients(c,rep)
    seed[62:124]=1e-7*np.sin(np.arange(62));seed[rep['geometry_count']+rep['base']['gauge_count']:rep['scalar_start']]=1e-6
    seed[rep['scalar_start']+4:rep['scalar_start']+12]=1e-6
    t=-.00041;step=1e-9
    center=temporal_iterate_at_time(t,seed,rep,ref)
    plus=temporal_iterate_at_time(t+step,seed,rep,ref);minus=temporal_iterate_at_time(t-step,seed,rep,ref)
    np.testing.assert_allclose((plus['q']-minus['q'])/(2*step),center['qdot'],rtol=2e-7,atol=2e-8)
    np.testing.assert_allclose((plus['fields']['gauge']-minus['fields']['gauge'])/(2*step),center['fields']['gauge_tau'],rtol=2e-9,atol=1e-10)
    np.testing.assert_allclose((plus['H_real']-minus['H_real'])/(2*step),center['H_coordinate_time_derivative'],rtol=1e-5,atol=3e-8)
    for t in (-rep['base']['length'],0.):
        end=temporal_iterate_at_time(t,seed,rep,ref)
        np.testing.assert_array_equal(end['q'],ref[0]+t*ref[1])
        np.testing.assert_array_equal(end['qdot'],ref[1])
        np.testing.assert_array_equal(end['m'],ref[2])
