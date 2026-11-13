"""Independent literal action checks; synthetic fixtures are CONTROL_ONLY."""
from pathlib import Path
import numpy as np
import pytest
from bhsm.interface.muon_literal_euclidean_wall_action import (
    intrinsic_natural_wall_hessian,natural_wall_lorentz_forms)
from bhsm.interface.muon_intrinsic_higgs_gauge_action import intrinsic_higgs_gauge_action_jet
from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import Jet


def test_control_literal_scalar_all_crosses_against_independent_jet_action():
    # CONTROL_ONLY: all components and Hdot are deliberately nonzero.
    H=np.array([.4,-.8,.2,.3]);Hd=np.array([-.1,.2,.3,-.4])
    A=np.arange(20).reshape(5,4)/57-.12;w=np.array([1.2,.8,1.7])
    V=np.zeros((1,4,8));D=np.zeros((1,4,4,8));V[0,:,:4]=np.eye(4);D[0,0,:,4:]=np.eye(4)
    weights={k:Jet.constant(float(v),0)for k,v in zip(('wT','wS','wV'),w)}
    weights.update(mechanical_connection_lambda=Jet.constant(1.,0),wall_rate=Jet.constant(0.,0))
    expected=intrinsic_higgs_gauge_action_jet(weights,scalar_coefficients=np.r_[H,Hd],
        scalar_value_map=V,scalar_derivative_map=D,gauge_coefficients=A.ravel(),
        gauge_trace_map=np.eye(20).reshape(1,5,4,20),angular_quadrature=np.ones(1),
        lambda_H=.13,nu_squared_action=4.)['action'].hessian/(2*np.pi**2)**2
    order=np.r_[np.arange(4),np.arange(8,28),np.arange(4,8)]
    actual=intrinsic_natural_wall_hessian(A,H,Hd,np.zeros((3,1,1)),metric_weights=w,
        lambda_H=.13,nu_squared_action=4.)
    np.testing.assert_allclose(actual['hessian'],expected[np.ix_(order,order)],rtol=3e-15,atol=3e-17)
    assert np.linalg.norm(actual['off_shell_DH_contact'])>.01
    without_rate=intrinsic_natural_wall_hessian(A,H,np.zeros(4),np.zeros((3,1,1)),metric_weights=w,
        lambda_H=.13,nu_squared_action=4.)
    assert np.linalg.norm(actual['hessian']-without_rate['hessian'])>.01


def test_control_complex_scalar_has_analytic_transpose_not_absolute_square():
    # CONTROL_ONLY complex continuation of a fixed real-coordinate field.
    A=(np.arange(20).reshape(5,4)/80)*(1+.2j);H=np.array([.4,.8,.2,.3])*(1-.1j)
    a=intrinsic_natural_wall_hessian(A,H,np.arange(4)*(.1+.03j),np.zeros((3,1,1)),
        metric_weights=np.array([1+.2j,2-.3j,3+.1j]),lambda_H=.2,nu_squared_action=4.)
    np.testing.assert_allclose(a['hessian'],a['hessian'].T,rtol=0,atol=8e-17)
    assert np.linalg.norm(a['hessian']-a['hessian'].conj().T)>.1


def test_control_at_chart_is_applied_once_to_both_literal_action_currents():
    from bhsm.interface.muon_literal_euclidean_wall_action import natural_wall_current_maps
    from bhsm.interface.muon_euclidean_angular_weak_action import euclidean_open_action_vertices
    # CONTROL_ONLY complex coframe; check each coordinate by direct formula.
    N=1.2+.07j;V=euclidean_open_action_vertices(.9-.04j,N,family=1)['vertices']
    P=np.eye(24);maps=natural_wall_current_maps(V,P,N,1)
    for c in range(24):
        wanted=V[c]*(1j*N if c<4 else 1)
        np.testing.assert_allclose(maps['right'][:,:,c],wanted,rtol=2e-16,atol=2e-17)
        np.testing.assert_allclose(maps['literal_left'][:,:,c],wanted,rtol=2e-16,atol=2e-17)
    assert np.linalg.norm(maps['literal_left']-maps['right'].conj().transpose(1,0,2))>.1


@pytest.mark.parametrize('side',('incoming','outgoing'))
def test_actual_n0_radial_wall_action_equals_frozen_full84_restriction(side):
    from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
    from bhsm.interface.muon_parent_positive_coupled_field import corrected_positive_parent_reference
    from bhsm.interface.muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
    from bhsm.interface.muon_parent_maxwell_full_weak import M
    root=Path(__file__).resolve().parents[1]
    with np.load(root/'artifacts/muon_coupled_lorentz_field_symbol_20261011/run_1/application.npz')as a:
        raw=a[side+'_raw_fields'];expected=a[side+'_field_action_hessian']
    folder='artifacts/muon_finite_normal_phase_20261011/incoming_run_1'if side=='incoming'else'artifacts/muon_inherited_finite_normal_phase_20261011/run_1'
    phase=load_profile_preserving_phase(root/folder);rep=phase['representation']
    kw={}if side=='incoming'else dict(initial_pair=phase['arrays']['initial_pair'],reference_pair=phase['arrays']['reference_pair'])
    b=corrected_positive_parent_reference(raw,rep,coordinate_time=0.,**kw)
    weights=intrinsic_m4_weight_jet(12,raw[:37],raw[37:74],raw[74:98],source_value=raw[98],source_rate=raw[99])
    # Original radial gauge functions have their exact wall values.
    wall=np.einsum('fcj,j->fc',rep['wall_trace_map'],raw[100:180])
    from bhsm.interface.muon_continued_action_reality import action_reality_coefficient
    # The action callback also includes the child inherited affine image.
    wall=action_reality_coefficient(phase,0.)['wall_independent_plus_inherited']
    wall=wall.copy();wall[2:]+=M*(weights['mechanical_connection_lambda'].value-1)
    got=natural_wall_lorentz_forms(b,rep,np.zeros((3,1,1)),wall_connection=wall,
        H=raw[-8:-4],Hdot=raw[-4:],metric_weights=[weights[k].value for k in ('wT','wS','wV')],
        lambda_H=rep['scalar_matching']['lambda_H'],nu_squared_action=4.)
    m,bmix,k=got['forms'];at=16;dyn=68
    # Literal full84 ordering: dynamic64+H4, their velocities, At16.
    ids=np.r_[np.arange(at,84),84+np.arange(at,84),np.arange(at)]
    dense=np.block([[k,bmix],[bmix.T,m]])[np.ix_(ids,ids)]
    np.testing.assert_allclose(dense,expected,rtol=2e-12,atol=2e-12)
    assert got['scalar_gauge_cross_norm']>0
    assert len(got['central_radial_frame_indices'])==4
    assert got['natural_gauge_wall_trace_is_internal_unknown']
    assert not got['magnetic_drive_columns_relabelled_internal']
