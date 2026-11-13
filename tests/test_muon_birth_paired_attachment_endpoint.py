import numpy as np
from bhsm.interface.muon_parent_gauge_geometry_correction import correction_representation
from bhsm.interface.muon_birth_trace_enriched_action import generic_coordinate_lift
from bhsm.interface.muon_birth_paired_field_endpoint import endpoint_layout
from bhsm.interface.muon_birth_paired_attachment_endpoint import paired_attachment_rows,paired_attachment_jacobian


def fixture():
    rep=correction_representation(radial_points=12,radial_order=2,cap_points=48,include_wall_lift=True)
    coord=generic_coordinate_lift(rep['gauge_labels']);P=coord['lift'];n=coord['x_count'];m=coord['y_count']
    rng=np.random.default_rng(753);C=rng.normal(size=(m,n))/4;A=np.diag(np.linspace(.8,1.4,n))
    h=np.zeros((2*n+m,2*n+m));h[n:2*n,n:2*n]=A;h[2*n:,n:2*n]=C;h[n:2*n,2*n:]=C.T;h[2*n:,2*n:]=.2*np.eye(m)
    def evaluate(raw):
        eta=P.T@raw;g=h@eta
        return dict(value=float(eta@g/2),gradient=g,hessian=h,raw_gradient=P@g,raw_hessian=P@h@P.T)
    raw=np.zeros((2,228));raw[:,37:98]=rng.normal(size=(2,61))/10
    raw[:,100:]=rng.normal(size=(2,128))/20;raw[:,160+coord['At_indices']]=0
    return rep,evaluate,raw


def test_full_paired_canonical_rows_and_implicit_cotangent_match_independent_derivative():
    rep,evaluate,raw=fixture();weights=np.linspace(.8,1.5,98);normalization=np.zeros(37)
    current=paired_attachment_rows(raw,evaluate,rep,weights,normalization)
    J,details=paired_attachment_jacobian(raw,evaluate,rep,weights,current)
    rng=np.random.default_rng(914);d=np.zeros(raw.size);free=endpoint_layout(rep)['all_free'];d[free]=rng.normal(size=len(free))/4;d=d.reshape(raw.shape)
    eps=1e-5
    plus=paired_attachment_rows(raw+eps*d,evaluate,rep,weights,normalization)
    minus=paired_attachment_rows(raw-eps*d,evaluate,rep,weights,normalization)
    np.testing.assert_allclose(J@d.ravel(),(plus['residual']-minus['residual'])/(2*eps),rtol=4e-9,atol=6e-10)
    assert J.shape==(180,456)
    assert all(a['constraint_velocity'].shape==(36,90) for a in current['attachments'])
    assert all(a['saddle'].shape==(128,128) for a in current['attachments'])
    assert max(d['free_weighted_step_halving_relative'] for d in details)<1e-10


def test_full_field_lifts_include_dynamic_gauge_and_higgs_reactions():
    rep,evaluate,raw=fixture();current=paired_attachment_rows(raw,evaluate,rep,np.ones(98),np.zeros(37))
    for a in current['attachments']:
        np.testing.assert_allclose(a['saddle_residual'],0,atol=8e-15)
        np.testing.assert_allclose(a['constraint_annihilation'],0,atol=8e-15)
        assert np.linalg.norm(a['lift'][38:])>0
