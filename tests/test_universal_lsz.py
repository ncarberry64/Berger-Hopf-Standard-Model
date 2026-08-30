import numpy as np
import pytest

from bhsm.interface.universal_lsz import lsz_amplitude, normalize_simple_pole
from bhsm.interface.universal_quadratic_spectrum import QuadraticDescriptorPencil


def poles():
    pencil = QuadraticDescriptorPencil(
        constant=np.diag([-2.0, -5.0]),
        linear=np.diag([2.0, 3.0]),
        action_version="BHSM-TEST",
        background_id="background",
        domain_id="domain",
        gate7_closed=True,
        quotient_applied=True,
        brst_cancellation_accounted=True,
        scale_map_id="scale",
    )
    return pencil, pencil.poles_and_residues()


def test_simple_pole_is_normalized_without_kinetic_inverse() -> None:
    pencil, found = poles()
    mode = normalize_simple_pole(
        found[0],
        pencil.linear,
        mode_id="mode-0",
        action_selected=True,
        provenance=("same-action descriptor pole",),
    )
    mode.require_physical_external_state()
    assert mode.descriptor_normalization_residual < 1.0e-14
    assert lsz_amplitude(2.0 + 3.0j, (mode,)) == 2.0 + 3.0j


def test_non_action_selected_pole_cannot_be_used_as_physical_external_state() -> None:
    pencil, found = poles()
    mode = normalize_simple_pole(
        found[0],
        pencil.linear,
        mode_id="unselected",
        action_selected=False,
        provenance=("candidate pole",),
    )
    with pytest.raises(RuntimeError, match="action_selected"):
        lsz_amplitude(1.0, (mode,))
