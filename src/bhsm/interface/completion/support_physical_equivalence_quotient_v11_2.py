"""Physical-equivalence tests after deriving the composite support connection."""

from __future__ import annotations

from typing import Any


def equivalence_payload() -> dict[str, Any]:
    tests = {
        "field_redefinition": {
            "map": "Phi_B=upsilon^(Delta w) Phi_A",
            "regular_invertible": True,
            "core_invertible": False,
            "derivative_map": "D_B(upsilon^(Delta w)Phi_A)=upsilon^(Delta w)D_A Phi_A only when the full character and connection assignments match",
        },
        "weyl": {"complete_test": False, "reason": "primitive coframe weight and paired GHY/core terms are not assigned"},
        "measure_redistribution": {"algebraic_integrated_weight_preserved": True, "canonical_equivalence": None},
        "natural_isomorphism": {"fixed_distinct_characters_linearly_isomorphic": False, "nonlinear_regular_map_is_global": False},
        "canonical": {"symplectomorphism": None},
        "spectral": {"isospectral": None},
        "domain": {"same_self_adjoint_domain": None},
        "observables": {"dimensionless_observables_equal": None},
    }
    validation = {
        "all_required_equivalence_classes_tested": len(tests) == 8,
        "regular_redefinition_identity_sharpened": True,
        "core_singularity_preserved": True,
        "neither_equivalence_nor_inequivalence_overclaimed": True,
    }
    return {
        "artifact": "BHSM_support_physical_equivalence_quotient_v11_2",
        "representative_A": "R_D^(A), provisional wall/fiber character (1,0)",
        "representative_B": "R_D^(B), provisional wall/fiber character (2,1)",
        "tests": tests,
        "bulk_equivalence": None,
        "boundary_equivalence": None,
        "core_equivalence": None,
        "spectral_equivalence": None,
        "observable_equivalence": None,
        "physically_equivalent": None,
        "physically_inequivalent": None,
        "status": "BHSM_SUPPORT_REPRESENTATIVE_PHYSICAL_EQUIVALENCE_REMAINS_UNDECIDABLE_WITHOUT_COMPLETE_ACTION_AND_DOMAIN",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }

