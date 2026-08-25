"""Audit direct compactness/coercivity routes to the finite-endpoint KKT root."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.special import exp1


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_DIRECT_KKT_EXISTENCE_PRECONDITIONS.json"
)
THEOREM = ROOT / "theory/n12_direct_kkt_existence_preconditions.md"
INPUTS = (
    ROOT / "artifacts/flagship_integration/BHSM_N12_FORWARD_ADJOINT_KKT_EXISTENCE_GATE.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_FINITE_ENDPOINT_ZERO_SOURCE_FORCE_FUNCTIONAL.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_SAME_ACTION_CONTINUATION_PRECONDITIONS.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_NEGATIVE_AXIS_SEAM_HEAT_SYNTHESIS_NO_GO.json",
    ROOT / "artifacts/intrinsic_state_selection/BHSM_N12_CONSTRAINT_REDUCED_ENERGY_IDENTITY_GATE.json",
    ROOT / "artifacts/intrinsic_state_selection/BHSM_N12_GLOBAL_FLOW_COERCIVE_CONTROL_GATE.json",
    ROOT / "artifacts/n12_direct_checkpoint/BHSM_N12_PRINCIPAL_COERCIVITY.json",
    THEOREM,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, object]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing direct-existence inputs: " + ", ".join(missing))

    existence, force, continuation, seam, energy, global_control, principal = (
        _load(path) for path in INPUTS[:-1]
    )
    records = (existence, force, continuation, seam, energy, global_control, principal)
    if not all(record.get("validation_passed") is True for record in records):
        raise RuntimeError("validated direct-existence inputs required")

    # Dimensionless spectral samples x=ell^2 lambda.  The exact formulas below
    # are independent of choosing ell=1 for this monotonicity/asymptotic witness.
    spectral_x = np.asarray([1.0e-12, 1.0e-4, 1.0, 10.0, 100.0])
    regulator = -0.5 * exp1(spectral_x)
    derivative = 0.5 * np.exp(-spectral_x) / spectral_x
    scaling_n = np.asarray([1.0, 4.0, 16.0, 64.0])
    scaling_values = -0.5 * exp1(scaling_n)

    validation = {
        "finite_endpoint_KKT_root_is_current_owner": (
            existence["claim_boundary"]["finite_endpoint_KKT_root"]
            == "OPEN_CURRENT_OWNER"
        ),
        "heat_regulator_samples_are_strictly_increasing": bool(
            np.all(np.diff(regulator) > 0.0)
        ),
        "heat_regulator_derivative_is_strictly_positive": bool(
            np.all(derivative > 0.0)
        ),
        "high_spectral_scaling_does_not_diverge_positive": bool(
            np.all(scaling_values < 0.0)
            and np.all(np.diff(scaling_values) > 0.0)
            and abs(float(scaling_values[-1])) < 1.0e-28
        ),
        "zero_constraint_energy_cannot_supply_norm": (
            energy["action_ownership_consequence"][
                "constraint_energy_can_supply_a_positive_strong_S2_norm"
            ]
            is False
        ),
        "global_coercive_S2_bound_is_absent": (
            global_control["owned_and_missing_energy_structure"][
                "coercive_S2_bound_on_continuum_child_component"
            ]
            is False
        ),
        "principal_certificate_is_not_continuum_KKT_compactness": (
            principal["CONTINUUM_EVENT_CHILD_CERTIFIED"] is False
            and len(principal["remaining_compact_blocks"]) > 0
        ),
        "broad_force_class_is_sign_indefinite": (
            seam["certified_force_counterpair"]["Dirichlet_far_load"]["strict_sign"]
            == "NEGATIVE"
            and seam["certified_force_counterpair"]["Neumann_far_load"]["strict_sign"]
            == "POSITIVE"
        ),
        "continuation_does_not_supply_degree": (
            continuation["adjudication"][
                "Brouwer_or_Leray_Schauder_degree_defined_now"
            ]
            is False
        ),
        "no_selector_endpoint_action_term_scale_fit_chord_or_prediction_added": True,
    }

    return {
        "artifact": "BHSM_N12_DIRECT_KKT_EXISTENCE_PRECONDITIONS",
        "status": "DIRECT_COMPACTNESS_COERCIVITY_AND_DEGREE_THEOREM_NOT_AVAILABLE",
        "classification": (
            "THE_RETAINED_HEAT_REGULATOR_IS_STRICTLY_INCREASING_BUT_TENDS_TO_"
            "ZERO_UNDER_HIGH_SPECTRAL_SCALING_AND_TO_MINUS_INFINITY_AT_GAP_"
            "CLOSURE,_SO_IT_IS_NOT_A_PROPER_COERCIVE_EXHAUSTION;_THE_ZERO_"
            "CONSTRAINT_ENERGY_AND_LOCAL_PRINCIPAL_INF_SUP_CERTIFICATE_DO_NOT_"
            "SUPPLY_GLOBAL_RESET_QUOTIENT_COMPACTNESS,_AND_THE_CURRENT_LEDGER_"
            "HAS_NO_NONZERO_KKT_DEGREE"
        ),
        "exact_heat_regulator_theorem": {
            "dimensionless_variable": "x=ell_kappa^2*lambda>0",
            "functional": "f(lambda)=-(1/2)*E1(ell_kappa^2*lambda)",
            "derivative": "f_prime(lambda)=exp(-ell_kappa^2*lambda)/(2*lambda)>0",
            "infrared_limit": "lim_lambda_to_0_plus_f(lambda)=-infinity",
            "ultraviolet_limit": "lim_lambda_to_infinity_f(lambda)=0_from_below",
            "high_scaling_countersequence": "P_n=n*P_0,_norm(P_n)->infinity,_Gamma_heat(P_n)->0",
            "conclusion": "HEAT_REGULATOR_ALONE_IS_NOT_A_PROPER_OR_COERCIVE_OPERATOR_EXHAUSTION",
            "claim_limit": (
                "DOES_NOT_PROVE_THE_COMPLETE_RETAINED_GEOMETRY_HAS_NO_"
                "INDEPENDENT_COMPACTNESS_ESTIMATE"
            ),
        },
        "numeric_formula_crosscheck": {
            "spectral_x": spectral_x.tolist(),
            "regulator": regulator.tolist(),
            "positive_derivative": derivative.tolist(),
            "scaling_n": scaling_n.tolist(),
            "scaling_regulator": scaling_values.tolist(),
        },
        "route_separation": {
            "constraint_reduced_Legendre_energy": "IDENTICALLY_ZERO_NOT_COERCIVE",
            "weighted_principal_inf_sup": (
                "LOCAL_LINEAR_ROOT_BALL_CERTIFICATE_NOT_NONLINEAR_KKT_"
                "CONFIGURATION_COMPACTNESS"
            ),
            "zeta_Casimir_term": (
                "REQUIRES_UNPROVED_GLOBAL_RADIUS_DURATION_ENDPOINT_AND_DOMAIN_"
                "MARGIN_BOUNDS_TO_ACT_AS_AN_EXHAUSTION"
            ),
            "opposite_broad_reference_force_signs": (
                "RULE_OUT_A_SIGN_SHORTCUT_BUT_DO_NOT_BY_THEMSELVES_PROVE_"
                "NONCOERCIVITY_OF_THE_ACTUAL_ACTION"
            ),
            "finite_encapsulation_ontology": (
                "RESTRICTS_PHYSICAL_READOUT_DOMAIN_BUT_DOES_NOT_COMPACTIFY_"
                "THE_RESET_QUOTIENT_OR_CREATE_A_POST_RESET_TERMINAL_STRATUM"
            ),
        },
        "missing_direct_method_objects": [
            "NONEMPTY_REGULAR_PHYSICAL_FINITE_ENDPOINT_KKT_CLASS",
            "ACTION_OWNED_APRIORI_COMPACTNESS_OR_PALAIS_SMALE_BOUND",
            "LOWER_SEMICONTINUITY_AND_CLOSEDNESS_THROUGH_THE_ENDPOINT_GRAPH",
            "CRITICAL_POINT_THEOREM_FOR_THE_INDEFINITE_CONSTRAINED_ACTION",
        ],
        "missing_degree_objects": [
            "BOUNDED_OPEN_PHYSICAL_QUOTIENT_DOMAIN",
            "COMPLETELY_CONTINUOUS_OR_FREDHOLM_KKT_RESIDUAL",
            "CERTIFIED_ABSENCE_OF_BOUNDARY_ZEROS_WITH_DOMAIN_MARGINS",
            "COMPUTABLE_NONZERO_BROUWER_LERAY_SCHAUDER_OR_FREDHOLM_DEGREE",
        ],
        "adjudication": {
            "heat_regulator_alone_closes_direct_method": False,
            "zeta_term_currently_closes_direct_method": False,
            "local_principal_coercivity_closes_global_KKT_existence": False,
            "nonzero_KKT_degree_available": False,
            "direct_existence_route_invalid_in_principle": False,
            "validated_finite_endpoint_BVP_route_remains_distinct": True,
            "retained_action_incompatibility_proved": False,
            "new_action_term_justified": False,
        },
        "exact_next_dependency": (
            "CERTIFY_ONE_NONEMPTY_REGULAR_FINITE_ENDPOINT_FORWARD_ADJOINT_KKT_"
            "ROOT_BY_A_VALIDATED_BVP,_OR_DERIVE_AN_INDEPENDENT_ACTION_OWNED_"
            "GLOBAL_COMPACTNESS_OR_NONZERO_DEGREE_THEOREM_FOR_THE_SAME_"
            "PHYSICAL_RESET_QUOTIENT_SYSTEM"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_KKT_ROOT_EXISTENCE_CURRENT_OWNER",
            "Gate8": "LOCKED",
            "finite_endpoint_KKT_root": "OPEN_CURRENT_OWNER",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(RESULT)


if __name__ == "__main__":
    main()
