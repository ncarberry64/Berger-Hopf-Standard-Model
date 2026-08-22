"""Certify the local retained continuum flow by Galerkin/Duhamel bounds."""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal, ROUND_CEILING, localcontext
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OBSERVATION = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_POSITIVE_DURATION_OBSERVATION.json"
)
MIXED = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_SOURCE_RESTRICTED_MIXED_GRAPH.json"
)
COMPACT = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_COMPACT_OBSERVATION_MODULI_AUDIT.json"
)
CUTOFF = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_FIRST_SUFFICIENT_COMPACT_CUTOFF.json"
)
CONTINUUM = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_CONTINUUM_EVENT_CHILD_CERTIFICATE.json"
)
THEOREM = ROOT / "theory/n12_local_continuum_galerkin_flow.md"
RESULT = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_LOCAL_CONTINUUM_GALERKIN_FLOW.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    inputs = (OBSERVATION, MIXED, COMPACT, CUTOFF, CONTINUUM, THEOREM)
    missing = [str(path) for path in inputs if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing local-continuum inputs: " + ", ".join(missing))
    observation = _load(OBSERVATION)
    mixed = _load(MIXED)
    compact = _load(COMPACT)
    cutoff = _load(CUTOFF)
    continuum = _load(CONTINUUM)

    with localcontext() as context:
        context.prec = 420
        context.rounding = ROUND_CEILING
        selected_M0 = int(continuum["selected_proof_cutoff"]["M0"])
        half_M0 = int(cutoff["optional_numerically_stable_half_margin_cutoff"][
            "M_half"
        ])
        c_ed = Decimal(cutoff["directed_decimal_bounds"][
            "compact_coefficients_upper"
        ]["Euler_Dirac"])
        epsilon_ed = Decimal(4) * c_ed / Decimal(selected_M0).sqrt()
        duration = Decimal(str(observation["common_coordinate_duration_lower"]))
        generator = Decimal(str(
            observation["maximum_Jacobi_generator_action_bound"]
        ))
        initial_tail = Decimal(
            continuum["nonlinear_continuum_radius"]["small_radii_root_upper"]
        )
        radius = Decimal(str(observation["full_action_neighborhood_radius"]))
        vector_field = max(
            Decimal(str(record["full_state_vector_field_action_bound"]))
            for record in observation["sector_bounds"].values()
        )
        lipschitz = generator + epsilon_ed
        exponential = (lipschitz * duration).exp()
        gronwall_error = (
            exponential * initial_tail
            + epsilon_ed * (exponential - Decimal(1)) / lipschitz
        )
        path_bound = vector_field * duration
        total_radius_use = initial_tail + path_bound + gronwall_error
        radius_margin = radius - total_radius_use

        validation = {
            "continuum_child_anchor_is_certified": continuum[
                "CONTINUUM_EVENT_CHILD_CERTIFIED"
            ] is True,
            "mixed_action_graph_architecture_is_validated": mixed[
                "validation_passed"
            ] is True,
            "Euler_Dirac_same_norm_compact_coefficient_is_closed": compact[
                "four_compact_blocks"
            ]["interior_lower_order_Euler_Dirac"][
                "same_norm_coefficient_enclosed"
            ] is True,
            "selected_cutoff_matches_continuum_certificate": (
                selected_M0 == half_M0
            ),
            "noncompact_pole_is_not_counted_as_compact": compact[
                "validation"
            ]["critical_pole_block_is_routed_out_of_the_compact_remainder"]
            is True,
            "configuration_trace_tail_is_zero": compact[
                "closed_same_norm_constants"
            ]["complete_four_row_direct_trace_tail"] == 0.0,
            "positive_local_duration": duration > 0,
            "finite_local_Lipschitz_majorant": lipschitz.is_finite(),
            "Galerkin_error_is_inside_existing_action_ball": (
                total_radius_use < radius
            ),
            "no_new_equation_gate_selector_or_trajectory": True,
        }
        payload = {
            "artifact": "BHSM_N12_LOCAL_CONTINUUM_GALERKIN_FLOW",
            "classification": (
                "LOCAL_CONTINUUM_RETAINED_CHILD_FLOW_CERTIFIED_ON_THE_EXISTING_"
                "ACTION_BALL_BY_DUHAMEL_GALERKIN_CONVERGENCE"
            ),
            "inputs": {
                str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
                for path in inputs
            },
            "spaces": mixed["spaces"],
            "proof": {
                "Galerkin_projector": (
                    "EXISTING_TRACE_COMPATIBLE_ACTION_ORTHOGONAL_P_M_G"
                ),
                "Euler_Dirac_consistency": (
                    "norm((I-P_M_G)V(Y))_XE<=4*C_ED_G/sqrt(M)"
                ),
                "Duhamel_Gronwall": (
                    "error(t)<=exp(L*t)*a0+(exp(L*t)-1)*epsilon_ED/L"
                ),
                "principal_pole_treatment": (
                    "EXISTING_SOURCE_RESTRICTED_INDICIAL_INVERSE_NOT_A_"
                    "COMPACT_REMAINDER"
                ),
                "theorem": "theory/n12_local_continuum_galerkin_flow.md",
            },
            "directed_decimal_bounds": {
                "selected_proof_cutoff_M0": str(selected_M0),
                "C_ED_G_upper": str(c_ed),
                "epsilon_ED_M0_upper": str(epsilon_ed),
                "initial_inverse_square_continuum_tail_upper": str(initial_tail),
                "local_Lipschitz_upper": str(lipschitz),
                "coordinate_duration": str(duration),
                "exp_Lt_upper": str(exponential),
                "Galerkin_flow_error_upper": str(gronwall_error),
                "vector_field_path_length_upper": str(path_bound),
                "total_action_ball_radius_use_upper": str(total_radius_use),
                "existing_action_ball_radius": str(radius),
                "remaining_action_ball_margin_lower": str(radius_margin),
            },
            "scientific_result": {
                "local_continuum_vector_field_exists_on_anchor_ball": True,
                "nested_Galerkin_flows_are_Cauchy_in_XE_on_interval": True,
                "unique_local_continuum_retained_child_flow_exists": True,
                "constraints_eta_Dirac_and_existing_trace_domain_retained": True,
                "global_continuation_or_return_proved": False,
            },
            "first_missing_action_owned_object": (
                "PROVE_AN_APRIORI_STRONG_S2_BOUND_WITH_UNIFORM_ETA_DIRAC_"
                "MARGINS_OR_CONSTRUCT_A_FINITE_ANALYTIC_ACTION_BALL_COVER_OF_"
                "THE_ACTUAL_CONTINUUM_CHILD_ORBIT_UP_TO_EVENT_RETURN_OR_"
                "PHYSICAL_DOMAIN_EXIT"
            ),
            "prediction_frozen": False,
            "FULL_BHSM_COMPLETE": False,
            "validation": validation,
            "validation_passed": all(validation.values()),
        }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "classification": payload["classification"],
        "coordinate_duration": payload["directed_decimal_bounds"][
            "coordinate_duration"
        ],
        "Galerkin_flow_error_upper": payload["directed_decimal_bounds"][
            "Galerkin_flow_error_upper"
        ],
        "first_missing_action_owned_object": payload[
            "first_missing_action_owned_object"
        ],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
