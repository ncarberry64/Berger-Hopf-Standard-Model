"""Check the mixed handoff against independent bivariate core composition."""

import mpmath as mp
import numpy as np
import pytest

from bhsm.interface.ae4_current_c2_factorized_hs_calderon import terminal_hs_jet_transport_coefficients
from bhsm.interface.ae4_event_response_jet_integration import substitute_terminal_hs_jets
from bhsm.interface.ae4_mixed_terminal_hs import substitute_mixed_terminal_hs_jets


def _arguments(chirality):
    return dict(
        log_radii=np.array([0., 0.1, -0.2, 0.05]),
        proper_durations=np.array([0.2, 0.3, 0.1]),
        source_profile=np.array([1., -0.5, 0.25]),
        dirac_eigenvalue_at_unit_radius=1.5, chirality=chirality,
        spectral_parameter=-1., terminal_load=0.5, decimal_precision=65,
    )


@pytest.mark.parametrize("chirality", [-1, 1])
def test_mixed_substitution_matches_independent_bivariate_mobius_composition(chirality):
    args = _arguments(chirality)
    coeff = terminal_hs_jet_transport_coefficients(**args)
    hjet = ("0.7", "-0.4", "0.15")
    ljet = ("0.375", "-0.25", "0.2")
    actual = substitute_mixed_terminal_hs_jets(coeff, hs_coordinate_jet=hjet, terminal_load_jet=ljet)
    with mp.workdps(65):
        hu, hv, huv = map(mp.mpf, hjet)
        lu, lv, luv = map(mp.mpf, ljet)

        def full_core(u, v):
            # Evaluate the unfactored finite transfer matrices, without using
            # extracted transport coefficients or their chain-rule formula.
            hs = hu*u + hv*v + huv*u*v
            load = mp.mpf("0.5") + lu*u + lv*v + luv*u*v
            midpoint = (args["log_radii"][:-1] + args["log_radii"][1:])/2
            for i in reversed(range(3)):
                w = chirality*mp.mpf("1.5")*mp.exp(-mp.mpf(str(float(midpoint[i]))))
                w += hs*mp.mpf(str(float(args["source_profile"][i])))
                k = mp.sqrt(w*w + 1)
                t = mp.mpf(str(float(args["proper_durations"][i])))
                a = mp.cosh(k*t) - w*mp.sinh(k*t)/k
                b = mp.sinh(k*t)/k
                c = mp.sinh(k*t)/k
                d = mp.cosh(k*t) + w*mp.sinh(k*t)/k
                load = (c + a*load)/(d + b*load)
            return load

        expected = (full_core(0, 0), mp.diff(lambda u: full_core(u, 0), 0),
                    mp.diff(lambda v: full_core(0, v), 0), mp.diff(full_core, (0, 0), (1, 1)))
        keys = ("Weyl_birth_value_decimal", "D_u_Weyl_birth_decimal",
                "D_v_Weyl_birth_decimal", "D_uv_Weyl_birth_decimal")
        for key, value in zip(keys, expected):
            assert abs(mp.mpf(actual[key]) - value) < mp.mpf("1e-55")
    assert not actual["finite_core_recomputed"]


def test_same_direction_reproduces_saved_scalar_second_derivative():
    coeff = terminal_hs_jet_transport_coefficients(**_arguments(1))
    actual = substitute_mixed_terminal_hs_jets(
        coeff, hs_coordinate_jet=(1, 1, 0), terminal_load_jet=("0.375", "0.375", "-0.25"))
    previous = substitute_terminal_hs_jets(coeff, terminal_load_first="0.375", terminal_load_second="-0.25")
    assert actual["D_u_Weyl_birth_decimal"] == previous["D_H_Weyl_birth_decimal"]
    assert actual["D_uv_Weyl_birth_decimal"] == previous["D2_H_Weyl_birth_decimal"]


def test_source_swap_and_nonlinear_coordinate_contacts_are_retained():
    coeff = terminal_hs_jet_transport_coefficients(**_arguments(1))
    a = substitute_mixed_terminal_hs_jets(coeff, hs_coordinate_jet=(0, 0, 1), terminal_load_jet=(0, 0, 2))
    with mp.workdps(60):
        expected = mp.mpf(coeff["first_local_coefficient_a_decimal"])+2*mp.mpf(coeff["terminal_first_jet_sensitivity_s_decimal"])
        assert abs(mp.mpf(a["D_uv_Weyl_birth_decimal"])-expected) < mp.mpf("1e-55")
    left = substitute_mixed_terminal_hs_jets(coeff, hs_coordinate_jet=(1, 2, 3), terminal_load_jet=(4, 5, 6))
    right = substitute_mixed_terminal_hs_jets(coeff, hs_coordinate_jet=(2, 1, 3), terminal_load_jet=(5, 4, 6))
    assert left["D_uv_Weyl_birth_decimal"] == right["D_uv_Weyl_birth_decimal"]


@pytest.mark.parametrize("bad", [(0, 0), (0, float("nan"), 0), (0, 0, "inf"), (None, 0, 0)])
def test_missing_or_nonfinite_leaves_rejected(bad):
    coeff = terminal_hs_jet_transport_coefficients(**_arguments(1))
    with pytest.raises(ValueError):
        substitute_mixed_terminal_hs_jets(coeff, hs_coordinate_jet=bad, terminal_load_jet=(0, 0, 0))


def test_unknown_input_and_wrong_coefficients_are_not_guessed():
    with pytest.raises(TypeError):
        substitute_mixed_terminal_hs_jets({})
    with pytest.raises(ValueError):
        substitute_mixed_terminal_hs_jets({}, hs_coordinate_jet=(0, 0, 0), terminal_load_jet=(0, 0, 0))
