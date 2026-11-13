"""Full nonsymmetric Schur difference including both state return orders."""
import numpy as np
from bhsm.interface.muon_d5_fixed_radial_poisson import fixed_radial_field_poisson


def test_source_energy_schur_matches_independent_whole_operator_difference():
    rng=np.random.default_rng(511);d,nw=7,3
    K=rng.normal(size=(d,d))+.2j*rng.normal(size=(d,d))+8*np.eye(d)
    E,S,ES=[rng.normal(size=(d,d))+.1j*rng.normal(size=(d,d))for _ in range(3)]
    z=fixed_radial_field_poisson(K,E,S[None],ES[None],wall_dimension=nw)
    ni=d-nw
    def schur(e,s):
        A=K+e*E+s*S+e*s*ES
        return A[ni:,ni:]-A[ni:,:ni]@np.linalg.solve(A[:ni,:ni],A[:ni,ni:])
    h=2e-4;fd=(schur(h,h)-schur(h,-h)-schur(-h,h)+schur(-h,-h))/(4*h*h)
    assert np.max(abs(fd-z['complete_source_energy_return'][0]))<8e-8
    assert np.max(abs(z['original_right_field_rows']))<2e-15
    assert np.max(abs(z['original_literal_left_field_rows']))<2e-15
    assert np.max(abs(z['original_right_energy_field_rows']))<2e-15
    assert np.max(abs(z['original_literal_left_energy_field_rows']))<2e-15
