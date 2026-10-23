import numpy as np
from bhsm.interface.muon_parent_gauge_geometry_correction import correction_representation
from bhsm.interface.muon_birth_paired_field_endpoint import paired_field_endpoint_rows,endpoint_layout


def action_fixture():
    rng=np.random.default_rng(9124);M=rng.normal(size=(228,9));K=M@M.T/100+np.diag(np.linspace(.7,1.3,228));b=rng.normal(size=228)/10
    def action(x):return dict(value=float(x@K@x/2+b@x),raw_gradient=K@x+b,raw_hessian=K)
    return action


def test_whole_paired_constraint_energy_trace_and_dual_jacobian_is_independent_derivative():
    rep=correction_representation(radial_points=12,radial_order=2,cap_points=48,include_wall_lift=True)
    rng=np.random.default_rng(71);raw=rng.normal(size=(2,228))/7;weights=np.linspace(.8,1.5,98);d=rng.normal(size=(2,228))/3
    app=paired_field_endpoint_rows(raw,action_fixture(),rep,weights);eps=1e-5
    p=paired_field_endpoint_rows(raw+eps*d,action_fixture(),rep,weights)
    m=paired_field_endpoint_rows(raw-eps*d,action_fixture(),rep,weights)
    np.testing.assert_allclose(app['jacobian']@d.reshape(-1),(p['residual']-m['residual'])/(2*eps),rtol=3e-9,atol=3e-10)
    assert app['residual'].shape==(178,)
    assert app['jacobian'].shape==(178,456)


def test_temporal_parent_child_covectors_have_opposite_sign_without_density_reapplication():
    rep=correction_representation(radial_points=12,radial_order=2,cap_points=48,include_wall_lift=True)
    raw=np.zeros((2,228));raw[0,224:228]=[.2,.4,-.1,.3];raw[1,224:228]=[-.3,.1,.6,.5]
    def action(x):
        G=np.zeros(228);G[224:228]=2*x[224:228];H=np.zeros((228,228));H[224:228,224:228]=2*np.eye(4)
        return dict(value=float(x[224:228]@x[224:228]),raw_gradient=G,raw_hessian=H)
    a=paired_field_endpoint_rows(raw,action,rep,np.ones(98))
    np.testing.assert_array_equal(a['residual'][174:178],2*(raw[0,224:228]-raw[1,224:228]))
    assert not a['physical_fullfield_junction_closed']


def test_all_At_Gauss_are_kept_but_At_rates_have_no_free_kinetic_coordinates():
    rep=correction_representation(radial_points=12,radial_order=2,cap_points=48,include_wall_lift=True)
    layout=endpoint_layout(rep)
    assert len(layout['free'])==177 and len(layout['all_free'])==354
    assert set(100+layout['At']).issubset(layout['free'])
    assert not set(160+layout['At']).intersection(layout['free'])
    assert set(np.arange(220,228)).issubset(layout['free'])
