"""BHSM v10.3 configuration-space and prior-work equivalence audit."""

from __future__ import annotations

from typing import Any


VERSION = "v10.3"
CONFIGURATION_VERDICT = (
    "BHSM_CURRENT_STRATIFIED_CONFIGURATION_SPACE_CONTAINS_A_LOCAL_M8_"
    "BREATHING_MODE_BUT_NO_SELECTED_BUOYANCY_DEGREE"
)


def prior_work_equivalence_ledger() -> list[dict[str, Any]]:
    """Map v10.3 terminology to authoritative earlier BHSM results."""

    return [
        {
            "v10_3_name": "seam normal displacement / dynamical embedding",
            "earlier_name": "moving B1 endpoint, support shift, and normal-support residual",
            "versions": ["v6.13", "v6.24", "v6.25", "v6.27"],
            "authoritative_result": "BHSM_FOLD_LOCALIZATION_COMPATIBLE_WITH_FIXED_B1_SUPPORT",
            "same_object": "only for the M5 B1 fold-support question",
            "imported_conclusion": (
                "full shift variation removes the apparent obstruction and no dynamical "
                "B1 embedding is required through local two-derivative order"
            ),
        },
        {
            "v10_3_name": "gauge-invariant normal/radion scalar",
            "earlier_name": "interface threading trace S_Sigma",
            "versions": ["v6.15", "v6.16", "v6.17", "v6.18", "v6.27"],
            "authoritative_result": "BHSM_ENDPOINT_TRACE_RESPONSE_DERIVED",
            "same_object": False,
            "imported_conclusion": (
                "the trace is gauge invariant but is fixed by the complete momentum "
                "constraint; it is not an independent physical radion"
            ),
        },
        {
            "v10_3_name": "one healthy scalar deformation",
            "earlier_name": "critical scalar-wall fold amplitude q",
            "versions": ["v6.28", "v6.29", "v6.30.2", "v6.30.4", "v6.30.5"],
            "authoritative_result": "BHSM_FOLD_KINETIC_NORM_POSITIVE_CONDITIONALLY",
            "same_object": False,
            "imported_conclusion": (
                "q is an action-linked scalar-wall Jacobi amplitude with a conditional "
                "positive kinetic norm and Fredholm construction, not seam depth or Hopf radius"
            ),
        },
        {
            "v10_3_name": "localized Hopf radion",
            "earlier_name": "vertical metric determinant / diagnostic pi_! S8 radion",
            "versions": ["v7.1", "v9.1", "v10.2"],
            "authoritative_result": (
                "If a_F varies, pi_!S8 is scalar-tensor gravity and is not the stored S5 action"
            ),
            "same_object": True,
            "imported_conclusion": (
                "the breathing mode is already an M8 metric degree, but its lower-stratum "
                "ownership, localized source, and stabilizing background are not completed"
            ),
        },
        {
            "v10_3_name": "compact-domain global zero-mode response",
            "earlier_name": "metric-modulus Schur lift and Fredholm projection",
            "versions": ["v6.28", "v6.29", "v6.30.4"],
            "authoritative_result": "BHSM_FOLD_PROJECTED_SCHUR_REDUCTION_DERIVED",
            "same_object": False,
            "imported_conclusion": (
                "a normalized fold-sector kernel response exists, but it neither fixes a "
                "dimensional modulus nor supplies the Hopf-radion restoring law"
            ),
        },
        {
            "v10_3_name": "common-domain stress pullback",
            "earlier_name": "covariant reduction functor and KKT compatibility adjoints",
            "versions": ["v7.1", "v7.3", "v10.2"],
            "authoritative_result": "BHSM_LOCALIZED_NORMAL_STRESS_PULLBACK_NOT_DERIVED",
            "same_object": "partial infrastructure only",
            "imported_conclusion": (
                "trace/pushforward maps and matcher reactions exist, but no single conserved "
                "M8 tensor contains every independently owned stratum"
            ),
        },
    ]


def configuration_space_ledger() -> dict[str, Any]:
    return {
        "M8_current": ["G_AB", "chi", "sigma_8", "eta", "omega_Sp1"],
        "M5_current": ["g_5,+", "g_5,-", "sigma_5,+", "sigma_5,-", "ADM lapse", "ADM shift"],
        "M4_current": ["h_mu_nu", "A_SM", "Psi_SM", "H", "intrinsic currents"],
        "compatibility": ["Lambda_85", "lambda_sigma", "Lambda_54,+", "Lambda_54,-"],
        "fixed_data": ["iota_54,+", "iota_54,-", "B1 support", "collar charts", "Z2 gluing"],
        "not_in_current_configuration_space": ["varied X:M4->M8", "varied Sigma7 embedding"],
        "largest_supported_pre_gauge_space": (
            "product of the independently owned M8, M5, M4, and multiplier spaces with fixed embeddings"
        ),
        "proposed_space_with_X": "action-domain extension, not a recovered current field",
    }


def gauge_group_ledger() -> dict[str, Any]:
    return {
        "parent": "Diff(M8) preserving the declared bundle/topology and boundary class",
        "internal": "Sp(1) bundle automorphisms and retained internal gauge groups",
        "cap": "cap diffeomorphisms compatible with fixed B1 and Z2 gluing",
        "seam": "Diff(M4) x SM gauge group",
        "compatibility": "matched subgroup acting consistently through Q_H, trace, and pullback maps",
        "single_semidirect_product_proved": False,
        "reason": "the stratified fields are distinct off shell and linked by KKT matchers",
    }


def constrained_scalar_ledger() -> list[dict[str, Any]]:
    return [
        {
            "candidate": "rho coordinate shift",
            "configuration_status": "coordinate/gauge",
            "canonical_pair": False,
            "survives_constraints": False,
            "physical_scalar_count": 0,
        },
        {
            "candidate": "B1 threading/endpoint trace",
            "configuration_status": "metric/endpoint representative",
            "canonical_pair": False,
            "survives_constraints": False,
            "physical_scalar_count": 0,
            "prior_result": "v6.27 complete momentum constraint fixes W and the endpoint trace",
        },
        {
            "candidate": "normal embedding psi",
            "configuration_status": "absent from current action domain",
            "canonical_pair": False,
            "survives_constraints": None,
            "physical_scalar_count": 0,
        },
        {
            "candidate": "local Hopf breathing beta=ln(a_F/a_F0)",
            "configuration_status": "existing M8 vertical-metric degree",
            "canonical_pair": True,
            "survives_constraints": "conditionally in the invariant M8 reduction",
            "physical_scalar_count": 1,
            "complete_stratified_ownership": False,
        },
        {
            "candidate": "scalar-wall fold amplitude q",
            "configuration_status": "existing M5 critical Jacobi amplitude",
            "canonical_pair": True,
            "survives_constraints": "conditionally on the v6.28-v6.30 fixed-h domain",
            "physical_scalar_count": 1,
            "same_as_normal_or_radion": False,
        },
    ]


def physical_count(n_canonical: int, n_first_class: int, n_second_class: int) -> int:
    """Return the physical phase-space dimension in Dirac--Bergmann counting."""

    count = n_canonical - 2 * n_first_class - n_second_class
    if min(n_canonical, n_first_class, n_second_class) < 0 or count < 0:
        raise ValueError("constraint count must define a nonnegative phase-space dimension")
    return count


def configuration_payload() -> dict[str, Any]:
    rows = constrained_scalar_ledger()
    validation = {
        "prior_routes_named": len(prior_work_equivalence_ledger()) == 6,
        "embedding_not_silently_added": "varied X:M4->M8" in configuration_space_ledger()["not_in_current_configuration_space"],
        "coordinate_count_zero": rows[0]["physical_scalar_count"] == 0,
        "threading_count_zero": rows[1]["physical_scalar_count"] == 0,
        "radion_candidate_count_one": rows[3]["physical_scalar_count"] == 1,
        "fold_not_conflated": rows[4]["same_as_normal_or_radion"] is False,
    }
    return {
        "artifact": "BHSM_full_configuration_space_v10_3",
        "version": VERSION,
        "configuration_space": configuration_space_ledger(),
        "gauge_group": gauge_group_ledger(),
        "prior_work_equivalence": prior_work_equivalence_ledger(),
        "scalar_degree_ledger": rows,
        "buoyancy_selected_physical_scalar_count": 0,
        "verdict": CONFIGURATION_VERDICT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
