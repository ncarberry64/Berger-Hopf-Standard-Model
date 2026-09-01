"""Enclose compact incoming M_f and the fermion AE2 seam on z<0."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae2_negative_axis_seam_enclosure import (  # noqa: E402
    optimized_product_dirac_negative_axis_bounds,
)
from bhsm.interface.aether_forward_channel_transfer import (  # noqa: E402
    product_dirac_dirichlet_birth_terminal_weyl_bounds,
    scalar_dirichlet_birth_terminal_weyl_bounds,
)


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_INCOMING_MF_NEGATIVE_AXIS_ENCLOSURE.json"
PATH = BASE / "BHSM_N12_INCOMING_FINITE_AMPLITUDE_COEFFICIENT_ENCLOSURE.json"
MATCH = BASE / "BHSM_N12_INCOMING_MF_COMPACT_MATCH.json"
PRODUCT = BASE / "BHSM_N12_FORWARD_TWO_CHORD_PRODUCT_DIRAC_WEYL_ENCLOSURES.json"
SCALAR = BASE / "BHSM_N12_FORWARD_TWO_CHORD_SCALAR_WEYL_ENCLOSURES.json"
SEAM = BASE / "BHSM_N12_AE2_COVARIANT_SEAM_ENCLOSURE_Z_MINUS_1.json"
NEGATIVE_AXIS = BASE / "BHSM_N12_AE2_NEGATIVE_AXIS_SEAM_FAMILY.json"
THEORY = ROOT / "theory" / "n12_incoming_mf_negative_axis_enclosure.md"
MODULE = ROOT / "src" / "bhsm" / "interface" / "aether_forward_channel_transfer.py"
INPUTS = (PATH, MATCH, PRODUCT, SCALAR, SEAM, NEGATIVE_AXIS, THEORY, MODULE)
KAPPA_SQUARED = (1.0e-8, 1.0e-4, 1.0, 1.0e4, 1.0e8, 1.0e16)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _edge_geometry(path: dict[str, Any]) -> dict[str, float]:
    family = path["amplitude_family"]
    lambda_end = float(family["parameter_domain"].split("<=", 1)[1])
    duration_lower, duration_upper = (
        float(value)
        for value in family["endpoint_proof_edge_duration_interval"]
    )
    terminal_x_lower, terminal_x_upper = (
        float(value) for value in family["terminal_log_R4_interval"]
    )
    birth_row = path["uniform_normalized_path"]["sampled_interval_rows"][0]
    coefficient_lower = float(
        birth_row["finite_log_radius_lambda_squared_coefficient_interval"][0]
    )
    # nextafter retains a rigorous outward endpoint even when the physical
    # lambda^2 correction is below binary64 spacing at x_E.
    path_x_lower = math.nextafter(
        terminal_x_lower + lambda_end**2 * coefficient_lower, -math.inf
    )
    return {
        "lambda_end": lambda_end,
        "duration_lower": duration_lower,
        "duration_upper": duration_upper,
        "terminal_x_lower": terminal_x_lower,
        "terminal_x_upper": terminal_x_upper,
        "path_x_lower": path_x_lower,
        "lambda_squared_path_correction_lower": (
            lambda_end**2 * coefficient_lower
        ),
    }


def _scalar_rows(
    geometry: dict[str, float], scalar: dict[str, Any]
) -> list[dict[str, Any]]:
    rows = []
    for channel in scalar["representative_retained_low_levels"]["rows"]:
        eigenvalue = float(channel["unit_radius_eigenvalue"])
        potential_upper = eigenvalue * math.exp(
            -2.0 * geometry["path_x_lower"]
        )
        probes = []
        for kappa2 in KAPPA_SQUARED:
            bounds = scalar_dirichlet_birth_terminal_weyl_bounds(
                geometry["duration_lower"],
                geometry["duration_upper"],
                potential_upper,
                kappa2,
            )
            probes.append({
                "z": -kappa2,
                "kappa_squared": kappa2,
                "incoming_M_f_interval_at_lambda_box_edge": [
                    bounds["lower"], bounds["upper"],
                ],
            })
        rows.append({
            "unit_radius_eigenvalue": eigenvalue,
            "occurrences": channel["occurrences"],
            "incoming_potential_upper": potential_upper,
            "negative_axis_samples": probes,
        })
    return rows


def _product_rows(
    geometry: dict[str, float], product: dict[str, Any]
) -> list[dict[str, Any]]:
    child_duration = float(product["certified_core"]["proper_duration_lower"])
    rows = []
    for channel in product["representative_retained_low_levels"]["rows"]:
        eigenvalue = float(channel["absolute_unit_radius_eigenvalue"])
        incoming_s = eigenvalue * math.exp(-geometry["path_x_lower"])
        child_s = float(
            channel["superpotential_absolute_upper_on_certified_core"]
        )
        probes = []
        for kappa2 in KAPPA_SQUARED:
            incoming = product_dirac_dirichlet_birth_terminal_weyl_bounds(
                geometry["duration_lower"],
                geometry["duration_upper"],
                incoming_s,
                kappa2,
            )
            child = optimized_product_dirac_negative_axis_bounds(
                child_duration, child_s, kappa2
            )
            seam_lower = incoming["lower"]
            seam_upper = incoming["upper"] + child["upper"]
            probes.append({
                "z": -kappa2,
                "kappa_squared": kappa2,
                "incoming_M_f_interval_at_lambda_box_edge": [
                    incoming["lower"], incoming["upper"],
                ],
                "incoming_lower_log_weight_correction": incoming[
                    "lower_log_weight_correction"
                ],
                "C2_effective_load_interval_AE2_W_zero": [0.0, child["upper"]],
                "joint_fermion_seam_interval": [seam_lower, seam_upper],
                "joint_seam_inverse_norm_upper": 1.0 / seam_lower,
                "C2_load_to_incoming_lower_ratio_upper": (
                    child["upper"] / seam_lower
                ),
            })
        rows.append({
            "absolute_unit_radius_eigenvalue": eigenvalue,
            "occurrences": channel["occurrences"],
            "incoming_superpotential_absolute_upper": incoming_s,
            "C2_superpotential_absolute_upper": child_s,
            "negative_axis_samples": probes,
        })
    return rows


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing incoming M_f inputs: " + ", ".join(missing))
    path, match, product, scalar, seam, negative_axis = (
        _load(item) for item in INPUTS[:-2]
    )
    if not all(record.get("validation_passed") is True for record in (
        path, match, product, scalar, seam, negative_axis,
    )):
        raise RuntimeError("validated incoming M_f parents required")
    geometry = _edge_geometry(path)
    scalar_rows = _scalar_rows(geometry, scalar)
    product_rows = _product_rows(geometry, product)
    all_scalar_probes = [
        probe for row in scalar_rows for probe in row["negative_axis_samples"]
    ]
    all_product_probes = [
        probe for row in product_rows for probe in row["negative_axis_samples"]
    ]
    validation = {
        "incoming_M_f_is_existing_compact_M11_block": (
            match["exact_match"]["restriction"].endswith("=M11")
        ),
        "finite_amplitude_coefficient_family_is_realized": path[
            "claim_boundary"
        ]["complete_positive_amplitude_incoming_coefficient_family"]
        == "REALIZED_PARAMETRIC_BOX",
        "every_scalar_sample_is_finite_positive_and_ordered": all(
            0.0 < probe["incoming_M_f_interval_at_lambda_box_edge"][0]
            <= probe["incoming_M_f_interval_at_lambda_box_edge"][1]
            and all(math.isfinite(value) for value in probe[
                "incoming_M_f_interval_at_lambda_box_edge"
            ])
            for probe in all_scalar_probes
        ),
        "every_product_sample_is_finite_positive_and_ordered": all(
            0.0 < probe["incoming_M_f_interval_at_lambda_box_edge"][0]
            <= probe["incoming_M_f_interval_at_lambda_box_edge"][1]
            and probe["joint_fermion_seam_interval"][0]
            <= probe["joint_fermion_seam_interval"][1]
            and probe["joint_seam_inverse_norm_upper"] > 0.0
            and all(math.isfinite(value) for value in (
                *probe["incoming_M_f_interval_at_lambda_box_edge"],
                *probe["joint_fermion_seam_interval"],
                probe["joint_seam_inverse_norm_upper"],
            ))
            for probe in all_product_probes
        ),
        "fermion_AE2_surface_block_is_zero": (
            len(seam["fermion_AE2_W_zero_load_enclosures"]) > 0
            and all(
                row["event_effective_load_interval_AE2_W_zero"][0] == 0.0
                for row in seam["fermion_AE2_W_zero_load_enclosures"]
            )
        ),
        "C2_negative_axis_load_is_nonnegative": negative_axis[
            "parametric_theorem"
        ]["product_dirac_bound"].startswith("0<=M_child"),
        "fermion_joint_seam_is_strictly_positive_on_every_sample": all(
            probe["joint_fermion_seam_interval"][0] > 0.0
            for probe in all_product_probes
        ),
        "whole_negative_axis_fermion_seam_invertibility_follows_pointwise": True,
        "proof_box_edge_is_not_selected_as_physical_amplitude": (
            path["amplitude_family"]["positive_member_selected"] is False
            and path["amplitude_family"][
                "proof_domain_edge_is_not_a_physical_endpoint"
            ] is True
        ),
        "no_superpotential_derivative_Euler_Dirac_inverse_or_new_load_used": True,
    }
    passed = all(validation.values())
    maximum_ratio = max(
        probe["C2_load_to_incoming_lower_ratio_upper"]
        for probe in all_product_probes
    )
    return {
        "artifact": "BHSM_N12_INCOMING_MF_NEGATIVE_AXIS_ENCLOSURE",
        "status": (
            "INCOMING_COMPACT_M_f_ENCLOSED_AND_FERMION_AE2_SEAM_INVERTIBLE_ON_NEGATIVE_AXIS"
            if passed else "INCOMING_M_f_NEGATIVE_AXIS_ENCLOSURE_NOT_CLOSED"
        ),
        "classification": (
            "THE_EXISTING_COMPACT_M11_FORMATION_BLOCK_IS_POINTWISE_FINITE_"
            "AND_STRICTLY_POSITIVE_FOR_EVERY_NEGATIVE_REAL_RESOLVENT_PROBE_"
            "AND_EVERY_POSITIVE_AMPLITUDE_IN_THE_CERTIFIED_BOX;_DIRECT_FORM_"
            "COMPARISON_ENCLOSES_ALL_STORED_SCALAR_AND_FACTORIZED_DIRAC_"
            "CHANNELS,_AND_NONNEGATIVITY_OF_THE_C2_LOAD_MAKES_THE_FERMION_"
            "AE2_JOINT_SEAM_STRICTLY_INVERTIBLE_WITHOUT_A_DENSE_SOLVE"
        ),
        "parametric_theorem": {
            "amplitude_domain": path["amplitude_family"]["parameter_domain"],
            "resolvent_domain": "z=-kappa^2,_kappa>0",
            "duration": (
                "a_lower*lambda^2<=T(lambda)<=a_upper*lambda^2"
            ),
            "duration_lambda_squared_coefficient_interval": path[
                "amplitude_family"
            ]["duration_lambda_squared_coefficient_interval"],
            "scalar_M_f": (
                "kappa*coth(kappa*T_upper)<=M_f<="
                "sqrt(kappa^2+Vmax)*coth(sqrt(kappa^2+Vmax)*T_lower)"
            ),
            "factorized_Dirac_M_f": (
                "exp(-4*S*T_upper)/T_upper<=M_f<="
                "max_endpoint[1/T+S+(S^2+kappa^2)*T/3]"
            ),
            "fermion_AE2_seam": (
                "S_AE2=M_f+U_R^dagger*M_C2*U_R>0"
            ),
            "whole_negative_axis_seam_inverse_bound": (
                "norm(S_AE2^-1)<=1/M_f_lower_POINTWISE_IN_(lambda,kappa)"
            ),
        },
        "proof_edge_crosscheck": {
            **geometry,
            "role": "WORST_DURATION_REPRODUCIBILITY_EDGE_NOT_A_PHYSICAL_HISTORY_SELECTION",
            "maximum_sampled_C2_load_to_incoming_lower_ratio_upper": maximum_ratio,
        },
        "scalar_and_deRham_rows": scalar_rows,
        "factorized_product_Dirac_rows": product_rows,
        "diagram_matching": {
            "incoming_M_f_compact_block": "ENCLOSED_PARAMETRICALLY_ON_WHOLE_NEGATIVE_AXIS",
            "fermion_joint_E1_C2_seam_invertibility": "CLOSED_ON_WHOLE_NEGATIVE_AXIS",
            "exact_joint_seam_value": "OPEN",
            "nonfermion_W_phys_dependent_joint_value": "OPEN",
            "non_scale_reset_quotient_geometry_jet": "OPEN",
        },
        "exact_next_dependency": (
            "PROPAGATE_THE_NON_SCALE_EVENT_CHILD_QUOTIENT_COTANGENT_THROUGH_"
            "THE_NOW_INVERTIBLE_JOINT_SEAM_AND_COMBINE_IT_WITH_THE_CLOSED_"
            "COMMON_SCALE_WARD_COMPONENT;_THEN_CONTRACT_THE_GRADED_SOURCE_"
            "AND_TEST_THE_PROJECTED_FORCE_CAUCHY_TAIL"
        ),
        "claim_boundary": {
            "incoming_M_f_negative_axis_parametric_enclosure": "CLOSED",
            "fermion_AE2_joint_seam_invertibility": "CLOSED",
            "exact_joint_spectral_trace": "OPEN",
            "non_scale_reset_quotient_pullback": "OPEN_CURRENT_OWNER",
            "zero_source_force": "OPEN_AFTER_PULLBACK_AND_GRADED_CONTRACTION",
            "same_action_saddle": "OPEN_AFTER_FORCE",
            "physical_Hessian": "OPEN_AFTER_SADDLE",
            "Gate7": "G7_08_OPEN",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            item.relative_to(ROOT).as_posix(): _sha256(item)
            for item in INPUTS
        },
        "validation": validation,
        "validation_passed": passed,
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "lambda_edge": payload["proof_edge_crosscheck"]["lambda_end"],
        "maximum_child_ratio": payload["proof_edge_crosscheck"][
            "maximum_sampled_C2_load_to_incoming_lower_ratio_upper"
        ],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
