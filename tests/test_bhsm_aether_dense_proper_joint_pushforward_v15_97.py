import math

from bhsm.interface.aether_dense_proper_joint_pushforward_v15_97 import (
    stored_state_witness,
    wavefunction_residue,
)


def test_stored_state_reproduces_direct_adm_joint_coefficients():
    result = stored_state_witness(0.08)
    assert math.isclose(result["boundary_lapse"], 2.6584440092989206, rel_tol=2.0e-10)
    assert math.isclose(result["K_magnetic"], 733.166317007997, rel_tol=2.0e-5)
    assert math.isclose(result["K_electric"], 2982.874990370266, rel_tol=2.0e-5)


def test_wavefunction_residue_is_positive_and_fixes_nonzero_yukawa():
    residue = wavefunction_residue(1.02)
    assert residue > 0.0
    assert residue**-0.5 > 0.0
