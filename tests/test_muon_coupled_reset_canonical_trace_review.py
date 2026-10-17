"""Independent value/jet check of the actual coupled candidate density trace."""
from pathlib import Path
import numpy as np
from bhsm.interface.muon_continued_action_reality import _geometry


def test_actual_nonreal_half_density_two_jet_against_independent_coframe_values():
    root=Path(__file__).resolve().parents[1]
    path=root/'artifacts/muon_coupled_reset_canonical_trace_20261012/run_1/application.npz'
    with np.load(path,allow_pickle=False)as z:
        raw=z['raw_pair'].copy();first=z['canonical_density_ratio_raw_first'].copy()
        second=z['canonical_density_ratio_raw_second'].copy()
        base=z['canonical_value_reset'][0,0]
        graphP=z['joint_canonical_Pi'][:106];ownP=z['parent_standalone_Pi']
        jointLy=z['joint_algebraic_constraint_rows'][:40];ownLy=z['parent_standalone_algebraic_rows']
    rng=np.random.default_rng(6923)
    direction=.005*(rng.normal(size=(2,268))+1j*rng.normal(size=(2,268)))
    # Independent direct coframe value extension uses no Jet derivatives.
    def value(t):
        p,c=(_geometry(x)['R4']for x in raw+t*direction)
        return (c/p)**1.5
    d=direction.reshape(-1);h=1e-3
    np.testing.assert_allclose(value(0),base,atol=2e-16)
    np.testing.assert_allclose(first@d,(value(h)-value(-h))/(2*h),rtol=2e-6,atol=2e-9)
    np.testing.assert_allclose(d@second@d,(value(h)-2*value(0)+value(-h))/(h*h),rtol=2e-5,atol=2e-8)
    # The incoming constraint equality at this point does not identify Pi.
    np.testing.assert_allclose(jointLy,ownLy,atol=2e-16)
    assert np.linalg.norm(graphP-ownP)>7.
