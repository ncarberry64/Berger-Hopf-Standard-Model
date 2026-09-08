"""Certify one rounding operand through all 370 stored midpoint Hessians.

Requires the complete, validated supplemental center campaign. No numerical
contraction is launched here. Missing inputs fail before a report is written.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from bhsm.interface import current_green_midpoint_coordinate_error as propagation
import certify_n12_gate7_current_green_midpoint_coordinate_solve as coordinate
import certify_n12_gate7_current_green_supplemental_midpoint_blocks as blocks
import certify_n12_gate7_symmetric_quadratic_representatives as quadratic_representatives
import certify_n12_gate7_current_green_scalar_covector_correction as scalar_correction_certificate

causal = coordinate.causal
supplement = coordinate.supplement
RESULT = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_MIDPOINT_COORDINATE_PULLBACK.json"


def certify_stored_pullback(basis, target, approximate, uu, cu, cc):
    """Verify epsilon directly; bind the bound to each exact stored operand."""
    operands = dict(basis=basis, target=target, approximate_coordinates=approximate,
                    retained_retained=uu, complement_retained=cu,
                    complement_complement=cc)
    # Reject complex/nonfinite inputs before the older solve API casts them.
    operands = {name: propagation._real_binary64(value, name)
                for name, value in operands.items()}
    solved = coordinate.certify_solve(operands["basis"], operands["target"],
                                      operands["approximate_coordinates"])
    result = propagation.bound_coordinate_pullback_error(
        operands["retained_retained"], operands["complement_retained"],
        operands["complement_complement"], operands["approximate_coordinates"],
        solved["coordinate_error_infinity_upper"],
    )
    result["coordinate_bound_requires_external_verification"] = False
    result["coordinate_solve_verification"] = solved
    result["operand_binary64_SHA256"] = {
        name: coordinate._array_hash(value) for name, value in operands.items()
    }
    return result


def build_payload():
    # Revalidate actual data and all restart rows instead of trusting a flag
    # in an old JSON report. This also validates the rectangular UU identity.
    validated = blocks.build_payload()
    if validated.get("validation_passed") is not True:
        raise RuntimeError("complete current supplemental validation required")
    fingerprint = supplement._fingerprint()
    if validated.get("campaign_fingerprint") != fingerprint:
        raise RuntimeError("supplemental validation fingerprint changed")
    raw_recovery = json.loads(quadratic_representatives.raw_certificate.RESULT.read_text(encoding="utf-8"))
    represented = json.loads(quadratic_representatives.RESULT.read_text(encoding="utf-8"))
    quadratic_representatives.validate_for_consumption(raw_recovery, represented)
    corrected = json.loads(scalar_correction_certificate.RESULT.read_text(encoding='utf-8'))
    scalar_correction_certificate.validate_for_consumption(corrected)
    representative_rows = {row['index']: row for row in corrected['rows'] if row['kind'] == 'midpoint'}
    paths = {Path(__file__), Path(propagation.__file__), Path(coordinate.__file__),
             Path(coordinate.basis_certificate.__file__), Path(blocks.__file__),
             Path(causal.__file__), Path(supplement.__file__),
             Path(causal.center.__file__), Path(causal.cert.__file__),
             Path(causal.component.scalar.__file__),
             ROOT / "src/bhsm/interface/current_green_supplemental_midpoint.py",
             quadratic_representatives.RESULT,
             Path(quadratic_representatives.__file__),
             Path(quadratic_representatives.representation.__file__),
             scalar_correction_certificate.RESULT,
             Path(scalar_correction_certificate.__file__),
             Path(scalar_correction_certificate.correction.__file__),
             blocks.VALIDATION}
    paths.update(path.with_suffix(".npz") for path in (
        causal.center.ENDPOINT, causal.center.REPLAY, causal.center.JACOBIAN,
        causal.center.PARTITION, causal.center.SCALAR))
    paths.add(causal.ENDPOINT.with_suffix(".npz"))
    # Bind the validated values before reading them for certificate arithmetic.
    for index in range(370):
        paths.add(supplement.recovery._path("midpoint", index))
        paths.add(scalar_correction_certificate.correction._path('midpoint', index))
        paths.add(supplement._aggregate_path(index))
        paths.update(causal.MIXED_WORK / f"endpoint_{node:03d}.npz"
                     for node in (index, index + 1) if node > 0)
    before = {path: supplement._sha(path) for path in sorted(paths)}
    geometry = supplement._load_geometry()
    inputs = geometry["inputs"]
    endpoint_tangents, axes = inputs["endpoint"][2:4]
    midpoint_tangents = inputs["midpoint"][2]
    with np.load(causal.ENDPOINT.with_suffix(".npz")) as source:
        times = np.asarray(source["collocation_arc_parameters"], dtype=float)
    rows = []
    for index in range(370):
        completion, recovered = supplement._completion(index, geometry)
        corrected_tensor, _ = scalar_correction_certificate.correction.corrected_tensor('midpoint', index)
        uu = quadratic_representatives.representation.symmetric_center(corrected_tensor)
        if quadratic_representatives.array_hash(uu) != representative_rows[index]['represented_tensor_binary64_SHA256']:
            raise RuntimeError(f'certified midpoint representative changed: {index}')
        with np.load(supplement._aggregate_path(index)) as source:
            if not (np.array_equal(source["retained_directions"], completion.retained_directions)
                    and np.array_equal(source["complement_directions"], completion.complement_directions)):
                raise RuntimeError(f"stored supplemental coordinate directions changed: {index}")
            cu = np.asarray(source["complement_retained"], dtype=float)
            cc = np.asarray(source["complement_complement"], dtype=float)
        target = causal._kinematic_midpoint_map(
            index, float(times[index + 1] - times[index]), axes,
            endpoint_tangents, midpoint_tangents,
        ).augmented
        approximate = np.linalg.solve(completion.full_basis, target)
        row = certify_stored_pullback(completion.full_basis, target, approximate, uu, cu, cc)
        row["interval"] = index
        row['stored_UU_representation_rounding_Frobenius_upper'] = representative_rows[index]['projection_rounding_Frobenius_upper']
        row['stored_UU_scalar_addition_rounding_Frobenius_upper'] = representative_rows[index]['scalar_addition_rounding_Frobenius_upper']
        rows.append(row)
    if any(supplement._sha(path) != digest for path, digest in before.items()):
        raise RuntimeError("certificate inputs changed during evaluation")
    if blocks._manifest([supplement._aggregate_path(i) for i in range(370)]) != validated["aggregate_manifest_SHA256"]:
        raise RuntimeError("supplemental aggregate manifest changed after validation")
    if supplement._fingerprint() != fingerprint:
        raise RuntimeError("campaign fingerprint changed during evaluation")
    return {
        "artifact": "BHSM_N12_GATE7_MIDPOINT_COORDINATE_PULLBACK",
        "status": "ALL_370_STORED_MIDPOINT_COORDINATE_PULLBACK_ERRORS_ENCLOSED",
        "scope": "COORDINATE_ERROR_THROUGH_EXACT_STORED_BINARY64_TENSOR_ONLY",
        "arithmetic_precision_bits": propagation.PRECISION,
        "coverage": {"verified_midpoints": len(rows), "required_midpoints": 370,
                     "complete": len(rows) == 370},
        "rows": rows,
        "maximum_pullback_coordinate_error_frobenius_upper": max(
            row["pullback_coordinate_error_frobenius_upper"] for row in rows),
        "campaign_fingerprint": fingerprint,
        "supplemental_aggregate_manifest_SHA256": validated["aggregate_manifest_SHA256"],
        "supplemental_restart_row_manifest_SHA256": validated["restart_row_manifest_SHA256"],
        "inputs": {path.relative_to(ROOT).as_posix(): digest for path, digest in before.items()},
        "validation_passed": True,
        "claim_boundary": {
            "all_370_stored_coordinate_errors_propagated_through_full_tensor": True,
            "physical_direction_construction_rounding_enclosed": False,
            "physical_Hessian_rounding_enclosed": False,
            "pullback_assembly_rounding_enclosed": False,
            "stored_quadratic_representation_rounding_propagated": False,
            "causal_output_maps_and_accumulation_enclosed": False,
            "physical_neighborhood_remainder_derived": False,
            "Gate7_closed": False,
            "FULL_BHSM_COMPLETE": False,
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=RESULT)
    args = parser.parse_args()
    payload = build_payload()
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: payload[key] for key in
                     ("status", "coverage", "maximum_pullback_coordinate_error_frobenius_upper")}))


if __name__ == "__main__":
    main()
