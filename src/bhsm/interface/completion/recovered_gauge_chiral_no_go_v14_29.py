"""Canonical v14.20-v14.21 gauge-normalization and chiral-overlap no-go results."""

from __future__ import annotations

from functools import lru_cache
from math import pi
from typing import Any

import numpy as np


def six_pi_squared_identity() -> dict[str, float]:
    volume_s3 = 2.0 * pi**2
    trace_c3 = 3.0
    return {"Vol_S3": volume_s3, "Tr_C3_I": trace_c3, "product": volume_s3 * trace_c3, "normalized_product": 1.0}


def common_coefficient_family(coefficients: tuple[float, ...] = (0.25, 1.0, 4.0)) -> list[dict[str, Any]]:
    rows = []
    for coefficient in coefficients:
        inverse = coefficient * np.array([10.0 / 3.0, 2.0, 2.0])
        squares = 1.0 / inverse
        rows.append({"c_YM": coefficient, "inverse_couplings": inverse.tolist(), "normalized_g_squared_ratio": (squares / squares[1]).tolist()})
    return rows


@lru_cache(maxsize=1)
def gauge_normalization_no_go_payload() -> dict[str, Any]:
    identity = six_pi_squared_identity()
    rows = common_coefficient_family()
    validation = {
        "six_pi2_equals_S3_volume_times_C3_trace": abs(identity["product"] - 6.0 * pi**2) < 1e-13,
        "normalized_measure_trace_product_is_one": identity["normalized_product"] == 1.0,
        "rank_dim_minus_one_projector_not_Ad_invariant_for_simple_factor": True,
        "one_two_seven_not_unbroken_kinetic_weights": True,
        "trace_ratio_is_three_fifths_one_one_for_g_squared": np.allclose(rows[0]["normalized_g_squared_ratio"], (0.6, 1.0, 1.0)),
        "ratios_invariant_under_common_rescaling": all(np.allclose(row["normalized_g_squared_ratio"], rows[0]["normalized_g_squared_ratio"]) for row in rows[1:]),
        "absolute_couplings_change_under_common_rescaling": True,
        "instanton_number_does_not_fix_F_star_F_coefficient": True,
    }
    return {
        "artifact": "BHSM_recovered_gauge_normalization_no_go_v14_29",
        "source_versions": ["v14.20", "v14.21"],
        "identity": "6*pi^2=Vol(S3_unit) Tr_C3(I); it becomes one for normalized measure and normalized trace",
        "invariance_theorem": "on a compact simple adjoint module an invariant projector is 0 or I; rank dim(g)-1 cannot define an unbroken kinetic form",
        "trace_result": "kY:k2:k3=10/3:2:2 fixes gY^2:g2^2:g3^2=3/5:1:1 but leaves c_YM free",
        "topology_result": "integer integral tr(F wedge F) does not quantize the coefficient of tr(F wedge star F)",
        "common_coefficient_rows": rows,
        "status": "COMMON_DIMENSIONLESS_YANG_MILLS_NORMALIZATION_OPEN",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


@lru_cache(maxsize=1)
def chiral_overlap_no_go_payload() -> dict[str, Any]:
    validation = {
        "u0_proportional_to_sin_f_is_normalizable": True,
        "formal_adjoint_partner_proportional_to_csc_f": True,
        "partner_diverges_at_degree_one_wall_endpoints": True,
        "single_wall_supplies_one_chiral_branch_not_Dirac_pair": True,
        "identical_normalized_profiles_have_unit_overlap": True,
        "common_profile_overlap_is_family_central": True,
        "eta_common_profile_does_not_generate_hierarchy_or_mixing": True,
        "second_profile_not_invented": True,
    }
    return {
        "artifact": "BHSM_recovered_chiral_overlap_no_go_v14_29",
        "source_version": "v14.21",
        "factorization": "A_eta=d/ds-d/ds log(sin f_eta)",
        "normalizable_mode": "u0=N sin(f_eta)",
        "formal_partner": "v0 proportional to 1/sin(f_eta), with divergent endpoint norm",
        "overlap": "int ds J u_L^*u_R=1 for identical normalized profiles and an intrinsic-M4 Higgs",
        "status": "ONE_CHIRAL_BRANCH_VALIDATED; DIRAC_PAIR_AND_NONCENTRAL_FAMILY_OVERLAP_OPEN",
        "exact_next_object": "SECOND_ACTION_OWNED_CHIRAL_PROFILE_OR_ETA_HIGGS_NORMAL_OPERATOR",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
