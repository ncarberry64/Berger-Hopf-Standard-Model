"""Synthetic pole fixtures test the bridge, not physical BHSM poles."""

from dataclasses import replace
import hashlib
import json
from math import exp, pi

import numpy as np
import pytest

from bhsm.interface.ae31_charged_lepton_pole_dressing_invariant import (
    dressed_sum_rule_witness,
)
from bhsm.interface.charged_lepton_pole_observable import (
    ChargedLeptonPoleInput,
    FAMILY_ROLES,
    charged_lepton_pole_observable,
)
from bhsm.interface.universal_dressed_pole import solve_dressed_pole


def inputs(masses=(2.0, 0.11, 0.0006)):
    records = []
    for role, mass in zip(FAMILY_ROLES, masses):
        position = mass * mass - 0.02j * mass
        pole = solve_dressed_pole(
            lambda z, position=position: np.asarray([[z - position]]),
            lambda _z: np.asarray([[1.0]]),
            position, np.asarray([1.0]),
            action_version="SYNTHETIC-ACTION", background_id="synthetic-background",
            provenance=("synthetic inverse symbol", role),
            complete_self_energy_ledger=True, gate7_closed=True,
        )
        records.append(ChargedLeptonPoleInput(
            role, pole, domain_id="synthetic-common-domain",
            scale_map_id="synthetic-common-mass-unit",
        ))
    return records


def read(records=None, covariance=None, coordinates="log_mass"):
    return charged_lepton_pole_observable(
        inputs() if records is None else records,
        covariance=np.zeros((3, 3)) if covariance is None else covariance,
        covariance_coordinates=coordinates,
    )


def test_existing_dressing_witness_and_pole_consumer_are_the_same_observable():
    tree = np.asarray([1.0, exp(-3.0), exp(54.0 / pi - 27.0)])
    dressed = tree * [1.03, 0.97, 1.11]
    result = read(inputs(dressed))
    witness = dressed_sum_rule_witness(tree_masses=tree, dressed_masses=dressed)
    assert result["dressed_sum_rule_residual"] == pytest.approx(
        witness["dressed_sum_rule_residual"], abs=2e-14,
    )
    assert result["dressed_sum_rule_residual"] == pytest.approx(
        witness["dressing_log_invariant"], abs=2e-14,
    )
    assert result["multiplicative_dressing_invariant"] == pytest.approx(
        exp(witness["dressing_log_invariant"]), abs=2e-14,
    )


def test_complete_correlated_log_covariance_is_used_without_independence():
    factor = np.asarray([[0.02, 0.0], [0.013, 0.008], [0.007, -0.01]])
    covariance = factor @ factor.T
    result = read(covariance=covariance)
    coefficient = np.asarray([8.0, -9.0, 1.0])
    expected = float(np.linalg.norm(coefficient @ factor) ** 2)
    assert result["residual_variance"] == pytest.approx(expected)
    independent = read(covariance=np.diag(np.diag(covariance)))
    assert result["residual_variance"] != pytest.approx(independent["residual_variance"])
    assert result["residual_variance_method"] == "EXACT_AFFINE_RESIDUAL_FROM_LOG_MASS_COVARIANCE"
    assert result["cross_family_covariances_retained"]


@pytest.mark.parametrize("scale_variance", [0.0, 1e-8, 0.125, 4.0])
def test_shared_log_scale_covariance_is_an_exact_null_direction(scale_variance):
    result = read(covariance=scale_variance * np.ones((3, 3)))
    assert result["residual_variance"] == 0.0
    assert result["common_log_scale_jacobian"] == 0.0


def test_adding_a_common_scale_uncertainty_preserves_the_residual_variance():
    covariance = np.asarray([[4.0, 2.0, 1.0], [2.0, 3.0, 0.5], [1.0, 0.5, 2.0]]) / 1024.0
    baseline = read(covariance=covariance)
    shifted = read(covariance=covariance + 0.25 * np.ones((3, 3)))
    assert shifted["residual_variance"] == baseline["residual_variance"]


def test_common_mass_unit_rescaling_preserves_the_invariant_and_covariance():
    masses = np.asarray([2.0, 0.11, 0.0006])
    covariance = np.diag((0.005 * masses) ** 2)
    result = read(inputs(masses), covariance, "mass")
    scaled = read(inputs(7.0 * masses), 49.0 * covariance, "mass")
    assert scaled["dressed_sum_rule_residual"] == pytest.approx(result["dressed_sum_rule_residual"], abs=1e-14)
    assert scaled["residual_variance"] == pytest.approx(result["residual_variance"])
    assert result["residual_variance_method"] == "FIRST_ORDER_DELTA_METHOD_FROM_MASS_COVARIANCE"


def test_mass_covariance_and_log_covariance_agree_under_the_delta_map():
    records = inputs()
    masses = np.asarray([record.pole.pole_mass for record in records])
    factor = np.asarray([[0.01, 0.03], [0.02, -0.01], [0.04, 0.0]])
    log_covariance = factor @ factor.T
    mass_covariance = log_covariance * np.outer(masses, masses)
    result = read(records, mass_covariance, "mass")
    expected = read(records, log_covariance)
    assert result["residual_variance"] == pytest.approx(expected["residual_variance"])
    gradient = np.asarray(result["mass_jacobian_heavy_middle_light"])
    assert result["residual_variance"] == pytest.approx(float(gradient @ mass_covariance @ gradient))
    assert float(gradient @ masses) == pytest.approx(0.0, abs=2e-15)


def test_family_permutation_reorders_both_poles_and_covariance_together():
    records = inputs()
    covariance = np.asarray([[0.004, 0.001, 0.0], [0.001, 0.003, 0.001], [0.0, 0.001, 0.002]])
    baseline = read(records, covariance)
    order = [2, 0, 1]
    reordered = read([records[i] for i in order], covariance[np.ix_(order, order)])
    assert reordered == baseline


@pytest.mark.parametrize("field,value", [
    ("action_version", "other-action"), ("background_id", "other-background"),
    ("domain_id", "other-domain"), ("scale_map_id", "other-scale"),
    ("spectral_convention", "unsquared energy E"),
])
def test_mixed_owner_domain_scale_or_convention_is_rejected(field, value):
    records = inputs()
    if field in ("action_version", "background_id"):
        records[1] = replace(records[1], pole=replace(records[1].pole, **{field: value}))
    else:
        records[1] = replace(records[1], **{field: value})
    with pytest.raises(ValueError, match="same action|spectral convention"):
        read(records)


@pytest.mark.parametrize("field,value", [
    ("gate7_closed", False), ("complete_self_energy_ledger", False),
    ("converged", False), ("simple", False), ("causal_width", False),
    ("relative_symbol_residual", 0.1),
])
def test_existing_pole_promotion_gates_are_reused(field, value):
    records = inputs()
    records[1] = replace(records[1], pole=replace(records[1].pole, **{field: value}))
    with pytest.raises(RuntimeError, match="dressed-pole promotion blocked"):
        read(records)


@pytest.mark.parametrize("field,value", [
    ("provenance", ()), ("provenance", ("",)), ("action_version", ""),
    ("background_id", ""), ("pole_mass", np.nan), ("pole_mass", 0.0),
    ("pole_mass", 3.0), ("pole_width", np.inf),
    ("spectral_parameter", complex(np.nan, 0.0)),
    ("relative_symbol_residual", np.nan),
    ("descriptor_derivative_normalization", 0.0),
    ("residue", np.asarray([[np.nan]])),
])
def test_malformed_pole_records_are_rejected(field, value):
    records = inputs()
    records[1] = replace(records[1], pole=replace(records[1].pole, **{field: value}))
    with pytest.raises(ValueError):
        read(records)


def test_missing_duplicate_or_unlabelled_families_are_rejected():
    records = inputs()
    with pytest.raises(ValueError, match="exactly three"):
        read(records[:2])
    with pytest.raises(ValueError, match="exactly once"):
        read([records[0], records[0], records[2]])
    records[1] = replace(records[1], family_role="second-largest observed mass")
    with pytest.raises(ValueError, match="explicit"):
        read(records)


@pytest.mark.parametrize("covariance", [
    np.zeros((2, 2)), np.full((3, 3), np.nan),
    np.asarray([[1.0, 0.1, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]),
    np.diag([1.0, -1.0, 1.0]),
    np.asarray([[1.0, 2.0, 0.0], [2.0, 1.0, 0.0], [0.0, 0.0, 1.0]]),
    np.asarray([[0.0, 0.1, 0.0], [0.1, 1.0, 0.0], [0.0, 0.0, 1.0]]),
    np.eye(3, dtype=complex),
])
def test_malformed_or_indefinite_covariance_is_rejected(covariance):
    with pytest.raises(ValueError):
        read(covariance=covariance)


def test_synthetic_readout_neither_promotes_physical_bhsm_poles_nor_error_bounds():
    result = read()
    assert result["classification"] == "CONDITIONAL_ALGEBRAIC_READOUT_FROM_SUPPLIED_DRESSED_POLES"
    assert result["existing_pole_promotion_gates_passed"]
    assert not result["current_bhsm_physical_prediction_promoted"]
    assert not result["covariance_is_outward_error_bound"]
    assert not result["empirical_reference_used"]
    assert not result["family_or_mode_selection_performed"]
    with pytest.raises(ValueError, match="coordinates"):
        read(coordinates="independent_errors")


def test_conditional_readout_serialization_reproduces_without_nan_values():
    first = json.dumps(read(), sort_keys=True, allow_nan=False).encode()
    second = json.dumps(read(), sort_keys=True, allow_nan=False).encode()
    assert first == second
    assert hashlib.sha256(first).hexdigest() == hashlib.sha256(second).hexdigest()


@pytest.mark.parametrize("middle_mass,match", [
    (exp(-53.0), "finite first-order invariant variance"),
    (exp(-110.0), "finite multiplicative dressing invariant"),
    (exp(110.0), "underflows"),
])
def test_unrepresentable_invariant_or_variance_is_rejected(middle_mass, match):
    with pytest.raises(ValueError, match=match):
        read(inputs((1.0, middle_mass, 1.0)), np.eye(3))
