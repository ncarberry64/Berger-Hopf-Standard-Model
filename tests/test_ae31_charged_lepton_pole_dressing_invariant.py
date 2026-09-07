import hashlib
from math import exp

import numpy as np
import pytest

from bhsm.interface.ae31_charged_lepton_pole_dressing_invariant import (
    DRESSING_COEFFICIENTS_HEAVY_MIDDLE_LIGHT,
    claim_boundary,
    common_rescaling_no_go,
    dressed_sum_rule_witness,
    pole_dressing_invariant_theorem,
    reference_pole_dressing_target,
)
from scripts.materialize_ae31_charged_lepton_pole_dressing_invariant import (
    TARGET,
    build_payload,
    main,
)


def test_exact_pole_dressing_invariant_is_orthogonal_to_common_rescaling():
    theorem = pole_dressing_invariant_theorem()
    assert theorem["log_dressing_coefficients_heavy_middle_light"] == [
        8.0,
        -9.0,
        1.0,
    ]
    assert theorem["coefficient_sum"] == 0.0
    assert theorem["common_multiplicative_pole_rescaling_cancels"]
    assert not theorem[
        "common_wavefunction_or_unit_rescaling_can_repair_nonzero_residual"
    ]


@pytest.mark.parametrize("factor", [0.1, 0.8, 1.0, 1.7, 10.0])
def test_common_multiplicative_rescaling_cannot_change_the_sum_rule(factor):
    witness = common_rescaling_no_go(factor=factor)
    assert abs(witness["dressing_log_invariant"]) < 2.0e-14
    assert abs(
        witness["dressed_sum_rule_residual"]
        - witness["tree_sum_rule_residual"]
    ) < 2.0e-14
    assert not witness["nonzero_residual_repaired"]


def test_arbitrary_positive_effective_dressings_obey_the_exact_identity():
    tree = np.asarray([1.0, 0.060074470932609765, 0.00029729106456492414])
    dressing = np.asarray([1.03, 0.97, 1.11])
    witness = dressed_sum_rule_witness(
        tree_masses=tree, dressed_masses=tree * dressing
    )
    expected = float(DRESSING_COEFFICIENTS_HEAVY_MIDDLE_LIGHT @ np.log(dressing))
    assert witness["dressing_log_invariant"] == pytest.approx(expected)
    assert abs(witness["residual_difference_minus_dressing_invariant"]) < 2.0e-14


def test_invalid_mass_or_rescaling_inputs_are_rejected():
    with pytest.raises(ValueError):
        dressed_sum_rule_witness(tree_masses=[1.0, 2.0], dressed_masses=[1, 2, 3])
    with pytest.raises(ValueError):
        dressed_sum_rule_witness(tree_masses=[1.0, 2.0, 3.0], dressed_masses=[1, 0, 3])
    with pytest.raises(ValueError):
        common_rescaling_no_go(factor=0.0)


def test_reference_target_is_post_derivation_and_not_an_action_fit():
    target = reference_pole_dressing_target(
        middle_over_heavy=0.05946353426831603,
        light_over_heavy=0.0002875853753250115,
    )
    assert target["required_log_dressing_invariant"] == pytest.approx(
        0.05880357568422312
    )
    assert target["required_multiplicative_dressing_invariant"] == pytest.approx(
        1.0605668991516508
    )
    assert target["effective_dressing_invariant_check"] == pytest.approx(
        target["required_multiplicative_dressing_invariant"]
    )
    minimum_log = np.asarray(target["minimum_Euclidean_log_norm_representative"])
    assert float(DRESSING_COEFFICIENTS_HEAVY_MIDDLE_LIGHT @ minimum_log) == pytest.approx(
        target["required_log_dressing_invariant"]
    )
    assert target["minimum_Euclidean_multiplicative_representative"] == pytest.approx(
        np.exp(minimum_log).tolist()
    )
    assert not target["representative_is_action_solution"]
    assert target["reference_data_used_only_after_derivation"]
    assert not target["target_inserted_into_action"]


def test_common_gauge_freedom_leaves_the_multiplicative_invariant_unchanged():
    target = reference_pole_dressing_target(
        middle_over_heavy=0.05946353426831603,
        light_over_heavy=0.0002875853753250115,
    )
    effective = np.asarray(
        target["effective_dressing_ratios_with_Z_tau_gauge_one"], dtype=float
    )
    for common in (0.25, 2.0, exp(3.0)):
        shifted = common * effective
        invariant = shifted[2] * shifted[0] ** 8 / shifted[1] ** 9
        assert invariant == pytest.approx(
            target["required_multiplicative_dressing_invariant"]
        )


def test_claim_boundary_does_not_invent_a_self_energy_or_physical_poles():
    boundary = claim_boundary()
    assert boundary["AE31_CHARGED_LEPTON_POLE_DRESSING_INVARIANT_DERIVED"]
    assert boundary["COMMON_MULTIPLICATIVE_POLE_RESCALING_NO_GO_DERIVED"]
    assert boundary["FAMILY_RESOLVED_DRESSING_TARGET_QUANTIFIED"]
    assert not boundary["ACTION_DERIVED_DRESSED_TWO_POINT_OPERATOR_AVAILABLE"]
    assert not boundary["MICROSCOPIC_SELF_ENERGY_OR_RG_FLOW_DERIVED"]
    assert not boundary["ADDITIVE_OR_NONDIAGONAL_POLE_CORRECTIONS_EXCLUDED"]
    assert not boundary["CURRENT_C2_GLOBAL_PHYSICAL_LEPTON_POLES_DERIVED"]
    assert not boundary["CURRENT_C2_PHYSICAL_MUON_POLE_DERIVED"]
    assert not boundary["MUON_MAGNETIC_MOMENT_DERIVED"]
    assert not boundary["particle_spectrum_rebuilt"]


def test_materialized_pole_dressing_invariant_is_valid_and_deterministic():
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
