import numpy as np

from bhsm.interface.muon_birth_full_field_attachment import constrained_attachment_lift,attachment_momentum_variation
from bhsm.interface.muon_magnetic_birth_mean_rows import attachment_paired_source,weighted_row_surjection,paired_mean_field_rows


def test_paired_source_saddle_contact_agrees_with_independent_implicit_derivative():
    n=3;m=1;H=np.diag([2.,3.,4.,4.,2.,3.,1.])
    H[6,3:6]=H[3:6,6]=np.array([.3,-.2,.6])
    g=np.array([.3,.7,-.2,.4,.5,-.6,.1]);B=np.eye(3)[:2]
    base=constrained_attachment_lift(dict(gradient=g,hessian=H),B,dynamic_count=n,algebraic_count=m)
    random=np.random.default_rng(429);dh=random.normal(size=(7,7));dh=(dh+dh.T)/2
    dg=random.normal(size=7)
    independent=attachment_momentum_variation(base,dg,dh)['momentum_variation']
    a=attachment_paired_source(base,dg[:,None,None],lambda d,s:(dh@d)[:,None,None],
        coordinate_weights=np.ones(7))
    np.testing.assert_allclose(a['momentum_source'][:,0,0],independent,rtol=2e-14,atol=2e-14)
    assert np.linalg.norm(a['paired_hessian_saddle_contact'])>0


def test_surjection_keeps_every_row_and_exports_the_actual_null_space():
    J=np.array([[1.,2.,0.,1.],[0.,1.,3.,-1.]])
    source=np.array([[.3,-.4],[.7,.2]]);row=np.array([2.,.5]);weight=np.array([.7,1.2,2.,.4])
    a=weighted_row_surjection(J,source,row,weight)
    np.testing.assert_allclose(J@a['correction']+source,0.,atol=2e-15)
    np.testing.assert_allclose((J/weight)@a['normalized_null_basis'],0.,atol=2e-15)
    assert a['spectral_directions_removed']==0
    # The weighted particular is orthogonal to every represented null.
    np.testing.assert_allclose(a['normalized_null_basis'].T@(weight[:,None]*a['correction']),0.,atol=2e-15)


def test_all_constraint_energy_trace_and_oriented_dual_source_rows_have_owned_order():
    from bhsm.interface.muon_parent_maxwell_full_weak import FIELD_ORDER
    labels=[dict(field=f,internal=k) for f in FIELD_ORDER for k in range(4)]
    rep=dict(gauge_labels=labels);nr=148
    g=np.arange(2*nr,dtype=float).reshape(2,nr,1,1);energy=np.array([.25,-.5])[:,None,None]
    weights=np.ones(98);weights[74:]=2.
    f=paired_mean_field_rows(g,energy,rep,weights)[:,0,0]
    np.testing.assert_array_equal(f[:24],g[0,74:98,0,0]/2)
    np.testing.assert_array_equal(f[24:28],g[0,100:104,0,0])
    assert f[28]==.25 and f[57]==-.5
    np.testing.assert_array_equal(f[58:74],0.)
    np.testing.assert_array_equal(f[74:90],g[0,124:140,0,0]-g[1,124:140,0,0])
    np.testing.assert_array_equal(f[90:94],0.)
    np.testing.assert_array_equal(f[94:],g[0,144:148,0,0]-g[1,144:148,0,0])
