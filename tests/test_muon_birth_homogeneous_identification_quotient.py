import numpy as np
from bhsm.interface.muon_birth_homogeneous_identification_quotient import homogeneous_identification_slice
from bhsm.interface.muon_birth_optimized_two_arm_action import optimized_coupled_rows
from test_muon_birth_optimized_two_arm_action import fixture


def test_joint_chart_bundle_slice_preserves_action_and_canonical_return():
    c,a,w,q=fixture();base=optimized_coupled_rows(c,a,w,q)
    quotient=homogeneous_identification_slice(c);new=optimized_coupled_rows(quotient['coefficients'],a,w,q)
    U=quotient['original_identification']['U']
    np.testing.assert_allclose(new['residual'][:56],base['residual'][:56],rtol=2e-9,atol=3e-12)
    np.testing.assert_allclose(new['scalar_birth']['momentum_residual'],base['scalar_birth']['momentum_residual'],atol=3e-16)
    np.testing.assert_allclose(new['scalar_birth']['trace_residual'][0],U.conj().T@base['scalar_birth']['trace_residual'][0],atol=3e-16)
    old_leg=base['scalar_legendre'][4:];old_leg=old_leg[:2]+1j*old_leg[2:]
    rotated=U.conj().T@old_leg
    np.testing.assert_allclose(new['scalar_legendre'][4:],np.r_[rotated.real,rotated.imag],atol=3e-16)
    np.testing.assert_allclose(np.linalg.norm(new['residual']),np.linalg.norm(base['residual']),rtol=1e-15)
    np.testing.assert_allclose(new['spatial_connection_graph_residual'],0,atol=5e-16)
    for original,transformed in zip(base['arms'],new['arms']):
        assert abs(original['action']['value']-transformed['action']['value'])<1e-14
    assert not quotient['physical_identification_selected']
    assert not quotient['physical_closed_holonomy_removed']
