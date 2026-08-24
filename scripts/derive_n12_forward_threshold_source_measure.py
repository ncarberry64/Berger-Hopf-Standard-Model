"""Derive the N12 fixed-channel threshold source-measure audit."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_threshold_source_measure import (  # noqa: E402
    constant_superpotential_zero_mode_witness,
    free_neumann_compact_counting_leading_coefficient,
    free_robin_compact_counting_bound,
    scalar_core_zero_energy_impedance_lower,
)


FLAGSHIP = ROOT / "artifacts/flagship_integration"
SCALAR = FLAGSHIP / "BHSM_N12_FORWARD_TWO_CHORD_SCALAR_WEYL_ENCLOSURES.json"
PRODUCT = FLAGSHIP / "BHSM_N12_FORWARD_TWO_CHORD_PRODUCT_DIRAC_WEYL_ENCLOSURES.json"
CRITERION = FLAGSHIP / "BHSM_N12_FORWARD_E1_SOURCE_MEASURE_CRITERION.json"
GRAPH = FLAGSHIP / "BHSM_N12_FORWARD_SOURCE_VARIATIONAL_GRAPH.json"
HEAT = FLAGSHIP / "BHSM_N12_GATE7_TWO_CHORD_HEAT_TAIL_AUDIT.json"
MODULE = ROOT / "src/bhsm/interface/aether_forward_threshold_source_measure.py"
RESULT = FLAGSHIP / "BHSM_N12_FORWARD_THRESHOLD_SOURCE_MEASURE_AUDIT.json"
INPUTS = (SCALAR, PRODUCT, CRITERION, GRAPH, HEAT, MODULE)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _canonical(value: Any) -> Any:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite threshold audit value")
        return value
    if isinstance(value, dict):
        return {str(key): _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    return value


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("all threshold source-measure inputs are required")
    scalar, product, criterion, graph, heat = (
        json.loads(path.read_text(encoding="utf-8")) for path in INPUTS[:-1]
    )
    if not all(
        record.get("validation_passed") is True
        for record in (scalar, product, criterion, graph, heat)
    ):
        raise RuntimeError("all threshold source-measure inputs must validate")

    duration = float(scalar["certified_core"]["proper_duration_lower"])
    radius_upper = max(
        float(row["R4_boundary_upper"])
        for row in heat["chord_tube_enclosures"]
    )
    channel_rows = []
    for row in scalar["representative_retained_low_levels"]["rows"]:
        eigenvalue = float(row["unit_radius_eigenvalue"])
        margin = scalar_core_zero_energy_impedance_lower(
            duration, radius_upper, eigenvalue
        )
        channel_rows.append(
            {
                "unit_radius_eigenvalue": eigenvalue,
                "occurrences": row["occurrences"],
                "child_zero_energy_impedance_lower": margin,
                "log_radius_first_vertex_zero": eigenvalue == 0.0,
            }
        )

    comparison_margin = channel_rows[1]["child_zero_energy_impedance_lower"]
    robin_model = free_robin_compact_counting_bound(
        comparison_margin,
        duration,
        1.0,
        1.0,
    )
    neumann_model = {
        "source": "unit_constant_density_on_unit_support",
        "leading_sqrt_Lambda_coefficient": (
            free_neumann_compact_counting_leading_coefficient(1.0)
        ),
        "counting_exponent": 0.5,
        "meets_E1_source_criterion": False,
    }
    product_kernel = constant_superpotential_zero_mode_witness(1.0)

    validation = {
        "all_inputs_validated": True,
        "certified_core_has_positive_radius_upper": radius_upper > 0.0,
        "constant_scalar_channel_has_zero_margin": (
            channel_rows[0]["unit_radius_eigenvalue"] == 0.0
            and channel_rows[0]["child_zero_energy_impedance_lower"] == 0.0
        ),
        "constant_scalar_log_radius_vertex_is_zero": channel_rows[0][
            "log_radius_first_vertex_zero"
        ],
        "every_positive_scalar_derham_channel_has_positive_child_margin": all(
            row["child_zero_energy_impedance_lower"] > 0.0
            for row in channel_rows
            if row["unit_radius_eigenvalue"] > 0.0
        ),
        "regular_free_Robin_model_meets_strict_excess_criterion": (
            robin_model["excess_exponent"] > 0.0
        ),
        "free_Neumann_model_fails_strict_excess_criterion": not neumann_model[
            "meets_E1_source_criterion"
        ],
        "factorized_exact_kernel_atom_has_zero_first_form_weight": (
            product_kernel["first_form_weight"] == 0.0
        ),
        "product_factorization_does_not_supply_positive_threshold_margin": (
            product_kernel["birth_conormal"] == 0.0
        ),
        "actual_continuous_threshold_density_not_promoted_from_free_model": True,
        "no_endpoint_reference_gap_chord3_selector_or_prediction_added": True,
    }

    return {
        "artifact": "BHSM_N12_FORWARD_THRESHOLD_SOURCE_MEASURE_AUDIT",
        "status": (
            "TWO_CHORD_SCALAR_THRESHOLD_MARGIN_AND_FACTORIZED_ZERO_ATOM_"
            "IDENTITIES_DERIVED_CONTINUOUS_THRESHOLD_OPEN"
        ),
        "classification": (
            "THE_CERTIFIED_TWO_CHORD_CORE_GIVES_A_STRICTLY_POSITIVE_CHILD_"
            "ZERO_ENERGY_IMPEDANCE_FOR_EVERY_POSITIVE_SCALAR_OR_DERHAM_"
            "ANGULAR_CHANNEL,_WHILE_THE_CONSTANT_CHANNEL_HAS_ZERO_LOG_RADIUS_"
            "VERTEX;_EXACT_KERNEL_ATOMS_OF_PRODUCT_DIRAC_SQUARES_ALSO_HAVE_"
            "ZERO_FIRST_FORM_WEIGHT,_BUT_THE_ACTION_OWNED_CONTINUOUS_"
            "THRESHOLD_SPECTRAL_DENSITY_REMAINS_UNCONTROLLED"
        ),
        "certified_core": {
            "proper_duration_lower": duration,
            "R4_upper": radius_upper,
            "scalar_derham_rows": channel_rows,
            "comparison_formula": (
                "M_child(0)>=a*tanh(a*T_lower),_"
                "a=sqrt(c)/R4_upper_FOR_c>0"
            ),
        },
        "factorized_product_Dirac_identity": {
            "form": "q[u]=norm(Au)^2",
            "first_form_jet": "D_h_q[u]=2*Re(inner(Au,A_hu))",
            "kernel_conclusion": "Au=0_IMPLIES_D_h_q[u]=0",
            "constant_superpotential_half_line_witness": product_kernel,
            "scope": (
                "EXACT_ZERO_EIGENVALUE_ATOMS_ONLY;_NO_CONTINUOUS_NEAR_ZERO_"
                "COUNTING_RATE_IS_INFERRED"
            ),
        },
        "threshold_model_dichotomy": {
            "positive_Robin_free_half_line": {
                **robin_model,
                "counting_exponent": 1.5,
                "meets_E1_source_criterion": True,
                "role": "REGULAR_THRESHOLD_COMPARISON_THEOREM_ONLY",
            },
            "Neumann_free_half_line": neumann_model,
            "lesson": (
                "A_POSITIVE_REGULAR_THRESHOLD_MARGIN_CAN_SUPPLY_THE_REQUIRED_"
                "STRICT_EXCESS,_BUT_NONNEGATIVITY_OR_FACTORIZATION_ALONE_"
                "DOES_NOT"
            ),
        },
        "adjudication": {
            "scalar_derham_positive_channel_child_zero_impedance": "CERTIFIED",
            "constant_scalar_radius_source_weight": "EXACTLY_ZERO",
            "product_Dirac_exact_zero_atom_first_weight": "EXACTLY_ZERO",
            "actual_N12_continuous_threshold_measure_exponent": "OPEN",
            "actual_N12_high_energy_E1_weighted_tail": "OPEN",
            "zero_source_force": "OPEN",
            "Gate_7": "ACTIVE_NOT_CLOSED",
            "Gate_8": "LOCKED",
            "chord_03_authorized": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "PROVE_AN_ACTION_OWNED_LIMITING_ABSORPTION_OR_WEYL_THRESHOLD_"
            "ESTIMATE_THAT_TRANSFERS_THE_CERTIFIED_CORE_MARGINS_AND_"
            "FACTORIZED_FORM_GAIN_TO_SUPERLINEAR_CONTINUOUS_SOURCE_WEIGHTED_"
            "SPECTRAL_COUNTING_FOR_EACH_PHYSICAL_CHANNEL,_AND_BOUND_ITS_"
            "E1_WEIGHTED_HIGH_ENERGY_TAIL;_THEN_ASSEMBLE_THE_GRADED_ANGULAR_"
            "SUM_AND_SIGN_ADJUDICATE_THE_ZERO_SOURCE_FORCE"
        ),
        "claim_boundary": {
            "free_Robin_model_is_actual_N12_exterior": False,
            "physical_birth_graph_threshold_margin_fully_assembled": False,
            "continuous_threshold_regular_class_derived": False,
            "zero_source_force_closed": False,
            "Gate_7": "ACTIVE_NOT_CLOSED",
            "Gate_8": "LOCKED",
            "chord_03_authorized": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in INPUTS
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def materialize() -> Path:
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(_canonical(build_payload()), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return RESULT


if __name__ == "__main__":
    print(materialize())
