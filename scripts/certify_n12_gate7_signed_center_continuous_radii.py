"""Adjudicate the complete stored signed center beyond a finite radius grid."""
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from bhsm.interface import nonnegative_two_radius_screen as radii
import certify_n12_gate7_current_green_signed_transverse_causal_center as center

RESULT = center.F / "BHSM_N12_GATE7_SIGNED_CENTER_CONTINUOUS_RADII.json"
THEORY = ROOT / "theory/n12_gate7_signed_center_continuous_radii.md"


def _sha(path):
    if path.suffix.lower() in {".json", ".md", ".py"}:
        return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def build_payload():
    record = json.loads(center.RESULT.read_text(encoding="utf-8"))
    if (record.get("validation_passed") is not True
            or record.get("status") != "SIGNED_TRANSVERSE_CAUSAL_CENTER_COMPOSED"
            or record.get("validation", {}).get("complete_midpoint_UU_CU_UC_CC_blocks_included") is not True):
        raise RuntimeError("A complete validated signed center is required")
    # The original artifact is retained, including its grid result and failures.
    endpoint = center.ENDPOINT.with_suffix(".npz")
    for path in (endpoint, Path(center.cert.__file__).resolve()):
        name = path.relative_to(ROOT).as_posix()
        if record.get("inputs", {}).get(name) != _sha(path):
            raise RuntimeError(f"Signed-center radius ceiling source changed: {name}")
    if record.get("data_SHA256") != _sha(center.DATA):
        raise RuntimeError("Signed-center data changed")
    sources = (center.RESULT, endpoint, Path(center.cert.__file__).resolve(),
               Path(__file__).resolve(), Path(radii.__file__).resolve(), THEORY)
    hashes = {path.relative_to(ROOT).as_posix(): _sha(path) for path in sources}
    with np.load(endpoint) as data:
        ceiling = float(data["independent_signed_descriptors"][-1] / center.cert.TRIAL_DESCRIPTOR_SCALE)
    coeff = record["coefficients"]
    old = record.get("screen") or {}
    initial = None
    if "best_longitudinal_radius" in old and "best_transverse_radius" in old:
        initial = [old["best_longitudinal_radius"], old["best_transverse_radius"]]
    result = radii.continuous_two_radius_screen(
        coeff["Y"], coeff["Z1"], coeff["central_quadratic"],
        coeff["mixed_quadratic"], coeff["signed_transverse_quadratic_center"],
        ceiling, initial_radius=initial)
    if any(_sha(ROOT/name) != value for name, value in hashes.items()):
        raise RuntimeError("Continuous radius adjudication inputs changed")
    return {
        "artifact": "BHSM_N12_GATE7_SIGNED_CENTER_CONTINUOUS_RADII",
        "inputs": hashes, "coefficients": coeff, "radius_ceiling": ceiling,
        "retained_grid_screen": old, "continuous_adjudication": result,
        "validation_passed": True, "FULL_BHSM_COMPLETE": False,
        "exact_next_calculation": {
            "STORED_POLYNOMIAL_SELF_MAP": "ATTACH_MISSING_PHYSICAL_AND_ARITHMETIC_ERRORS_AND_NEIGHBORHOOD_REMAINDER_TO_THE_SAME_CENTER",
            "STORED_POLYNOMIAL_CAP_OBSTRUCTION": "RECORD_STORED_POLYNOMIAL_OBSTRUCTION_WITHOUT_CLAIMING_ROOT_NONEXISTENCE_OR_RETUNING",
            "UNRESOLVED": "CONTINUE_RADIUS_ADJUDICATION_WITHOUT_TREATING_SEARCH_FAILURE_AS_NONEXISTENCE",
        }[result["status"]],
    }


def main():
    payload = build_payload()
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"artifact": payload["artifact"],
                      "status": payload["continuous_adjudication"]["status"],
                      "validation_passed": payload["validation_passed"]}))


if __name__ == "__main__":
    main()
