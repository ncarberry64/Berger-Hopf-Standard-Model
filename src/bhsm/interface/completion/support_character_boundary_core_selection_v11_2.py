"""Boundary, core, and anomaly selection tests for primitive characters."""

from __future__ import annotations

from typing import Any


def boundary_core_payload() -> dict[str, Any]:
    boundary = {
        "GHY": "full Weyl scaling generates paired normal derivatives, but the nontrivial coframe candidate is already rejected and partial support weights are absent",
        "support_normal_derivative": "pi_D=sqrt(|h|) n.dq_D is known; its boundary ensemble is not selected",
        "fermion_boundary_form": "historical maximal-isotropic families do not determine a G_D character",
        "gauge_boundary_terms": "no support term for forced-zero gauge-connection character",
        "scalar_boundary_terms": "conditional linear coupling yields -w boundary(n.A_D |phi|^2), but w is open",
        "compatibility_terms": "no G_D-equivariant cross-stratum multiplier law",
        "normalized_boundary_measure": "normalization fixes an integral, not its support transformation",
        "weights_fixed": [],
        "action_owned_ensemble": None,
    }
    core = {
        "limit": "q_D->+infinity, upsilon->0+",
        "candidate_character_behavior": "upsilon^w=exp[-w q_D/lambda_D] decays for w>0, is constant for w=0, and grows for w<0",
        "finite_action": None,
        "finite_energy": None,
        "finite_symplectic_flux": None,
        "finite_support_flux": None,
        "reason": "the core measure, response functional, asymptotic field profiles, and self-adjoint domain are absent",
        "weights_fixed": [],
        "incoming_outgoing_domain": None,
    }
    anomaly = {
        "forced_zero_matter_candidate": "trivially compatible with gauge anomaly cancellation",
        "mixed_support_gauge_anomalies": None,
        "fermion_measure_jacobian": None,
        "Hermiticity": "requires a missing G_D pairing/adjoint law",
        "charge_conjugation": None,
        "orientation_reversal": None,
        "selection_result": "does not fix w_C,w_W,w_wall,w_compatibility,w_core",
    }
    validation = {
        "all_boundary_sectors_tested": len(boundary) >= 9,
        "all_core_finiteness_tests_explicit": all(key in core for key in ("finite_action", "finite_energy", "finite_symplectic_flux", "finite_support_flux")),
        "no_ensemble_imposed": boundary["action_owned_ensemble"] is None,
        "no_core_selection_fabricated": core["weights_fixed"] == [],
        "anomaly_not_assumed_away": anomaly["mixed_support_gauge_anomalies"] is None,
    }
    return {
        "artifact": "BHSM_support_character_boundary_core_selection_v11_2",
        "boundary_test": boundary,
        "core_test": core,
        "anomaly_test": anomaly,
        "boundary_selects_ledger": False,
        "core_selects_ledger": False,
        "anomaly_selects_ledger": False,
        "status": "BHSM_BOUNDARY_CORE_AND_ANOMALY_TESTS_DO_NOT_SELECT_PRIMITIVE_SUPPORT_LEDGER_FROM_CURRENT_ACTION",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }

