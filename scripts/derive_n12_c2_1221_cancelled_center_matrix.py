"""Regenerate the tracked 1221 center jets for cancelled-field assembly."""

from __future__ import annotations

import importlib.util
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
SOURCE = ROOT / "scripts" / "audit_n12_c2_exact_center_fixed_s_field_matrix.py"
RESULT = BASE / "BHSM_N12_C2_1221_CANCELLED_CENTER_MATRIX.json"
DATA = RESULT.with_suffix(".npz")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def main() -> None:
    spec = importlib.util.spec_from_file_location("fixed_center_source", SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load canonical fixed-center assembly")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.BORDERED = BASE / "BHSM_N12_C2_LOHNER_BORDERED_MATRIX_1221.json"
    module.BORDERED_DATA = module.BORDERED.with_suffix(".npz")
    module.CONTINUATION = BASE / "BHSM_N12_C2_LOHNER_CENTER_1221_INPUT.json"
    module.GROWTH = BASE / "BHSM_N12_C2_LOHNER_GROWTH_1221.json"
    module.RESULT = RESULT
    module.DATA_RESULT = DATA
    module.INPUTS = (
        module.BORDERED, module.BORDERED_DATA, module.CONTINUATION,
        module.GROWTH, module.THEORY,
    )
    payload = module.build_payload()
    payload["artifact"] = "BHSM_N12_C2_1221_CANCELLED_CENTER_MATRIX"
    payload["purpose"] = (
        "SUPPLY_SIGNED_Delta_FIRST_JET_FOR_DENOMINATOR_FREE_G_theta_ASSEMBLY"
    )
    payload["derivation_source"] = SOURCE.relative_to(ROOT).as_posix()
    payload["derivation_source_SHA256"] = _sha256(SOURCE)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "Delta": payload["center_field"]["Delta"],
        "validation_passed": payload["validation_passed"],
        "data": payload["data"],
    }, indent=2))


if __name__ == "__main__":
    main()
