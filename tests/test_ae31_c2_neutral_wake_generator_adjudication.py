import hashlib

import numpy as np
import pytest

from bhsm.interface.ae31_c2_neutral_wake_generator_adjudication import (
    claim_boundary,
    historical_first_order_owner_alignment,
    positive_stiffness_zero_reference_theorem,
    traceless_wake_generator,
    unitary_wake_evolution,
)
from scripts.materialize_ae31_c2_neutral_wake_generator_adjudication import (
    TARGET,
    build_payload,
    main,
)


def test_zero_reference_diagonal_forbids_positive_stiffness_mixing():
    result = positive_stiffness_zero_reference_theorem()
    assert result["historical_H00"] == 0.0
    assert result["historical_beta"] == 1.0 / 3.0
    assert np.isclose(result["leading_principal_minor"], -1.0 / 9.0)
    assert not result["historical_seed_is_positive_stiffness"]
    assert result["same_obstruction_for_any_nonzero_beta_with_zero_reference_cost"]


def test_common_phase_removal_produces_two_gap_traceless_generator():
    result = traceless_wake_generator()
    assert result["exact_common_trace_shift"] == "14/9"
    assert result["trace_residual"] < 5.0e-16
    assert result["Hermitian"]
    assert result["two_nonzero_eigenvalue_gaps"]
    assert not result["negative_eigenvalue_obstructs_first_order_unitary_evolution"]


def test_seed_generates_unitary_norm_preserving_evolution():
    result = unitary_wake_evolution(0.713)
    assert result["unitary"]
    assert result["unitarity_residual"] < 2.0e-14
    assert result["norm_preserving"]
    assert not result["physical_time_unit_derived"]
    with pytest.raises(ValueError):
        unitary_wake_evolution(float("nan"))


def test_historical_action_type_aligns_but_current_owner_is_not_evaluated():
    owner = historical_first_order_owner_alignment()
    boundary = claim_boundary()
    assert owner["K_nu_has_correct_Hermitian_three_channel_type"]
    assert not owner["K_nu_equals_action_evaluated_H_wake_on_current_C2"]
    assert not owner["v14_57_diagnostic_fixture_may_be_substituted"]
    assert not boundary["CURRENT_C2_ACTION_EVALUATED_PHYSICAL_HWAKE_DERIVED"]
    assert not boundary["CURRENT_C2_PHYSICAL_NEUTRINO_MONODROMY_DERIVED"]


def test_materialized_wake_adjudication_is_valid_and_deterministic():
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
