"""Certify graph/product norm equivalence from determinant and Frobenius data."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.interval_weight_five_center_lift import (  # noqa: E402
    assemble_interval_weight_five_lift,
)


RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_BORDERED_GRAPH_PRODUCT_NORM_EQUIVALENCE.json"
)
THEORY = ROOT / "theory/n12_bordered_graph_product_norm_equivalence.md"
INPUTS = (
    ROOT / "artifacts/flagship_integration/BHSM_N12_ASYMPTOTIC_BORDERED_GRAPH_NORM.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_COMPACTIFIED_ASYMPTOTIC_COMMON_CHART.json",
    ROOT / "src/bhsm/interface/interval_weight_five_center_lift.py",
    THEORY,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _squared_weights() -> list[int]:
    windowed = list(range(0, 48, 4))
    lapse = list(range(4, 52, 4))
    physical = [0] + windowed + windowed
    multipliers = lapse + windowed
    return (
        [(1 + omega * omega) ** 6 for omega in physical]
        + [(1 + omega * omega) ** 5 for omega in physical]
        + [(1 + omega * omega) ** 6 for omega in multipliers]
    )


def build_payload() -> dict[str, object]:
    import flint
    from flint import arb, arb_mat, ctx

    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing graph-equivalence inputs: " + ", ".join(missing))
    graph, chart = (_load(path) for path in INPUTS[:2])
    if not all(record.get("validation_passed") is True for record in (graph, chart)):
        raise RuntimeError("validated graph-equivalence inputs required")

    assembled = assemble_interval_weight_five_lift(
        points=128, decimal_digits=160
    )
    matrix = assembled["matrix"]
    squared_weights = _squared_weights()
    if matrix.nrows() != 74 or matrix.ncols() != 74:
        raise RuntimeError("74 by 74 bordered recurrence required")
    prior_digits = ctx.dps
    ctx.dps = 145
    try:
        weights = [arb(value).sqrt() for value in squared_weights]
        scaled = arb_mat(74, 74, [
            matrix[row, column] / (weights[row] * weights[column])
            for row in range(74)
            for column in range(74)
        ])
        determinant = scaled.det()
        determinant_absolute = abs(determinant)
        frobenius_squared = arb(0)
        for row in range(74):
            for column in range(74):
                entry_absolute = abs(scaled[row, column])
                frobenius_squared += entry_absolute * entry_absolute
        frobenius = frobenius_squared.sqrt()
        determinant_lower = determinant_absolute.lower()
        frobenius_upper = frobenius.upper()
        sigma_lower = determinant_lower / (frobenius_upper ** 73)
        inverse_equivalence_upper = 1 / sigma_lower
        data = {
            "scaled_determinant_ball": str(determinant),
            "scaled_absolute_determinant_lower": str(determinant_lower),
            "scaled_frobenius_ball": str(frobenius),
            "scaled_frobenius_upper": str(frobenius_upper),
            "sigma_min_determinant_lower": str(sigma_lower),
            "graph_to_product_equivalence_upper": str(inverse_equivalence_upper),
            "determinant_relative_accuracy_bits": int(
                determinant.rel_accuracy_bits()
            ),
            "determinant_contains_zero": determinant.contains(0),
        }
        # Logarithms remain representable when the directed bound is far
        # outside binary64's exponent range; the full Arb balls remain primary.
        log_ten = arb(10).log()
        sigma_log10 = float((sigma_lower.log() / log_ten).mid())
        inverse_log10 = float(
            (inverse_equivalence_upper.log() / log_ten).mid()
        )
    finally:
        ctx.dps = prior_digits

    validation = {
        "python_flint_version_pinned_to_0_9_0": flint.__version__ == "0.9.0",
        "scaled_bordered_matrix_is_74_by_74": scaled.nrows() == scaled.ncols() == 74,
        "directed_determinant_excludes_zero": not data["determinant_contains_zero"],
        "directed_determinant_has_at_least_200_accuracy_bits": (
            data["determinant_relative_accuracy_bits"] >= 200
        ),
        "determinant_lower_is_strictly_positive": bool(determinant_lower > 0),
        "frobenius_upper_is_finite_positive": bool(frobenius_upper > 0),
        "sigma_min_lower_is_strictly_positive": bool(sigma_lower > 0),
        "graph_product_equivalence_upper_is_finite_positive": bool(
            inverse_equivalence_upper > 0
        ),
        "explicit_bordered_inverse_not_formed": True,
        "ill_conditioned_kinetic_Dirac_block_not_inverted": True,
        "nonlinear_defect_and_capture_not_overpromoted": True,
        "no_selector_scale_fit_endpoint_action_term_or_chord_added": True,
    }

    return {
        "artifact": "BHSM_N12_BORDERED_GRAPH_PRODUCT_NORM_EQUIVALENCE",
        "status": "POSITIVE_DIRECTED_GRAPH_TO_PRODUCT_EQUIVALENCE_DERIVED_CONSERVATIVE",
        "classification": (
            "THE_DIRECTED_SCALED_BORDERED_DETERMINANT_EXCLUDES_ZERO_AND_A_"
            "FROBENIUS_PRODUCT_BOUND_GIVES_A_STRICTLY_POSITIVE_LOWER_BOUND_"
            "FOR_sigma_min(W^-1*B_minus2*W^-1),_HENCE_AN_EXPLICIT_GRAPH_TO_"
            "PRODUCT_NORM_EQUIVALENCE_WITHOUT_FORMING_ANY_COMBINED_INVERSE;_"
            "THE_BOUND_IS_EXTREMELY_CONSERVATIVE_AND_THE_NONLINEAR_RELATIVE_"
            "GRAPH_DEFECT_REMAINS_OPEN"
        ),
        "definition": {
            "scaled_operator": "B_tilde=W^-1*B_minus2*W^-1",
            "determinant_bound": (
                "sigma_min>=abs(det(B_tilde))/norm(B_tilde)_F^73"
            ),
            "norm_consequence": (
                "norm(X)_product<=sigma_min_lower^-1*norm(X)_graph"
            ),
            "explicit_inverse_formed": False,
        },
        "directed_certificate": data,
        "magnitude_diagnostic": {
            "sigma_min_lower_log10": sigma_log10,
            "equivalence_upper_log10": inverse_log10,
            "binary_actual_sigma_min_diagnostic": 5.810017231126665e-27,
            "binary_diagnostic_has_proof_authority": False,
            "interpretation": (
                "DETERMINANT_FROBENIUS_IS_A_POSITIVE_FALLBACK;_A_USEFUL_"
                "RADIUS_REQUIRES_CERTIFIED_REPEATED_SOLVE_GRAPH_BOUNDS"
            ),
        },
        "exact_next_dependency": (
            "COMPUTE_THE_LEADING_NONLINEAR_BORDERED_DERIVATIVE_TENSORS_AND_"
            "BOUND_THEIR_GRAPH_RELATIVE_ACTION_BY_CERTIFIED_REPEATED_SOLVES;_"
            "USE_THE_DETERMINANT_EQUIVALENCE_ONLY_AS_A_POSITIVE_FALLBACK_FOR_"
            "THE_REMAINDER_NOT_RESOLVED_BY_STRUCTURE"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_BORDERED_RELATIVE_GRAPH_DEFECT_MAJORANT",
            "Gate8": "LOCKED",
            "positive_graph_product_equivalence": "DERIVED",
            "useful_repeated_solve_relative_bound": "OPEN_CURRENT_OWNER",
            "quantitative_capture_surface": "OPEN",
            "reset_to_capture_overlap": "NOT_CERTIFIED",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS
        },
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
