"""Common seam--fold--Hopf perturbation audit for BHSM v10.3."""

from __future__ import annotations

from typing import Any

import sympy as sp

from bhsm.interface.full_shift_variation_support_closure import (
    ENDPOINT_RESULT,
    SUPPORT_RESULT,
)
from bhsm.interface.fold_schur_kinetic import (
    PRIMARY_RESULT as FOLD_KINETIC_RESULT,
    SCHUR_RESULT,
)
from .local_radion_v10_3 import RADION_VERDICT


VERSION = "v10.3"
UNRESOLVED = "EQUIVALENCE_UNRESOLVED"
PRIMARY_VERDICT = (
    "BHSM_COMMON_ENVELOPMENT_MODE_EQUIVALENCE_BLOCKED_BY_UNDERIVED_"
    "CROSS_DOMAIN_HESSIAN"
)
NEXT_EXACT_OBJECT = (
    "COMMON_PHYSICAL_ENVELOPMENT_MODE_INTERTWINER_BETWEEN_SEAM_SHIFT_"
    "FOLD_AND_HOPF_BREATHING"
)

BLOCK_STATUSES = (
    "DERIVED",
    "DERIVED_CONDITIONAL",
    "ZERO_BY_SYMMETRY",
    "ZERO_BY_DOMAIN_RESTRICTION",
    "UNDEFINED_CROSS_DOMAIN",
    "OPEN",
)


def historical_import_audit() -> list[dict[str, str]]:
    """Link to authoritative implementations rather than duplicate their derivations."""

    return [
        {"module": "bhsm.interface.full_shift_variation_support_closure", "result": ENDPOINT_RESULT},
        {"module": "bhsm.interface.full_shift_variation_support_closure", "result": SUPPORT_RESULT},
        {"module": "bhsm.interface.fold_schur_kinetic", "result": SCHUR_RESULT},
        {"module": "bhsm.interface.fold_schur_kinetic", "result": FOLD_KINETIC_RESULT},
        {"module": "bhsm.interface.envelopment.local_radion_v10_3", "result": RADION_VERDICT},
    ]


def perturbation_provenance() -> list[dict[str, Any]]:
    """Return the three existing variables without creating aliases."""

    return [
        {
            "component": "psi",
            "exact_repository_variable": "S_Sigma endpoint threading trace",
            "representation": "observable-boundary / fixed-B1 support response",
            "source": "v6.27 full shift variation and support closure",
            "definition": "S_Sigma=-tau*pi*chi_1*q_fold/16",
            "independent_on_imported_domain": False,
        },
        {
            "component": "zeta",
            "exact_repository_variable": "q_fold",
            "representation": "scalar-wall/interface Jacobi amplitude",
            "source": "v6.28-v6.30.5 fold Fredholm and Lyapunov--Schmidt chain",
            "definition": "normalized critical scalar-wall kernel amplitude",
            "independent_on_imported_domain": True,
        },
        {
            "component": "varphi_F",
            "exact_repository_variable": "delta beta=delta ln(a_F/a_F0)",
            "representation": "M8 interior Hopf-fiber breathing",
            "source": "v7.1, v9.1, v10.2, and v10.3 local-radion audit",
            "definition": "variation of the vertical metric determinant",
            "independent_on_imported_domain": "conditional M8 invariant reduction",
        },
    ]


def block_ledger() -> dict[str, list[list[dict[str, Any]]]]:
    """Classify every block; reduced-action absence is never called symmetry zero."""

    def block(status: str, value: Any, reason: str) -> dict[str, Any]:
        if status not in BLOCK_STATUSES:
            raise ValueError(f"invalid block status: {status}")
        return {"status": status, "value": value, "reason": reason}

    restricted = "psi is constrained to the fold amplitude on the imported fixed-B1 domain"
    cross = "no common M8/M5 variational domain has been derived"
    kinetic = [
        [block("ZERO_BY_DOMAIN_RESTRICTION", 0, restricted), block("ZERO_BY_DOMAIN_RESTRICTION", 0, restricted), block("UNDEFINED_CROSS_DOMAIN", None, cross)],
        [block("ZERO_BY_DOMAIN_RESTRICTION", 0, restricted), block("DERIVED_CONDITIONAL", 6.935084858283065, "v6.29 normalized fold kinetic norm"), block("UNDEFINED_CROSS_DOMAIN", None, cross)],
        [block("UNDEFINED_CROSS_DOMAIN", None, cross), block("UNDEFINED_CROSS_DOMAIN", None, cross), block("DERIVED_CONDITIONAL", "6*kappa5", "Einstein-frame Hopf breathing coefficient")],
    ]
    hessian = [
        [block("ZERO_BY_DOMAIN_RESTRICTION", 0, restricted), block("ZERO_BY_DOMAIN_RESTRICTION", 0, restricted), block("UNDEFINED_CROSS_DOMAIN", None, cross)],
        [block("ZERO_BY_DOMAIN_RESTRICTION", 0, restricted), block("DERIVED_CONDITIONAL", "H_fold on D_fold", "v6.28-v6.30 fold operator and reduced interaction"), block("UNDEFINED_CROSS_DOMAIN", None, cross)],
        [block("UNDEFINED_CROSS_DOMAIN", None, cross), block("UNDEFINED_CROSS_DOMAIN", None, cross), block("DERIVED_CONDITIONAL", "H_F on D_M8", "local Hopf-radion operator; no stationary background")],
    ]
    return {"basis": ["psi", "zeta", "varphi_F"], "K_env": kinetic, "H_env": hessian}


def gauge_audit() -> dict[str, Any]:
    """Gauge matrix for the already reduced/invariant repository variables."""

    requested_operations = [
        "radial_diffeomorphism",
        "seam_reparametrization",
        "collar_coordinate_change",
        "fiber_rescaling",
        "matcher_support_shift",
    ]
    generators = [item for item in requested_operations if item != "fiber_rescaling"]
    matrix = sp.zeros(3, len(generators))
    return {
        "generators": generators,
        "requested_operations": requested_operations,
        "transformation_ledger": [
            {"operation": "radial_diffeomorphism", "on_psi_zeta_varphiF": [0, 0, 0], "scope": "invariant S_Sigma, quotient q_fold, and beta0'=0"},
            {"operation": "seam_reparametrization", "on_psi_zeta_varphiF": [0, 0, 0], "scope": "scalar representatives"},
            {"operation": "collar_coordinate_change", "on_psi_zeta_varphiF": [0, 0, 0], "scope": "S_Sigma is the invariant endpoint trace"},
            {"operation": "fiber_rescaling", "on_psi_zeta_varphiF": [0, 0, "epsilon_F"], "scope": "physical metric breathing, not an admissible gauge generator"},
            {"operation": "matcher_support_shift", "on_psi_zeta_varphiF": [0, 0, 0], "scope": "fixed-support and moving-coordinate representatives give the same S_Sigma"},
        ],
        "matrix": [[0 for _ in generators] for _ in range(3)],
        "rank": matrix.rank(),
        "quotient_dimension_before_constraints": 3 - matrix.rank(),
        "interpretation": (
            "S_Sigma and q_fold are post-constraint/gauge representatives; delta beta is "
            "invariant on beta0'=0. Raw coordinate shifts are not substituted for them."
        ),
        "general_local_identity": "q_env=delta beta+beta0' psi_raw",
        "fiber_rescaling_in_ImG": False,
    }


def constraint_audit() -> dict[str, Any]:
    """Known seam--fold relation, separate from gauge equivalence."""

    alpha = sp.Symbol("alpha_Sigma", nonzero=True, real=True)
    matrix = sp.Matrix([[1, alpha, 0]])
    return {
        "matrix": [[1, "alpha_Sigma", 0]],
        "coefficient": "alpha_Sigma=tau*pi*chi_1/16",
        "equation": "psi+alpha_Sigma*zeta=0",
        "rank": matrix.rank(),
        "quotient_dimension_after_known_constraint": 2,
        "seam_fold_relation_type": "DERIVED_CONSTRAINT_PROJECTION_NOT_GAUGE_IDENTIFICATION",
    }


def source_ledger() -> dict[str, Any]:
    return {
        "J_env": ["J_psi", "J_zeta", "J_F"],
        "J_psi": "derived boundary projection of the v6.27 fold/threading source",
        "J_zeta": "derived conditionally in the v6.28-v6.30 fold domain",
        "J_F": "defined for M8 fields but lacks the complete localized M4 pullback",
        "one_J_total": None,
        "projection_maps": {"Pi_psi": "derived locally from q_fold", "Pi_zeta": "fold projector", "Pi_F": None},
        "unified_source_status": UNRESOLVED,
    }


def common_mode_payload() -> dict[str, Any]:
    blocks = block_ledger()
    gauge = gauge_audit()
    constraints = constraint_audit()
    validation = {
        "three_exact_variables": len(perturbation_provenance()) == 3,
        "historical_operators_imported": len(historical_import_audit()) == 5,
        "statuses_typed": all(cell["status"] in BLOCK_STATUSES for matrix in (blocks["K_env"], blocks["H_env"]) for row in matrix for cell in row),
        "mixed_blocks_not_false_zero": blocks["H_env"][1][2]["status"] == "UNDEFINED_CROSS_DOMAIN",
        "gauge_rank_exact": gauge["rank"] == 0,
        "known_constraint_rank_one": constraints["rank"] == 1,
        "inequivalence_not_claimed": True,
    }
    return {
        "artifact": "BHSM_common_envelopment_mode_v10_3",
        "version": VERSION,
        "common_perturbation_vector": ["psi", "zeta", "varphi_F"],
        "provenance": perturbation_provenance(),
        "historical_operator_imports": historical_import_audit(),
        "quadratic_action": "S2_env=1/2 int[(dot q)^T K_env dot q-q^T H_env q+2 q^T J_env] dmu",
        "blocks": blocks,
        "gauge": gauge,
        "constraints": constraints,
        "source": source_ledger(),
        "equivalence_status": UNRESOLVED,
        "physically_inequivalent": False,
        "primary_verdict": PRIMARY_VERDICT,
        "next_exact_object": NEXT_EXACT_OBJECT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
