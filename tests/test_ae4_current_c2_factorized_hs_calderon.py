import hashlib

import numpy as np
import pytest

from bhsm.interface.ae4_current_c2_factorized_hs_calderon import (
    claim_boundary,
    direct_composition_hs_weyl_value,
    factorized_product_dirac_hs_weyl_jet,
)
from scripts.materialize_ae4_current_c2_factorized_hs_calderon import (
    TARGET,
    build_payload,
    main,
)


def _small_data():
    x = np.asarray((0.1, 0.17, 0.26, 0.39, 0.54))
    h = np.asarray((0.3, 0.45, 0.38, 0.51))
    profile = np.asarray((1.0, 0.7, 1.2, 0.5))
    return x, h, profile


def test_factorized_hs_jets_match_direct_composition_finite_differences():
    x, h, profile = _small_data()
    arguments = {
        "log_radii": x,
        "proper_durations": h,
        "dirac_eigenvalue_at_unit_radius": 1.5,
        "chirality": 1,
        "source_profile": profile,
        "spectral_parameter": -2.3,
        "decimal_precision": 70,
    }
    jet = factorized_product_dirac_hs_weyl_jet(**arguments)
    step = 2.0e-4
    center = direct_composition_hs_weyl_value(**arguments, hs_coordinate=0.0)
    plus = direct_composition_hs_weyl_value(**arguments, hs_coordinate=step)
    minus = direct_composition_hs_weyl_value(**arguments, hs_coordinate=-step)
    first = (plus - minus) / (2.0 * step)
    second = (plus - 2.0 * center + minus) / (step * step)
    assert abs(jet["D_H_Weyl_birth"] - first) < 2e-8
    assert abs(jet["D2_H_Weyl_birth"] - second) < 2e-7
    assert jet["first_order_product_Dirac_factorization_preserved"]
    assert not jet["dense_generalized_eigensolve_formed"]


def test_factorized_jet_rejects_nonnegative_spectral_parameter():
    x, h, profile = _small_data()
    with pytest.raises(ValueError):
        factorized_product_dirac_hs_weyl_jet(
            log_radii=x,
            proper_durations=h,
            dirac_eigenvalue_at_unit_radius=1.5,
            chirality=1,
            source_profile=profile,
            spectral_parameter=0.0,
        )


def test_full_current_c2_factorized_payload_preserves_tail_gate():
    payload = build_payload()
    result = payload["central_gap_probe_result"]
    boundary = payload["claim_boundary"]
    assert payload["validation_passed"]
    assert result["tail_domain_changes_the_HS_Calderon_jet"]
    assert abs(result["plus_Dirichlet_D_H"] + 1.0) < 1e-14
    assert result["plus_Dirichlet_D2_H"] > 0.0
    assert boundary[
        "AE4_CURRENT_C2_FULL_FINITE_CORE_FACTORIZED_HS_CALDERON_JET_DERIVED"
    ]
    assert not boundary["AE4_CURRENT_C2_MAXIMAL_TAIL_LOAD_AND_HS_JETS_DERIVED"]
    assert not boundary[
        "AE4_CURRENT_C2_MAXIMAL_HISTORY_RETARDED_HS_CALDERON_BLOCK_DERIVED"
    ]


def test_materialized_factorized_hs_calderon_is_deterministic():
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
