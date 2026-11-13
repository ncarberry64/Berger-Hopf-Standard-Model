import numpy as np
from bhsm.interface.muon_d5_recharted_pole_domain import (
    rechart_regular_frame,propagate_recharted_regular_frame,sew_regular_pole_rows,
)


def test_rechart_preserves_every_amplitude_and_source_transition():
    Y=np.array([[.4,.1],[.3,1.2],[1.1,-.2],[-.1,.7]],complex)
    Yx=np.array([[.1,.03],[-.02,.04],[.01,-.03],[.2,-.1]],complex)
    a=np.array([[.7,-.2],[.4,.8]]);ax=np.array([[.1,.3],[-.2,.1]])
    c=rechart_regular_frame(Y,Yx);Q,Qx,T,Tx=(c[k] for k in
        ('value','source','amplitude_transition','amplitude_transition_source'))
    np.testing.assert_allclose(Q@T@a,Y@a,atol=3e-16)
    np.testing.assert_allclose(Qx@T@a+Q@Tx@a+Q@T@ax,Yx@a+Y@ax,atol=3e-16)
    np.testing.assert_allclose(Q[c['pivot_rows']],np.eye(2),atol=2e-16)


def test_original_sewn_rows_retain_both_boundary_and_state_variations():
    B=np.array([[1.,-.3,.2],[.1,.4,-.7]])
    Bx=np.array([[-.1,.2,.05],[.3,-.2,.1]])
    V=np.arange(12).reshape(3,4)/17;Vx=np.flip(V,axis=1)/3
    rows=sew_regular_pole_rows(B,Bx,V,Vx)
    np.testing.assert_allclose(rows['source_rows'],Bx@V+B@Vx)
    # Independent physical state variation uses its original V coefficient,
    # rather than being deleted as a numerical boundary chart freedom.
    np.testing.assert_array_equal(rows['independent_state_source_coefficient'],B@V)


def test_each_original_stage_retains_all_regular_columns_after_rechart():
    bounds=np.array([.1,.2,.3]);G=np.zeros((2,3,4,4),complex);Gx=G.copy()
    seed=np.array([[1.,0.],[.2,1.],[.3,.4],[.5,-.2]],complex)
    sx=np.zeros_like(seed)
    app=propagate_recharted_regular_frame(bounds,G,Gx,seed,sx)
    assert app['slopes'].shape==(2,3,4,2)
    np.testing.assert_allclose(app['final_frame']@app['transitions'][1]@app['transitions'][0],seed,atol=3e-16)
    np.testing.assert_allclose(app['stage_rows'],0,atol=0)
    np.testing.assert_allclose(app['source_reconstruction_rows'],0,atol=0)
