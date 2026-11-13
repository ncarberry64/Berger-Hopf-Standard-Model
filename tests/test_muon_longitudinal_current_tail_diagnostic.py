"""CONTROL_ONLY algebra and coefficient-map checks, no state selection."""
import numpy as np
import pytest
import sympy as sp

from bhsm.interface.muon_longitudinal_current_tail_diagnostic import (
    central_longitudinal_vector,central_gauge_current_ward_point,
)
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
from bhsm.interface.muon_native_dirac_hamiltonian import fixed_y_higgs_hamiltonian
from bhsm.interface.muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
from bhsm.interface.muon_native_product_factor_graph import lepton_unit_trace_gauge_representation


def test_tent_has_exact_nonzero_complement_to_the_owned_ghost_bubbles():
    u=sp.symbols('u',real=True);g=u**2*(1-u)**2
    d=2*sp.integrate(2*u*g,(u,0,sp.Rational(1,2)))
    q=sp.integrate(g*g,(u,0,1));norm=2*sp.integrate((2*u)**2,(u,0,sp.Rational(1,2)))
    # The antisymmetric bubble has zero pairing with the symmetric tent.
    assert sp.integrate((2*u-1)*g*g,(u,0,1))==0
    assert d==sp.Rational(11,480)
    assert norm-d*d/q==sp.Rational(19,7680)
    assert -d/q==-sp.Rational(231,16)


def test_full_actual_representation_ward_identity_keeps_external_euler_contact():
    # Supplied finite operands are CONTROL_ONLY; the retained action
    # representation, including fixed Yukawa and U1 charge, is the owner.
    raw=np.zeros(268);raw[-8:-4]=[.3,.7,-.2,.4]
    H=raw[-8:-6]+1j*raw[-6:-4]
    mass=fixed_y_higgs_hamiltonian(H[None])[0]
    op=dict(N=.8,R4=.7,W=mass,Omega_tau=np.zeros((18,18),complex))
    r=central_gauge_current_ward_point(raw,op,eta=.23,eta_rate=-.11,external_value=.4,external_rate=.7)
    np.testing.assert_allclose(r['source_identity_residual'],0,atol=2e-17)
    np.testing.assert_allclose(r['external_ward_residual'],0,atol=8e-17)
    np.testing.assert_allclose(r['spatial_source_identity_residual'],0,atol=2e-16)
    assert np.linalg.norm(r['external_Euler_contact'])>.01
    assert not r['physical_on_shell_annihilation_proved']


def test_longitudinal_coordinates_use_exact_casimir_and_no_eigenvector_deletion():
    E=retained_full_q_angular_space()['derivative_matrices']
    z,q=central_longitudinal_vector(E,0,1)
    assert q==pytest.approx(3.,abs=2e-14)
    assert np.sum(z*z)==pytest.approx(1.,abs=2e-14)
    assert not z[:400].any()and not z[800:].any()
    # All three angular components, in the literal central internal slot.
    for field in range(5):
        for internal in range(4):
            row=z[400+field*80+internal*20:400+field*80+(internal+1)*20]
            if field<2 or internal!=3:assert not row.any()


def test_clifford_current_norm_is_casimir_normalized_without_high_shell_subtraction():
    # This exact represented identity fixes the leading direct current norm:
    # sum_h ||sum_i alpha_i G (E_i Y)_h/sqrt(q)||_F²=||G||_F².
    E=retained_full_q_angular_space()['derivative_matrices']
    alpha=lepton_current_hilbert_representation()['alpha']
    G=lepton_unit_trace_gauge_representation()['generators'][3]
    for h in range(20):
        grad=E[:,:,h];q=np.sum(grad*grad)
        current=np.einsum('aij,ah->hij',alpha@G,grad)/np.sqrt(q)
        assert np.sum(abs(current)**2)==pytest.approx(np.sum(abs(G)**2),rel=2e-14)

