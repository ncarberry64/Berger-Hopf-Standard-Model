"""Exact finite action/placement controls; no state or physical pole selected."""
import numpy as np
import pytest
import sympy as sp
from bhsm.interface.muon_changing_coupled_open_current import literal_source_pairings,positive_factor_open_vertices


def test_nonnormal_source_adjoint_before_inverse_and_literal_left():
    # CONTROL_ONLY finite matrices; independent exact algebra.
    A=sp.Matrix([[1,sp.I],[0,2]])
    S=sp.Matrix([[sp.I,1],[-1,-2*sp.I]])
    P=A.H*A+sp.eye(2)
    expected=S*P.inv()*A.H*S
    reversed_order=S*A.H*P.inv()*S
    wrong_left=S.H*P.inv()*A.H*S
    assert expected!=reversed_order and expected!=wrong_left
    av=np.array(A,dtype=complex);s=np.array(S,dtype=complex)
    r=literal_source_pairings(np.eye(2),av,s[None,None],1.)
    np.testing.assert_array_equal(r['left'][:,:,0],s)
    np.testing.assert_array_equal(r['right'][:,:,0],av.conj().T@s)
    result=r['left'][:,:,0]@np.linalg.solve(av.conj().T@av+np.eye(2),r['right'][:,:,0])
    np.testing.assert_allclose(result,np.array(expected,dtype=complex),rtol=1e-14,atol=1e-14)


def test_temporal_factor_vertex_conversion_and_scalar_angular_normalization():
    from bhsm.interface.muon_magnetic_open_lepton_vertex import canonical_open_field_vertices
    from bhsm.interface.muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
    N,R=.7,.9;v=positive_factor_open_vertices(R,N);old=canonical_open_field_vertices(R,N)
    G=lepton_unit_trace_gauge_representation()['generators']
    np.testing.assert_allclose(v['gauge'][0],G/N,rtol=0,atol=3e-16)
    np.testing.assert_array_equal(v['gauge'][1:],old['gauge'][1:])
    np.testing.assert_array_equal(v['scalar'],old['scalar'])
    assert np.linalg.norm(v['gauge'][0]-old['gauge'][0])>1
    np.testing.assert_allclose(v['gauge'][0].conj().transpose(0,2,1),-v['gauge'][0],atol=1e-16)


def test_complete_temporal_product_image_has_real_complement():
    # CONTROL_ONLY exact polynomial half-cell chart; no chosen physical time.
    u=sp.symbols('u',real=True);b=2*u;g=u**2*(1-u)**2
    trial=sp.Matrix([b,b*b]);M=sp.integrate(trial*trial.T,(u,0,sp.Rational(1,2)))
    scalar=b*b;coef=M.inv()*sp.integrate(trial*scalar,(u,0,sp.Rational(1,2)))
    assert sp.expand(scalar-(trial.T*coef)[0])==0
    source=b*g;coef=M.inv()*sp.integrate(trial*source,(u,0,sp.Rational(1,2)))
    residual=sp.integrate((source-(trial.T*coef)[0])**2,(u,0,sp.Rational(1,2)))
    assert residual>0 # dependent ghost product is not b/b², even before variable R/N.


def test_source_pairing_rejects_missing_or_mixed_dimensions():
    with pytest.raises(ValueError,match='same source/trial/action'):
        literal_source_pairings(np.eye(2),np.eye(2),np.zeros((2,1,2,2)),1.)
    with pytest.raises(ValueError,match='same source/trial/action'):
        literal_source_pairings(np.eye(2),np.eye(2),np.full((1,1,2,2),np.nan),1.)
