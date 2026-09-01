import hashlib

import numpy as np
import pytest

from bhsm.interface.ae31_c2_capture_neutrino_propagation_gate import (
    capture_boundary_to_propagation_contract,
    claim_boundary,
    common_shift_invariance,
    electron_capture_family_source,
    family_central_propagation,
    family_noncentrality_theorem,
    historical_neutrino_reconciliation,
    squared_neutral_operator_contract,
)
from scripts.materialize_ae31_c2_capture_neutrino_propagation_gate import (
    TARGET,
    build_payload,
    main,
)


def test_capture_selects_nue_source_not_mass_eigenstate():
    source = electron_capture_family_source()
    assert source["source_vector"] == [1.0, 0.0, 0.0]
    assert not source["fixed_mass_eigenstate_selected_at_production"]
    assert not source["propagation_operator_selected_at_production"]


def test_family_central_environment_changes_only_common_phase():
    result = family_central_propagation((1.0, 0.0, 0.0), 0.713)
    assert result["probability_change_norm"] < 1.0e-15
    assert not result["flavor_change"]
    with pytest.raises(ValueError):
        family_central_propagation((1.0, 1.0, 0.0), 0.0)


def test_common_shift_preserves_two_independent_gaps():
    operator = np.asarray(((0.2, 0.1, 0.0), (0.1, 0.7, 0.05), (0.0, 0.05, 1.4)))
    result = common_shift_invariance(operator, 8.3)
    assert result["gap_invariance_residual"] < 5.0e-15
    assert not result["common_environment_generates_splittings"]


def test_mass_readout_and_boundary_chain_fail_closed():
    squared = squared_neutral_operator_contract()
    family = family_noncentrality_theorem()
    chain = capture_boundary_to_propagation_contract()
    history = historical_neutrino_reconciliation()
    boundary = claim_boundary()
    assert not squared["local_D_squared_eigenvalue_is_automatically_a_mass_squared"]
    assert not family["current_C2_family_noncentral_neutral_operator_derived"]
    assert not family[
        "family_noncentrality_alone_sufficient_for_flavor_conversion"
    ]
    assert not chain["outgoing_nu_e_boundary_trace_derived"]
    assert history["v14_55_status"] == "FORMALIZED_HYPOTHESIS_NOT_ACTION_DERIVED"
    assert boundary["CURRENT_C2_CAPTURE_INITIAL_NUE_FAMILY_SOURCE_DERIVED"]
    assert not boundary["CURRENT_C2_TWO_NEUTRINO_SPLITTINGS_DERIVED"]
    assert not boundary["CURRENT_C2_NONTRIVIAL_NEUTRAL_FLAVOR_MONODROMY_DERIVED"]


def test_artifact_is_valid_and_deterministic():
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
