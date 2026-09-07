"""Audit retained midpoint directions without evaluating the action.

The diagnostics are binary64 center data. The rational witness is exact
algebra; neither item is an outward or physical certificate.
"""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_CURRENT_GREEN_COMPONENTWISE_TWO_RADIUS_SCREEN.json"
)
DATA = SOURCE.with_suffix(".npz")
RESULT = ROOT / (
    "artifacts/current_semantics/"
    "BHSM_N12_GATE7_SIGNED_MIDPOINT_COMPLETENESS_AUDIT.json"
)
THEORY = ROOT / "theory/n12_gate7_signed_midpoint_completeness_audit.md"
INTERVALS = 370


def _sha(path: Path) -> str:
    content = path.read_bytes()
    if path.suffix in {".json", ".py", ".md"}:
        content = content.replace(b"\r\n", b"\n")
    return hashlib.sha256(content).hexdigest().upper()


def summarize_diagnostic(values: np.ndarray) -> dict[str, object]:
    """Summarize one finite nonnegative norm per retained interval."""
    values = np.asarray(values, dtype=float)
    if values.shape != (INTERVALS,):
        raise ValueError("exactly 370 retained midpoint norms are required")
    if not np.all(np.isfinite(values)) or np.any(values < 0.0):
        raise ValueError("midpoint norms must be finite and nonnegative")
    return {
        "count": int(values.size),
        "nonzero_count": int(np.count_nonzero(values)),
        "minimum": float(values.min()),
        "maximum": float(values.max()),
        "maximum_interval": int(values.argmax()),
    }


def exact_complement_witness() -> dict[str, object]:
    """Show that a transported endpoint complement need not stay transverse."""
    axis = [Fraction(1), Fraction(0)]
    vector = [Fraction(0), Fraction(1)]
    midpoint_map = [[Fraction(0), Fraction(1)],
                    [Fraction(1), Fraction(0)]]

    def dot(left, right):
        return sum(a * b for a, b in zip(left, right, strict=True))

    image = [dot(row, vector) for row in midpoint_map]
    longitudinal = dot(axis, image)
    projected = [value - longitudinal * axis[i]
                 for i, value in enumerate(image)]
    # H = diag(1, 0), the Hessian of f(x) = x_0**2 / 2.
    return {
        "arithmetic": "EXACT_RATIONAL",
        "scope": "ALGEBRAIC_WITNESS_NOT_A_BHSM_ACTION_EVALUATION",
        "endpoint_axis_dot_input": int(dot(axis, vector)),
        "midpoint_axis_component": int(longitudinal),
        "full_quadratic": int(image[0] ** 2),
        "transverse_only_quadratic": int(projected[0] ** 2),
    }


def build_payload(
    source_path: Path = SOURCE, data_path: Path = DATA,
) -> dict[str, object]:
    """Read a validated, hash-matched retained diagnostic and emit an audit."""
    source = json.loads(source_path.read_text(encoding="utf-8"))
    if source.get("validation_passed") is not True:
        raise ValueError("validated source diagnostic is required")
    if source.get("artifact") != (
        "BHSM_N12_GATE7_CURRENT_GREEN_COMPONENTWISE_TWO_RADIUS_SCREEN"
    ):
        raise ValueError("unexpected source artifact")
    if _sha(data_path) != source.get("data_SHA256"):
        raise ValueError("source diagnostic data SHA256 mismatch")
    with np.load(data_path, allow_pickle=False) as data:
        longitudinal = summarize_diagnostic(
            data["midpoint_longitudinal_coordinate_operator_norm"]
        )
        normal = summarize_diagnostic(
            data["omitted_midpoint_normal_operator_norm"]
        )
    if normal["maximum"] != source.get(
        "maximum_omitted_midpoint_normal_operator_norm"
    ):
        raise ValueError("source JSON and data normal maxima disagree")
    witness = exact_complement_witness()
    validation = {
        "retained_source_validated_and_data_hash_matched": True,
        "all_370_midpoint_diagnostics_finite": True,
        "source_normal_maximum_reproduced": True,
        "exact_witness_is_endpoint_transverse": (
            witness["endpoint_axis_dot_input"] == 0
        ),
        "exact_witness_has_nonzero_omitted_quadratic": (
            witness["full_quadratic"] == 1
            and witness["transverse_only_quadratic"] == 0
        ),
    }
    return {
        "artifact": "BHSM_N12_GATE7_SIGNED_MIDPOINT_COMPLETENESS_AUDIT",
        "status": "RETAINED_MIDPOINT_AXIS_AND_NORMAL_COMPONENTS_AUDITED",
        "authority": (
            "RETAINED_BINARY64_DIRECTION_DIAGNOSTICS_AND_EXACT_ALGEBRAIC_"
            "WITNESS_NOT_OUTWARD_OR_PHYSICAL_AUTHORITY"
        ),
        "inputs": {
            str(SOURCE.relative_to(ROOT)): _sha(source_path),
            str(DATA.relative_to(ROOT)): _sha(data_path),
            str(THEORY.relative_to(ROOT)): _sha(THEORY),
            str(Path(__file__).resolve().relative_to(ROOT)): _sha(
                Path(__file__).resolve()
            ),
        },
        "midpoint_longitudinal_coordinate_operator_norm": longitudinal,
        "midpoint_normal_operator_norm": normal,
        "all_retained_midpoints_have_nonzero_longitudinal_and_normal_components": (
            longitudinal["nonzero_count"] == INTERVALS
            and normal["nonzero_count"] == INTERVALS
        ),
        "exact_counterexample": witness,
        "chain_rule": {
            "decomposition": "w = ell*g + t + n",
            "tangent_terms": "ell^2*H[g,g] + 2*ell*H[g,t] + H[t,t]",
            "normal_terms": "2*H[ell*g+t,n] + H[n,n]",
            "radius_owner": (
                "All terms induced from endpoint-transverse input contribute "
                "to its r_T^2 coefficient, irrespective of midpoint direction."
            ),
            "source_conversion": (
                "Existing central and mixed contractions require their actual "
                "ambient directions, scales, and span; column labels alone "
                "do not identify them with the recovered transverse basis."
            ),
        },
        "scientific_consequence": (
            "Retained diagnostics do not support dropping midpoint axis or "
            "normal components. Restore their signed contractions or supply "
            "an explicit bound before full-center or outward authority. "
            "No action or tensor rerun follows from this diagnostic alone."
        ),
        "claim_boundary": {
            "FULL_MIDPOINT_HESSIAN_CHAIN_RULE_CERTIFIED": False,
            "ACTUAL_OMITTED_HESSIAN_MAGNITUDE_EVALUATED": False,
            "OUTWARD_TRANSVERSE_REMAINDER_DERIVED": False,
            "GATE7_CLOSED": False,
            "ROOT_NONEXISTENCE_DERIVED": False,
            "PHYSICAL_INSTABILITY_DERIVED": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_calculation": (
            "RESTORE_SIGNED_MIDPOINT_AXIS_AND_NORMAL_CHAIN_RULE_CONTRACTIONS_"
            "FROM_PROVENANCE_MATCHED_CURRENT_ACTION_DATA_THEN_EVALUATE_THE_"
            "COMPLETE_CENTER_SCREEN_BEFORE_OUTWARD_CERTIFICATION"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


if __name__ == "__main__":
    payload = build_payload()
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": payload["status"],
        "longitudinal": payload[
            "midpoint_longitudinal_coordinate_operator_norm"
        ],
        "normal": payload["midpoint_normal_operator_norm"],
        "validation_passed": payload["validation_passed"],
        "FULL_BHSM_COMPLETE": False,
    }, sort_keys=True))
