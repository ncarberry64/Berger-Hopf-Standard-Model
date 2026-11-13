"""Algebraic controls for a diagnostic, never BHSM prediction inputs."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'audits'))

import numpy as np
from scipy.linalg import eig
from muon_complex_pole_slope import pole_slope_invariants


def test_complex_energy_and_width_slopes_match_independent_eigenproblem():
    h=np.array([[.2-.3j,.4+.1j],[-.2j,-.1+.05j]])
    a=pole_slope_invariants(h)
    expected=eig(h,left=False,right=False)
    actual=a['unordered_complex_pole_slopes']
    assert max(min(abs(z-actual))for z in expected)<5e-16
    assert np.max(abs(a['characteristic_rows']))<1e-16
    assert np.max(abs(a['unordered_width_slopes']))>.1
    assert a['physical_magnetic_moment'] is None


def test_independent_left_and_right_frame_changes_preserve_slopes():
    # The original pole normalization Z is not a Hilbert/current Gram.
    Z=np.array([[1+.1j,.2],[.1j,.9-.2j]])
    M=np.array([[.3-.1j,.2j],[-.1,.4+.05j]])
    left=np.array([[1,.2j],[.3,1.1]])
    right=np.array([[.9,.1],[.2j,1.2]])
    h=-np.linalg.solve(Z,M)
    changed=-np.linalg.solve(left@Z@right,left@M@right)
    a,b=pole_slope_invariants(h),pole_slope_invariants(changed)
    assert abs(a['complex_center']-b['complex_center'])<2e-16
    assert abs(a['half_splitting_squared']-b['half_splitting_squared'])<2e-16
    assert np.max(abs(changed-np.linalg.solve(right,h@right)))<3e-16


def test_zero_center_does_not_erase_spin_splitting_or_width_slopes():
    h=np.diag([.4-.08j,-.4+.08j])
    a=pole_slope_invariants(h)
    assert a['complex_center']==0
    assert np.max(abs(a['unordered_energy_slopes']))==.4
    assert np.max(abs(a['unordered_width_slopes']))==.16
    assert not a['pole_or_analytic_branch_admitted']
